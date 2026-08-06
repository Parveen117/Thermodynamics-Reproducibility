from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_SHA256 = "b60cec3dcec1468d9885f00bfa53912f9259a755992c7f247234aca8bb6d3b0b"


def audit(contract: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    source = contract.get("source", {})
    if source.get("supplement_sha256") != EXPECTED_SHA256:
        errors.append("unexpected Block supplement SHA-256")
    if source.get("supplement_page_count") != 21:
        errors.append("unexpected Block supplement page count")
    if source.get("data_availability") != (
        "available from the corresponding author on reasonable request"
    ):
        errors.append("data-availability contract changed")

    base = contract.get("base_chart", {})
    candidate = contract.get("candidate_chart", {})
    base_coordinates = base.get("coordinates", [])
    candidate_coordinates = candidate.get("coordinates", [])
    coordinate_aligned = base_coordinates == candidate_coordinates

    if candidate.get("lattice_temperature_K") != 300.0:
        errors.append("Block lattice temperature must remain frozen at 300 K")
    if candidate.get("temperature_coordinate_matches_base_chart") is not False:
        errors.append("transient electron temperature must not be typed as base temperature")

    figures = {
        item.get("figure"): item
        for item in contract.get("figure_typing", [])
        if isinstance(item, dict)
    }
    required_figures = {
        "Fig_2e",
        "Fig_3e_f",
        "Fig_3g_h",
        "Supplementary_Fig_5",
        "Supplementary_Fig_9",
        "Extended_Data_Fig_1",
    }
    missing = sorted(required_figures - set(figures))
    if missing:
        errors.append(f"missing figure contracts: {missing}")
    if figures.get("Fig_3g_h", {}).get("role") != (
        "THEORY_CALCULATED_DIFFUSIVITY_SURFACES"
    ):
        errors.append("Fig_3g_h must remain typed as calculated theory")
    if figures.get("Fig_3g_h", {}).get("fit_allowed") is not False:
        errors.append("Fig_3g_h must remain excluded from experimental fitting")
    if figures.get("Extended_Data_Fig_1", {}).get("extrapolation_present") is not True:
        errors.append("Extended Data Fig. 1 extrapolation must remain declared")

    gate = contract.get("replacement_gate", {})
    required_false = [
        "raw_spatiotemporal_maps_publicly_machine_readable",
        "pointwise_measured_D_Te_n_table_publicly_verified",
        "power_to_Te_calibration_covariance_frozen",
        "gate_to_density_calibration_covariance_frozen",
        "focus_width_and_IRF_covariance_frozen",
        "state_variable_alignment_with_base_chart",
        "theory_surfaces_allowed_as_experimental_data",
    ]
    for key in required_false:
        if gate.get(key) is not False:
            errors.append(f"replacement gate {key} must remain false")

    measured_surface_ready = all(
        gate.get(key) is True
        for key in (
            "raw_spatiotemporal_maps_publicly_machine_readable",
            "pointwise_measured_D_Te_n_table_publicly_verified",
            "power_to_Te_calibration_covariance_frozen",
            "gate_to_density_calibration_covariance_frozen",
            "focus_width_and_IRF_covariance_frozen",
            "state_variable_alignment_with_base_chart",
        )
    )

    if errors:
        status = "FAIL_CONTRACT_AUDIT"
    elif measured_surface_ready and coordinate_aligned:
        status = "PASS_DE_REPLACEMENT_COVERAGE"
    else:
        status = "INCONCLUSIVE_STATE_VARIABLE_ALIGNMENT_AND_MEASURED_SURFACE"

    return {
        "campaign": contract.get("campaign"),
        "status": status,
        "errors": errors,
        "supplement_pin_verified": not any(
            "supplement" in error for error in errors
        ),
        "base_temperature_coordinate": (
            base_coordinates[0] if base_coordinates else None
        ),
        "candidate_temperature_coordinate": (
            candidate_coordinates[0] if candidate_coordinates else None
        ),
        "temperature_coordinates_identical": coordinate_aligned,
        "lattice_temperature_K": candidate.get("lattice_temperature_K"),
        "primary_measured_observable": contract.get(
            "measurement_chain", {}
        ).get("primary_observable"),
        "direct_dense_measured_diffusivity_surface": False,
        "calculated_diffusivity_surface_excluded": True,
        "author_data_required": True,
        "two_dimensional_replacement_ready": measured_surface_ready,
        "fit_allowed": False,
        "experimental_plucker_significance_computed": False,
        "decisive_reasons": [
            "The base channels use an equilibrium sample-temperature coordinate, while Block 2021 varies a transient peak electron temperature inferred from optical power at fixed 300 K lattice temperature.",
            "The primary measurement is Delta I_TE spatial-temporal response and fitted width, not a public pointwise measured D(T_e,n) table.",
            "The complete Fig. 3g-h diffusivity surfaces are Boltzmann calculations and cannot be promoted to experimental response channels.",
            "Power, density, focus-width and instrument-response covariance are not frozen from public machine-readable data."
        ],
        "selected_next_action": "REQUEST_RAW_MAPS_FIT_OUTPUTS_AND_CALIBRATIONS",
        "next_stage": "G12_TEMPERATURE_COORDINATE_REDESIGN",
        "claim_boundary": contract.get("claim_boundary"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "contract",
        nargs="?",
        type=Path,
        default=Path("protocols/G11_DE_COVERAGE_CONTRACT.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/G11_DE_COVERAGE_CERTIFICATE.json"),
    )
    args = parser.parse_args()

    result = audit(json.loads(args.contract.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["status"] == "FAIL_CONTRACT_AUDIT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
