# Codex 开发进度深度评审 — R13 复评补遗

日期：2026-05-29
评审者：Opus 4.7 (1M)
分支：`claude-mainline`
R13 输入锚点：`298dfed docs(opus): 梳理当前复评handoff`
工作树：clean
对比基线：`origin/codex-review-line @ cfda256 (2026-05-13)`、`origin/claude-mainline @ 298dfed (2026-05-29)`

> 本轮目的：在 R12 关闭 CDR-001（claude-mainline 发布到 origin）之后，对 Codex 关键 deliverable 做一次**逐行落地核验**，不依赖此前轮次的摘要结论，并复核 r12 之后是否出现新的有效 open 项。本补遗只增不覆盖，沿用 `[[codex_progress_action_register]]` 系列的 supersedes 规则。

---

## 1. 本轮核验范围与方法

| 维度 | 方法 | 结论 |
|---|---|---|
| PyFluent 工作流 | 直接读取 mainline 源码 + 与 codex 原始版本 diff + 跑测试 | 已落地且被加固，护栏真实存在 |
| Codex 2026-05-15 评审包 | 逐条核验 10 条 CDR + 4 条 AMR 的代码现状 | 结论成立，4 条代码类 CDR 已在主线修复 |
| codex-docs 知识库 | 子代理独立核验 + 关键路径抽查 | 成熟度边界严格，无过度声明 |
| 分支同步状态 | `git log origin/codex-review-line..codex-review-line` | **发现新 open 项**：Codex 源线未发布 |

验证命令与结果见 `[[codex_progress_action_register_r13_followup]]` 的 `verification` 段。

---

## 2. PyFluent 工作流逐行核验（关闭项复核）

R08 曾以"dry-run / manifest / validation_chain / boundary allow-list"为由关闭 PyFluent 系列项。本轮直接读 mainline 源码确认这些护栏**真实存在**，并非文档声明：

- `sim/pyfluent_workflow.py:16-21`：`REQUIRED_VALIDATION_CHAIN_FIELDS = (cad_source_sha256, material_card_path, mesh_summary)`，在 `FluentRunConfig.validate()`（:57-65）强制校验，缺失即 `raise ValueError`。
- `sim/pyfluent_workflow.py:46-56`：boundary update 走 `allowed_boundary_variables` allow-list，zone/variable 不在白名单即拒绝，杜绝任意边界注入。
- `sim/pyfluent_workflow.py:158-168`：manifest 基底硬编码 `engineering_validated=False`、`production_release_allowed=False` 以及明确 `validation_note`（"does not constitute FEA, bench, HIL, or production-release evidence"）。
- `sim/run_pyfluent_workflow.py:56-79`：CLI 用 `--dry-run` / `--run` 互斥组，dry-run payload（:47-53）同样强制 `engineering_validated=False`。

**与 Codex 原始版本对比**（`git diff codex-review-line:sim/pyfluent_workflow.py HEAD:sim/pyfluent_workflow.py`）：Codex 原版（159 行）只有 `report_exports` + `save_case_data`，**没有** validation_chain 必填校验、**没有** boundary allow-list、**没有** 成熟度 note。mainline 集成版（176 行）是对 Codex 草案的**实质性加固**，而非简单 cherry-pick。

测试：`tests/test_pyfluent_workflow.py`、`tests/test_run_pyfluent_workflow.py` 共 7 项全绿。

**评级：高。** Codex 提供了高质量的 adapter 边界骨架（frozen dataclass + Protocol + 懒加载），mainline 在其上补齐了成熟度与安全护栏。关闭结论成立。

---

## 3. Codex 2026-05-15 评审包结论复核

逐条核验 `codex-review/docs/review_action_register_2026-05-15.json` 的 10 条 CDR 对应代码现状。四条代码类发现**已在主线修复**，证明 Codex 评审推动了真实整改：

| CDR | 主题 | 2026-05-15 状态 | 当前主线证据 | 现状 |
|---|---|---|---|---|
| CDR-003 | `combined_losses` 返回语义混淆 | open | `sim/iron_loss.py:297,306-307` 返回值已更名 `iron_loss_fraction`，docstring 标注 0..1 | 已修复 |
| CDR-004 | `freq_max_hz` 声明未强制 | open | `sim/run_iron_loss_experiment.py:182-187,234` 分离越界点并标注"extrapolations, not coefficient validation" | 已修复 |
| CDR-005 | 铁损/铜损比例统计口径不匹配 | open | `sim/run_iron_loss_experiment.py:268-275` 改为 `avg_iron/avg_copper` 且增加 `valid_freq` 变体 | 已修复 |
| CDR-006 | Flux LUT 不校验 pole_pairs | open | `sim/nonlinear_flux_lut.py:26-79` 增加 `motor_id`/`pole_pairs` 字段与校验；`sim/search.py:197-203` grid 裁剪到 LUT 轴 | 已修复 |

本表 CDR 编号沿用 Codex `review_action_register_2026-05-15.json` 的短号（与 Opus 自有的 `OPUS-2026-05-25-*` 命名空间不同）。其中 CDR-002（测试产物污染）、CDR-007/008（文档滞后）、CDR-009（.claude 隔离）已在 R06/R07/R11 各自闭环；CDR-001（分支集成）在 R12 关闭；CDR-010（PyFluent 主线决策）在 R08 关闭。

> **命名提醒**：本节的 Codex `CDR-002`（测试产物污染，已闭环）与 Opus 旧项 `OPUS-2026-05-25-CDR-002`（工作树卫生，已由 r07 关闭）属于不同命名空间。R13 默认分支滞后项使用新 ID `OPUS-2026-05-29-R13-DEFAULT-BRANCH-STALE`，避免机器复算把新 open 项误并入旧关闭项。

**子代理核验补充**：每条 CDR/AMR 都有证据路径引用，无空泛断言；未发现把 proxy/synthetic 写成 FEA/台架/HIL 的过度成熟度声明。轻微缺口：register 缺 `owner`/`deadline` 字段，部分证据引用到文件级而非行级。属文风建议，不构成有效 open。

> 核验诚信记录：子代理一度误报 `review_action_register_2026-05-15.json` 缺失（实际读成了 mutation matrix）。已用直接读文件纠正——该文件存在（6449 字节，10 条 CDR 结构完整）。

**评级：中—高。** 评审结论全部成立且已驱动主线修复；扣分项仅为登记表元数据粒度。

---

## 4. codex-docs 知识库核验

子代理独立核验 + 关键路径抽查结论：

- `codex-docs/simulation_traceability.md`：12 方案 `engineering_validated` 全部 `false`；成熟度分布（3 parameterized_linear / 4 proxy / 4 research_pool_proxy / 1 synthetic_fixture）与红线一致，无任何 proxy/synthetic 被写成真实工程验证。
- `codex-docs/evidence_manifest.md`：抽查 `experiments/exp_001_linear_dq/summary.json`、`experiments/exp_004_safety_boundaries/safety_boundary_results.csv`、`models/scheme_simulation_coverage.json` 均真实存在。
- snapshots wiki/HTML：措辞用"可仿真/可标定/可台架验证"（目标态）与"必须经过人工审查、仿真、HIL/台架验证"（边界声明），无过度成熟度声明。

**评级：高。** 红线执行严格，证据链完整。

---

## 5. 新发现的有效 open 项：Codex 源线未发布

R12 关闭 CDR-001 时只发布了 `claude-mainline`。本轮 `git log origin/codex-review-line..codex-review-line` 暴露一个此前未登记的事实：

```text
local  codex-review-line @ 6b137bf  (4 commits ahead)
origin codex-review-line @ cfda256  (2026-05-13, 冻结)
```

`origin/codex-review-line` 仍停在 `cfda256`，**不包含**以下 Codex 原创 deliverable：

| 提交 | deliverable | 当前是否已到 origin |
|---|---|---|
| `4e0c489` | PyFluent 工作流（`sim/pyfluent_workflow.py` 等 4 文件） | 仅经 mainline 加固版发布；codex 原始草案未发布 |
| `69b40b4` | 2026-05-15 Claude 开发深度评审工程包 | 经迁入 mainline 发布（`d9f95fe`）；codex 源线未发布 |
| `dd47e70` | 测试产物污染专项评审（AMR） | 同上 |
| `6b137bf` | 评审目标覆盖审计 | 同上 |

**关键升级：这是 origin 的默认分支。** `git symbolic-ref refs/remotes/origin/HEAD` 解析到 `refs/remotes/origin/codex-review-line`——也就是说 `origin/codex-review-line` 是**仓库默认分支**，全新 clone 默认 checkout 的就是它。`git cat-file -e origin/codex-review-line:sim/pyfluent_workflow.py` 与 `git cat-file -e origin/codex-review-line:codex-review/docs/claude_development_review_2026-05-15.md` 均返回缺失，证实默认分支冻结在 16 天前、缺 Codex 自己的 headline deliverable。

**风险定性**：内容层面这 4 个提交的等价产物**已通过 mainline 进入 origin**（PyFluent 加固版、迁入的 2026-05-15 评审包），因此**不是数据丢失风险**。但因为这个滞后分支正是 `origin/HEAD`，每一次全新 clone 都会拿到一个落后 16 天、缺 PyFluent 与 2026-05-15 评审包的"Codex 视角"。这把它从单纯的分支卫生项抬升为 **P1**：默认分支对外是仓库的第一印象，长期滞后会误导任何只看默认 checkout 的人。

**为什么本轮不直接关闭**：`codex-review-line` 当前绑定在独立 worktree `G:/tesla_moto-codex`，该 worktree 除本地领先 4 个已提交提交外，还有大量 modified/untracked 工程产物。直接在脏 worktree 上推送默认分支会绕过内容分组审计，也可能把未归档工作误判为可发布状态。因此本轮只登记 P1 open，并要求按 `branch_integration_strategy.md` 先决定发布 `codex-review-line` 还是重指默认分支。

**与当前 handoff 的口径核对**：`opus_handoff_for_review_current_2026-05-29.md` 报告 `effective_open_count=0` 且"远端对齐"。逐条核验后，该结论**只对 `claude-mainline` 成立**（`git rev-list --left-right --count origin/claude-mainline...HEAD` 确为 `0 0`），对 `origin/HEAD`（默认分支 codex-review-line）的滞后只字未提。这是一个 **scope-of-claim 缺口，不是事实造假**：handoff 没说错 claude-mainline 的状态，但把单分支对齐表述得像整个远端都已就绪。

登记为 `OPUS-2026-05-29-R13-DEFAULT-BRANCH-STALE`（见 r13 register，severity=P1）。该 ID 不复用早期已被 r07 关闭的 `OPUS-2026-05-25-CDR-002` 工作树卫生项，避免机器复算误把新 open 项过滤掉。建议按 `[[branch_integration_strategy]]` 决策：发布 `codex-review-line` 到 origin（首选，因为它是 origin/HEAD），或把 origin/HEAD 重指到 claude-mainline 并显式文档化 `origin/codex-review-line` 已被取代。在此之前，当前 handoff 的"远端对齐 / effective_open=0"口径应显式收敛到 claude-mainline，而非暗示整个远端皆已就绪。

---

## 6. R13 有效 open 项汇总

| ID | Severity | 状态 | 说明 |
|---|---|---|---|
| `OPUS-2026-05-29-R13-DEFAULT-BRANCH-STALE` | P1 | open | `origin/HEAD` = `origin/codex-review-line`（仓库默认分支）冻结在 cfda256（2026-05-13），缺 PyFluent 与 2026-05-15 评审包；内容已经 mainline 进入 origin（非数据丢失），但默认 clone 拿到的是 16 天前的 Codex 视图。当前 handoff 的"effective_open=0 / 远端对齐"仅对 claude-mainline 成立，是 scope-of-claim 缺口 |

CDR-001、DOCS-SYNC、PYFLUENT 系列、008、017 均维持 R08–R12 的 closed 结论，本轮逐行复核无翻案。

---

## 7. 不可越界口径（维持）

1. `engineering_validated=false` 全程未被翻转。
2. r02 proxy / synthetic / research_pool / parameterized_linear_model 未被写成 FEA / HIL / 台架 / 量产释放。
3. S02 60 A r02 soft gate 与 30 A r03 production target 仍显式区分。
4. S04 `flux_lut_sample.json` 仍为 synthetic_fixture。
5. PyFluent 仍为离线可审计自动化入口，不替代电磁 FEA 或冷却/材料工程验证。

---

## 8. 关联文件

- `[[codex_progress_action_register_r13_followup]]` — 本轮机器可读登记
- `[[codex_progress_deep_review]]` — R01 主报告
- `[[opus_handoff_for_review_2026-05-29]]` — 介入 handoff
- `[[branch_integration_strategy]]` — 分支集成策略
