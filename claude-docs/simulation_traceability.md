# Claude 数值仿真追踪矩阵

## 1. 总览

当前 `claude-mainline` 的 `models/scheme_simulation_coverage.json` 用于追踪 12 类可控磁通量方案到仿真、测试、报告或下一步数值模型的状态。

| 状态 | 含义 |
|---|---|
| `passed_numeric_simulation` | 已有可运行数值实验和测试覆盖 |
| `needs_next_numeric_model` | 已有工程方向或代理证据，但缺少专门数值模型 |
| `passed_architecture_verification` | 工程目录/阶段门可追踪，但未形成完整数值评分 |

该矩阵证明的是证据链完整性，不等于工程释放。

## 2. 方案到实验映射

| 方案 ID | 当前状态 | 当前证据 | 主要测试 | 下一步 |
|---|---|---|---|---|
| `negative_d_axis_field_weakening` | `passed_numeric_simulation` | EXP-001 | `tests/test_dq_model.py`, `tests/test_param_sweep.py` | 增加温度相关 `id_min(T)` |
| `mtpa_fw_mtpv_control` | `passed_numeric_simulation` | EXP-001 | `tests/test_exp_001_runner.py`, `tests/test_dq_model.py` | 生成控制 LUT 并检查模式切换连续性 |
| `svpwm_overmodulation_voltage_utilization` | `passed_numeric_simulation` | EXP-005 | `tests/test_modulation.py`, `tests/test_modulation_factor_experiment.py` | 用实测逆变器损耗图和 PWM 重建 THD 替换参数惩罚 |
| `nonlinear_flux_lut` | `passed_numeric_simulation` | EXP-006 phase-1 + phase-2 synthetic LUT | `tests/test_nonlinear_flux_lut.py`, `tests/test_nonlinear_flux_lut_search.py`, `tests/test_scheme_catalog.py` | 用 FEA/测量 `lambda_d/lambda_q` 替换 synthetic LUT，并导出共享控制 LUT |
| `magnetic_saturation_codesign` | `passed_numeric_simulation` | EXP-003 | `tests/test_param_sweep.py` | 用 FEA `lambda_d/lambda_q` 替换缩放代理 |
| `pmasynrm_high_saliency_low_pm` | `passed_numeric_simulation` | EXP-003 | `tests/test_param_sweep.py` | 增加 PM fraction 和转矩脉动筛选 |
| `variable_magnetization_memory_motor` | `passed_numeric_simulation` | EXP-002 | `tests/test_variable_flux.py` | 增加状态转换能量和未知状态降额 |
| `hybrid_excitation` | `passed_numeric_simulation` | EXP-007 | `tests/test_hybrid_excitation.py`, `tests/test_hybrid_excitation_experiment.py` | 增加励磁绕组电感、励磁损耗和转子漏磁，并做热耦合 |
| `winding_reconfiguration` | `passed_numeric_simulation` | EXP-008 | `tests/test_winding_reconfiguration.py`, `tests/test_winding_reconfiguration_experiment.py` | 建模接触器切换瞬态、环流和并联支路热分配 |
| `multiphase_phase_group_control` | `passed_numeric_simulation` | EXP-009 | `tests/test_multiphase_phase_group.py`, `tests/test_multiphase_phase_group_experiment.py` | 增加谐波子空间解耦、中性点偏移电压矢量和每相热 RC |
| `thermal_demag_safety_protection` | `passed_numeric_simulation` | EXP-004 | `tests/test_safety_limits.py`, `tests/test_safety_boundary_experiment.py` | 用 FEA 或磁钢数据替换简化退磁线 |
| `weighted_efficiency_pareto_selection` | `passed_numeric_simulation` | EXP-010 | `tests/test_drive_cycle.py`, `tests/test_weighted_efficiency_pareto_experiment.py` | 用实测工况替换示意工况，并补充铁耗/机械损耗/逆变器损耗 |

## 3. 已落地实验

| 实验 | 模型范围 | 结果路径 |
|---|---|---|
| EXP-001 | `quasi_steady_linear_dq_grid_search` | `experiments/exp_001_linear_dq/summary.json` |
| EXP-002 | `quasi_steady_linear_dq_virtual_psi_f_scaling` | `experiments/exp_002_variable_flux/summary.json` |
| EXP-003 | `quasi_steady_linear_dq_scaled_parameter_family` | `experiments/exp_003_param_sweep/summary.json` |
| EXP-004 | `temperature_corrected_linear_dq_with_simplified_demag_limit` | `experiments/exp_004_safety_boundaries/summary.json` |
| EXP-005 | `linear_dq_with_explicit_modulation_factor_penalties` | `experiments/exp_005_modulation_factor/summary.json` |
| EXP-006 | `synthetic_lambda_d_lambda_q_lut_interpolation` | `experiments/exp_006_nonlinear_flux_lut/summary.json` |
| EXP-006 phase-2 | `quasi_steady_nonlinear_flux_lut_grid_search` | `experiments/exp_006_nonlinear_flux_lut/lut_search_summary.json` |
| EXP-007 | `quasi_steady_linear_dq_with_hybrid_excitation_proxy` | `experiments/exp_007_hybrid_excitation/summary.json` |
| EXP-008 | `quasi_steady_linear_dq_with_winding_reconfiguration_proxy` | `experiments/exp_008_winding_reconfiguration/summary.json` |
| EXP-009 | `quasi_steady_linear_dq_with_multiphase_phase_group_derating` | `experiments/exp_009_multiphase_phase_group/summary.json` |
| EXP-010 | `weighted_efficiency_route_screening` | `experiments/exp_010_weighted_efficiency_pareto/summary.json` |

## 4. 当前深化方向

| 方向 | 当前基线 | 下一步最小深化 |
|---|---|---|
| EXP-004 安全边界 | 简化 `id_min(T)` 退磁线 | 用 FEA 或磁钢数据替换简化退磁线 |
| EXP-005 调制利用率 | 参数化 `k_mod`、THD/损耗惩罚 | 接入实测逆变器损耗图与 PWM 重建 THD |
| EXP-006 非线性磁链 LUT | synthetic LUT + constrained search | 用 FEA/测量 `lambda_d/lambda_q` 替换 synthetic LUT，并导出共享控制 LUT |
| EXP-007 混合励磁 | 等效 `psi_eff = psi_pm + kf * if` | 增加励磁绕组电感、励磁损耗和转子漏磁，并做热耦合 |
| EXP-008 绕组重构 | 串/并配置代理与切换连续性 | 建模接触器切换瞬态、环流和并联支路热分配 |
| EXP-009 多相相组 | 相组降额与失组可达性 | 增加谐波子空间解耦、中性点偏移电压矢量和每相热 RC |
| EXP-010 Pareto 选择 | 示意工况下的加权路由排序 | 用实测工况替换示意工况，并补充铁耗/机械损耗/逆变器损耗 |

## 5. 验收命令

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q
```

如果运行后生成实验产物差异，必须先确认差异来自模型/参数变化还是测试步长变化。

## 6. 不应误读的地方

- `passed_numeric_simulation` 表示已有可复现实验，不表示工程释放。
- `needs_next_numeric_model` 不是失败，而是下一阶段数值建模缺口。
- `passed_architecture_verification` 只表示工程目录/流程完整，不代表已有数值评分。
- `claude-docs` 中的快照是证据留痕，不是唯一事实源；活动事实源仍在 `models/`, `reports/`, `experiments/`, `sim/`, `tests/`。
