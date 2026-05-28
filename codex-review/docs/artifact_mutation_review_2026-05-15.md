# 测试与产物写入专项评审

评审日期：2026-05-15
评审包：`codex-review/docs`
专项对象：测试、runner、summary、CSV、LUT 与 Git 工作树清洁度

## 1. 结论

当前项目的实验 runner 已经能稳定生成 summary、CSV、LUT 等工程产物，这是正向能力。但普通测试与默认 runner 仍会写入 tracked artifact，并且部分 summary 写入 worktree 绝对路径，部分 LUT 写入当前时间戳。这会让“运行测试”本身制造 Git diff，从而削弱评审、交接和证据包的可信度。

这不是单个文件问题，而是一个工程门禁问题。后续必须区分两类动作：

| 动作类型 | 应有行为 |
|---|---|
| 普通验证 | 不改 tracked files，或只写 `tmp_path` |
| 显式更新产物 | 通过专门 update 命令重生成 summary/CSV/LUT，并接受 Git diff 审查 |

## 2. 复核命令

本轮使用以下命令复核：

```powershell
rg -n -F -e "write_text(" -e ".open(" -e "generated_at" -e "csv_path" -e "summary_path" -e "OUTPUT_DIR" -e "output_path" sim tests experiments models
git grep -n -F -e "write_text(" -e ".open(" -e "generated_at" -e "csv_path" -e "summary_path" -e "OUTPUT_DIR" -e "output_path" claude-mainline -- sim tests experiments models
git diff -- experiments/exp_001_linear_dq/summary.json experiments/exp_004_safety_boundaries/summary.json experiments/exp_005_modulation_factor/summary.json experiments/exp_006_nonlinear_flux_lut/summary.json experiments/exp_007_hybrid_excitation/summary.json experiments/exp_008_winding_reconfiguration/summary.json experiments/exp_009_multiphase_phase_group/summary.json experiments/exp_010_weighted_efficiency_pareto/summary.json
git -C G:\tesla_moto diff -- models/control_lut.json
```

## 3. 当前评审线观察

当前 `codex-review-line` 工作区有 8 个 summary 修改，全部是路径从 `G:\tesla_moto\...` 变成 `G:\tesla_moto-codex\...`：

| 文件 | 变更类型 |
|---|---|
| `experiments/exp_001_linear_dq/summary.json` | `csv_path` 绝对路径变化 |
| `experiments/exp_004_safety_boundaries/summary.json` | `csv_path` 绝对路径变化 |
| `experiments/exp_005_modulation_factor/summary.json` | `csv_path` 绝对路径变化 |
| `experiments/exp_006_nonlinear_flux_lut/summary.json` | `lut_path` 与 `csv_path` 绝对路径变化 |
| `experiments/exp_007_hybrid_excitation/summary.json` | `csv_path` 绝对路径变化 |
| `experiments/exp_008_winding_reconfiguration/summary.json` | `csv_path` 绝对路径变化 |
| `experiments/exp_009_multiphase_phase_group/summary.json` | `csv_path` 绝对路径变化 |
| `experiments/exp_010_weighted_efficiency_pareto/summary.json` | `csv_path` 绝对路径变化 |

对应 runner 的共同模式是：

```text
OUTPUT_DIR = ROOT / "experiments" / ...
csv_path = OUTPUT_DIR / ...
summary["csv_path"] = str(csv_path)
summary_path.write_text(...)
```

风险判断：

- `str(csv_path)` 在 Windows worktree 间不可复现；
- 测试读取和验证 tracked summary/CSV，容易把“生成产物”和“验证产物”混在一起；
- 当前 diff 已证明普通验证会污染工作区。

正向例外：

- PyFluent 新测试使用 `tmp_path` 写 case/config/output，当前不污染 tracked artifact；
- PyFluent workflow 本身按 config 的 `output_dir` 写 manifest，适合作为可借鉴的测试隔离模式。

## 4. Claude 主线观察

Claude 主线已经做了部分改进：

| 文件 | 当前状态 |
|---|---|
| `experiments/exp_006_nonlinear_flux_lut/summary.json` | `csv_path` 已是相对路径 |
| `experiments/exp_006_nonlinear_flux_lut/lut_search_summary.json` | `csv_path` 已是相对路径 |
| `experiments/exp_011_iron_loss/summary.json` | `csv_path` 已是相对路径 |

但多数 legacy runner 仍写绝对路径：

| runner | 风险 |
|---|---|
| `sim/run_linear_dq_experiment.py` | 写 tracked EXP-001 summary/CSV，summary 用绝对 `csv_path` |
| `sim/run_variable_flux_experiment.py` | 写 tracked EXP-002 summary/CSV，summary 用绝对 `csv_path` |
| `sim/run_param_sweep_experiment.py` | 写 tracked EXP-003 summary/CSV，summary 用绝对 `csv_path` |
| `sim/run_safety_boundary_experiment.py` | 写 tracked EXP-004 summary/CSV，summary 用绝对 `csv_path` |
| `sim/run_modulation_factor_experiment.py` | 写 tracked EXP-005 summary/CSV，summary 用绝对 `csv_path` |
| `sim/run_hybrid_excitation_experiment.py` | 写 tracked EXP-007 summary/CSV，summary 用绝对 `csv_path` |
| `sim/run_winding_reconfiguration_experiment.py` | 写 tracked EXP-008 summary/CSV，summary 用绝对 `csv_path` |
| `sim/run_multiphase_phase_group_experiment.py` | 写 tracked EXP-009 summary/CSV，summary 用绝对 `csv_path` |
| `sim/run_weighted_efficiency_pareto_experiment.py` | 写 tracked EXP-010 summary/CSV，summary 用绝对 `csv_path` |

另一个独立问题是控制 LUT：

```text
models/control_lut.json
generated_at: 2026-05-14T12:58:40.822407+00:00
generated_at: 2026-05-14T14:01:32.036529+00:00
```

`tests/test_control_lut_generator.py` 调用默认 `run()`，默认输出是 `models/control_lut.json`，并写入 `datetime.now(timezone.utc)`。因此测试会稳定制造时间戳 diff。

## 5. 主要风险

### AMR-001：普通测试不应更新 tracked artifact

严重度：P0

测试的职责是验证行为，不应默认更新仓库产物。当前多个测试调用 `run()` 后检查 tracked summary/CSV 是否存在，这会把测试变成隐式 artifact regeneration。

建议：

- runner 增加 `output_dir` 或 `output_path` 参数；
- 测试传入 `tmp_path`；
- 正式产物更新使用单独命令，例如 `python -m sim.run_linear_dq_experiment --update-artifacts` 或现有 CLI 风格的明确入口。

### AMR-002：summary 内路径必须相对仓库根

严重度：P0

绝对路径会绑定本地工作区，导致 `G:\tesla_moto` 与 `G:\tesla_moto-codex` 之间产生无意义 diff。

建议：

- 所有 summary 的 `csv_path`、`lut_path`、`case_path` 等引用优先使用 `path.relative_to(ROOT)`；
- 对外部文件无法相对化时，字段名应改成 `external_*` 并标记不可冻结；
- 增加测试扫描 summary JSON，禁止 `G:\`、`C:\` 或 `/home/` 这类本机根路径出现在冻结产物中。

### AMR-003：生成时间戳不应破坏确定性产物

严重度：P1

`control_lut.json` 的 `generated_at` 对审计有价值，但对 committed artifact 的普通测试不友好。

建议：

- `run_control_lut_generator.run()` 增加 `generated_at` 参数，测试注入固定时间；
- 或把 `generated_at` 放入非冻结 manifest，而不是控制 LUT 主体；
- 或在测试中写到临时 output path，不覆盖 `models/control_lut.json`。

### AMR-004：缺少“测试后工作树清洁”门禁

严重度：P1

当前即使测试全绿，也不能证明工作树没有被污染。

建议：

在 CI 或本地验证脚本中增加：

```powershell
python -m pytest
git diff --exit-code
git status --short
```

如果确实需要更新产物，应使用单独 job 或显式更新命令，不与普通测试混跑。

## 6. 推荐修复顺序

| 顺序 | 修复项 | 验收 |
|---|---|---|
| 1 | 让 EXP-001、004 到 010 runner 写相对路径 | 重跑后 summary 不含本机绝对路径 |
| 2 | 给 runner 增加测试可注入的 `output_dir` | 测试使用 `tmp_path` 后不改 tracked summary/CSV |
| 3 | 修正 control LUT 生成器的时间戳策略 | 运行 `tests/test_control_lut_generator.py` 后 `models/control_lut.json` 不变 |
| 4 | 增加 summary 路径扫描测试 | 含绝对路径的冻结产物会失败 |
| 5 | 增加测试后 dirty check 到验证流程 | 绿灯覆盖“测试通过且工作树未污染” |

## 7. 与主目标的关系

这条专项评审直接服务“过程文档、wiki、HTML、Git 历史与工程产物深度评审”。它说明当前证据包不只需要文档索引，还必须保证实验产物本身能跨 worktree 复现。否则 Git 历史会持续混入路径、时间戳和本地工作区差异，影响后续所有评审结论。
