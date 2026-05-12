"""Linear dq IPMSM model using amplitude-invariant, phase-peak conventions."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi, sqrt
from typing import Any

EXPECTED_UNIT_CONVENTION = {
    "dq_transform": "amplitude_invariant",
    "current": "phase_peak_ampere",
    "voltage": "phase_peak_volt",
    "resistance": "single_phase_ohm",
    "speed": "mechanical_rpm_input_and_electrical_rad_per_second_internal",
}


@dataclass(frozen=True)
class MotorParams:
    """Motor parameters for the v1 quasi-steady linear dq model."""

    name: str
    pole_pairs: int
    rs_ohm: float
    ld_h: float
    lq_h: float
    psi_f_wb: float
    vdc_v: float
    i_max_a: float
    speed_max_rpm: float
    torque_target_nm: float
    temperature_c: float = 25.0
    svpwm_linear_vmax_factor: float = 1.0 / sqrt(3.0)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "MotorParams":
        required = [
            "name",
            "pole_pairs",
            "Rs_ohm",
            "Ld_h",
            "Lq_h",
            "psi_f_wb",
            "Vdc_v",
            "Imax_a",
            "speed_max_rpm",
            "torque_target_nm",
            "svpwm_linear_vmax_factor",
        ]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Missing motor parameter fields: {', '.join(missing)}")

        unit_convention = data.get("unit_convention")
        if unit_convention != EXPECTED_UNIT_CONVENTION:
            raise ValueError(
                "unit_convention must match the v1 amplitude-invariant phase-peak schema"
            )

        params = MotorParams(
            name=str(data["name"]),
            pole_pairs=int(data["pole_pairs"]),
            rs_ohm=float(data["Rs_ohm"]),
            ld_h=float(data["Ld_h"]),
            lq_h=float(data["Lq_h"]),
            psi_f_wb=float(data["psi_f_wb"]),
            vdc_v=float(data["Vdc_v"]),
            i_max_a=float(data["Imax_a"]),
            speed_max_rpm=float(data["speed_max_rpm"]),
            torque_target_nm=float(data["torque_target_nm"]),
            temperature_c=float(data.get("temperature_c", 25.0)),
            svpwm_linear_vmax_factor=float(data["svpwm_linear_vmax_factor"]),
        )
        params.validate()
        return params

    def validate(self) -> None:
        if self.pole_pairs <= 0:
            raise ValueError("pole_pairs must be positive")

        finite_fields = {
            "rs_ohm": self.rs_ohm,
            "ld_h": self.ld_h,
            "lq_h": self.lq_h,
            "psi_f_wb": self.psi_f_wb,
            "vdc_v": self.vdc_v,
            "i_max_a": self.i_max_a,
            "speed_max_rpm": self.speed_max_rpm,
            "torque_target_nm": self.torque_target_nm,
            "temperature_c": self.temperature_c,
            "svpwm_linear_vmax_factor": self.svpwm_linear_vmax_factor,
        }
        non_finite = [
            name for name, value in finite_fields.items() if not isfinite(value)
        ]
        if non_finite:
            raise ValueError(f"Parameters must be finite: {', '.join(non_finite)}")

        positive_fields = {
            "rs_ohm": self.rs_ohm,
            "ld_h": self.ld_h,
            "lq_h": self.lq_h,
            "psi_f_wb": self.psi_f_wb,
            "vdc_v": self.vdc_v,
            "i_max_a": self.i_max_a,
            "speed_max_rpm": self.speed_max_rpm,
            "svpwm_linear_vmax_factor": self.svpwm_linear_vmax_factor,
        }
        invalid = [name for name, value in positive_fields.items() if value <= 0]
        if invalid:
            raise ValueError(f"Parameters must be positive: {', '.join(invalid)}")
        if self.torque_target_nm < 0:
            raise ValueError("torque_target_nm must be non-negative")

    @property
    def vmax_v(self) -> float:
        return self.vdc_v * self.svpwm_linear_vmax_factor

    @property
    def vmax_phase_v(self) -> float:
        return self.vmax_v

    @property
    def imax_a(self) -> float:
        return self.i_max_a

    def mechanical_to_electrical_rad_s(self, mechanical_speed_rpm: float) -> float:
        return mechanical_rpm_to_electrical_rad_per_second(
            mechanical_speed_rpm, self.pole_pairs
        )

    def flux_d(self, id_a: float) -> float:
        return flux_d(self, id_a)

    def flux_q(self, iq_a: float) -> float:
        return flux_q(self, iq_a)

    def voltage_d(self, id_a: float, iq_a: float, omega_e_rad_s: float) -> float:
        return voltage_d_v(self, id_a, iq_a, omega_e_rad_s)

    def voltage_q(self, id_a: float, iq_a: float, omega_e_rad_s: float) -> float:
        return voltage_q_v(self, id_a, iq_a, omega_e_rad_s)

    def torque_nm(self, id_a: float, iq_a: float) -> float:
        return torque_nm(self, id_a, iq_a)


def mechanical_rpm_to_electrical_rad_per_second(
    speed_rpm: float, pole_pairs: int
) -> float:
    if not isfinite(speed_rpm):
        raise ValueError("speed_rpm must be finite")
    if pole_pairs <= 0:
        raise ValueError("pole_pairs must be positive")
    return speed_rpm * 2.0 * pi / 60.0 * pole_pairs


def flux_d(params: MotorParams, id_a: float) -> float:
    return params.ld_h * id_a + params.psi_f_wb


def flux_q(params: MotorParams, iq_a: float) -> float:
    return params.lq_h * iq_a


def torque_nm(params: MotorParams, id_a: float, iq_a: float) -> float:
    pm_torque = params.psi_f_wb * iq_a
    reluctance_torque = (params.ld_h - params.lq_h) * id_a * iq_a
    return 1.5 * params.pole_pairs * (pm_torque + reluctance_torque)


def voltage_d_v(params: MotorParams, id_a: float, iq_a: float, omega_e: float) -> float:
    return params.rs_ohm * id_a - omega_e * flux_q(params, iq_a)


def voltage_q_v(params: MotorParams, id_a: float, iq_a: float, omega_e: float) -> float:
    return params.rs_ohm * iq_a + omega_e * flux_d(params, id_a)


def voltage_mag_v(
    params: MotorParams, id_a: float, iq_a: float, omega_e: float
) -> float:
    vd_v = voltage_d_v(params, id_a, iq_a, omega_e)
    vq_v = voltage_q_v(params, id_a, iq_a, omega_e)
    return voltage_magnitude(vd_v, vq_v)


def current_mag_a(id_a: float, iq_a: float) -> float:
    return sqrt(id_a * id_a + iq_a * iq_a)


def current_magnitude(id_a: float, iq_a: float) -> float:
    return current_mag_a(id_a, iq_a)


def voltage_magnitude(vd_v: float, vq_v: float) -> float:
    return sqrt(vd_v * vd_v + vq_v * vq_v)


def copper_loss(current_rms_a: float, rs_ohm: float) -> float:
    if current_rms_a < 0 or rs_ohm <= 0:
        raise ValueError(
            "current_rms_a must be non-negative and rs_ohm must be positive"
        )
    return 3.0 * current_rms_a * current_rms_a * rs_ohm


def copper_loss_w(params: MotorParams, id_a: float, iq_a: float) -> float:
    current_peak = current_mag_a(id_a, iq_a)
    current_rms = current_peak / sqrt(2.0)
    return copper_loss(current_rms, params.rs_ohm)


def point_is_safe(
    params: MotorParams, id_a: float, iq_a: float, omega_e: float
) -> bool:
    return (
        current_mag_a(id_a, iq_a) <= params.imax_a
        and voltage_mag_v(params, id_a, iq_a, omega_e) <= params.vmax_v
    )
