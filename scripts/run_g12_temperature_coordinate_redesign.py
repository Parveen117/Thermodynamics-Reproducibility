from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_SECTORS = {
    "EQ_HIGH_TN",
    "EQ_LOW_TN",
    "TRANSIENT_HOT_TE_N",
    "REDUCED_DEGENERACY_T_OVER_TF_N",
    "NONEQUILIBRIUM_TE_TL_N",
}


def _sector_map(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("sector_id")): item
        for item in contract.get("sectors", [])
        if isinstance(item, dict) and item.get("sector_id")
    }


def audit(contract: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    if contract.get("campaign") != "G12_TEMPERATURE_COORDINATE_REDESIGN":
        errors.append("unexpected campaign identifier")

    theorem = contract.get("theorem_contract", {})
    if theorem.get("required_state_dimension") != 2:
        errors.append("the frozen theorem must remain two-dimensional")
    if theorem.get("single_smooth_sector_required") is not True:
        errors.append("single-sector requirement must remain active")
    if theorem.get("cross_sector_brackets_forbidden") is not True:
        errors.append("cross-sector brackets must remain forbidden")
    if theorem.get("hidden_protocol_variable_substitution_forbidden") is not True:
        errors.append("hidden protocol substitution must remain forbidden")

    temperatures = contract.get("temperature_types", {})
    equilibrium_name = "equilibrium_sample_temperature_K"
    transient_name = "transient_peak_electron_temperature_K"
    lattice_name = "lattice_temperature_K"

    transient = temperatures.get(transient_name, {})
    lattice = temperatures.get(lattice_name, {})
    reduced = temperatures.get("reduced_temperature_T_over_TF", {})

    if transient.get("not_identical_to") != equilibrium_name:
        errors.append("transient electron temperature must remain distinct from equilibrium temperature")
    if lattice.get("not_identical_to") != transient_name:
        errors.append("lattice temperature must remain distinct from transient electron temperature")
    if reduced.get("global_graphene_chart_allowed") is not False:
        errors.append("T/TF must not be allowed as a global graphene chart")
    if reduced.get("singular_at_carrier_density_zero") is not True:
        errors.append("T/TF singularity at n=0 must remain declared")

    sectors = _sector_map(contract)
    missing = sorted(EXPECTED_SECTORS - set(sectors))
    if missing:
        errors.append(f"missing temperature sectors: {missing}")

    eq_high = sectors.get("EQ_HIGH_TN", {})
    eq_low = sectors.get("EQ_LOW_TN", {})
    transient_hot = sectors.get("TRANSIENT_HOT_TE_N", {})
    reduced_sector = sectors.get("REDUCED_DEGENERACY_T_OVER_TF_N", {})
    nonequilibrium = sectors.get("NONEQUILIBRIUM_TE_TL_N", {})

    if eq_high.get("coordinates") != [
        equilibrium_name,
        "carrier_density_1e12_cm_minus_2",
    ]:
        errors.append("EQ_HIGH_TN coordinates changed")
    if eq_high.get("dimension") != 2 or eq_high.get("theorem_eligible") is not True:
        errors.append("EQ_HIGH_TN must remain a theorem-eligible two-dimensional sector")
    if eq_high.get("temperature_window_K") != [110.0, 260.0]:
        errors.append("EQ_HIGH_TN temperature window changed")
    if eq_high.get("existing_channel_count") != 3:
        errors.append("EQ_HIGH_TN must retain exactly three existing channels")
    if len(eq_high.get("existing_channels", [])) != 3:
        errors.append("EQ_HIGH_TN channel list must contain three entries")
    if eq_high.get("machine_readable_source_data") is not True:
        errors.append("EQ_HIGH_TN machine-readable provenance must remain declared")
    if eq_high.get("contains_dirac_point_support") is not True:
        errors.append("EQ_HIGH_TN Dirac-point support must remain declared")
    if eq_high.get("fourth_channel_ready") is not False:
        errors.append("EQ_HIGH_TN fourth channel must not be marked ready")
    if eq_high.get("fit_allowed") is not False:
        errors.append("EQ_HIGH_TN fit must remain blocked")

    if eq_low.get("dimension") != 2 or eq_low.get("theorem_eligible") is not True:
        errors.append("EQ_LOW_TN must remain a separate eligible two-dimensional sector")
    if eq_low.get("selected_primary_sector") is not False:
        errors.append("EQ_LOW_TN must not be selected as the primary sector")

    if transient_hot.get("coordinates") != [
        transient_name,
        "carrier_density_1e12_cm_minus_2",
    ]:
        errors.append("TRANSIENT_HOT_TE_N coordinates changed")
    if transient_hot.get("fixed_lattice_temperature_K") != 300.0:
        errors.append("transient sector lattice temperature must remain 300 K")
    if transient_hot.get("join_with_equilibrium_sector_allowed") is not False:
        errors.append("transient and equilibrium sectors must not be joined")
    if transient_hot.get("selected_primary_sector") is not False:
        errors.append("transient sector must not become the current primary sector")

    if reduced_sector.get("dimension") != 2:
        errors.append("reduced-degeneracy candidate must remain two-dimensional")
    if reduced_sector.get("theorem_eligible") is not False:
        errors.append("reduced-degeneracy chart must remain ineligible globally")
    if reduced_sector.get("singular_at_carrier_density_zero") is not True:
        errors.append("reduced-degeneracy sector must retain n=0 singularity")
    if reduced_sector.get("join_equilibrium_and_transient_sectors") is not False:
        errors.append("reduced coordinate must not join equilibrium and transient sectors")

    if nonequilibrium.get("dimension") != 3:
        errors.append("honest nonequilibrium chart must remain three-dimensional")
    if nonequilibrium.get("theorem_eligible") is not False:
        errors.append("three-dimensional nonequilibrium chart must remain theorem-ineligible")
    if nonequilibrium.get("physically_honest_for_mixed_temperature_experiments") is not True:
        errors.append("three-dimensional chart must remain the honest mixed-temperature description")

    selection = contract.get("selection", {})
    selected_id = selection.get("selected_sector_id")
    selected = sectors.get(str(selected_id), {})
    selected_flags = [
        sector_id
        for sector_id, sector in sectors.items()
        if sector.get("selected_primary_sector") is True
    ]
    if selected_id != "EQ_HIGH_TN":
        errors.append("G12 must select EQ_HIGH_TN")
    if selected_flags != ["EQ_HIGH_TN"]:
        errors.append(f"exactly EQ_HIGH_TN must carry the primary-selection flag: {selected_flags}")
    if selected.get("dimension") != theorem.get("required_state_dimension"):
        errors.append("selected sector dimension is incompatible with the theorem")
    if selected.get("theorem_eligible") is not True:
        errors.append("selected sector must be theorem-eligible")

    rejected_shortcuts = set(selection.get("rejected_shortcuts", []))
    required_shortcuts = {
        "IDENTIFY_TRANSIENT_TE_WITH_EQUILIBRIUM_T",
        "USE_T_OVER_TF_AS_GLOBAL_CHART_ACROSS_N_ZERO",
        "PROJECT_TE_TL_N_TO_TWO_DIMENSIONS_WITHOUT_A_CLOSURE_THEOREM",
        "COMPUTE_CROSS_SECTOR_BRACKETS",
    }
    if not required_shortcuts.issubset(rejected_shortcuts):
        errors.append("one or more forbidden coordinate shortcuts were removed")

    gate = contract.get("current_gate", {})
    if gate.get("selected_sector_has_four_channels") is not False:
        errors.append("selected sector must not be represented as four-channel ready")
    if gate.get("uncertainty_model_frozen") is not False:
        errors.append("uncertainty model must remain unfrozen")
    if gate.get("independent_six_bracket_contract_ready") is not False:
        errors.append("independent bracket contract must remain unready")
    if gate.get("fit_allowed") is not False:
        errors.append("fit must remain forbidden")
    if gate.get("experimental_plucker_significance_computed") is not False:
        errors.append("G12 must not compute experimental significance")

    if errors:
        status = "FAIL_TEMPERATURE_COORDINATE_CONTRACT"
    else:
        status = "PASS_SECTORIZED_TEMPERATURE_REDESIGN"

    return {
        "campaign": contract.get("campaign"),
        "status": status,
        "errors": errors,
        "selected_sector_id": selected_id,
        "selected_coordinates": selected.get("coordinates"),
        "selected_temperature_window_K": selected.get("temperature_window_K"),
        "selected_sector_dimension": selected.get("dimension"),
        "selected_existing_channels": selected.get("existing_channels", []),
        "selected_existing_channel_count": selected.get("existing_channel_count"),
        "selected_sector_regular_at_dirac_point": bool(
            selected.get("contains_dirac_point_support")
        ),
        "equilibrium_and_transient_temperatures_identified": False,
        "global_T_over_TF_chart_allowed": False,
        "three_dimensional_nonequilibrium_chart_reduced_to_two_dimensions": False,
        "cross_sector_brackets_allowed": False,
        "fourth_channel_ready": False,
        "fit_allowed": False,
        "experimental_plucker_significance_computed": False,
        "sector_decisions": {
            "EQ_HIGH_TN": "SELECT_PRIMARY",
            "EQ_LOW_TN": "KEEP_AS_SEPARATE_FALLBACK_SECTOR",
            "TRANSIENT_HOT_TE_N": "SEPARATE_COMPANION_CAMPAIGN",
            "REDUCED_DEGENERACY_T_OVER_TF_N": "REJECT_AS_GLOBAL_CHART",
            "NONEQUILIBRIUM_TE_TL_N": "PHYSICALLY_HONEST_BUT_OUTSIDE_TWO_DIMENSIONAL_THEOREM",
        },
        "next_requirement": selected.get("next_requirement"),
        "next_stage": contract.get("next_stage"),
        "claim_boundary": contract.get("claim_boundary"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "contract",
        nargs="?",
        type=Path,
        default=Path("protocols/G12_TEMPERATURE_COORDINATE_REDESIGN.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/G12_TEMPERATURE_COORDINATE_CERTIFICATE.json"),
    )
    args = parser.parse_args()

    result = audit(json.loads(args.contract.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["status"].startswith("FAIL_") else 0


if __name__ == "__main__":
    raise SystemExit(main())
