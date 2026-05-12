# EXP-001 Linear dq Baseline

## Purpose

Validate the first clean-room controllable-flux simulation loop using a quasi-steady linear dq IPMSM model.

## Model scope

This experiment uses:

- amplitude-invariant dq convention;
- phase peak current and phase peak voltage;
- single-phase Rs;
- quasi-steady voltage equations;
- grid-search minimum-current target torque and maximum-feasible-torque approximations.

It does not yet include:

- current-loop dynamics;
- nonlinear λd/λq LUT;
- iron loss;
- inverter loss;
- thermal derating;
- demagnetization boundary;
- sensor delay or PWM nonlinearity.

## Current result

Using `models/motor_params.json` baseline parameters:

- target torque: 100 Nm;
- DC bus: 360 V;
- SVPWM linear phase peak voltage limit: 207.85 V;
- current limit: 260 A peak;
- minimum-current target torque point reachable to 6750 rpm;
- maximum-feasible positive torque point remains feasible to 18000 rpm.

The `id_zero` target is not reachable at any scanned speed because the baseline IPMSM needs negative d-axis current to reduce current magnitude / exploit reluctance torque for the selected target.

## Outputs

- `summary.json`: compact experiment summary.
- `scan_results.csv`: speed sweep with `id_zero`, `min_current_target`, and `max_feasible_torque` candidates.

## Next steps

1. Add plots for torque-speed, id/iq-speed, voltage margin, and copper loss.
2. Add nonlinear `λd/λq` LUT schema.
3. Add demagnetization and temperature limits for negative `id`.
4. Add variable `ψf` experiment to compare true low-Ke states against control-only weak flux.
