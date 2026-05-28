"""Nonlinear lambda_d/lambda_q LUT interpolation for dq torque checks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any

EXPECTED_FLUX_LUT_UNIT_CONVENTION = {
    "dq_transform": "amplitude_invariant",
    "current": "phase_peak_ampere",
    "flux_linkage": "weber",
}


@dataclass(frozen=True)
class FluxPoint:
    lambda_d_wb: float
    lambda_q_wb: float


@dataclass(frozen=True)
class FluxLut:
    motor_id: str
    pole_pairs: int
    unit_convention: dict[str, str]
    id_axis_a: list[float]
    iq_axis_a: list[float]
    lambda_d_wb: list[list[float]]
    lambda_q_wb: list[list[float]]
    maturity: dict[str, Any]

    @staticmethod
    def from_file(path: Path | str) -> "FluxLut":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return FluxLut.from_dict(raw)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "FluxLut":
        required = [
            "motor_id",
            "pole_pairs",
            "unit_convention",
            "id_axis_a",
            "iq_axis_a",
            "lambda_d_wb",
            "lambda_q_wb",
            "maturity",
        ]
        missing = [field for field in required if field not in data]
        if missing:
            raise ValueError(f"Missing flux LUT fields: {', '.join(missing)}")

        lut = FluxLut(
            motor_id=str(data["motor_id"]),
            pole_pairs=int(data["pole_pairs"]),
            unit_convention={
                str(key): str(value) for key, value in data["unit_convention"].items()
            },
            id_axis_a=[float(value) for value in data["id_axis_a"]],
            iq_axis_a=[float(value) for value in data["iq_axis_a"]],
            lambda_d_wb=[
                [float(value) for value in row] for row in data["lambda_d_wb"]
            ],
            lambda_q_wb=[
                [float(value) for value in row] for row in data["lambda_q_wb"]
            ],
            maturity=dict(data["maturity"]),
        )
        lut.validate()
        return lut

    def validate(self) -> None:
        if not self.motor_id:
            raise ValueError("motor_id must not be empty")
        if self.pole_pairs <= 0:
            raise ValueError("pole_pairs must be positive")
        if self.unit_convention != EXPECTED_FLUX_LUT_UNIT_CONVENTION:
            raise ValueError(
                "unit_convention must match the amplitude-invariant phase-peak flux LUT schema"
            )
        _validate_maturity(self.maturity)
        if len(self.id_axis_a) < 2 or len(self.iq_axis_a) < 2:
            raise ValueError("flux LUT axes must each contain at least two points")
        if not _is_strictly_increasing(self.id_axis_a):
            raise ValueError("id_axis_a must be strictly increasing")
        if not _is_strictly_increasing(self.iq_axis_a):
            raise ValueError("iq_axis_a must be strictly increasing")

        values = [*self.id_axis_a, *self.iq_axis_a]
        values.extend(value for row in self.lambda_d_wb for value in row)
        values.extend(value for row in self.lambda_q_wb for value in row)
        if not all(isfinite(value) for value in values):
            raise ValueError("flux LUT values must be finite")

        expected_rows = len(self.id_axis_a)
        expected_cols = len(self.iq_axis_a)
        for name, table in {
            "lambda_d_wb": self.lambda_d_wb,
            "lambda_q_wb": self.lambda_q_wb,
        }.items():
            if len(table) != expected_rows:
                raise ValueError(f"{name} row count must match id_axis_a")
            if any(len(row) != expected_cols for row in table):
                raise ValueError(f"{name} column count must match iq_axis_a")

    def contains(self, id_a: float, iq_a: float) -> bool:
        return (
            self.id_axis_a[0] <= id_a <= self.id_axis_a[-1]
            and self.iq_axis_a[0] <= iq_a <= self.iq_axis_a[-1]
        )

    def interpolate(self, id_a: float, iq_a: float) -> FluxPoint:
        if not self.contains(id_a, iq_a):
            raise ValueError("current point is outside the flux LUT bounds")
        lower_id = _lower_index(self.id_axis_a, id_a)
        lower_iq = _lower_index(self.iq_axis_a, iq_a)
        lambda_d = _bilinear(
            self.id_axis_a,
            self.iq_axis_a,
            self.lambda_d_wb,
            lower_id,
            lower_iq,
            id_a,
            iq_a,
        )
        lambda_q = _bilinear(
            self.id_axis_a,
            self.iq_axis_a,
            self.lambda_q_wb,
            lower_id,
            lower_iq,
            id_a,
            iq_a,
        )
        return FluxPoint(lambda_d_wb=lambda_d, lambda_q_wb=lambda_q)


def nonlinear_torque_nm(
    lut: FluxLut, pole_pairs: int, id_a: float, iq_a: float
) -> float:
    if pole_pairs <= 0:
        raise ValueError("pole_pairs must be positive")
    lambdas = lut.interpolate(id_a, iq_a)
    return 1.5 * pole_pairs * (lambdas.lambda_d_wb * iq_a - lambdas.lambda_q_wb * id_a)


def _is_strictly_increasing(axis: list[float]) -> bool:
    return all(axis[index] < axis[index + 1] for index in range(len(axis) - 1))


def _validate_maturity(maturity: dict[str, Any]) -> None:
    required = {
        "model_maturity",
        "physics_model_validated",
        "engineering_validated",
        "production_release_allowed",
        "required_replacement",
    }
    missing = sorted(required - set(maturity))
    if missing:
        raise ValueError(f"Missing flux LUT maturity fields: {', '.join(missing)}")
    if maturity["model_maturity"] != "synthetic_fixture":
        raise ValueError("model_maturity must be synthetic_fixture")
    for field in (
        "physics_model_validated",
        "engineering_validated",
        "production_release_allowed",
    ):
        if maturity[field] is not False:
            raise ValueError(f"{field} must be false")
    replacement = maturity["required_replacement"]
    if not isinstance(replacement, str) or not replacement:
        raise ValueError("required_replacement must be a non-empty string")


def _lower_index(axis: list[float], value: float) -> int:
    if value == axis[-1]:
        return len(axis) - 2
    for index in range(len(axis) - 1):
        if axis[index] <= value <= axis[index + 1]:
            return index
    raise ValueError("value outside axis")


def _bilinear(
    id_axis: list[float],
    iq_axis: list[float],
    table: list[list[float]],
    id_index: int,
    iq_index: int,
    id_a: float,
    iq_a: float,
) -> float:
    id0 = id_axis[id_index]
    id1 = id_axis[id_index + 1]
    iq0 = iq_axis[iq_index]
    iq1 = iq_axis[iq_index + 1]
    q11 = table[id_index][iq_index]
    q12 = table[id_index][iq_index + 1]
    q21 = table[id_index + 1][iq_index]
    q22 = table[id_index + 1][iq_index + 1]
    id_ratio = 0.0 if id1 == id0 else (id_a - id0) / (id1 - id0)
    iq_ratio = 0.0 if iq1 == iq0 else (iq_a - iq0) / (iq1 - iq0)
    lower = q11 + (q21 - q11) * id_ratio
    upper = q12 + (q22 - q12) * id_ratio
    return lower + (upper - lower) * iq_ratio
