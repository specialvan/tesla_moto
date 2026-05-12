# EXP-003 Parameter-Family Sweep

## Purpose

Explore whether low `ψf` can become useful when co-designed with saliency (`Lq/Ld`), voltage, and current capability.

## Sweep axes

- `ψf` scale: 100%, 85%, 70%
- `Ld` scale: 80%, 100%, 120%
- `Lq` scale: 100%, 130%, 160%
- `Vdc` scale: 100%, 115%
- `Imax` scale: 100%, 115%

## Evaluation points

- Low-speed peak requirement: 100 Nm at 1000 rpm
- High-speed requirement: 60 Nm at 12000 rpm
- High-speed max feasible torque at 12000 rpm

## Score

The score is a heuristic ranking metric:

```text
score = high_voltage_margin + 0.25 * high_max_torque
        - 0.002 * (low_copper_loss + high_copper_loss)
        - 0.05 * abs(high_target_id)
```

Any candidate that cannot satisfy low-speed peak torque receives a large negative score. Any candidate that passes low speed but fails high-speed target torque receives a smaller negative score.

## Current result

With the current illustrative linear model, the top ranked variant is `psi1.00_ld0.80_lq1.60_vdc1.15_imax1.15`. It keeps the 100 Nm low-speed point feasible and reaches the 12000 rpm / 60 Nm high-speed point with about 4.06 V voltage margin and 68.58 A current margin. The best low-flux candidate, `psi0.70_ld0.80_lq1.60_vdc1.15_imax1.15`, ranks second and keeps about 5.08 V voltage margin at the same high-speed target.

Interpretation: low `ψf` only becomes competitive in this simplified scan when paired with high saliency and higher voltage/current capability. These are candidate regions for nonlinear FEA/LUT validation, not validated geometry recommendations.

## Important limitations

This is not an electromagnetic design. It scales parameters independently and only identifies promising parameter regions for later FEA/Pyleecan/SyR-e exploration.

The experiment does not include:

- nonlinear saturation;
- cross-saturation;
- demagnetization limits;
- iron loss;
- inverter voltage drop;
- mechanical stress;
- thermal derating.

## Outputs

- `summary.json`: ranked top candidates and sweep metadata.
- `param_sweep_results.csv`: full ranked parameter sweep.
