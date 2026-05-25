# 分支集成策略

评审日期：2026-05-25  
作者：Opus 4.7 (1M)  
目标：把 `codex-review-line` 与 `claude-mainline` 当前的能力收敛到一条线，不丢 PyFluent、不丢 r02/r03 闭环、不引入已被覆盖的旧实验产物。

---

## 1. 当前分叉态势

```text
共同祖先：6f0ae80 feat: 建立Claude主线可控磁通量电机仿真闭环

claude-mainline (HEAD d7abf6e)
  ▲ 30 commits unique
  e7edde3 → a8169fb → 391ce20 → 1039866 → 09b4a84 → ...
  → c43e9bb → 8fe0b02 → e52c3b4 → 1e26568 → 02fadda → a0fd057
  → 26df963 → 965c59c → 33be7a6 → ee7f34b → 03b0a63
  → 8aa5199 → 8f01644 → 5c7314c → 7c4e502 → e06c1fe → d7abf6e

codex-review-line (HEAD 6b137bf)
  ▲ 17 commits unique
  951657a → e16af86 → 49f2c53 → 5bd82b6 → a26ec32 → 3f49d99
  → 8666172 → fb414c1 → 9b84e83 → 2e5f36c → 4f3c912 → 57f795d
  → 9a85004 → e5d2ca7 → ab9ce2c → 5b0995c → 7b9887e → 1b35cda
  → cec8077 → 19ceb13 → d2be095 → b3afc6f → 9bc4dd9 → 27bfe15
  → 21fc948 → 37de045 → 674388b → 8f3312d → 14462e9 → 90d2a66
  → cfda256 → 4e0c489 → 69b40b4 → dd47e70 → 6b137bf
```

> 注：上面 codex-review-line 列出的全部独有提交中，有约一半是 EXP-005..010 数值入口的早期实现 + 实验输出快照 chore；这些已经被 `claude-mainline` 重新实现（更结构化的 sim/* runner、coverage JSON、acceptance harness）覆盖，不应整段 merge。

---

## 2. 不推荐的合并方式

### 2.1 `git merge codex-review-line` → `claude-mainline`

风险：

- 会引入 `d2be095 feat: 补齐Claude主线EXP-005至EXP-010数值推演` 与之后的 chore 提交，但主线已经用 `e52c3b4..1e26568..02fadda..a0fd057` 重做这件事；
- 主线的 `sim/run_*` 与 `tests/test_scheme_*` 与评审线 `sim/run_*` 在 EXP-005..010 上很可能形成内容冲突，被迫人工选择 hunk；
- `codex-reviwe/`（拼写错误）目录会被引入主线，需要额外清理；
- 风险/收益严重不对等。

### 2.2 `git rebase claude-mainline` onto `codex-review-line`

风险：

- 把主线 30 个提交重新基于评审线，会丢失 GitHub 上的远端 `origin/claude-mainline` 引用；
- 评审线分支策略本来就是 “Codex 评审 + Codex 知识库”，主线被强行 rebase 到这里会让叙事混乱。

---

## 3. 推荐的集成方式：单向 cherry-pick + 文件级迁移

### 3.1 必须 cherry-pick 的能力

只有 PyFluent 工作流是评审线独立能力，必须以原子方式合到主线：

```bash
# 在 claude-mainline 上执行
git cherry-pick 4e0c489
```

预期产物：

- `sim/pyfluent_workflow.py`（159 行）
- `sim/run_pyfluent_workflow.py`（80 行）
- `tests/test_pyfluent_workflow.py`（99 行）
- `tests/test_run_pyfluent_workflow.py`（44 行）

冲突预期：低（这 4 个文件主线没有同名文件）。

cherry-pick 后必须立即做的：

1. 在 `pyproject.toml` 增加 `ansys-fluent-core` 为 optional extras（`[project.optional-dependencies]` 中加 `fluent = ["ansys-fluent-core"]`）；
2. 在 `models/scheme_simulation_coverage.json` 中 S04/S05/S06/S11 的 `next_simulation_step` 显式引用 PyFluent 入口；
3. 新增 `tests/test_pyfluent_dry_run.py`，只跑 `load_config()` 路径，永远不调用 Fluent；
4. 同步更新 `claude-docs/toolchain_selection_and_github_references.md`（或直接迁移 `codex-docs/` 的同名文件）。

### 3.2 文件级迁移（非 cherry-pick）

`codex-docs/` 与 `codex-review/docs/*_2026-05-15.md` 评审包：建议用 “文件复制 + 主线提交” 方式迁移，避免把评审线 14 个 chore/快照提交也一并拉进主线。

具体步骤：

```bash
# 在 claude-mainline 上执行
mkdir -p codex-docs/snapshots/{html,wiki}

# 评审线复制（git show + write）
git show codex-review-line:codex-docs/README.md > codex-docs/README.md
git show codex-review-line:codex-docs/evidence_manifest.md > codex-docs/evidence_manifest.md
git show codex-review-line:codex-docs/handoff_context.md > codex-docs/handoff_context.md
git show codex-review-line:codex-docs/simulation_traceability.md > codex-docs/simulation_traceability.md
git show codex-review-line:codex-docs/wiki_html_evidence.md > codex-docs/wiki_html_evidence.md
git show codex-review-line:codex-docs/toolchain_selection_and_github_references.md \
    > codex-docs/toolchain_selection_and_github_references.md
git show codex-review-line:codex-docs/snapshots/html/controllable_flux_motor_kb.html \
    > codex-docs/snapshots/html/controllable_flux_motor_kb.html
git show codex-review-line:codex-docs/snapshots/wiki/controllable_flux_motor_research_plan.md \
    > codex-docs/snapshots/wiki/controllable_flux_motor_research_plan.md

# codex-review 评审包
git show codex-review-line:codex-review/docs/claude_development_review_2026-05-15.md \
    > codex-review/docs/claude_development_review_2026-05-15.md
git show codex-review-line:codex-review/docs/evidence_index_2026-05-15.md \
    > codex-review/docs/evidence_index_2026-05-15.md
git show codex-review-line:codex-review/docs/git_state_2026-05-15.md \
    > codex-review/docs/git_state_2026-05-15.md
git show codex-review-line:codex-review/docs/review_action_register_2026-05-15.json \
    > codex-review/docs/review_action_register_2026-05-15.json
git show codex-review-line:codex-review/docs/artifact_mutation_review_2026-05-15.md \
    > codex-review/docs/artifact_mutation_review_2026-05-15.md
git show codex-review-line:codex-review/docs/artifact_mutation_matrix_2026-05-15.json \
    > codex-review/docs/artifact_mutation_matrix_2026-05-15.json
git show codex-review-line:codex-review/docs/goal_traceability_audit_2026-05-15.md \
    > codex-review/docs/goal_traceability_audit_2026-05-15.md
git show codex-review-line:codex-review/docs/goal_traceability_checklist_2026-05-15.json \
    > codex-review/docs/goal_traceability_checklist_2026-05-15.json

# 同步更新两个 README 入口表
# （手动编辑 codex-docs/README.md 与 codex-review/docs/README.md 中的入口表）
```

提交 message 建议：

```text
docs(codex): 迁入Codex 2026-05-15评审包与知识库到claude-mainline

- 迁入 codex-docs/ 全套（README/evidence_manifest/handoff/traceability/wiki_html_evidence/toolchain_selection + snapshots）
- 迁入 codex-review/docs/*_2026-05-15.md 系列（CDR + AMR + 目标审计 + 三份 JSON 登记）
- 不引入 codex-review-line 上已被主线 r02/r03 闭环覆盖的 EXP-005..010 旧实现与 chore 实验快照
- 详见 opus-review/docs/2026-05-25/branch_integration_strategy.md
```

### 3.3 评审线侧反向同步

迁移完成后，评审线（`codex-review-line`）也应当吸收 `claude-mainline` 上的 r02 sim 批包与 r03 闭环：

```bash
git checkout codex-review-line
git cherry-pick 1e26568 02fadda a0fd057 26df963 965c59c 8aa5199 8f01644 5c7314c 7c4e502 e06c1fe d7abf6e
```

或者，更稳妥：直接把 `claude-mainline` 标为 “codex-review-line 的事实源”，废弃评审线 17 个独有提交中除 PyFluent 之外的全部内容。Codex 后续若有新评审，直接基于 `claude-mainline` 派生新分支。

---

## 4. 不可破坏边界

无论选哪条集成路径，下面这些约束必须保留：

1. **`engineering_validated=false` 不翻转**：12 个 `sim_binding-r02.json`、12 个 r03 prompt pack、`tests/test_r03_prompt_maturity.py`、`tests/test_scheme_*_acceptance.py` 中任何一个文件被改成 `engineering_validated=true` 都视为评审违规。
2. **S02 的 60 A r02 soft gate 与 30 A r03 production target 必须显式区分**：合并任何 PR 前都要 grep 一次 `60 A` 与 `30 A`，确认两者没有被合并成单一阈值。
3. **S04 `flux_lut_sample.json` 是 synthetic_fixture**：禁止把 3x3 LUT 描述为 FEA-validated；`feasibility_map.feasible_points_min = 1` 是 smoke gate 而不是 production gate。
4. **PyFluent 自动化不替代 FEA 工程释放**：迁移后 PyFluent manifest 必须保留 `engineering_validated: False` 与 `validation_note`；测试不能依赖真实 Fluent license。
5. **不引入 `codex-reviwe/`（拼写错误）目录到主线**：迁移时统一改为 `codex-review/`，避免命名冲突与搜索盲区。

---

## 5. 校验脚本

集成完成后，强制跑下面四组校验：

```bash
# 1. 提示词成熟度护栏
python -m pytest tests/test_r03_prompt_maturity.py -q

# 2. P0/P1/P2 acceptance harness
python -m pytest tests/test_scheme_p0_lut_acceptance.py \
                  tests/test_scheme_experiment_acceptance.py \
                  tests/test_scheme_simulation_coverage.py -q

# 3. PyFluent dry-run（无 license）
python -m pytest tests/test_pyfluent_workflow.py tests/test_run_pyfluent_workflow.py -q

# 4. 工作树清洁度（AMR-004）
git status --short
git diff --exit-code

# 5. 跨包链接体检（OPUS-2026-05-25-017）
grep -rln "../../claude-review" codex-review/docs/ codex-docs/ \
  | xargs -I{} python -c "import pathlib, sys; \
      f=pathlib.Path('{}'); \
      txt=f.read_text(encoding='utf-8'); \
      import re; \
      [print(f'BROKEN: {f}: {m}') for m in re.findall(r'\\(\\.\\./[^)]+\\)', txt) \
        if not (f.parent / m.strip('()')).exists()]"
```

预期：1/2/3 全绿，4 干净，5 没有 BROKEN 输出。

---

## 6. 评审记录

- 本策略尚未执行；预留 Codex 或 Claude 主线下一次 PR 时落地；
- 执行后，建议在 `opus-review/docs/<执行日期>/branch_integration_result.md` 写一份事后回顾，记录实际冲突、license 检查结果与未跟踪文件清理情况。
