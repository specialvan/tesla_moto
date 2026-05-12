# 数值仿真追踪矩阵

## 1. 总览

当前 `codex-review-line` 分支的 `models/scheme_simulation_coverage.json` 状态为：

| 状态 | 数量 |
|---|---:|
| `passed_numeric_simulation` | 12 |

本矩阵用于把方案、仿真、测试和工程下一步串起来，避免只保留实验文件而丢失方案上下文。

## 2. 方案到实验映射

| 方案 ID | 状态 | 当前证据 | 主要测试 | 下一步 |
|---|---|---|---|---|
| `negative_d_axis_field_weakening` | `passed_numeric_simulation` | EXP-001 | `tests/test_dq_model.py`, `tests/test_param_sweep.py` | 增加温度相关 `id_min(T)` |
| `mtpa_fw_mtpv_control` | `passed_numeric_simulation` | EXP-001 | `tests/test_control_search.py`, `tests/test_dq_model.py` | 统一搜索接口并生成控制 LUT |
| `svpwm_overmodulation_voltage_utilization` | `passed_numeric_simulation` | EXP-005 | `tests/test_modulation_sweep.py` | 用 PWM 波形、电流纹波、EMI、器件损耗图替换参数惩罚 |
| `nonlinear_flux_lut` | `passed_numeric_simulation` | EXP-006 | `tests/test_nonlinear_flux_lut.py` | 用 FEA / dyno `lambda_d/lambda_q` 数据替换合成 LUT |
| `magnetic_saturation_codesign` | `passed_numeric_simulation` | EXP-003 | `tests/test_param_sweep.py` | 用 FEA `lambda_d/lambda_q` 替换缩放代理 |
| `pmasynrm_high_saliency_low_pm` | `passed_numeric_simulation` | EXP-003 | `tests/test_param_sweep.py` | 增加 PM fraction 和转矩脉动筛选 |
| `variable_magnetization_memory_motor` | `passed_numeric_simulation` | EXP-002 | `tests/test_variable_flux.py` | 增加状态转换能量和未知状态降额 |
| `hybrid_excitation` | `passed_numeric_simulation` | EXP-007 | `tests/test_hybrid_excitation.py` | 增加励磁 L/R 动态、励磁电源损耗和热耦合 |
| `winding_reconfiguration` | `passed_numeric_simulation` | EXP-008 | `tests/test_winding_reconfiguration.py` | 增加切换瞬态、绝缘、循环电流和开关损耗 |
| `multiphase_phase_group_control` | `passed_numeric_simulation` | EXP-009 | `tests/test_multiphase_phase_group.py` | 增加谐波子空间、开相电压矢量和逐相热模型 |
| `thermal_demag_safety_protection` | `passed_numeric_simulation` | EXP-004 | `tests/test_safety_limits.py`, `tests/test_safety_boundary_experiment.py` | 用 FEA 或磁钢数据替换简化退磁线 |
| `weighted_efficiency_pareto_selection` | `passed_numeric_simulation` | EXP-010 | `tests/test_weighted_efficiency_pareto.py` | 用工况权重、成本、质量和安全风险替换 v0 权重 |

## 3. 已落地实验

| 实验 | 模型范围 | 结果路径 |
|---|---|---|
| EXP-001 | `quasi_steady_linear_dq_grid_search` | `experiments/exp_001_linear_dq/summary.json` |
| EXP-002 | `quasi_steady_linear_dq_virtual_psi_f_scaling` | `experiments/exp_002_variable_flux/summary.json` |
| EXP-003 | `quasi_steady_linear_dq_scaled_parameter_family` | `experiments/exp_003_param_sweep/summary.json` |
| EXP-004 | `temperature_corrected_linear_dq_with_simplified_demag_limit` | `experiments/exp_004_safety_boundaries/summary.json` |
| EXP-005 | `linear_dq_with_explicit_voltage_utilization_axis` | `experiments/exp_005_modulation_factor/summary.json` |
| EXP-006 | `synthetic_lambda_d_lambda_q_lut_interpolation` | `experiments/exp_006_nonlinear_flux_lut/summary.json` |
| EXP-007 | `linear_dq_with_equivalent_field_excitation` | `experiments/exp_007_hybrid_excitation/summary.json` |
| EXP-008 | `linear_dq_multi_winding_configuration_sweep` | `experiments/exp_008_winding_reconfiguration/summary.json` |
| EXP-009 | `linear_dq_with_phase_group_current_derating` | `experiments/exp_009_multiphase_phase_group/summary.json` |
| EXP-010 | `traceable_weighted_scheme_selection` | `experiments/exp_010_weighted_efficiency_pareto/summary.json` |

## 4. 模型成熟度缺口

| 实验 | 当前已证明 | 下一阶段必须补齐 |
|---|---|---|
| EXP-005 | `k_mod` 轴和参数化谐波/损耗惩罚 | PWM 波形、电流纹波、EMI、器件损耗图 |
| EXP-006 | LUT schema、边界、插值、非线性转矩 | FEA / dyno `lambda_d/lambda_q` 数据 |
| EXP-007 | 等效励磁电流、磁链变化、励磁铜耗 | 励磁绕组 L/R、励磁电源、热耦合 |
| EXP-008 | 多配置参数集、Ke/Kt/R/L 代理、切换指标 | 开关瞬态、绝缘、循环电流、接触器/固态开关损耗 |
| EXP-009 | 相组健康/失效/不均流降额 | 开相电压矢量、谐波子空间、中性点漂移、逐相热 |
| EXP-010 | 速度/损耗/风险 v0 权重评分 | 驱动循环能耗、成本、质量、功能安全风险 |

## 5. 验收命令

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q
```

当前 Codex 分支最新验证记录：`55 passed`。

## 6. 不应误读的地方

- `passed_numeric_simulation` 表示已有可复现实验，不表示工程释放。
- EXP-005 到 EXP-010 是 v0 参数化模型，不是 FEA/台架/EDA 释放。
- `codex-docs` 中的快照是证据留痕，不是唯一事实源；活动事实源仍在 `models/`, `reports/`, `experiments/`, `sim/`, `tests/`。
