# V2 r02-sim 图档改图开跑 Handoff

日期：2026-05-20  
状态：等待用户确认生图服务器 OK 后开跑  
范围：首批只跑 S02 / S04 的 r02-sim 仿真锚点图，不跑全量 96 张。

## 1. 开跑判定

收到用户确认“生图服务器 OK”后，先做 smoke + dry-run，再进入小批改图。

不开跑条件：

- smoke test 失败；
- prompt dry-run 无法展开；
- `--edit-reference-dir` 找不到参考图；
- 输出 prompt 中缺少 `SIM ANCHOR`、`engineering_validated=false`、`model_maturity`；
- S02 prompt 未显示 30 A vs 60 A gate mismatch；
- S04 prompt 未显示 `synthetic_fixture` / `feasible_points_min=1 smoke gate`。

## 2. 输入文件

### r02-sim 规则源

- `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/README.md`
- `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/_simulation_globals.md`
- `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/simulation_anchor_matrix.json`
- `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/scheme-02-r02-sim.md`
- `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/scheme-04-r02-sim.md`

### 可直接跑的 prompt pack

- `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/V2-S02-PROMPT-r02-simulation_anchor_pack.md`
- `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/V2-S04-PROMPT-r02-simulation_anchor_pack.md`

### 参考图目录

使用现有 r00/r01 输出作为 edit reference：

```text
gpt-image-2/outputs/
```

CLI 会按 `T01/T03/T07/T08` 或 `T01/T04/T05/T07` 自动匹配 `V2-SXX-ILL-TYY-*.png`。

## 3. 首批图清单

| Scheme | 图 | 目的 |
|---|---|---|
| S02 | T01 driver block | 显示 sim data path、linear dq estimate、torque axis binding |
| S02 | T03 state machine | 显示 transition -> DVP/check 映射，以及 30 A vs 60 A mismatch |
| S02 | T07 verification tree | 拆分 strong / soft / planned gates |
| S02 | T08 protocol link | 显示 pytest observable telemetry 与 planned HIL DTC |
| S04 | T01 driver block | 显示 synthetic fixture LUT source 与 FEA 30x30xT target |
| S04 | T04 PCB concept | 把 PCB 图改成 simulation variable map |
| S04 | T05 CAD/FEA concept | 显示缺失 STEP/mesh/material/B-H/boundary/LUT export 证据 |
| S04 | T07 verification tree | 拆分 current smoke / soft warn / required r03 physics gate |

## 4. 开跑命令

所有命令在仓库根目录 `G:\tesla_moto` 执行。

### 4.1 设置 Python path

```powershell
$env:PYTHONPATH = 'gpt-image-2'
```

### 4.2 服务器 smoke

```powershell
python -m gpt_image2.generate --smoke --output-dir gpt-image-2/outputs/_smoke/r02-sim-2026-05-20
```

成功标准：

- 输出 `smoke OK`；
- 生成 `gpt-image-2/outputs/_smoke/r02-sim-2026-05-20/smoke-r00.png`；
- 生成同名 `smoke-r00-prompt.txt`。

### 4.3 dry-run S02

```powershell
python -m gpt_image2.generate `
  --prompt-pack codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/V2-S02-PROMPT-r02-simulation_anchor_pack.md `
  --dry-run `
  --output-dir gpt-image-2/outputs/_dry_run/r02-sim/S02 `
  --report-json gpt-image-2/outputs/_dry_run/r02-sim/S02/report.json
```

### 4.4 dry-run S04

```powershell
python -m gpt_image2.generate `
  --prompt-pack codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/V2-S04-PROMPT-r02-simulation_anchor_pack.md `
  --dry-run `
  --output-dir gpt-image-2/outputs/_dry_run/r02-sim/S04 `
  --report-json gpt-image-2/outputs/_dry_run/r02-sim/S04/report.json
```

### 4.5 改图 S02

```powershell
python -m gpt_image2.generate `
  --prompt-pack codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/V2-S02-PROMPT-r02-simulation_anchor_pack.md `
  --edit-reference-dir gpt-image-2/outputs `
  --output-dir gpt-image-2/outputs/S02/r02-sim `
  --force `
  --report-json gpt-image-2/outputs/S02/r02-sim/report.json
```

### 4.6 改图 S04

```powershell
python -m gpt_image2.generate `
  --prompt-pack codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/prompt_packs/V2-S04-PROMPT-r02-simulation_anchor_pack.md `
  --edit-reference-dir gpt-image-2/outputs `
  --output-dir gpt-image-2/outputs/S04/r02-sim `
  --force `
  --report-json gpt-image-2/outputs/S04/r02-sim/report.json
```

## 5. 输出路径

S02：

```text
gpt-image-2/outputs/S02/r02-sim/V2-S02-R02-T01-s02_r02_sim_driver_block.png
gpt-image-2/outputs/S02/r02-sim/V2-S02-R02-T03-s02_r02_sim_state_machine.png
gpt-image-2/outputs/S02/r02-sim/V2-S02-R02-T07-s02_r02_sim_verification_tree.png
gpt-image-2/outputs/S02/r02-sim/V2-S02-R02-T08-s02_r02_sim_protocol_link.png
```

S04：

```text
gpt-image-2/outputs/S04/r02-sim/V2-S04-R02-T01-s04_r02_sim_driver_block.png
gpt-image-2/outputs/S04/r02-sim/V2-S04-R02-T04-s04_r02_sim_pcb_variable_map.png
gpt-image-2/outputs/S04/r02-sim/V2-S04-R02-T05-s04_r02_sim_fea_boundary.png
gpt-image-2/outputs/S04/r02-sim/V2-S04-R02-T07-s04_r02_sim_verification_tree.png
```

每张 PNG 同目录会生成 `-prompt.txt` sidecar。

## 6. 图面验收 Checklist

### 通用

- [ ] 有 `SIM ANCHOR` 面板。
- [ ] 有 `scheme_id`。
- [ ] 有 `simulation_status`。
- [ ] 有 `model_maturity`。
- [ ] 有 `sim_binding`。
- [ ] 有 `pytest_gate`。
- [ ] 有 `engineering_validated=false`。
- [ ] 有 `next_simulation_step`。
- [ ] 没有 `production ready`、`FEA proven`、`HIL passed`、`bench verified`。
- [ ] 没有把 PCB/CAD 图画成制造源文件。

### S02 专项

- [ ] 显示 `numeric_proxy_passed`。
- [ ] 显示 `parameterized_linear_model`。
- [ ] 显示 `torque_axis [50,100,150,200] Nm [binding]`。
- [ ] 显示 `document target <=30 A`。
- [ ] 显示 `current binding gate <=60 A`。
- [ ] 30 A 不能被画成 green pass。
- [ ] DTC 枚举必须标 `planned HIL`。

### S04 专项

- [ ] 显示 `binding_smoke_passed`。
- [ ] 显示 `synthetic_fixture`。
- [ ] 显示 `flux_lut_sample.json`。
- [ ] 显示 `feasible_points_min=1 smoke gate`。
- [ ] 显示 `FEA 30x30xT planned`。
- [ ] 不能出现 `FEA validated` 或 `physics_model_validated`。
- [ ] T05 必须保持 flat line concept，不得写实 3D。

## 7. 失败处理

| 失败现象 | 处理 |
|---|---|
| smoke 失败 | 停止，检查 `GPT_IMAGE_BASE_URL` / `GPT_IMAGE_API_KEY` / endpoint |
| dry-run prompt 缺字段 | 停止，修 prompt pack |
| reference image not found | 停止，检查 `gpt-image-2/outputs/SXX/` 是否有对应 T 图 |
| 单张生成失败 | 保留 failed sidecar，先不重试全批；只重跑失败单张 |
| 图面文字错漏 | 不进入下一批；先做针对性 prompt 修订 |
| 出现制造/验证误导词 | 拒收并重生 |

## 8. 后续批次

首批 8 张验收通过后，再扩：

1. S01/S11：T03/T07/T08，补退磁和安全边界。
2. S03/S05/S06/S12：T07，补 proxy maturity 和下一步物理模型替换。
3. S07/S08/S09/S10：T01/T07/T08，只保留 research pool 标识。

不要在首批通过前跑全量。

