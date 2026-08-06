from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "run_t01d_independent_plucker.py"
    spec = importlib.util.spec_from_file_location("t01d_fit", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def contract() -> dict:
    return {
        "evaluation_point": {"temperature_K": 300.0, "pressure_kPa": 1000.0},
        "state_coordinates": {
            "temperature_bandwidth_K": 10.0,
            "pressure_bandwidth_kPa": 1000.0,
        },
        "fit_model": {
            "hard_window": {"absolute_x_max": 3.0, "absolute_y_max": 3.0}
        },
        "fit_gates": {
            "minimum_included_points": 9,
            "minimum_effective_sample_size": 6.5,
            "required_design_rank": 6,
            "maximum_normal_matrix_condition_number": 1.0e12,
        },
    }


def synthetic_slot(a: float, b: float) -> dict:
    records = []
    for x in (-1.0, 0.0, 1.0):
        for y in (-1.0, 0.0, 1.0):
            value = 2.0 + a * x + b * y + 0.2 * x * x - 0.1 * x * y + 0.3 * y * y
            records.append(
                {
                    "temperature_K": 300.0 + 10.0 * x,
                    "pressure_kPa": 1000.0 + 1000.0 * y,
                    "property_value": value,
                    "uncertainty": {
                        "standard_uncertainty": 0.01,
                        "expanded_uncertainty": None,
                    },
                }
            )
    return {"reference_scale": 1.0, "records": records}


def test_fit_recovers_quadratic_gradient():
    module = load_module()
    fit = module.fit_slot(synthetic_slot(0.4, -0.7), contract())

    assert fit["status"] == "PASS_FIT"
    assert np.allclose(fit["gradient_xy"], [0.4, -0.7], atol=1e-10)


def test_bracket_delta_method_is_positive():
    module = load_module()
    left = module.fit_slot(synthetic_slot(0.4, -0.7), contract())
    right = module.fit_slot(synthetic_slot(1.1, 0.2), contract())
    bracket = module.bracket_from_fits(left, right)

    assert np.isclose(bracket["value"], 0.4 * 0.2 - (-0.7) * 1.1)
    assert bracket["variance"] >= 0.0
    assert bracket["standard_error"] >= 0.0
