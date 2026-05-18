# V2-S01-PARAM-acceptance-r02

方案：`negative_d_axis_field_weakening`
domain：control + safety + verification（合并 sheet）
关联：
- 控制器源：`engineering/v2/scheme-01/controller/V2-S01-CTRL-field_weakening_state_machine-r00.drawio`
- PCB 草案：`engineering/v2/scheme-01/pcb/V2-S01-PCB-sensing_fault_path-r00.md`
- DVP&R 草案：`engineering/v2/scheme-01/test_dvpr/V2-S01-DVP-fw_fault_injection-r00.md`
- r01 视觉：`gpt-image-2/outputs/S01/V2-S01-ILL-T03-state_machine-r00.png` 与 r01 prompt
- 仿真入口：`sim.run_control_lut_generator.run`（共享 S02 链路，重点验证 demag 限制）
- 仿真绑定：`engineering/v2/scheme-01/parameters/V2-S01-PARAM-sim_binding-r02.json`

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| 适用电机 | `baseline_ipmsm_v1` |
| 适用电压窗 | Vdc ∈ [240, 400] V，标称 360 V；Vmax_v = 207.85 V |
| 适用电流窗 | I_phase_peak ∈ [-260, +260] A |
| 适用转速 | [0, 18 000] rpm |
| 适用温度（r02 estimate） | 25 °C / 100 °C / 140 °C 三点；台架/FEA 替换前不得超出 [-30, +120] °C |
| 工程结论可认定 | 数值仿真层面的 FW 进入条件、`id_min(T,fault)` 限幅与 demag 不可行原因分类 |
| 不可认定 | 台架实测、磁钢退磁实测、gate-disable 实时关断 |

`engineering_validated = false`。

## 2. 控制 / 安全生产参数

### 2.1 弱磁 + 限幅阈值

| 参数 | 标称 | 单位 | 来源 |
|---|---|---|---|
| Vmax | 207.85 | V | `models/motor_params.json` (Vdc · 1/√3) |
| FW 进入 V_margin | 5.0 | V | r02 工程窗 |
| FW 退出 V_margin | 0.0 | V | r02 工程窗 |
| derate 触发温度 | pm 100 °C / winding 140 °C / oil 80 °C | °C | 与 S11 同步 |
| gate_disable 关断目标延迟 | < 100 | μs | r02 工程窗（与 S11 同步） |
| latch reset 策略 | 仅服务工具 | — | PCB 草案 |

### 2.2 DemagLimit（分段折线，与 `run_safety_boundary_experiment.py` 同口径）

| 温度 (°C) | id_min_allowed (A) | 来源 |
|---|---|---|
| 25 | -240 | r02 estimate |
| 100 | -210 | r02 estimate |
| 140 | -180 | r02 estimate |

> id_min 随温度升高变得更不负（demag 风险变高，允许的反 d 轴电流缩小）。estimate 待 S11 thermal binding 与磁钢供应商曲线替换。

### 2.3 PCB 采样链生产参数

| 信号 | 类型 | 精度 / 带宽 |
|---|---|---|
| `ia/ib/ic` | 电流 ADC，12-bit | ±0.5 % FS，100 kSPS |
| `vdc_sense` | Vdc 分压 ADC，12-bit | ±1 % FS，sample with PWM |
| `motor_temp`, `inverter_temp` | NTC + ADC | 检测延迟 ≤ 1 ms |
| `gate_disable_n` | 硬件 latch 输出 | 关断延迟 < 100 μs |
| `fault_latched` | 反馈输入 | latch hold + service reset |

## 3. 不可破坏边界

1. **退磁优先级最高**：FW 收益不能以违反 `id_min_allowed(T)` 换取。
2. **V_margin 阈值不动态绕过**：r02 = 5 V，r03 修改前必须回 drawio 状态机。
3. **gate_disable 不依赖软件主循环**：必须有硬件 latch 路径。
4. **`engineering_validated` 不翻**：r02 / r03 都不翻。

## 4. 仿真绑定

仿真入口：

```python
from sim.run_control_lut_generator import run
from sim.safety_limits import DemagLimit
output = run(
    model_type="linear_dq",
    torque_axis_nm=[80.0, 100.0, 120.0],
    torque_step_nm=20.0,
    temperature_c=100.0,
    demag_limit=DemagLimit(points_c_to_id_min_a=[(25.0, -240.0), (100.0, -210.0), (140.0, -180.0)]),
)
```

期望产物：
- `metadata.demag_limit` 非空
- `feasibility_map.infeasible_reasons.demagnetization_risk` 反映温度抬升后的限制（r02 工程窗：100°C 时 ≥ 0）
- `mode_transitions.demagnetization_limit` 数组非空（demag 边界已进入主线）

## 5. DVP&R 验收映射（来自 `V2-S01-DVP-fw_fault_injection-r00.md`）

| DVP ID | 本 sheet 提供 |
|---|---|
| S01-DV-001 弱磁进入/退出 | §2.1 V_margin 阈值 + §4 mode_transitions |
| S01-DV-002 `id_min(T,fault)` 限幅 | §2.2 DemagLimit + §4 feasibility_map demagnetization_risk |
| S01-DV-003 Vdc 采样故障 | §2.3 Vdc 分压精度（HIL-side） |
| S01-DV-004 电流采样异常 | §2.3 电流采样精度（HIL-side） |
| S01-DV-005 gate-disable latch | §3 不可破坏边界 #3 + PCB 草案 |

## 6. 升级清单（r02 → r03）

1. R_s / L_d / L_q / ψ_f estimate 替换为 EXP-006 nonlinear flux LUT 或 FEA 标定。
2. DemagLimit 三点 estimate 替换为 S11 thermal + 磁钢供应商数据。
3. gate_disable 延迟从 estimate 提升为实测（< 100 μs）。
4. r01 视觉路径在 r01 PNG 出图后更新。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；与 S02 复用 sim 链路，重点扩 demag 限制 |
