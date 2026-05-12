# EXP-002 Variable Flux State Comparison

## Purpose

Compare control-only weak flux with virtual lower `ψf` states. This experiment represents a clean-room approximation of true equivalent `Ke` reduction, without claiming any specific hardware implementation.

## Method

The baseline motor parameters are copied into several virtual flux states:

- `psi_100pct`: original permanent-magnet flux linkage;
- `psi_85pct`: 85% equivalent `ψf`;
- `psi_70pct`: 70% equivalent `ψf`;
- `psi_55pct`: 55% equivalent `ψf`.

For each speed and flux state, the experiment searches for the minimum-current feasible grid point that reaches the target torque under voltage/current constraints.

## Important limitations

This is not yet a physical memory-motor model. It does not include:

- magnetization or demagnetization pulse energy;
- irreversible demagnetization boundary;
- magnetic-state observer error;
- Ld/Lq changes across magnetic states;
- iron loss, inverter loss, or thermal derating;
- torque shock during state switching.

## Outputs

- `summary.json`: per-state maximum target-speed reachability and coarse margins.
- `variable_flux_scan.csv`: speed-by-state operating-point scan.

## Interpretation

If a lower `ψf` state reaches higher speed with less negative `id`, it supports the hypothesis that true equivalent `Ke` reduction can reduce voltage pressure compared with control-only weak flux. If low `ψf` fails low-speed target torque, the state must be used only in high-speed operating regions or combined with state switching.
