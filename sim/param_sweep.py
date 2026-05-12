"""Parameter-family sweep for low-flux high-saliency IPMSM studies."""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
from math import isfinite
from typing import Iterable

from .dq_model import MotorParams


@dataclass(frozen=True)
class ParamVariant:
    """A scaled motor-parameter variant for topology-family exploration."""

    name: str
    psi_scale: float
    ld_scale: float
    lq_scale: float
    vdc_scale: float
    imax_scale: float
    params: MotorParams

    @property
    def saliency_ratio(self) -> float:
        return self.params.lq_h / self.params.ld_h


def validate_scale(name: str, value: float) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def make_variant(
    base: MotorParams,
    psi_scale: float,
    ld_scale: float,
    lq_scale: float,
    vdc_scale: float,
    imax_scale: float,
) -> ParamVariant:
    """Create an immutable scaled motor variant."""
    scales = {
        "psi_scale": psi_scale,
        "ld_scale": ld_scale,
        "lq_scale": lq_scale,
        "vdc_scale": vdc_scale,
        "imax_scale": imax_scale,
    }
    for name, value in scales.items():
        validate_scale(name, value)

    name = (
        f"psi{psi_scale:.2f}_ld{ld_scale:.2f}_lq{lq_scale:.2f}_"
        f"vdc{vdc_scale:.2f}_imax{imax_scale:.2f}"
    )
    params = replace(
        base,
        name=f"{base.name}_{name}",
        psi_f_wb=base.psi_f_wb * psi_scale,
        ld_h=base.ld_h * ld_scale,
        lq_h=base.lq_h * lq_scale,
        vdc_v=base.vdc_v * vdc_scale,
        i_max_a=base.i_max_a * imax_scale,
    )
    params.validate()
    return ParamVariant(
        name=name,
        psi_scale=psi_scale,
        ld_scale=ld_scale,
        lq_scale=lq_scale,
        vdc_scale=vdc_scale,
        imax_scale=imax_scale,
        params=params,
    )


def variant_grid(
    base: MotorParams,
    psi_scales: Iterable[float],
    ld_scales: Iterable[float],
    lq_scales: Iterable[float],
    vdc_scales: Iterable[float],
    imax_scales: Iterable[float],
) -> Iterable[ParamVariant]:
    for psi_scale, ld_scale, lq_scale, vdc_scale, imax_scale in product(
        psi_scales, ld_scales, lq_scales, vdc_scales, imax_scales
    ):
        yield make_variant(base, psi_scale, ld_scale, lq_scale, vdc_scale, imax_scale)
