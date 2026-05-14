# Claude 开发内容深度评审报告

评审日期：2026-05-14  
评审包：`codex-review/docs`  
评审对象：Claude 主线过程文档、wiki、HTML、实验事实源、测试覆盖、工程报告与 git 状态  
对照工作树：`claude-mainline` 本地分支，领先 `origin/claude-mainline` 4 个提交

## 1. 总体结论

Claude 主线已经从早期 EXP-001 到 EXP-004 的线性 dq、虚拟磁链、参数族与热/退磁边界，推进到 EXP-005、EXP-006、EXP-007、EXP-008、EXP-009、EXP-010 的完整可重跑数值代理层。当前 `models/scheme_simulation_coverage.json` 已把 12 个可控磁通量方案全部标为 `passed_numeric_simulation`，并且对应的 `experiments/*/summary.json` 普遍包含 `parameter_source`、`engineering_validated=false`、`model_scope`、`model_limitations` 等限制字段。

这说明 Claude 开发线的代码和实验事实源已经明显前进；但过程文档、wiki、HTML 和跨目录知识库尚未完全追上。当前最大风险不是“缺少实验”，而是“多个文档入口对当前状态的描述互相矛盾”，容易让后续 agent 或工程师误判哪些方案已可重跑、哪些只是架构规划、哪些仍是 FEA/台架前的代理模型。

首轮评审判定：

- Claude 主线的数值代理覆盖已经扩展到 EXP-001 到 EXP-010；
- `passed_numeric_simulation` 的含义必须严格限制为可复现数值实验，不得解释为工程验证；
- `claude-docs/`、`codex-docs/`、wiki、HTML、manifest 和 coverage JSON 需要一次集中对齐；
- git 工作树存在未提交文档修改与未跟踪 `.claude/` 目录，提交前需要明确取舍；
- coverage 测试还存在证据链漏洞：`pytest_tests` 字段没有被验证为真实存在，当前 `models/scheme_simulation_coverage.json` 已引用不存在的 `tests/test_control_search.py`。

## 2. 评审范围

| 类别 | 路径 | 本轮结论 |
|---|---|---|
| Claude 知识库入口 | `claude-docs/README.md` | 已有较清晰边界，但当前状态落后于最新实验事实源 |
| Claude handoff | `claude-docs/handoff_context.md` | 仍写 EXP-001 到 EXP-004 与 EXP-006，漏掉 EXP-005/007/008/009/010 |
| Claude 证据 manifest | `claude-docs/evidence_manifest.md` | 仿真实验证据只列 EXP-001 到 EXP-004，需补 EXP-005 到 EXP-010 和 EXP-006 |
| Claude 追踪矩阵 | `claude-docs/simulation_traceability.md` | 方案表已接近最新事实，但“下一批最小实验包”语义仍像待实施 |
| Wiki | `wiki/controllable_flux_motor_research_plan.md` | 仍是早期研发矩阵，需要重编号并回填最新 EXP 状态 |
| HTML | `controllable_flux_motor_kb.html` | 可视化矩阵明显滞后，EXP 编号和当前事实源不一致 |
| Coverage JSON | `models/scheme_simulation_coverage.json` | 当前最接近事实源，12 个方案均 numeric，但有测试路径断点 |
| 实验 summary | `experiments/exp_005*` 到 `exp_010*` | 已有可重跑代理实验，并保留 `engineering_validated=false` |
| 测试 | `tests/` | 20 个测试文件存在，但 coverage 元数据未校验测试文件真实存在 |
| Git | `git status`, `git log` | 本地领先 4 个提交，两个 `claude-docs` 文件未提交，`.claude/` 未跟踪 |

## 3. 当前事实基线

### 3.1 Git 基线

当前本地分支：

```text
claude-mainline...origin/claude-mainline [ahead 4]
```

近四个本地提交显示：

1. `ab9ce2c feat(sim): EXP-005/007/008/009/010 可重跑仿真入口`
2. `5b0995c test(sim): EXP-005/007/008/009/010 单元与烟雾测试`
3. `a3a413d docs(coverage): EXP-005..010 仿真状态从 needs_next_numeric_model 提升至 passed_numeric_simulation`
4. `7b9887e feat(sim): 补齐EXP-006非线性磁链LUT实验`

这组提交说明当前代码和模型事实已经进入 EXP-001 到 EXP-010 的代理闭环阶段。评审后续判断应以这些提交之后的工作树为准，而不是以较早的 `claude-docs` 文本为准。

当前未提交状态：

```text
M claude-docs/maxwell_motorcad_simulation_plan.md
M claude-docs/toolchain_selection_and_github_references.md
?? .claude/
```

评审含义：

- 两个工具链文档的 PyFluent/Fluent/Icepak 补充仍处于本地修改态；
- `.claude/` 看起来是 agent 本地工作目录，不应在没有明确意图时进入长期工程包；
- 本轮新增的 `codex-review/docs` 应作为新的评审工程包单独提交，避免与未冻结的工具链文档混在一个无说明提交中。

### 3.2 数值实验基线

当前 `experiments/` 下存在 10 个 summary：

| 实验 | 当前模型范围 | 工程限制 |
|---|---|---|
| EXP-001 | 线性 dq 基线、目标转矩、最大可行转矩 | 线性参数，不含 FEA 饱和/损耗闭环 |
| EXP-002 | 虚拟 `psi_f` 档位扫描 | 虚拟磁链缩放，不代表真实可变磁化硬件 |
| EXP-003 | `psi_f/Ld/Lq/Vdc/Imax` 参数族 | 缩放代理，不是真实几何推荐 |
| EXP-004 | 温度、Vdc 降额、简化退磁边界 | 简化退磁线需 FEA/磁钢数据替换 |
| EXP-005 | 过调制 `k_mod` 轴和参数化惩罚 | 无 PWM 波形重建、器件损耗图、EMI 模型 |
| EXP-006 | synthetic `lambda_d/lambda_q` LUT 插值与非线性转矩 | 未使用 FEA/测量 LUT，未接入电压约束控制搜索 |
| EXP-007 | 混合励磁等效 `psi_eff` 与励磁铜耗 | 无励磁绕组电感、热耦合、励磁机/转子漏磁 |
| EXP-008 | 绕组重构参数缩放和切换连续性代理 | 无接触器暂态、环流、绝缘和并联支路热分配 |
| EXP-009 | 多相相组电流降额 | 无谐波子空间、零序偏移、相级热 RC |
| EXP-010 | 说明性工况下铜耗 Pareto 排序 | 无铁耗、机械损耗、逆变器损耗、真实 drive cycle |

全部新增代理实验都正确保留了 `engineering_validated=false`，这是正向设计。后续文档必须继承这一口径。

## 4. 主要发现

### F-001：Claude 文档入口状态滞后

证据：

- `claude-docs/README.md`
- `claude-docs/handoff_context.md`
- `models/scheme_simulation_coverage.json`
- `experiments/exp_005_modulation_factor/summary.json`
- `experiments/exp_010_weighted_efficiency_pareto/summary.json`

问题：

`claude-docs/README.md` 仍写 EXP-005、EXP-007 到 EXP-010 不属于 Claude 主线已完成工程闭环；`handoff_context.md` 仍写当前状态为 EXP-001 到 EXP-004 与 EXP-006。与此同时，coverage JSON 和实验 summary 已显示 EXP-005 到 EXP-010 具备可重跑数值代理。

风险：

- 后续接手者可能忽略已经存在的 runner、tests 和 summary；
- 也可能反向误解为文档说“未完成”，从而重复实现 EXP-005 到 EXP-010；
- 文档与事实源冲突会降低证据链可信度。

建议：

- 将 `claude-docs/README.md` 的“当前落地实验”更新为 EXP-001 到 EXP-010；
- 同时明确分层：EXP-001 到 EXP-010 是 `passed_numeric_simulation`，不是 `engineering_validated`；
- 将 `handoff_context.md` 的当前状态改成 12 个方案均有数值代理，但 FEA、铁耗、逆变损耗、热/NVH/EMC/台架仍缺。

### F-002：证据 manifest 未覆盖最新实验

证据：

- `claude-docs/evidence_manifest.md`
- `experiments/exp_005_modulation_factor/summary.json`
- `experiments/exp_006_nonlinear_flux_lut/summary.json`
- `experiments/exp_007_hybrid_excitation/summary.json`
- `experiments/exp_008_winding_reconfiguration/summary.json`
- `experiments/exp_009_multiphase_phase_group/summary.json`
- `experiments/exp_010_weighted_efficiency_pareto/summary.json`

问题：

`claude-docs/evidence_manifest.md` 的“仿真实验证据”只列 EXP-001 到 EXP-004，未列 EXP-005 到 EXP-010，也没有把 EXP-006 的 LUT schema/sample 和 summary 纳入 manifest。

风险：

- 最新数值实验在知识库入口不可见；
- 审计时无法从 manifest 追踪到最新事实源；
- `claude-docs` 自称是证据入口，但入口不完整。

建议：

- 在 manifest 中新增 EXP-005 到 EXP-010 的 Summary/CSV/README 或说明；
- 对没有 README 的实验，先登记 Summary/CSV，并新增后续行动项补 README；
- 将 `models/flux_lut_schema.json` 和 `models/flux_lut_sample.json` 登记为 EXP-006 关键模型证据。

### F-003：Wiki 和 HTML 活动源未同步最新实验编号

证据：

- `wiki/controllable_flux_motor_research_plan.md`
- `controllable_flux_motor_kb.html`
- `models/scheme_simulation_coverage.json`

问题：

Wiki 中仍保留早期 EXP-01 到 EXP-08/09 的规划式矩阵；HTML 可视化矩阵只展示到 EXP-07，且把 EXP-07 写为工况加权效率。但当前事实源中：

- EXP-005 是 SVPWM 过调制；
- EXP-006 是非线性磁链 LUT；
- EXP-007 是混合励磁；
- EXP-008 是绕组重构；
- EXP-009 是多相相组；
- EXP-010 是工况加权 Pareto。

风险：

- 面向汇报的 HTML 会传播错误编号；
- Wiki 的研发路线与实际实验目录脱节；
- 快照机制会固化过时内容。

建议：

- 先更新活动源 wiki 和 HTML，再刷新 `claude-docs/snapshots/`；
- 在 wiki 中新增“当前实验事实源表”，以 `experiments/exp_*` 实际目录为准；
- HTML 增加 EXP-005 到 EXP-010 的卡片，并明确每个是代理模型或 synthetic LUT。

### F-004：`codex-docs` 与当前主线事实不一致

证据：

- `codex-docs/handoff_context.md`
- `codex-docs/simulation_traceability.md`
- `models/scheme_simulation_coverage.json`
- `experiments/exp_006_nonlinear_flux_lut/summary.json`

问题：

`codex-docs` 仍描述 `nonlinear_flux_lut` 是唯一 `needs_next_numeric_model` 缺位，而当前 Claude 主线已经通过 EXP-006 补齐 synthetic LUT schema、插值和非线性转矩证明，并在 coverage JSON 中标为 `passed_numeric_simulation`。

风险：

- `codex-docs` 与 `claude-docs` 之间不再只是分支视角不同，而是事实过期；
- 如果后续把 `codex-docs` 作为评审入口，会误导 EXP-006 的优先级。

建议：

- 在 `codex-docs` 标明其历史分支视角，或更新为“截至某提交”的归档状态；
- 当前新的 Codex 评审入口应迁移到 `codex-review/docs`，以当前 `claude-mainline` 为评审对象；
- 若继续维护 `codex-docs`，需要同步 EXP-006 状态。

### F-005：Coverage 元数据引用不存在测试文件

证据：

- `models/scheme_simulation_coverage.json`
- `tests/test_scheme_simulation_coverage.py`
- `tests/` 目录清单

问题：

`models/scheme_simulation_coverage.json` 中 `mtpa_fw_mtpv_control` 引用了 `tests/test_control_search.py`，但当前 `tests/` 下不存在该文件。现有 `tests/test_scheme_simulation_coverage.py` 只检查 `pytest_tests` 字段非空，不检查每个测试路径是否存在。

风险：

- 覆盖目录看似完整，实际测试证据链有断点；
- 未来可能继续登记不存在的测试路径而不被 CI 发现；
- 这会削弱 `passed_numeric_simulation` 的可审计性。

建议：

- 将 `models/scheme_simulation_coverage.json` 中不存在的 `tests/test_control_search.py` 替换为实际主线测试路径，例如 `tests/test_exp_001_runner.py` 或新增真实控制搜索测试；
- 增强 `tests/test_scheme_simulation_coverage.py`，对 `pytest_tests` 和 `result_artifacts` 都执行 `Path.exists()`；
- 若某测试是计划项，不应放在 `pytest_tests` 字段，应放入 `next_simulation_step` 或单独 `planned_tests`。

### F-006：工程目录中的部分 deliverables 仍指向旧实验编号或未来文件

证据：

- `models/scheme_engineering_catalog.json`
- `experiments/` 实际目录

问题：

工程目录里存在一些 deliverables 与当前实际目录编号不一致或仍是未来文件，例如 modulation deliverable 写 `experiments/exp_004_modulation_factor/results.csv`，hybrid/winding/multiphase 等也有早期编号痕迹。

风险：

- 工程报告和 coverage JSON 的证据路径不一致；
- 后续生成报告或自动审计时会追踪到不存在路径；
- 方案目录的权威性下降。

建议：

- 把 engineering catalog 的 deliverables 分成 `existing_artifacts` 和 `planned_deliverables`；
- 对现有 artifact 使用真实路径：`experiments/exp_005_modulation_factor/...`、`exp_007_hybrid_excitation/...` 等；
- 增加测试，检查 `existing_artifacts` 必须存在，而 `planned_deliverables` 可不存在但必须标注未来状态。

### F-007：未提交工具链文档修改需要冻结策略

证据：

- `git status --short --branch`
- `git diff -- claude-docs/maxwell_motorcad_simulation_plan.md claude-docs/toolchain_selection_and_github_references.md`

问题：

当前两个 `claude-docs` 文件有未提交修改，主要补充 PyFluent/Fluent/Icepak 相关表述。这些修改本身方向合理：PyAEDT 控制 AEDT/Maxwell，PyFluent 控制 Fluent 冷却/CFD，不应把 PyFluent 误作 Maxwell 电磁仿真入口。

风险：

- 若与其他文档修正混合提交，后续审计不容易区分“工具链口径修正”和“实验状态同步”；
- 若长期不提交，会导致 `claude-docs` 入口有本地态与远端态差异。

建议：

- 单独提交工具链澄清，提交信息可为 `docs(toolchain): clarify PyAEDT and PyFluent responsibilities`；
- 再单独提交本轮 `codex-review/docs` 评审包；
- 最后单独提交 Claude 文档/wiki/HTML 状态对齐。

### F-008：`.claude/` 未跟踪目录需要显式忽略或隔离

证据：

- `git status --short --branch`
- `.gitignore`

问题：

`.claude/` 当前未跟踪，`.gitignore` 没有忽略它。该目录通常属于本地 agent 工作区，不应默认进入工程知识库。

风险：

- 误提交本地工作树、缓存或临时文件；
- grep/搜索时纳入大量重复 worktree 内容，影响评审准确性；
- 外部审计时混入非主线事实源。

建议：

- 如果 `.claude/` 是本地私有目录，加入 `.gitignore`；
- 如果其中有需要保留的工作流或长期规则，只抽取必要文件到明确目录，不整目录提交；
- 后续 grep/search 时默认排除 `.claude/worktrees/`。

## 5. 分层评估

### 5.1 代码与实验层

优点：

- EXP-005 到 EXP-010 已经有独立 runner 和 smoke/unit tests；
- EXP-006 已有 schema、sample、插值器和边界检查；
- summary 文件普遍包含限制说明和 `engineering_validated=false`；
- 12 个方案在 coverage JSON 中均有下一步建模方向。

不足：

- 多数新增实验仍是参数化代理；
- EXP-006 还没有接入电压约束搜索、MTPA/FW/MTPV 轨迹和热/退磁边界；
- EXP-010 只做铜耗和说明性工况，尚不能得出真实效率 Pareto；
- coverage 测试没有校验测试路径存在。

### 5.2 文档层

优点：

- `claude-docs` 已有 README、handoff、manifest、traceability、toolchain、Maxwell/Motor-CAD 方案；
- 文档普遍保留干净室边界和工程验证限制；
- 工具链文档已把 Motor-CAD、Maxwell、PyAEDT、PyMotorCAD、PyFluent 的分工写清楚。

不足：

- README/handoff/manifest/wiki/HTML 的当前状态落后；
- `claude-docs/simulation_traceability.md` 的“下一批最小实验包”需要改成“已落地代理实验与下一步高保真升级”；
- `wiki_html_evidence.md` 仍只说明 HTML 同步到 EXP-003；
- snapshots 机制尚未跟上活动源更新。

### 5.3 工程报告层

优点：

- `reports/` 已覆盖落地矩阵、驱动/上电/协议、BOM/EDA、stage-gate；
- `models/scheme_engineering_catalog.json` 有 12 个方案的工程目标、输入、实验、验收、失败模式和交付物。

不足：

- 工程目录中的部分 deliverable 路径仍像规划项而非实际 artifact；
- BOM/EDA 和驱动图应继续保持架构规划口径，不应被误读为硬件设计完成；
- 缺少一个统一字段区分 `existing_artifacts` 与 `planned_deliverables`。

## 6. 建议行动优先级

| 优先级 | 行动 | 目标 |
|---|---|---|
| P0 | 修正 coverage JSON 中不存在的 `tests/test_control_search.py` 引用 | 消除测试证据链断点 |
| P0 | 增强 coverage 测试，校验 `pytest_tests` 路径存在 | 防止未来登记虚假测试路径 |
| P0 | 更新 `claude-docs/README.md`、`handoff_context.md`、`evidence_manifest.md` | 恢复知识库入口可信度 |
| P1 | 更新 wiki 和 HTML 的实验矩阵到 EXP-001 到 EXP-010 | 防止汇报入口传播过时编号 |
| P1 | 刷新 `claude-docs/snapshots/` 和 `wiki_html_evidence.md` | 保持活动源与冻结快照一致 |
| P1 | 对 `models/scheme_engineering_catalog.json` 拆分现有/计划交付物 | 改善工程目录审计性 |
| P2 | 单独提交工具链文档的 PyFluent/Fluent 澄清 | 冻结本地未提交文档状态 |
| P2 | 决定 `.claude/` 是否加入 `.gitignore` | 避免本地 agent 工作目录误提交 |
| P2 | 为每个实验补 README 或统一生成实验卡片 | 提升人类可读证据链 |

## 7. 下一轮评审建议

下一轮应从“文档状态修复”进入“自动化一致性门禁”：

1. 增加测试：coverage JSON 中所有 `pytest_tests` 必须存在。
2. 增加测试：coverage JSON 中所有 `result_artifacts` 必须存在且 summary 包含 `engineering_validated`。
3. 增加脚本：从 `models/scheme_simulation_coverage.json` 自动生成 `claude-docs/simulation_traceability.md` 的主体表格，减少手写漂移。
4. 增加检查：HTML/wiki 的实验编号必须覆盖 EXP-001 到 EXP-010。
5. 增加 release checklist：提交前检查 git 工作树、快照、manifest、coverage、tests 是否同步。

## 8. 评审判定

本轮 Codex 评审认为 Claude 主线的技术推进方向是正向的：它没有把代理模型包装成工程释放，且每个新增实验都保留限制说明。但当前知识库已经出现“事实源前进、过程文档滞后”的典型漂移。

因此，短期最重要的不是继续新增 EXP-011，而是先把已有 EXP-001 到 EXP-010 的证据链打通：coverage JSON、summary、tests、README/handoff/manifest、wiki、HTML、snapshots、git 提交状态必须一致。完成这一步后，再推进 FEA `lambda_d/lambda_q` 回灌、非线性控制搜索、实测 drive cycle、铁耗/逆变器损耗和热/退磁高保真闭环。
