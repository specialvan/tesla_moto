# 数值仿真追踪矩阵

## 1. 总览

当前 `codex-review-line` 分支的 `models/scheme_simulation_coverage.json` 状态为：

| 状态 | 数量 |
|---|---:|
| `passed_numeric_simulation` | 6 |
| `needs_next_numeric_model` | 5 |
| `passed_architecture_verification` | 1 |

本矩阵用于把方案、仿真、测试和工程下一步串起来，避免只保留实验文件而丢失方案上下文。

## 2. 方案到实验映射

| 方案 ID | 状态 | 当前证据 | 主要测试 | 下一步 |
|---|---|---|---|---|
| `negative_d_axis_field_weakening` | `passed_numeric_simulation` | EXP-001 | `tests/test_dq_model.py`, `tests/test_param_sweep.py` | 增加温度相关 `id_min(T)` |
| `mtpa_fw_mtpv_control` | `passed_numeric_simulation` | EXP-001 | `tests/test_dq_model.py` | 统一搜索接口并生成控制 LUT |
| `svpwm_overmodulation_voltage_utilization` | `needs_next_numeric_model` | EXP-003 Vdc 缩放代理 | `tests/test_param_sweep.py` | 增加显式 `k_mod`、谐波和损耗列 |
| `nonlinear_flux_lut` | `needs_next_numeric_model` | 工程文档和 BOM/EDA | `tests/test_scheme_catalog.py` | 增加 LUT schema、插值和非线性转矩测试 |
| `magnetic_saturation_codesign` | `passed_numeric_simulation` | EXP-003 | `tests/test_param_sweep.py` | 用 FEA `lambda_d/lambda_q` 替换缩放代理 |
| `pmasynrm_high_saliency_low_pm` | `passed_numeric_simulation` | EXP-003 | `tests/test_param_sweep.py` | 增加 PM fraction 和转矩脉动筛选 |
| `variable_magnetization_memory_motor` | `passed_numeric_simulation` | EXP-002 | `tests/test_variable_flux.py` | 增加状态转换能量和未知状态降额 |
| `hybrid_excitation` | `needs_next_numeric_model` | BOM/EDA 架构 | `tests/test_scheme_catalog.py` | 增加等效励磁电流和励磁损耗模型 |
| `winding_reconfiguration` | `needs_next_numeric_model` | 驱动/协议/BOM 架构 | `tests/test_scheme_catalog.py` | 增加多绕组配置参数集和切换连续性 |
| `multiphase_phase_group_control` | `needs_next_numeric_model` | 驱动/协议/BOM 架构 | `tests/test_scheme_catalog.py` | 增加相组降额和失组工况 |
| `thermal_demag_safety_protection` | `passed_numeric_simulation` | EXP-004 | `tests/test_safety_limits.py`, `tests/test_safety_boundary_experiment.py` | 用 FEA 或磁钢数据替换简化退磁线 |
| `weighted_efficiency_pareto_selection` | `passed_architecture_verification` | 工程目录和 stage-gate | `tests/test_scheme_industry_process.py` | 增加工况权重和可追溯评分 |

## 3. 已落地实验

| 实验 | 模型范围 | 结果路径 |
|---|---|---|
| EXP-001 | `quasi_steady_linear_dq_grid_search` | `experiments/exp_001_linear_dq/summary.json` |
| EXP-002 | `quasi_steady_linear_dq_virtual_psi_f_scaling` | `experiments/exp_002_variable_flux/summary.json` |
| EXP-003 | `quasi_steady_linear_dq_scaled_parameter_family` | `experiments/exp_003_param_sweep/summary.json` |
| EXP-004 | `temperature_corrected_linear_dq_with_simplified_demag_limit` | `experiments/exp_004_safety_boundaries/summary.json` |

## 4. 待补实验包

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

运行后如果 `experiments/exp_004_safety_boundaries/safety_boundary_results.csv` 因测试步长发生差异，需要判断是否为预期生成物变化后再提交。

## 6. 不应误读的地方

- `passed_numeric_simulation` 表示已有可复现实验，不表示工程释放。
- `needs_next_numeric_model` 不是失败，而是下一阶段数值建模缺口。
- `passed_architecture_verification` 只表示工程目录/流程完整，不代表已有数值评分。
- `codex-docs` 中的快照是证据留痕，不是唯一事实源；活动事实源仍在 `models/`, `reports/`, `experiments/`, `sim/`, `tests/`。
