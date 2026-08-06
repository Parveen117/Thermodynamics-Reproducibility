from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "run_g13_eq_high_fourth_channel_search.py"
    spec = importlib.util.spec_from_file_location("g13_search", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_contract() -> dict:
    path = Path(__file__).parents[1] / "protocols" / "G13_EQ_HIGH_FOURTH_CHANNEL_SEARCH.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_contract_is_inconclusive_not_fit_ready() -> None:
    module = load_module()
    result = module.audit(load_contract())
    assert result["status"] == "INCONCLUSIVE_EQ_HIGH_FOURTH_CHANNEL_ACQUISITION"
    assert result["selected_candidate_id"] == "SEEBECK_WANG_SHI_2011"
    assert result["fourth_channel_ready"] is False
    assert result["fit_allowed"] is False


def test_zuev_two_temperature_support_fails_three_temperature_gate() -> None:
    module = load_module()
    result = module.audit(load_contract())
    assert result["secondary_target_window_temperatures_K"] == [150.0, 200.0]
    assert result["secondary_temperature_gate_pass"] is False


def test_cross_sector_candidate_cannot_be_promoted() -> None:
    module = load_module()
    contract = load_contract()
    for candidate in contract["candidates"]:
        if candidate["candidate_id"] == "TRANSIENT_PHOTOTHERMOELECTRIC_OR_SPIN_RESPONSE":
            candidate["decision"] = "SELECT_PRIMARY_ACQUISITION_TARGET"
    result = module.audit(contract)
    assert result["status"] == "FAIL_EQ_HIGH_FOURTH_CHANNEL_SEARCH"
    assert any("cross-sector" in error for error in result["errors"])


def test_hall_density_cannot_duplicate_chart_coordinate() -> None:
    module = load_module()
    contract = load_contract()
    for candidate in contract["candidates"]:
        if candidate["candidate_id"] == "HALL_COEFFICIENT_OR_CARRIER_DENSITY":
            candidate["decision"] = "SELECT_PRIMARY_ACQUISITION_TARGET"
    result = module.audit(contract)
    assert result["status"] == "FAIL_EQ_HIGH_FOURTH_CHANNEL_SEARCH"
    assert any("coordinate duplicate" in error for error in result["errors"])


def test_machine_readable_and_uncertainty_gates_cannot_be_skipped() -> None:
    module = load_module()
    contract = load_contract()
    contract["qualification_contract"]["machine_readable_numerical_data_required_before_fit"] = False
    contract["qualification_contract"]["pointwise_uncertainty_or_reconstructible_covariance_required"] = False
    result = module.audit(contract)
    assert result["status"] == "FAIL_EQ_HIGH_FOURTH_CHANNEL_SEARCH"
    assert len(result["errors"]) >= 2
