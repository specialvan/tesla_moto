# Codex 当前开发进度深度评审 · R03 逐字段深挖补遗

评审日期：2026-05-28  
评审员：Opus 4.7 (1M context)  
分支：`claude-mainline` 工作树（含未提交 Codex/Claude 增量）  
对照基线：[`codex_progress_deep_review_r02.md`](./codex_progress_deep_review_r02.md)  
本文件作用：把 R02 的“问题成立 / 已部分修复”继续下钻到 **字段是否真正进入运行时、测试是否真正锁住不变量、展示层是否同步工程成熟度边界**。

---

## 0. 本轮实际审计范围

### 0.1 当前 tracked diff 范围

`git diff --stat` 显示本轮 tracked 增量覆盖 32 个文件、约 `5614 insertions / 317 deletions`，核心分组如下：

| 分组 | 文件 |
|---|---|
| r03 prompt | `engineering/v2/scheme-01..12/prompts/V2-Sxx-PROMPT-r03-production_drawing_pack.md` |
| r02 sim binding | `engineering/v2/scheme-01/02/08/09/11/12/parameters/*sim_binding-r02.json` |
| EXP-011 / LUT runtime | `sim/iron_loss.py`, `sim/run_iron_loss_experiment.py`, `sim/nonlinear_flux_lut.py`, `sim/run_control_lut_generator.py` |
| tests | `tests/test_control_lut_generator.py`, `tests/test_iron_loss.py`, `tests/test_nonlinear_flux_lut.py`, `tests/test_scheme_experiment_acceptance.py`, `tests/test_scheme_p0_lut_acceptance.py`, `tests/test_r03_prompt_simulation_anchor.py` |
| 展示层 | `controllable_flux_motor_kb.html`, `sim/dashboard_api.py`, `tests/test_dashboard_api.py`, `tests/test_frontend_dashboard.py`, `reports/dashboard-api-schema.json`, `reports/open_design_dashboard_spec.json`, `reports/dashboard_black_gold_handoff.md` |

另有 untracked 增量（`models/demag_limit_estimate.json`, `tests/test_dashboard_api.py`, `tests/test_frontend_dashboard.py`, `sim/dashboard_api.py`, `reports/*dashboard*`, `codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/` 等）也进入本轮只读评审视野。

### 0.2 R03 总判定

**R03 判定：方向上明显吸收了 R02 的若干打回项，但当前仍不宜进入“下一里程碑闭环”。**

已正向吸收：

1. r03 prompt 已补 `SIM ANCHOR` 七字段；
2. S08/S09/S12 DVP 数量已补到 5 项；
3. S01/S02/S11 demag 估算改为 `$ref: models/demag_limit_estimate.json`；
4. EXP-011 支持 `output_dir`，测试不再直接写 `experiments/exp_011_iron_loss/`；
5. `combined_losses()` docstring 已从错误的 efficiency 改为 `iron_loss_fraction`；
6. control LUT 生成增加 `generated_at` 注入；
7. P0/P1 harness 增加 runner cache 与 DVP count guard。

但 R03 新发现：

- **运行时合同仍弱于 JSON schema**（FluxLut 的 maturity 只在 schema/sample 中，运行时可绕过）；
- **EXP-011 主 KPI 混入 Bertotti 频率有效域外 extrapolation 点**；
- **dashboard/API 展示层没有承载工程成熟度边界，反而新增客户交付/可刷写/验证投入等更接近商业承诺的口径**；
- **HTTP API 对 POST 体大小无上限，且 CORS 全开，作为本地工具可接受但需要明确禁止公网/共享环境使用**；
- **测试新增 cache 规避耗时，但 cache key 与输出路径分离，容易掩盖写文件行为与测试隔离问题**。

---

## 1. R02 已吸收项复核

### 1.1 r03 prompt 已补 SIM ANCHOR，但只是“文本存在”级护栏

**证据：**

- `tests/test_r03_prompt_simulation_anchor.py:18-26` 定义七字段：`scheme_id`, `simulation_status`, `model_maturity`, `sim_binding`, `pytest_gate`, `engineering_validated`, `next_simulation_step`。
- `tests/test_r03_prompt_simulation_anchor.py:41-57` 对 12 份 r03 prompt 逐份断言上述字段、scheme/status/maturity/binding/gate 文本存在。
- `engineering/v2/scheme-04/prompts/V2-S04-PROMPT-r03-production_drawing_pack.md:5-14` 示例已包含：

```text
## SIM ANCHOR
scheme_id: nonlinear_flux_lut
scheme_short: S04
simulation_status: binding_smoke_passed
model_maturity: synthetic_fixture
sim_binding: engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json
pytest_gate: tests/test_scheme_p0_lut_acceptance.py
engineering_validated: false
next_simulation_step: Replace synthetic 3x3 LUT with FEA-derived 30x30 LUT...
```

**R03 判定：部分吸收，仍有缺口。**

当前 test 只检查字段是否出现在整份 markdown 文本中，不检查每张图 prompt 是否都带 anchor，也不检查 `Prompt:` 正文是否引用了 anchor 字段。比如 S04 文件头部有完整 anchor，但第 1/2/3/4 张图仅通过自然语言写 `synthetic fixture / engineering_validated = false`，没有强制每张图都带 `sim_binding`、`pytest_gate`、`next_simulation_step`。

**最小整改：**

- 把 `tests/test_r03_prompt_simulation_anchor.py` 从“文件级存在”升级为“每个 `Prompt:` block 至少包含 `engineering_validated=false` + maturity tag + evidence_gap”；
- `sim_binding` / `pytest_gate` 可保留文件级，但必须要求每个 prompt 包含 `SIM ANCHOR` 或 `Anchor: Sxx / maturity / gate` 短行，避免生图时只复制单条 prompt 而丢上下文。

### 1.2 DVP 数量缺口已修复

**证据：**

- `engineering/v2/scheme-08/parameters/V2-S08-PARAM-sim_binding-r02.json:23-29` 已有 `S08-DV-001` 到 `S08-DV-005`。
- `engineering/v2/scheme-12/parameters/V2-S12-PARAM-sim_binding-r02.json:31-37` 已有 `S12-DV-001` 到 `S12-DV-005`。
- `tests/test_scheme_experiment_acceptance.py:214-230` 增加 `len(mapping) >= 5`。
- `tests/test_scheme_p0_lut_acceptance.py:217-233` 同样增加 P0 DVP 数量断言。

**R03 判定：已吸收。**

### 1.3 demag DRY 已从三份 binding 抽到单一模型文件

**证据：**

- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json:19-21`：`"demag_limit": {"$ref": "models/demag_limit_estimate.json"}`。
- `tests/test_scheme_p0_lut_acceptance.py:48-55` 通过 `_load_ref()` 限制 `$ref` 必须 resolve inside project root。
- `tests/test_scheme_p0_lut_acceptance.py:185-201` 固定断言 `models/demag_limit_estimate.json` 的三点 `(25,-240)/(100,-210)/(140,-180)` 被 materialize 为 `DemagLimit`。

**R03 判定：已吸收，但 `models/demag_limit_estimate.json` 当前仍 untracked，必须随本轮提交一起纳入，否则 P0 harness 在干净 checkout 下会失败。**

---

## 2. P1：Flux LUT schema 与运行时合同仍漂移

### 2.1 schema/sample 要求 maturity，`FluxLut.from_dict()` 不要求

**证据：**

`models/flux_lut_schema.json:5-16` 顶层 required 包含：

```json
"required": [
  "version", "purpose", "motor_id", "pole_pairs", "unit_convention",
  "id_axis_a", "iq_axis_a", "lambda_d_wb", "lambda_q_wb", "maturity"
]
```

`models/flux_lut_schema.json:88-115` 进一步要求：

```json
"maturity": {
  "required": [
    "model_maturity", "physics_model_validated", "engineering_validated",
    "production_release_allowed", "required_replacement"
  ],
  "properties": {
    "model_maturity": {"const": "synthetic_fixture"},
    "physics_model_validated": {"const": false},
    "engineering_validated": {"const": false},
    "production_release_allowed": {"const": false}
  }
}
```

`models/flux_lut_sample.json:55-61` 的确包含 maturity：

```json
"maturity": {
  "model_maturity": "synthetic_fixture",
  "physics_model_validated": false,
  "engineering_validated": false,
  "production_release_allowed": false,
  "required_replacement": "FEA-derived >=30x30 id/iq LUT..."
}
```

但 `sim/nonlinear_flux_lut.py:40-49` 的运行时 required 仍只有：

```python
required = [
    "motor_id", "pole_pairs", "unit_convention", "id_axis_a", "iq_axis_a",
    "lambda_d_wb", "lambda_q_wb",
]
```

`FluxLut` dataclass 本身也没有 maturity 字段（`sim/nonlinear_flux_lut.py:24-32`）。

### 2.2 现有测试反而允许“无 maturity”的运行时输入

**证据：**

`tests/test_nonlinear_flux_lut.py:65-115` 三个负例字典都没有 `version/purpose/maturity`，但期望错误是 axes/shape，而不是缺 maturity。这说明当前测试把“运行时最小 DTO 可无 maturity”固化了下来。

### 2.3 风险

S04 binding 已经明确 `model_maturity=synthetic_fixture` 与 `physics_model_validated=false`（`engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json:68-85`），但真正进入 `run_control_lut_generator.run()` 的 `FluxLut.from_file()` 不读取、不保存、不断言 maturity。任何缺少 maturity 或把 `production_release_allowed=true` 的 LUT 只要轴和矩阵形状合法，就能驱动控制 LUT 生成。

这使“schema 合同”和“运行时执行合同”分裂：schema 看起来强，运行时实际弱。

### 2.4 最小整改

推荐二选一：

1. **严格路线**：给 `FluxLut` dataclass 增加 `maturity: dict[str, Any]`，`from_dict()` required 增加 `version/purpose/maturity`，`validate()` 断言：
   - `maturity.model_maturity == "synthetic_fixture"`
   - `maturity.physics_model_validated is False`
   - `maturity.engineering_validated is False`
   - `maturity.production_release_allowed is False`
2. **分层路线**：如果确实需要最小 DTO，则新增 `FluxLutContract.from_file()` 或 `_validate_flux_lut_schema_contract(raw)`，在 `run_control_lut_generator.run()` 加载 JSON 原文时先执行 schema/maturity 检查，再构造 `FluxLut`。

同时新增测试：缺 maturity、`production_release_allowed=true`、`physics_model_validated=true` 均必须拒绝。

---

## 3. P1：EXP-011 已标记频率越界，但主 KPI 仍混入越界点

### 3.1 已修复部分

`sim/run_iron_loss_experiment.py:182` 已统计：

```python
freq_out_of_range_rows = [r for r in rows if r["freq_hz"] > coeffs.freq_max_hz]
```

`experiments/exp_011_iron_loss/summary.json:26-27` 当前输出：

```json
"freq_out_of_range_points": 48,
"freq_out_of_range_max_hz": 1199.999999999921
```

`tests/test_iron_loss.py:227-245` 也断言越界计数与 CSV 一致。

### 3.2 未修复部分：主 KPI 仍直接使用全部 target_points

`sim/run_iron_loss_experiment.py:180-201`：

```python
target_points = [r for r in rows if r["min_current_target_feasible"]]
...
avg_iron_loss_target = sum(... for r in target_points) / len(target_points)
avg_copper_loss_target = sum(... for r in target_points) / len(target_points)
avg_efficiency_target = sum(... for r in target_points) / len(target_points)
```

这里没有排除 `freq_hz > coeffs.freq_max_hz` 的 target torque 点。

R03 基于当前 CSV 精算：

```text
total_rows = 73
freq_out_of_range_rows = 48
target_points = 28
target_out_of_range_points = 3
target_oob_pct = 10.71%
first_target_oob_speed = 6250 rpm, freq = 416.67 Hz
last_target_oob_speed = 6750 rpm, freq = 450.00 Hz
```

即：summary 中 `avg_iron_loss_at_target_torque_w`, `avg_efficiency_at_target_torque_pct`, `iron_loss_vs_copper_loss_ratio` 三个主 KPI 有 **3/28 = 10.71%** 的样本来自 Bertotti 系数有效域外 extrapolation。

### 3.3 风险

当前 summary 同时写了“越界点是 extrapolation”与“平均效率 43.32% / 铁铜损比 17.24”。如果客户看板或报告只消费 KPI，不消费 `freq_out_of_range_points`，会把局部外推混入主结论。

### 3.4 最小整改

新增两套 KPI，而不是覆盖原字段：

```json
"target_torque_valid_freq_count": 25,
"target_torque_freq_out_of_range_count": 3,
"avg_iron_loss_at_target_torque_valid_freq_w": ...,
"avg_efficiency_at_target_torque_valid_freq_pct": ...,
"iron_loss_vs_copper_loss_ratio_valid_freq": ...,
"avg_iron_loss_at_target_torque_all_points_w": ...
```

并在 dashboard API 只展示 valid_freq KPI，或者在图上把 out-of-range 点做单独样式。

---

## 4. P1：展示层/API 没有携带工程成熟度边界，且新增商业化措辞放大误读

### 4.1 `/api/dashboard` response contract 没有 `engineering_validated` / `model_maturity`

`sim/dashboard_api.py:168-182`：

```python
return {
    "meta": {"title": ..., "source": "backend-api", "schemaVersion": 1},
    "paretoFront": ...,
    "cycleRows": ...,
    "ironLossRows": ...,
    "algorithmRows": ALGORITHM_ROWS,
    "deliveryItems": DELIVERY_ITEMS,
}
```

`reports/dashboard-api-schema.json:10-17` 对 `/api/dashboard` responseKeys 的登记也只有：

```json
["meta", "paretoFront", "cycleRows", "ironLossRows", "algorithmRows", "deliveryItems"]
```

没有任何：

- `engineering_validated`
- `production_drawing_ready`
- `manufacturing_release_ready`
- `model_maturity`
- `evidence_scope`
- `not_for_engineering_release`

### 4.2 展示文案更接近客户交付/软件资产，而不是 proxy 边界

`sim/dashboard_api.py:78-82`：

```python
[
  "控制 LUT 生成",
  "输入最优轨迹和约束边界，输出可刷写的控制查表数据。",
  "JSON LUT、标定版本、台架回灌接口。",
  "把算法变成可交付软件资产",
]
```

`controllable_flux_motor_kb.html:2089-2090`：

```html
<div class="kpi"><span>铁耗扫描</span><strong>0-18000 转/分</strong><small>Bertotti 三项简化模型</small></div>
<div class="kpi"><span>交付状态</span><strong>方案评估</strong><small>下一步进入有限元、硬件在环、台架闭环</small></div>
```

`controllable_flux_motor_kb.html:2145-2146`：

```html
<h2>客户交付清单</h2>
<p>每一项交付物都能回到算法、数据和验证证据。</p>
```

`controllable_flux_motor_kb.html:2180-2181` 有较好的 disclaimer：

```html
看板展示“方案筛选收益”，不承诺量产实机收益；量产口径需接入实测材料、热模型、逆变器损耗和台架数据。
```

但该 disclaimer 是页面局部文本，不在 API contract 中，也没有进入所有导出/客户摘要路径。

### 4.3 `build_decision_pack_payload()` 的 disclaimer 不足以覆盖所有响应

`sim/dashboard_api.py:718-724`：

```python
"evidence": [
  "EXP-010 weighted efficiency Pareto",
  "EXP-011 iron loss sweep",
  "wiki research plan",
  "OpenDesign black-gold handoff",
],
"disclaimer": "仅用于客户方案筛选和早期决策，不代表量产实机收益承诺。",
```

这只覆盖 `/api/decision-pack`，不覆盖 `/api/dashboard`、`/api/schema`、`/api/customer-brief` 的 schema 约束，也不把 `engineering_validated=false` 作为机器可读字段。

### 4.4 最小整改

在 `/api/dashboard` 与 `/api/decision-pack` 顶层都加入：

```json
"maturity": {
  "engineering_validated": false,
  "production_drawing_ready": false,
  "manufacturing_release_ready": false,
  "evidence_scope": "proxy_simulation_and_customer_screening_only",
  "not_allowed_claims": ["engineering release", "production control LUT release", "bench/HIL/FEA validated"]
}
```

并更新：

- `reports/dashboard-api-schema.json`
- `tests/test_dashboard_api.py`
- `tests/test_frontend_dashboard.py`
- `reports/dashboard_black_gold_handoff.md`

把 `ALGORITHM_ROWS` 中“可刷写 / 可交付软件资产 / 台架回灌接口”改成“控制 LUT 候选 / 标定草案 / 台架回灌计划”。

---

## 5. P1：dashboard HTTP API 本地工具边界没有写进代码/报告

### 5.1 POST 体没有大小上限

`sim/dashboard_api.py:852-864`：

```python
length = int(self.headers.get("Content-Length", "0"))
raw_body = self.rfile.read(length).decode("utf-8") if length else "{}"
state = json.loads(raw_body)
```

没有限制 `Content-Length`，如果这个服务绑定非 localhost 或被浏览器/局域网误访问，任意大 POST 会占用内存。

### 5.2 CORS 全开

`sim/dashboard_api.py:776-780`：

```python
self.send_header("Access-Control-Allow-Origin", "*")
self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
self.send_header("Access-Control-Allow-Headers", "Accept, Content-Type")
```

`tests/test_dashboard_api.py:305-317` 还将全开 CORS 固化为预期。

### 5.3 持久化路径由 server attribute 控制，测试里可传 tmp_path，但运行时需要限定本地用途

`sim/dashboard_api.py:632-643` 的 `_new_dashboard_server()` 可注入 state/snapshot path；`sim/dashboard_api.py:598-604` 会写：

```python
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
```

当前没有 evidence 表明 CLI 会把路径暴露给用户任意指定；但作为 review 边界，必须在 handoff 中写明：这是本地 dev/customer-demo server，不允许部署公网或共享网段。

### 5.4 最小整改

- `MAX_POST_BYTES = 256 * 1024`，超过返回 413；
- CORS 默认只允许 `127.0.0.1` / `localhost`，或至少在 `dashboard_black_gold_handoff.md` 写“不得公网部署”；
- `tests/test_dashboard_api.py` 增加大 body 413 与 invalid `Content-Length` 400；
- CLI 默认 host 必须是 `127.0.0.1`，不要默认 `0.0.0.0`。

---

## 6. P2：测试 cache 解决耗时，但引入隔离盲区

### 6.1 control LUT cache key 不含输出路径

`tests/test_control_lut_generator.py:41-48`：

```python
def generate_control_lut(tmp_path: Path, **kwargs: Any) -> dict[str, Any]:
    kwargs.setdefault("generated_at", FIXED_GENERATED_AT)
    cache_key = _cache_key(kwargs)
    if cache_key not in _GENERATED_LUT_CACHE:
        _GENERATED_LUT_CACHE[cache_key] = run(
            output_path=tmp_path / "control_lut.json", **kwargs
        )
    return _GENERATED_LUT_CACHE[cache_key]
```

`cache_key` 由 kwargs 构造，不包含 `tmp_path` 和最终 `output_path`。

### 6.2 风险

大多数测试只检查返回 dict，因此缓存能降耗；但如果后续测试检查当前 `tmp_path/control_lut.json` 是否存在或内容是否匹配，cache hit 会导致当前 tmp_path 没有文件，却返回前一测试的 dict。

`test_control_lut_generator_writes_json_output()` 直接调用 `run(output_path=output_path)`，所以当前没暴露；但这是靠测试顺序与调用方式维持，不是 cache 设计本身安全。

### 6.3 最小整改

二选一：

- cache key 加入显式输出路径，并在 `generate_control_lut()` 始终确保当前 tmp_path 有文件；
- 只缓存纯计算核心，把写文件行为从 `run()` 拆到 wrapper；测试写文件路径不走 cache。

---

## 7. P2：P0 与 P1/P2 expect DSL 仍未统一

### 7.1 P1/P2 已是通用 suffix DSL

`tests/test_scheme_experiment_acceptance.py:67-119` 支持：`.equals`, `.regex`, `.enum`, `.count_min`, `.count_max`, `.min`, `.max`, `.present`, `.absent`。

### 7.2 P0 仍是 hardcoded 分支

`tests/test_scheme_p0_lut_acceptance.py:83-136` 仍是 15+ 个 `if key == ...` 分支。

这比 R02 时略有改善（增加 `$ref`、DVP count、tmp output），但 DSL 分裂仍存在。新增 P0 字段仍要改 Python 分支，P1/P2 新字段则只改 JSON。

### 7.3 最小整改

把 P0 的特殊字段先映射成 derived output，再复用 P1/P2 `_eval_check()`：

```python
output["derived"] = {
  "voltage_exceeded_ratio": _voltage_exceeded_ratio(output),
  "mode_transition_max_id_jump_a": _all_transition_jumps(output, "id_jump_a"),
}
```

binding 写：

```json
"derived.voltage_exceeded_ratio.max": 0.95
```

---

## 8. P2：JSON 输出仍未设置 `allow_nan=False`

### 8.1 当前写法

- `sim/run_control_lut_generator.py:241-243`：`json.dumps(control_lut, ensure_ascii=False, indent=2)`。
- `sim/run_iron_loss_experiment.py:247-250`：`json.dumps(summary, ensure_ascii=False, indent=2)`。
- `sim/dashboard_api.py:646-647`：`json.dumps(payload, ensure_ascii=False)`。

### 8.2 风险

Python 默认允许 `NaN/Infinity` 输出到 JSON 文本；这不是标准 JSON。当前多数输入路径有 `isfinite` 校验，EXP-006 也有文本测试，但 control LUT、EXP-011、dashboard API 没有统一 `allow_nan=False` 防线。

### 8.3 最小整改

所有面向文件/API 的 `json.dumps` 统一：

```python
json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
```

HTTP API 若遇到非标准数值应返回 500 并在测试中锁定。

---

## 9. P2：前端/展示测试锁住了功能存在，但没锁住成熟度口径

### 9.1 现有测试覆盖

`tests/test_frontend_dashboard.py` 覆盖：

- DOM id 唯一（line 60-65）；
- evidence links 存在（line 68-74）；
- API fetch/schema fallback（line 103-124）；
- OpenDesign handoff（line 171-187）；
- 黑金视觉（line 191-213）；
- stage gate、evidence gap、meeting script、decision pack 等模块存在。

### 9.2 未覆盖内容

没有测试断言页面必须包含：

- `engineering_validated=false`；
- `production_drawing_ready=false`；
- `manufacturing_release_ready=false`；
- `proxy_simulation_only` 或等价中文；
- 禁止“可刷写 / 交付软件资产 / 客户决策已接入”这类强交付化措辞。

### 9.3 最小整改

新增 `test_dashboard_preserves_engineering_maturity_disclaimer()`：

```python
page = HTML.read_text(encoding="utf-8")
assert "engineering_validated=false" in page.replace(" ", "")
assert "不代表量产实机收益承诺" in page
assert "非工程释放" in page or "非量产释放" in page
assert "production ready" not in page.lower()
```

API 测试同步断言 `/api/dashboard` 与 `/api/decision-pack` 的 maturity object。

---

## 10. R03 行动项登记

| ID | 严重度 | 标题 | 证据 | 最小整改 |
|---|---|---|---|---|
| OPUS-2026-05-28-R03-FLUX-MATURITY-RUNTIME | P1 | Flux LUT schema/sample 的 maturity 未进入 `FluxLut.from_dict()` 运行时合同 | `models/flux_lut_schema.json:5-16`, `sim/nonlinear_flux_lut.py:40-49` | 运行时断言 maturity false / synthetic_fixture，或 schema validate 后再构造 DTO |
| OPUS-2026-05-28-R03-EXP011-KPI-OOB | P1 | EXP-011 主 KPI 混入 3/28 个 Bertotti 频率有效域外 target 点 | `sim/run_iron_loss_experiment.py:180-201`, `experiments/exp_011_iron_loss/summary.json:26-33` | 增加 valid_freq KPI 并在 dashboard 使用 valid_freq 字段 |
| OPUS-2026-05-28-R03-DASHBOARD-MATURITY-MISSING | P1 | `/api/dashboard` 和 schema 不输出工程成熟度边界 | `sim/dashboard_api.py:168-182`, `reports/dashboard-api-schema.json:10-17` | API 顶层增加 maturity object，测试和 schema 同步 |
| OPUS-2026-05-28-R03-DASHBOARD-COMMERCIAL-WORDING | P1 | 展示层“可刷写 / 可交付软件资产 / 客户交付清单”弱化 proxy 边界 | `sim/dashboard_api.py:78-82`, `controllable_flux_motor_kb.html:2145-2146` | 改为候选/草案/计划口径，并全局显示 `engineering_validated=false` |
| OPUS-2026-05-28-R03-LOCAL-API-BOUNDARY | P1 | dashboard POST 无大小上限且 CORS 全开，本地工具边界未锁 | `sim/dashboard_api.py:776-780`, `sim/dashboard_api.py:852-864` | 增加 `MAX_POST_BYTES`、本地用途声明、测试 413 |
| OPUS-2026-05-28-R03-CONTROL-LUT-CACHE-PATH | P2 | control LUT 测试 cache key 不含输出路径，可能掩盖写文件行为 | `tests/test_control_lut_generator.py:41-48` | cache key 加 output_path 或拆纯计算/写文件 |
| OPUS-2026-05-28-R03-P0-DSL-SPLIT | P2 | P0 acceptance 仍是 hardcoded expect 分支，P1/P2 是 suffix DSL | `tests/test_scheme_p0_lut_acceptance.py:83-136`, `tests/test_scheme_experiment_acceptance.py:67-119` | 抽 derived output 后统一 DSL |
| OPUS-2026-05-28-R03-ALLOW-NAN | P2 | 文件/API JSON 输出未统一 `allow_nan=False` | `sim/run_control_lut_generator.py:241-243`, `sim/run_iron_loss_experiment.py:247-250`, `sim/dashboard_api.py:646-647` | 所有 JSON dumps 加 `allow_nan=False` |
| OPUS-2026-05-28-R03-PROMPT-BLOCK-ANCHOR | P2 | r03 SIM ANCHOR 已文件级存在，但未逐 prompt block 锁定 | `tests/test_r03_prompt_simulation_anchor.py:41-57` | 对每个 `Prompt:` block 检查 maturity/evidence/false 标识 |
| OPUS-2026-05-28-R03-UNTRACKED-DEMAG-REF | P1 | P0 binding 引用 `models/demag_limit_estimate.json`，但当前文件仍 untracked | `engineering/v2/scheme-02/...:19-21`, `git status --short` | 提交该 ref 文件，或回退 binding 引用 |

---

## 11. R03 结论

R03 比 R02 看到更多正向吸收：Codex/Claude 开发已经把很多“文档层评审意见”转成了测试和字段，尤其是 SIM ANCHOR、DVP count、demag `$ref`、EXP-011 output isolation。

但当前最大问题已经从“有没有字段”转移到 **字段是否进入执行路径 / API contract / 客户展示出口**：

1. `maturity` 在 Flux LUT schema 中很强，但运行时没用；
2. `freq_out_of_range_points` 在 EXP-011 summary 中存在，但主 KPI 仍混入 10.71% 有效域外 target 点；
3. r03 prompt 有 SIM ANCHOR，但每条生图 prompt 仍可脱离 anchor 使用；
4. dashboard 有 disclaimer，但 API/schema/客户交付清单没有机器可读成熟度边界；
5. 本地 dashboard API 具备状态持久化和 POST，但未显式约束为本地 demo server。

**下一轮优先级不是继续扩 UI 或新增图，而是把成熟度边界从 markdown/header 推到运行时、API、JSON、测试和客户导出物。**
