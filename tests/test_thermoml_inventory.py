from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_inventory_module():
    script = Path(__file__).parents[1] / "scripts" / "build_t01d_water_inventory.py"
    spec = importlib.util.spec_from_file_location("thermoml_inventory", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def water_document(component_count: int = 1) -> dict:
    values = []
    for temperature in (290.0, 300.0, 310.0):
        for pressure in (100.0, 500.0, 1000.0):
            values.append(
                {
                    "VariableValue": [
                        {"nVarNumber": 1, "nVarValue": temperature},
                        {"nVarNumber": 2, "nVarValue": pressure},
                    ],
                    "PropertyValue": [
                        {
                            "nPropNumber": 1,
                            "nPropValue": 1400.0 + 0.1 * temperature + 0.001 * pressure,
                            "CombinedUncertainty": {"nCombExpandUncertValue": 0.5},
                        }
                    ],
                }
            )

    components = [{"RegNum": {"nOrgNum": 1}}]
    if component_count == 2:
        components.append({"RegNum": {"nOrgNum": 2}})

    return {
        "Citation": {
            "sDOI": "10.example/water",
            "sTitle": "Synthetic water sound data",
            "sPubName": "Test Journal",
            "yrPubYr": "2026",
        },
        "Compound": [
            {
                "RegNum": {"nOrgNum": 1},
                "sStandardInChIKey": "XLYOFNOQVPJJNP-UHFFFAOYSA-N",
            },
            {
                "RegNum": {"nOrgNum": 2},
                "sStandardInChIKey": "OTHER-COMPOUND",
            },
        ],
        "PureOrMixtureData": [
            {
                "nPureOrMixtureDataNumber": 1,
                "Component": components,
                "PhaseID": {"ePhase": "Liquid"},
                "Variable": [
                    {
                        "nVarNumber": 1,
                        "VariableID": {"VariableType": {"eTemperature": "Temperature, K"}},
                    },
                    {
                        "nVarNumber": 2,
                        "VariableID": {"VariableType": {"ePressure": "Pressure, kPa"}},
                    },
                ],
                "Property": [
                    {
                        "nPropNumber": 1,
                        "ePresentation": "Direct value, X",
                        "Property-MethodID": {
                            "PropertyGroup": {
                                "RefractionSurfaceTensionSoundSpeed": {
                                    "ePropName": "Speed of sound, m/s",
                                    "eMethodName": "Pulse-echo method",
                                }
                            }
                        },
                        "CombinedUncertainty": {"nCombUncertLevOfConfid": 95},
                    }
                ],
                "NumValues": values,
            }
        ],
    }


def test_pure_water_surface_is_detected(tmp_path: Path):
    module = load_inventory_module()
    source = tmp_path / "water.json"
    source.write_text(json.dumps(water_document()), encoding="utf-8")

    records = module.parse_document(source)

    assert len(records) == 1
    record = records[0]
    assert record.category == "speed_of_sound"
    assert record.point_count == 9
    assert record.unique_temperature_count == 3
    assert record.unique_pressure_count == 3
    assert record.surface_capable
    assert record.has_uncertainty_metadata


def test_mixture_is_not_misclassified_as_pure_water(tmp_path: Path):
    module = load_inventory_module()
    source = tmp_path / "mixture.json"
    source.write_text(json.dumps(water_document(component_count=2)), encoding="utf-8")

    assert module.parse_document(source) == []


def test_inventory_gate_reports_insufficient_categories(tmp_path: Path):
    module = load_inventory_module()
    source = tmp_path / "water.json"
    source.write_text(json.dumps(water_document()), encoding="utf-8")

    inventory = module.build_inventory(tmp_path)

    assert inventory["summary"]["gate"] == "INCONCLUSIVE_DATA_COVERAGE"
    assert inventory["summary"]["categories"]["speed_of_sound"]["publication_count"] == 1
