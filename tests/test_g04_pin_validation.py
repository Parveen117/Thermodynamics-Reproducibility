from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "validate_g04_source_pins.py"
    spec = importlib.util.spec_from_file_location("g04_pin_validator", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def payload(sha256: str = "abc") -> dict:
    return {
        "campaign": "G04_GRAPHENE_SOURCE_PINNING",
        "source_files_committed": False,
        "source_files_uploaded_as_artifacts": False,
        "experimental_plucker_significance_computed": False,
        "sources": [
            {
                "source_id": "S1",
                "status": "PINNED",
                "byte_size": 10,
                "sha256": sha256,
                "page_count": 2,
                "topology_status": "PDF_TEXT_AND_FIGURES_ONLY",
                "machine_readable_attachment_names": [],
            }
        ],
    }


def test_equal_pin_passes() -> None:
    module = load_module()
    result = module.validate_pins(payload(), payload())
    assert result["status"] == "PASS_PIN_VALIDATION"


def test_hash_drift_fails() -> None:
    module = load_module()
    result = module.validate_pins(payload("old"), payload("new"))
    assert result["status"] == "FAIL_PIN_VALIDATION"
    assert any("sha256 changed" in error for error in result["errors"])


def test_new_embedded_table_requires_new_contract() -> None:
    module = load_module()
    observed = payload()
    observed["sources"][0]["machine_readable_attachment_names"] = ["data.xlsx"]
    result = module.validate_pins(payload(), observed)
    assert result["status"] == "FAIL_PIN_VALIDATION"
    assert any("machine-readable" in error for error in result["errors"])
