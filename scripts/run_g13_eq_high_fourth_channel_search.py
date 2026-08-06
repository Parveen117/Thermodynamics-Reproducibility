from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_SECTOR = "EQ_HIGH_TN"
EXPECTED_COORDINATES = [
    "equilibrium_sample_temperature_K",
    "carrier_density_1e12_cm_minus_2",
]
EXPECTED_EXISTING_CHANNELS = [
    "G_CONDUCTANCE",
    "KE_THERMAL_CONDUCTANCE",
    "SIGMA_Q",
]


def audit(contract: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    sector = contract.get("selected_sector", {})
    if sector.get("sector_id") != EXPECTED_SECTOR:
        errors.append("G13 must remain inside EQ_HIGH_TN")
    if sector.get("coordinates") != EXPECTED_COORDINATES:
        errors.append("selected coordinates changed")
    if sector.get("temperature_range_K") != [110.0, 260.0]:
        errors.append("selected temperature range changed")
    if sector.get("existing_channels") != EXPECTED_EXISTING_CHANNELS:
        errors.append("existing channel set changed")
    if sector.get("required_new_channel_count") != 1:
        errors.append("exactly one fourth channel is required")

    qualification = contract.get("qualification_contract", {})
    required_true = [
        "equilibrium_measurement_required",
        "directly_measured_response_required",
        "carrier_density_resolved_required",
        "machine_readable_numerical_data_required_before_fit",
        "pointwise_uncertainty_or_reconstructible_covariance_required",
        "no_temperature_extrapolation",
        "no_density_extrapolation",
        "no_theory_curve_as_measurement",
        "no_channel_reconstruction_from_existing_G_KE_SIGMAQ",
        "no_cross_sector_temperature_alias",
    ]
    for key in required_true:
        if qualification.get(key) is not True:
            errors.append(f"qualification gate {key} must remain true")
    if qualification.get("minimum_distinct_temperatures_in_target_window") != 3:
        errors.append("minimum target-window temperature count must remain three")
    if qualification.get("minimum_distinct_densities_per_temperature") != 5:
        errors.append("minimum density count must remain five")

    candidates = {
        item.get("candidate_id"): item
        for item in contract.get("candidates", [])
        if isinstance(item, dict)
    }
    required_candidates = {
        "SEEBECK_WANG_SHI_2011",
        "SEEBECK_ZUEV_KIM_2009",
        "QUANTUM_CAPACITANCE_XIA_2009",
        "HALL_COEFFICIENT_OR_CARRIER_DENSITY",
        "RAMAN_G_OR_2D_PEAK_EQUILIBRIUM",
        "TRANSIENT_PHOTOTHERMOELECTRIC_OR_SPIN_RESPONSE",
    }
    missing = sorted(required_candidates - set(candidates))
    if missing:
        errors.append(f"missing candidate contracts: {missing}")

    wang = candidates.get("SEEBECK_WANG_SHI_2011", {})
    if wang.get("decision") != "SELECT_PRIMARY_ACQUISITION_TARGET":
        errors.append("Wang-Shi Seebeck candidate must remain primary")
    if wang.get("public_machine_readable_arrays_verified") is not False:
        errors.append("Wang-Shi public array gate must remain false")
    if wang.get("pointwise_uncertainty_verified") is not False:
        errors.append("Wang-Shi uncertainty gate must remain false")

    zuev = candidates.get("SEEBECK_ZUEV_KIM_2009", {})
    target_temperatures = sorted(
        float(value) for value in zuev.get("verified_target_window_temperatures_K", [])
    )
    minimum_temperatures = int(
        qualification.get("minimum_distinct_temperatures_in_target_window", 0)
    )
    zuev_temperature_gate = len(set(target_temperatures)) >= minimum_temperatures
    if zuev.get("minimum_temperature_gate_pass") is not False:
        errors.append("Zuev temperature gate must remain false")
    if zuev_temperature_gate:
        errors.append("Zuev target-window temperature count unexpectedly passed")

    capacitance = candidates.get("QUANTUM_CAPACITANCE_XIA_2009", {})
    if capacitance.get("temperature_resolved_target_window") is not False:
        errors.append("Xia quantum-capacitance temperature gate must remain false")

    hall = candidates.get("HALL_COEFFICIENT_OR_CARRIER_DENSITY", {})
    if hall.get("decision") != "REJECT_AS_COORDINATE_OR_CALIBRATION_CHANNEL":
        errors.append("Hall-density candidate must remain rejected as a coordinate duplicate")

    transient = candidates.get("TRANSIENT_PHOTOTHERMOELECTRIC_OR_SPIN_RESPONSE", {})
    if transient.get("decision") != "REJECT_CROSS_SECTOR":
        errors.append("transient or different-material candidate must remain cross-sector")

    selection = contract.get("selection", {})
    fit_ready = int(selection.get("fit_ready_candidate_count", -1))
    if selection.get("selected_candidate_id") != "SEEBECK_WANG_SHI_2011":
        errors.append("selected fourth-channel target changed")
    if selection.get("secondary_candidate_id") != "SEEBECK_ZUEV_KIM_2009":
        errors.append("secondary target changed")
    if fit_ready != 0:
        errors.append("no candidate may be declared fit-ready in G13")
    if selection.get("fit_allowed") is not False:
        errors.append("fit must remain forbidden")
    if selection.get("experimental_plucker_significance_computed") is not False:
        errors.append("G13 must not compute Pluecker significance")

    if errors:
        status = "FAIL_EQ_HIGH_FOURTH_CHANNEL_SEARCH"
    else:
        status = "INCONCLUSIVE_EQ_HIGH_FOURTH_CHANNEL_ACQUISITION"

    return {
        "campaign": contract.get("campaign"),
        "status": status,
        "errors": errors,
        "selected_sector_id": sector.get("sector_id"),
        "selected_coordinates": sector.get("coordinates"),
        "selected_temperature_range_K": sector.get("temperature_range_K"),
        "existing_channel_count": len(sector.get("existing_channels", [])),
        "selected_candidate_id": selection.get("selected_candidate_id"),
        "selected_observable": wang.get("observable"),
        "selected_candidate_equilibrium": (
            wang.get("measurement_class") == "DIRECT_EQUILIBRIUM_THERMOELECTRIC_RESPONSE"
        ),
        "selected_candidate_machine_readable_ready": bool(
            wang.get("public_machine_readable_arrays_verified")
        ),
        "selected_candidate_uncertainty_ready": bool(
            wang.get("pointwise_uncertainty_verified")
        ),
        "secondary_candidate_id": selection.get("secondary_candidate_id"),
        "secondary_target_window_temperatures_K": target_temperatures,
        "secondary_temperature_gate_pass": zuev_temperature_gate,
        "fit_ready_candidate_count": fit_ready,
        "fourth_channel_ready": fit_ready > 0,
        "fit_allowed": False,
        "experimental_plucker_significance_computed": False,
        "decisive_reasons": [
            "Equilibrium Seebeck coefficient is the strongest directly measured and conceptually independent fourth-response candidate.",
            "The primary Wang-Shi source reports broad temperature and carrier-density coverage, but public machine-readable arrays and covariance are not verified.",
            "The Zuev-Kim source provides clearly verified density sweeps at only 150 K and 200 K inside the 110-260 K sector, below the frozen three-temperature gate.",
            "Quantum capacitance lacks a verified target-window temperature-density surface, Hall density duplicates a chart coordinate, and transient or Raman candidates fail sector or two-dimensional coverage gates.",
        ],
        "required_author_data": selection.get("required_author_data", []),
        "next_stage": contract.get("next_stage"),
        "claim_boundary": contract.get("claim_boundary"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "contract",
        nargs="?",
        type=Path,
        default=Path("protocols/G13_EQ_HIGH_FOURTH_CHANNEL_SEARCH.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/G13_EQ_HIGH_FOURTH_CHANNEL_CERTIFICATE.json"),
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
