from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "run_g12_temperature_coordinate_redesign.py"
    spec = importlib.util.spec_from_file_location("g12_redesign", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def repository_contract() -> dict:
    path = Path(__file__).parents[1] / "protocols" / "G12_TEMPERATURE_COORDINATE_REDESIGN.json"
    return json.loads(path.read_text(encoding="utf-8"))


def sector(contract: dict, sector_id: str) -> dict:
    return next(item for item in contract["sectors"] if item["sector_id"] == sector_id)


def test_repository_contract_selects_equilibrium_high_temperature_sector() -> None:
    module = load_module()
    result = module.audit(repository_contract())

    assert result["status"] == "PASS_SECTORIZED_TEMPERATURE_REDESIGN"
    assert result["selected_sector_id"] == "EQ_HIGH_TN"
    assert result["selected_sector_dimension"] == 2
    assert result["selected_existing_channel_count"] == 3
    assert result["fit_allowed"] is False
    assert result["experimental_plucker_significance_computed"] is False


def test_transient_temperature_cannot_be_aliased_to_equilibrium_temperature() -> None:
    module = load_module()
    contract = copy.deepcopy(repository_contract())
    contract["temperature_types"]["transient_peak_electron_temperature_K"][
        "not_identical_to"
    ] = "transient_peak_electron_temperature_K"

    result = module.audit(contract)

    assert result["status"] == "FAIL_TEMPERATURE_COORDINATE_CONTRACT"
    assert any("transient electron temperature" in error for error in result["errors"])


def test_reduced_temperature_cannot_cross_the_dirac_point_globally() -> None:
    module = load_module()
    contract = copy.deepcopy(repository_contract())
    contract["temperature_types"]["reduced_temperature_T_over_TF"][
        "global_graphene_chart_allowed"
    ] = True
    sector(contract, "REDUCED_DEGENERACY_T_OVER_TF_N")["theorem_eligible"] = True

    result = module.audit(contract)

    assert result["status"] == "FAIL_TEMPERATURE_COORDINATE_CONTRACT"
    assert any("T/TF" in error or "reduced-degeneracy" in error for error in result["errors"])


def test_three_dimensional_nonequilibrium_chart_is_not_silently_projected() -> None:
    module = load_module()
    contract = copy.deepcopy(repository_contract())
    nonequilibrium = sector(contract, "NONEQUILIBRIUM_TE_TL_N")
    nonequilibrium["dimension"] = 2
    nonequilibrium["theorem_eligible"] = True

    result = module.audit(contract)

    assert result["status"] == "FAIL_TEMPERATURE_COORDINATE_CONTRACT"
    assert any("nonequilibrium chart" in error for error in result["errors"])


def test_cross_sector_brackets_remain_forbidden() -> None:
    module = load_module()
    contract = copy.deepcopy(repository_contract())
    contract["theorem_contract"]["cross_sector_brackets_forbidden"] = False
    sector(contract, "TRANSIENT_HOT_TE_N")[
        "join_with_equilibrium_sector_allowed"
    ] = True

    result = module.audit(contract)

    assert result["status"] == "FAIL_TEMPERATURE_COORDINATE_CONTRACT"
    assert any("cross-sector" in error or "must not be joined" in error for error in result["errors"])


def test_three_existing_channels_do_not_authorize_a_fit() -> None:
    module = load_module()
    contract = copy.deepcopy(repository_contract())
    sector(contract, "EQ_HIGH_TN")["fit_allowed"] = True
    contract["current_gate"]["fit_allowed"] = True

    result = module.audit(contract)

    assert result["status"] == "FAIL_TEMPERATURE_COORDINATE_CONTRACT"
    assert any("fit" in error for error in result["errors"])
