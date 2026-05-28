# Claude 开发内容深度评审报告

评审日期：2026-05-15
评审包：`codex-review/docs`
评审对象：Claude 主线过程文档、wiki、HTML、Git 历史、代码、实验产物、测试和工程报告
当前工作区：`G:\tesla_moto-codex`
对照主线：`claude-mainline` at `391ce20`

## 1. 总体结论

Claude 主线已经从 2026-05-13 的 V1/V2 代理实验推进到更完整的工程事实源：`models/scheme_simulation_coverage.json` 已经登记控制 LUT、非线性 LUT phase-2、EXP-011 Bertotti 铁损，`codex-review/docs` 也已经在主线中形成 2026-05-14 的评审包。

但当前项目的最大风险仍然是“事实源漂移”。代码、coverage、summary、wiki、HTML、manifest、评审包、Git 工作树在不同分支上的状态并不一致。当前 `codex-review-line` 新增了 PyFluent 编排入口，但缺少 Claude 主线的控制 LUT 与 EXP-011；Claude 主线有 EXP-011 和控制 LUT，但本地 `models/control_lut.json` 因测试写入时间戳变脏，且 `.claude/` 未跟踪。

本轮评审判定：

- Claude 主线方向正向，能持续把概念路线转成可重跑数值代理、测试和结构化 coverage。
- `passed_numeric_simulation` 的边界仍需要被反复守住，它不是 FEA、台架或工程释放。
- 当前最优先修复项不是继续新增实验，而是让 Git 状态、测试输出、summary 路径、文档入口和证据 manifest 稳定下来。
- 代码层新增了几处应尽快修正的评审点：测试污染跟踪产物、`combined_losses()` 返回值语义错误、Bertotti 频率有效范围未执行、LUT 与电机参数缺少一致性校验。

## 2. 评审范围

| 类别 | 范围 |
|---|---|
| 过程文档 | `claude-docs/`、`codex-docs/`、`claude-review/`、`codex-review/docs` |
| Wiki / HTML | `wiki/controllable_flux_motor_research_plan.md`、`controllable_flux_motor_kb.html` |
| Git | `codex-review-line`、`claude-mainline`、近 40 条提交、分支差异、两个工作树状态 |
| 代码 | `sim/search.py`、`sim/nonlinear_flux_lut.py`、`sim/run_control_lut_generator.py`、`sim/iron_loss.py`、`sim/run_iron_loss_experiment.py`、PyFluent 工作流 |
| 测试 | `tests/test_control_lut_generator.py`、`tests/test_iron_loss.py`、PyFluent 相关测试、coverage 测试 |
| 实验产物 | EXP-001 到 EXP-011 summary/CSV，重点关注绝对路径和 generated output |

## 3. 主要发现

### CDR-2026-05-15-001：两条开发线已经明显分叉，需要先定集成策略

严重度：P0
状态：open

证据：

- 当前评审线：`4e0c489 feat: 增加PyFluent高保真工作流入口`
- Claude 主线：`391ce20 feat(exp011): 新增铁损模型和Bertotti三相铁损速度扫描实验`
- `git diff --stat codex-review-line..claude-mainline`
- `sim/pyfluent_workflow.py`
- `sim/iron_loss.py`
- `sim/run_control_lut_generator.py`

问题：

当前 `codex-review-line` 有 PyFluent 工作流提交，但 Claude 主线没有；Claude 主线有控制 LUT、EXP-011、`claude-docs/` 和 `codex-review/docs`，当前评审线没有。两条线不是简单前后关系，而是各自新增了不同能力。

影响：

- 后续 cherry-pick 或 merge 容易误删 PyFluent 或误丢 EXP-011；
- 文档评审若不记录分支和 HEAD，会把一条线的事实误套到另一条线；
- 评审包本身如果只落在当前分支，Claude 主线看不到本轮发现。

建议：

先做一个明确选择：将 `codex-review/docs` 本轮评审包和 PyFluent 工作迁移到 Claude 主线，或把 Claude 主线合回当前评审线。迁移前不要把任一分支描述为“唯一当前事实”。

### CDR-2026-05-15-002：测试和 runner 会写入跟踪产物，导致工作树持续变脏

严重度：P0
状态：open

证据：

- 当前评审线 8 个 `experiments/exp_*/summary.json` 仅绝对路径发生变化；
- Claude 主线 `models/control_lut.json` 仅 `generated_at` 时间戳发生变化；
- `tests/test_control_lut_generator.py` 调用 `run()` 默认写 `models/control_lut.json`；
- `tests/test_iron_loss.py` 调用 `run()` 默认写 `experiments/exp_011_iron_loss/*`；
- 多个实验 runner 的 summary 写入绝对 `csv_path`。

问题：

测试直接写 tracked artifact，且部分输出包含当前 worktree 绝对路径或当前时间。这样 `pytest` 本身会制造 Git diff。

影响：

- 接手者很难判断 diff 是真实模型变化还是测试副作用；
- 评审包、summary、CSV 可能在不同工作区中反复漂移；
- CI 如果检查干净工作树，会被无业务意义的路径或时间戳差异干扰。

建议：

测试应写入 `tmp_path` 或显式临时输出路径。若必须生成正式产物，使用专门的更新命令，不在普通测试中写跟踪文件。summary 内部路径应改为相对路径，`generated_at` 应支持测试注入固定时间或从 schema 中拆出。

### CDR-2026-05-15-003：`combined_losses()` 返回的不是效率，语义与文档不一致

严重度：P1
状态：open

证据：

- `sim/iron_loss.py` 中 `combined_losses()` docstring 写返回 `(total_loss_w, efficiency_percent)`；
- 实现返回 `total_iron / total_loss`；
- `tests/test_iron_loss.py` 在 copper loss 为 0 时断言 `eff == 1.0`。

问题：

`total_iron / total_loss` 是铁损占总损耗比例，不是电机效率，也不是百分比。当前测试把这个错误语义固化了。

影响：

- 后续若有人复用 `combined_losses()` 做 Pareto 或效率排序，会把损耗占比误读为效率；
- `efficiency_percent` 命名会让报告结果产生严重误导。

建议：

将返回值改名为 `iron_loss_fraction`，或让函数接收机械输出功率并返回真实效率。测试也要改成验证名称和物理含义一致。

### CDR-2026-05-15-004：Bertotti 系数的 `freq_max_hz` 没有被执行

严重度：P1
状态：open

证据：

- `BertottiCoeffs.freq_max_hz` 默认 400 Hz；
- `bertotti_iron_loss_per_phase()` 只检查 `freq_hz > 0`；
- EXP-011 按最高 18000 rpm、4 极对计算电频率可达约 1200 Hz。

问题：

模型声明了系数有效频率上限，但运行时没有警告、截断或标记超范围。EXP-011 的高转速点会超出默认有效范围。

影响：

- 高速铁损结果可能被误读为材料模型有效输出；
- `engineering_validated=false` 虽然保留，但 summary 中缺少逐点或汇总的 out-of-range 标记。

建议：

在铁损计算或 runner 中增加 `freq_hz > coeffs.freq_max_hz` 标记。对超范围点可选择抛错、写 warning 字段，或把 summary 的有效速度上限单独列出。

### CDR-2026-05-15-005：EXP-011 损耗比例指标混合了平均铁损和首个铜损点

严重度：P2
状态：open

证据：

- `sim/run_iron_loss_experiment.py`
- `iron_loss_vs_copper_loss_ratio = avg_iron_loss_target / target_points[0]["min_current_target_copper_loss_w"]`

问题：

分子是所有 target feasible 点的平均铁损，分母却取第一个 feasible 点的铜损。这个比例不是同一统计口径。

影响：

- summary 的比值可能随第一个 feasible 点变化而偏移；
- 后续若用它比较铁损和铜损重要性，会得到不稳定结论。

建议：

改为 `avg_iron_loss_target / avg_copper_loss_target`，或输出逐点 ratio 的平均/最大值。

### CDR-2026-05-15-006：Flux LUT 搜索没有校验 LUT 与电机参数的一致性

严重度：P1
状态：open

证据：

- `sim/search.py` 在 nonlinear 分支中使用 `flux_lut.pole_pairs` 计算转矩；
- 电压计算仍使用 `params.rs_ohm` 和 `omega_e`；
- `params.pole_pairs` 与 `flux_lut.pole_pairs` 没有一致性校验。

问题：

当前实现允许把一个极对数、单位或来源不同的 LUT 与另一个电机参数集混用。虽然 `FluxLut` 校验了自身 unit convention，但没有校验它与 `MotorParams` 的系统一致性。

影响：

- 转矩、速度和电压可能来自不同物理对象；
- 搜索结果会看似 feasible，但实际不可审计；
- 后续 FEA/测量 LUT 回灌时，这会成为高风险输入错误。

建议：

在 search 或 runner 入口增加 `params.pole_pairs == flux_lut.pole_pairs` 校验，并在 LUT manifest 中登记 motor id、unit convention、temperature、source 和 coordinate convention。

### CDR-2026-05-15-007：Claude 文档入口仍需追上 EXP-011 与控制 LUT

严重度：P1
状态：open

证据：

- `claude-docs/README.md`
- `claude-docs/handoff_context.md`
- `models/scheme_simulation_coverage.json`
- `experiments/exp_011_iron_loss/summary.json`
- `models/control_lut_schema.json`

问题：

Claude 主线结构化事实源已经包含控制 LUT 和 EXP-011，但人类入口文档仍主要围绕 EXP-001 到 EXP-004 与 EXP-006。2026-05-14 的评审包已经指出 EXP-005 到 EXP-010 文档滞后，2026-05-15 后这个滞后扩展到了 EXP-011。

影响：

- 新接手者会低估主线已经完成的实验和代码；
- 也可能忽略 EXP-011 仍是简化铁损代理，而不是 FEA/材料标定结果。

建议：

更新 `claude-docs/README.md`、`handoff_context.md`、`evidence_manifest.md`、`simulation_traceability.md`，把控制 LUT 与 EXP-011 纳入证据入口，同时保留模型限制。

### CDR-2026-05-15-008：Wiki / HTML 展示入口仍可能传播过时实验编号

严重度：P1
状态：open

证据：

- `wiki/controllable_flux_motor_research_plan.md`
- `controllable_flux_motor_kb.html`
- `claude-docs/snapshots/wiki/controllable_flux_motor_research_plan.md`
- `claude-docs/snapshots/html/controllable_flux_motor_kb.html`

问题：

活动 wiki 和 HTML 是最容易被人阅读和复用的入口，但它们仍保留早期路线矩阵和实验编号。若快照机制不刷新，会把旧状态继续固化。

影响：

- 汇报材料可能引用过时 EXP 编号；
- 工程包和 manifest 即使更新，也无法阻止 HTML 传播旧口径。

建议：

先更新活动 wiki/HTML，再刷新 snapshots 和 manifest SHA256。HTML 应增加 EXP-005 到 EXP-011 卡片，并标明 proxy、synthetic、`engineering_validated=false`。

### CDR-2026-05-15-009：`.claude/` 与多 worktree 需要隔离策略

严重度：P2
状态：open

证据：

- `git -C G:\tesla_moto status --short --branch`
- `git branch -a -vv` 中大量 `worktree-agent-*`

问题：

Claude 主线本地存在 `.claude/` 未跟踪目录，仓库也有多个 agent worktree 分支指向旧提交。它们对开发有用，但不应该默认参与长期工程证据。

影响：

- 搜索、grep 和评审可能扫进临时 worktree；
- 误提交 `.claude/` 会把本地配置或缓存带入仓库；
- 分支列表会让接手者误判主线状态。

建议：

将 `.claude/` 加入忽略规则，或只抽取明确需要长期化的规则文件。评审命令默认排除 `.claude/worktrees/`。

### CDR-2026-05-15-010：当前 PyFluent 工作流需要决定主线命运

严重度：P2
状态：open

证据：

- `sim/pyfluent_workflow.py`
- `sim/run_pyfluent_workflow.py`
- `tests/test_pyfluent_workflow.py`
- `tests/test_run_pyfluent_workflow.py`
- `codex-review-line` HEAD `4e0c489`

问题：

PyFluent 工作流已经在当前评审线提交并通过测试，但 Claude 主线没有这组文件。主线文档已经把 PyFluent 定位为 Fluent 冷却/CFD 支线，所以这组代码方向合理，但目前还没有进入 Claude 主线证据链。

影响：

- 若主线继续推进 Fluent/Icepak 冷却复核，会重复实现或漏掉这组已完成编排边界；
- 若不迁移，当前评审线和主线工具链文档会继续分叉。

建议：

在主线单独评审并 cherry-pick PyFluent 工作流，或在本包中登记为“评审线候选，不属于 Claude 主线已落地能力”。迁移时补充配置样例和文档入口。

## 4. 优先行动

| 优先级 | 行动 | 目标 |
|---|---|---|
| P0 | 停止普通测试写 tracked artifact，改用 `tmp_path` 或显式 update 命令 | 消除工作树噪声和绝对路径漂移 |
| P0 | 明确 `codex-review-line` 与 `claude-mainline` 集成策略 | 防止 PyFluent、EXP-011、控制 LUT 互相丢失 |
| P1 | 修正 `combined_losses()` 语义或命名 | 防止损耗比例被误读为效率 |
| P1 | 执行 Bertotti `freq_max_hz` 并在 summary 标记超范围点 | 防止高速铁损代理被误用 |
| P1 | 校验 Flux LUT 与 `MotorParams` 一致性 | 防止 FEA/测量 LUT 回灌时混用模型 |
| P1 | 更新 Claude docs、wiki、HTML、snapshots、manifest 到 EXP-011 | 恢复人类入口和事实源一致性 |
| P2 | `.claude/` 忽略或隔离 | 避免本地 agent 状态污染主线 |
| P2 | 决定 PyFluent 工作流迁移、保留或标记为候选 | 对齐高保真工具链路线 |

## 5. 后续评审路线

下一轮建议不要直接扩展新实验，而是先进入自动一致性门禁：

1. coverage JSON 中所有 `pytest_tests` 和 `result_artifacts` 必须存在。
2. 所有 summary 路径必须是仓库相对路径。
3. 普通 pytest 后工作树应保持干净，或明确只允许指定 update 命令写 tracked artifacts。
4. 控制 LUT、铁损、非线性 LUT 的 schema 必须包含数据来源、坐标约定和有效范围。
5. wiki/HTML 展示入口必须从 coverage JSON 或统一实验索引生成，减少手写漂移。

## 6. 评审判定

Claude 开发内容在工程化方向上是有持续进展的：主线已经从“能跑 dq 基线”推进到“有控制 LUT、有非线性 LUT 搜索、有铁损代理、有评审包”。但越往后，真正的质量门槛越不在“新增一个实验编号”，而在证据链是否稳定、测试是否不污染工作树、模型限制是否被机器和人类入口同时保留。

本轮报告已经落到 `codex-review/docs`，后续应按日期追加，而不是覆盖旧报告。
