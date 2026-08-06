import numpy as np
import pytest

from thermo_recognition.plucker import (
    common_gradient_control,
    delta_method_variance,
    independent_bracket_test,
    pairs_from_gradients,
    plucker_gradient,
    plucker_residual,
    skew_matrix_from_pairs,
)


def test_common_gradient_construction_is_plucker_flat() -> None:
    rng = np.random.default_rng(20260806)
    for _ in range(100):
        u = rng.normal(size=4)
        v = rng.normal(size=4)
        pairs = pairs_from_gradients(u, v)
        scale = max(1.0, float(np.dot(pairs, pairs)))
        assert abs(plucker_residual(pairs)) <= 1e-12 * scale


def test_skew_matrix_preserves_pair_order() -> None:
    pairs = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    matrix = skew_matrix_from_pairs(pairs)
    assert np.allclose(matrix + matrix.T, 0.0)
    assert matrix[0, 1] == 1.0
    assert matrix[0, 2] == 2.0
    assert matrix[0, 3] == 3.0
    assert matrix[1, 2] == 4.0
    assert matrix[1, 3] == 5.0
    assert matrix[2, 3] == 6.0


def test_plucker_gradient_matches_finite_difference() -> None:
    pairs = np.array([-0.7, 1.7, 1.9, 2.7, 4.15, -2.75])
    analytic = plucker_gradient(pairs)
    step = 1e-7
    numerical = np.empty(6)
    for index in range(6):
        direction = np.zeros(6)
        direction[index] = step
        numerical[index] = (
            plucker_residual(pairs + direction)
            - plucker_residual(pairs - direction)
        ) / (2.0 * step)
    assert np.allclose(analytic, numerical, rtol=1e-8, atol=1e-8)


def test_delta_method_variance_for_diagonal_covariance() -> None:
    pairs = np.array([-0.7, 1.7, 1.9, 2.7, 4.15, -2.75])
    sigma = 1e-3
    covariance = np.eye(6) * sigma**2
    expected = sigma**2 * float(np.dot(plucker_gradient(pairs), plucker_gradient(pairs)))
    assert delta_method_variance(pairs, covariance) == pytest.approx(expected)


def test_synthetic_detector_separates_small_and_large_inconsistency() -> None:
    u = np.array([1.0, 2.0, -1.0, 0.5])
    v = np.array([0.2, -0.3, 1.5, 2.0])
    baseline = pairs_from_gradients(u, v)
    covariance = np.eye(6) * 1e-6

    small = baseline.copy()
    small[5] += 1e-3
    assert independent_bracket_test(small, covariance).status == "NOT_FALSIFIED"

    large = baseline.copy()
    large[5] += 1e-1
    result = independent_bracket_test(large, covariance)
    assert result.status == "FALSIFIED_MEASUREMENT_CONTRACT"
    assert result.z_score is not None and result.z_score > 5.0


def test_control_is_labelled_as_control() -> None:
    result = common_gradient_control([1, 0, 0, 0], [0, 1, 0, 0])
    assert result.status == "PASS_CONTROL"
    assert "cannot validate" in result.note


def test_invalid_covariance_is_rejected() -> None:
    pairs = np.ones(6)
    covariance = np.eye(6)
    covariance[0, 1] = 0.2
    with pytest.raises(ValueError, match="symmetric"):
        independent_bracket_test(pairs, covariance)
