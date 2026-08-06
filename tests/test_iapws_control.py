import pytest

from thermo_recognition.iapws_control import iapws_point_control, water_channels


@pytest.mark.parametrize(
    ("temperature_K", "pressure_MPa"),
    [
        (285.0, 0.1),
        (300.0, 0.1),
        (300.0, 1.0),
        (325.0, 5.0),
        (350.0, 10.0),
    ],
)
def test_iapws_water_closure_controls(temperature_K: float, pressure_MPa: float) -> None:
    result = iapws_point_control(temperature_K, pressure_MPa)
    assert result.status == "PASS_CONTROL"
    assert result.flat_closure_error < 1e-8
    assert result.sound_bulk_relative_error < 1e-8
    assert result.normalized_plucker_residual < 1e-12


def test_water_channels_are_positive_and_dimensionless() -> None:
    channels, raw = water_channels(300.0, 0.1)
    assert channels.shape == (4,)
    assert (channels > 0).all()
    assert raw["K_S_MPa"] > raw["K_T_MPa"]
    assert raw["cp_kJ_kgK"] > raw["cv_kJ_kgK"]
