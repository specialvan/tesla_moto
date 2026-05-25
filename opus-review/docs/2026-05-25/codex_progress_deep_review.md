# Codex 当前开发进度深度评审报告

评审日期：2026-05-25  
评审员：Opus 4.7 (1M context)  
分支：`claude-mainline` HEAD `d7abf6e`；对照 `codex-review-line` HEAD `6b137bf`  
评审包：`opus-review/docs/2026-05-25/`  
对照评审：[`codex-review/docs/claude_development_review_2026-05-15.md`](../../../codex-review/docs/claude_development_review_2026-05-15.md)、[`codex-review/docs/claude_image_to_production_deep_review_2026-05-19.md`](../../../codex-review/docs/claude_image_to_production_deep_review_2026-05-19.md)

---

## 1. 评审目标

把 Codex 当前已落地与未合入主线的开发产物深度过一遍，回答四个问题：

1. Codex 这一轮交付了什么？工程上是否成立？
2. Codex 已经指出的风险（10 条 CDR + AMR + 图档打回）目前是否被消化到 Claude 主线？
3. 两条线（PyFluent 高保真路线 vs r02/r03 概念→生产收敛路线）应该怎样合一，避免后续 cherry-pick / merge 漏交付？
4. 还有哪些点是 Codex 没明确指出，但 Opus 视角认为必须在下一轮闭环之前解决？

不在评审范围：

- 真实 FEA 结果、台架数据、HIL 报告（项目仍处于 v0 数值代理阶段）；
- 全量 12 个方案逐一拉一遍 PCB/CAD/BOM 内部审查（已由 codex-review 多轮做过）；
- gpt-image-2 真实生图服务器对 r02-sim 批包的回归（仍在 `gpt-image-2/outputs/` 等待 handoff 触发）。

---

## 2. 总体结论

**Codex 当前开发进度是健康的，质量门槛在持续收紧，但有 4 处 Codex 已明确点名、Claude 主线仍未结案的强约束没有闭环；同时 Codex 自己的 PyFluent 高保真路线还停留在评审线本地，没有进入 Claude 主线的证据链。**

具体判定：

- **正向能力（持续积累）**
  - Codex 的 r02 仿真锚点提示词批包是迄今最强的“防误读”工程产物之一：把 12 方案的 `scheme_id`、`simulation_status`、`model_maturity`、`sim_binding`、`pytest_gate`、`engineering_validated=false`、`next_simulation_step` 强制写到图面 SIM ANCHOR 面板。Claude 主线已按此打回意见落地了 r03 提示词包与护栏测试（`tests/test_r03_prompt_maturity.py` 42/42 绿灯）。
  - Codex 的 `codex-review/docs/claude_development_review_2026-05-15.md`（10 条 CDR）与 `artifact_mutation_review_2026-05-15.md`（4 条 AMR）是首批可以直接当作 PR review checklist 使用的评审包，证据链完整、严重度分级清晰、修复路径具体。
  - Codex 的 `codex-docs/toolchain_selection_and_github_references.md` 把 “Maxwell 电机仿真设计” 工程上等价于 Ansys Maxwell 这件事写死，给后续 EXP-001..010 升级到 FEA 的路径定调了。
  - Codex 的 PyFluent 工作流（`sim/pyfluent_workflow.py` 159 行 + runner 80 行 + tests 99+44 行）在代码层质量上是当前仓库里最干净的 Python 模块：`@dataclass(frozen=True)` 不变量、`Protocol` 抽象 + 懒加载 `PyFluentAdapter`、测试用 `tmp_path` + Fake adapter、`engineering_validated=False` 写入 manifest、所有错误路径走 `try / finally` 保证 `close()`。
- **未闭环约束（Opus 视角 P0）**
  - **CDR-2026-05-15-001 分支分叉未解决**：PyFluent 仍只在 `codex-review-line`，不在 `claude-mainline`；Codex 的 `codex-review/docs/*_2026-05-15.md` 评审包也未在 `claude-mainline` 上呈现（参见 [`branch_integration_strategy.md`](./branch_integration_strategy.md)）。
  - **CDR-2026-05-15-002 测试产物污染未根治**：当前工作树仍有 `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/`（Codex r02 sim 批包）与 `codex-review/docs/v2_r02_sim_image_generation_handoff_2026-05-20.md` 处于 untracked 状态，外加 `codex-docs/wereview.md`、`review-pr/`、`.claude/worktrees/`。其中 `review-pr/` 装了两份外部参考 HTML + `_files` 资源目录，正在污染工程证据。
  - **CDR-2026-05-15-003 `combined_losses()` 语义错误**：未在 `claude-mainline` 上验证修正（`sim/iron_loss.py` 的 docstring 与返回值仍需逐字复核）。
  - **AMR-001/002/003 测试默认写 tracked artifact / 绝对路径 / 时间戳漂移**：`run_control_lut_generator.run()` 的默认 `output_path = models/control_lut.json`、`metadata.generated_at = datetime.now(...)` 仍在，CI 端没有 dirty check。
- **结构性正向收敛（可计入“r02→r03 落地成熟度”）**
  - 12 个方案均有 `sim_binding-r02.json`；P0 四方案（S01/S02/S04/S11）已绑定 `tests/test_scheme_p0_lut_acceptance.py` 通用 harness；P1/P2 八方案已绑定 `tests/test_scheme_experiment_acceptance.py` 通用 harness；`tests/test_r03_prompt_maturity.py` 强约束 12 个 r03 prompt pack 必须含 `engineering_validated = false`、`evidence_gap`、proxy/synthetic_fixture/sample-only 标识，且禁止 `fea-backed validation` / `engineering recommendation` / `production release approved` 等 9 个超成熟度短语。
  - S02 的 60 A vs 30 A 文档目标已显式区分为 r02 proxy soft gate vs r03 production target；S04 的 3x3 synthetic LUT 已显式标 `synthetic_fixture` 并把 `feasible_points_min = 1` 限定为 smoke gate；这些是“防止 r02 通过被宣传为 r03 通过”的关键护栏。

判定一句话：**Codex 这一轮在“证据成熟度边界 + 不让 Claude 主线越界”这件事上做了非常关键的贡献；下一步阻塞点不是再写新评审，而是把 Codex 已经存在的 4 处 P0 修复实际推进到 `claude-mainline`。**

---

## 3. Codex 当前交付盘点

详见 [`codex_deliverable_inventory.md`](./codex_deliverable_inventory.md)。核心摘要：

### 3.1 仅在 `codex-review-line` 落地（未进入 `claude-mainline`）

| 类别 | 产物 | 提交 | 评价 |
|---|---|---|---|
| 代码 | `sim/pyfluent_workflow.py`、`sim/run_pyfluent_workflow.py` | `4e0c489` | 设计干净，测试隔离；但 ANSYS Fluent license 在当前工作环境未验证 |
| 测试 | `tests/test_pyfluent_workflow.py`、`tests/test_run_pyfluent_workflow.py` | `4e0c489` | 使用 `tmp_path` + Fake adapter，是 AMR-001 推荐模式的活范例 |
| 文档 | `codex-docs/README.md`、`codex-docs/evidence_manifest.md`、`codex-docs/handoff_context.md`、`codex-docs/simulation_traceability.md`、`codex-docs/wiki_html_evidence.md` | `14462e9` + `90d2a66` | 知识库入口完整，与 `claude-docs/` 形成对照 |
| 文档 | `codex-docs/toolchain_selection_and_github_references.md` | `cfda256` | 把 Maxwell/Motor-CAD/Simulink/Pyleecan/motulator 路线定调；GitHub 引用可直接审计 |
| 文档 | `codex-docs/snapshots/wiki/`、`codex-docs/snapshots/html/` | `14462e9` | 与 `claude-docs/snapshots/` 双套快照，便于离线复核 |
| 评审 | `codex-review/docs/claude_development_review_2026-05-15.md` | `69b40b4` | 10 条 CDR，Opus 复审认为全部成立 |
| 评审 | `codex-review/docs/artifact_mutation_review_2026-05-15.md` | `dd47e70` | 4 条 AMR，是工程证据链最直接的护栏 |
| 评审 | `codex-review/docs/goal_traceability_audit_2026-05-15.md` | `6b137bf` | 评审目标到产物的覆盖审计，避免“评审被宣称完成”的错觉 |
| 数据 | `codex-review/docs/review_action_register_2026-05-15.json`、`artifact_mutation_matrix_2026-05-15.json`、`goal_traceability_checklist_2026-05-15.json` | 同上 | 机器可读，可作为 dashboard 数据源 |

### 3.2 Codex 贡献且当前工作树 untracked（影响 Claude 主线）

| 路径 | 状态 | 评价 |
|---|---|---|
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/` | untracked | r02 仿真锚点提示词批包；Claude 主线 r03 提示词已按它打回意见重写，但批包本体仍未提交 |
| `codex-review/docs/v2_r02_sim_image_generation_handoff_2026-05-20.md` | untracked | r02-sim 图档开跑 handoff；包含 smoke/dry-run/edit-reference 命令清单 |
| `codex-docs/wereview.md` | untracked | 内容未审查，疑为占位/草稿 |
| `codex-review/docs/README.md` | modified | 仅追加上面两项的入口表，未提交 |

### 3.3 Claude 主线已落地的 Codex 反馈消化产物

| 路径 | 性质 | 是否覆盖 Codex 打回意见 |
|---|---|---|
| `engineering/v2/scheme-*/parameters/V2-S*-PARAM-sim_binding-r02.json` (12 份) | 仿真合同 | 是；显式 strong/soft check、DVP mapping、open_items、`engineering_validated=false` |
| `engineering/v2/scheme-*/prompts/V2-S*-PROMPT-r03-production_drawing_pack.md` (12 份) | r03 prompt | 是；通用负面约束、`engineering_validated = false`、`evidence_gap`、`proxy`/`synthetic fixture`/`sample-only` |
| `tests/test_r03_prompt_maturity.py` | 提示词护栏 | 是；12 方案 × 4 条 prompt = 48 条强约束 |
| `tests/test_scheme_p0_lut_acceptance.py` | P0 通用 harness | 是；S01/S02/S04/S11 共享 strong/soft check 与 DVP 校验 |
| `tests/test_scheme_experiment_acceptance.py` | P1/P2 通用 harness | 是；suffix DSL（`.equals`/`.regex`/`.enum`/`.count_min`/`.min`/`.max`/`.present`/`.absent`）支持 8 个非 P0 方案 |
| `models/scheme_simulation_coverage.json` | 覆盖矩阵 | 是；每方案 `simulation_status` + `model_maturity` + `maturity_flags` 同步写入 |
| `claude-review/docs/2026-05-20/v2_r03_prompt_parameter_sim_deep_review.md` | 自查 | 是；S05-S10/S12 的 High risk 被 r03 包归并到 `proxy ranking only` / `research pool` |

---

## 4. 代码级评审：PyFluent 工作流

### 4.1 设计正向

`sim/pyfluent_workflow.py:14-95` 把 Fluent 自动化拆成 5 层：

1. `BoundaryUpdate` / `ReportExport`：`@dataclass(frozen=True)`，符合本项目 immutability 约束；
2. `FluentRunConfig.validate()`：在调用前显式检查 case 文件存在、`iterations > 0`、report 文件名不含目录；
3. `FluentRunResult`：返回 manifest 与产物路径，不外泄 session；
4. `FluentAdapter(Protocol)`：解耦真实 PyFluent 依赖；
5. `FluentWorkflow.run()`：finally 块保证 `adapter.close()`，并把 `engineering_validated: False` + 解释性 note 写到 manifest。

`PyFluentAdapter` 把 `from ansys.fluent.core import launch_fluent` 放在 `__init__` 里，意味着 import 阶段不会因为缺失商业依赖而崩；测试侧 `tests/test_pyfluent_workflow.py:1-90` 直接消费 `FluentWorkflow(adapter=FakeFluentAdapter())`，对 `tmp_path` 完全干净。

### 4.2 待补强点

| ID | 风险 | 证据 | 严重度 | 建议 |
|---|---|---|---|---|
| OPUS-2026-05-25-001 | `BoundaryUpdate.variable` 直接 `setattr(zone, variable.replace("-", "_"), value)`，若 zone 对象不存在或属性名不匹配会抛 `AttributeError`，但 manifest 已写一半 | `sim/pyfluent_workflow.py:155-159` | P2 | 把 `adapter.set_boundary` 失败的具体 zone/variable 写到 manifest 前置 dry-run 字段；或在 `FluentRunConfig.validate()` 增加 boundary key allow-list |
| OPUS-2026-05-25-002 | manifest 写入在 `finally` 之外，如果 `iterate()` 抛错就不会写 manifest | `sim/pyfluent_workflow.py:88-117` | P2 | 在 `finally` 中按 `success=False` 也写 manifest，便于 audit 失败 run |
| OPUS-2026-05-25-003 | `run_pyfluent_workflow.py` 没有 `--dry-run` / `--no-launch` 模式；评审者无法在没有 Fluent license 的环境下复核 config 解析 | `sim/run_pyfluent_workflow.py:50-72` | P2 | 增加 `--dry-run`：只 `load_config()` + 打印解析后的 `FluentRunConfig` 但不实例化 `PyFluentAdapter` |
| OPUS-2026-05-25-004 | `engineering_validated` 写在 manifest 主体，但没有等价的 `validation_chain`（如 `bench_correlation_required`、`material_card_source`）字段 | `sim/pyfluent_workflow.py:95-110` | P2 | manifest schema 应至少补 `cad_source_sha256`、`material_card_path`、`mesh_summary` 字段，避免成为下一个“看起来很全的 manifest 但没有溯源” |

### 4.3 主线吸收建议

把 PyFluent 工作流 cherry-pick 进 `claude-mainline` 之前，先做：

1. 在 `requirements.txt` 与 `pyproject.toml` 标 `ansys-fluent-core` 为 optional extras（避免 CI 强依赖商业 license）；
2. `models/scheme_simulation_coverage.json` 中 S04/S05/S06/S11 的 `next_simulation_step` 显式引用 PyFluent 入口（目前只写 “FEA-derived”）；
3. 增加 `tests/test_pyfluent_dry_run.py`：只跑 `load_config()` 路径，永不调用 Fluent；
4. 评审线的 `codex-docs/toolchain_selection_and_github_references.md` 同步迁到 `claude-docs/`。

---

## 5. 文档级评审：Codex 评审包

### 5.1 `claude_development_review_2026-05-15.md`（10 条 CDR）

Opus 复审结论：**全部成立**。其中：

| CDR | Opus 判定 | 当前 `claude-mainline` 状态 | 注 |
|---|---|---|---|
| CDR-001 分支分叉 | 成立 | **未消化**：评审线 17 个 unique 提交未合并；主线 30 个 unique 提交（含 r02/r03 收敛）评审线没看到 | 见 §6 |
| CDR-002 测试污染 | 成立 | **未消化**：本次工作树仍有 5 处 untracked + 1 处 modified | 见 §7 |
| CDR-003 `combined_losses()` 语义错误 | 成立 | **未验证修复**：未读到 `sim/iron_loss.py` diff | OPUS-2026-05-25-010 |
| CDR-004 Bertotti `freq_max_hz` 未执行 | 成立 | 同上 | OPUS-2026-05-25-011 |
| CDR-005 EXP-011 ratio 混合分子分母 | 成立 | 同上 | OPUS-2026-05-25-012 |
| CDR-006 Flux LUT vs MotorParams 不一致校验 | 成立 | 同上 | OPUS-2026-05-25-013 |
| CDR-007 Claude docs 入口滞后 | 成立 | **部分消化**：`models/scheme_simulation_coverage.json` 已更新；`claude-docs/README.md` 与 `handoff_context.md` 未确认 | OPUS-2026-05-25-014 |
| CDR-008 wiki/HTML 展示入口滞后 | 成立 | 同上 | OPUS-2026-05-25-015 |
| CDR-009 `.claude/` 与 worktree 隔离 | 成立 | **未消化**：`.claude/worktrees/` 仍 untracked，14 个 worktree 分支仍在 | OPUS-2026-05-25-016 |
| CDR-010 PyFluent 主线命运 | 成立 | **未消化**：仍在评审线 | 见 §4.3 |

### 5.2 `artifact_mutation_review_2026-05-15.md`（4 条 AMR）

Opus 复审结论：**全部成立，且 P0 项目级影响**。`run_control_lut_generator.run()` 默认输出 `models/control_lut.json` + `generated_at = datetime.now(...)` 仍未拆分注入点，正常 `pytest` 仍会污染 tracked artifact。建议把 AMR-001 到 AMR-004 拆成 4 张 issue 单独排期，参见 [`codex_progress_action_register.json`](./codex_progress_action_register.json)。

### 5.3 `goal_traceability_audit_2026-05-15.md`

价值评估：**高**。这是当前仓库中唯一一份 “评审目标 ↔ 产物” 的覆盖矩阵，明确写出 “持续目标不能被关闭” —— 阻断了 “一次评审完成 + 关单” 这种危险叙事。

未来扩展建议：增加 `wiki_html_sync_review_*.md` 与 `reports_audit_*.md`（Codex 自己已在 §5 列为 weakly-covered），Opus 同意优先级。

### 5.4 `codex-docs/toolchain_selection_and_github_references.md`

价值评估：**高**。两点建议：

1. §3 GitHub 项目清单缺少 “最近一次校验日期”；建议在每条增加一列，避免知识库随上游 archive/rename 漂移；
2. §5 把 EXP-001..010 → Maxwell/Motor-CAD 升级映射写得很扎实，但缺一行 “何时不应该升级到 FEA”（例如 S07 memory motor 仍是 research pool，跳过 FEA 直接做磁化脉冲电路 prototype 更高效）。

---

## 6. 跨分支差异（再确认 CDR-001）

详见 [`branch_integration_strategy.md`](./branch_integration_strategy.md)。摘要：

```text
claude-mainline ↑ 30 commits 独有
codex-review-line ↑ 17 commits 独有

claude-mainline 独有的最大块：
  e7edde3 feat(control): 控制 LUT 生成器和 schema
  a8169fb feat(control): 控制 LUT 安全边界归因
  391ce20 feat(exp011): 铁损 Bertotti
  e52c3b4..1e26568..02fadda..a0fd057 r01→r02→r03 全链路
  d7abf6e r03 提示词成熟度同步

codex-review-line 独有的最大块：
  951657a Codex deep review 初稿
  d2be095 EXP-005..010 数值推演（已被 claude-mainline e52c3b4 系列覆盖/重做）
  6f0ae80 仿真闭环 baseline
  4e0c489 PyFluent 工作流（独立能力，必须迁移）
  14462e9..90d2a66..cfda256..674388b Codex 知识库
  69b40b4..dd47e70..6b137bf 2026-05-15 评审包
```

关键判断：

- **PyFluent 工作流是评审线唯一独立能力**，必须 cherry-pick 进主线；
- **2026-05-15 Codex 评审包 + `codex-docs/`** 应该作为 `claude-mainline` 上的 read-only 证据迁入，而不是用 `git merge codex-review-line`（会引入 `d2be095` 等已被主线 superseded 的实验产物）；
- 主线已经走完了 r02→r03 闭环，反向 merge 主线到评审线会让评审线一次性激增 30 个 commit，风险高于价值。

建议路径：**单向 cherry-pick + 文件级迁移**，详见集成策略文档。

---

## 7. 工作树健康（再确认 CDR-002 + AMR-001..004）

`git status` 实测：

```text
On branch claude-mainline
Your branch is ahead of 'origin/claude-mainline' by 27 commits.

Changes not staged for commit:
  modified:   codex-review/docs/README.md

Untracked files:
  .claude/worktrees/
  codex-docs/wereview.md
  codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/
  codex-review/docs/v2_r02_sim_image_generation_handoff_2026-05-20.md
  review-pr/
```

| 路径 | 应有动作 |
|---|---|
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/` | **必须提交**：这是 Claude 主线 r03 提示词重写的直接源头，缺它意味着 r03 prompts 失去了打回上下文 |
| `codex-review/docs/v2_r02_sim_image_generation_handoff_2026-05-20.md` | **必须提交**：handoff 文档，已经被 `codex-review/docs/README.md` 入口表引用 |
| `codex-review/docs/README.md` (modified) | **必须提交**：上面两项的入口已加进 README |
| `codex-docs/wereview.md` | **审查后决定**：文件为空 / 占位；建议删除或并入 `codex-docs/handoff_context.md` |
| `review-pr/` | **不应进入仓库**：内含两份外部参考 HTML + `_files` 资源（共 4 项），会污染工程证据链。建议加 `.gitignore` 或迁到 `experiments/_external_refs/` 并显式登记来源 |
| `.claude/worktrees/` | **不应进入仓库**：14 个 agent worktree 是本地缓存，建议在 `.gitignore` 中加 `.claude/worktrees/` 与 `.claude/` 子项 |

AMR 修复未推进的具体证据：

- `sim/run_control_lut_generator.py:215-235` 仍写 `datetime.now(timezone.utc).isoformat()` 与默认 `output_path = ROOT / "models" / "control_lut.json"`。
- `tests/test_scheme_p0_lut_acceptance.py:131-137` 通过 `kwargs["output_path"] = tmp_path / ...` 局部绕过了污染，但其他 runner 的默认行为没改，正常单独跑 `pytest tests/test_control_lut_generator.py` 仍会写 `models/control_lut.json`。

---

## 8. r02 / r03 一致性现场抽查

### 8.1 r03 提示词包 × `engineering_validated=false`

`tests/test_r03_prompt_maturity.py` 强约束：

```python
EXPECTED_SCHEMES = {f"S{n:02d}" for n in range(1, 13)}
MATURITY_MARKERS = ("engineering_validated = false", "evidence_gap")
PROXY_MARKERS = ("proxy", "synthetic fixture", "sample-only")
FORBIDDEN_PHRASES = {
    "fea-backed validation", "green engineering candidate gate",
    "engineering recommendation", "engineering_validated = true",
    "validated = true", "production release approved",
    "manufacturing release approved", "released in green",
    "engineering gate decision",
}
```

Opus 现场验证：

```text
python -m pytest tests/test_r03_prompt_maturity.py tests/test_scheme_p0_lut_acceptance.py \
   tests/test_scheme_experiment_acceptance.py tests/test_scheme_simulation_coverage.py -q
→ 42 passed in 235.85s
```

抽查样本（`engineering/v2/scheme-02/prompts/V2-S02-PROMPT-r03-production_drawing_pack.md:14-27`）：

- 图 1 / 2 / 3 / 4 每条 standalone `Prompt:` 都包含 `engineering_validated = false; evidence_gap`；
- 图 3 显式标注 `r02 id/iq jump soft gate <= 60 A; r03 target <= 30 A` —— 没有把 60 A 通过宣称为 30 A 达成；
- 图 4 顶部 callout: `proxy only; engineering_validated = false; evidence_gap`。

**判定：通过。**

### 8.2 r02 sim_binding × 通用 harness

`tests/test_scheme_p0_lut_acceptance.py:30-35` 把 S01/S02/S04/S11 参数化：

```python
P0_SCHEMES = [
    ("S01", "scheme-01", "V2-S01-PARAM-sim_binding-r02.json"),
    ("S02", "scheme-02", "V2-S02-PARAM-sim_binding-r02.json"),
    ("S04", "scheme-04", "V2-S04-PARAM-sim_binding-r02.json"),
    ("S11", "scheme-11", "V2-S11-PARAM-sim_binding-r02.json"),
]
```

每个 binding 必须通过：

- strong checks：`metadata.generator_version.regex`、`model_source.model_type.enum`、`feasibility_map.feasible_points_min`、`validation.torque_discontinuity_at_transitions_nm_max`、`metadata.demag_limit_present`；
- soft checks（warn）：`search_not_converged_max`、`demagnetization_risk_max`、`voltage_exceeded_ratio_max`、`id_jump_a_max`、`iq_jump_a_max`；
- 独立断言：`engineering_validated is False`；
- DVP id 必须匹配 `S<id>-DV-NNN`。

S04 的 binding（`engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json:18-26`）将 `feasibility_map.feasible_points_min` 限定为 `1`，并在 `model_maturity: synthetic_fixture` + `fixture_limits.not_allowed_claims` 写明四条禁止陈述：

```json
"not_allowed_claims": [
  "FEA-derived LUT validation",
  "bench-correlated flux map",
  "production control LUT release",
  "engineering validation"
]
```

**判定：通过。这是 “smoke gate 必须 ≥ 1 但禁止被宣称为 LUT 验证” 的工程边界，护栏到位。**

### 8.3 P1/P2 通用 harness

`tests/test_scheme_experiment_acceptance.py:80-117` 实现了 suffix DSL：`.equals` / `.regex` / `.enum` / `.count_min` / `.count_max` / `.min` / `.max` / `.present` / `.absent`，让 8 个 P1/P2 方案在不引入新 Python 代码的情况下绑定到既有 runner。

抽查 S12（`engineering/v2/scheme-12/parameters/V2-S12-PARAM-sim_binding-r02.json:10-19`）：

```json
"expect": {
  "experiment.equals": "exp_010_weighted_efficiency_pareto",
  "engineering_validated.equals": false,
  "cycles.count_min": 1,
  "candidates.count_min": 1,
  "cycle_winners.present": true,
  "pareto_front.present": true,
  "row_count.min": 1,
  "csv_path.present": true
}
```

`engineering_validated.equals=false` 是 strong check 之一 —— 把 “runner 输出 engineering_validated=true” 这种回归一次性堵死。**判定：通过。**

---

## 9. Opus 视角的新发现

### OPUS-2026-05-25-005：r02 sim_binding 中 `feasible_points_min` 在 P0 与 smoke 之间没有明确分级
严重度：P2 / 状态：open  
证据：S02 = 60、S04 = 1、S11 = 60、S01 = 60（默认 P0）；S04 的 1 与其余的 60 没有在 `models/scheme_simulation_coverage.json` 或 `engineering/v2/scheme-04/README.md` 中显式写为 “smoke vs production” 两挡。  
建议：在 `models/scheme_simulation_coverage.json` 增加 `feasible_points_gate_class` 字段（`smoke` / `proxy` / `production_target`），或在 `sim_binding-r02.json` 增加 `gate_class` 字段同步标识。否则未来人会拿 S04 的 1 推 S02 应该是 1 / 反之。

### OPUS-2026-05-25-006：r02 sim binding 没有 schema 验证
严重度：P1 / 状态：open  
证据：12 份 `V2-S*-PARAM-sim_binding-r02.json` 都遵循同一形状（`schema_version`、`scheme_id`、`entry`、`function`、`kwargs`、`expect`、`strong_checks`、`soft_checks`、`dvp_mapping`、`open_items`、`related_artifacts`），但没有 JSON schema 或 dataclass 做形状校验；新增 binding 时打字错误会被 `tests/test_scheme_experiment_acceptance.py` 在运行 runner 时才发现。  
建议：在 `models/` 增加 `sim_binding_schema.json`，并在 `tests/test_scheme_simulation_coverage.py` 加 “12 份 binding ↔ schema” 校验。

### OPUS-2026-05-25-007：r03 prompt pack 的 `## 图 N：` 顺序假定固定，但 `tests/test_r03_prompt_maturity.py` 未校验图编号
严重度：P2 / 状态：open  
证据：`tests/test_r03_prompt_maturity.py:62-74` 强约束每包 4 条 `Prompt:`，但没要求 “图 1 / 图 2 / 图 3 / 图 4” 编号；若有人按 “图 1 / 图 2 / 图 5 / 图 7” 排版仍能通过。  
建议：增加 prompt pack 顶层 figure id 校验，与 r02 sim 批包的 T01/T03/T07/T08 命名对齐。

### OPUS-2026-05-25-008：r02 sim 批包仅覆盖 S02 / S04 两个 prompt pack
严重度：P1 / 状态：open  
证据：`codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/` 当前只有 `V2-S02-...` 与 `V2-S04-...`；`simulation_anchor_matrix.json` 列了全部 12 方案的规则，但 prompt pack 尚未生成 S01/S03/S05..S12。Claude 主线已经做了全 12 方案的 r03 prompt pack，但 “r02 sim 批包 → r03 prompt pack” 的对照链不完整。  
建议：把 12 方案的 r02 sim prompt pack 补齐（或显式声明 r03 已完全替代 r02 sim 批包），写入 `codex-review/docs/README.md`。

### OPUS-2026-05-25-009：`review-pr/` 目录含外部 HTML 与 `_files` 资源，正在被 git 视为可提交内容
严重度：P1 / 状态：open  
证据：`git status` 显示 `review-pr/` 为 untracked，内含两份中文 HTML（驱动电机扁线/油冷/多合一、奇瑞可变磁通电机）与对应 `_files/` 资源（可能数百 KB-数 MB）。任何人误执行 `git add .` 都会把这些外部参考拉进仓库。  
建议：立即 `.gitignore` `review-pr/`，并把这两份资料迁到 `claude-docs/external_refs/` 或 `experiments/_external_refs/`，同时在 `evidence_manifest.md` 记录来源 URL 与 fetch 日期。

### OPUS-2026-05-25-010：`sim/iron_loss.py::combined_losses` 语义错误仍未修
严重度：P1 / 状态：open  
证据：Codex CDR-003。Opus 未在 `claude-mainline` 上看到 commit `fix(iron-loss): rename combined_losses return / 修复` 等修正记录。  
建议：参考 Codex 给的修复建议，把返回值改名为 `iron_loss_fraction` 或接收机械输出功率并返回真效率；同步修 `tests/test_iron_loss.py` 的语义断言。

### OPUS-2026-05-25-011：Bertotti `freq_max_hz` 仍未在运行时执行
严重度：P1 / 状态：open  
证据：Codex CDR-004。EXP-011 在 18 000 rpm × 4 pole pairs ≈ 1200 Hz 工况下超出默认 400 Hz 有效范围。  
建议：在 `sim/iron_loss.py::bertotti_iron_loss_per_phase` 增加 `freq_hz > coeffs.freq_max_hz` 标记，`sim/run_iron_loss_experiment.py` 在 summary 输出 `out_of_range_speed_points` 字段。

### OPUS-2026-05-25-012：EXP-011 损耗比指标分子分母统计口径不一致
严重度：P2 / 状态：open  
证据：Codex CDR-005。  
建议：改为 `avg_iron_loss_target / avg_copper_loss_target` 或输出逐点 ratio 的均值与最大值。

### OPUS-2026-05-25-013：Flux LUT 与 MotorParams 一致性未校验
严重度：P1 / 状态：open  
证据：Codex CDR-006。`sim/search.py` 的 nonlinear 分支使用 `flux_lut.pole_pairs`，但电压路径仍使用 `params.rs_ohm`，没有验证 `params.pole_pairs == flux_lut.pole_pairs`。  
建议：在 `sim/run_control_lut_generator.run` 入口（model_type=nonlinear_flux_lut 分支）增加 `assert params.pole_pairs == flux_lut.pole_pairs` 与 `flux_lut.unit_convention == params.unit_convention`；在 LUT JSON 增加 `motor_id` 字段做 round-trip 校验。

### OPUS-2026-05-25-014：`claude-docs/` 入口仍可能停留在 EXP-001..004
严重度：P2 / 状态：open（Codex CDR-007 同类）  
证据：未在 `claude-docs/README.md` 与 `handoff_context.md` 看到对 EXP-011、控制 LUT、`sim_binding-r02.json` 的入口更新；现场存在 `claude-docs/maxwell_motorcad_simulation_plan.md`、`toolchain_selection_and_github_references.md` 等未跟踪修改。  
建议：用一次性 “docs sync PR” 把 EXP-005..011 与 r02/r03 链路登记到 `claude-docs/README.md`、`evidence_manifest.md`、`simulation_traceability.md`，并刷新 `snapshots/` 哈希。

### OPUS-2026-05-25-015：wiki/HTML 展示入口未跟随 r02/r03 更新
严重度：P2 / 状态：open（Codex CDR-008 同类）  
证据：`controllable_flux_motor_kb.html` 与 `wiki/controllable_flux_motor_research_plan.md` 当前评审未抽样比对；如果 Codex CDR-008 给出的现状还有效，那么 r02 sim_binding / r03 prompt pack / 12 方案 acceptance harness 都没被 HTML 入口反映。  
建议：把 HTML/wiki 升级合并到 OPUS-2026-05-25-014 的 docs sync PR；并增加 `tests/test_docs_links.py` 或 link-check 脚本，校验 HTML 入口对 `engineering/v2/scheme-*/...` 路径的引用始终命中真实文件。

### OPUS-2026-05-25-016：`.claude/worktrees/` 与 14 个 agent worktree 分支应迁出仓库
严重度：P2 / 状态：open（Codex CDR-009 同类）  
证据：`git branch -a` 列出 14 个 `worktree-agent-*` 分支，本地存在 `.claude/worktrees/` 未跟踪目录。  
建议：在 `.gitignore` 增加 `.claude/worktrees/`、`.claude/cache/`、`.claude/sessions/`；过期 worktree 分支批量删除（前提：先核对没有未合并提交）。

### OPUS-2026-05-25-017：codex-review 与 claude-review 缺少“互引证据”自动校验
严重度：P3 / 状态：open  
证据：`codex-review/docs/README.md` 引用 `../../claude-review/docs/2026-05-15/...`，反向 `claude-review/README.md` 引用 `../engineering/v2/README.md` 等；目前没有 CI 检查这些跨包链接是否仍然命中。  
建议：在 `tests/` 增加链接体检脚本（grep markdown 中的相对路径，逐一 `Path.exists()`）。

---

## 10. 优先行动汇总

| 优先级 | 行动 | 负责类别 | 关联 |
|---|---|---|---|
| **P0** | 提交 `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/`、`v2_r02_sim_image_generation_handoff_2026-05-20.md`、`codex-review/docs/README.md` modified 三项 | git | §7、本次任务必做 |
| **P0** | `.gitignore` 增加 `.claude/worktrees/`、`review-pr/`；删除/迁出 `codex-docs/wereview.md` | git | OPUS-2026-05-25-009、016 |
| **P0** | 用 single cherry-pick 把 PyFluent 工作流（`sim/pyfluent_workflow.py` + runner + 2 个 test）合到 `claude-mainline` | code | §4.3、CDR-001、010 |
| **P0** | `run_control_lut_generator.run` 增加可注入 `generated_at` / `output_path` 必传机制；测试统一走 `tmp_path` | code | AMR-001/002/003 |
| **P1** | 修 `combined_losses()` 语义、Bertotti `freq_max_hz`、EXP-011 ratio、Flux LUT 一致性校验 | code | CDR-003/004/005/006、OPUS-2026-05-25-010/011/012/013 |
| **P1** | `claude-docs/` 入口与 wiki/HTML 同步到 EXP-011 + r02/r03 | docs | CDR-007/008、OPUS-2026-05-25-014/015 |
| **P1** | 补齐 S01/S03/S05..S12 r02 sim 批包（或宣布 r03 全面替代并归档 r02 sim 批包） | docs | OPUS-2026-05-25-008 |
| **P1** | 增加 `models/sim_binding_schema.json` + 校验 | code | OPUS-2026-05-25-006 |
| **P2** | r03 prompt pack 增加 figure id 校验 | tests | OPUS-2026-05-25-007 |
| **P2** | `feasible_points_gate_class` 字段同步到 coverage + binding | docs/code | OPUS-2026-05-25-005 |
| **P2** | PyFluent runner 增加 `--dry-run`、manifest in finally、boundary key allow-list | code | OPUS-2026-05-25-001/002/003/004 |
| **P3** | codex-review × claude-review 跨包链接体检 | tests | OPUS-2026-05-25-017 |

---

## 11. 下一轮评审建议

1. PyFluent cherry-pick 后立刻补一份 `opus-review/docs/<date>/pyfluent_mainline_integration_review.md`，记录 license/CI/test 隔离三层情况；
2. AMR-001..004 修复后跑 `pytest && git diff --exit-code` 体检，并把结果固化为 CI step；
3. 完成 12 方案 r02 sim 批包（或归档）后，把 `simulation_anchor_matrix.json` 与 r03 prompt pack 做一次双向 round-trip 审计；
4. Codex 下一轮若新增 evidence，请先把 `2026-05-15` 系列报告标记为 supersedes / superseded，避免后续读者把 5/15 评审当作最新事实。

---

## 12. 评审判定

**Codex 当前开发进度：方向正确，节奏合适，护栏到位。阻塞点不是评审深度，而是落地动作。**

- Codex 的评审包 + r02 sim 批包 + `codex-docs/` 已经把项目从 “r0 概念 → r02 提示词 → r03 仿真合同” 的三层结构稳定下来；
- Claude 主线已经按 Codex 打回意见把 r03 prompt pack 与 P0/P1 通用 acceptance harness 落到 12 方案；
- 仍卡在 4 个 Codex 提出但未消化的 P0/P1 修复（PyFluent 迁移、测试污染根治、`combined_losses()` / Bertotti / Flux LUT 一致性、docs/wiki/HTML 入口同步）。

只要把本报告 §10 的 P0 行动在下一次 PR 内合并，Codex 当前阶段的开发可以认定为“达到下一里程碑准入”。不能在这之前把任何方案描述为“工程验证通过”。`engineering_validated=false` 这条护栏在本评审中再次得到确认。
