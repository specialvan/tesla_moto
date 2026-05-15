# Claude 可控磁通量电机知识库

## 1. 目录定位

`claude-docs` 是 `claude-mainline` 分支的工程知识库与交接包，负责沉淀 Claude 主线推演中的：

- 开发上下文 handoff；
- wiki / HTML 知识库冻结快照；
- EXP-001 到 EXP-004 与 EXP-006 的仿真实验证据；
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
| `toolchain_selection_and_github_references.md` | 高保真仿真工具链选型与 GitHub 参考项目 |
| `maxwell_motorcad_simulation_plan.md` | Maxwell / Motor-CAD / 开源工具链仿真设计落地方案 |
| `migration_alignment_index.md` | Claude 文档迁移与 Codex 对齐索引 |
| `snapshots/wiki/controllable_flux_motor_research_plan.md` | wiki 原始快照 |
| `snapshots/wiki/v2_review_pr_engineering_prd_wiki.md` | V2 review-pr 工程落地差距 Wiki 快照 |
| `snapshots/wiki/v2_scheme_engineering_playbook_wiki.md` | V2 分方案工程落地 playbook Wiki 快照 |
| `snapshots/wiki/v2_scheme_physical_deliverables_matrix_wiki.md` | V2 分方案物理工程交付物矩阵 Wiki 快照 |
| `snapshots/html/controllable_flux_motor_kb.html` | HTML 知识库原始快照 |
| `snapshots/html/v2_review_pr_engineering_prd.html` | V2 review-pr 工程落地差距 HTML 快照 |
| `snapshots/html/v2_scheme_engineering_playbook.html` | V2 分方案工程落地 playbook HTML 快照 |
| `snapshots/html/v2_scheme_physical_deliverables_matrix.html` | V2 分方案物理工程交付物矩阵 HTML 快照 |
| `../engineering/v2/README.md` | V2 12 个方案图纸包仓库落点和 README 审计索引 |

## 3. 当前主线状态

- 主线分支：`claude-mainline`
- 研发原则：干净室推演，不复制、不猜测闭源厂商实现
- 当前落地实验：EXP-001、EXP-002、EXP-003、EXP-004、EXP-006（synthetic `lambda_d/lambda_q` LUT 插值与非线性转矩证明）
- 当前关键结论：低 `ψf` 不能单独带来高速收益，必须与高凸极比、母线电压、电流能力、MTPV 轨迹和安全边界协同设计
- 当前工程文档：`reports/` 下已有工程落地矩阵、驱动/上电/协议图、BOM/EDA、stage-gate 流程
- 当前仿真方案：`toolchain_selection_and_github_references.md` 和 `maxwell_motorcad_simulation_plan.md` 已明确 Motor-CAD + Maxwell 2D/3D 为工程主线，PyMotorCAD/PyAEDT 为自动化入口，PyFluent 仅用于 Fluent 冷却/CFD 支线，Pyleecan/FEMM/SyR-e/Simulink/Python 为开源复核与控制闭环

## 4. 主线证明了什么

- 线性 dq 基线模型可以复现电压/电流约束下的转矩-转速边界。
- 虚拟可变 `ψf` 扫描说明单纯降磁链会损失目标转矩能力。
- 参数族扫描说明低磁链候选必须与高凸极比和更高 `Vdc/Imax` 协同。
- 热/退磁安全边界已进入简化数值模型，但仍需要真实磁钢、FEA 或台架数据替换。
- 工程路线已有可追踪目录，便于把仿真、测试、报告和下一步建模缺口关联起来。

## 5. 主线尚未证明什么

- 当前参数族排序不是真实电磁几何推荐。
- EXP-005、EXP-007 到 EXP-010 不属于 Claude 主线已完成工程闭环的正式结论；EXP-006 当前仅完成独立的 synthetic LUT 数值证明，尚未接入共享控制搜索。
- 非线性 `lambda_d/lambda_q` LUT、铁耗、逆变器损耗、NVH、EMC、机械强度仍未完成。
- 任何结果都不能直接用于高压高速实机部署。
- 工程释放仍需 FEA、HIL/台架、热、绝缘、EMC、功能安全和失效模式验证。

## 6. 维护规则

1. 新增实验必须同步更新 `simulation_traceability.md` 和 `models/scheme_simulation_coverage.json`。
2. wiki 或 HTML 知识库发生关键变更时，必须重新写入 `snapshots/` 并更新 `evidence_manifest.md`。
3. 所有工程结论必须标注证据路径，避免只写结论。
4. `passed_numeric_simulation` 只代表可复现实验，不代表工程验证。
5. Claude 主线与 Codex 推演应继续分支隔离，避免把 Codex 扩展实验误写成 Claude 主线结论。
