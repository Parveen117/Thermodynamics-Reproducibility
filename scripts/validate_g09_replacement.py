from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


READY = "READY_FOR_FOUR_CHANNEL_FIT"
NOT_READY = "INCONCLUSIVE_REPLACEMENT_DATA_ACQUISITION"


def candidate_gate(candidate: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    publication_independent = candidate.get("publication_independent") is True
    controls = set(candidate.get("controls_reported", []))
    two_control = (
        "electronic_temperature" in controls
        and (
            "carrier_density" in controls
            or "carrier_density_or_gate_voltage" in controls
        )
    )
    machine_readable = candidate.get("machine_readable_table_verified") is True
    covariance_ready = (
        candidate.get("reported_uncertainty_or_covariance_ready") is True
    )
    circular = (
        candidate.get("algebraically_independent_of_base_channels") is False
        or "requires_join_through_existing_channel" in candidate
    )
    derived_shared = candidate.get("derived_from_shared_transport_and_thermodynamic_inputs") is True

    if not publication_independent:
        warnings.append("candidate is not publication-independent")
    if not two_control:
        errors.append("full temperature-density support is not verified")
    if not machine_readable:
        errors.append("machine-readable numerical surface is not verified")
    if not covariance_ready:
        errors.append("uncertainty or covariance contract is not frozen")
    if circular:
        errors.append("candidate is circularly constructed from a base channel")
    if derived_shared:
        errors.append("candidate is derived from shared transport inputs")

    return {
        "candidate_id": candidate.get("candidate_id"),
        "ready": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def validate_contract(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if payload.get("campaign") != "G09_COMMON_DOMAIN_CHANNEL_REPLACEMENT":
        errors.append("unexpected campaign identifier")
    if payload.get("base_channels") != [
        "G_CONDUCTANCE",
        "KE_THERMAL_CONDUCTANCE",
        "SIGMA_Q",
    ]:
        errors.append("base channel set changed")
    if payload.get("required_temperature_range_K") != [110.0, 260.0]:
        errors.append("required temperature range changed")

    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        errors.append("candidate ledger is empty")
        candidates = []

    candidate_results = [candidate_gate(candidate) for candidate in candidates]
    ready_candidates = [
        result["candidate_id"] for result in candidate_results if result["ready"]
    ]
    status = READY if ready_candidates and not errors else NOT_READY

    return {
        "campaign": "G09_COMMON_DOMAIN_CHANNEL_REPLACEMENT",
        "status": status,
        "errors": errors,
        "candidate_count": len(candidates),
        "ready_candidates": ready_candidates,
        "candidate_results": candidate_results,
        "experimental_plucker_significance_computed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "contract",
        nargs="?",
        type=Path,
        default=Path("protocols/G09_COMMON_DOMAIN_REPLACEMENT.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/G09_REPLACEMENT_AUDIT.json"),
    )
    args = parser.parse_args()

    payload = json.loads(args.contract.read_text(encoding="utf-8"))
    result = validate_contract(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
