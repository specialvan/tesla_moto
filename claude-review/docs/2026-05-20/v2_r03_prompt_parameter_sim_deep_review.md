# V2 r03 图档提示词 × r02 参数/仿真一致性深度 Review

日期：2026-05-20  
范围：`engineering/v2/scheme-*/parameters/*`、`engineering/v2/scheme-*/prompts/*r03-production_drawing_pack.md`、`models/scheme_simulation_coverage.json`、`tests/test_scheme_*`  
结论：**FAIL（先不生图）**。当前 r03 prompt pack 已能全量 dry-run，但多方案的图档提示词明显超出现有 r02 仿真证据与测试合同，若直接生图容易把“工程证据计划图”误读成“已验证工程图”。

## 执行摘要

- 48 条 r03 prompt 已可由 `gpt-image-2` dry-run 展开；脚本可用，不是阻塞点。
- r02 仿真合同明确所有方案 `engineering_validated=false`、`production_drawing_ready=false`、`manufacturing_release_ready=false`。
- S01/S02/S04/S11 有 P0 LUT acceptance harness，但仍只覆盖 control LUT / demag / feasibility / synthetic LUT smoke 等代理链路。
- S03/S05/S06/S12 是 numeric proxy；S07/S08/S09/S10 是 research pool proxy / binding smoke。
- 高风险集中在 S05-S10/S12：prompt 中出现 CAD/FEA、硬件电流/电压/时序、recommendation gate 等强工程语义，但 r02 参数与测试只覆盖代理实验输出结构。

## 审查基准

本轮判断不以“prompt 能否生成好看的图”为准，而以是否满足以下三条为准：

1. 图中每个工程数字、硬件路径、状态机阈值是否能追溯到 r02 参数/仿真绑定或显式 evidence gap。
2. prompt 是否避免把 proxy/synthetic/estimate 画成 FEA、bench、HIL、ASIL 或 manufacturing release。
3. prompt 是否服务后续仿真闭环：能暴露下一步需要补的 schema/test/fixture，而不是只增强视觉可信度。

## 总体矩阵

| 方案 | r02 仿真成熟度 | r03 prompt 风险 | 主要漂移 | 处理优先级 |
|---|---|---:|---|---|
| S01 | parameterized linear numeric proxy | Medium | sensing/gate-disable 延迟未入仿真合同 | P1 |
| S02 | parameterized linear numeric proxy | Medium | NVM/CRC/CAN/SPI/XCP 仅是图档目标 | P1 |
| S03 | proxy model numeric proxy | Medium | THD/EMC/NVH 与 loss map 未由 scoped test 覆盖 | P1 |
| S04 | synthetic fixture / binding smoke | Medium | FEA-backed validation 标题过强，温度切片未入合同 | P0 |
| S05 | proxy model numeric proxy | High | FEA/stress/demag/iron loss/manufacturing risk 超前 | P0 |
| S06 | proxy model numeric proxy | High | PM fraction、torque ripple、stress、BOM risk 未入合同 | P0 |
| S07 | research pool binding smoke | High | 1000 A/50 us/100 J 脉冲硬件未验证 | P0 |
| S08 | research pool binding smoke | High | field converter、loss-of-field、thermal derate 未验证 | P0 |
| S09 | research pool binding smoke | High | 800 V/300 A switch matrix、切换暂态未验证 | P0 |
| S10 | research pool binding smoke | High | six-phase 130 A/phase、fault derate <2 ms 未验证 | P0 |
| S11 | parameterized linear numeric proxy | Medium | 三温度链路、开短路、gate-disable、ASIL gap 未测试 | P1 |
| S12 | proxy model numeric proxy | High | recommendation gate / maturity penalty 未被 evidence gate 阻断 | P0 |

## 分方案发现

### S01 Negative d-axis field weakening

- r02 覆盖：`V2-S01-PARAM-sim_binding-r02.json` 驱动 `sim.run_control_lut_generator.run`，验证 demag limit、feasibility、mode transition、demag metadata。
- prompt 对齐点：r03 明确 `engineering_validated = false`、demag estimate 非 bench validation、S11 safety link。
- 漂移：ADC 12-bit/100 kSPS、Vdc ±1%、temperature <1 ms、gate-disable <100 us 目前是图档/DVP目标，不是仿真可验字段。
- 建议：保留图档，但在每张图补 `latency/electrical specs are DVP targets, not simulated acceptance`；后续 schema 增加 `sensor_latency_target_us`、`gate_disable_target_us` evidence slot。

### S02 MTPA / FW / MTPV

- r02 覆盖：S02 专用测试已确认 60 A 是 r02 soft gate、30 A 是 r03 target；P0 harness 验证 LUT feasibility、mode transition、DVP mapping。
- prompt 对齐点：NVM/CRC、LUT version、XCP、S11 demag input都适合作为 r03 production drawing target。
- 漂移：`control_lut_schema.json` 没有 `lut_crc`、`lut_version`、DTC、CAN/SPI/XCP 字段；prompt 不应暗示这些已被仿真验证。
- 建议：图 1/2 增加 `interface target only; not exercised by r02 simulation`；后续为 CRC/version 增加 schema 与 smoke test。

### S03 SVPWM overmodulation

- r02 覆盖：EXP-005 k_mod sweep，验证 experiment ID、model_scope、k_mod sweep、scoring fields、CSV output。
- prompt 漂移：PWM harmonic model、inverter loss map、THD/EMC/NVH DVP、gate/PWM/EMC interface 没有 scoped test 覆盖。
- 成熟度风险：文件没有强制 `engineering_validated = false`、`evidence_gap`、`proxy only` 出现在所有图。
- 建议：在通用负面约束加 `All figures must visibly label engineering_validated=false, proxy/estimate only, evidence_gap`；图 4 标题保留 proxy chain，不使用 validation/gate pass 语义。

### S04 Nonlinear flux LUT

- r02 覆盖：`models/flux_lut_sample.json` synthetic 3x3 LUT，P0 harness 验证 `flux_lut_ref` 与 out-of-bounds smoke。
- prompt 对齐点：已正确标注 synthetic fixture、FEA gap、fallback active、`engineering_validated=false`。
- 漂移：图 4 标题 “Synthetic LUT to FEA-backed Validation” 过强；`>=30x30`、`>=5 temperature slices`、`residual_high 12%`、CRC fail 都还只是目标。
- 建议：标题改为 “Synthetic LUT to FEA-backed Evidence Plan”；将 `>=30x30` 与 temperature slices 标成 `r03 target / not linked dataset`。

### S05 Magnetic saturation co-design

- r02 覆盖：EXP-003 参数缩放，验证 `variant_count`、`top_candidates`、CSV output。
- 高风险漂移：prompt 要求 rotor barrier geometry、FEA LUT、stress FEA、iron loss、demag boundary、manufacturing risk，但 r02 没有真实几何/FEA/材料/应力合同。
- 生图风险：CAD/FEA-style 图可能被误读为已有 FEA candidate。
- 建议：把 “FEA-backed Candidate” 改为 “FEA evidence target”；所有图加 `geometry placeholder / no released CAD / no FEA-derived LUT`。

### S06 PMaSynRM high saliency low PM

- r02 覆盖：共享 EXP-003 参数缩放，近似 lower psi_f / higher saliency 变量。
- 高风险漂移：PM fraction、torque ripple、stress safety factor、demag margin、BOM risk 都未进入 r02 输出字段。
- 建议：prompt 中 CAD/FEA panel 必须标 `parameter-scaled proxy only`；新增下一步 schema：`pm_fraction`, `torque_ripple_proxy`, `stress_margin_placeholder`, `bom_risk_evidence_status`。

### S07 Variable magnetization memory motor

- r02 覆盖：EXP-002 虚拟 `psi_f` states，research pool binding smoke。
- 高风险漂移：1000 A peak、50 us pulse、100 J energy、interlock latency <1 ms 是硬件设计目标，不是当前仿真结果。
- 建议：所有图加 `research pool concept / pulse values are design targets`；不要把 magnetization pulse driver 画成 release-ready PCB。

### S08 Hybrid excitation

- r02 覆盖：EXP-007 `psi_eff = psi_pm + kf * if`，验证 row_count/CSV。
- 高风险漂移：field converter current range、loss-of-field <5 ms、thermal derate、field winding package 都缺电路/热/故障模型。
- 建议：图 1/3 中把 converter 和 loss-of-field 标成 `control target only`；后续补 field-winding inductance、exciter loss、thermal coupling schema。

### S09 Winding reconfiguration

- r02 覆盖：EXP-008 turns-scale 配置扫，验证 configs、transitions、recommended_config、row_count。
- 高风险漂移：800 V/300 A switch matrix、50-200 ms switching window、circulating current <5 A、arc suppression 都未被仿真验证。
- 建议：状态机可保留，但所有 HV switch matrix 图必须标 `static proxy is not switching validation` 与 `no arc/transient model`；后续补 switching transient fixture。

### S10 Multiphase phase group control

- r02 覆盖：EXP-009 fault case 下 phase current derating，验证 cases、case_count、worst_case。
- 高风险漂移：six-phase hardware、130 A/phase、fault derate <2 ms、xy harmonic observer 目前不是测试合同。
- 建议：图中把 six-phase inverter 标为 `architecture target`; fault derate `<2 ms` 标为 DVP target；后续补 harmonic subspace / thermal RC / transient tests。

### S11 Thermal demag safety

- r02 覆盖：EXP-004 Rs(T)、psi_f(T)、Vdc derating、简化 id_min(T)，P0 harness 覆盖 120 °C operating limit 与 demag metadata。
- prompt 对齐点：明确 ASIL/FM​​EDA evidence gap、`engineering_validated=false`。
- 漂移：pm/winding/oil 三温度阈值、sensor open/short <1 ms、gate-disable <100 us、fault latch 都未入当前测试。
- 建议：图 1/3 加 `timing thresholds are bench/HIL targets`; 后续为 sensor fault injection 与 gate-disable timing 建 schema/test。

### S12 Weighted efficiency Pareto selection

- r02 覆盖：EXP-010/011 drive-cycle、candidate、pareto_front、iron loss sweep proxy。
- 高风险漂移：prompt 中 “green engineering candidate gate” 与“工程决策图”容易被误读为推荐闭环完成。
- 建议：改成 `candidate-for-review gate`；加 `proxy ranking only / no engineering recommendation without reviewed PCB/CAD/BOM/DVP/S11 evidence`。

## 必修修改建议

### Prompt wording P0

1. S03/S05/S06/S07/S08/S09/S10/S12 的通用负面约束统一补：
   - `All images must visibly label engineering_validated = false`。
   - `proxy / estimate only`。
   - `evidence_gap`。
   - `concept illustration only, not production drawing or validation evidence`。
2. S04 图 4 标题由 `FEA-backed Validation` 改为 `FEA-backed Evidence Plan`。
3. S05/S06 中所有 `FEA-backed Candidate`、`FEA Flux LUT` 改为 `FEA evidence target` 或 `FEA placeholder`，直到真实 FEA dataset 链接。
4. S12 中 `green engineering candidate gate` 改为 `green candidate-for-review gate`。

### 仿真合同 P0/P1

| 方向 | 应补字段/测试 | 适用方案 |
|---|---|---|
| prompt-to-binding trace | 检查 r03 prompt 中硬件/阈值是否有 binding evidence 或 evidence_gap | 全部 |
| CRC/version schema | `lut_crc`, `lut_version`, DTC enums | S02 |
| synthetic LUT maturity | fixture_limits、temperature slice status、residual threshold | S04 |
| FEA placeholder status | geometry_source、fea_dataset_ref、stress_model_status | S05/S06 |
| pulse/converter/switch transient | energy/current/timing target 与仿真状态分离 | S07/S08/S09 |
| fault transient | derate latency、harmonic observer status、thermal RC evidence | S10 |
| safety timing | sensor fault injection、gate-disable latency、FMEDA status | S01/S11 |
| recommendation gate | evidence completeness blocks recommendation | S12 |

## 生图前 Gate

在真实调用图像端点前，建议至少满足：

1. P0 prompt wording 修改完成，避免生成带过度工程成熟度的 PNG。
2. `gpt-image-2 --prompt-pack-all --dry-run` 重新通过 48/48。
3. 新增一个轻量 prompt maturity test：扫描 12 个 r03 prompt pack，要求包含 `engineering_validated = false`、`evidence_gap` 或等价边界词。
4. 若只想低成本试跑，先选 S01/S02/S04/S11 中 1 个方案；不要先跑 S05-S10/S12。

## 结论

当前 r03 prompt pack 适合作为“工程图档意图草案”，不适合直接全量生图归档为生产图纸。下一步应先做 prompt wording 收敛与 prompt-to-binding trace 测试，再进入 smoke 或小范围 S01/S02/S04/S11 出图。
