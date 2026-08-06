"""IAPWS-95 water controls for the T01 Pluecker campaign.

This module deliberately treats IAPWS-95 as a smooth equation-of-state control,
not as independent experimental evidence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from iapws import IAPWS95

from .plucker import common_gradient_control, pairs_from_gradients, plucker_residual

CHANNEL_NAMES = ("cp", "cv", "K_T", "K_S")
CHANNEL_SCALES = np.array([4.2, 4.0, 2200.0, 2300.0], dtype=float)
TEMPERATURE_SCALE_K = 300.0
PRESSURE_SCALE_MPA = 1.0


@dataclass(frozen=True)
class IAPWSPointResult:
    temperature_K: float
    pressure_MPa: float
    raw_channels: dict[str, float]
    dimensionless_channels: dict[str, float]
    flat_closure: float
    flat_closure_error: float
    sound_bulk_modulus_MPa: float
    sound_bulk_relative_error: float
    plucker_residual: float
    normalized_plucker_residual: float
    status: str
    note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def water_channels(temperature_K: float, pressure_MPa: float) -> tuple[np.ndarray, dict[str, float]]:
    """Return dimensionless (cp, cv, K_T, K_S) and raw diagnostics.

    The bulk moduli are computed from reciprocal compressibilities rather than
    the package's historical ``Kt``/``Ks`` labels, whose naming is ambiguous in
    the implementation. Here K_T = 1/kappa_T and K_S = 1/kappa_S by definition.
    """
    if not np.isfinite(temperature_K) or temperature_K <= 0:
        raise ValueError("temperature_K must be positive and finite")
    if not np.isfinite(pressure_MPa) or pressure_MPa <= 0:
        raise ValueError("pressure_MPa must be positive and finite")

    state = IAPWS95(T=float(temperature_K), P=float(pressure_MPa))
    cp = float(state.cp)
    cv = float(state.cv)
    kappa_t = float(state.kappa)
    kappa_s = float(state.ks)
    density = float(state.rho)
    sound_speed = float(state.w)

    if min(cp, cv, kappa_t, kappa_s, density, sound_speed) <= 0:
        raise ValueError("IAPWS state returned a nonpositive stable-response value")

    bulk_t = 1.0 / kappa_t
    bulk_s = 1.0 / kappa_s
    raw = np.array([cp, cv, bulk_t, bulk_s], dtype=float)
    dimensionless = raw / CHANNEL_SCALES
    diagnostics = {
        "cp_kJ_kgK": cp,
        "cv_kJ_kgK": cv,
        "kappa_T_per_MPa": kappa_t,
        "kappa_S_per_MPa": kappa_s,
        "K_T_MPa": bulk_t,
        "K_S_MPa": bulk_s,
        "density_kg_m3": density,
        "sound_speed_m_s": sound_speed,
    }
    return dimensionless, diagnostics


def central_response_gradients(
    temperature_K: float,
    pressure_MPa: float,
    *,
    delta_temperature_K: float = 0.05,
    delta_pressure_MPa: float = 0.005,
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate gradients in x=T/T_ref and y=P/P_ref coordinates."""
    if delta_temperature_K <= 0 or delta_pressure_MPa <= 0:
        raise ValueError("finite-difference steps must be positive")
    if pressure_MPa <= delta_pressure_MPa:
        raise ValueError("pressure must exceed the central-difference step")

    plus_t, _ = water_channels(temperature_K + delta_temperature_K, pressure_MPa)
    minus_t, _ = water_channels(temperature_K - delta_temperature_K, pressure_MPa)
    plus_p, _ = water_channels(temperature_K, pressure_MPa + delta_pressure_MPa)
    minus_p, _ = water_channels(temperature_K, pressure_MPa - delta_pressure_MPa)

    derivative_t = (plus_t - minus_t) / (2.0 * delta_temperature_K)
    derivative_p = (plus_p - minus_p) / (2.0 * delta_pressure_MPa)
    gradient_x = TEMPERATURE_SCALE_K * derivative_t
    gradient_y = PRESSURE_SCALE_MPA * derivative_p
    return gradient_x, gradient_y


def iapws_point_control(
    temperature_K: float,
    pressure_MPa: float,
    *,
    delta_temperature_K: float = 0.05,
    delta_pressure_MPa: float = 0.005,
    closure_tolerance: float = 1e-8,
    sound_tolerance: float = 1e-8,
) -> IAPWSPointResult:
    """Run equilibrium closure, sound-speed, and common-gradient controls."""
    dimensionless, raw = water_channels(temperature_K, pressure_MPa)
    gradient_x, gradient_y = central_response_gradients(
        temperature_K,
        pressure_MPa,
        delta_temperature_K=delta_temperature_K,
        delta_pressure_MPa=delta_pressure_MPa,
    )
    pairs = pairs_from_gradients(gradient_x, gradient_y)
    control = common_gradient_control(gradient_x, gradient_y)

    flat_closure = (raw["cv_kJ_kgK"] / raw["cp_kJ_kgK"]) * (
        raw["K_S_MPa"] / raw["K_T_MPa"]
    )
    closure_error = abs(flat_closure - 1.0)

    sound_bulk = raw["density_kg_m3"] * raw["sound_speed_m_s"] ** 2 / 1e6
    sound_relative_error = abs(sound_bulk - raw["K_S_MPa"]) / raw["K_S_MPa"]

    status = "PASS_CONTROL"
    if control.status != "PASS_CONTROL" or closure_error > closure_tolerance or sound_relative_error > sound_tolerance:
        status = "FAIL_CONTROL"

    return IAPWSPointResult(
        temperature_K=float(temperature_K),
        pressure_MPa=float(pressure_MPa),
        raw_channels=raw,
        dimensionless_channels={
            name: float(value) for name, value in zip(CHANNEL_NAMES, dimensionless)
        },
        flat_closure=float(flat_closure),
        flat_closure_error=float(closure_error),
        sound_bulk_modulus_MPa=float(sound_bulk),
        sound_bulk_relative_error=float(sound_relative_error),
        plucker_residual=plucker_residual(pairs),
        normalized_plucker_residual=control.normalized_residual,
        status=status,
        note=(
            "IAPWS-95 supplies one smooth Helmholtz equation of state. The Pluecker "
            "calculation is therefore a common-gradient control, not independent "
            "experimental falsification."
        ),
    )
