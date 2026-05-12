from sim.control_search import (
    field_weakening_search,
    mtpa_grid_search,
    mtpv_grid_search,
)
from sim.dq_model import MotorParams


def sample_params():
    return MotorParams(
        name="sample",
        pole_pairs=4,
        rs_ohm=0.03,
        ld_h=0.00012,
        lq_h=0.00025,
        psi_f_wb=0.045,
        vdc_v=400.0,
        i_max_a=500.0,
        speed_max_rpm=18000.0,
        torque_target_nm=120.0,
        temperature_c=25.0,
    )


def test_mtpa_finds_low_current_point_for_target_torque():
    result = mtpa_grid_search(
        sample_params(), target_torque_nm=80.0, current_step_a=20.0
    )

    assert result.feasible
    assert result.torque_nm >= 80.0
    assert result.current_a <= sample_params().i_max_a


def test_field_weakening_respects_voltage_limit():
    params = sample_params()
    result = field_weakening_search(
        params,
        target_torque_nm=80.0,
        mechanical_speed_rpm=8000.0,
        current_step_a=20.0,
    )

    assert result.feasible
    assert result.voltage_v <= params.vmax_phase_v + 1e-9
    assert result.torque_nm >= 80.0


def test_mtpv_returns_maximum_feasible_torque_point():
    params = sample_params()
    result = mtpv_grid_search(params, mechanical_speed_rpm=12000.0, current_step_a=25.0)

    assert result.feasible
    assert result.voltage_v <= params.vmax_phase_v + 1e-9
    assert result.current_a <= params.i_max_a + 1e-9
    assert result.torque_nm > 0.0
