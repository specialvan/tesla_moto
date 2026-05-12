# 可控磁通量方案成熟业界设计推进流程

## 0. 流程基准

每种方案都按汽车电子常见的 **V 模型** 推进，用 **APQP** 的阶段策划思路组织设计质量门，用 **功能安全** 生命周期约束安全边界，用 **ASPICE** 式需求-设计-测试追溯管理证据链，用 **DFMEA / DVP&R / PPAP** 把设计、验证和发布资料闭环。

本文不声明项目已经满足任何认证标准；它定义的是研发推进纪律和证据结构。具体认证、ASIL、PPAP 等级和客户格式，需要在项目边界冻结后再定。

## 1. G0-G7 阶段门

| Gate | 名称 | 核心产物 | 退出标准 |
|---|---|---|---|
| G0 | 策略和 Item Definition | item definition、业务目标、风险等级、干净室边界 | 方案 owner 和 go/no-go 假设明确 |
| G1 | 需求和功能安全概念 | 系统需求、功能安全概念、初版 HARA/FMEA、追溯矩阵 | 每条需求可测、保护优先级明确 |
| G2 | 系统架构和 Trade Study | 系统架构、BOM 架构、EDA block、方案 scorecard | 接口分配、硬件变体和风险 owner 明确 |
| G3 | 模型仿真和控制策略 | 仿真模型、控制策略、校准草案、模型验证报告 | 指标可复现，不可行区已标记 |
| G4 | BOM/EDA 原理图和 DFMEA | 原理图、BOM draft、DFMEA、DVP&R draft | 原理图审查通过，DFMEA action 分配 |
| G5 | PCB、样机和 Bring-up | PCB layout、样机包、bring-up checklist、安全检查表 | 样机安全启动，gate-disable/fault path 验证 |
| G6 | 台架 DV 和标定 | bench report、DVP&R 结果、标定候选、故障注入证据 | DV 通过或偏差批准，故障响应符合安全概念 |
| G7 | PV、发布和变更控制 | PV/PPAP evidence pack、控制计划、release notes、变更基线 | 证据包完整，风险关闭或批准，变更控制生效 |

## 2. 方案级推进覆盖

| 方案 ID | 主风险 | BOM/EDA 重点 | 必须证据 |
|---|---|---|---|
| `negative_d_axis_field_weakening` | 负 id 导致退磁或低压高速越压 | 电流采样、Vdc 采样、温度输入、gate-disable | `id_min(T)`、低 Vdc 扫描、弱磁 DVP&R |
| `mtpa_fw_mtpv_control` | LUT 不连续或不可行区插值导致转矩台阶 | MCU/NVM、同步 ADC、校准 CRC | 控制 LUT、连续性报告、不可行区图 |
| `svpwm_overmodulation_voltage_utilization` | 过调制带来电流畸变和 NVH | 栅极驱动、DC-Link、采样带宽、EMI | `k_mod` 扫描、THD/NVH 评估、调制 DVP&R |
| `nonlinear_flux_lut` | LUT 单位或边界错误导致控制误判 | NVM/外部 Flash、温度采样、标定接口 | LUT schema、越界测试、FEA 导入验证 |
| `magnetic_saturation_codesign` | FEA 单指标优化但强度/退磁/损耗失败 | 候选 ID、传感线束、日志接口 | 候选 scorecard、FEA LUT、强度/退磁审查 |
| `pmasynrm_high_saliency_low_pm` | 低 Ke 牺牲低速转矩或转矩脉动过大 | 高精度位置、ripple 测量、候选校准 | PM 比例 trade study、ripple/NVH 筛选 |
| `variable_magnetization_memory_motor` | 磁链状态未知或磁化脉冲过应力 | 脉冲 interlock、脉冲电流采样、状态观测 | 多档 `ψf` 模型、脉冲能量、状态误判故障表 |
| `hybrid_excitation` | 励磁损耗和热抵消收益 | 励磁变换器、励磁电流环、失励检测 | `id/iq/if` 优化、励磁热模型、失励故障分析 |
| `winding_reconfiguration` | 高电流切换瞬态、非法配置、绝缘风险 | 切换矩阵、配置反馈、硬件互锁 | 多配置模型、切换点分析、switch matrix DFMEA |
| `multiphase_phase_group_control` | 相组复杂度超过容错/热收益 | 多通道 gate drive、多相采样、故障域隔离 | 缺相能力、PWM/ADC 资源预算、phase-loss DVP&R |
| `thermal_demag_safety_protection` | 优化覆盖安全限制 | safety supervisor、watchdog、fault latch、gate-disable | 功能安全概念、热/退磁 limit、故障注入 |
| `weighted_efficiency_pareto_selection` | 单指标错误晋级方案 | logging、route ID、calibration CRC | drive-cycle 权重、Pareto 报告、变更控制 |

## 3. 每个 Gate 的设计动作

### G0 策略和 Item Definition

- 写清楚方案要解决的物理瓶颈：电压、转矩、热、退磁、Ke、效率或容错。
- 标出方案成熟度：主线、增强线、预研线、横向安全层。
- 明确不做什么：例如 V1 不做高压实机，不推断闭源厂商方案。

### G1 需求和功能安全概念

- 每个方案必须有需求编号、验收指标和验证方法。
- 功能安全优先级固定为：硬件保护 > 退磁保护 > 电压/电流限制 > 热限制 > 转矩跟随 > 效率优化。
- 高压相关设计必须预留 gate-disable、故障锁存和诊断。

### G2 系统架构和 Trade Study

- 把方案映射到驱动拓扑、BOM 模块、EDA 原理图页、协议接口。
- 形成 trade study：收益、成本、复杂度、风险、验证周期。
- 不允许没有 scorecard 的方案直接进入原理图设计。

### G3 模型仿真和控制策略

- 先跑可复现脚本，再输出报告。
- 每个仿真结果都要标明模型边界和数据路径。
- 不可行区必须显式标记，禁止插值造点。

### G4 BOM/EDA 原理图和 DFMEA

- BOM 先按器件类别和约束定义，不急着锁厂商料号。
- EDA 原理图按系统页分层：高压输入、DC-Link、功率桥、驱动、采样、MCU、安全、通信、扩展。
- 每个方案必须有 DFMEA 行项目和 DVP&R 验证项。

### G5 PCB、样机和 Bring-up

- PCB review 必须覆盖功率回路、隔离、爬电、采样回路、EMC、热路径。
- Bring-up 必须从低压限流开始。
- gate-disable、过流、欠压、过压、温度故障先验证，再做性能测试。

### G6 台架 DV 和标定

- 台架先验证安全，再验证性能。
- DVP&R 结果和标定版本必须绑定。
- 故障注入必须覆盖低 Vdc、高温、传感器错误、通信丢失和保护触发。

### G7 PV、发布和变更控制

- 进入样机/量产导入前，必须形成 PV/PPAP evidence pack。
- 所有 BOM、EDA、固件、标定、测试结果进入版本基线。
- 变更必须走影响分析：需求、功能安全、DFMEA、DVP&R、BOM、PCB、软件、标定。

## 4. 方案推进顺序

第一批进入 G1-G3：

- `negative_d_axis_field_weakening`
- `mtpa_fw_mtpv_control`
- `thermal_demag_safety_protection`
- `weighted_efficiency_pareto_selection`

第二批进入 G1-G2，同时准备 G3：

- `nonlinear_flux_lut`
- `svpwm_overmodulation_voltage_utilization`
- `pmasynrm_high_saliency_low_pm`
- `magnetic_saturation_codesign`

第三批保持 G0-G2 预研：

- `variable_magnetization_memory_motor`
- `hybrid_excitation`
- `winding_reconfiguration`
- `multiphase_phase_group_control`

## 5. 当前马上要做的落地动作

1. 为第一批方案建立需求追溯矩阵。
2. 将 `models/scheme_bom_eda_catalog.json` 的 BOM 类别转成 EDA 原理图页任务。
3. 为每个方案建立 DFMEA 初版行项目。
4. 将 V1 仿真结果接入 DVP&R 初版。
5. 形成 `reports/v2_scheme_scorecard.md`，作为 G2 trade study 的输入。

## 6. 参考流程来源

- ISO 26262 road vehicles functional safety overview: https://www.iso.org/standard/68383.html
- Automotive SPICE process assessment model ecosystem: https://www.automotivespice.com/
- AIAG APQP/PPAP quality planning and production approval references: https://www.aiag.org/quality/automotive-core-tools

这些来源用于流程结构参考；本项目当前产物仍是研发规划和仿真阶段资料，不等同于认证或客户提交资料。
