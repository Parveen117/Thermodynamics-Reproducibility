from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "validate_g09_replacement.py"
    spec = importlib.util.spec_from_file_location("g09_validator", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ready_candidate() -> dict:
    return {
        "candidate_id": "READY",
        "publication_independent": True,
        "controls_reported": ["electronic_temperature", "carrier_density"],
        "machine_readable_table_verified": True,
        "reported_uncertainty_or_covariance_ready": True,
    }


def base_contract(candidate: dict) -> dict:
    return {
        "campaign": "G09_COMMON_DOMAIN_CHANNEL_REPLACEMENT",
        "base_channels": ["G_CONDUCTANCE", "KE_THERMAL_CONDUCTANCE", "SIGMA_Q"],
        "required_temperature_range_K": [110.0, 260.0],
        "candidates": [candidate],
    }


def test_complete_independent_candidate_is_ready() -> None:
    module = load_module()
    result = module.validate_contract(base_contract(ready_candidate()))
    assert result["status"] == "READY_FOR_FOUR_CHANNEL_FIT"
    assert result["ready_candidates"] == ["READY"]


def test_pdf_only_candidate_remains_not_ready() -> None:
    module = load_module()
    candidate = ready_candidate()
    candidate["machine_readable_table_verified"] = False
    result = module.validate_contract(base_contract(candidate))
    assert result["status"] == "INCONCLUSIVE_REPLACEMENT_DATA_ACQUISITION"
    assert any(
        "machine-readable" in error
        for error in result["candidate_results"][0]["errors"]
    )


def test_circular_join_is_rejected() -> None:
    module = load_module()
    candidate = ready_candidate()
    candidate["requires_join_through_existing_channel"] = "KE_THERMAL_CONDUCTANCE"
    candidate["algebraically_independent_of_base_channels"] = False
    result = module.validate_contract(base_contract(candidate))
    assert result["status"] == "INCONCLUSIVE_REPLACEMENT_DATA_ACQUISITION"
    assert any(
        "circularly" in error
        for error in result["candidate_results"][0]["errors"]
    )
