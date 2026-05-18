# V2-S11-PARAM-acceptance-r02

方案：`thermal_demag_safety_protection`
domain：thermal + safety + verification（合并 sheet）
关联：
- 控制器源：`engineering/v2/scheme-11/controller/V2-S11-CTRL-safety_fault_state_machine-r00.drawio`
- PCB 草案：`engineering/v2/scheme-11/pcb/V2-S11-PCB-safety_fault_latch-r00.md`
- CAD 草案：`engineering/v2/scheme-11/cad/V2-S11-CAD-thermal_sensor_cooling-r00.md`
- DVP&R 草案：`engineering/v2/scheme-11/test_dvpr/V2-S11-DVP-safety_fault_injection-r00.md`
- r01 视觉：`gpt-image-2/outputs/S11/V2-S11-ILL-T01-driver_block-r00.png` 与 r01 prompt
- 仿真入口：`sim.run_control_lut_generator.run`（共享 demag 限制路径） + `sim.run_safety_boundary_experiment.run`
- 仿真绑定：`engineering/v2/scheme-11/parameters/V2-S11-PARAM-sim_binding-r02.json`

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| 适用温度 | pm/winding/oil 三链路；台架替换前不得超出 [-30, +160] °C |
| 适用电压窗 | Vdc 240-420 V critical |
| 安全目标 | 退磁保护 / 热降额 / gate-disable / fault latch |
| 工程结论可认定 | demag 边界主线接入、id_min(T) 限幅、模式切换 |
| 不可认定 | ASIL 认证、FMEDA、HIL gate-disable 物理延迟 |

`engineering_validated = false`。

## 2. 安全 / 热生产参数

### 2.1 温度阈值

| 通道 | warning (°C) | critical (°C) | 期望动作 |
|---|---|---|---|
| pm_temp | 100 | 120 | warning：进 derate；critical：gate-disable + latch |
| winding_temp | 140 | 160 | warning：derate；critical：gate-disable |
| oil_temp | 80 | 100 | warning：derate；critical：限功率 |

### 2.2 Vdc 安全窗

| 边界 | 阈值 (V) | 动作 |
|---|---|---|
| Vdc 低 critical | 240 | gate-disable |
| Vdc 高 critical | 420 | gate-disable + latch |

### 2.3 DemagLimit（同 S01 / S02）

| 温度 (°C) | id_min_allowed (A) |
|---|---|
| 25 | -240 |
| 100 | -210 |
| 140 | -180 |

### 2.4 关断 / 复位时序

| 项 | 标称 | 单位 |
|---|---|---|
| gate_disable 关断延迟目标 | < 100 | μs |
| 传感器开短路检测延迟 | < 1 | ms |
| latch reset 策略 | 仅服务工具 | — |

### 2.5 PCB 安全链信号（来自 `V2-S11-PCB-safety_fault_latch-r00.md`）

`pm_temp` (NTC, 双通道冗余)、`winding_temp` (PT1000)、`oil_temp` (NTC)、`id_min_allowed`、`gate_disable_n`、`fault_latched`、`fault_reason`。

## 3. 不可破坏边界

1. **退磁保护优先级最高**：任何 warning/critical 必须先退磁后降额。
2. **gate_disable 不依赖软件主循环**：硬件 latch 路径必须独立。
3. **latch 仅服务工具复位**：禁止自动 reset 闭环。
4. **`engineering_validated` 不翻**。

## 4. 仿真绑定

仿真入口：

```python
from sim.run_control_lut_generator import run
from sim.safety_limits import DemagLimit
output = run(
    model_type="linear_dq",
    torque_axis_nm=[80.0, 120.0],
    torque_step_nm=40.0,
    temperature_c=120.0,
    demag_limit=DemagLimit(points_c_to_id_min_a=[(25.0, -240.0), (100.0, -210.0), (140.0, -180.0)]),
)
```

期望产物：
- `metadata.demag_limit` 非空
- `feasibility_map.infeasible_reasons.demagnetization_risk` 在 T=120 °C 升高
- `mode_transitions.demagnetization_limit` 数组非空

## 5. DVP&R 验收映射（来自 `V2-S11-DVP-safety_fault_injection-r00.md`）

| DVP ID | 本 sheet 提供 |
|---|---|
| S11-DV-001 温度 warning/critical 阈值 | §2.1 三链路阈值 |
| S11-DV-002 传感器开短路 | §2.4 < 1 ms 检测 |
| S11-DV-003 demag margin 低 | §2.3 DemagLimit + §4 demagnetization_risk |
| S11-DV-004 gate-disable 断言 | §2.4 < 100 μs + §3 不可破坏边界 #2 |
| S11-DV-005 fault reason 追溯 | PCB 草案 fault_reason 编码 |

## 6. 升级清单（r02 → r03）

1. 三链路 warning/critical 阈值由 estimate 升为台架/磁钢供应商数据。
2. DemagLimit 三点替换为温度-退磁实测曲线。
3. gate_disable 延迟由 estimate 升为台架实测。
4. FMEDA、ASIL 分配仍属台架后档，不在 r02 / r03 范围。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；与 S01/S02 共享 demag 主线，扩温度三链路 |
