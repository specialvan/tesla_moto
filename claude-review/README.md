# Claude Review 工程包

## 1. 包定位

`claude-review` 用于沉淀 Claude 对 Codex 开发线返回的评审意见、事实核验、处置矩阵和后续执行清单。

当前包不是新的仿真实现，也不是把 Codex 代码直接合并到 Claude 主线的入口。它的作用是：

- 保存原始评审；
- 把评审意见转成可执行工程事项；
- 标明哪些反馈在当前 `claude-mainline` 已经满足；
- 标明哪些反馈只在未来合并 Codex 分支时生效；
- 防止 v0 参数化模型被误读为工程验证结论。

## 2. 文件入口

| 文件 | 用途 |
|---|---|
| `codex_development_review.md` | Claude 返回的原始评审 |
| `codex_review_deep_triage.md` | 对评审意见的逐条核验和深度处置 |
| `review_action_register.json` | 机器可读的行动项登记表 |

## 3. 当前核验结论

当前 `claude-mainline` 工作树中：

- 不存在 `sim/control_search.py`；
- 不存在 `experiments/exp_001_linear_dq/run.py`；
- 不存在 `tests/test_control_search.py`；
- 不存在 `codex-reviwe/phase1_linear_dq_implementation_plan.md`；
- 当前只落地 EXP-001 到 EXP-004；
- 覆盖目录状态为 6 个 `passed_numeric_simulation`、5 个 `needs_next_numeric_model`、1 个 `passed_architecture_verification`。

因此评审中关于“重复 EXP-001 入口”的问题，在当前 Claude 主线并未实际存在；但它对未来 Codex 分支合并仍是硬约束。

## 4. 处理原则

1. 文档可吸收，重复 runner 不直接吸收。
2. 测试意图可吸收，但要绑定 `sim/search.py` 和 `sim/run_linear_dq_experiment.py`。
3. EXP-005 到 EXP-010 若要进入 Claude 主线，必须按主线接口、主线测试和覆盖目录重做闭环。
4. 所有 v0 结果必须保留 `engineering_validated=false` 或同等限制说明。
