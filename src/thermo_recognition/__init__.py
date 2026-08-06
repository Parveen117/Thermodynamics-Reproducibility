"""Thermodynamic Recognition falsification tools."""

from .plucker import (
    PAIR_ORDER,
    PluckerTestResult,
    common_gradient_control,
    delta_method_variance,
    independent_bracket_test,
    normalized_residual,
    pairs_from_gradients,
    paper_gradient_error_bound,
    plucker_gradient,
    plucker_residual,
    skew_matrix_from_pairs,
)

__all__ = [
    "PAIR_ORDER",
    "PluckerTestResult",
    "common_gradient_control",
    "delta_method_variance",
    "independent_bracket_test",
    "normalized_residual",
    "pairs_from_gradients",
    "paper_gradient_error_bound",
    "plucker_gradient",
    "plucker_residual",
    "skew_matrix_from_pairs",
]
