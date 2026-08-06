from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "run_g06_variable_map_v2.py"
    spec = importlib.util.spec_from_file_location("g06_v2", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def empty_groups() -> dict[str, list[str]]:
    return {
        "temperature_control": [],
        "density_control": [],
        "electrical_transport": [],
        "thermal_transport": [],
        "derived_hydrodynamics": [],
        "uncertainty": [],
    }


def test_compact_t_n_sigma_headers_are_recognized() -> None:
    module = load_module()
    labels = ["T=160 K", "n (10^10 cm-2)", "Sigma_Q"]
    matches = module.matched_labels(labels, empty_groups())
    assert matches["temperature_control"] == ["T=160 K"]
    assert matches["density_control"] == ["n (10^10 cm-2)"]
    assert matches["electrical_transport"] == ["Sigma_Q"]
    status, observables = module.BASE.classify_sheet(matches)
    assert status == "TWO_CONTROL_CHANNEL_CANDIDATE"
    assert observables == ["electrical_transport"]


def test_vg_and_kappa_e_are_recognized() -> None:
    module = load_module()
    labels = ["Temperature", "Vg", "kappa_e"]
    matches = module.matched_labels(labels, empty_groups())
    assert matches["density_control"] == ["Vg"]
    assert matches["thermal_transport"] == ["kappa_e"]


def test_eta_th_is_derived_not_primary_transport() -> None:
    module = load_module()
    labels = ["eta_th"]
    matches = module.matched_labels(labels, empty_groups())
    assert matches["derived_hydrodynamics"] == ["eta_th"]
