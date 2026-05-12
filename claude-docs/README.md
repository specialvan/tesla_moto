# Claude 可控磁通量电机知识库

## 1. 目录定位

`claude-docs` 是 `claude-mainline` 分支的工程知识库与交接包，负责沉淀 Claude 主线推演中的：

- 开发上下文 handoff；
- wiki / HTML 知识库冻结快照；
- EXP-001 到 EXP-004 的仿真实验证据；
- 工程路线、阶段门、报告和覆盖目录的证据索引；
- 后续 FEA、非线性 LUT、台架验证前的技术边界。

本目录是证据入口和交接索引，不替代正式仿真代码、EDA 工程、FEA 结果或台架验证报告。

## 2. 快速入口

| 文件 | 用途 |
|---|---|
| `handoff_context.md` | 给下一位 agent / 工程师的上下文交接 |
| `evidence_manifest.md` | 关键证据文件、来源和用途 |
| `simulation_traceability.md` | 12 类方案到当前仿真/待建模状态的追踪矩阵 |
| `wiki_html_evidence.md` | wiki 与 HTML 知识库快照说明 |
| `snapshots/wiki/controllable_flux_motor_research_plan.md` | wiki 原始快照 |
| `snapshots/html/controllable_flux_motor_kb.html` | HTML 知识库原始快照 |

## 3. 当前主线状态

- 主线分支：`claude-mainline`
- 研发原则：干净室推演，不复制、不猜测闭源厂商实现
- 当前落地实验：EXP-001、EXP-002、EXP-003、EXP-004
- 当前关键结论：低 `ψf` 不能单独带来高速收益，必须与高凸极比、母线电压、电流能力、MTPV 轨迹和安全边界协同设计
- 当前工程文档：`reports/` 下已有工程落地矩阵、驱动/上电/协议图、BOM/EDA、stage-gate 流程

## 4. 主线证明了什么

- 线性 dq 基线模型可以复现电压/电流约束下的转矩-转速边界。
- 虚拟可变 `ψf` 扫描说明单纯降磁链会损失目标转矩能力。
- 参数族扫描说明低磁链候选必须与高凸极比和更高 `Vdc/Imax` 协同。
- 热/退磁安全边界已进入简化数值模型，但仍需要真实磁钢、FEA 或台架数据替换。
- 工程路线已有可追踪目录，便于把仿真、测试、报告和下一步建模缺口关联起来。

## 5. 主线尚未证明什么

- 当前参数族排序不是真实电磁几何推荐。
- EXP-005 到 EXP-010 不属于 Claude 主线已落地的正式数值闭环。
- 非线性 `lambda_d/lambda_q` LUT、铁耗、逆变器损耗、NVH、EMC、机械强度仍未完成。
- 任何结果都不能直接用于高压高速实机部署。
- 工程释放仍需 FEA、HIL/台架、热、绝缘、EMC、功能安全和失效模式验证。

## 6. 维护规则

1. 新增实验必须同步更新 `simulation_traceability.md` 和 `models/scheme_simulation_coverage.json`。
2. wiki 或 HTML 知识库发生关键变更时，必须重新写入 `snapshots/` 并更新 `evidence_manifest.md`。
3. 所有工程结论必须标注证据路径，避免只写结论。
4. `passed_numeric_simulation` 只代表可复现实验，不代表工程验证。
5. Claude 主线与 Codex 推演应继续分支隔离，避免把 Codex 扩展实验误写成 Claude 主线结论。
