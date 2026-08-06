from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def load_module():
    path = ROOT / "scripts" / "run_g10_ce_coverage_audit.py"
    spec = importlib.util.spec_from_file_location("g10", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract() -> dict:
    return json.loads(
        (ROOT / "protocols" / "G10_CE_COVERAGE_CONTRACT.json").read_text()
    )


def test_repository_contract_is_inconclusive_not_failed() -> None:
    result = load_module().audit(contract())
    assert result["status"] == "INCONCLUSIVE_TWO_DIMENSIONAL_COMMON_DOMAIN"
    assert result["density_resolved_exact_overlap_K"] == []
    assert result["fixed_density_continuous_overlap_K"] == [110.0, 195.0]
    assert result["fixed_density_overlap_is_two_dimensional"] is False
    assert result["fit_allowed"] is False


def test_theory_figure_cannot_be_promoted() -> None:
    payload = contract()
    for item in payload["published_measurement_map"]:
        if item["figure"] == "Fig_S22":
            item["role"] = "MEASURED_INPUT"
    result = load_module().audit(payload)
    assert result["status"] == "FAIL_CONTRACT_AUDIT"
    assert any("theory only" in error for error in result["errors"])


def test_bad_pin_is_rejected() -> None:
    payload = contract()
    payload["source"]["supplement_sha256"] = "0" * 64
    result = load_module().audit(payload)
    assert result["status"] == "FAIL_CONTRACT_AUDIT"
