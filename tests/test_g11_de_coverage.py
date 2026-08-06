from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def load_module():
    path = ROOT / "scripts" / "run_g11_de_coverage_audit.py"
    spec = importlib.util.spec_from_file_location("g11", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract() -> dict:
    return json.loads(
        (ROOT / "protocols" / "G11_DE_COVERAGE_CONTRACT.json").read_text()
    )


def test_repository_contract_is_inconclusive_not_failed() -> None:
    result = load_module().audit(contract())
    assert result["status"] == (
        "INCONCLUSIVE_STATE_VARIABLE_ALIGNMENT_AND_MEASURED_SURFACE"
    )
    assert result["temperature_coordinates_identical"] is False
    assert result["lattice_temperature_K"] == 300.0
    assert result["direct_dense_measured_diffusivity_surface"] is False
    assert result["fit_allowed"] is False


def test_theory_surface_cannot_be_promoted() -> None:
    payload = contract()
    for item in payload["figure_typing"]:
        if item["figure"] == "Fig_3g_h":
            item["role"] = "MEASURED_DIFFUSIVITY_SURFACE"
            item["fit_allowed"] = True
    result = load_module().audit(payload)
    assert result["status"] == "FAIL_CONTRACT_AUDIT"
    assert any("calculated theory" in error for error in result["errors"])


def test_temperature_coordinate_substitution_is_rejected() -> None:
    payload = contract()
    payload["candidate_chart"]["temperature_coordinate_matches_base_chart"] = True
    result = load_module().audit(payload)
    assert result["status"] == "FAIL_CONTRACT_AUDIT"
    assert any("transient electron temperature" in error for error in result["errors"])


def test_bad_source_pin_is_rejected() -> None:
    payload = contract()
    payload["source"]["supplement_sha256"] = "0" * 64
    result = load_module().audit(payload)
    assert result["status"] == "FAIL_CONTRACT_AUDIT"
