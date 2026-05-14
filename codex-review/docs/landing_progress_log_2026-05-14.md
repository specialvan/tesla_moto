# 方案落地推进日志

记录日期：2026-05-14

## 1. 本轮完成项

### P0-EVIDENCE-001：修复仿真覆盖证据链

状态：已完成

问题：

`models/scheme_simulation_coverage.json` 中 `mtpa_fw_mtpv_control` 原引用 `tests/test_control_search.py`，但该文件不存在。原 `tests/test_scheme_simulation_coverage.py` 只检查 `pytest_tests` 字段非空，没有验证路径真实存在。

TDD 过程：

1. 先在 `tests/test_scheme_simulation_coverage.py` 中增加 `pytest_tests` 路径存在性断言。
2. 运行：

```powershell
python -m pytest tests/test_scheme_simulation_coverage.py -q
```

3. 测试按预期失败，错误为：

```text
mtpa_fw_mtpv_control pytest test missing: tests/test_control_search.py
```

4. 将 `models/scheme_simulation_coverage.json` 中该引用替换为现有主线测试 `tests/test_exp_001_runner.py`。
5. 再次运行同一测试，结果通过：

```text
3 passed in 0.01s
```

## 2. 涉及文件

| 文件 | 变更 |
|---|---|
| `tests/test_scheme_simulation_coverage.py` | 增加 `pytest_tests` 路径存在性校验 |
| `models/scheme_simulation_coverage.json` | `mtpa_fw_mtpv_control` 测试证据从不存在的 `tests/test_control_search.py` 改为 `tests/test_exp_001_runner.py` |
| `codex-review/docs/review_action_register.json` | 将 CDR-005 标记为 `resolved_2026-05-14` |
| `codex-review/docs/scheme_landing_work_packages_2026-05-14.json` | 将 P0-EVIDENCE-001 标记为 `completed_2026-05-14` |

## 3. 落地意义

该修复把“coverage 表声称有测试”推进到“coverage 表引用的测试路径必须真实存在”，避免后续继续把不存在的测试文件写入方案状态表。

这是 12 个方案进一步落地的基础门禁：任何方案要标记为 `passed_numeric_simulation`，都必须具备真实可定位的测试证据和产物证据。

## 4. 新观察

本轮推进期间，工作树中已出现 EXP-006 LUT search 相关未提交改动：

- `sim/search.py`
- `sim/run_nonlinear_flux_lut_search_experiment.py`
- `tests/test_nonlinear_flux_lut_search.py`
- `experiments/exp_006_nonlinear_flux_lut/lut_search_summary.json`
- `experiments/exp_006_nonlinear_flux_lut/lut_search_scan_results.csv`

这些文件说明 EXP-006 正在从 synthetic LUT 插值证明继续推进到“非线性 LUT 接入共享搜索”。后续需要单独跑完整相关测试，并同步 `claude-docs/evidence_manifest.md`、`simulation_traceability.md`、wiki/HTML 和 snapshots，避免状态再次漂移。

## 5. 下一步建议

1. 继续 P0-DOCS-001：同步 `claude-docs/README.md`、`handoff_context.md`、`evidence_manifest.md`。
2. 对 EXP-006 LUT search 相关未提交改动运行针对性测试：

```powershell
python -m pytest tests/test_nonlinear_flux_lut.py tests/test_nonlinear_flux_lut_search.py tests/test_exp_001_runner.py -q
```

3. 若测试通过，将 EXP-006 状态更新为“两层闭环”：
   - synthetic LUT schema / interpolation / torque proof；
   - nonlinear LUT constrained search integration。
4. 继续推进 `models/control_lut_schema.json` 和 `models/route_scorecard_schema.json`，把控制主线和 Pareto 决策层落成可执行 schema。
