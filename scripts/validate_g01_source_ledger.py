from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_CHANNELS = {
    "electronic_heat_capacity",
    "quantum_capacitance",
    "electrical_conductivity",
    "electronic_thermal_diffusivity",
}

EXPECTED_GATE = (
    "TWO_CHANNEL_COMMON_DEVICE_ROUTE_AVAILABLE_BUT_"
    "NO_FOUR_CHANNEL_MACHINE_READABLE_CONTRACT"
)


def source_channels(source: dict[str, Any], source_id: str, errors: list[str]) -> set[str]:
    """Normalize a one-channel or multi-channel source entry."""

    singular = source.get("channel")
    plural = source.get("channels")
    if singular is not None and plural is not None:
        errors.append(f"source {source_id} declares both channel and channels")
        return set()
    if isinstance(singular, str) and singular:
        return {singular}
    if isinstance(plural, list) and plural:
        if not all(isinstance(value, str) and value for value in plural):
            errors.append(f"source {source_id} has invalid channels list")
            return set()
        channels = set(plural)
        if len(channels) != len(plural):
            errors.append(f"source {source_id} repeats a channel")
        return channels
    errors.append(f"source {source_id} lacks channel coverage")
    return set()


def validate_ledger(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("campaign") != "G01_GRAPHENE_FEASIBILITY":
        errors.append("unexpected campaign identifier")
    if payload.get("significance_computed") is not False:
        errors.append("feasibility ledger must not claim a computed significance")
    if payload.get("current_gate") != EXPECTED_GATE:
        errors.append("unexpected current acquisition gate")

    chart = payload.get("chart_target")
    if chart != ["electronic_temperature", "carrier_density"]:
        errors.append("chart target must remain (electronic_temperature, carrier_density)")

    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("source ledger is empty")
        sources = []

    source_ids: set[str] = set()
    represented_channels: set[str] = set()
    raw_ready_channels: set[str] = set()

    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"source {index} is not an object")
            continue
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"source {index} lacks source_id")
            normalized_id = f"index-{index}"
        elif source_id in source_ids:
            errors.append(f"duplicate source_id: {source_id}")
            normalized_id = source_id
        else:
            source_ids.add(source_id)
            normalized_id = source_id

        channels = source_channels(source, normalized_id, errors)
        represented_channels.update(channels)

        access = source.get("access", {})
        if isinstance(access, dict) and access.get("machine_readable_raw_table_verified") is True:
            raw_ready_channels.update(channels)

        material = str(source.get("material", "")).lower()
        status = str(source.get("status", ""))
        if any(term in material for term in ("graphene oxide", "composite", "aerogel")):
            if status not in {
                "EXCLUDED_FROM_TE_N_CHANNEL_SET",
                "INSUFFICIENT_FOR_PRIMARY_GRAPHENE_TEST",
            }:
                errors.append(f"non-pristine source {normalized_id} is not explicitly excluded")

    if not REQUIRED_CHANNELS.issubset(represented_channels):
        missing = sorted(REQUIRED_CHANNELS - represented_channels)
        errors.append(f"candidate channel coverage missing: {missing}")

    if raw_ready_channels:
        warnings.append(
            "machine-readable raw tables are marked verified; acquisition status should be reviewed"
        )

    thermoml = payload.get("thermoml", {})
    if not isinstance(thermoml, dict):
        errors.append("ThermoML audit block is missing")
    elif thermoml.get("pristine_monolayer_four_surface_archive") is not False:
        errors.append("ThermoML must not be represented as a pristine four-surface archive")

    return {
        "campaign": "G01_GRAPHENE_FEASIBILITY",
        "status": "PASS_FEASIBILITY_LEDGER" if not errors else "FAIL_FEASIBILITY_LEDGER",
        "errors": errors,
        "warnings": warnings,
        "source_count": len(sources),
        "represented_channels": sorted(represented_channels),
        "machine_readable_ready_channels": sorted(raw_ready_channels),
        "significance_computed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "ledger",
        nargs="?",
        type=Path,
        default=Path("graphene/G01_SOURCE_LEDGER.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/G01_FEASIBILITY_AUDIT.json"),
    )
    args = parser.parse_args()

    payload = json.loads(args.ledger.read_text(encoding="utf-8"))
    result = validate_ledger(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS_FEASIBILITY_LEDGER" else 1


if __name__ == "__main__":
    raise SystemExit(main())
