from __future__ import annotations

import numpy as np

from thermo_recognition.plucker import independent_bracket_test


def test_thirty_sigma_is_rejection_not_confirmation() -> None:
    # Pair values chosen so P = b12*b34 = 30 while the propagated
    # standard error is one. The repository convention must label this
    # as a rejection, never as a residual buried below uncertainty.
    pairs = np.array([30.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    covariance = np.zeros((6, 6))
    covariance[0, 0] = 1.0

    result = independent_bracket_test(pairs, covariance, z_threshold=5.0)

    assert result.z_score == 30.0
    assert result.status == "FALSIFIED_MEASUREMENT_CONTRACT"


def test_residual_thirty_times_below_uncertainty_is_small_z() -> None:
    # Here P = 1/30 and sigma_P = 1, so z = 1/30.
    pairs = np.array([1.0 / 30.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    covariance = np.zeros((6, 6))
    covariance[0, 0] = 1.0

    result = independent_bracket_test(pairs, covariance, z_threshold=5.0)

    assert np.isclose(result.z_score, 1.0 / 30.0)
    assert result.status == "NOT_FALSIFIED"
