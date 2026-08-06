from __future__ import annotations

import importlib.util
import io
from pathlib import Path

from openpyxl import Workbook


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "run_g05_source_data_discovery.py"
    spec = importlib.util.spec_from_file_location("g05_discovery", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def workbook_bytes() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Fig1"
    sheet["A1"] = "temperature"
    sheet["B1"] = "conductivity"
    sheet["A2"] = 100.0
    sheet["B2"] = 2.0
    stream = io.BytesIO()
    workbook.save(stream)
    workbook.close()
    return stream.getvalue()


def test_xlsx_signature_and_topology() -> None:
    module = load_module()
    payload = workbook_bytes()
    assert module.is_xlsx(payload)
    audit = module.workbook_audit("source.xlsx", payload, "https://example.org/source.xlsx")
    assert audit["sheet_count"] == 1
    assert audit["sheets"][0]["numeric_cell_count"] == 2
    assert audit["sheets"][0]["text_cell_count"] == 2
    assert audit["raw_workbook_stored"] is False


def test_article_link_discovery_accepts_only_official_hosts() -> None:
    module = load_module()
    page = b'''
    <a href="https://media.springernature.com/path/source-data.xlsx">official</a>
    <a href="https://example.org/copied-data.xlsx">copy</a>
    '''
    links = module.discover_article_links("https://www.nature.com/articles/test", page)
    assert links == ["https://media.springernature.com/path/source-data.xlsx"]


def test_candidate_generator_includes_moesm2_xlsx() -> None:
    module = load_module()
    contract = {
        "media_stem": "41567_2025_2972",
        "candidate_bases": ["https://media.springernature.com/base/"],
        "candidate_indices": [2],
        "candidate_extensions": ["xlsx"],
    }
    urls = module.candidate_urls(contract, [])
    assert urls == [
        "https://media.springernature.com/base/41567_2025_2972_MOESM2_ESM.xlsx"
    ]
