from __future__ import annotations

import html
import importlib.util
import re
import urllib.parse
from pathlib import Path


def _load_base_module():
    script = Path(__file__).with_name("run_g04_source_acquisition.py")
    spec = importlib.util.spec_from_file_location("g04_base", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load acquisition engine from {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = _load_base_module()


def sanitize_url(url: str) -> str:
    """Encode literal spaces without destroying existing percent escapes.

    Springer supplementary URLs contain an encoded colon (`%3A`). Decoding
    and re-encoding that path changes the server route, so existing `%XX`
    escapes must survive byte-for-byte.
    """
    parts = urllib.parse.urlsplit(html.unescape(url.strip()))
    if parts.scheme not in {"http", "https"}:
        raise ValueError(f"unsupported URL scheme: {parts.scheme!r}")
    path = urllib.parse.quote(
        parts.path,
        safe="/%:@-._~!$&'()*+,;=",
    )
    query = urllib.parse.quote(
        parts.query,
        safe="=&%+;,:/?@-._~!$'()*",
    )
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, path, query, parts.fragment)
    )


def candidate_urls_from_html(
    landing_url: str,
    expected_filename: str,
    html_payload: bytes,
) -> tuple[list[str], list[str]]:
    """Collect valid HTTP(S) candidates while ignoring malformed page tokens."""
    text = html_payload.decode("utf-8", errors="replace")
    parser = BASE.LinkCollector()
    parser.feed(text)

    url_like = re.findall(r"(?:https?://|/)[^\"'<>\s]+", html.unescape(text))
    raw_links = list(dict.fromkeys(parser.links + url_like))
    expected_lower = expected_filename.casefold()

    exact: list[str] = []
    likely: list[str] = []
    for raw in raw_links:
        try:
            decoded = urllib.parse.unquote(html.unescape(raw))
            resolved = urllib.parse.urljoin(landing_url, raw)
            clean = sanitize_url(resolved)
            parsed = urllib.parse.urlsplit(clean)
            if not parsed.netloc or parsed.hostname is None:
                continue
        except (TypeError, ValueError, UnicodeError):
            continue

        lowered = decoded.casefold()
        if expected_lower in lowered:
            exact.append(clean)
        if any(token in lowered for token in ("download", ".pdf", ".zip", "/files/")):
            likely.append(clean)

    return list(dict.fromkeys(exact)), list(dict.fromkeys(likely))


# Patch the base module's global lookups. Its remaining acquisition, hashing,
# PDF parsing, and certificate logic stays unchanged.
BASE.sanitize_url = sanitize_url
BASE.candidate_urls_from_html = candidate_urls_from_html


if __name__ == "__main__":
    raise SystemExit(BASE.main())
