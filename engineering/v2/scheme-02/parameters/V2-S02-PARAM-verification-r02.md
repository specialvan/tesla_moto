# V2-S02-PARAM-verification-r02

方案：`mtpa_fw_mtpv_control`
domain：verification（仿真与 DVP&R 接口 / pass-fail 阈值）
关联文档：
- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-control-r02.md`（控制参数）
- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json`（机器可读绑定）
- `engineering/v2/scheme-02/test_dvpr/V2-S02-TEST-lut_mode_hil-r00.md`（DVP&R 草案）
- `sim/run_control_lut_generator.py`、`tests/test_control_lut_generator.py`

---

## 1. 仿真闭环 pass / fail 阈值

每条 expectation 既是 r02 工程窗、也是 r03 pytest 自动校验的输入。

| 检查 ID | 字段 | 期望 | 阈值 | 失败响应 |
|---|---|---|---|---|
| S02-SIM-001 | `metadata.lut_version` | 非空 + semver 格式 | regex `^\d+\.\d+\.\d+$` | r03 fail |
| S02-SIM-002 | `model_source.model_type` | `linear_dq` 或 `nonlinear_flux_lut` | enum | r03 fail |
| S02-SIM-003 | `grid_definition.speed_axis_rpm` 节点数 | ≥ 60 | 整数 | r03 fail |
| S02-SIM-004 | `grid_definition.torque_axis_nm` 节点数 | r02：≥ 1；r03：≥ 4 | 整数 | r03 fail（r02 不阻 r02 通过） |
| S02-SIM-005 | `feasibility_map.feasible_count` | r02 / r03：≥ 200 | 整数 | r03 fail |
| S02-SIM-006 | `feasibility_map.infeasible_reasons.search_not_converged` | = 0 | 强制 | r03 fail |
| S02-SIM-007 | `feasibility_map.infeasible_reasons.demagnetization_risk` | ≤ 25 | 软阈值 | r03 warn（不 fail） |
| S02-SIM-008 | `feasibility_map.infeasible_reasons.voltage_exceeded` | ≤ feasible_count × 25 % | 软阈值 | r03 warn |
| S02-SIM-009 | `validation.torque_discontinuity_at_transitions_nm` | ≤ 5.0 | 强制 | r03 fail |
| S02-SIM-010 | `mode_transitions[*].id_jump_a` | ≤ 30 | 强制 | r03 fail |
| S02-SIM-011 | `mode_transitions[*].iq_jump_a` | ≤ 30 | 强制 | r03 fail |
| S02-SIM-012 | `mode_transitions[*].demagnetization_limit` 字段存在性 | true | 强制 | r03 fail |

> 阈值"软/强"区分：strong 失败立即翻 fail，soft 仅记录 warning 但允许 r03 通过；用户在 r03 报告中可看到 warning，不会被静默吞掉。

---

## 2. DVP&R 验收阈值

每条 DVP 测试给出 r02 标称参数，再由 r03 仿真 / 后续 HIL 闭环逐条验证。

### 2.1 S02-DV-001 MTPA / FW / MTPV 模式切换连续性

| 输入 | 标称 | 单位 | 来源 |
|---|---|---|---|
| 转速扫描点 | 0..18000，步 250 | rpm | `motor_params.json:base_speed_scan_step_rpm` |
| 转矩切片 | [50, 100, 150, 200] | N·m | r02 工程窗 |
| 期望模式数（每切片） | 仅 MTPA / FW / MTPV，不含 INFEASIBLE 集中段 | — | §1 |
| 模式跳变 `id_jump_a` | ≤ 30 | A | S02-SIM-010 |
| 模式跳变 `iq_jump_a` | ≤ 30 | A | S02-SIM-011 |
| 转矩跳变 | ≤ 5.0 | N·m | S02-SIM-009 |

### 2.2 S02-DV-002 LUT CRC 失败

| 输入 | 标称 | 单位 | 来源 |
|---|---|---|---|
| 注入故障模式 | 1 字节翻位 / 校验区域擦除 / NVM 双 bank A 损坏 | — | r02 NVM 设计 |
| 期望响应 | 进 fault fallback，禁用 torque | — | §3 不可破坏边界 #3 |
| 验证窗口 | 上电 200 ms 内 | ms | r02 工程窗 |
| 期望 DTC | `S02-DTC-LUT-CRC-FAIL` | — | r02 待落实 |

### 2.3 S02-DV-003 LUT 版本不匹配

| 输入 | 标称 | 单位 | 来源 |
|---|---|---|---|
| 注入 LUT 版本 | 与 firmware allow-list 不符 | — | NVM A/B 设计 |
| 期望响应 | 拒绝加载、进诊断模式 | — | r02 |
| 验证窗口 | 上电 200 ms 内 | ms | r02 工程窗 |
| 期望 DTC | `S02-DTC-LUT-VER-MISMATCH` | — | r02 待落实 |

### 2.4 S02-DV-004 断电恢复

| 输入 | 标称 | 单位 | 来源 |
|---|---|---|---|
| 电源循环序列 | hot reset / cold reset / brown-out @ 90 V Vdc | — | r02 待落实 |
| 期望响应 | NVM 读取通过 + CRC ok + mode reset | — | §2.6 控制 sheet |
| 验证窗口 | 上电 500 ms 内 | ms | r02 工程窗 |

### 2.5 S02-DV-005 不可行区请求

| 输入 | 标称 | 单位 | 来源 |
|---|---|---|---|
| 转矩请求 | 250 N·m @ 18000 rpm（超 MTPV 边界） | — | 人为越界 |
| 期望响应 | 返回 `INFEASIBLE` + reason `voltage_exceeded` 或 `current_exceeded`；执行 derate | — | §2.5 控制 sheet |
| `feasibility_map` 计数 | 该切片至少 1 个 INFEASIBLE | — | S02-SIM-005 |

---

## 3. r03 pytest 接口预约

下一档（r03）落地时建议增加：

```text
tests/test_scheme_02_lut_acceptance.py
```

伪代码（用户许可后实施）：

```python
import json
from sim.run_control_lut_generator import run, DemagLimit

def test_s02_r02_r03_acceptance():
    binding = json.load(open("engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json"))
    expect = binding["expect"]
    output = run(**binding["kwargs"])
    # Strong checks (raise on fail)
    assert output["feasibility_map"]["infeasible_reasons"]["search_not_converged"] == 0
    assert output["validation"]["torque_discontinuity_at_transitions_nm"] <= expect["validation.torque_discontinuity_at_transitions_nm_max"]
    for transition in output["mode_transitions"]:
        assert transition["id_jump_a"] <= expect["mode_transitions.id_jump_a_max"]
        assert transition["iq_jump_a"] <= expect["mode_transitions.iq_jump_a_max"]
    # Soft checks (warning)
    if output["feasibility_map"]["infeasible_reasons"]["demagnetization_risk"] > expect["feasibility_map.infeasible_reasons.demagnetization_risk_max"]:
        print("WARN: demagnetization_risk exceeded soft threshold")
```

> 该 pytest 必须在 r03 落地时编写并通过；当前 r02 不引入新代码。

---

## 4. 不可破坏边界

1. r02 sheet 通过不等于 r03 仿真通过；r03 仿真通过不等于工程验证。
2. soft / strong 阈值的"软"不允许在生产分支静默忽略；warning 必须落到 r03 报告。
3. 任何 DVP 阈值变更必须在草案 + 控制 sheet + 本 sheet 三处同步。
4. r02 sheet 不引入新仿真代码、不修改 `sim/`；只定义阈值。

---

## 5. 版本与变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；建立 S02 仿真闭环 12 项 strong/soft 阈值与 5 条 DVP 验收映射 |
