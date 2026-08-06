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


def validate_ledger(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("campaign") != "G01_GRAPHENE_FEASIBILITY":
        errors.append("unexpected campaign identifier")
    if payload.get("significance_computed") is not False:
        errors.append("feasibility ledger must not claim a computed significance")
    if payload.get("current_gate") != "NO_FOUR_CHANNEL_MACHINE_READABLE_CONTRACT":
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
        elif source_id in source_ids:
            errors.append(f"duplicate source_id: {source_id}")
        else:
            source_ids.add(source_id)

        channel = source.get("channel")
        if isinstance(channel, str):
            represented_channels.add(channel)

        access = source.get("access", {})
        if isinstance(access, dict) and access.get("machine_readable_raw_table_verified") is True:
            if isinstance(channel, str):
                raw_ready_channels.add(channel)

        material = str(source.get("material", "")).lower()
        status = str(source.get("status", ""))
        if any(term in material for term in ("graphene oxide", "composite", "aerogel")):
            if status not in {"EXCLUDED_FROM_TE_N_CHANNEL_SET", "INSUFFICIENT_FOR_PRIMARY_GRAPHENE_TEST"}:
                errors.append(f"non-pristine source {source_id} is not explicitly excluded")

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
    else:
        if thermoml.get("pristine_monolayer_four_surface_archive") is not False:
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
