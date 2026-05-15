# Wiki / HTML 知识库证据说明

## 1. 快照目的

本目录固化 `claude-mainline` 当前阶段的两类核心知识库：

| 类型 | 活动源 | 冻结快照 |
|---|---|---|
| Wiki 研究计划 | `wiki/controllable_flux_motor_research_plan.md` | `claude-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` |
| V2 review-pr 工程差距 Wiki | `wiki/v2_review_pr_engineering_prd_wiki.md` | `claude-docs/snapshots/wiki/v2_review_pr_engineering_prd_wiki.md` |
| V2 分方案工程落地 Wiki | `wiki/v2_scheme_engineering_playbook_wiki.md` | `claude-docs/snapshots/wiki/v2_scheme_engineering_playbook_wiki.md` |
| HTML 可视化知识库 | `controllable_flux_motor_kb.html` | `claude-docs/snapshots/html/controllable_flux_motor_kb.html` |
| V2 review-pr 工程差距 HTML | `claude-review/docs/2026-05-15/v2_review_pr_engineering_prd.html` | `claude-docs/snapshots/html/v2_review_pr_engineering_prd.html` |
| V2 分方案工程落地 HTML | `claude-review/docs/2026-05-15/v2_scheme_engineering_playbook.html` | `claude-docs/snapshots/html/v2_scheme_engineering_playbook.html` |

快照用于上下文恢复和证据留痕。活动源发生变更时，应重新复制到 `snapshots/` 并更新 `evidence_manifest.md`。

## 2. Wiki 当前承载的信息

`wiki/controllable_flux_motor_research_plan.md` 是主线研发文本基准，包含：

- 研发目标和干净室原则；
- dq 动态/准稳态电压方程；
- 线性和非线性磁链模型；
- 线性与 LUT 转矩方程；
- 电压、电流、速度、铜耗、退磁裕度指标；
- 技术假设树：控制路线、非线性磁路路线、真实可变磁链路线；
- Phase 0 到 Phase 5 的研发路径；
- EXP-001 到 EXP-009 的实验矩阵；
- Agent / Codex 并行任务拆分；
- 当前推荐结论和工具链。

关键结论：

- 普通弱磁降低合成 d 轴磁链和端电压压力，但不改变永磁体本身 `Ke/psi_f`。
- 只有可变磁化、混合励磁或绕组重构等路线才可能改变真实等效 `Ke/psi_f`。
- EXP-002 显示单纯降低 `psi_f` 会损失目标转矩能力。
- EXP-003 显示低磁链候选必须结合高凸极比和更高 `Vdc/Imax`。

## 3. HTML 当前承载的信息

`controllable_flux_motor_kb.html` 是面向阅读和汇报的可视化入口，包含：

- 目标定义；
- 核心方程卡片；
- 技术路线表；
- 可执行实验矩阵；
- 开源工具链；
- 研发里程碑；
- Agent/Codex 分工；
- 风险边界与判断指标。

当前 HTML 已同步 EXP-003 结论：

- 已完成 `psi_f/Ld/Lq/Vdc/Imax` 共 108 个组合；
- 最高分组合为 `psi_f100% + Ld80% + Lq160% + Vdc115% + Imax115%`；
- 低 `psi_f70%` 只有配合高凸极比、较高 `Vdc/Imax` 才进入候选。

## 4. V2 review-pr 知识库补充

`wiki/v2_review_pr_engineering_prd_wiki.md` 和 `claude-review/docs/2026-05-15/v2_review_pr_engineering_prd.html` 用于承载 review-pr 外部资料对真实工程落地差距的 V2 对齐结果。

关键结论：

- v0.3 控制主线继续保留：弱磁、MTPA/FW/MTPV、非线性磁链 LUT、热/退磁安全保护。
- 可变磁通 / Memory Motor 不能只用 `psi_f` 档位缩放证明，必须补磁状态机、脉冲能量、状态观测、未知状态回退。
- 扁线、油冷、多合一不是算法实验，而是 G2-G6 的系统工程阶段门约束。
- 当前数值实验默认不得替代 FEA、台架、DFMEA、DVP&R、PV/PPAP 等硬证据。

## 5. V2 分方案工程落地知识库补充

`wiki/v2_scheme_engineering_playbook_wiki.md` 和 `claude-review/docs/2026-05-15/v2_scheme_engineering_playbook.html` 用于承载 V2 每个方案深度推进工程落地的索引版与页面化证据。

关键结论：

- 主线四件套是近期闭环重点：负 d 轴弱磁、MTPA/FW/MTPV、非线性磁链 LUT、温度/退磁安全保护。
- P1 候选路线必须通过 FEA LUT、系统损耗、NVH、制造风险和 scorecard 晋级，不能只靠参数缩放。
- P2 研究池路线必须先有 guardrail：Memory Motor、混合励磁、绕组重构、多相相组都要明确禁止误判和必补证据。
- V2 推进纪律是主线先闭环，候选靠 scorecard 晋级，研究池靠 guardrail 防止误判。

## 6. 使用方式

1. 面向工程继续开发时，以活动源为准。
2. 面向上下文交接或审计时，使用 `claude-docs/snapshots/` 中的冻结快照。
3. 如果活动源与快照不一致，需要判断是否应刷新快照。
4. 不允许只更新 HTML 不更新 wiki，或只更新 wiki 不更新证据索引。
