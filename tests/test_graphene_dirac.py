from __future__ import annotations

import numpy as np
import pytest

from thermo_recognition.graphene_dirac import (
    dimensionless_channels,
    evaluate_control_point,
    neutrality_reference,
)


def test_neutrality_matches_closed_form() -> None:
    actual = dimensionless_channels(1.0, 0.0)
    expected = neutrality_reference(1.0)
    assert np.allclose(actual, expected, rtol=2e-12, atol=2e-12)


def test_graphene_channels_have_expected_mu_parity() -> None:
    positive = dimensionless_channels(1.2, 1.7)
    negative = dimensionless_channels(1.2, -1.7)

    assert np.isclose(positive[0], -negative[0], rtol=1e-12, atol=1e-12)
    assert np.isclose(positive[1], negative[1], rtol=1e-12, atol=1e-12)
    assert np.isclose(positive[2], negative[2], rtol=1e-12, atol=1e-12)
    assert np.isclose(positive[3], negative[3], rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize(
    ("theta", "chemical_potential"),
    [
        (0.6, -2.0),
        (0.8, -0.5),
        (1.0, 0.0),
        (1.2, 0.75),
        (1.5, 2.5),
    ],
)
def test_ideal_dirac_graphene_is_plucker_flat(
    theta: float, chemical_potential: float
) -> None:
    point = evaluate_control_point(theta, chemical_potential)
    assert point.status == "PASS_CONTROL"
    assert point.normalized_plucker_residual < 1e-14
    assert point.rank_tail_ratio < 1e-12


def test_invalid_temperature_is_rejected() -> None:
    with pytest.raises(ValueError, match="theta must be positive"):
        dimensionless_channels(0.0, 0.0)
