from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "run_g06_variable_map.py"
    spec = importlib.util.spec_from_file_location("g06_map", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def groups() -> dict[str, list[str]]:
    return {
        "temperature_control": ["temperature", "T (K)"],
        "density_control": ["carrier density", "n (cm"],
        "electrical_transport": ["conductivity", "conductance"],
        "thermal_transport": ["thermal conductivity", "kappa"],
        "derived_hydrodynamics": ["viscosity", "entropy"],
        "uncertainty": ["error"],
    }


def test_two_control_electrical_sheet_is_candidate() -> None:
    module = load_module()
    labels = ["T (K)", "Carrier density n (cm-2)", "Electrical conductivity"]
    matches = module.matched_labels(labels, groups())
    status, observables = module.classify_sheet(matches)
    assert status == "TWO_CONTROL_CHANNEL_CANDIDATE"
    assert observables == ["electrical_transport"]


def test_density_only_curve_is_not_two_control() -> None:
    module = load_module()
    labels = ["Carrier density n (cm-2)", "Conductance"]
    matches = module.matched_labels(labels, groups())
    status, _ = module.classify_sheet(matches)
    assert status == "ONE_CONTROL_OR_UNRESOLVED"


def test_derived_only_sheet_is_auxiliary() -> None:
    module = load_module()
    labels = ["Viscosity", "Entropy density"]
    matches = module.matched_labels(labels, groups())
    status, observables = module.classify_sheet(matches)
    assert status == "DERIVED_OR_AUXILIARY_CHANNEL"
    assert observables == ["derived_hydrodynamics"]
