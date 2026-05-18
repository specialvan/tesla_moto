# V2 自动化与成熟度闭环 handoff

日期：2026-05-19  
分支：`claude-mainline`  
上一提交：`a0fd057 feat(r02/r03): 收敛Codex打回后的生产图纸成熟度闭环`

## 1. 当前状态

本轮在 Codex 打回“工程图纸生产化未完成”后，已将项目口径从“真实生产图纸完成”收敛为分级成熟度闭环：

- `concept_drawing`
- `parameter_sheet`
- `source_design_file`
- `simulation_input`
- `manufacturing_release`

当前全局默认结论仍是：

```json
{
  "engineering_validated": false,
  "production_drawing_ready": false,
  "manufacturing_release_ready": false
}
```

任何后续 agent 不应把 PNG、prompt、Markdown 参数草案、proxy simulation 或 synthetic fixture 写成正式生产发布证据。

## 2. 已新增只读审查自动化资产

### 2.1 项目技能

新增：`.claude/skills/v2-maturity-review/SKILL.md`

用途：审查 V2 文档、图档、仿真覆盖矩阵、Codex/Claude 评审包中的成熟度口径，防止过度声明。

重点规则：

- S02：`60 A` 是 r02 proxy soft gate；`30 A` 是 r03 production target。
- S04：`models/flux_lut_sample.json` 是 `synthetic_fixture`，只证明 schema/runtime smoke binding。
- 图像：PNG/prompt/sidecar 是 concept illustration，外部上传必须脱敏并审批。
- `gpt-image-2/config/model.json` 不得包含真实 endpoint 或 API key。

新增：`.claude/skills/evidence-sync/SKILL.md`

用途：在新增评审/仿真/工程文档后，同步 `claude-review/docs`、`wiki`、HTML、`claude-docs/evidence_manifest.md`、`codex-review/docs/README.md` 和 scheme README。

### 2.2 项目子代理

新增：`.claude/agents/maturity-consistency-reviewer.md`

用途：并行审查工程文档与评审包中的成熟度一致性和生产化过度声明。

新增：`.claude/agents/schema-test-contract-reviewer.md`

用途：审查 JSON schema、fixture、生成模型输出和 pytest 断言之间的契约漂移。

推荐后续使用方式：

- 大规模文档或模型 JSON 变更后，先跑 `maturity-consistency-reviewer`。
- schema/sample/test 任一变化后，跑 `schema-test-contract-reviewer`。
- 提交前仍应跑 security/code review，尤其检查密钥和外部图像端点。

## 3. 关键文件入口

### 成熟度与证据矩阵

- `claude-review/docs/2026-05-15/v0.5_true_production_drawing_deliverables_matrix.md`
- `claude-review/docs/2026-05-15/v0.5_true_production_drawing_deliverables_matrix.html`
- `wiki/v2_true_production_drawing_deliverables_wiki.md`
- `models/scheme_simulation_coverage.json`
- `tests/test_scheme_simulation_coverage.py`

### S02 阈值口径

- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-control-r02.md`
- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-verification-r02.md`
- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json`
- `tests/test_scheme_02_lut_acceptance.py`

### S04 synthetic fixture

- `engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json`
- `models/flux_lut_sample.json`
- `models/flux_lut_schema.json`
- `tests/test_nonlinear_flux_lut.py`

### 图像工程包

- `gpt-image-2/README.md`
- `gpt-image-2/config/model.json`
- `gpt-image-2/config/model.local.example.json`
- `gpt-image-2/gpt_image2/config.py`
- `gpt-image-2/gpt_image2/generate.py`

注意：`gpt-image-2/config/model.local.json`、`gpt-image-2/outputs/**` 不应提交。

## 4. 已验证命令

最近一次提交前通过：

```bash
python -m pytest tests/test_nonlinear_flux_lut.py tests/test_scheme_simulation_coverage.py tests/test_scheme_02_lut_acceptance.py tests/test_control_lut_generator.py
```

结果：`48 passed`

并发保护验证：

```bash
PYTHONPATH=gpt-image-2 python -m gpt_image2.generate --all --priority P0 --dry-run --concurrency 2
```

预期：exit 2，报错 `external image generation is approval-gated and must run with --concurrency 1`。

## 5. 后续 agent 推荐推进顺序

1. 用 `maturity-consistency-reviewer` 扫描本轮新增或修改文档，找残留过度声明。
2. 用 `schema-test-contract-reviewer` 检查 JSON/schema/test 是否仍一致。
3. 若继续推进生产图纸真实化，不要再写 Markdown 假冒 CAD/EDA/FEA 证据；应明确需要真实源文件：
   - PCB/EDA：原理图、layout、Gerber、BOM、DRC/ERC 报告。
   - CAD：STEP/参数化模型、尺寸链、公差、材料、装配约束。
   - FEA：FEA 输入、网格/材料/边界条件、残差、温度切片、验证报告。
   - HIL/bench：测试台架、数据记录、通过/失败判据。
4. 所有新增证据同步到：
   - `claude-review/docs/<date>/`
   - `claude-docs/evidence_manifest.md`
   - `wiki/` 或 HTML 页面
   - 相关 `engineering/v2/scheme-XX/README.md`
5. 提交时显式暂存文件，避免 `git add -A` 把 `.claude/worktrees/`、`review-pr/`、生成 PNG 或本地配置带入。

## 6. 当前待注意本地项

上一轮提交后仍有未跟踪本地项：

- `.claude/`：本轮现在会新增技能/代理；只应提交 `.claude/skills/**` 和 `.claude/agents/**`，不要提交 `.claude/worktrees/**` 或 `settings.local.json`。
- `codex-docs/wereview.md`：未确认是否属于本轮交付，默认不要提交。
- `review-pr/`：默认不要提交。

显式 denylist：

- `.claude/settings.local.json`
- `.claude/worktrees/**`
- `review-pr/**`
- `gpt-image-2/outputs/**`
- `gpt-image-2/config/model.local.json`
- `.env*`，安全示例文件除外

## 7. 建议下一步

如果继续优化自动化，建议先做只读评审闭环，不急着配置 Hook：

- 运行两个新子代理做独立审查。
- 根据结果补齐 `claude-review/docs/2026-05-19/` 的自动化说明。
- 仅显式暂存 `.claude/skills/**`、`.claude/agents/**` 和本 handoff 文档。
