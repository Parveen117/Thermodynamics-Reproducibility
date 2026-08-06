"""Run the first deterministic Pluecker audit and print a JSON certificate."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from thermo_recognition.plucker import (
    PAIR_ORDER,
    common_gradient_control,
    independent_bracket_test,
    pairs_from_gradients,
    plucker_residual,
)


def main() -> int:
    u = np.array([1.0, 2.0, -1.0, 0.5])
    v = np.array([0.2, -0.3, 1.5, 2.0])
    baseline = pairs_from_gradients(u, v)

    control = common_gradient_control(u, v)

    sigma = 1.0e-3
    covariance = np.eye(6) * sigma**2

    consistent = baseline.copy()
    consistent[5] += 1.0e-3
    consistent_result = independent_bracket_test(consistent, covariance)

    inconsistent = baseline.copy()
    inconsistent[5] += 1.0e-1
    inconsistent_result = independent_bracket_test(inconsistent, covariance)

    certificate = {
        "campaign": "T01_PLUCKER_INDEPENDENT_BRACKETS",
        "stage": "T01B_INDEPENDENT_BRACKET_SYNTHETIC",
        "pair_order": list(PAIR_ORDER),
        "common_gradients": {"u": u.tolist(), "v": v.tolist()},
        "baseline_pairs": baseline.tolist(),
        "baseline_residual": plucker_residual(baseline),
        "control": control.to_dict(),
        "small_independent_perturbation": {
            "pairs": consistent.tolist(),
            "result": consistent_result.to_dict(),
        },
        "large_independent_perturbation": {
            "pairs": inconsistent.tolist(),
            "result": inconsistent_result.to_dict(),
        },
        "expected": {
            "control": "PASS_CONTROL",
            "small_independent_perturbation": "NOT_FALSIFIED",
            "large_independent_perturbation": "FALSIFIED_MEASUREMENT_CONTRACT",
        },
    }

    output = Path("results/T01_SYNTHETIC_AUDIT.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(json.dumps(certificate, indent=2, sort_keys=True))

    statuses = (
        control.status,
        consistent_result.status,
        inconsistent_result.status,
    )
    expected = (
        "PASS_CONTROL",
        "NOT_FALSIFIED",
        "FALSIFIED_MEASUREMENT_CONTRACT",
    )
    return 0 if statuses == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
