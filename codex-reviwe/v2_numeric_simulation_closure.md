# V2 数值仿真闭环与工程落地推进记录

## 1. 当前闭环结论

本轮把此前仍停留在“架构验证/下一步建模”的方案补成可运行数值实验，并更新 `models/scheme_simulation_coverage.json`。当前 12 类方案均已挂接到可复现仿真、测试和结果文件。

注意：这些实验仍是 clean-room / v0 参数化模型，`engineering_validated=false`。它们用于方案推进、接口打通、EDA/BOM/驱动设计前置筛选，不等价于 FEA、台架或车规设计释放。

## 2. 新增实验矩阵

| 实验 | 对应方案 | 新增能力 | 结果文件 |
|---|---|---|---|
| EXP-005 | `svpwm_overmodulation_voltage_utilization` | 显式 `k_mod` 电压利用系数、谐波电流/转矩脉动/逆变损耗惩罚 | `experiments/exp_005_modulation_factor/summary.json` |
| EXP-006 | `nonlinear_flux_lut` | `lambda_d/lambda_q` LUT 边界检查、双线性插值、非线性 dq 转矩计算 | `experiments/exp_006_nonlinear_flux_lut/summary.json` |
| EXP-007 | `hybrid_excitation` | `psi_eff = psi_pm + kf * if`、励磁铜耗、目标速度边界对比 | `experiments/exp_007_hybrid_excitation/summary.json` |
| EXP-008 | `winding_reconfiguration` | 串联/基准/并联绕组参数集、Ke/Kt 代理、切换连续性检查 | `experiments/exp_008_winding_reconfiguration/summary.json` |
| EXP-009 | `multiphase_phase_group_control` | 健康/失组/不均流相组降额、可用电流和目标扭矩可达性 | `experiments/exp_009_multiphase_phase_group/summary.json` |
| EXP-010 | `weighted_efficiency_pareto_selection` | 速度/损耗/风险权重评分，形成可追溯 Pareto 排序 | `experiments/exp_010_weighted_efficiency_pareto/summary.json` |

## 3. 面向成熟业界流程的工程门槛

### 3.1 驱动与控制

- SVPWM/过调制：下一阶段必须从参数化惩罚升级为 PWM 波形重构、死区、电流纹波、EMI 和器件损耗图。
- 混合励磁：下一阶段必须加入励磁绕组 L/R 动态、励磁电源/整流器损耗、励磁电流上电斜率和失励保护。
- 绕组重构：下一阶段必须补充切换瞬态、接触器/固态开关损耗、绝缘距离、互锁和循环电流保护。
- 多相相组：下一阶段必须加入开相电压矢量、谐波子空间控制、中性点漂移和逐相热模型。

### 3.2 BOM / EDA

- 现有 `reports/scheme_bom_eda_integration_design.md` 和 `models/scheme_bom_eda_catalog.json` 已给出每种方案的 BOM 分组、EDA 模块、接口和保护边界。
- V2 后续需要把 EXP-005 至 EXP-010 的数值边界回填到 EDA 约束：采样带宽、驱动保护阈值、隔离电源余量、连接器 pin 定义、预充/上电互锁。

### 3.3 上电时序与协议

- 现有 `reports/scheme_driver_power_protocol_diagrams.md` 已覆盖每种方案的驱动设计图、上电时序图和协议链路图。
- 下一阶段要把仿真输出变成协议字段：`k_mod_limit`、`id_min_allowed`、`flux_state`、`field_current_cmd`、`winding_config_state`、`phase_group_health`、`pareto_score_version`。

## 4. 当前数值发现

- EXP-005：测试粒度下 `k_mod=1.04` 的综合评分最高，目标扭矩可达速度提升到 7000 rpm，但引入谐波电流和逆变损耗惩罚。
- EXP-006：合成 LUT 最优样例点出现在 `id=-200 A, iq=200 A`，非线性转矩为 108 Nm；该结论只证明接口和公式闭环。
- EXP-007：当前 v0 励磁参数下最佳综合点仍为 `if=0 A`，说明励磁方案需要更真实的 kf/损耗/热边界后再判断收益。
- EXP-008：当前参数化绕组族中基准配置目标速度最高；并联高速配置未在现有参数下证明收益，需要真实绕组 CAD/FEA 参数。
- EXP-009：一组失效后 100 Nm 目标不可达，说明多相方案的主要价值更偏容错/跛行，而不是无降额保持峰值性能。
- EXP-010：v0 权重下过调制方案排名第一；该排名依赖当前速度权重和风险惩罚，后续要替换为工况能耗权重。

## 5. 后续推进顺序

1. 把 EXP-005 到 EXP-010 的参数化模型升级为 FEA/器件/台架来源数据。
2. 生成控制 LUT 和协议字段定义，避免仿真结果停留在报告层。
3. 把 BOM/EDA 目录转成原理图片段：电源、采样、隔离、驱动、保护、通信分别出 net-level 约束。
4. 建立 stage-gate 审查表：需求冻结、仿真冻结、原理图冻结、PCB 约束冻结、HIL、台架、热/EMC、设计释放。
