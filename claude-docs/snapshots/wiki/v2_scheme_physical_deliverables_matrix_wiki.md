# V2 分方案物理工程交付物矩阵 Wiki

日期：2026-05-15  
来源：`claude-review/docs/2026-05-15/v2_scheme_physical_deliverables_matrix.md`

---

## 1. 页面定位

本 Wiki 是 V2 分方案物理工程交付物矩阵的知识库索引版，用于快速确认每条方案是否具备可见的 PCB、3D/CAD、控制器设计、BOM/EDA 和 gate evidence。

---

## 2. 为什么 V2 不能只停留在方案描述

V2 每个方案若要从研究项进入工程落地，必须能回答：

1. PCB / EDA 页级设计在哪里；
2. 3D / CAD / 封装与冷却边界在哪里；
3. 控制器状态机、故障路径和标定图在哪里；
4. BOM、制造包、线束和供应链字段在哪里；
5. DVP&R、DFMEA、HIL/台架证据在哪里。

没有这些图纸和交付物，数值仿真、参数扫描和 playbook 文字不得被写成工程验证结论。

---

## 3. 12 个方案图纸交付状态总览

| ID | 方案 | PCB/EDA | 3D/CAD | 控制器图 | BOM/MFG | DVP&R/DFMEA | 当前判断 |
|---|---|---|---|---|---|---|---|
| S01 | 负 d 轴弱磁 | stub | missing | draft | missing | missing | 先补传感/故障页和弱磁状态机 |
| S02 | MTPA/FW/MTPV | stub | missing | draft | missing | missing | 先补 LUT 模式切换和控制器接口 |
| S03 | SVPWM/过调制 | missing | missing | stub | missing | missing | 需补逆变器功率级和 THD/EMC/NVH 图纸 |
| S04 | 非线性磁链 LUT | stub | missing | draft | missing | missing | 需补 FEA 几何源和 LUT 插值图 |
| S05 | 磁路饱和协同 | missing | missing | stub | missing | missing | 需补 barrier/bridge CAD 和 FEA scorecard |
| S06 | PMaSynRM | missing | missing | stub | missing | missing | 需补转子/定子 CAD、PM fraction 和风险 BOM |
| S07 | Memory Motor | missing | missing | stub | missing | missing | 需补磁化脉冲驱动和磁状态机 |
| S08 | 混合励磁 | missing | missing | stub | missing | missing | 需补励磁 DC/DC、field winding CAD 和三变量控制图 |
| S09 | 绕组重构 | missing | missing | stub | missing | missing | 需补开关矩阵、互锁、arc 和非法状态图 |
| S10 | 多相相组 | missing | missing | stub | missing | missing | 需补多相逆变器、相组封装和 fault allocator |
| S11 | 温度/退磁/安全 | stub | missing | draft | missing | missing | 先补 safety fault latch 和热传感 CAD |
| S12 | Pareto 决策 | stub | stub | draft | missing | missing | 需绑定候选图纸/BOM 版本，防止空泛 ranking |

---

## 4. 四类硬证据

### 4.1 PCB / EDA

- 原理图、Layout、stackup、ERC/DRC；
- current / voltage / temperature sensing；
- gate-disable、fault latch、隔离、连接器；
- Gerber、ODB++、Pick-place、IPC 图。

### 4.2 3D / CAD

- 电机几何、转子/定子、barrier/bridge、壳体；
- 冷却油路、母排、接插件、线束出口；
- 控制器壳体、功率模块、传感器安装；
- STEP / native CAD / Motor-CAD / Maxwell 几何源。

### 4.3 控制器设计图

- MTPA/FW/MTPV、过调制、弱磁、derating 状态机；
- fault path、unknown state fallback、gate-disable 映射；
- LUT 插值、模式切换、标定 map；
- HIL/bench 可执行的输入输出定义。

### 4.4 BOM / DVP&R / DFMEA

- 关键器件 BOM、供应商、额定值、温漂、诊断覆盖；
- DFMEA / FMEDA 初稿；
- DVP&R 测试项目、阈值和 pass/fail 规则；
- PV/PPAP 前的版本冻结和变更控制。

---

## 5. Gate 验收规则

| Gate | 最低要求 | 禁止通过条件 |
|---|---|---|
| G0-G1 | 方案边界、风险、图纸目录和命名规则 | 没有图纸目录 |
| G2 | PCB/CAD/CTRL 三类至少 stub，BOM 初表 | 只有仿真或文字描述 |
| G3 | FEA/CAD/控制器图进入 draft | 参数缩放未回灌物理约束 |
| G4 | PCB 原理图、BOM/EDA、控制器状态机评审 | 没有 ERC/DRC、BOM 或 fault path |
| G5 | 样机制造包、HIL/bench、DVP&R、DFMEA | 无台架或故障注入计划 |
| G6-G7 | released 制造包、DVP&R 执行、PV/PPAP | numeric simulation 替代工程验证 |

---

## 6. 当前缺口与下一步

近期最小推进顺序：

1. **P0 主线**：补 S01/S02/S04/S11 的控制器状态机、传感/故障 PCB 页和热/退磁 CAD 安装图。
2. **P1 候选**：补 S03/S05/S06/S12 的逆变器、FEA/CAD、BOM scorecard 和系统损耗图纸索引。
3. **P2 研究池**：补 S07/S08/S09/S10 的关键硬件拓扑、互锁、故障路径和停止条件图。

---

## 7. 证据链入口

- 完整源文档：`claude-review/docs/2026-05-15/v2_scheme_physical_deliverables_matrix.md`
- HTML 阅读版：`claude-review/docs/2026-05-15/v2_scheme_physical_deliverables_matrix.html`
- Wiki 快照：`claude-docs/snapshots/wiki/v2_scheme_physical_deliverables_matrix_wiki.md`
- HTML 快照：`claude-docs/snapshots/html/v2_scheme_physical_deliverables_matrix.html`

---

## 8. 最终判断

V2 后续不能再只问“方案怎么推进”，而要问：

> PCB 在哪里、3D/CAD 在哪里、控制器图在哪里、BOM/EDA 在哪里、DVP&R/DFMEA 如何验证。
