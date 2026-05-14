"""Tests for sim/iron_loss.py and sim/run_iron_loss_experiment.py."""

from __future__ import annotations

import json
from math import isclose, sqrt
from pathlib import Path

from sim.iron_loss import (
    BertottiCoeffs,
    SteinmetzCoeffs,
    bertotti_iron_loss_per_phase,
    flux_density_from_lambda,
    iron_loss_from_id_iq,
    steinmetz_iron_loss_per_phase,
    combined_losses,
    DEFAULT_BERTOTTI,
    DEFAULT_STEINMETZ,
)
from sim.run_iron_loss_experiment import run


EXPERIMENT_DIR = Path("experiments/exp_011_iron_loss")
SUMMARY_PATH = EXPERIMENT_DIR / "summary.json"
CSV_PATH = EXPERIMENT_DIR / "iron_loss_sweep_results.csv"


class TestBertottiCoeffs:
    def test_valid_construction(self) -> None:
        coeffs = BertottiCoeffs(k_hyst=0.04, k_eddy=0.004, k_excess=0.003)
        assert coeffs.k_hyst == 0.04
        assert coeffs.k_eddy == 0.004
        assert coeffs.k_excess == 0.003
        coeffs.validate()

    def test_negative_coefficient_raises(self) -> None:
        import pytest
        with pytest.raises(ValueError, match="must be positive"):
            BertottiCoeffs(k_hyst=-0.01, k_eddy=0.004, k_excess=0.003)
        with pytest.raises(ValueError, match="must be positive"):
            BertottiCoeffs(k_hyst=0.04, k_eddy=-0.001, k_excess=0.003)
        with pytest.raises(ValueError, match="must be positive"):
            BertottiCoeffs(k_hyst=0.04, k_eddy=0.004, k_excess=-0.001)

    def test_inf_coefficient_raises_at_construction(self) -> None:
        import pytest
        with pytest.raises(ValueError, match="must be finite"):
            BertottiCoeffs(k_hyst=float("inf"), k_eddy=0.004, k_excess=0.003)


class TestSteinmetzCoeffs:
    def test_valid_construction(self) -> None:
        coeffs = SteinmetzCoeffs(k_st=0.03, alpha=1.4, beta=2.0)
        assert coeffs.k_st == 0.03
        assert coeffs.alpha == 1.4
        assert coeffs.beta == 2.0
        coeffs.validate()

    def test_invalid_alpha_raises(self) -> None:
        import pytest
        with pytest.raises(ValueError, match="alpha must be in"):
            SteinmetzCoeffs(k_st=0.03, alpha=0.1, beta=2.0)
        with pytest.raises(ValueError, match="alpha must be in"):
            SteinmetzCoeffs(k_st=0.03, alpha=5.0, beta=2.0)


class TestFluxDensityFromLambda:
    def test_flux_density_calculation(self) -> None:
        # B_peak = lambda_peak / (sqrt(2) * A), A = pi * r^2
        # For r=0.05m, A = pi * 0.0025 = 0.00785398 m^2
        # B_peak = 0.055 / (1.414 * 0.00785) = 4.95 T (for psi_f baseline)
        b = flux_density_from_lambda(0.055, 0.05)
        expected_area = 3.14159265359 * 0.05 * 0.05
        expected_b = 0.055 / (sqrt(2.0) * expected_area)
        assert isclose(b, expected_b, rel_tol=1e-9)

    def test_negative_lambda_gives_positive_b(self) -> None:
        b = flux_density_from_lambda(-0.055, 0.05)
        assert b > 0

    def test_zero_radius_raises(self) -> None:
        import pytest
        with pytest.raises(ValueError, match="core_radius_m must be positive"):
            flux_density_from_lambda(0.055, 0.0)


class TestBertottiIronLoss:
    def test_iron_loss_increases_with_frequency(self) -> None:
        coeffs = BertottiCoeffs(k_hyst=0.04, k_eddy=0.004, k_excess=0.003)
        iron_50hz = bertotti_iron_loss_per_phase(0.055, 0.0, 50.0, coeffs, 0.05)
        iron_100hz = bertotti_iron_loss_per_phase(0.055, 0.0, 100.0, coeffs, 0.05)
        assert iron_100hz.total_per_phase_w > iron_50hz.total_per_phase_w

    def test_iron_loss_increases_with_flux(self) -> None:
        coeffs = DEFAULT_BERTOTTI
        iron_low = bertotti_iron_loss_per_phase(0.03, 0.0, 100.0, coeffs, 0.05)
        iron_high = bertotti_iron_loss_per_phase(0.06, 0.0, 100.0, coeffs, 0.05)
        assert iron_high.total_per_phase_w > iron_low.total_per_phase_w

    def test_three_term_breakdown(self) -> None:
        coeffs = BertottiCoeffs(k_hyst=0.04, k_eddy=0.004, k_excess=0.003)
        b_peak = flux_density_from_lambda(0.055, 0.05)
        freq_hz = 100.0
        iron = bertotti_iron_loss_per_phase(0.055, 0.0, freq_hz, coeffs, 0.05)

        # Hysteresis: k_hyst * f * B^2
        expected_hyst = coeffs.k_hyst * freq_hz * b_peak * b_peak
        assert isclose(iron.hysteresis_w, expected_hyst, rel_tol=1e-9)

        # Eddy: k_eddy * f^2 * B^2
        expected_eddy = coeffs.k_eddy * freq_hz * freq_hz * b_peak * b_peak
        assert isclose(iron.eddy_current_w, expected_eddy, rel_tol=1e-9)

        # Total
        assert isclose(
            iron.total_per_phase_w,
            iron.hysteresis_w + iron.eddy_current_w + iron.excess_w,
            rel_tol=1e-9,
        )

    def test_total_three_phase(self) -> None:
        coeffs = DEFAULT_BERTOTTI
        iron = bertotti_iron_loss_per_phase(0.055, 0.0, 100.0, coeffs, 0.05)
        assert iron.total_three_phase_w == 3.0 * iron.total_per_phase_w


class TestSteinmetzIronLoss:
    def test_steinmetz_total_in_hysteresis_field(self) -> None:
        coeffs = SteinmetzCoeffs(k_st=0.03, alpha=1.4, beta=2.0)
        iron = steinmetz_iron_loss_per_phase(0.055, 0.0, 100.0, coeffs, 0.05)

        b_peak = flux_density_from_lambda(0.055, 0.05)
        expected = coeffs.k_st * (100.0 ** coeffs.alpha) * (b_peak ** coeffs.beta)
        assert isclose(iron.hysteresis_w, expected, rel_tol=1e-9)
        assert iron.eddy_current_w == 0.0
        assert iron.excess_w == 0.0
        assert iron.total_per_phase_w == iron.hysteresis_w

    def test_steinmetz_frequency_scaling(self) -> None:
        coeffs = SteinmetzCoeffs(k_st=0.03, alpha=1.4, beta=2.0)
        iron_50 = steinmetz_iron_loss_per_phase(0.055, 0.0, 50.0, coeffs, 0.05)
        iron_100 = steinmetz_iron_loss_per_phase(0.055, 0.0, 100.0, coeffs, 0.05)
        # At 100Hz, loss should be 2^1.4 = 2.64x higher than 50Hz
        ratio = iron_100.total_per_phase_w / iron_50.total_per_phase_w
        expected_ratio = 2.0 ** 1.4
        assert isclose(ratio, expected_ratio, rel_tol=1e-6)


class TestIronLossFromIdIq:
    def test_linear_flux_from_id_iq(self) -> None:
        # lambda_d = ld * id + psi_f, lambda_q = lq * iq
        iron = iron_loss_from_id_iq(
            id_a=0.0, iq_a=100.0,
            ld_h=0.00018, lq_h=0.00042, psi_f_wb=0.055,
            freq_hz=100.0,
            coeffs=DEFAULT_BERTOTTI,
        )
        assert iron.total_per_phase_w > 0

    def test_zero_current_gives_zero_flux_contribution(self) -> None:
        iron = iron_loss_from_id_iq(
            id_a=0.0, iq_a=0.0,
            ld_h=0.00018, lq_h=0.00042, psi_f_wb=0.055,
            freq_hz=100.0,
            coeffs=DEFAULT_BERTOTTI,
        )
        # With zero current, only psi_f contributes
        assert iron.total_per_phase_w > 0  # PM flux still causes some iron loss


class TestCombinedLosses:
    def test_combined_loss_additive(self) -> None:
        coeffs = DEFAULT_BERTOTTI
        iron = bertotti_iron_loss_per_phase(0.055, 0.0, 100.0, coeffs, 0.05)
        copper_w = 1000.0

        total, eff = combined_losses(iron, copper_w)
        assert total == iron.total_three_phase_w + copper_w
        assert 0.0 <= eff <= 1.0

    def test_zero_copper_loss(self) -> None:
        coeffs = DEFAULT_BERTOTTI
        iron = bertotti_iron_loss_per_phase(0.055, 0.0, 100.0, coeffs, 0.05)
        total, eff = combined_losses(iron, 0.0)
        assert total == iron.total_three_phase_w
        assert eff == 1.0


class TestIronLossExperiment:
    def test_iron_loss_experiment_writes_summary_and_csv(self) -> None:
        summary = run()

        assert SUMMARY_PATH.exists()
        assert CSV_PATH.exists()
        assert summary["experiment"] == "exp_011_iron_loss"
        assert summary["model_scope"] == "linear_dq_with_iron_loss_estimation"
        assert summary["iron_loss_model"]["type"] == "bertotti_three_term"

    def test_iron_loss_experiment_summary_contains_key_metrics(self) -> None:
        summary = run()

        assert "avg_iron_loss_at_target_torque_w" in summary
        assert "avg_efficiency_at_target_torque_pct" in summary
        assert "target_torque_feasible_count" in summary
        assert "iron_loss_vs_copper_loss_ratio" in summary
        assert summary["target_torque_nm"] == 100.0

    def test_iron_loss_experiment_csv_has_iron_loss_columns(self) -> None:
        run()
        with CSV_PATH.open("r", encoding="utf-8") as f:
            header = f.readline().strip()
        assert "baseline_iron_loss_w" in header
        assert "min_current_target_iron_loss_w" in header
        assert "min_current_target_efficiency_pct" in header
        assert "min_current_target_b_peak_t" in header

    def test_iron_loss_experiment_csv_row_count(self) -> None:
        summary = run()
        with CSV_PATH.open("r", encoding="utf-8") as f:
            row_count = sum(1 for _ in f) - 1  # subtract header
        max_speed = summary["max_speed_scanned_rpm"]
        step = summary["scan_step_rpm"]
        expected_rows = int(max_speed / step) + 1
        assert row_count == expected_rows

    def test_iron_loss_experiment_persists_to_disk(self) -> None:
        summary = run()
        saved = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        assert saved["experiment"] == "exp_011_iron_loss"
        assert saved["target_torque_nm"] == 100.0