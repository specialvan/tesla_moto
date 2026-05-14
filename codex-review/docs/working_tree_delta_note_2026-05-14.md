# 工作树漂移补充记录

记录时间：2026-05-14

## 1. 背景

首轮 `codex-review/docs` 评审包落盘并完成 JSON 校验后，再次执行 `git status --short --branch` 时，工作树相比评审初始核验新增了测试侧变化：

```text
M tests/test_exp_001_runner.py
?? tests/test_nonlinear_flux_lut_search.py
```

这些变化不属于本轮评审包创建动作。本轮评审只新增 `codex-review/docs/*`，没有修改 `tests/` 下文件。

## 2. 新观察到的测试变化

### 2.1 `tests/test_exp_001_runner.py`

当前 diff 显示原有 CSV 非标准数值字符串检查被替换为 EXP-001 线性基线回归断言：

- `model_scope == quasi_steady_linear_dq_grid_search`
- `no_nonlinear_flux_lut` 在 `model_limitations` 中
- 最小电流目标转矩边界保持 `6750.0 rpm`
- 最大可行正转矩边界保持 `18000.0 rpm`
- `id_zero_target_max_speed_rpm is None`

评审含义：这是有价值的回归意图，可以防止 EXP-006 非线性 LUT 搜索改动污染 EXP-001 线性基线。但它移除了 CSV 中 `inf/nan` 字符串检查，后续应确认该检查是否已由其他测试覆盖。

### 2.2 `tests/test_nonlinear_flux_lut_search.py`

新文件显示正在推进 EXP-006 从“独立 synthetic LUT 插值证明”进入“接入共享搜索接口”的方向，覆盖点包括：

- `make_candidate(..., flux_lut=lut)` 使用非线性 `lambda_d/lambda_q` 计算转矩与电压；
- `find_max_torque_feasible(..., flux_lut=lut)` 将基线 grid 裁剪到 LUT 边界；
- `find_id_zero_candidate` 与 `find_min_current_for_torque` 在样例 LUT 目标不可达时返回 `None`；
- 新 runner `sim.run_nonlinear_flux_lut_search_experiment.run` 写出 `lut_search_summary.json` 和 `lut_search_scan_results.csv`；
- 新 LUT 搜索 CSV header 与 EXP-001 scan CSV header 保持一致。

评审含义：如果对应 `sim/run_nonlinear_flux_lut_search_experiment.py`、`sim/search.py` 的 `flux_lut` 参数支持和实验产物也已落地，则 `claude-docs` 中“EXP-006 尚未接入共享控制搜索”的旧表述需要进一步更新为“已出现 LUT 接入搜索的在研/未提交变更”。

## 3. 风险

| 风险 | 说明 |
|---|---|
| 并发修改混入 | 当前工作树同时存在评审包、工具链文档修改、测试修改和 `.claude/` 未跟踪目录，提交时容易混合不相关改动 |
| 评审基线漂移 | 首轮深度评审报告以最初核验状态为基线，新测试变化可能代表后续开发已继续推进 |
| 产物路径未核验 | 新测试引用 `experiments/exp_006_nonlinear_flux_lut/lut_search_summary.json` 和 `lut_search_scan_results.csv`，需确认 runner 是否存在并且产物是否应该纳入 manifest/coverage |
| 旧断言被替换 | CSV `inf/nan` 检查被替换后，需要确认 JSON/CSV 非标准数值防线是否仍充分 |

## 4. 建议处置

1. 不要把 `codex-review/docs`、`tests/` 修改、工具链文档修改和 `.claude/` 一次性混合提交。
2. 先确认 `tests/test_nonlinear_flux_lut_search.py` 是否属于当前要继续推进的 EXP-006 搜索闭环。
3. 如果确认要保留，应同步检查：
   - `sim/run_nonlinear_flux_lut_search_experiment.py` 是否存在；
   - `sim/search.py` 是否已稳定支持 `flux_lut` 参数；
   - 新产物是否进入 `models/scheme_simulation_coverage.json`、`claude-docs/evidence_manifest.md` 和 `claude-docs/simulation_traceability.md`；
   - 是否需要恢复或迁移 CSV `inf/nan` 检查。
4. 在下一轮评审中，把 EXP-006 状态从“synthetic LUT 插值证明”拆成两层：
   - 已提交主线：schema、sample、插值、非线性转矩；
   - 工作树在研：LUT 接入共享搜索、CSV schema 对齐和目标不可达行为。
