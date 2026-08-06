from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_module():
    scripts = Path(__file__).parents[1] / "scripts"
    sys.path.insert(0, str(scripts))
    script = scripts / "extract_t01d_candidate_points.py"
    spec = importlib.util.spec_from_file_location("t01d_extraction", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def synthetic_document() -> dict:
    rows = []
    for temperature in (290.0, 300.0, 310.0):
        for pressure in (100.0, 500.0, 1000.0):
            rows.append(
                {
                    "VariableValue": [
                        {"nVarNumber": 1, "nVarValue": temperature},
                        {"nVarNumber": 2, "nVarValue": pressure},
                    ],
                    "PropertyValue": [
                        {
                            "nPropNumber": 1,
                            "nPropValue": 1400.0 + temperature / 10.0 + pressure / 1000.0,
                            "CombinedUncertainty": {
                                "nCombExpandUncertValue": 0.5,
                                "nCombUncertLevOfConfid": 95,
                            },
                        }
                    ],
                }
            )
    return {
        "Citation": {
            "sDOI": "10.example/water",
            "sTitle": "Synthetic independent sound surface",
            "sPubName": "Test Journal",
            "yrPubYr": "2026",
            "sAuthor": ["Dabas, M."],
            "eSourceType": "Original",
        },
        "Compound": [
            {
                "RegNum": {"nOrgNum": 1},
                "sStandardInChIKey": "XLYOFNOQVPJJNP-UHFFFAOYSA-N",
            }
        ],
        "PureOrMixtureData": [
            {
                "nPureOrMixtureDataNumber": 1,
                "Component": [{"RegNum": {"nOrgNum": 1}}],
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
                    }
                ],
                "NumValues": rows,
            }
        ],
    }


def test_extract_slot_and_topology(tmp_path: Path):
    module = load_module()
    source = tmp_path / "10.example" / "water.json"
    source.parent.mkdir(parents=True)
    source.write_text(json.dumps(synthetic_document()), encoding="utf-8")

    slot = module.extract_slot(
        tmp_path,
        "10.example/water",
        "speed_of_sound",
        "Speed of sound, m/s",
    )
    topology = module.topology(
        slot,
        {"temperature_K": [290.0, 310.0], "pressure_kPa": [100.0, 1000.0]},
        {"temperature_K": 300.0, "pressure_kPa": 500.0},
    )

    assert len(slot["records"]) == 9
    assert slot["citation"]["doi"] == "10.example/water"
    assert topology["status"] == "DIRECT_LOCAL_SUPPORT"
    assert topology["uncertainty_metadata_record_count"] == 9
    assert topology["expanded_uncertainty_record_count"] == 9


def test_find_doi_file_requires_unique_match(tmp_path: Path):
    module = load_module()
    for prefix in ("a", "b"):
        source = tmp_path / prefix / "10.example" / "water.json"
        source.parent.mkdir(parents=True)
        source.write_text("{}", encoding="utf-8")

    try:
        module.find_doi_file(tmp_path, "10.example/water")
    except FileNotFoundError as exc:
        assert "found 2" in str(exc)
    else:
        raise AssertionError("duplicate DOI files must be rejected")
