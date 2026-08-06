from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import tempfile
import urllib.parse
import urllib.request
import zipfile
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "Chrome/151.0 Safari/537.36 Thermodynamics-Reproducibility-G04/1.1"
)
MACHINE_READABLE_SUFFIXES = {
    ".csv",
    ".tsv",
    ".txt",
    ".json",
    ".xml",
    ".xls",
    ".xlsx",
    ".ods",
    ".zip",
}
COOKIE_JAR = CookieJar()
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(COOKIE_JAR))


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if not value:
                continue
            if key.lower() in {
                "href",
                "src",
                "data-url",
                "data-file-url",
                "data-download-url",
            }:
                self.links.append(html.unescape(value))


def sanitize_url(url: str) -> str:
    parts = urllib.parse.urlsplit(html.unescape(url.strip()))
    path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/%:@-._~!$&()*+,;=")
    query = urllib.parse.quote(
        urllib.parse.unquote(parts.query),
        safe="=&%+;,:/?@-._~!$'()*",
    )
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def request_bytes(
    url: str,
    *,
    timeout: float = 90.0,
    referer: str | None = None,
) -> tuple[bytes, str, str, dict[str, str]]:
    clean_url = sanitize_url(url)
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/pdf,application/zip,text/html;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if referer:
        headers["Referer"] = referer
    request = urllib.request.Request(clean_url, headers=headers)
    with OPENER.open(request, timeout=timeout) as response:
        payload = response.read()
        final_url = response.geturl()
        content_type = response.headers.get_content_type()
        response_headers = {key.lower(): value for key, value in response.headers.items()}
    return payload, final_url, content_type, response_headers


def request_json(
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: float = 90.0,
) -> Any:
    body = None
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(sanitize_url(url), data=body, headers=headers)
    with OPENER.open(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def candidate_urls_from_html(
    landing_url: str,
    expected_filename: str,
    html_payload: bytes,
) -> tuple[list[str], list[str]]:
    text = html_payload.decode("utf-8", errors="replace")
    parser = LinkCollector()
    parser.feed(text)

    url_like = re.findall(r"(?:https?://|/)[^\"'<>\s]+", html.unescape(text))
    raw_links = list(dict.fromkeys(parser.links + url_like))
    expected_lower = expected_filename.casefold()

    exact: list[str] = []
    likely: list[str] = []
    for raw in raw_links:
        decoded = urllib.parse.unquote(html.unescape(raw))
        resolved = urllib.parse.urljoin(landing_url, raw)
        lowered = decoded.casefold()
        if expected_lower in lowered:
            exact.append(resolved)
        if any(token in lowered for token in ("download", ".pdf", ".zip", "/files/")):
            likely.append(resolved)

    return list(dict.fromkeys(exact)), list(dict.fromkeys(likely))


def discover_url_from_html(
    landing_url: str,
    expected_filename: str,
    html_payload: bytes,
) -> str | None:
    exact, _ = candidate_urls_from_html(landing_url, expected_filename, html_payload)
    return exact[0] if exact else None


def disposition_filename(headers: dict[str, str]) -> str | None:
    value = headers.get("content-disposition", "")
    match = re.search(r"filename\*?=(?:UTF-8''|\")?([^\";]+)", value, flags=re.I)
    if not match:
        return None
    return urllib.parse.unquote(match.group(1).strip().strip('"'))


def extract_expected_from_zip(payload: bytes, expected_filename: str) -> bytes | None:
    if not payload.startswith(b"PK"):
        return None
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for name in archive.namelist():
            if Path(name).name.casefold() == expected_filename.casefold():
                return archive.read(name)
    return None


def figshare_file_url(title: str, expected_filename: str) -> str | None:
    results = request_json(
        "https://api.figshare.com/v2/articles/search",
        payload={"search_for": title, "limit": 100},
    )
    if not isinstance(results, list):
        return None
    for item in results:
        if not isinstance(item, dict) or "id" not in item:
            continue
        details = request_json(f"https://api.figshare.com/v2/articles/{item['id']}")
        for file_item in details.get("files", []):
            if str(file_item.get("name", "")).casefold() == expected_filename.casefold():
                return str(file_item["download_url"])
    return None


def acquire_source(
    source: dict[str, Any],
) -> tuple[bytes, str, str, list[dict[str, str]]]:
    attempts: list[dict[str, str]] = []
    expected_filename = str(source["expected_filename"])
    landing_url = source.get("landing_url")

    for candidate in source.get("direct_urls", []):
        try:
            payload, final_url, content_type, _ = request_bytes(
                str(candidate),
                referer=landing_url if isinstance(landing_url, str) else None,
            )
            attempts.append({"url": str(candidate), "status": "SUCCESS"})
            return payload, final_url, content_type, attempts
        except Exception as exc:
            attempts.append(
                {
                    "url": str(candidate),
                    "status": "FAILED",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    figshare_title = source.get("figshare_search_title")
    if isinstance(figshare_title, str) and figshare_title:
        try:
            resolved = figshare_file_url(figshare_title, expected_filename)
            if resolved:
                payload, final_url, content_type, _ = request_bytes(resolved)
                attempts.append({"url": resolved, "status": "FIGSHARE_SUCCESS"})
                return payload, final_url, content_type, attempts
            attempts.append(
                {
                    "url": "https://api.figshare.com/v2/articles/search",
                    "status": "FIGSHARE_NO_MATCH",
                }
            )
        except Exception as exc:
            attempts.append(
                {
                    "url": "https://api.figshare.com/v2/articles/search",
                    "status": "FIGSHARE_FAILED",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    if not isinstance(landing_url, str) or not landing_url:
        raise RuntimeError(f"no successful source route for {expected_filename}")

    landing_payload, final_landing_url, landing_content_type, _ = request_bytes(landing_url)
    attempts.append(
        {
            "url": landing_url,
            "status": "LANDING_FETCHED",
            "content_type": landing_content_type,
        }
    )
    exact, likely = candidate_urls_from_html(
        final_landing_url,
        expected_filename,
        landing_payload,
    )

    candidates = list(dict.fromkeys(exact + likely))[:60]
    for candidate in candidates:
        try:
            payload, final_url, content_type, headers = request_bytes(
                candidate,
                referer=final_landing_url,
            )
            resolved_name = disposition_filename(headers)
            decoded_url = urllib.parse.unquote(final_url)

            if payload.startswith(b"%PDF"):
                if (
                    expected_filename.casefold() in decoded_url.casefold()
                    or (resolved_name and resolved_name.casefold() == expected_filename.casefold())
                    or candidate in exact
                ):
                    attempts.append({"url": candidate, "status": "LANDING_PDF_SUCCESS"})
                    return payload, final_url, content_type, attempts

            zipped = extract_expected_from_zip(payload, expected_filename)
            if zipped is not None:
                attempts.append({"url": candidate, "status": "LANDING_ZIP_SUCCESS"})
                return zipped, final_url + f"#{expected_filename}", "application/pdf", attempts

            if content_type == "text/html":
                nested_exact, _ = candidate_urls_from_html(
                    final_url,
                    expected_filename,
                    payload,
                )
                for nested in nested_exact[:10]:
                    nested_payload, nested_url, nested_type, _ = request_bytes(
                        nested,
                        referer=final_url,
                    )
                    if nested_payload.startswith(b"%PDF"):
                        attempts.append({"url": nested, "status": "NESTED_PDF_SUCCESS"})
                        return nested_payload, nested_url, nested_type, attempts
        except Exception as exc:
            attempts.append(
                {
                    "url": candidate,
                    "status": "CANDIDATE_FAILED",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    sample = [sanitize_url(value) for value in candidates[:12]]
    raise RuntimeError(
        f"landing page did not yield {expected_filename!r}; candidate sample={sample}"
    )


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def keyword_audit(text: str, groups: dict[str, list[str]]) -> dict[str, Any]:
    lowered = text.casefold()
    result: dict[str, Any] = {}
    for group, keywords in groups.items():
        counts = {keyword: lowered.count(keyword.casefold()) for keyword in keywords}
        result[group] = {
            "total_occurrences": sum(counts.values()),
            "per_keyword": counts,
        }
    return result


def audit_pdf(
    payload: bytes,
    source: dict[str, Any],
    final_url: str,
    content_type: str,
    attempts: list[dict[str, str]],
    keyword_groups: dict[str, list[str]],
) -> dict[str, Any]:
    expected_filename = str(source["expected_filename"])
    minimum_size = int(source.get("min_bytes", 1))
    errors: list[str] = []
    warnings: list[str] = []

    if not payload.startswith(b"%PDF"):
        errors.append("download does not start with the PDF signature")
    if len(payload) < minimum_size:
        errors.append(f"downloaded file is smaller than min_bytes={minimum_size}")

    page_count: int | None = None
    metadata: dict[str, str | None] = {}
    embedded_names: list[str] = []
    machine_readable_names: list[str] = []
    text = ""

    if not errors:
        try:
            from pypdf import PdfReader

            with tempfile.NamedTemporaryFile(suffix=".pdf") as temp:
                temp.write(payload)
                temp.flush()
                reader = PdfReader(temp.name)
                page_count = len(reader.pages)
                raw_metadata = reader.metadata or {}
                metadata = {
                    "title": raw_metadata.get("/Title"),
                    "author": raw_metadata.get("/Author"),
                    "subject": raw_metadata.get("/Subject"),
                    "creator": raw_metadata.get("/Creator"),
                    "producer": raw_metadata.get("/Producer"),
                }
                text_parts: list[str] = []
                for page in reader.pages:
                    try:
                        text_parts.append(page.extract_text() or "")
                    except Exception as exc:
                        warnings.append(f"page text extraction failed: {type(exc).__name__}")
                text = "\n".join(text_parts)

                try:
                    attachments = reader.attachments
                    embedded_names = sorted(str(name) for name in attachments.keys())
                except Exception:
                    embedded_names = []
                machine_readable_names = sorted(
                    name
                    for name in embedded_names
                    if Path(name).suffix.lower() in MACHINE_READABLE_SUFFIXES
                )
        except Exception as exc:
            errors.append(f"PDF parse failed: {type(exc).__name__}: {exc}")

    topology = (
        "PDF_WITH_MACHINE_READABLE_ATTACHMENT"
        if machine_readable_names
        else "PDF_TEXT_AND_FIGURES_ONLY"
        if text.strip()
        else "PDF_WITHOUT_EXTRACTABLE_TEXT"
    )

    return {
        "source_id": source["source_id"],
        "doi": source.get("doi"),
        "expected_filename": expected_filename,
        "channels": source.get("channels", []),
        "rights": source.get("rights"),
        "redistribute_source_file": source.get("redistribute_source_file", False),
        "resolved_url": final_url,
        "content_type": content_type,
        "byte_size": len(payload),
        "sha256": sha256_hex(payload),
        "page_count": page_count,
        "pdf_metadata": metadata,
        "embedded_attachment_names": embedded_names,
        "machine_readable_attachment_names": machine_readable_names,
        "extracted_text_character_count": len(text),
        "keyword_audit": keyword_audit(text, keyword_groups),
        "topology_status": topology,
        "attempts": attempts,
        "status": "PINNED" if not errors else "FAILED",
        "errors": errors,
        "warnings": warnings,
    }


def run_contract(contract: dict[str, Any]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    keyword_groups = contract["audit_contract"]["keyword_groups"]

    for source in contract["sources"]:
        try:
            payload, final_url, content_type, attempts = acquire_source(source)
            result = audit_pdf(
                payload,
                source,
                final_url,
                content_type,
                attempts,
                keyword_groups,
            )
        except Exception as exc:
            result = {
                "source_id": source.get("source_id"),
                "doi": source.get("doi"),
                "expected_filename": source.get("expected_filename"),
                "channels": source.get("channels", []),
                "status": "FAILED",
                "errors": [f"{type(exc).__name__}: {exc}"],
                "warnings": [],
            }
        results.append(result)

    pinned = [item for item in results if item["status"] == "PINNED"]
    machine_ready = sorted(
        {
            channel
            for item in pinned
            if item.get("machine_readable_attachment_names")
            for channel in item.get("channels", [])
        }
    )
    if len(pinned) == len(results):
        overall_status = "PASS_SOURCE_PINNING"
    elif pinned:
        overall_status = "PARTIAL_SOURCE_PINNING"
    else:
        overall_status = "FAIL_SOURCE_PINNING"

    return {
        "campaign": contract["campaign"],
        "stage": contract["stage"],
        "status": overall_status,
        "source_count": len(results),
        "pinned_source_count": len(pinned),
        "failed_source_count": len(results) - len(pinned),
        "machine_readable_ready_channels": machine_ready,
        "sources": results,
        "source_files_committed": False,
        "source_files_uploaded_as_artifacts": False,
        "experimental_plucker_significance_computed": False,
        "claim_boundary": contract["claim_boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "contract",
        nargs="?",
        type=Path,
        default=Path("protocols/G04_GRAPHENE_SOURCE_PINNING.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/G04_SOURCE_ACQUISITION_AUDIT.json"),
    )
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    result = run_contract(contract)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["status"] == "FAIL_SOURCE_PINNING" else 0


if __name__ == "__main__":
    raise SystemExit(main())
