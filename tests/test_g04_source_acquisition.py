from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "run_g04_source_acquisition.py"
    spec = importlib.util.spec_from_file_location("g04_acquisition", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_discovers_exact_filename_from_relative_link() -> None:
    module = load_module()
    page = b'''<html><body><a href="/downloads/file?id=3&amp;name=sample.pdf">Detail</a></body></html>'''
    resolved = module.discover_url_from_html(
        "https://example.org/datasets/abc",
        "sample.pdf",
        page,
    )
    assert resolved == "https://example.org/downloads/file?id=3&name=sample.pdf"


def test_discovers_percent_encoded_filename() -> None:
    module = load_module()
    page = b'''<a href="files/Accepted%20Manuscript.pdf?download=1">download</a>'''
    resolved = module.discover_url_from_html(
        "https://example.org/record/1",
        "Accepted Manuscript.pdf",
        page,
    )
    assert resolved == "https://example.org/record/files/Accepted%20Manuscript.pdf?download=1"


def test_sha256_is_stable() -> None:
    module = load_module()
    assert (
        module.sha256_hex(b"graphene")
        == "a6f815099914723b933800d1c5ab23b3ae4f024c723039293ccafb3f2fbacb8d"
    )


def test_keyword_audit_is_case_insensitive() -> None:
    module = load_module()
    result = module.keyword_audit(
        "Carrier Density and carrier density with ERROR BAR",
        {"chart": ["carrier density"], "uncertainty": ["error bar"]},
    )
    assert result["chart"]["total_occurrences"] == 2
    assert result["uncertainty"]["total_occurrences"] == 1
