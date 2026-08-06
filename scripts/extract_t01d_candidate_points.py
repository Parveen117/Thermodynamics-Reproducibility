#!/usr/bin/env python3
"""Extract the frozen T01D pure-water source slots from ThermoML.

This stage performs no surface fitting and computes no Pluecker residual. It
records raw values, methods, constraints, uncertainty fields, and design-point
topology for the source assignments frozen in T01D_CANDIDATE_MANIFEST.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from build_t01d_water_inventory import (
    WATER_INCHIKEY,
    as_list,
    compound_map,
    contains_uncertainty,
    first_key,
    is_pure_water_dataset,
    org_number,
    property_method,
    property_name,
    variable_kind,
    variable_name,
    walk,
)


def classify_candidate_property(name: str) -> str:
    text = name.lower()
    if "speed of sound" in text or "sound speed" in text:
        return "speed_of_sound"
    if "density" in text and "excess" not in text:
        return "density"
    if "isobaric heat capacity" in text or "heat capacity at constant pressure" in text:
        return "isobaric_heat_capacity"
    if "viscosity" in text:
        return "viscosity"
    return "other"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_sha256(path: Path) -> str:
    canonical = json.dumps(json.loads(path.read_text(encoding="utf-8")), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def find_doi_file(root: Path, doi: str) -> Path:
    relative = Path(f"{doi}.json")
    matches = [
        path
        for path in root.rglob(relative.name)
        if path.as_posix().endswith(relative.as_posix())
    ]
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected one ThermoML JSON for {doi}, found {len(matches)}")
    return matches[0]


def numeric_constraint_value(node: Any) -> float | None:
    preferred = {
        "nConstraintValue",
        "nConstrValue",
        "nConstraintPhaseValue",
        "nConstraintValueLower",
    }
    for key, value in walk(node):
        if key in preferred and isinstance(value, (int, float)):
            return float(value)
    for key, value in walk(node):
        lowered = key.lower()
        if "constraint" in lowered and "value" in lowered and isinstance(value, (int, float)):
            return float(value)
    return None


def constraint_kind(node: Any) -> str | None:
    labels = [str(value).lower() for _, value in walk(node) if isinstance(value, str)]
    joined = " ".join(labels)
    if "temperature" in joined:
        return "temperature"
    if "pressure" in joined:
        return "pressure"
    return None


def fixed_constraints(dataset: dict[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    for constraint in as_list(dataset.get("Constraint")):
        if not isinstance(constraint, dict):
            continue
        kind = constraint_kind(constraint)
        value = numeric_constraint_value(constraint)
        if kind is not None and value is not None:
            result[kind] = value
    return result


def uncertainty_payload(prop: dict[str, Any], value: dict[str, Any]) -> dict[str, Any]:
    combined = value.get("CombinedUncertainty")
    if not isinstance(combined, dict):
        combined = prop.get("CombinedUncertainty") if isinstance(prop.get("CombinedUncertainty"), dict) else {}

    expanded = first_key(value, {"nCombExpandUncertValue", "nExpandUncertValue"})
    if expanded is None:
        expanded = first_key(combined, {"nCombExpandUncertValue", "nExpandUncertValue"})

    standard = first_key(value, {"nCombStdUncertValue", "nStdUncertValue"})
    if standard is None:
        standard = first_key(combined, {"nCombStdUncertValue", "nStdUncertValue"})

    confidence = first_key(combined, {"nCombUncertLevOfConfid", "nUncertLevOfConfid"})
    assessment = first_key(combined, {"nCombUncertAssessNum", "nUncertAssessNum"})
    evaluator = first_key(combined, {"sCombUncertEvaluator", "sUncertEvaluator"})
    method = first_key(combined, {"eCombUncertEvalMethod", "eUncertEvalMethod"})

    return {
        "expanded_uncertainty": float(expanded) if isinstance(expanded, (int, float)) else None,
        "standard_uncertainty": float(standard) if isinstance(standard, (int, float)) else None,
        "confidence_level_percent": float(confidence) if isinstance(confidence, (int, float)) else None,
        "assessment_number": int(assessment) if isinstance(assessment, (int, float)) else None,
        "evaluator": str(evaluator) if evaluator is not None else None,
        "evaluation_method": str(method) if method is not None else None,
        "metadata_present": contains_uncertainty(prop) or contains_uncertainty(value),
    }


def citation_payload(document: dict[str, Any]) -> dict[str, Any]:
    citation = document.get("Citation") if isinstance(document.get("Citation"), dict) else {}
    return {
        "doi": str(citation.get("sDOI", "")),
        "title": str(citation.get("sTitle", "")),
        "journal": str(citation.get("sPubName", "")),
        "year": str(citation.get("yrPubYr", "")),
        "authors": [str(item) for item in as_list(citation.get("sAuthor"))],
        "source_type": str(citation.get("eSourceType", "")),
    }


def variable_map(dataset: dict[str, Any]) -> dict[int, str]:
    result: dict[int, str] = {}
    for variable in as_list(dataset.get("Variable")):
        if not isinstance(variable, dict):
            continue
        number = variable.get("nVarNumber")
        if isinstance(number, (int, float)):
            result[int(number)] = variable_name(variable)
    return result


def property_map(dataset: dict[str, Any]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for prop in as_list(dataset.get("Property")):
        if not isinstance(prop, dict):
            continue
        number = prop.get("nPropNumber")
        if isinstance(number, (int, float)):
            result[int(number)] = prop
    return result


def phase_name(dataset: dict[str, Any]) -> str | None:
    value = first_key(dataset.get("PhaseID"), {"ePhase"})
    return str(value) if value is not None else None


def extract_slot(
    root: Path,
    doi: str,
    expected_category: str,
    expected_property_name: str,
) -> dict[str, Any]:
    source = find_doi_file(root, doi)
    document = json.loads(source.read_text(encoding="utf-8"))
    compounds = compound_map(document)
    records: list[dict[str, Any]] = []
    datasets: list[dict[str, Any]] = []

    for dataset in as_list(document.get("PureOrMixtureData")):
        if not isinstance(dataset, dict) or not is_pure_water_dataset(dataset, compounds):
            continue
        variables = variable_map(dataset)
        properties = property_map(dataset)
        constraints = fixed_constraints(dataset)
        dataset_number_raw = dataset.get("nPureOrMixtureDataNumber")
        dataset_number = int(dataset_number_raw) if isinstance(dataset_number_raw, (int, float)) else None

        selected_properties = {
            number: prop
            for number, prop in properties.items()
            if classify_candidate_property(property_name(prop)) == expected_category
            and property_name(prop) == expected_property_name
        }
        if not selected_properties:
            continue

        dataset_record_count = 0
        for row_index, row in enumerate(as_list(dataset.get("NumValues"))):
            if not isinstance(row, dict):
                continue
            row_variables: dict[str, float] = {}
            for item in as_list(row.get("VariableValue")):
                if not isinstance(item, dict):
                    continue
                number = item.get("nVarNumber")
                numeric = item.get("nVarValue")
                if not isinstance(number, (int, float)) or not isinstance(numeric, (int, float)):
                    continue
                kind = variable_kind(variables.get(int(number), ""))
                if kind in {"temperature", "pressure"}:
                    row_variables[kind] = float(numeric)

            for kind, numeric in constraints.items():
                row_variables.setdefault(kind, numeric)

            for item in as_list(row.get("PropertyValue")):
                if not isinstance(item, dict):
                    continue
                number = item.get("nPropNumber")
                numeric = item.get("nPropValue")
                if not isinstance(number, (int, float)) or not isinstance(numeric, (int, float)):
                    continue
                prop_number = int(number)
                if prop_number not in selected_properties:
                    continue
                if "temperature" not in row_variables or "pressure" not in row_variables:
                    continue
                prop = selected_properties[prop_number]
                records.append(
                    {
                        "dataset_number": dataset_number,
                        "row_index": row_index,
                        "property_number": prop_number,
                        "temperature_K": row_variables["temperature"],
                        "pressure_kPa": row_variables["pressure"],
                        "property_value": float(numeric),
                        "property_digits": int(item["nPropDigits"]) if isinstance(item.get("nPropDigits"), (int, float)) else None,
                        "uncertainty": uncertainty_payload(prop, item),
                    }
                )
                dataset_record_count += 1

        for prop_number, prop in selected_properties.items():
            datasets.append(
                {
                    "dataset_number": dataset_number,
                    "property_number": prop_number,
                    "property_name": property_name(prop),
                    "method": property_method(prop),
                    "phase": phase_name(dataset),
                    "presentation": str(prop.get("ePresentation")) if prop.get("ePresentation") else None,
                    "variable_names": sorted(variables.values()),
                    "fixed_constraints": constraints,
                    "record_count": dataset_record_count,
                }
            )

    records.sort(key=lambda item: (item["temperature_K"], item["pressure_kPa"], item["dataset_number"] or -1, item["row_index"]))
    return {
        "citation": citation_payload(document),
        "source_file_relative": source.relative_to(root).as_posix(),
        "source_file_sha256": file_sha256(source),
        "water_identifier": WATER_INCHIKEY,
        "expected_category": expected_category,
        "expected_property_name": expected_property_name,
        "datasets": datasets,
        "records": records,
    }


def finite_range(values: list[float]) -> list[float] | None:
    return [min(values), max(values)] if values else None


def topology(slot: dict[str, Any], domain: dict[str, list[float]], target: dict[str, float]) -> dict[str, Any]:
    records = slot["records"]
    temperatures = [float(item["temperature_K"]) for item in records]
    pressures = [float(item["pressure_kPa"]) for item in records]
    t_min, t_max = domain["temperature_K"]
    p_min, p_max = domain["pressure_kPa"]
    in_domain = [
        item
        for item in records
        if t_min <= item["temperature_K"] <= t_max and p_min <= item["pressure_kPa"] <= p_max
    ]
    in_t = [float(item["temperature_K"]) for item in in_domain]
    in_p = [float(item["pressure_kPa"]) for item in in_domain]
    t0 = float(target["temperature_K"])
    p0 = float(target["pressure_kPa"])

    target_inside_total_range = bool(
        temperatures
        and pressures
        and min(temperatures) <= t0 <= max(temperatures)
        and min(pressures) <= p0 <= max(pressures)
    )
    bracketed_temperature = any(value < t0 for value in temperatures) and any(value > t0 for value in temperatures)
    bracketed_pressure = any(value < p0 for value in pressures) and any(value > p0 for value in pressures)
    direct_support = (
        len(in_domain) >= 6
        and len(set(in_t)) >= 2
        and len(set(in_p)) >= 2
        and any(value < t0 for value in in_t)
        and any(value > t0 for value in in_t)
        and any(value < p0 for value in in_p)
        and any(value > p0 for value in in_p)
    )
    global_support = (
        len(records) >= 9
        and len(set(temperatures)) >= 3
        and len(set(pressures)) >= 3
        and target_inside_total_range
        and bracketed_temperature
        and bracketed_pressure
    )

    if direct_support:
        status = "DIRECT_LOCAL_SUPPORT"
    elif global_support:
        status = "GLOBAL_RANGE_SUPPORT"
    else:
        status = "INSUFFICIENT_TOPOLOGY"

    uncertainty_rows = sum(bool(item["uncertainty"]["metadata_present"]) for item in records)
    expanded_rows = sum(item["uncertainty"]["expanded_uncertainty"] is not None for item in records)
    standard_rows = sum(item["uncertainty"]["standard_uncertainty"] is not None for item in records)

    return {
        "status": status,
        "record_count": len(records),
        "temperature_range_K": finite_range(temperatures),
        "pressure_range_kPa": finite_range(pressures),
        "unique_temperature_count": len(set(temperatures)),
        "unique_pressure_count": len(set(pressures)),
        "in_frozen_domain_record_count": len(in_domain),
        "in_frozen_domain_unique_temperature_count": len(set(in_t)),
        "in_frozen_domain_unique_pressure_count": len(set(in_p)),
        "target_inside_total_range": target_inside_total_range,
        "target_bracketed_in_temperature": bracketed_temperature,
        "target_bracketed_in_pressure": bracketed_pressure,
        "uncertainty_metadata_record_count": uncertainty_rows,
        "expanded_uncertainty_record_count": expanded_rows,
        "standard_uncertainty_record_count": standard_rows,
    }


def build_extraction(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    channels = manifest["channels"]
    domain = manifest["chart"]["frozen_fit_domain"]
    target = manifest["chart"]["evaluation_point"]
    slots: dict[str, Any] = {}

    for pair in manifest["pair_order"]:
        assignment = manifest["pair_assignments"][pair]
        for side in ("left", "right"):
            channel_id = assignment[f"{side}_channel"]
            doi = assignment[f"{side}_doi"]
            channel = channels[channel_id]
            slot_name = f"{pair}.{side}"
            extracted = extract_slot(
                root,
                doi,
                channel["category"],
                channel["property_name"],
            )
            extracted["slot"] = slot_name
            extracted["pair"] = pair
            extracted["side"] = side
            extracted["channel_id"] = channel_id
            extracted["channel_symbol"] = channel["symbol"]
            extracted["reference_scale"] = channel["reference_scale"]
            extracted["reference_unit"] = channel["reference_unit"]
            extracted["topology"] = topology(extracted, domain, target)
            slots[slot_name] = extracted

    insufficient = [name for name, slot in slots.items() if slot["topology"]["status"] == "INSUFFICIENT_TOPOLOGY"]
    missing_uncertainty = [
        name
        for name, slot in slots.items()
        if slot["topology"]["uncertainty_metadata_record_count"] == 0
    ]
    gate = "CANDIDATE_EXTRACTION_COMPLETE" if not insufficient else "INCONCLUSIVE_DATA_COVERAGE"

    return {
        "campaign": manifest["campaign"],
        "stage": "FROZEN_SOURCE_EXTRACTION",
        "manifest_path": manifest_path.as_posix(),
        "manifest_canonical_sha256": manifest_sha256(manifest_path),
        "archive": manifest["archive"],
        "chart": manifest["chart"],
        "gate": gate,
        "insufficient_topology_slots": insufficient,
        "slots_without_uncertainty_metadata": missing_uncertainty,
        "residual_computed": False,
        "fit_model_selected": False,
        "slots": slots,
    }


def compact_summary(extraction: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign": extraction["campaign"],
        "stage": extraction["stage"],
        "manifest_canonical_sha256": extraction["manifest_canonical_sha256"],
        "archive": extraction["archive"],
        "chart": extraction["chart"],
        "gate": extraction["gate"],
        "insufficient_topology_slots": extraction["insufficient_topology_slots"],
        "slots_without_uncertainty_metadata": extraction["slots_without_uncertainty_metadata"],
        "residual_computed": extraction["residual_computed"],
        "fit_model_selected": extraction["fit_model_selected"],
        "slot_topology": {
            name: {
                "doi": slot["citation"]["doi"],
                "title": slot["citation"]["title"],
                "channel_symbol": slot["channel_symbol"],
                "property_name": slot["expected_property_name"],
                "methods": sorted({str(item["method"]) for item in slot["datasets"] if item["method"]}),
                "topology": slot["topology"],
            }
            for name, slot in extraction["slots"].items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive_root", type=Path)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("protocols/T01D_CANDIDATE_MANIFEST.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/T01D_CANDIDATE_RAW.json"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/T01D_CANDIDATE_TOPOLOGY.json"),
    )
    args = parser.parse_args()

    extraction = build_extraction(args.archive_root, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(extraction, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.summary.write_text(json.dumps(compact_summary(extraction), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(compact_summary(extraction), indent=2, sort_keys=True))
    return 0 if extraction["gate"] == "CANDIDATE_EXTRACTION_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
