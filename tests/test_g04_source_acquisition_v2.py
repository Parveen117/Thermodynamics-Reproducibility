from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "run_g04_source_acquisition_v2.py"
    spec = importlib.util.spec_from_file_location("g04_v2", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_springer_percent_encoded_colon_is_preserved() -> None:
    module = load_module()
    url = (
        "https://media.springernature.com/original/springer-static/esm/"
        "art%3A10.1038%2Fs41565-021-00957-6/MediaObjects/file.pdf"
    )
    assert module.sanitize_url(url) == url


def test_literal_spaces_are_encoded_without_decoding_existing_escapes() -> None:
    module = load_module()
    url = "https://example.org/files/Accepted%20Manuscript and supplement.pdf"
    assert (
        module.sanitize_url(url)
        == "https://example.org/files/Accepted%20Manuscript%20and%20supplement.pdf"
    )


def test_malformed_ipv6_like_page_token_is_ignored() -> None:
    module = load_module()
    page = b'''
    <a href="//[broken-template-token]">bad</a>
    <a href="/files/Accepted%20Manuscript.pdf">good</a>
    '''
    exact, likely = module.candidate_urls_from_html(
        "https://example.org/datasets/abc",
        "Accepted Manuscript.pdf",
        page,
    )
    assert exact == ["https://example.org/files/Accepted%20Manuscript.pdf"]
    assert likely == ["https://example.org/files/Accepted%20Manuscript.pdf"]
