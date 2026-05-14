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
| `mtpa_fw_mtpv_control` | `passed_numeric_simulation` | EXP-001 | `tests/test_control_search.py`, `tests/test_dq_model.py` | 生成控制 LUT 并检查模式切换连续性 |
| `svpwm_overmodulation_voltage_utilization` | `passed_numeric_simulation` | EXP-005 | `tests/test_modulation.py`, `tests/test_modulation_factor_experiment.py` | 用实测逆变器损耗图和 PWM 重建 THD 替换参数惩罚 |
| `nonlinear_flux_lut` | `passed_numeric_simulation` | EXP-006 synthetic LUT | `tests/test_nonlinear_flux_lut.py`, `tests/test_scheme_catalog.py` | 用 FEA/测量 `lambda_d/lambda_q` 替换 synthetic LUT，并接入控制搜索 |
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
| EXP-006 | `synthetic_lambda_d_lambda_q_lut_interpolation` | `experiments/exp_006_nonlinear_flux_lut/summary.json` |

## 4. 下一批最小实验包

| 目标实验 | 对应方案 | 最小验收 |
|---|---|---|
| EXP-005 | SVPWM 过调制 | `k_mod` 轴、谐波电流、转矩脉动、逆变损耗惩罚 |
| EXP-006 | 非线性磁链 LUT | `lambda_d/lambda_q` 样例、边界检查、插值、非线性转矩 |
| EXP-007 | 混合励磁 | `psi_eff = psi_pm + kf * if`、励磁铜耗、目标速度边界 |
| EXP-008 | 绕组重构 | 串/并/基准配置、Ke/Kt/R/L 代理、切换连续性 |
| EXP-009 | 多相相组 | 健康/失组/不均流、可用电流降额、目标可达性 |
| EXP-010 | Pareto 选择 | 速度/损耗/风险权重、候选排序、来源追踪 |

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
