from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


def load_validator():
    script = Path(__file__).parents[1] / "scripts" / "validate_g01_source_ledger.py"
    spec = importlib.util.spec_from_file_location("g01_validator", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def repository_ledger() -> dict:
    path = Path(__file__).parents[1] / "graphene" / "G01_SOURCE_LEDGER.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_repository_ledger_passes_without_significance_claim() -> None:
    module = load_validator()
    result = module.validate_ledger(repository_ledger())

    assert result["status"] == "PASS_FEASIBILITY_LEDGER"
    assert result["significance_computed"] is False
    assert result["machine_readable_ready_channels"] == []
    assert "electrical_conductivity" in result["represented_channels"]
    assert "electronic_thermal_conductivity" in result["represented_channels"]


def test_multi_channel_source_is_counted_without_duplication() -> None:
    module = load_validator()
    ledger = repository_ledger()
    source = next(
        entry
        for entry in ledger["sources"]
        if entry["source_id"] == "G01_SIGMA_KAPPA_MAJUMDAR_2025"
    )

    channels = module.source_channels(source, source["source_id"], [])

    assert channels == {
        "electrical_conductivity",
        "electronic_thermal_conductivity",
    }


def test_computed_significance_is_rejected_at_feasibility_stage() -> None:
    module = load_validator()
    ledger = repository_ledger()
    ledger["significance_computed"] = True

    result = module.validate_ledger(ledger)

    assert result["status"] == "FAIL_FEASIBILITY_LEDGER"
    assert any("must not claim" in error for error in result["errors"])


def test_thermoml_pristine_archive_claim_is_rejected() -> None:
    module = load_validator()
    ledger = repository_ledger()
    ledger["thermoml"]["pristine_monolayer_four_surface_archive"] = True

    result = module.validate_ledger(ledger)

    assert result["status"] == "FAIL_FEASIBILITY_LEDGER"
    assert any("ThermoML" in error for error in result["errors"])


def test_source_cannot_declare_singular_and_plural_channels() -> None:
    module = load_validator()
    ledger = copy.deepcopy(repository_ledger())
    ledger["sources"][0]["channels"] = ["electronic_heat_capacity"]

    result = module.validate_ledger(ledger)

    assert result["status"] == "FAIL_FEASIBILITY_LEDGER"
    assert any("both channel and channels" in error for error in result["errors"])
