# Opus 介入评审 Handoff

日期：2026-05-29  
分支：`claude-mainline`  
写作基线 HEAD：`e95ff72 docs(opus): 记录r02仿真批包归档闭环`  
远端状态：`claude-mainline` 本地仍 ahead origin，最终发布/集成未执行。  
目的：让 Opus 直接从当前工作面继续评审，不需要重新从 R01 开始梳理。

## 1. 必读入口

| 入口 | 用途 |
|---|---|
| `opus-review/README.md` | Opus review 包定位、维护规则和 follow-up 索引 |
| `opus-review/docs/2026-05-25/README.md` | 2026-05-25 评审包入口 |
| `opus-review/docs/2026-05-25/codex_progress_action_register_r10_followup.json` | 当前最新有效 action register |
| `opus-review/docs/2026-05-25/branch_integration_strategy.md` | 分支发布/集成策略，当前唯一 P0 open |
| `codex-review/docs/README.md` | Codex 评审包入口，含已迁入的 2026-05-15 CDR/AMR 证据包 |
| `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/README.md` | r02-sim 局部批包已由 r03 全量包归档替代的证据 |
| `claude-docs/handoff_context.md` | Claude 主线交接入口，已补 EXP-011 与 r02/r03 成熟度口径 |

## 2. 本轮已分组提交

最新 5 个与 Opus 评审直接相关的提交：

```text
e95ff72 docs(opus): 记录r02仿真批包归档闭环
85437c8 docs(codex-review): 明确r02仿真批包由r03归档替代
ec0c299 docs(opus): 记录跨包链接闭环
6b9e7eb test(docs): 增加跨包Markdown链接体检
d9f95fe docs(codex-review): 迁入2026-05-15评审证据包
```

更早一组关键提交：

```text
a0cc8b7 feat(pyfluent): 接入离线可审计workflow
f987f8a docs(opus): 记录工作树卫生闭环
df2ef16 docs(opus): 追加R02-R06深度复评闭环
f719ffb feat(dashboard): 增加成熟度合同与决策包护栏
20146b2 docs(v2): 固化r03提示词成熟度锚点
a40225e test(v2): 统一sim_binding schema与gate分级
a4a7825 fix(control-lut): 要求显式输出路径避免污染制品
4f340c3 fix(sim): 收紧铁耗指标与Flux LUT成熟度合同
```

## 3. 当前有效 open 项

按 `codex_progress_action_register.json` + R04..R10 follow-up 重新计算，当前只剩两项有效 open：

| ID | Severity | 状态 | 下一步 |
|---|---|---|---|
| `OPUS-2026-05-25-CDR-001` | P0 | open | 本地分支仍 ahead origin；按 `branch_integration_strategy.md` 发布或集成内容化提交 |
| `OPUS-2026-05-25-DOCS-SYNC` | P1 | open | `claude-docs`、wiki、HTML 与 snapshots 仍需完整同步到 EXP-011 与 r02/r03 成熟度合同 |

已经关闭但建议 Opus 抽查的项：

- `OPUS-2026-05-25-017`：跨包 Markdown 链接校验已由 `scripts/docs_link_check.py` 和 `tests/test_docs_links.py` 固化；红灯曾暴露缺失的 2026-05-15 Codex 评审文件，现已迁入。
- `OPUS-2026-05-25-008`：r02-sim 批包不再扩展 S01/S03/S05-S12，已显式归档为 S02/S04 历史证据，由 12 份 r03 production drawing pack 全量替代。
- `OPUS-2026-05-25-PYFLUENT-001` 与 `001..004`：PyFluent workflow 已主线落地，保留 dry-run、manifest、validation_chain 和 boundary allow-list 护栏。

## 4. 最新验证证据

最近一次组合验证：

```powershell
python -m pytest tests/test_docs_links.py tests/test_pyfluent_workflow.py tests/test_run_pyfluent_workflow.py tests/test_scheme_simulation_coverage.py -q
# 14 passed in 1.02s

python -m pytest tests/test_r02_sim_batch_archival.py tests/test_r03_prompt_simulation_anchor.py tests/test_r03_prompt_maturity.py tests/test_docs_links.py -q
# 10 passed in 0.07s

python -m json.tool opus-review/docs/2026-05-25/codex_progress_action_register_r10_followup.json
# exit 0
```

更早一轮较宽验证（在 PyFluent 与 r09/r10 之前）：

```powershell
python -m pytest tests/test_repository_hygiene.py tests/test_scheme_simulation_coverage.py tests/test_r03_prompt_maturity.py tests/test_r03_prompt_simulation_anchor.py tests/test_control_lut_generator.py tests/test_scheme_02_lut_acceptance.py tests/test_scheme_p0_lut_acceptance.py tests/test_scheme_experiment_acceptance.py tests/test_iron_loss.py tests/test_nonlinear_flux_lut.py tests/test_dashboard_api.py tests/test_frontend_dashboard.py -q
# 220 passed in 553.43s
```

建议 Opus 介入后先跑：

```powershell
git status --short --branch
python -m pytest tests/test_docs_links.py tests/test_r02_sim_batch_archival.py tests/test_r03_prompt_simulation_anchor.py tests/test_r03_prompt_maturity.py tests/test_pyfluent_workflow.py tests/test_run_pyfluent_workflow.py tests/test_scheme_simulation_coverage.py -q
```

## 5. DOCS-SYNC 局部进展

本 handoff 同轮包含一组面向 `OPUS-2026-05-25-DOCS-SYNC` 的轻量交接口径更新：

- `claude-docs/README.md`
- `claude-docs/handoff_context.md`

这两处只更新交接口径：EXP-001 到 EXP-011、EXP-011 Bertotti 铁耗风险、r02 sim_binding / r03 production drawing pack 成熟度边界，以及 `engineering_validated=false`。尚未完成 `claude-docs/evidence_manifest.md`、`wiki_html_evidence.md`、wiki、HTML 和 snapshots 的完整同步，因此不能关闭 `OPUS-2026-05-25-DOCS-SYNC`。

## 6. 不可越界口径

Opus 继续评审时请重点守住以下边界：

1. `engineering_validated=false` 不能被任何 r02/r03 prompt、coverage、dashboard 或 handoff 文档翻转。
2. r02 proxy / synthetic / research_pool / parameterized linear model 不能写成 FEA、HIL、台架或量产释放结论。
3. S02 的 60 A r02 soft gate 与 30 A r03 production target 必须继续显式区分。
4. S04 `flux_lut_sample.json` 是 `synthetic_fixture`，不是 FEA-derived nonlinear flux map。
5. PyFluent workflow 是离线可审计自动化入口，不替代电磁 FEA 或冷却/材料工程验证。

## 7. 建议 Opus 下一步评审顺序

1. 读取 R10 register，确认有效 open 项是否只剩 CDR-001 与 DOCS-SYNC。
2. 抽查 r09/r10 对旧项的 `supersedes` 是否合理，尤其链接闭环和 r02-sim 归档是否有足够证据。
3. 对 `claude-docs/README.md` 与 `claude-docs/handoff_context.md` 本轮交接口径更新做 review，确认是否作为 DOCS-SYNC 的第一批局部进展。
4. 若继续推进 DOCS-SYNC，先补测试，再同步 `claude-docs/evidence_manifest.md`、`wiki_html_evidence.md`、`wiki/controllable_flux_motor_research_plan.md`、`controllable_flux_motor_kb.html` 与 snapshots。
5. 分支发布/集成只能按 `branch_integration_strategy.md` 处理；本地文档/code 闭环不等于 P0 关闭。
