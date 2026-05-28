# Codex 当前开发进度深度评审 · R04 前后端/客户出口逐句深挖补遗

评审日期：2026-05-29  
评审员：Opus 4.7 (1M context)  
分支：`claude-mainline` 工作树（含未提交 dashboard / sim / prompt / test 增量）  
对照基线：[`codex_progress_deep_review_r03.md`](./codex_progress_deep_review_r03.md)  
本文件作用：继续响应“颗粒度不够”的打回，把 R03 的展示层/API 风险继续下钻到 **前后端公式一致性、客户复制出口、离线 fallback 数据、状态恢复输入边界、测试断言腐化**。

---

## 0. R04 总判定

R04 新增一个 **P0 阻断级问题**：同一客户 ROI 计算，前端离线/本地路径与后端 API 路径使用不同换算系数，导致年化收益与回收周期相差 **15 倍**。

这不是文字成熟度问题，而是客户决策包的核心数字不一致：

| 路径 | 公式核心 | 默认推荐方案结果 |
|---|---|---|
| 前端 `computeBusinessCase()` | `savedWatts / 1000 * 1.8 * mileage / 100 * energyPrice` | 约 `368.16 万元/年`，回收 `5.87 月` |
| 后端 `build_decision_pack_payload()` | `savedWatts / 1000 * 0.12 * mileage / 100 * energyPrice` | 约 `24.54 万元/年`，回收 `88.00 月` |

同一个页面在 API 正常与 API fallback 两种状态下，会给客户完全不同的商业结论。这个问题优先级高于 R03 中的 P1 展示措辞，因为它直接改变“是否值得推进验证”的判断。

---

## 1. P0：前后端 ROI 公式相差 15 倍，客户决策包数值不一致

### 1.1 前端公式证据

`controllable_flux_motor_kb.html:3648-3658`：

```javascript
function computeBusinessCase(assumptions, candidateId = selected) {
  const baseline = byCandidate("baseline");
  const cand = byCandidate(candidateId) || byCandidate(selected);
  const savedWatts = baseline.loss - cand.loss;
  const normalizedKwhPer100km = savedWatts / 1000 * 1.8;
  const perVehicleAnnualKwh = normalizedKwhPer100km * assumptions.mileage / 100;
  const perVehicleAnnualSaving = perVehicleAnnualKwh * assumptions.energyPrice;
  const fleetAnnualSaving = perVehicleAnnualSaving * assumptions.production;
  const investmentYuan = assumptions.validationInvestment * 10000;
  const paybackMonths = fleetAnnualSaving > 0 ? investmentYuan / fleetAnnualSaving * 12 : Infinity;
  return { ... };
}
```

前端把 `savedWatts` 转换为 `kWh/100km` 时乘以 `1.8`。

### 1.2 后端公式证据

`sim/dashboard_api.py:682-690`：

```python
saved_watts = baseline["loss"] - selected["loss"]
assumptions = {
    key: _query_float(query, key, default)
    for key, default in DEFAULT_BUSINESS_ASSUMPTIONS.items()
}
per_vehicle_annual_saving = max(saved_watts, 0) / 1000 * 0.12 * assumptions["mileage"] / 100 * assumptions["energyPrice"]
fleet_annual_saving = per_vehicle_annual_saving * assumptions["production"]
investment_yuan = assumptions["validationInvestment"] * 10000
payback_months = investment_yuan / fleet_annual_saving * 12 if fleet_annual_saving else None
```

后端同一换算位置乘以 `0.12`。

### 1.3 精算结果

使用默认推荐方案 `hybrid_excitation_if_plus_20` 对基线：

```text
saved_watts = 4809.21 - 4468.317 = 340.893 W
mileage = 15000 km/year
energyPrice = 0.8 yuan/kWh
production = 50000 vehicles/year
validationInvestment = 180 万元
```

R04 计算：

```text
frontend_per_vehicle_yuan = 73.632888
backend_per_vehicle_yuan  = 4.9088592
ratio = 15.0
frontend_fleetAnnualSavingYuan = 3,681,644.40
backend_fleetAnnualSavingYuan  =   245,442.96
frontend_payback_months = 5.8669
backend_payback_months  = 88.0042
```

### 1.4 为什么是 P0

`controllable_flux_motor_kb.html:5196-5220` 的 `loadDecisionPack()` 有三段路径：

```javascript
try POST /api/decision-pack -> backend payload
catch -> try GET /api/decision-pack?... -> backend payload
catch -> return buildDecisionPack() // 前端本地 fallback
```

也就是说：

- API 正常时，导出的决策包使用后端 `0.12` 公式；
- API 失败或 schema 不兼容时，导出的决策包使用前端 `1.8` 公式；
- 页面内 ROI 卡片、敏感性矩阵、验收门禁、会议纪要等均调用前端 `calculateBusinessCase()`，所以即便 API 正常，页面展示和后端导出也可不一致。

这会导致客户现场出现：页面说“年化收益 368 万、5.9 月回收”，导出 JSON/API 说“24.5 万、88 月回收”。

### 1.5 现有测试为何没拦住

`tests/test_dashboard_api.py:370-371` 只断言：

```python
assert payload["businessCase"]["assumptions"]["production"] == 50000
assert payload["businessCase"]["paybackMonths"] is not None
```

没有断言具体 `fleetAnnualSavingYuan` 或公式。

`tests/test_frontend_dashboard.py:406-419` 只检查字符串存在：

```python
assert "fleetAnnualSavingYuan" in page
assert "paybackMonths" in page
```

没有执行前端公式，也没有与后端公式对齐。

### 1.6 最小整改

1. 建立单一 ROI 参数合同，例如：

```json
{
  "roi_energy_conversion_kwh_per_100km_per_kw": 0.12,
  "source": "dashboard_api_contract_v1"
}
```

2. 前端和后端都读取同一常量；不要在 HTML 与 Python 中各写一次 magic number。
3. 新增后端测试锁定默认推荐方案数值：

```python
assert payload["businessCase"]["fleetAnnualSavingYuan"] == 245442.96
assert payload["businessCase"]["paybackMonths"] == 88.00
```

或如果产品选择 `1.8`，就反向更新后端，关键是只能有一个来源。
4. 前端 smoke 增加一个公式一致性断言：调用 `/api/decision-pack` 后，把页面 `business-results` 的数值与 API payload 比较。

---

## 2. P1：客户复制出口大量前端自生成，不受后端 disclaimer/maturity contract 约束

R03 已指出 `/api/dashboard` 不输出机器可读 maturity。R04 进一步发现：即便后端补了 maturity，也覆盖不了多个前端本地复制出口，因为这些出口直接调用前端 builder。

### 2.1 前端本地决策包 fallback

`controllable_flux_motor_kb.html:5053-5091` 的 `buildDecisionPack()` 在前端直接生成完整 JSON：

```javascript
return {
  schemaVersion: 1,
  generatedAt: new Date().toISOString(),
  dashboard: "controllable_flux_motor_kb.html",
  theme: "premium black-gold engineering dashboard",
  selected: {...},
  gains: {...},
  businessCase: {...},
  ranking,
  evidence: ["EXP-010 weighted efficiency Pareto", "EXP-011 iron loss sweep", ...],
  disclaimer: "仅用于客户方案筛选和早期决策，不代表量产实机收益承诺。"
};
```

缺少：

- `engineering_validated: false`
- `model_maturity`
- `production_drawing_ready: false`
- `manufacturing_release_ready: false`
- `not_allowed_claims`
- `proxy_simulation_only`

### 2.2 决策包预览复制出口

`controllable_flux_motor_kb.html:3755-3798` 的 `buildDecisionPackPreview()` 输出：

```text
客户决策包预览
方案：...
收益：...
证据链完整度：...
建议动作：...
声明：仅用于方案筛选和客户早期决策，不代表量产实机收益承诺。
```

它有量产收益 disclaimer，但没有 `engineering_validated=false`，也没有说明 EXP-010/EXP-011 是 proxy / clean-room / extrapolation limited。

### 2.3 客户验收门禁复制出口

`controllable_flux_motor_kb.html:3978-4085` 的 `buildCustomerAcceptanceGate()` 使用更强的签收措辞：

```javascript
const statusForTone = tone => tone === "ready" ? "可签收" : tone === "watch" ? "条件满足" : "需补证";
...
const outcome = outcomeLevel === "ready" ? "可签收进入联合验证" : outcomeLevel === "watch" ? "带条件签收" : "暂缓签收";
...
"声明：验收结论仅用于客户联合验证准入，不代表量产实机收益承诺。"
```

问题不是“量产收益承诺”一句有没有，而是 `可签收 / 条件满足 / 验收门禁分` 这些词会被客户理解为项目 gate，而不是 proxy evidence gate。当前 copyText 没有机器可读 maturity，也没写 `engineering_validated=false`。

### 2.4 客户评审纪要复制出口

`controllable_flux_motor_kb.html:4288-4333` 的 `buildCustomerMinutes()`：

```javascript
technical: `建议以${ctx.cand.label}作为下一轮技术复核基准...`
business: `建议按${saving}和${payback}作为早期 ROI 沟通口径...`
validation: `建议把${gap.title}列为首个闭环项...`
...
copyText = [
  `客户评审纪要 - ${mode.label}`,
  `结论：${conclusionByMode[mode.id]}`,
  `当前方案：${ctx.cand.label}，收益：${saving}，回收周期：${payback}`,
  ...
]
```

`risks` 数组里有“量产需实测效率地图复核”，但 copyText 没有显式 `engineering_validated=false` / `proxy-only`。

### 2.5 会议脚本复制出口

`controllable_flux_motor_kb.html:4595-4638` 的 `buildMeetingScript()`：

```javascript
const metrics = [
  ["推荐口径", ctx.cand.feasible ? "可推进验证" : "风险备选", riskCopy],
  ["收益证据", lossCopy, savingCopy],
  ...
]
...
"注意：本脚本仅用于方案筛选沟通，不代表量产实机收益承诺。"
```

同样只有量产收益 disclaimer，没有工程验证 false 与模型成熟度。

### 2.6 最小整改

建立统一前端函数：

```javascript
function maturityDisclaimerLines() {
  return [
    "engineering_validated=false",
    "model_maturity=proxy/synthetic/research_pool depending on scheme",
    "not for engineering release / production release",
    "requires FEA + HIL + bench + material/thermal evidence"
  ];
}
```

所有复制出口必须拼入该函数，而不是各自手写“量产收益不承诺”。测试必须检查每个 builder 的 copyText 包含 `engineering_validated=false`。

---

## 3. P1：后端输入边界只校验 finite，不校验业务范围；前端恢复可把越界值写回 slider

### 3.1 后端只校验 finite

`sim/dashboard_api.py:400-409`：

```python
def _query_float(query, key, default):
    value = _query_value(query, key)
    if value in (None, ""):
        return default
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{key} must be finite")
    return parsed
```

没有范围限制：

- `production` 可以是负数或极大值；
- `mileage` 可以是负数；
- `energyPrice` 可以是负数；
- `validationInvestment` 可以是负数；
- 权重可以是负数或全零。

### 3.2 前端 slider 有范围，但持久化恢复绕过范围

HTML slider 范围：`controllable_flux_motor_kb.html:2545-2548`：

```html
production min="5000" max="200000"
mileage min="5000" max="50000"
energyPrice min="0.3" max="2"
validationInvestment min="20" max="1000"
```

但状态恢复：`controllable_flux_motor_kb.html:5118-5137`：

```javascript
if (state.businessAssumptions && typeof state.businessAssumptions === "object") {
  Object.entries(state.businessAssumptions).forEach(([key, value]) => {
    if (Object.hasOwn(businessAssumptions, key)) {
      businessAssumptions[key] = Number(value);
      const input = document.querySelector(`[data-business-input="${key}"]`);
      if (input) input.value = String(value);
    }
  });
}
...
readBusinessAssumptions();
```

这会把后端持久化文件或 POST 进来的任意有限值写进 input value，再由 `readBusinessAssumptions()` 接收。浏览器 range 控件通常会有 UI 限制，但直接设置 `input.value = "-999999"` 后再读 `Number(input.value)` 不等价于业务层 clamp。

### 3.3 后端测试没覆盖负数/越界

`tests/test_dashboard_api.py` 覆盖 unknown candidate 400（line 614-635），但没有覆盖：

- `production=-1`
- `mileage=-1`
- `energyPrice=-1`
- `validationInvestment=-1`
- `urban_low_speed=-100`
- 权重全零

### 3.4 风险

负 `validationInvestment` 会让 `investment_yuan` 为负；若 `fleet_annual_saving > 0`，`payback_months` 可为负。负 `energyPrice` 可让节省变成负，影响 `paybackMonths` 与推荐文案。极大 `production` 会输出荒谬年化收益。

### 3.5 最小整改

后端增加业务范围：

```python
BOUNDS = {
  "production": (5000, 200000),
  "mileage": (5000, 50000),
  "energyPrice": (0.3, 2.0),
  "validationInvestment": (20, 1000),
  "urban_low_speed": (0, 100),
  ...
}
```

前端 `applyScenarioState()` 和 `readBusinessAssumptions()` 复用同样 bounds clamp。schema 报告登记 bounds。测试覆盖 GET/POST/session restore 三条路径。

---

## 4. P1：前端离线内置数据不是从实验产物生成，且 EXP-011 图不标有效域外

### 4.1 内置数据硬编码

`controllable_flux_motor_kb.html:2918-2936`：

```javascript
let paretoFront = [ ... ];
let cycleRows = [ ... ].map(...);
let ironLossRows = [
  [0,0,0],[1000,4298.75,59.49],...,[7000,192612.02,28.6],[8000,null,null],...
].map(...);
```

这些数据在 API 失败时作为 fallback 使用，但文件中没有 manifest/hash 标明它们来自哪个实验文件快照。

### 4.2 EXP-011 有效域外未在图层表达

R03 已算出 EXP-011 主 KPI 有 3/28 target 点超出 `freq_max_hz=400`。前端 `ironLossRows` 到 7000 rpm 仍显示有效数字：

```text
6000 rpm -> 138617.18 W, 31.82%
7000 rpm -> 192612.02 W, 28.6%
```

而 4 pole-pair 下：

- 6000 rpm -> 400 Hz，刚到上限；
- 7000 rpm -> 466.7 Hz，超出 Bertotti 系数有效范围。

`drawIronLoss()` 只画一条线：`controllable_flux_motor_kb.html:3264-3268`：

```javascript
const valid = ironLossRows.filter(d => d.ironLoss !== null);
const path = valid.map(...).join(" ");
svg.append(svgEl("path", { class: "line", d: path, stroke: "#ef6a73" }));
```

没有 out-of-range 样式或警告。

### 4.3 最小整改

- fallback 数据增加 `sourceHash` / `generatedFrom`；
- `ironLossRows` 增加 `freqHz` 与 `freqOutOfRange`；
- 7000 rpm 及以上（或 >400 Hz）用虚线/红色 out-of-range 标注；
- dashboard API 直接传 `freqOutOfRange`，前端不要推断。

---

## 5. P2：测试断言出现 `??????`，中文护栏已腐化

### 5.1 证据

`tests/test_frontend_dashboard.py:540-569`：

```python
def test_dashboard_has_customer_acceptance_gate():
    ...
    assert "??????" in page
    assert "????" in page
    assert "??????" in page
    ...
    assert "??????" in handoff_text
```

这些断言不是业务语义，而是编码腐化后的问号占位。它们会鼓励页面/文档保留错误问号，只要问号还在，测试就通过。

### 5.2 风险

这与 `reports/dashboard_black_gold_handoff.md:66` 的规则冲突：

```text
不要把中文写坏成连续问号或替换字符。Windows 上改中文时必须使用 UTF-8 安全方式。
```

### 5.3 最小整改

- 把 `??????` 断言替换回真实中文，例如 `客户验收门禁`、`验收门禁分`、`复制验收结论`；
- 新增反向测试：

```python
assert "????" not in page
assert "????" not in handoff_text
```

- 对所有 HTML/MD 报告跑 UTF-8 replacement scan。

---

## 6. P2：前端 API schema 校验只检查字段存在，不检查公式/边界/成熟度语义

`tests/test_frontend_dashboard.py:572-591` 只确认页面含：

```python
assert "loadDecisionPack" in page
assert "buildDecisionPackQuery" in page
assert "validateDecisionPackSchema" in page
assert "businessAssumptions" in page
assert "return buildDecisionPack()" in page
```

`validateDecisionPackPayload()` 自身只检查：`controllable_flux_motor_kb.html:5190-5194`

```javascript
if (payload?.source !== "backend-api" || payload?.schemaVersion !== 1 || !payload.selected || !payload.businessCase?.assumptions) {
  throw new Error("decision-pack schema incompatible");
}
```

没有检查：

- `businessCase.fleetAnnualSavingYuan` 是否与页面公式一致；
- `paybackMonths` 是否在合理范围；
- `maturity` object 是否存在；
- `disclaimer` 是否存在；
- `engineering_validated=false` 是否存在。

最小整改：把 schema 校验从“字段存在”升级到关键字段类型/范围/成熟度声明检查，并增加端到端 smoke 比对页面 ROI 与 `/api/decision-pack` ROI。

---

## 7. R04 行动项登记

| ID | 严重度 | 标题 | 证据 | 最小整改 |
|---|---|---|---|---|
| OPUS-2026-05-29-R04-ROI-FORMULA-DRIFT | **P0** | 前端 ROI 系数 `1.8` 与后端 `0.12` 不一致，客户收益/回收周期相差 15 倍 | `controllable_flux_motor_kb.html:3648-3658`, `sim/dashboard_api.py:682-690` | 单一 ROI 常量/合同；前后端共用；测试锁定默认推荐方案具体数值 |
| OPUS-2026-05-29-R04-COPY-EXPORT-MATURITY | P1 | 决策包预览、验收门禁、纪要、会议脚本等复制出口不含 `engineering_validated=false` | `controllable_flux_motor_kb.html:3755-3798`, `3978-4085`, `4288-4333`, `4595-4638` | 统一 `maturityDisclaimerLines()` 并注入所有 copyText |
| OPUS-2026-05-29-R04-INPUT-BOUNDS | P1 | 后端 POST/GET 只校验 finite，不校验业务范围；状态恢复可写回越界值 | `sim/dashboard_api.py:400-409`, `controllable_flux_motor_kb.html:5118-5137` | 增加 bounds，前后端同源 clamp/validate，测试负数/极值 |
| OPUS-2026-05-29-R04-FALLBACK-DATA-PROVENANCE | P1 | 前端 fallback 数据硬编码，无实验 hash/source，EXP-011 越界点不标注 | `controllable_flux_motor_kb.html:2918-2936`, `3264-3268` | fallback 数据带 source/hash；iron loss row 带 `freqOutOfRange` |
| OPUS-2026-05-29-R04-QUESTION-MARK-TEST | P2 | 前端测试用 `??????` 作为中文断言，固化编码腐化 | `tests/test_frontend_dashboard.py:540-569` | 恢复真实中文断言，新增 `????` 反向扫描 |
| OPUS-2026-05-29-R04-SCHEMA-SHALLOW | P2 | 前端 schema 校验只看字段存在，不校验 ROI/边界/maturity 语义 | `controllable_flux_motor_kb.html:5190-5194`, `tests/test_frontend_dashboard.py:572-591` | 校验具体数值范围、disclaimer、maturity object |

---

## 8. R04 结论

R04 将风险从“成熟度措辞”进一步定位到“客户出口数字与 gate 结论”。当前最必须先修的是 ROI 公式漂移：它会让同一页面在 API 正常和 fallback 状态下输出相差 15 倍的收益与回收周期。

因此下一步顺序应为：

1. **先修 P0 ROI 公式一致性**，并用测试锁定默认方案数值；
2. 再把 `engineering_validated=false / proxy only / not engineering release` 注入所有客户复制出口；
3. 给 POST/GET/session restore 加业务范围校验；
4. 修复 `??????` 测试腐化；
5. 最后再处理展示文案、API maturity object 和 fallback 数据 provenance。

在 P0 未修之前，不建议把 dashboard 作为客户决策材料交付或截图归档为有效评审证据。
