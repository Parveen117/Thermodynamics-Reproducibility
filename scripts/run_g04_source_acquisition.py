from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "Chrome/151.0 Safari/537.36 Thermodynamics-Reproducibility-G04/1.0"
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


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() not in {"a", "link"}:
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(html.unescape(value))


def request_bytes(url: str, *, timeout: float = 90.0) -> tuple[bytes, str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read()
        final_url = response.geturl()
        content_type = response.headers.get_content_type()
    return payload, final_url, content_type


def discover_url_from_html(
    landing_url: str,
    expected_filename: str,
    html_payload: bytes,
) -> str | None:
    text = html_payload.decode("utf-8", errors="replace")
    parser = LinkCollector()
    parser.feed(text)
    expected_lower = expected_filename.lower()

    candidates: list[str] = []
    for href in parser.links:
        decoded = urllib.parse.unquote(href)
        if expected_lower in decoded.lower():
            candidates.append(urllib.parse.urljoin(landing_url, href))

    if not candidates:
        escaped = re.escape(expected_filename)
        for match in re.findall(rf"[^\"'<>\s]*{escaped}[^\"'<>\s]*", text, flags=re.I):
            candidates.append(urllib.parse.urljoin(landing_url, html.unescape(match)))

    unique = list(dict.fromkeys(candidates))
    return unique[0] if unique else None


def acquire_source(source: dict[str, Any]) -> tuple[bytes, str, str, list[dict[str, str]]]:
    attempts: list[dict[str, str]] = []
    expected_filename = str(source["expected_filename"])

    for candidate in source.get("direct_urls", []):
        try:
            payload, final_url, content_type = request_bytes(str(candidate))
            attempts.append({"url": str(candidate), "status": "SUCCESS"})
            return payload, final_url, content_type, attempts
        except Exception as exc:  # network failures are reported in the certificate
            attempts.append(
                {
                    "url": str(candidate),
                    "status": "FAILED",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    landing_url = source.get("landing_url")
    if not isinstance(landing_url, str) or not landing_url:
        raise RuntimeError(f"no successful direct URL and no landing URL for {expected_filename}")

    landing_payload, final_landing_url, landing_content_type = request_bytes(landing_url)
    attempts.append(
        {
            "url": landing_url,
            "status": "LANDING_FETCHED",
            "content_type": landing_content_type,
        }
    )
    resolved = discover_url_from_html(final_landing_url, expected_filename, landing_payload)
    if resolved is None:
        raise RuntimeError(
            f"landing page did not expose a link containing {expected_filename!r}"
        )
    payload, final_url, content_type = request_bytes(resolved)
    attempts.append({"url": resolved, "status": "SUCCESS"})
    return payload, final_url, content_type, attempts


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
    overall_status = "PASS_SOURCE_PINNING" if len(pinned) == len(results) else "FAIL_SOURCE_PINNING"

    return {
        "campaign": contract["campaign"],
        "stage": contract["stage"],
        "status": overall_status,
        "source_count": len(results),
        "pinned_source_count": len(pinned),
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
    return 0 if result["status"] == "PASS_SOURCE_PINNING" else 1


if __name__ == "__main__":
    raise SystemExit(main())
