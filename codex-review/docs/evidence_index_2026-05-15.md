# Claude 开发内容评审证据索引

评审日期：2026-05-15
评审包：`codex-review/docs`
当前工作区：`G:\tesla_moto-codex`
对照主线：`claude-mainline`

## 1. Git 证据

| 证据 | 当前观察 | 评审用途 |
|---|---|---|
| `git status --short --branch` | `codex-review-line...origin/codex-review-line [ahead 1]` | 当前评审线已有 1 个本地提交，包含 PyFluent 工作流入口 |
| `git log --oneline -1` | `4e0c489 feat: 增加PyFluent高保真工作流入口` | 当前评审线 HEAD |
| `git branch -a -vv` | `claude-mainline` 指向 `391ce20`，当前分支指向 `4e0c489` | 确认两条线已经分叉 |
| `git diff --stat codex-review-line..claude-mainline` | 100 个文件差异，约 9487 行新增、4026 行删除 | 判断 Claude 主线已经远超过当前评审线 |
| `git -C G:\tesla_moto status --short --branch` | `models/control_lut.json` 修改，`.claude/` 未跟踪 | 记录 Claude 主线本地未冻结状态 |
| `git diff --stat` | 当前评审线 8 个 summary 仅路径变化 | 记录测试写入绝对路径造成的工作树噪声 |

## 2. 当前评审线证据

| 路径 | 当前观察 | 评审用途 |
|---|---|---|
| `codex-docs/README.md` | 说明 `codex-review-line` 知识库定位和 EXP-001 到 EXP-010 状态 | 当前评审线知识库入口 |
| `codex-docs/handoff_context.md` | 接手说明中提示 summary/CSV 可能被测试重写 | 支撑“测试写跟踪产物”风险判断 |
| `codex-docs/evidence_manifest.md` | 记录 wiki/html 快照和活动证据 SHA256 | 评估证据冻结机制 |
| `wiki/controllable_flux_motor_research_plan.md` | 研发过程 wiki | 评审 wiki 与实验事实源是否同步 |
| `controllable_flux_motor_kb.html` | HTML 知识库 | 评审展示入口是否同步当前实验编号 |
| `sim/pyfluent_workflow.py` | 当前评审线新增 PyFluent 编排边界 | 判断 PyFluent 工作是否需要迁移到 Claude 主线 |
| `tests/test_pyfluent_workflow.py` | 当前评审线 PyFluent 测试 | 判断新增入口可测性 |

## 3. Claude 主线文档证据

| 路径 | 当前观察 | 评审用途 |
|---|---|---|
| `claude-docs/README.md` | 主线知识库入口仍强调 EXP-001、EXP-002、EXP-003、EXP-004、EXP-006 | 与 EXP-011、控制 LUT、coverage v1 对照 |
| `claude-docs/handoff_context.md` | 写明干净室边界和后续优先级 | 判断工程限制口径是否清晰 |
| `claude-docs/evidence_manifest.md` | 证据 manifest | 判断最新 EXP、LUT、铁损是否被索引 |
| `codex-review/docs/README.md` | Claude 主线已有 2026-05-14 评审工程包 | 当前新包沿用其目录意图 |
| `codex-review/docs/claude_development_deep_review_2026-05-14.md` | 已发现文档滞后、coverage 路径和 `.claude/` 风险 | 作为本轮评审起点 |
| `codex-review/docs/review_action_register.json` | 机器可读行动登记 | 对照本轮新增发现是否已覆盖 |

## 4. Claude 主线代码与测试证据

| 路径 | 当前观察 | 评审用途 |
|---|---|---|
| `sim/iron_loss.py` | EXP-011 铁损模型，含 Bertotti 与 Steinmetz 接口 | 抽查新增模型 API 和数值边界 |
| `sim/run_iron_loss_experiment.py` | 生成 `experiments/exp_011_iron_loss` summary/CSV | 评估 EXP-011 可复现性和指标计算 |
| `tests/test_iron_loss.py` | 直接写入跟踪目录 `experiments/exp_011_iron_loss` | 支撑测试污染工作树发现 |
| `sim/run_control_lut_generator.py` | 生成 `models/control_lut.json`，含 `generated_at` | 支撑控制 LUT 非确定性输出发现 |
| `tests/test_control_lut_generator.py` | 直接写入 `models/control_lut.json` | 支撑 Claude 主线 `control_lut.json` 变脏原因 |
| `sim/search.py` | 已支持可选 `flux_lut` 参数 | 评估非线性 LUT 接入共享搜索的边界 |
| `sim/nonlinear_flux_lut.py` | LUT schema、边界检查、双线性插值 | 评估 LUT 数据一致性校验 |
| `models/scheme_simulation_coverage.json` | version `2026-05-14-v1`，已索引控制 LUT 和 EXP-011 | 当前 Claude 主线结构化事实源 |

## 5. 评审边界

本轮没有切换分支、没有合并主线、没有回滚任何用户或测试产生的本地修改。对 Claude 主线的判断来自 `git show claude-mainline:<path>`、`git diff codex-review-line..claude-mainline` 和 `git -C G:\tesla_moto status`。
