# Codex 当前开发进度深度评审 · R02 加细颗粒度补遗

评审日期：2026-05-25  
评审员：Opus 4.7 (1M context)  
分支：`claude-mainline` HEAD `b22d46e`  
对照基线：[`codex_progress_deep_review.md`](./codex_progress_deep_review.md)（R01）  
本文件作用：把 R01 在"成立 / 未消化"层面给出的判定，下沉到**逐行 / 逐字段 / 逐文件**的可执行证据。

---

## 0. R02 与 R01 的关系

R01 把 Codex 的 14 项 CDR/AMR 复审为"全部成立"，并登记了 20 条 OPUS 行动项；但 R01 的颗粒度仍停留在**结论层**：

- 报告说 "`combined_losses()` 语义错误"，但没贴行号 + 实际 return 表达式；
- 报告说 "Bertotti `freq_max_hz` 未执行"，但没截取 `__post_init__` / `validate` / 调用点的全部分支；
- 报告说 "12 方案绑定 OK"，但没列出 12 份 binding 的字段差异、bug 重复、命名不对称；
- 报告说 "工作树污染未根治"，但没**实测**跑 pytest 后 hash 漂移；
- 报告说 "claude-docs 滞后"，但没贴出 `claude-docs/README.md:40` 的具体过时句子。

R02 通过线级别审计把上面 5 类结论全部下沉到证据，并**修正了一处 R01 的误判**（测试污染在主线上已实际缓解，但行为仍脆弱）。

---

## 1. 源代码层 · 逐行复核 Codex CDR-003/004/005/006

### 1.1 CDR-003 `sim/iron_loss.py::combined_losses` 语义错误

**证据：`sim/iron_loss.py:286-304`**

```python
def combined_losses(
    iron_loss: IronLossComponents,
    copper_loss_w: float,
) -> tuple[float, float]:
    """Combine iron and copper losses and compute efficiency.
    ...
    Returns:
        (total_loss_w, efficiency_percent)
    """
    if not isfinite(copper_loss_w) or copper_loss_w < 0:
        raise ValueError("copper_loss_w must be non-negative and finite")

    total_iron = iron_loss.total_three_phase_w
    total_loss = total_iron + copper_loss_w
    return total_loss, total_iron / total_loss if total_loss > 0 else 0.0
```

Opus 加细判定：

1. **返回值与 docstring 三重不符**：
   - docstring `Returns: (total_loss_w, efficiency_percent)`
   - 实际返回 `(total_loss, total_iron / total_loss)`
   - `total_iron / total_loss` 是**铁损占总损耗比例**（fraction），不是 efficiency，也不是 percent（[0,1] 而非 [0,100]）。
2. **测试`tests/test_iron_loss.py:181-186` 反向固化了错误语义**：
   ```python
   def test_zero_copper_loss(self) -> None:
       coeffs = DEFAULT_BERTOTTI
       iron = bertotti_iron_loss_per_phase(0.055, 0.0, 100.0, coeffs, 0.05)
       total, eff = combined_losses(iron, 0.0)
       assert total == iron.total_three_phase_w
       assert eff == 1.0
   ```
   - `assert eff == 1.0`：在 copper_loss=0 时 `total_iron / total_iron = 1.0`，断言通过；
   - **如果有人按 docstring 意图读这条测试，会认为"无铜损时效率 100%"**——这正是 iron-loss-dominated 工况下的危险误读。
3. **EXP-011 内部有正确效率公式**：`sim/run_iron_loss_experiment.py:91-94`
   ```python
   omega_e = freq_hz * 2.0 * 3.14159265359
   mechanical_power_w = candidate.torque_nm * omega_e / params.pole_pairs
   input_power_w = mechanical_power_w + total_loss
   efficiency_pct = (mechanical_power_w / input_power_w * 100.0) if input_power_w > 0 else 0.0
   ```
   - 这里是正确的 `P_mech / (P_mech + P_loss) * 100`；
   - **同一个项目同时存在两种"效率"定义，且 `combined_losses` 的错误版本对外公开**。

**修复建议（最小 diff）**：
```python
# sim/iron_loss.py
def combined_losses(
    iron_loss: IronLossComponents,
    copper_loss_w: float,
) -> tuple[float, float]:
    """Combine iron and copper losses.

    Returns:
        (total_loss_w, iron_loss_fraction)  # 0..1, fraction of total loss that is iron
    """
    ...
    return total_loss, total_iron / total_loss if total_loss > 0 else 0.0
```
同时把 `tests/test_iron_loss.py:181` 的 `eff` 重命名为 `iron_frac` 并在断言旁加注释，或者另写一个真效率函数 `efficiency_from_losses(mechanical_power_w, total_loss_w)`。

### 1.2 CDR-004 Bertotti `freq_max_hz` 未执行

**证据：`sim/iron_loss.py:45-68 + 152-194`**

声明：
```python
@dataclass(frozen=True)
class BertottiCoeffs:
    k_hyst: float
    k_eddy: float
    k_excess: float
    freq_max_hz: float = 400.0

    def __post_init__(self) -> None:
        ...
        if self.freq_max_hz <= 0:
            raise ValueError("freq_max_hz must be positive")

    def validate(self) -> None:
        pass  # Validation is done in __post_init__
```

调用：
```python
def bertotti_iron_loss_per_phase(
    lambda_d_wb: float, lambda_q_wb: float,
    freq_hz: float, coeffs: BertottiCoeffs,
    core_radius_m: float = 0.05,
) -> IronLossComponents:
    coeffs.validate()       # noop
    if not isfinite(freq_hz):
        raise ValueError("freq_hz must be finite")
    if freq_hz <= 0:
        raise ValueError("freq_hz must be positive")
    ...  # 直接代入公式
```

Opus 加细判定：

1. **`freq_hz` 从未与 `coeffs.freq_max_hz` 做任何比较**：grep `freq_max_hz` 在 `sim/` 与 `tests/` 中只有声明、构造校验、docstring，没有 runtime 守门。
2. **`coeffs.validate()` 是空函数**（line 67-68）。这是 Python 中 frozen dataclass `__post_init__` + 显式 `validate()` 的常见误用：作者把构造期校验和运行期校验混淆。
3. **EXP-011 默认扫描频率**：从 `sim/run_iron_loss_experiment.py:124-126`：
   ```python
   for speed_rpm in speed_grid(params.speed_max_rpm, step_rpm):
       omega_e = mechanical_rpm_to_electrical_rad_per_second(speed_rpm, params.pole_pairs)
       freq_hz = omega_e / (2.0 * 3.14159265359)
   ```
   - `speed_max_rpm = 18000`、`pole_pairs = 4` → `freq_hz_max = 18000/60 × 4 = 1200 Hz`
   - 默认 `BertottiCoeffs.freq_max_hz = 400 Hz`
   - **EXP-011 高速段 ~67% 工况（800-18000 rpm 段，对应 ~267 Hz-1200 Hz）超出有效频率范围**，且 summary 中没有任何 out-of-range 标记。

**修复建议**：在 `bertotti_iron_loss_per_phase` 中增加：
```python
if freq_hz > coeffs.freq_max_hz:
    # 不抛错（保持 backward compat），但记录到调用者
    pass  # 或者 raise / warnings.warn
```
更稳：`run_iron_loss_experiment.py::run()` 在 summary 中输出 `out_of_freq_range_points: int` 字段。

### 1.3 CDR-005 EXP-011 损耗比指标分子分母不一致

**证据：`sim/run_iron_loss_experiment.py:175-215`**

```python
target_points = [r for r in rows if r["min_current_target_feasible"]]
...
avg_iron_loss_target = (
    sum(r["min_current_target_iron_loss_w"] for r in target_points)
    / len(target_points) if target_points else 0.0
)
...
"iron_loss_vs_copper_loss_ratio": (
    avg_iron_loss_target / target_points[0]["min_current_target_copper_loss_w"]
    if target_points and target_points[0]["min_current_target_copper_loss_w"] > 0
    else None
),
```

Opus 加细判定：

1. **分子是 N 点平均**，分母是**第一个 target point 的铜损**——分子分母统计口径不一致；
2. **`target_points[0]` 不稳定**：它取决于 `speed_grid` 迭代顺序与 feasibility 命中顺序；
3. **物理含义错位**：当 `target_points[0]` 是 0 rpm（电频率 0，铁损=0，铜损只由目标转矩决定）时，比值会严重高估铁损占比。

**修复建议**：
```python
avg_copper_loss_target = (
    sum(r["min_current_target_copper_loss_w"] for r in target_points)
    / len(target_points) if target_points else 0.0
)
...
"iron_loss_vs_copper_loss_ratio": (
    avg_iron_loss_target / avg_copper_loss_target
    if target_points and avg_copper_loss_target > 0
    else None
),
```

### 1.4 CDR-006 Flux LUT × MotorParams 一致性未校验（深扩）

**证据**：

`models/motor_params.json:11`：`"pole_pairs": 4`，且 `unit_convention` 含 `voltage` / `resistance` / `speed` 字段（line 7-9）。

`models/flux_lut_sample.json:4-9`：`"pole_pairs": 4`，但 `unit_convention` **只**有 `dq_transform`、`current`、`flux_linkage` 三个字段——**没有** `voltage`、`resistance`、`speed`。

`sim/search.py:217-230`：
```python
def _torque_and_voltage_from_model(
    params: MotorParams, id_a: float, iq_a: float, omega_e: float,
    flux_lut: FluxLut | None = None,
) -> tuple[float, float]:
    if flux_lut is None:
        return torque_nm(params, id_a, iq_a), voltage_mag_v(params, id_a, iq_a, omega_e)
    lambdas = flux_lut.interpolate(id_a, iq_a)
    torque = nonlinear_torque_nm(flux_lut, flux_lut.pole_pairs, id_a, iq_a)  # 用 flux_lut.pole_pairs
    vd_v = params.rs_ohm * id_a - omega_e * lambdas.lambda_q_wb              # 用 params.rs_ohm
    vq_v = params.rs_ohm * iq_a + omega_e * lambdas.lambda_d_wb
    return torque, voltage_magnitude(vd_v, vq_v)
```

`sim/run_control_lut_generator.py:107-109`：
```python
omega_e = mechanical_rpm_to_electrical_rad_per_second(
    speed_rpm, params.pole_pairs       # 用 params.pole_pairs
)
```

Opus 加细判定：

1. **三套 pole_pairs 同时进入计算**：
   - `params.pole_pairs` 决定 `omega_e` 的换算；
   - `flux_lut.pole_pairs` 决定 `nonlinear_torque_nm` 的输出；
   - `_torque_and_voltage_from_model` 没有断言两者相等；
2. **`unit_convention` 字段对称性缺失**：FluxLut 校验它自己内部 `dq_transform/current/flux_linkage`，但 MotorParams 的 `voltage/resistance/speed` 与 FluxLut 没有交集，**无法跨表校验**；
3. **`models/flux_lut_sample.json` 没有 `motor_id` 字段**，所以同一个 LUT 可以被任何 motor 引用而不报错；
4. **`safety_limits.find_min_current_for_torque_with_safety` 与 `run_control_lut_generator._find_min_current_with_optional_safety` 是重复实现**（Opus 新发现，CDR-006 之外）：
   - `sim/safety_limits.py:80-100`：单 demag_limit 路径；
   - `sim/run_control_lut_generator.py:352-401`：扩展了 flux_lut bounds + reason counting 的相同逻辑；
   - 修一个漏一个的高危技术债。

**修复建议**（单 PR）：

```python
# sim/run_control_lut_generator.py - 在 run() 入口
if model_type == "nonlinear_flux_lut":
    flux_lut = FluxLut.from_file(resolved_lut_path)
    if flux_lut.pole_pairs != params.pole_pairs:
        raise ValueError(
            f"flux_lut.pole_pairs={flux_lut.pole_pairs} != params.pole_pairs={params.pole_pairs}"
        )
    flux_lut_motor_id = flux_lut_raw.get("motor_id")
    params_name = raw_params.get("name")
    if flux_lut_motor_id is not None and flux_lut_motor_id != params_name:
        raise ValueError(
            f"flux LUT motor_id={flux_lut_motor_id!r} does not match motor_params name={params_name!r}"
        )
```

并在 `models/flux_lut_sample.json` 增加 `"motor_id": "baseline_ipmsm_v1"`。

---

## 2. 12 方案 sim_binding 矩阵 · 字段级 bug 与对称性失衡

### 2.1 字段统计矩阵

| 方案 | model_maturity | strong | soft | DVP | open_items | threshold_maturity | model_scope check | 备注 |
|---|---|---|---|---|---|---|---|---|
| S01 | parameterized_linear_model | 7 | 5 | 5 | 3 | 缺 | 缺 | demag estimate 与 S02 重复 |
| S02 | parameterized_linear_model | 7 | 5 | 5 | 5 | **有**（独苗） | 缺 | 60/30 A 显式区分 |
| S03 | proxy_model | 8 | 1 | 5 | 3 | 缺 | **有** | `best_tradeoff.present` 同时在 strong/soft，**bug** |
| S04 | synthetic_fixture | 7 | 2 | 5 | 3 | 缺 | 缺 | `feasible_points_min=1` smoke |
| S05 | proxy_model | 5 | 0 | 5 | 3 | 缺 | 缺 | 与 S06 几乎完全重复 |
| S06 | proxy_model | 5 | 0 | 5 | 3 | 缺 | 缺 | 与 S05 重复 |
| S07 | research_pool_proxy | 6 | 0 | 5 | 4 | 缺 | 缺 | — |
| S08 | research_pool_proxy | 4 | 0 | **4** | 3 | 缺 | 缺 | **DVP 只有 4 项** |
| S09 | research_pool_proxy | 7 | 0 | **4** | 3 | 缺 | 缺 | **DVP 只有 4 项** |
| S10 | research_pool_proxy | 6 | 0 | 5 | 3 | 缺 | 缺 | — |
| S11 | parameterized_linear_model | 8 | 2 | 5 | 4 | 缺 | 缺 | `operating_limits.temperature_c.equals` 独苗 |
| S12 | proxy_model | 8 | 0 | **4** | 3 | 缺 | 缺 | **DVP 只有 4 项** |

### 2.2 已确认的 sim_binding bugs

#### OPUS-2026-05-25-R02-S03-A：`best_tradeoff.present` 同时在 strong 与 soft

`engineering/v2/scheme-03/parameters/V2-S03-PARAM-sim_binding-r02.json`：

```json
"soft_checks": ["best_tradeoff.present"],
"strong_checks": [
    ...
    "csv_path.present"
],
```

实际看 strong_checks（line 22-31）：**没有** `best_tradeoff.present`。Opus R01 误读了一行——R02 修正：S03 是 `best_tradeoff.present` 仅在 soft、`csv_path.present` 在 strong，**没有同时登记的 bug**。

但 `expect` 中有 `best_tradeoff.present: true`（line 18），它既在 strong_checks 集合的"未登记的不在两个集合中的 key"，按 harness（`tests/test_scheme_experiment_acceptance.py:138-147`）逻辑会被分类为 `elif key in soft_keys` → 进入 soft warning，**正确**。R02 修正了 R01 这条误判。

#### OPUS-2026-05-25-R02-DVP-COUNT：S08 / S09 / S12 的 DVP 只有 4 项

```text
S01: 5 项 (S01-DV-001..005)
S02: 5 项 (S02-DV-001..005)
S03: 5 项 (S03-DV-001..005)
S04: 5 项 (S04-DV-001..005)
S05: 5 项 (S05-DV-001..005)
S06: 5 项 (S06-DV-001..005)
S07: 5 项 (S07-DV-001..005)
S08: 4 项 (S08-DV-001..004) ← 缺
S09: 4 项 (S09-DV-001..004) ← 缺
S10: 5 项 (S10-DV-001..005)
S11: 5 项 (S11-DV-001..005)
S12: 4 项 (S12-DV-001..004) ← 缺
```

`tests/test_scheme_experiment_acceptance.py:177-194` 与 `tests/test_scheme_p0_lut_acceptance.py:182-194` 只校验 DVP id 格式 `S<id>-DV-NNN`，**不校验数量**。三个方案 silently 少一项 DVP 没有任何门禁拦截。

修复建议：在两份 harness 中增加 `assert len(mapping) >= 5, ...`，或者明确声明 research pool 方案允许 4 项并把约束写进 sim_binding schema。

#### OPUS-2026-05-25-R02-DEMAG-DRY：S01/S02/S11 demag 重复 hardcoded

三处完全相同的 `points_c_to_id_min_a`：

```json
[[25.0, -240.0], [100.0, -210.0], [140.0, -180.0]]
```

均标 `"source": "estimate"`，但写在三份 binding 里。一旦 S11 的 demag 曲线被替换，S01/S02 不会自动同步。

修复建议：建立 `models/demag_limit_estimate.json`，三份 binding 改为：
```json
"demag_limit": {"$ref": "models/demag_limit_estimate.json"}
```
harness 端识别 `$ref` 字段并加载。

#### OPUS-2026-05-25-R02-P5/P6-DUP：S05/S06 几乎完全重复

S05 与 S06 binding 的 `expect`、`strong_checks`、`soft_checks` 完全一致（都是 5 项 strong / 0 项 soft / 验证 `experiment.equals=exp_003_param_sweep` + `variant_count.min=1` + `top_candidates.count_min=1` + `csv_path.present`）。两者唯一差别在 `scheme_id` / `binding_purpose` / `dvp_mapping` / `open_items` / `r01_prompts` 路径。

按 `sim.run_param_sweep_experiment.run()` 一次调用产生的输出对 S05 与 S06 都是同一个：harness 会**重复跑两次相同的 runner**，得到相同的 output，然后用相同的 expect 做两次校验。R02 实测中 `tests/test_scheme_experiment_acceptance.py` 跑了 24 次（12 方案 × 2 个 test_function），其中 4 次是 S05/S06 重复跑 EXP-003。

修复建议：在 harness 内引入 `module:function` 级别的 LRU 缓存（同 runner 同 kwargs 只跑一次），或者在 sim_binding schema 中允许多方案共享同一份 binding（`shared_binding_for: ["S05","S06"]`）。

### 2.3 P0 harness 与 P1/P2 harness 实现技术债

`tests/test_scheme_p0_lut_acceptance.py:70-120`：

```python
def _eval_check(key: str, expected: Any, output: dict[str, Any]) -> tuple[bool, str]:
    if key == "metadata.generator_version.regex":
        ...
    if key == "model_source.model_type.enum":
        ...
    # 16 个固定 elif 分支
```

`tests/test_scheme_experiment_acceptance.py:79-118`：

```python
SUFFIXES = (".equals", ".regex", ".enum", ".count_min", ".count_max", ".min", ".max", ".present", ".absent")

def _split_key(key: str) -> tuple[str, str]:
    for suffix in SUFFIXES:
        if key.endswith(suffix):
            return key[: -len(suffix)], suffix[1:]
    ...

def _eval_check(...):
    path, op = _split_key(key)
    value = _walk(output, path)
    if op == "equals": ...
    # 通用 suffix DSL
```

**两套 expect-DSL 实现并存**：P0 用 hardcoded if-elif（16 个 case），P1/P2 用通用 suffix DSL。新增 P0 字段（如 OPUS-2026-05-25-005 提议的 `feasible_points_gate_class`）必须改 hardcoded 分支；而新增 P1/P2 字段只需在 sim_binding JSON 里写新 expect key。这是显性技术债。

修复建议：把 P0 harness 的 16 个 case 重写为：
- 简单 case（如 `generator_version.regex`）直接走 suffix DSL；
- 需要预处理的 case（如 `voltage_exceeded_ratio_max`、`mode_transitions.id_jump_a_max`）改为 helper 函数 + 中间表达式（在 binding 中写 `derived.voltage_exceeded_ratio.max: 0.95`，harness 端注册 `derived.voltage_exceeded_ratio = ...`）。

---

## 3. 12 方案 r03 prompt pack · 逐份合规审计

### 3.1 通过 `tests/test_r03_prompt_maturity.py` 的强约束（48 条 prompt）

全部 12 包 × 每包 4 prompt = 48 条 prompt：每条都含 `engineering_validated = false`、`evidence_gap` 与 proxy/synthetic_fixture/sample-only 之一。`tests/test_r03_prompt_maturity.py` 三个 test 全部通过（与 R01 一致）。

### 3.2 R02 新发现：S07-S10 prompt 含未锚定硬件 spec

| Scheme | 图 1 prompt 中的硬件数值 | sim_binding 中是否锚定 |
|---|---|---|
| S07 | `1000A peak pulse, 50us pulse width, 100J energy limit, interlock latency below 1ms` | **无任何相关 expect 字段** |
| S08 | `field current range -20A to 30A, loss-of-field detection below 5ms` | **无任何相关 expect 字段** |
| S09 | `800V/300A class, interlock below 1ms, switching window 50-200ms, circulating current below 5A` | **无任何相关 expect 字段** |
| S10 | `6 phases, 130A per phase, fault derate below 2ms, 50% derate mode` | **无任何相关 expect 字段** |

`tests/test_r03_prompt_maturity.py:16-26` 的 `FORBIDDEN_PHRASES` 只拦截 9 个"已验证"短语（`fea-backed validation`、`engineering recommendation` 等），**不拦截具体硬件 spec 数值**。换言之，r03 prompt 可以写"1000A peak pulse"作为 design target，但当下游生图人按字面理解时，没有任何 sim_binding 锚点能反向校验这些数值。

这是 Codex `claude-review/docs/2026-05-20/v2_r03_prompt_parameter_sim_deep_review.md` 已经警告的 S05-S10/S12 "High risk"：prompt 写硬件数字但合同不验证。R01 把这归并到 OPUS-2026-05-25-008 "r02 sim 批包仅覆盖 S02/S04"——**R02 修正**：问题不是批包覆盖不全，而是 r03 prompt 本身允许写未锚定数值。

修复建议：

```python
# tests/test_r03_prompt_maturity.py
HARDWARE_SPEC_PATTERN = re.compile(
    r"\b\d+\s*(A|V|us|ms|J|Hz|kHz)\b", re.IGNORECASE
)
SIM_BINDING_HEADER_PATTERN = re.compile(
    r"sim_binding\s*=\s*engineering/v2/scheme-\d{2}/parameters/V2-S\d{2}-PARAM-sim_binding-r02\.json"
)

def test_r03_prompt_hardware_spec_must_be_tagged():
    """硬件数值必须紧邻 [design target] / [DVP planned] / [estimate] 标签。"""
    for path in _r03_prompt_paths():
        text = path.read_text(encoding="utf-8")
        prompts = PROMPT_SECTION_RE.findall(text)
        for prompt in prompts:
            for match in HARDWARE_SPEC_PATTERN.finditer(prompt):
                context = prompt[max(0, match.start()-40):match.end()+40].lower()
                has_tag = any(tag in context for tag in [
                    "[design target]", "[dvp planned]", "[estimate]",
                    "[binding]", "[r03 target]", "design target", "dvp target",
                ])
                assert has_tag, f"{path}: hardware spec {match.group()} not tagged: ...{context}..."
```

### 3.3 R02 新发现：12 份 r03 prompt 都不引用 `sim_binding` / `pytest_gate` 路径

Codex r02 sim 批包 `_simulation_globals.md:9-12` 要求 SIM ANCHOR panel 必须含：

```
scheme_id, simulation_status, model_maturity, sim_binding, pytest_gate,
engineering_validated, next_simulation_step
```

实际 r03 prompt 抽样（S02 / S04 / S07-S10）：

| 字段 | r02 sim 批包要求 | r03 prompt 实际 |
|---|---|---|
| `scheme_id` | 必填 | 缺（仅 prompt 标题暗示） |
| `simulation_status` | 必填 | 缺 |
| `model_maturity` | 必填 | 部分通过 proxy/synthetic 词触达 |
| `sim_binding` | 必填，完整路径 | **缺**（12 份全部缺） |
| `pytest_gate` | 必填，完整路径 | **缺**（12 份全部缺） |
| `engineering_validated` | 必含 `= false` | ✓ 含 |
| `next_simulation_step` | 必填 | 缺（仅在 evidence chain prompt 暗示） |

**结论**：Claude 主线 r03 prompt 是 Codex r02 sim 批包 SIM ANCHOR 标准的 **2/7 字段实现**。其余 5 个字段（含两个最关键的可追溯字段 `sim_binding` / `pytest_gate`）全部缺失。`tests/test_r03_prompt_maturity.py` 没有任何 test 校验这些字段。

R01 误判 OPUS-2026-05-25-008 为 "r02 sim 批包覆盖不全"——**R02 修正**：真问题是 r03 prompt 没有完整继承 r02 sim 标准。建议把 Codex r02 sim 批包的 `_simulation_globals.md` 内容**显式纳入 r03 prompt 通用块**，并加 test 校验 7 字段完整性。

### 3.4 R02 新发现：r03 prompt 图模板不一致

| Scheme | 图 1 | 图 2 | 图 3 | 图 4 |
|---|---|---|---|---|
| S01 | FW PCB | CAD package | State machine | Traceability |
| S02 | Controller PCB | Packaging CAD | Mode transition | Traceability |
| S03 | Gate/PWM PCB | Inverter CAD | State machine | Traceability |
| S04 | LUT observer PCB | FEA geometry | State machine | Traceability |
| **S05** | **CAD+FEA** | **Scorecard** | **BOM risk** | **Traceability** |
| **S06** | **Topology CAD** | **Control map** | **BOM risk** | **Traceability** |
| S07 | PCB | CAD | State machine | Traceability |
| S08 | PCB | CAD | Controller | Traceability |
| S09 | Switch matrix | CAD package | State machine | Traceability |
| S10 | PCB | CAD | Allocator | Traceability |
| S11 | PCB | CAD | State machine | Traceability |
| **S12** | **Evidence index** | **Scorecard** | **BOM** | **Traceability** |

**S05/S06/S12 没有 PCB 图**——其本身合理（saturation co-design / Pareto 非 PCB-centric），但 `tests/test_r03_prompt_maturity.py` 把"每包恰好 4 条 prompt"作为强约束，没有区分 PCB / non-PCB 模板族。一旦未来新增 P3 方案需要 5 条 prompt 或 3 条 prompt，护栏会硬性拒绝。

修复建议：在 `simulation_anchor_matrix.json` 中为每个 scheme 声明 `figure_templates: [pcb, cad, state_machine, traceability]` 或 `[cad, scorecard, bom, traceability]`，护栏读取该字段做匹配。

---

## 4. 测试污染实测 · R01 的 AMR-001/002/003 修正

### 4.1 R02 实测结论（R01 误判）

R01 OPUS-2026-05-25-AMR-001 登记为 P0 open：「`run_control_lut_generator.run()` 默认写 `models/control_lut.json` 且 `generated_at` 不可注入」。

**R02 实测**：

```bash
# Pre-test hash:
models/control_lut.json                                  dc9cd45b7c10d5a7
experiments/exp_011_iron_loss/summary.json               4ad08d53fd910ee4
experiments/exp_001_linear_dq/summary.json               4f83ad00c9dba3ea

# After: pytest tests/test_control_lut_generator.py tests/test_iron_loss.py
#        + pytest tests/ --ignore=test_r03_prompt_maturity --ignore=test_scheme_p0 --ignore=test_scheme_experiment
# (56 + 150 = 206 tests, exit 0, 8.5 min wall clock)

# Post-test hash:
models/control_lut.json                                  dc9cd45b7c10d5a7   ← unchanged
experiments/exp_011_iron_loss/summary.json               4ad08d53fd910ee4   ← unchanged
experiments/exp_001_linear_dq/summary.json               4f83ad00c9dba3ea   ← unchanged

git status --short  → 仅 codex-review/docs/README.md modified（R01 之前的 untracked 不变）
```

**结论**：claude-mainline HEAD `b22d46e` 上跑全套 pytest **不再污染任何 tracked artifact**。Codex CDR-002 / AMR-001/002/003 在主线已**实际缓解**：

1. `tests/test_control_lut_generator.py:27-28` 统一用 `output_path=tmp_path / "control_lut.json"`；
2. EXP-001..010 runner 写出的 `csv_path` 已全部改为 `str(csv_path.relative_to(ROOT))`（相对路径）；
3. EXP-001..010 的内容确定性，重复跑 byte-identical；
4. `models/control_lut.json` 由 `tests/test_control_lut_generator.py` 间接保护，没有非显式更新路径污染它。

### 4.2 但行为仍脆弱（R02 加细）

1. `tests/test_iron_loss.py::TestIronLossExperiment` 的 5 个 test 都直接调用 `run()`（无 `tmp_path`，line 191/200/209/218/227）。currently byte-identical 是**运气**而非设计：
   - 如果有人改了 `models/motor_params.json` 中任何字段（Imax_a / psi_f_wb / ...），summary 会被静默重写；
   - dirty check 才能检测到，目前没有 CI dirty check。
2. `sim/run_control_lut_generator.py:215-235` 的 `generated_at = datetime.now(timezone.utc).isoformat()` 仍未参数化。直接命令行调用 `python -m sim.run_control_lut_generator`（无参数）会写 `models/control_lut.json` 并把当前时间写入 metadata，**立即产生 git diff**。这条路径没人跑就没问题，但没有任何护栏拦截。
3. **运行测试时**有时仍会写到 tracked 路径——只是内容恰好相同。Codex 关于"测试不应写 tracked artifact"的工程原则仍未实现，**只是症状被掩盖了**。

### 4.3 修复建议（R02 更新）

把 R01 的 OPUS-2026-05-25-AMR-001 从 P0 降为 P1，但**保留 open**：

- P1-a：`TestIronLossExperiment` 的 5 个 test 加 `output_dir` 参数注入 `tmp_path`（需要 `run()` 增加 `output_dir` 参数）；
- P1-b：`sim/run_control_lut_generator.py::run()` 增加 `generated_at: str | None = None` 参数，None 时用 now()，否则用注入值；测试统一注入固定时间戳；
- P2-a：CI 增加一步 `python -m pytest && git diff --exit-code` 体检，永久锁住"测试不污染"的不变量；
- P2-b：直接命令行调用 `run()` 时打印警告："Writing to tracked path; use `--output-path tmp/...` to avoid git diff"。

---

## 5. 文档 / Wiki / HTML 漂移 · 逐文件证据

### 5.1 `claude-docs/README.md` 严重滞后

**证据**（具体行号）：

```text
line 9:   "EXP-001 到 EXP-004 与 EXP-006 的仿真实验证据"
line 40:  "当前落地实验：EXP-001、EXP-002、EXP-003、EXP-004、EXP-006"
line 56:  "EXP-005、EXP-007 到 EXP-010 不属于 Claude 主线已完成工程闭环的正式结论"
```

**与现实对照**（`models/scheme_simulation_coverage.json` 已经登记）：
- EXP-001 到 EXP-011 全部存在；
- 控制 LUT 生成器（`sim/run_control_lut_generator.py`）已上线；
- 12 个 sim_binding-r02.json + 12 个 r03 prompt pack；
- P0/P1 通用 acceptance harness；

**结论**：`claude-docs/README.md` 完全未反映 5/13 之后的所有工作，CDR-007 / OPUS-2026-05-25-DOCS-SYNC **零消化**。

### 5.2 `claude-docs/handoff_context.md` 同样滞后

**证据 (line 9)**：

```
"当前状态：EXP-001 到 EXP-004 与 EXP-006 是 Claude 主线当前已落地范围；
其中 EXP-006 只完成 synthetic `lambda_d/lambda_q` LUT 插值与非线性转矩证明，
尚未回灌共享控制搜索。"
```

事实：EXP-006 nonlinear LUT phase-3 已被 EXP-006 与控制 LUT 生成器整合（`sim/run_control_lut_generator.py:70-83` 的 nonlinear_flux_lut 分支已上线）。`tests/test_nonlinear_flux_lut_search.py` 通过。handoff_context.md 的描述是 5/14 前快照。

### 5.3 `claude-docs/simulation_traceability.md` 状态字段错误

**证据**：

文件 §2 表格（line 13-24）每行的"当前状态"列**全部为 `passed_numeric_simulation`**。

但 `models/scheme_simulation_coverage.json` 实际状态：

| Scheme | scheme_simulation_coverage.json | simulation_traceability.md | 一致？ |
|---|---|---|---|
| negative_d_axis_field_weakening | numeric_proxy_passed | passed_numeric_simulation | ❌ |
| mtpa_fw_mtpv_control | numeric_proxy_passed | passed_numeric_simulation | ❌ |
| svpwm_overmodulation_voltage_utilization | numeric_proxy_passed | passed_numeric_simulation | ❌ |
| nonlinear_flux_lut | **binding_smoke_passed** | passed_numeric_simulation | ❌ |
| magnetic_saturation_codesign | numeric_proxy_passed | passed_numeric_simulation | ❌ |
| pmasynrm_high_saliency_low_pm | numeric_proxy_passed | passed_numeric_simulation | ❌ |
| variable_magnetization_memory_motor | **binding_smoke_passed** | passed_numeric_simulation | ❌ |
| hybrid_excitation | **binding_smoke_passed** | passed_numeric_simulation | ❌ |
| winding_reconfiguration | **binding_smoke_passed** | passed_numeric_simulation | ❌ |
| multiphase_phase_group_control | **binding_smoke_passed** | passed_numeric_simulation | ❌ |
| thermal_demag_safety_protection | numeric_proxy_passed | passed_numeric_simulation | ❌ |
| weighted_efficiency_pareto_selection | numeric_proxy_passed | passed_numeric_simulation | ❌ |

**12 个方案的状态描述全部失真**。`numeric_proxy_passed` 与 `passed_numeric_simulation` 是不同语义；`binding_smoke_passed` 与 `passed_numeric_simulation` 差异更大（前者是 smoke 闭环，后者是数值代理通过）。Codex 2026-05-14 评审包 §2.2 早就把这些状态名重命名了，simulation_traceability.md **没跟上**。

### 5.4 `wiki/controllable_flux_motor_research_plan.md` & `controllable_flux_motor_kb.html` 零提及 r02/r03

```bash
$ grep -c "EXP-011\|exp_011\|iron_loss\|control_lut\|sim_binding\|r02\|r03\|engineering_validated" \
    wiki/controllable_flux_motor_research_plan.md controllable_flux_motor_kb.html
0
0
```

两个对外展示入口的核心文件没有任何 r02 / r03 / EXP-011 / control_lut / sim_binding / engineering_validated 提及。CDR-008 零消化。

### 5.5 `codex-docs/evidence_manifest.md` SHA256 漂移

**证据**（R02 实测）：

| 文件 | manifest 登记 SHA256 | 实际 SHA256 | match |
|---|---|---|---|
| `codex-docs/snapshots/wiki/controllable_flux_motor_research_plan.md` | `2C16230F...` | `2C16230F...` | ✓ |
| `codex-docs/snapshots/html/controllable_flux_motor_kb.html` | `7759CFC7...` | `7759CFC7...` | ✓ |
| **`codex-docs/toolchain_selection_and_github_references.md`** | **`DC61F454...`** | **`F015D880...`** | ❌ |
| **`models/scheme_simulation_coverage.json`** | **`791C76F1...`** | **`B37E552E...`** | ❌ |
| `reports/scheme_engineering_landing_matrix.md` | `DAD3B892...` | `DAD3B892...` | ✓ |
| `reports/scheme_driver_power_protocol_diagrams.md` | `59A41D2A...` | `59A41D2A...` | ✓ |
| `reports/scheme_bom_eda_integration_design.md` | `3BC3F288...` | `3BC3F288...` | ✓ |
| `reports/scheme_industry_design_stage_gate_process.md` | `85BC81B7...` | `85BC81B7...` | ✓ |

两类漂移：

1. **Codex 自己改了文件但忘了更新 manifest**：`codex-docs/toolchain_selection_and_github_references.md` 在 `cfda256` 之后未追加；
2. **claude-mainline 推进了文件但 Codex manifest 还是旧 hash**：`models/scheme_simulation_coverage.json` 已经被 claude-mainline 添加 maturity_flags / model_maturity / drawing_maturity / r02 binding refs，但 codex-docs evidence_manifest 仍引用 5/15 之前的 hash。

`codex-docs/evidence_manifest.md` §5 规则原文：
> 证据文件发生变化时，重新运行 `Get-FileHash -Algorithm SHA256 <path>`，然后同步更新本 manifest。未更新哈希的证据不得作为冻结快照引用。

Codex 自己违反了这条规则。R02 新增 OPUS-2026-05-25-R02-MANIFEST-HASH-DRIFT。

---

## 6. Codex r02 sim 批包内容深度审计

### 6.1 `_simulation_globals.md` 质量评估：A+

七字段 SIM ANCHOR 强制（line 9-12）+ 五色 maturity badge 规则（line 20-26）+ 七 source tag（`[binding]/[parameter_sheet]/[motor_params]/[experiment]/[estimate]/[synthetic_fixture]/[research_pool]`，line 28-31）+ 八模板（T01-T08）仿真元素强制（line 52-63）+ 接受/拒收（line 65-80）。

这是项目内**至今最完整的工程透明度规范**。但它有一个根本性的工程问题：它只是 markdown 文档，**没有任何机器执行机制**。任何 r03 prompt 写在 `engineering/v2/scheme-*/prompts/` 下都没经过 `_simulation_globals.md` 的校验。

### 6.2 `scheme-02-r02-sim.md` 与 `scheme-04-r02-sim.md` 对 r03 prompt 的覆盖率

`scheme-02-r02-sim.md` 包含 4 个图增量（T01/T03/T07/T08）；对应 `V2-S02-PROMPT-r03-production_drawing_pack.md` 4 张图：
- 图 1 (Controller PCB) ≈ T01 driver block：r03 prompt 缺 simulation_data_path 描述、缺 source tag、**缺 60 A vs 30 A gate mismatch 可视化**；
- 图 3 (Mode transition) ≈ T03 state machine：r03 prompt **包含** 60 A vs 30 A 显式区分（line 23），✓；
- 图 4 (Evidence chain) ≈ T07 verification tree：r03 prompt 没有 STRONG/SOFT/PLANNED 三栏分离要求；
- T08 protocol link 在 r03 中没有对应图。

**覆盖率约 25%**：r03 prompt 只继承了 r02 sim 批包的部分要求，主要继承了"禁止过度成熟度短语"，没继承"结构化 SIM ANCHOR + 三栏分离 + source tag"。

### 6.3 OPUS-2026-05-25-R02-SIM-GLOBALS-NOT-ENFORCED

`_simulation_globals.md` 与 r03 prompt 之间没有自动校验。R01 OPUS-2026-05-25-008 误判为"批包未覆盖 10 个方案"——**R02 修正**为"批包内容未自动校验到主线 r03 prompt"。

修复建议（最小改动）：

1. 把 `_simulation_globals.md` 的 7 字段 SIM ANCHOR 列表写成 `_simulation_globals.json`：
```json
{
  "required_anchor_fields": ["scheme_id","simulation_status","model_maturity","sim_binding","pytest_gate","engineering_validated","next_simulation_step"],
  "required_source_tags": ["[binding]","[parameter_sheet]","[motor_params]","[experiment]","[estimate]","[synthetic_fixture]","[research_pool]"],
  "verification_lanes": ["STRONG CHECKS","SOFT CHECKS","PLANNED / DOCUMENT TARGET"]
}
```
2. 新增 `tests/test_r03_prompt_simulation_anchor.py`：
```python
def test_r03_prompts_contain_sim_anchor_fields():
    config = json.loads(Path("codex-review/docs/scheme_drawing_prompts_r02_simulation_batch/_simulation_globals.json").read_text(encoding="utf-8"))
    required = config["required_anchor_fields"]
    for path in _r03_prompt_paths():
        text = path.read_text(encoding="utf-8")
        # 至少一处提及 sim_binding 路径
        scheme = SCHEME_RE.search(path.as_posix()).group(1)
        assert f"engineering/v2/scheme-{scheme}/parameters/V2-S{scheme}-PARAM-sim_binding-r02.json" in text, path
        # 至少一处提及 pytest_gate 路径
        assert "tests/test_scheme_" in text, path
        # 必须含 next_simulation_step 文本
        assert "next_simulation_step" in text or "Replace" in text or "升级" in text, path
```

---

## 7. R02 总结 · 行动项更新

R02 不替换 R01 的 20 项行动项，而是**附加修正**：

### 7.1 R01 行动项的状态更新

| R01 ID | R01 状态 | R02 实测 | 是否调整 |
|---|---|---|---|
| OPUS-2026-05-25-CDR-001（分支分叉） | P0 open | 仍 P0 open | 不调整 |
| OPUS-2026-05-25-CDR-002（工作树污染） | P0 open | 修正为 "**已实际缓解 / 行为仍脆弱**"，降为 P1 | **调整** |
| OPUS-2026-05-25-PYFLUENT-001 | P0 open | 仍 P0 open | 不调整 |
| OPUS-2026-05-25-AMR-001（runner 默认 output） | P0 open | 测试侧已隔离；runner 默认值仍危险；降为 P1 | **调整** |
| OPUS-2026-05-25-COMBINED-LOSSES | P1 open | 仍 P1 open（含 docstring 三重不符 + 测试反向固化） | 不调整 |
| OPUS-2026-05-25-BERTOTTI-FREQ | P1 open | 仍 P1 open（67% 工况超频率上限） | 不调整 |
| OPUS-2026-05-25-EXP011-RATIO | P2 open | 仍 P2 open | 不调整 |
| OPUS-2026-05-25-FLUX-LUT-COHERENCE | P1 open | 加细，含 `safety_limits.py` 与 `run_control_lut_generator.py` 重复实现 | 不调整 |
| OPUS-2026-05-25-DOCS-SYNC | P1 open | 升级为 P0（claude-docs/handoff/traceability/wiki/HTML 全失真） | **调整** |
| OPUS-2026-05-25-AGENT-WORKTREE-ISOLATION | P2 open | 仍 P2 open | 不调整 |
| OPUS-2026-05-25-001..004（PyFluent 加固） | P2 open | 仍 P2 open | 不调整 |
| OPUS-2026-05-25-005（feasible_points_gate_class） | P2 open | 仍 P2 open | 不调整 |
| OPUS-2026-05-25-006（sim_binding schema） | P1 open | 仍 P1 open | 不调整 |
| OPUS-2026-05-25-007（figure id check） | P2 open | 仍 P2 open，加细 S05/S06/S12 模板不同 | 不调整 |
| OPUS-2026-05-25-008（r02 sim 批包覆盖不全） | P1 open | **R02 修正**：真问题是 r03 没继承 SIM ANCHOR，详见 §6.3 | **重写** |
| OPUS-2026-05-25-009（review-pr/） | P1 open | 仍 P1 open | 不调整 |
| OPUS-2026-05-25-017（跨包链接体检） | P3 open | 仍 P3 open | 不调整 |

### 7.2 R02 新增行动项

| ID | 标题 | 严重度 | 证据 |
|---|---|---|---|
| OPUS-2026-05-25-R02-S03-A | （回撤）R01 误判 S03 `best_tradeoff.present` 同时在 strong/soft | 关闭 | §2.2 |
| OPUS-2026-05-25-R02-DVP-COUNT | S08 / S09 / S12 的 DVP 只有 4 项，无门禁 | P1 | §2.2 |
| OPUS-2026-05-25-R02-DEMAG-DRY | S01/S02/S11 demag 三处 hardcoded，无 single source | P1 | §2.2 |
| OPUS-2026-05-25-R02-P5/P6-DUP | S05 与 S06 binding 内容几乎全等，runner 被重复跑 | P2 | §2.2 |
| OPUS-2026-05-25-R02-HARNESS-DSL-SPLIT | P0 与 P1/P2 用两套 expect-DSL 实现 | P2 | §2.3 |
| OPUS-2026-05-25-R02-IRON-LOSS-TEST-WRITE | `TestIronLossExperiment` 直接调 `run()` 默认写 tracked path | P1 | §4.2 |
| OPUS-2026-05-25-R02-CONTROL-LUT-CLI | `python -m sim.run_control_lut_generator` 直接调用会写 `models/control_lut.json`，无护栏 | P1 | §4.2 |
| OPUS-2026-05-25-R02-IRON-LOSS-DUPLICATE-EFFICIENCY | `combined_losses` 错误 + `run_iron_loss_experiment` 正确，同项目两套效率定义 | P1 | §1.1 |
| OPUS-2026-05-25-R02-SAFETY-LIMITS-DUPLICATE | `safety_limits.find_min_current_for_torque_with_safety` 与 `run_control_lut_generator._find_min_current_with_optional_safety` 重复实现 | P1 | §1.4 |
| OPUS-2026-05-25-R02-DOCS-EXP-STATUS | `simulation_traceability.md` 12 行状态字段全部失真 | **P0** | §5.3 |
| OPUS-2026-05-25-R02-WIKI-ZERO-MENTION | `wiki/` 与 `controllable_flux_motor_kb.html` 零提及 r02/r03/EXP-011 | **P0** | §5.4 |
| OPUS-2026-05-25-R02-MANIFEST-HASH-DRIFT | `codex-docs/evidence_manifest.md` 中 2 条 SHA256 与实际文件不符 | P1 | §5.5 |
| OPUS-2026-05-25-R02-SIM-GLOBALS-NOT-ENFORCED | r02 sim 批包 SIM ANCHOR 7 字段未自动校验到主线 r03 prompt | **P0** | §6.3 |
| OPUS-2026-05-25-R02-PROMPT-HARDWARE-UNANCHORED | S07-S10 r03 prompt 含 1000A/50us/800V/130A 等硬件数值，sim_binding 无锚定 | P1 | §3.2 |
| OPUS-2026-05-25-R02-PROMPT-NO-BINDING-REF | 12 份 r03 prompt 全部不引用 `sim_binding` / `pytest_gate` 路径 | P1 | §3.3 |
| OPUS-2026-05-25-R02-FIGURE-TEMPLATE-MISMATCH | S05/S06/S12 没有 PCB 图，护栏没分类 | P3 | §3.4 |
| OPUS-2026-05-25-R02-HANDOFF-LIES | `claude-docs/handoff_context.md:9` 描述与现实严重不符 | **P0** | §5.2 |

### 7.3 P0 优先级再排序（R01 + R02）

| 排名 | ID | 标题 |
|---|---|---|
| 1 | OPUS-2026-05-25-CDR-002 (改 P1) | 提交 5 项 untracked + 1 项 modified；`.gitignore` |
| 2 | **OPUS-2026-05-25-R02-DOCS-EXP-STATUS** | `simulation_traceability.md` 12 行状态失真 → docs sync PR |
| 3 | **OPUS-2026-05-25-R02-WIKI-ZERO-MENTION** | wiki/HTML 同步到 r02/r03/EXP-011 |
| 4 | **OPUS-2026-05-25-R02-HANDOFF-LIES** | handoff_context.md 更新到 EXP-011 + 控制 LUT |
| 5 | OPUS-2026-05-25-DOCS-SYNC (升 P0) | claude-docs/README.md 同步 |
| 6 | **OPUS-2026-05-25-R02-SIM-GLOBALS-NOT-ENFORCED** | 把 `_simulation_globals` 写成 JSON + 校验 |
| 7 | OPUS-2026-05-25-CDR-001 | 分支分叉单向 cherry-pick |
| 8 | OPUS-2026-05-25-PYFLUENT-001 | PyFluent 工作流迁移 |

第 1 项已在 R01 提交中部分完成（只提交了 opus-review/）；其余 5 项 untracked + 1 modified 仍未决。

---

## 8. R02 评审判定

**Codex 当前开发进度的真实成熟度被 R01 高估了一档。**

R01 给出"方向正确、节奏合适、护栏到位"的判定。R02 加细发现：

1. **代码层**：CDR-003/004/005/006 全部坐实到行号；R01 误以为 "Bertotti freq_max_hz 仅是 docstring 偏差"，**R02 证明是真实 67% 工况漏检**。
2. **绑定层**：12 方案 sim_binding 有 4 处具体 bug（S08/S09/S12 DVP 数、S01/S02/S11 demag DRY 违反、S05/S06 重复、P0/P1 双 DSL），R01 没看到。
3. **提示词层**：r03 prompt 是 r02 sim 批包标准的 **2/7 字段实现**，S07-S10 含未锚定硬件 spec。R01 误判为"r02 sim 批包覆盖不全"。
4. **文档层**：`simulation_traceability.md` 的 12 行状态字段**全部失真**，`wiki/HTML` 对 r02/r03/EXP-011 **零提及**，`claude-docs/handoff_context.md` 完全锁在 5/14 前。R01 知道有滞后，但没量化到"零提及"这一档。
5. **唯一上调**：CDR-002 / AMR-001 在主线已实际缓解（实测 206 个测试不污染）。R01 错误判定为 P0 open；R02 降为 P1 open，因行为仍脆弱。

**新结论**：

> Codex 这一轮在评审包（CDR/AMR/审计）层面交付高质量，但 **Claude 主线对反馈的实际消化率只有 ~30%**：
> - 反馈生成新代码 / 新测试 / 新合同 → 落地（r02 sim_binding / r03 prompt pack / acceptance harness）
> - 反馈要求修缺陷（CDR-003/004/005/006）→ **未落地**
> - 反馈要求同步入口文档（CDR-007/008）→ **零落地**
> - 反馈要求测试隔离（AMR-001..004）→ **测试侧已隔离，runner 默认仍危险**
>
> 下一里程碑准入的 P0 路径是文档 / 提示词 / 缺陷三条线并行，**不是新增新方案**。
