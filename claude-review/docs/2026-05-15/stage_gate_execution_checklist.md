# 可控磁通项目阶段门执行清单与证据矩阵

日期：2026-05-15  
依据：

- `models/scheme_industry_stage_gate_process.json`
- `models/scheme_engineering_catalog.json`
- `models/scheme_simulation_coverage.json`
- `models/scheme_bom_eda_catalog.json`

目的：把当前阶段门定义转成可直接执行的检查清单，明确每一门需要什么证据、当前仓库已有多少、还缺什么。

---

## 1. 使用原则

阶段门不是文档装饰，而是每条方案能否升级的硬约束。

判断逻辑：

- **已有证据**：仓库中已有 JSON / CSV / README / pytest / schema；
- **缺失证据**：当前模型或工程包中没有可引用产物；
- **放行条件**：必须明确到文件级或报告级；
- **研究池策略**：证据不足时不强行推进到下一门。

---

## 2. G0 策略与 Item Definition

### 2.1 门定义

- 入口：方案已存在，业务目标和使用场景已说明。
- 退出：路线 owner、目标工况、go/no-go 假设明确。

### 2.2 当前已具备证据

- 方案目录：`models/scheme_engineering_catalog.json:1`
- 路线分类、目标、失败模式、交付物：同文件各 scheme 条目
- 研究方案总梳理：`claude-review/docs/2026-05-15/research_scheme_engineering_landing_matrix.md`

### 2.3 仍缺证据

- 路线 owner
- 目标车型/驱动工况
- 商业目标或约束优先级

### 2.4 放行建议

- 主线方案可通过 G0；
- 长周期研究项也可通过 G0，但必须明确“仅研究，不承诺工程化”。

---

## 3. G1 需求与安全概念

### 3.1 门定义

- 入口：G0 已通过，基线电机/逆变器约束可获得。
- 退出：需求可测量，安全限制优先于性能目标，验证方法已指定。

### 3.2 当前已具备证据

- 主线工况边界：`experiments/exp_001_linear_dq/summary.json:1`
- 温度 / 退磁 / 低母线保护边界：`experiments/exp_004_safety_boundaries/summary.json:1`
- 控制 LUT 契约中已有 operating limits / infeasibility 原因定义：`models/control_lut_schema.json:124`、`346`
- 阶段门总定义：`models/scheme_industry_stage_gate_process.json:18`

### 3.3 仍缺证据

- 明确的 requirement trace matrix
- 正式 safety concept 文档
- 故障注入 / 失效模式到验证方法的映射表

### 3.4 放行建议

- `negative_d_axis_field_weakening`、`mtpa_fw_mtpv_control`、`thermal_demag_safety_protection` 可进入 G1 收敛；
- 其余方案仍以研究需求草案为主。

---

## 4. G2 系统架构与 Trade Study

### 4.1 门定义

- 入口：需求基线存在，接口和约束已知。
- 退出：接口已分配，主要硬件变体已识别，风险项有 owner。

### 4.2 当前已具备证据

- 工程目录：`models/scheme_engineering_catalog.json:1`
- BOM / EDA 规划：`models/scheme_bom_eda_catalog.json:1`
- 方案 overlay 风险与下一步动作：`models/scheme_industry_stage_gate_process.json:68`
- 参数候选对比：`experiments/exp_003_param_sweep/summary.json:1`

### 4.3 仍缺证据

- 主干接口架构图
- 硬件 variant 选择逻辑
- 风险 owner / 关闭策略
- 候选电机 scorecard 模板

### 4.4 放行建议

- 主线控制方案已具备进入 G2 的基础；
- `magnetic_saturation_codesign`、`pmasynrm_high_saliency_low_pm` 适合在 G2 深化；
- Memory Motor / 绕组重构 / 多相方案在 G2 只保留概念架构，不进入硬件承诺。

---

## 5. G3 模型、仿真与控制

### 5.1 门定义

- 入口：架构已选，模型输入已版本化。
- 退出：仿真复现验收指标，不可行区被标记，模型局限被记录。

### 5.2 当前已具备证据

- 覆盖总账：`models/scheme_simulation_coverage.json:1`
- 线性 dq：`experiments/exp_001_linear_dq/summary.json:1`
- 变量磁链状态：`experiments/exp_002_variable_flux/summary.json:1`
- 参数家族：`experiments/exp_003_param_sweep/summary.json:1`
- 安全边界：`experiments/exp_004_safety_boundaries/summary.json:1`
- 过调制：`experiments/exp_005_modulation_factor/summary.json:1`
- 非线性 LUT：`experiments/exp_006_nonlinear_flux_lut/summary.json:1`
- 混合励磁：`experiments/exp_007_hybrid_excitation/summary.json:1`
- 绕组重构：`experiments/exp_008_winding_reconfiguration/summary.json:1`
- 多相相组：`experiments/exp_009_multiphase_phase_group/summary.json:1`
- 加权效率：`experiments/exp_010_weighted_efficiency_pareto/summary.json:1`
- 铁耗：`experiments/exp_011_iron_loss/summary.json:1`
- 控制 LUT schema：`models/control_lut_schema.json:1`
- 磁链 LUT schema：`models/flux_lut_schema.json:1`

### 5.3 仍缺证据

- 主线统一控制 LUT 输出已吸收 exp_004/006 边界
- FEA / 实测来源的 LUT 输入
- 更真实的铁耗、逆变器损耗、机械损耗
- G3 汇总验证报告

### 5.4 放行建议

- 当前仓库已经具备较强 G3 研究基础；
- 但真正通过 G3 的主线，只应优先认定为：
  - 弱磁
  - 连续控制
  - 非线性 LUT
  - 安全保护
- 其余路线虽然有数值实验，不等于可进入下游硬件门。

---

## 6. G4 BOM / EDA / 原理图 / DFMEA

### 6.1 门定义

- 入口：仿真门已通过，BOM 类别和 EDA 页面已定义。
- 退出：原理图评审通过，关键器件约束明确，DFMEA 行动项已分配。

### 6.2 当前已具备证据

- BOM / EDA 框架目录：`models/scheme_bom_eda_catalog.json:1`
- 各方案重点保护项和接口方向：同文件各条目
- 阶段门约束：`models/scheme_industry_stage_gate_process.json:40`

### 6.3 仍缺证据

- 原理图页级结构
- BOM draft
- DFMEA / FMEDA 实体文档
- DVP&R draft

### 6.4 放行建议

- 只有主线控制方案和安全保护方案值得优先推进到 G4 规划；
- 混合励磁、绕组重构、多相方案若无明显系统收益，不建议在当前阶段进入 G4。

---

## 7. G5 PCB Layout / Prototype / Bring-up

### 7.1 门定义

- 入口：原理图和 DFMEA 已过门。
- 退出：布局、电源地、隔离、故障路径验证通过，样机安全启动。

### 7.2 当前已具备证据

- 仅有 PCB integration notes 的目录级提示：`models/scheme_bom_eda_catalog.json:1`

### 7.3 仍缺证据

- layout constraint
- bring-up checklist
- prototype build package
- safety bring-up report

### 7.4 放行建议

- 当前仓库尚未准备好进入 G5；
- 需要等 G4 的真实硬件资产建立后再推进。

---

## 8. G6 Bench DV 与 Calibration

### 8.1 门定义

- 入口：样机 bring-up 完成，夹具就绪。
- 退出：DV 通过或偏差获批，标定可追溯，故障响应符合安全概念。

### 8.2 当前已具备证据

- 数值侧已有 calibration / LUT / 模型雏形，但无台架证据。

### 8.3 仍缺证据

- bench test report
- calibration release candidate
- DVP&R results
- fault injection evidence

### 8.4 放行建议

- 当前不放行；
- 只能把现有结果作为台架计划的输入，而不是替代台架证据。

---

## 9. G7 PV Release 与变更控制

### 9.1 门定义

- 入口：DV 通过，制造过程与供应链信息可用。
- 退出：PV/PPAP 证据完备，开放风险清零或已处置，变更控制生效。

### 9.2 当前已具备证据

- 无。

### 9.3 仍缺证据

- PV plan/results
- control plan
- PPAP evidence
- release notes
- change-control baseline

### 9.4 放行建议

- 当前阶段与 G7 仍有明显距离；
- 不应因数值实验较丰富而误判成熟度。

---

## 10. 按方案的阶段门优先级建议

### 10.1 近期主线

| 方案 | 当前建议门位 | 说明 |
|---|---|---|
| 负 d 轴弱磁 | G3 强化中，准备 G4 前置 | 需补可信 demag / 热边界 |
| MTPA/FW/MTPV 连续控制 | G3 主线 | 应成为统一控制出口 |
| 非线性磁链 LUT | G3 主线 | 需接入控制 LUT 与 FEA 数据 |
| 温度/退磁安全保护 | G3 主线，G4 前必绑 | 属于横切必做项 |

### 10.2 中期候选

| 方案 | 当前建议门位 | 说明 |
|---|---|---|
| 过调制 / 电压利用率提升 | G3 候选 | 需 THD / NVH / 损耗实证 |
| 磁路饱和协同设计 | G2-G3 候选 | 需 FEA→LUT→控制回灌 |
| PMaSynRM / 高凸极低永磁占比 | G2-G3 候选 | 需 torque ripple / stress / FEA 证据 |

### 10.3 研究池

| 方案 | 当前建议门位 | 说明 |
|---|---|---|
| Memory Motor | G0-G3 研究 | 先证状态可控可观测 |
| 混合励磁 | G2-G3 研究 | 先证明总损耗收益覆盖新增复杂度 |
| 绕组重构 | G2-G3 研究 | 先证明切换瞬态与收益成立 |
| 多相 / 相组控制 | G2-G3 研究 | 先证明容错或热优势真实存在 |

---

## 11. 当前最关键的阶段门动作

### P0

1. 形成主线 G3 汇总证据包。  
2. 统一 control LUT 输出与模型来源字段。  
3. 把安全边界与非线性磁链并入统一控制主干。

### P1

1. 建立 FEA / 候选电机导入桥。  
2. 建立 scorecard 与 candidate ID。  
3. 把 Pareto 评估升级成正式晋级入口。

### P2

1. 针对重硬件方案保留研究池说明。  
2. 防止研究型实验被误读为可直接过 G4/G5 的工程证据。

---

## 12. 最终判断

当前仓库最大的价值，不是已经走到哪一个硬件阶段，而是已经把 **G3 研究证据的地基** 搭出来了。

真正的推进重点应是：

- 先让主线方案在 G3 层收敛成统一证据链；
- 再决定哪些方案有资格进入 G4；
- 对其余研究路线明确保留但不承诺工程化。

这样才能避免路线过多、资源分散、成熟度误判。