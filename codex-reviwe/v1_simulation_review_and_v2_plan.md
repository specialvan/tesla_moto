# V1 线性 dq 仿真复核与 V2 推进计划

## 0. 当前状态

Claude 已完成 V1 仿真闭环，当前主要产物是：

- `sim/dq_model.py`：线性 dq IPMSM 模型，显式采用幅值不变 dq、相峰值电流/电压约定。
- `sim/search.py`：电流网格搜索、目标转矩最小电流点、id=0 对照点、最大可行转矩点。
- `sim/run_linear_dq_experiment.py`：EXP-001 主仿真入口。
- `models/motor_params.json`：clean-room 示例参数。
- `experiments/exp_001_linear_dq/summary.json`：V1 摘要。
- `experiments/exp_001_linear_dq/scan_results.csv`：全速域扫描结果。
- `sim/variable_flux.py`：可变 `ψf` 预研的最小参数缩放工具。

当前测试状态：

```text
python -m pytest -q
19 passed
```

V1 仍是工程草案，不是工程验证结果。`summary.json` 已明确标记：

```text
engineering_validated = false
model_scope = quasi_steady_linear_dq_grid_search
```

---

## 1. V1 仿真结论

基线参数：

| 项 | 值 |
|---|---:|
| 电机参数集 | `baseline_ipmsm_v1` |
| 目标转矩 | 100 Nm |
| 母线电压 | 360 V |
| 相峰值电压限制 | 207.846 V |
| 相峰值电流限制 | 260 A |
| 扫描步长 | 250 rpm |
| 最高扫描转速 | 18000 rpm |

关键结果：

| 指标 | 结果 |
|---|---:|
| `id=0` 达成 100 Nm 的最高转速 | 不可达 |
| 最小电流目标转矩达成最高转速 | 6750 rpm |
| 目标转矩首次不可达转速 | 7000 rpm |
| MTPV 正转矩最高可行转速 | 18000 rpm |

6750 rpm 边界点：

| 项 | 值 |
|---|---:|
| `id` | -202 A |
| `iq` | 162 A |
| 转矩 | 100.583 Nm |
| 电流幅值 | 258.936 A |
| 电压幅值 | 207.815 V |
| 电压裕度 | 0.0308 V |
| 铜耗 | 3520 W |

18000 rpm MTPV 点：

| 项 | 值 |
|---|---:|
| `id` | -252 A |
| `iq` | 58 A |
| 转矩 | 40.187 Nm |
| 电压裕度 | 1.365 V |

直接判断：

- 这个参数集在 100 Nm 目标下，电压和电流边界都非常紧，6750 rpm 处几乎贴着电压上限。
- `id=0` 对照点完全不可达 100 Nm，说明这组 IPMSM 参数强依赖负 d 轴电流/磁阻转矩。
- 18000 rpm 仍能输出正转矩，但已经从 100 Nm 掉到约 40 Nm，说明恒功率扩展能力有限。
- V1 已经能证明弱磁/MTPV 路径的基本价值，但还不能判断效率、热、退磁和真实磁路风险。

---

## 2. V1 模型可信边界

V1 可以可信回答：

- 在给定线性 `Rs/Ld/Lq/ψf` 下，准稳态电压/电流约束是否可行。
- 给定目标转矩时，最小电流可行点大致在哪里。
- 给定转速时，电压/电流约束下最大转矩大致是多少。
- `id=0`、最小电流目标点、最大可行转矩点之间的差异。

V1 不能可信回答：

- 高电流饱和后的真实转矩误差。
- 高速铁耗和逆变器损耗。
- 温度升高后的 `Rs/ψf` 漂移。
- 负 d 轴退磁风险。
- 电流环动态、PWM 延迟和电压利用率非理想。
- 台架可标定性。
- 真实可变磁化、混合励磁、绕组重构的硬件收益。

因此，V1 是“边界探测器”，不是“设计定案器”。

---

## 3. 当前代码结构问题

当前仓库里存在两套相近搜索接口：

| 路径 | 状态 | 用途 |
|---|---|---|
| `sim/search.py` + `sim/run_linear_dq_experiment.py` | Claude V1 主线 | 正式 EXP-001 输出 |
| `sim/control_search.py` + `experiments/exp_001_linear_dq/run.py` | 早期 Codex 测试接口 | 测试和 JSON/CSV 输出接口 |

这两套逻辑目前都能跑，但会带来三个风险：

1. 搜索策略分叉，后续修一个地方漏另一个地方。
2. 实验入口分叉，结果文件可能被不同 runner 覆盖。
3. V2 引入 LUT、损耗、热模型后，接口重复会放大维护成本。

V2 前建议收敛为单一主线：

```text
sim/dq_model.py
sim/search.py
sim/run_linear_dq_experiment.py
```

`sim/control_search.py` 可以后续合并或废弃，但在合并前不要直接删除，因为现有测试依赖它。

---

## 4. V2 优先目标

V2 不应直接跳到硬件，也不应直接做复杂 Memory Motor。应先补齐 V1 缺失的三个工程判断能力：

1. **温度敏感性**：`Rs(T)`、`ψf(T)`、电流限制/电压裕度随温度变化。
2. **退磁边界**：至少引入简化 `id_min(T)`，避免负 d 轴搜索给出不可用点。
3. **非线性磁链 LUT 接口**：先用物理合理的合成 LUT 验证接口，再接 FEA/台架数据。

建议 V2 目标定义：

```text
V2 = V1 线性 dq 主线
   + 温度修正
   + 退磁 id_min 约束
   + λd/λq LUT schema
   + 方案 scorecard
```

---

## 5. V2 任务拆解

### Task V2-01：收敛实验入口

目标：确定 `sim/run_linear_dq_experiment.py` 是 EXP-001 唯一正式入口。

动作：

- 保留 `sim/search.py` 作为主搜索模块。
- 将 `experiments/exp_001_linear_dq/run.py` 标记为兼容入口或迁移到主入口。
- 测试统一验证正式输出文件。

验收：

- `python -m sim.run_linear_dq_experiment` 可生成 `summary.json/scan_results.csv`。
- `python -m pytest -q` 通过。
- 文档明确哪个入口是主入口。

### Task V2-02：温度修正

目标：加入第一版温度模型。

建议公式：

```text
Rs(T) = Rs_25 * [1 + alpha_cu * (T - 25)]
ψf(T) = ψf_25 * [1 + alpha_pm * (T - 25)]
```

建议参数：

```text
alpha_cu ≈ 0.0039 / °C
alpha_pm < 0
```

注意：`alpha_pm` 必须作为参数，不要写死材料结论。

输出：

- 常温、高温两组扫描结果。
- 高温下最高可达目标转速变化。
- 高温下电压裕度变化。

### Task V2-03：退磁边界

目标：禁止搜索结果进入明显不可用的负 d 轴区域。

第一版简化模型：

```text
id_min_allowed(T) = table_or_linear_limit(T)
candidate_feasible = electrical_feasible and id >= id_min_allowed(T)
```

输出：

- 无退磁约束 vs 有退磁约束的最高可达转速。
- 被退磁约束淘汰的候选点数量。
- 目标最高速是否仍可达。

### Task V2-04：非线性磁链 LUT schema

目标：先定义数据结构，不急着追求真实 FEA。

最小 schema：

```json
{
  "unit_convention": {},
  "temperature_c": [25, 100],
  "id_axis_a": [],
  "iq_axis_a": [],
  "lambda_d_wb": [],
  "lambda_q_wb": [],
  "valid_bounds": {}
}
```

验收：

- 单元测试验证轴长度和表尺寸匹配。
- 禁止外推。
- 支持温度维度预留。

### Task V2-05：方案 scorecard

目标：把 V1/V2 结果转成决策表。

字段：

```text
scheme
target_torque_max_speed_rpm
positive_torque_max_speed_rpm
min_voltage_margin_v
max_negative_id_a
copper_loss_at_boundary_w
demag_feasible
thermal_feasible
model_status
```

验收：

- 输出 `reports/v2_scheme_scorecard.md`。
- 每个指标都能追溯到 CSV/JSON 数据路径。

---

## 6. 对 V1 结果的工程解读

### 6.1 为什么 `id=0` 不可达

在当前参数下，`id=0` 时只能依赖永磁转矩：

```text
Te = 1.5 * p * ψf * iq
```

100 Nm 需要较高 `iq`，但受 260 A 电流限制和电压限制影响，网格中找不到满足条件的 `id=0` 点。负 `id` 一方面参与磁阻转矩，另一方面在高速区降低 `λd`，所以目标点转向负 d 轴。

### 6.2 为什么 6750 rpm 是关键边界

6750 rpm 时电压裕度只有约 0.0308 V，已经贴近电压极限。到 7000 rpm，搜索找不到同时满足：

```text
Te >= 100 Nm
I <= 260 A
V <= 207.846 V
```

的点，所以目标转矩不可达。

### 6.3 为什么 18000 rpm 还有正转矩

MTPV 不要求维持 100 Nm，只要求在电压/电流约束下找最大正转矩。它可以牺牲转矩幅值，继续输出约 40 Nm。因此：

- 100 Nm 恒转矩能力到 6750 rpm；
- 正转矩能力到 18000 rpm；
- 这两个指标不能混用。

---

## 7. 下一步建议

短期建议按下面顺序推进：

1. 先整理 V1 报告，把 `summary.json` 和边界点写成人可读结论。
2. 收敛双入口/双搜索接口，避免 V2 分叉。
3. 做温度修正和退磁边界，先解决“负 d 轴是否安全”的问题。
4. 定义 `λd/λq` LUT schema，再进入非线性磁链闭环。
5. 在此基础上再做可变 `ψf` 多档仿真，不直接进入硬件路线。

当前最重要的技术问题不是“最高速还能不能扫到 18000 rpm”，而是：

```text
在 100 Nm 目标边界附近，负 d 轴、电压裕度、温度和退磁是否同时可接受。
```

V2 应围绕这个问题展开。
