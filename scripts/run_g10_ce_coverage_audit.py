from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_SHA256 = "f3665ddf503d23400452d10366a39e783ab58ceabe5c80b04a03f2c375c7ef05"


def interval_intersection(a: list[float], b: list[float]) -> list[float] | None:
    lower = max(float(a[0]), float(b[0]))
    upper = min(float(a[1]), float(b[1]))
    return [lower, upper] if lower <= upper else None


def audit(contract: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    source = contract.get("source", {})
    if source.get("supplement_sha256") != EXPECTED_SHA256:
        errors.append("unexpected Aamir supplement SHA-256")
    if source.get("supplement_page_count") != 31:
        errors.append("unexpected Aamir supplement page count")

    measurement_map = contract.get("published_measurement_map", [])
    by_figure = {
        item.get("figure"): item
        for item in measurement_map
        if isinstance(item, dict)
    }
    required_figures = {
        "Fig_3A",
        "Fig_3B",
        "Fig_4A",
        "Fig_4B",
        "Fig_S18",
        "Fig_S20",
        "Fig_S22",
    }
    missing = sorted(required_figures - set(by_figure))
    if missing:
        errors.append(f"missing figure contracts: {missing}")
    if by_figure.get("Fig_S20", {}).get("fit_allowed") is not False:
        errors.append("Fig_S20 must remain excluded from the primary fit")
    if by_figure.get("Fig_S22", {}).get("role") != "THEORY_ONLY":
        errors.append("Fig_S22 must remain typed as theory only")

    gate = contract.get("replacement_gate", {})
    base_range = [float(x) for x in gate.get("base_temperature_range_K", [])]
    density_temps = sorted(
        float(x)
        for x in gate.get("density_resolved_ce_temperature_support_K", [])
    )
    fixed_n_range = [
        float(x)
        for x in gate.get("fixed_density_ce_temperature_range_K", [])
    ]

    if len(base_range) != 2 or len(fixed_n_range) != 2:
        errors.append("temperature ranges must have two endpoints")
        base_density_overlap: list[float] = []
        fixed_n_overlap = None
    else:
        base_density_overlap = [
            temperature
            for temperature in density_temps
            if base_range[0] <= temperature <= base_range[1]
        ]
        fixed_n_overlap = interval_intersection(base_range, fixed_n_range)

    two_dimensional_ready = len(base_density_overlap) >= int(
        gate.get("minimum_distinct_temperatures_in_overlap", 3)
    )

    if errors:
        status = "FAIL_CONTRACT_AUDIT"
    elif two_dimensional_ready:
        status = "PASS_CE_REPLACEMENT_COVERAGE"
    else:
        status = "INCONCLUSIVE_TWO_DIMENSIONAL_COMMON_DOMAIN"

    return {
        "campaign": contract.get("campaign"),
        "status": status,
        "errors": errors,
        "supplement_pin_verified": not any(
            "supplement" in error for error in errors
        ),
        "base_temperature_range_K": base_range,
        "density_resolved_ce_temperature_support_K": density_temps,
        "density_resolved_exact_overlap_K": base_density_overlap,
        "fixed_density_ce_temperature_range_K": fixed_n_range,
        "fixed_density_continuous_overlap_K": fixed_n_overlap,
        "fixed_density_overlap_is_two_dimensional": False,
        "two_dimensional_replacement_ready": two_dimensional_ready,
        "fit_allowed": False,
        "experimental_plucker_significance_computed": False,
        "decisive_reason": (
            "Measured density-resolved heat-capacity curves stop at 100 K, "
            "below the 110 K lower bound of the current base-channel range. "
            "The measured 15-195 K temperature sweep is at one fixed carrier "
            "density and therefore cannot supply local derivatives in both T and n."
        ),
        "selected_next_action": (
            "REQUEST_OR_DIGITIZE_ADDITIONAL_DENSITY_SWEEPS_AT_110_TO_195_K"
        ),
        "fallback_next_channel": "DE_BLOCK_2021",
        "claim_boundary": contract.get("claim_boundary"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "contract",
        nargs="?",
        type=Path,
        default=Path("protocols/G10_CE_COVERAGE_CONTRACT.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/G10_CE_COVERAGE_CERTIFICATE.json"),
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
