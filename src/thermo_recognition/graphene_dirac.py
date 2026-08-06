"""Ideal massless-Dirac graphene control on a two-variable state chart.

The chart coordinates are dimensionless temperature ``theta = T / T0`` and
chemical potential ``m = mu / (k_B T0)``.  The four dimensionless channels are
net carrier density, total electronic energy density, entropy density, and
quantum-compressibility response.  Overall dimensional prefactors are omitted
because nonzero constant channel rescalings do not change decomposability.

This module is a common-model control.  It is not an independent experimental
falsification test.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .plucker import (
    common_gradient_control,
    pairs_from_gradients,
    skew_matrix_from_pairs,
)

APERY_CONSTANT = 1.2020569031595942854
CHANNEL_ORDER = ("net_density", "energy", "entropy", "compressibility")

# Fixed Gauss-Legendre quadrature on [0, 60].  The campaign restricts
# |mu/(k_B T)| to modest values, so the omitted Fermi tail is negligible.
_GL_NODES, _GL_WEIGHTS = np.polynomial.legendre.leggauss(256)
_QUAD_X = 30.0 * (_GL_NODES + 1.0)
_QUAD_W = 30.0 * _GL_WEIGHTS


@dataclass(frozen=True)
class DiracControlPoint:
    theta: float
    chemical_potential: float
    eta: float
    channels: tuple[float, ...]
    gradient_theta: tuple[float, ...]
    gradient_mu: tuple[float, ...]
    pairs: tuple[float, ...]
    plucker_residual: float
    normalized_plucker_residual: float
    rank_tail_ratio: float
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _finite_scalar(value: float, name: str) -> float:
    number = float(value)
    if not np.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def fermi_integral(order: int, eta: float) -> float:
    """Return integral x**order / (1 + exp(x-eta)) dx from zero to infinity.

    A fixed quadrature is used so the control is deterministic across runs.
    The accepted control range is |eta| <= 8; outside that range a wider
    integration contract should be frozen rather than silently extrapolated.
    """

    if order not in (0, 1, 2):
        raise ValueError("order must be 0, 1, or 2")
    eta_value = _finite_scalar(eta, "eta")
    if abs(eta_value) > 8.0:
        raise ValueError("ideal graphene control is frozen to |eta| <= 8")

    if order == 0:
        return float(np.logaddexp(0.0, eta_value))

    exponent = np.clip(_QUAD_X - eta_value, -700.0, 700.0)
    occupancy = 1.0 / (1.0 + np.exp(exponent))
    values = (_QUAD_X**order) * occupancy
    return float(np.dot(_QUAD_W, values))


def dimensionless_channels(theta: float, chemical_potential: float) -> NDArray[np.float64]:
    """Evaluate four ideal-Dirac response channels on the (theta, m) chart."""

    theta_value = _finite_scalar(theta, "theta")
    mu_value = _finite_scalar(chemical_potential, "chemical_potential")
    if theta_value <= 0.0:
        raise ValueError("theta must be positive")

    eta = mu_value / theta_value
    f1_plus = fermi_integral(1, eta)
    f1_minus = fermi_integral(1, -eta)
    f2_plus = fermi_integral(2, eta)
    f2_minus = fermi_integral(2, -eta)

    net_density = theta_value**2 * (f1_plus - f1_minus)
    energy = theta_value**3 * (f2_plus + f2_minus)
    entropy = (1.5 * energy - mu_value * net_density) / theta_value
    compressibility = theta_value * (
        np.logaddexp(0.0, eta) + np.logaddexp(0.0, -eta)
    )

    channels = np.array(
        [net_density, energy, entropy, compressibility], dtype=float
    )
    if not np.all(np.isfinite(channels)):
        raise ValueError("channel evaluation produced non-finite values")
    return channels


def channel_gradients(
    theta: float,
    chemical_potential: float,
    *,
    relative_step: float = 1e-4,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return central-difference gradients with respect to theta and m."""

    theta_value = _finite_scalar(theta, "theta")
    mu_value = _finite_scalar(chemical_potential, "chemical_potential")
    step = _finite_scalar(relative_step, "relative_step")
    if theta_value <= 0.0:
        raise ValueError("theta must be positive")
    if step <= 0.0:
        raise ValueError("relative_step must be positive")

    h_theta = step * max(1.0, abs(theta_value))
    h_mu = step * max(1.0, abs(mu_value))
    if theta_value - h_theta <= 0.0:
        raise ValueError("relative_step crosses the theta = 0 boundary")

    gradient_theta = (
        dimensionless_channels(theta_value + h_theta, mu_value)
        - dimensionless_channels(theta_value - h_theta, mu_value)
    ) / (2.0 * h_theta)
    gradient_mu = (
        dimensionless_channels(theta_value, mu_value + h_mu)
        - dimensionless_channels(theta_value, mu_value - h_mu)
    ) / (2.0 * h_mu)
    return gradient_theta, gradient_mu


def evaluate_control_point(
    theta: float,
    chemical_potential: float,
    *,
    relative_step: float = 1e-4,
) -> DiracControlPoint:
    """Evaluate the common-gradient Pluecker control at one state point."""

    channels = dimensionless_channels(theta, chemical_potential)
    gradient_theta, gradient_mu = channel_gradients(
        theta, chemical_potential, relative_step=relative_step
    )
    pairs = pairs_from_gradients(gradient_theta, gradient_mu)
    result = common_gradient_control(
        gradient_theta,
        gradient_mu,
        tolerance=1e-8,
    )
    singular_values = np.linalg.svd(
        skew_matrix_from_pairs(pairs), compute_uv=False
    )
    leading = max(float(singular_values[0]), 1e-30)
    rank_tail_ratio = float(singular_values[2] / leading)

    return DiracControlPoint(
        theta=float(theta),
        chemical_potential=float(chemical_potential),
        eta=float(chemical_potential / theta),
        channels=tuple(float(value) for value in channels),
        gradient_theta=tuple(float(value) for value in gradient_theta),
        gradient_mu=tuple(float(value) for value in gradient_mu),
        pairs=tuple(float(value) for value in pairs),
        plucker_residual=float(result.residual),
        normalized_plucker_residual=float(result.normalized_residual),
        rank_tail_ratio=rank_tail_ratio,
        status=result.status,
    )


def neutrality_reference(theta: float) -> NDArray[np.float64]:
    """Closed-form channel values at chemical potential zero."""

    theta_value = _finite_scalar(theta, "theta")
    if theta_value <= 0.0:
        raise ValueError("theta must be positive")
    return np.array(
        [
            0.0,
            3.0 * APERY_CONSTANT * theta_value**3,
            4.5 * APERY_CONSTANT * theta_value**2,
            2.0 * np.log(2.0) * theta_value,
        ],
        dtype=float,
    )
