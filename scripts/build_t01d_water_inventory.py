#!/usr/bin/env python3
"""Build a provenance-rich inventory of pure-water ThermoML datasets.

The scanner is deliberately conservative. It does not fit thermodynamic surfaces
or manufacture Pluecker brackets. Its only job is to identify which independent
experimental property records exist, their state-space coverage, methods, and
uncertainty metadata before the T01D measurement contract is specialized.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

WATER_INCHIKEY = "XLYOFNOQVPJJNP-UHFFFAOYSA-N"
ARCHIVE_SHA256 = "231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2"
PAIR_ORDER = ("12", "13", "14", "23", "24", "34")

TARGET_CATEGORIES = (
    "isobaric_heat_capacity",
    "isochoric_heat_capacity",
    "density",
    "speed_of_sound",
    "isothermal_compressibility",
    "isentropic_compressibility",
    "thermal_expansion",
    "bulk_modulus",
)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def walk(node: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(node, dict):
        for key, value in node.items():
            yield key, value
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def first_key(node: Any, keys: set[str]) -> Any:
    for key, value in walk(node):
        if key in keys:
            return value
    return None


def contains_uncertainty(node: Any) -> bool:
    return any("uncert" in key.lower() for key, _ in walk(node))


def numeric_values(node: Any, keys: set[str]) -> list[float]:
    values: list[float] = []
    for key, value in walk(node):
        if key in keys and isinstance(value, (int, float)):
            values.append(float(value))
    return values


def org_number(node: Any) -> int | None:
    value = first_key(node, {"nOrgNum"})
    return int(value) if isinstance(value, (int, float)) else None


def classify_property(name: str) -> str:
    text = name.lower()
    if "speed of sound" in text or "sound speed" in text:
        return "speed_of_sound"
    if "density" in text and "excess" not in text:
        return "density"
    if "isobaric heat capacity" in text or "heat capacity at constant pressure" in text:
        return "isobaric_heat_capacity"
    if "isochoric heat capacity" in text or "heat capacity at constant volume" in text:
        return "isochoric_heat_capacity"
    if "isothermal compressibility" in text:
        return "isothermal_compressibility"
    if "adiabatic compressibility" in text or "isentropic compressibility" in text:
        return "isentropic_compressibility"
    if "thermal expansion" in text or "expansion coefficient" in text:
        return "thermal_expansion"
    if "bulk modulus" in text:
        return "bulk_modulus"
    if "molar volume" in text or "specific volume" in text:
        return "volume"
    return "other"


def variable_kind(name: str) -> str:
    text = name.lower()
    if "temperature" in text:
        return "temperature"
    if "pressure" in text:
        return "pressure"
    return "other"


def finite_range(values: list[float]) -> list[float] | None:
    if not values:
        return None
    return [min(values), max(values)]


@dataclass(frozen=True)
class PropertyRecord:
    doi: str
    title: str
    journal: str
    year: str
    file: str
    dataset_number: int | None
    property_number: int
    property_name: str
    category: str
    method: str | None
    phase: str | None
    presentation: str | None
    point_count: int
    temperature_range_K: list[float] | None
    pressure_range_kPa: list[float] | None
    unique_temperature_count: int
    unique_pressure_count: int
    has_uncertainty_metadata: bool
    property_value_range: list[float] | None
    variable_names: list[str]
    constraint_summary: list[str]

    @property
    def surface_capable(self) -> bool:
        return (
            self.point_count >= 9
            and self.unique_temperature_count >= 3
            and self.unique_pressure_count >= 3
        )

    def to_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        result["surface_capable"] = self.surface_capable
        return result


def compound_map(document: dict[str, Any]) -> dict[int, str]:
    result: dict[int, str] = {}
    for compound in as_list(document.get("Compound")):
        if not isinstance(compound, dict):
            continue
        number = org_number(compound.get("RegNum"))
        key = compound.get("sStandardInChIKey")
        if number is not None and isinstance(key, str):
            result[number] = key
    return result


def is_pure_water_dataset(dataset: dict[str, Any], compounds: dict[int, str]) -> bool:
    components = [item for item in as_list(dataset.get("Component")) if isinstance(item, dict)]
    if len(components) != 1:
        return False
    number = org_number(components[0].get("RegNum"))
    return number is not None and compounds.get(number) == WATER_INCHIKEY


def property_name(prop: dict[str, Any]) -> str:
    value = first_key(prop.get("Property-MethodID", prop), {"ePropName", "sPropName"})
    return str(value) if value is not None else "UNKNOWN_PROPERTY"


def property_method(prop: dict[str, Any]) -> str | None:
    value = first_key(prop.get("Property-MethodID", prop), {"eMethodName", "sMethodName"})
    return str(value) if value is not None else None


def variable_name(variable: dict[str, Any]) -> str:
    variable_id = variable.get("VariableID", variable)
    for key, value in walk(variable_id):
        if key.startswith("e") and key not in {"eVarPhase"} and isinstance(value, str):
            return value
    return "UNKNOWN_VARIABLE"


def constraint_summary(dataset: dict[str, Any]) -> list[str]:
    summary: list[str] = []
    for constraint in as_list(dataset.get("Constraint")):
        if not isinstance(constraint, dict):
            continue
        labels = [
            str(value)
            for key, value in walk(constraint)
            if (key.startswith("e") or key.startswith("s")) and isinstance(value, str)
        ]
        numbers = [
            str(value)
            for key, value in walk(constraint)
            if key.startswith("n") and isinstance(value, (int, float))
        ]
        joined = " | ".join(dict.fromkeys(labels + numbers))
        if joined:
            summary.append(joined)
    return summary


def parse_document(path: Path) -> list[PropertyRecord]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []

    citation = document.get("Citation", {}) if isinstance(document, dict) else {}
    doi = str(citation.get("sDOI", ""))
    title = str(citation.get("sTitle", ""))
    journal = str(citation.get("sPubName", ""))
    year = str(citation.get("yrPubYr", ""))
    compounds = compound_map(document)
    records: list[PropertyRecord] = []

    for dataset in as_list(document.get("PureOrMixtureData")):
        if not isinstance(dataset, dict) or not is_pure_water_dataset(dataset, compounds):
            continue

        variables: dict[int, str] = {}
        for variable in as_list(dataset.get("Variable")):
            if not isinstance(variable, dict):
                continue
            number = variable.get("nVarNumber")
            if isinstance(number, (int, float)):
                variables[int(number)] = variable_name(variable)

        properties: dict[int, dict[str, Any]] = {}
        for prop in as_list(dataset.get("Property")):
            if not isinstance(prop, dict):
                continue
            number = prop.get("nPropNumber")
            if isinstance(number, (int, float)):
                properties[int(number)] = prop

        observations: dict[int, list[tuple[dict[int, float], float, bool]]] = defaultdict(list)
        for row in as_list(dataset.get("NumValues")):
            if not isinstance(row, dict):
                continue
            row_variables: dict[int, float] = {}
            for value in as_list(row.get("VariableValue")):
                if not isinstance(value, dict):
                    continue
                number = value.get("nVarNumber")
                numeric = value.get("nVarValue")
                if isinstance(number, (int, float)) and isinstance(numeric, (int, float)):
                    row_variables[int(number)] = float(numeric)
            for value in as_list(row.get("PropertyValue")):
                if not isinstance(value, dict):
                    continue
                number = value.get("nPropNumber")
                numeric = value.get("nPropValue")
                if isinstance(number, (int, float)) and isinstance(numeric, (int, float)):
                    observations[int(number)].append(
                        (row_variables.copy(), float(numeric), contains_uncertainty(value))
                    )

        phase_value = first_key(dataset.get("PhaseID"), {"ePhase"})
        phase = str(phase_value) if phase_value is not None else None
        dataset_number_raw = dataset.get("nPureOrMixtureDataNumber")
        dataset_number = int(dataset_number_raw) if isinstance(dataset_number_raw, (int, float)) else None
        constraints = constraint_summary(dataset)

        for number, prop in properties.items():
            rows = observations.get(number, [])
            if not rows:
                continue
            name = property_name(prop)
            method = property_method(prop)
            temperatures: list[float] = []
            pressures: list[float] = []
            values: list[float] = []
            row_has_uncertainty = False
            for row_variables, numeric, has_uncertainty in rows:
                values.append(numeric)
                row_has_uncertainty = row_has_uncertainty or has_uncertainty
                for var_number, var_value in row_variables.items():
                    kind = variable_kind(variables.get(var_number, ""))
                    if kind == "temperature":
                        temperatures.append(var_value)
                    elif kind == "pressure":
                        pressures.append(var_value)

            records.append(
                PropertyRecord(
                    doi=doi,
                    title=title,
                    journal=journal,
                    year=year,
                    file=str(path),
                    dataset_number=dataset_number,
                    property_number=number,
                    property_name=name,
                    category=classify_property(name),
                    method=method,
                    phase=phase,
                    presentation=str(prop.get("ePresentation")) if prop.get("ePresentation") else None,
                    point_count=len(rows),
                    temperature_range_K=finite_range(temperatures),
                    pressure_range_kPa=finite_range(pressures),
                    unique_temperature_count=len(set(temperatures)),
                    unique_pressure_count=len(set(pressures)),
                    has_uncertainty_metadata=contains_uncertainty(prop) or row_has_uncertainty,
                    property_value_range=finite_range(values),
                    variable_names=sorted(set(variables.values())),
                    constraint_summary=constraints,
                )
            )
    return records


def summarize(records: list[PropertyRecord]) -> dict[str, Any]:
    grouped: dict[str, list[PropertyRecord]] = defaultdict(list)
    for record in records:
        grouped[record.category].append(record)

    categories: dict[str, Any] = {}
    for category in sorted(grouped):
        items = grouped[category]
        dois = sorted({item.doi for item in items if item.doi})
        categories[category] = {
            "dataset_count": len(items),
            "publication_count": len(dois),
            "point_count": sum(item.point_count for item in items),
            "surface_capable_dataset_count": sum(item.surface_capable for item in items),
            "uncertainty_dataset_count": sum(item.has_uncertainty_metadata for item in items),
            "methods": sorted({item.method for item in items if item.method}),
            "dois": dois,
        }

    target_surface_sources = {
        category: sorted({record.doi for record in grouped.get(category, []) if record.surface_capable and record.doi})
        for category in TARGET_CATEGORIES
    }
    usable_categories = [category for category, sources in target_surface_sources.items() if sources]
    independently_replicated = [category for category, sources in target_surface_sources.items() if len(sources) >= 2]

    if len(usable_categories) < 4:
        gate = "INCONCLUSIVE_DATA_COVERAGE"
    elif len(independently_replicated) < 4:
        gate = "INCONCLUSIVE_INDEPENDENCE"
    else:
        gate = "CANDIDATE_CHANNEL_SET_AVAILABLE"

    return {
        "gate": gate,
        "pure_water_property_record_count": len(records),
        "publication_count": len({record.doi for record in records if record.doi}),
        "categories": categories,
        "target_surface_sources": target_surface_sources,
        "surface_capable_target_categories": usable_categories,
        "independently_replicated_target_categories": independently_replicated,
        "audit_note": (
            "A surface-capable record has at least 9 points, 3 temperatures, and 3 pressures. "
            "This is an inventory heuristic only; it is not a fitted-surface quality certificate."
        ),
    }


def build_inventory(root: Path) -> dict[str, Any]:
    files = sorted(root.rglob("*.json"))
    records: list[PropertyRecord] = []
    for path in files:
        records.extend(parse_document(path))
    records.sort(key=lambda item: (item.category, item.doi, item.dataset_number or -1, item.property_number))
    return {
        "campaign": "T01D_THERMOML_EXPERIMENTAL",
        "stage": "PURE_WATER_ARCHIVE_INVENTORY",
        "archive": {
            "name": "ThermoML.v2020-09-30.tgz",
            "sha256": ARCHIVE_SHA256,
            "source": "https://data.nist.gov/od/ds/mds2-2422/ThermoML.v2020-09-30.tgz",
            "coverage": "ThermoML entries published through calendar year 2019",
        },
        "water_identifier": {"standard_inchi_key": WATER_INCHIKEY},
        "summary": summarize(records),
        "records": [record.to_dict() for record in records],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive_root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results/T01D_WATER_INVENTORY.json"))
    args = parser.parse_args()

    inventory = build_inventory(args.archive_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = inventory["summary"]
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
