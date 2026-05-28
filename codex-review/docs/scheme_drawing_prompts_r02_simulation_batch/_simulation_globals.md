# r02 仿真锚点全局提示词规则

修订日期：2026-05-20  
作用：作为 r01 prompt 的追加层。所有 r02-sim 图都必须包含本文件的语义要求。

## 1. 全局正向追加

```text
Add a clearly separated "SIM ANCHOR" panel in the lower-right corner.
The panel MUST use monospace text and contain exactly these field labels:
scheme_id, simulation_status, model_maturity, sim_binding, pytest_gate,
engineering_validated, next_simulation_step.
The value of engineering_validated MUST be "false".
The SIM ANCHOR panel MUST be visually separate from the main diagram and
must not look like a manufacturing title block.

Use two verification lanes where applicable:
- STRONG CHECKS: gold border, checked by pytest, fail the gate.
- SOFT CHECKS: amber dashed border, warn only, not production acceptance.

Use maturity badges:
- binding_smoke_passed: amber badge
- numeric_proxy_passed: blue badge
- physics_model_validated: green badge, only if supported by FEA/bench evidence
- research_pool_proxy: red badge
- synthetic_fixture: red badge

Every numeric parameter shown in the figure MUST be tagged with one source:
[binding], [parameter_sheet], [motor_params], [experiment], [estimate],
[synthetic_fixture], or [research_pool].
Do not show untagged numeric values.

Add a small top-left boundary label:
"CONCEPT DIAGRAM · SIMULATION ANCHOR ONLY · NOT A SIMULATION SOURCE".
```

## 2. 全局负向追加

```text
Do NOT claim "validated", "production ready", "manufacturing release",
"FEA proven", "HIL passed", or "bench verified" unless the prompt explicitly
provides that evidence.
Do NOT use the phrase "passed_numeric_simulation" alone; always spell out
binding_smoke_passed or numeric_proxy_passed.
Do NOT imply PCB/CAD diagrams are EDA, Gerber, STEP, ODB++, FEA mesh, or
manufacturing source files.
Do NOT hide soft checks inside success checkmarks.
Do NOT draw a green badge for synthetic_fixture or research_pool_proxy.
Do NOT convert estimate parameters into fixed manufacturing tolerances.
```

## 3. 模板级仿真锚点

| 模板 | r02-sim 必须新增的仿真元素 |
|---|---|
| T01 driver block | 数据流从 `sim_binding kwargs` 到 runner 输出字段；突出哪些 block 只是 proxy |
| T02 power-on sequence | 上电动作必须区分 software load、binding load、CRC check、fault fallback、HIL planned |
| T03 state machine | 每条状态转移必须映射到 DVP ID、strong/soft check 或 planned HIL |
| T04 PCB concept | 只画 signal-to-parameter map，不画 layout；每个信号标注仿真变量名 |
| T05 CAD concept | 只画 geometry/FEA source boundary；标注缺失的 STEP/mesh/material source |
| T06 BOM tree | 加一支 `model maturity risk`，区分 hardware risk 与 simulation maturity risk |
| T07 verification tree | 根节点必须显示 pytest command；叶子分 strong / soft / planned |
| T08 protocol link | 每条 telemetry 边必须映射到 runner output、DTC、calibration 或 planned HIL |

## 4. r02-sim 接受/拒收规则

接受：

- 图面能让审阅者一眼看出当前是否只是 smoke/proxy；
- strong checks 与 soft checks 分离；
- next simulation step 明确；
- concept-only 边界保留。

拒收：

- 只把 r01 图换了标题；
- 继续写“production parameter drawing”但没有 sim binding；
- 绿色通过标识盖住 estimate/synthetic/research pool；
- 没有 `engineering_validated=false`；
- 没有 `next_simulation_step`。

