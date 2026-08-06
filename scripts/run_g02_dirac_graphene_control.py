from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from thermo_recognition.graphene_dirac import (
    CHANNEL_ORDER,
    dimensionless_channels,
    evaluate_control_point,
    neutrality_reference,
)

STATES = [
    (0.6, -2.0),
    (0.8, -0.5),
    (1.0, 0.0),
    (1.2, 0.75),
    (1.5, 2.5),
]


def scaled_error(actual: float, expected: float) -> float:
    return abs(actual - expected) / max(1.0, abs(expected))


def main() -> None:
    points = [evaluate_control_point(theta, mu) for theta, mu in STATES]

    neutrality_errors: list[float] = []
    for theta in (0.6, 1.0, 1.5):
        actual = dimensionless_channels(theta, 0.0)
        expected = neutrality_reference(theta)
        neutrality_errors.extend(
            scaled_error(float(a), float(b)) for a, b in zip(actual, expected, strict=True)
        )

    parity_errors: list[float] = []
    for theta, mu in ((0.75, 0.5), (1.0, 1.5), (1.5, 2.5)):
        plus = dimensionless_channels(theta, mu)
        minus = dimensionless_channels(theta, -mu)
        expected_minus = np.array([-plus[0], plus[1], plus[2], plus[3]])
        parity_errors.extend(
            scaled_error(float(a), float(b))
            for a, b in zip(minus, expected_minus, strict=True)
        )

    max_normalized = max(point.normalized_plucker_residual for point in points)
    max_rank_tail = max(point.rank_tail_ratio for point in points)
    max_neutrality_error = max(neutrality_errors)
    max_parity_error = max(parity_errors)

    passed = (
        all(point.status == "PASS_CONTROL" for point in points)
        and max_normalized < 1e-14
        and max_rank_tail < 1e-12
        and max_neutrality_error < 1e-10
        and max_parity_error < 1e-10
    )

    certificate = {
        "campaign": "G02_DIRAC_GRAPHENE_CONTROL",
        "status": "PASS_CONTROL" if passed else "FAIL_CONTROL",
        "claim_boundary": (
            "All four channels come from one ideal massless-Dirac model on a common "
            "two-variable chart. This checks graphene thermodynamic algebra and the "
            "numerical pipeline; it is not independent experimental evidence."
        ),
        "chart": {
            "theta": "T / T0",
            "chemical_potential": "mu / (k_B T0)",
            "eta_restriction": "abs(mu / (k_B T)) <= 8",
        },
        "channel_order": list(CHANNEL_ORDER),
        "channels": {
            "net_density": "dimensionless net Dirac carrier density",
            "energy": "dimensionless total electronic energy density",
            "entropy": "dimensionless electronic entropy density",
            "compressibility": "dimensionless dn/dmu response",
        },
        "quadrature": {
            "family": "fixed Gauss-Legendre",
            "nodes": 256,
            "domain": [0.0, 60.0],
        },
        "finite_difference_relative_step": 1e-4,
        "control_points": [point.to_dict() for point in points],
        "audit": {
            "maximum_normalized_plucker_residual": max_normalized,
            "maximum_skew_rank_tail_ratio": max_rank_tail,
            "maximum_neutrality_formula_error": max_neutrality_error,
            "maximum_mu_parity_error": max_parity_error,
        },
        "interpretation": {
            "pass": "The ideal common-model graphene control is numerically Pluecker-flat.",
            "not_allowed": [
                "This is a graphene experimental confirmation.",
                "This result has an experimental sigma significance.",
                "Spatial two-dimensionality alone caused the pass.",
            ],
        },
    }

    output = Path("results/G02_DIRAC_GRAPHENE_CONTROL.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(json.dumps(certificate, indent=2, sort_keys=True))

    if not passed:
        raise SystemExit("G02 ideal Dirac graphene control failed")


if __name__ == "__main__":
    main()
