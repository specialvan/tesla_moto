# V2-S02-PARAM-control-r02

方案：`mtpa_fw_mtpv_control`
domain：control（控制算法 / LUT 生产参数）
关联图：
- 概念图：`gpt-image-2/outputs/S02/V2-S02-ILL-T01-driver_block-r00.png` `V2-S02-ILL-T03-state_machine-r00.png`
- 控制器源：`engineering/v2/scheme-02/controller/V2-S02-CTRL-mode_transition_lut-r00.drawio`
- 仿真入口：`sim/run_control_lut_generator.py::run`
- DVP&R 入口：`engineering/v2/scheme-02/test_dvpr/V2-S02-TEST-lut_mode_hil-r00.md`
- 数据底座：`models/motor_params.json` `models/control_lut.json` `models/control_lut_schema.json`

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| 适用电机 | `baseline_ipmsm_v1`（`models/motor_params.json`），pole_pairs = 4，IPMSM 拓扑 |
| 适用电压窗 | Vdc ∈ [240 V, 400 V] 标称 360 V；Vmax_v = 207.85 V（已应用 SVPWM linear factor 1/√3） |
| 适用电流窗 | I_phase_peak ∈ [-260 A, +260 A]（含 d 轴负向弱磁与 q 轴主动转矩两轴） |
| 适用转速 | [0, 18 000 rpm] 机械转速，按 `pole_pairs = 4` 折成电角速度 |
| 适用温度 | 仿真 25 °C 标称，r02 sheet 内增加 80 °C 工程参考点；台架 / FEA 校准前不得超出 [−30 °C, +120 °C] |
| 工程结论可认定 | 数值仿真层面的 MTPA / FW / MTPV 模式切换、不可行区分类、LUT CRC / 版本管理 |
| 不可认定 | 台架实测、ASIL 安全认证、EMC / NVH、长寿命漂移、磁钢退磁实测 |

> 本 sheet 仍保持 `engineering_validated = false`；仅作为 r03 仿真闭环准入参数源。

---

## 2. 控制生产参数

### 2.1 电机底座参数（来源：`models/motor_params.json`）

| 参数 | 符号 | 标称值 | 公差 | 单位 | 来源 | Stage Gate |
|---|---|---|---|---|---|---|
| 极对数 | p | 4 | ±0 | — | `motor_params.json:pole_pairs` | G0 |
| 相电阻（单相） | R_s | 0.035 | ±20 % | Ω | `motor_params.json:Rs_ohm` | estimate / G0 |
| d 轴电感 | L_d | 1.8e-4 | ±15 % | H | `motor_params.json:Ld_h` | estimate / G0 |
| q 轴电感 | L_q | 4.2e-4 | ±15 % | H | `motor_params.json:Lq_h` | estimate / G0 |
| 永磁磁链 | ψ_f | 0.055 | ±10 % | Wb | `motor_params.json:psi_f_wb` | estimate / G0 |
| 母线电压标称 | V_dc | 360.0 | +40 / −120 | V | `motor_params.json:Vdc_v` | G0 |
| 最大相电流（峰值） | I_max | 260.0 | -0 / +5 | A | `motor_params.json:Imax_a` | G0 |
| 最高机械转速 | n_max | 18 000 | ±0 | rpm | `motor_params.json:speed_max_rpm` | G0 |
| 转矩目标参考点 | T_ref | 100.0 | ±0 | N·m | `motor_params.json:torque_target_nm` | G0 |
| SVPWM 线性最大利用率因子 | k_svpwm | 0.57735 | ±0 | — | `motor_params.json:svpwm_linear_vmax_factor`（=1/√3） | G1 |

> 公差仅为 r02 标称工程窗，不是台架实测公差。所有 `estimate` 必须在 r02 → r03 闭环通过 + FEA 回灌后替换为实测公差。

### 2.2 网格 / 搜索参数（来源：`models/motor_params.json:grid` 与 `models/control_lut.json:model_source.search_config`）

| 参数 | 标称值 | 单位 | 来源 | 说明 |
|---|---|---|---|---|
| `id_min_a` | -260.0 | A | grid.id_min_a | d 轴负向搜索下界 |
| `id_max_a` | 40.0 | A | grid.id_max_a | d 轴正向搜索上界（受 demag 限制约束） |
| `iq_min_a` | 0.0 | A | grid.iq_min_a | q 轴下界（电动象限） |
| `iq_max_a` | 260.0 | A | grid.iq_max_a | q 轴上界（= I_max） |
| `step_a` | 2.0 | A | grid.step_a | 当前网格步长，r03 收敛后可减到 1.0 |
| `base_speed_scan_step_rpm` | 250.0 | rpm | motor_params.json | LUT 速度轴步长 |

### 2.3 LUT 输出格点定义（来源：`models/control_lut.json:grid_definition`）

| 参数 | 当前值 | 单位 | 工程窗 | 说明 |
|---|---|---|---|---|
| `speed_axis_rpm` 节点数 | 73 | 个 | ≥ 60 / G3 | 0..18000 rpm，250 rpm 等步长 |
| `torque_axis_nm` 节点数 | 1（兼容模式） | 个 | r03 要求 ≥ 4 | 当前仅单 torque；r03 需扩展为 [50, 100, 150, 200] |
| `speed_step_rpm` | 250.0 | rpm | ≤ 500 | r03 收敛要求 |
| `torque_step_nm` | 0.0（单点） | N·m | r03 改 50.0 | 显式 4 点扫描 |

### 2.4 模式切换阈值（来源：`run_control_lut_generator.py` 的 `_determine_control_mode`）

| 模式 | 进入条件 | 退出条件 | 工程窗 | 来源 |
|---|---|---|---|---|
| MTPA | 电压裕度 > VOLTAGE_MARGIN_WARNING_V 且无 demag | V_margin ≤ 0 | 进入：V_margin ≥ 5 V；退出：≤ 0 V | `run_control_lut_generator.py:DEFAULT_VOLTAGE_MARGIN_WARNING_V` |
| FW（弱磁） | MTPA 退出 + id < 0 还有裕度 | demag 触发或 V_margin 持续 ≤ 0 | id 单调减小，di/dn 不得 > 2.0 A/(rpm·100) | `_check_mode_continuity` |
| MTPV | V_margin ≤ 0 且 FW 边界达成 | demag 风险或 i_phase = I_max | i_phase 不得跨越 I_max；torque 不得跳变 > 5 N·m | `_max_id_slope` `_detect_mode_transitions` |
| INFEASIBLE | 任一原因命中 | 进入更高优先级安全状态 | 单切片中 INFEASIBLE 数量 ≤ 2 | 不可行原因表（§2.5） |
| IDLE | 上电 / Reset 后 | LUT CRC 通过 + 自检通过 | r02 sheet 强制 CRC = CRC-32 IEEE 802.3 | NVM 设计 |

### 2.5 不可行原因映射（来源：`run_control_lut_generator.py`）

| 原因 | 触发条件 | 期望响应 | r02 工程窗 |
|---|---|---|---|
| `voltage_exceeded` | candidate v_margin < 0 | 切 FW / MTPV | feasibility map 比例 ≤ 25 % |
| `current_exceeded` | candidate i_margin < 0 | derate or fault | ≤ 5 % |
| `demagnetization_risk` | id_a < id_min_allowed(T) | 限幅 + S11 联动 | ≤ 8 % |
| `out_of_flux_lut_bounds` | nonlinear LUT 全越界 | fallback linear dq | r02 接 nonlinear 时 ≤ 2 % |
| `search_not_converged` | 无候选 | fault fallback | r02 要求 = 0 % |

### 2.6 LUT 元数据生产参数

| 字段 | 标称值 | 单位 | 工程要求 | 来源 |
|---|---|---|---|---|
| `lut_version` | semver `MAJOR.MINOR.PATCH` + git hash | — | NVM 必须存 16 字节版本结构 | NVM 设计 |
| `lut_crc` | CRC-32 IEEE 802.3 | uint32 | 上电自检必须验证 | NVM 设计 |
| `lut_temperature_c` | 25.0（标称） / 80.0（高温参考） | °C | r03 必须验证 T 修正闭环 | `apply_temperature` |
| `lut_demag_limit` | `id_min_at_25c_a = -240.0, temp_coefficient = -0.0035 A/°C` | — | r02 给 estimate；r03 需 S11 协同验证 | `DemagLimit` |

### 2.7 NVM / 存储要求（r02 估值）

| 项 | 标称值 | 单位 | 来源 |
|---|---|---|---|
| LUT 单格点字节 | 24 | byte | id (4) + iq (4) + mode (1) + reason (1) + actual_torque (4) + reserved (10) |
| 73 × 4 控制点容量 | 6 K | byte | r03 扩展到 73 × 4 |
| NVM 总预算 | 256 K | byte | 含 4 套候选 LUT + 校验扇区，含弱磁 / MTPV / FW / Derate 4 模式 |
| 写入次数预算 | ≥ 10 000 | 次/年 | NVM 寿命 ≥ 10 年 |
| 写入完整性 | A/B 双 banks + CRC | — | r02 强制 |

---

## 3. 不可破坏边界

1. **退磁优先级最高**：任何 MTPA / FW / MTPV 优化结果若与 `demagnetization_risk` 冲突，必须放弃优化、保安全。
2. **V_margin 阈值不得动态绕过**：r02 标称 5 V，若 r03 要降到 3 V，需先在草案 + 状态机 drawio 同步。
3. **LUT CRC 失败 → fault fallback**：r02 sheet 不允许 "best-effort"；任何 CRC 失败必须切 fault fallback。
4. **温度高于 120 °C 时**：r02 sheet 内的 demag 限值估值不再适用，必须接 S11 thermal 输入；r02 暂禁止 > 120 °C 工况仿真。
5. **`engineering_validated` 不翻转**：本 sheet 与 r03 仿真闭环都不翻转 `engineering_validated`。

---

## 4. 仿真绑定（指向 `V2-S02-PARAM-sim_binding-r02.json`）

仿真入口：

```python
from sim.run_control_lut_generator import run
output = run(
    motor_params_path="models/motor_params.json",
    torque_axis_nm=[50.0, 100.0, 150.0, 200.0],
    temperature_c=80.0,
    demag_limit=DemagLimit(id_min_at_25c_a=-240.0, temp_coefficient=-0.0035),
)
```

期望产物（来源：`models/control_lut_schema.json` 的 `feasibility_map / mode_transitions / validation` 字段）：

| 字段 | 期望 | 容差 |
|---|---|---|
| `feasibility_map.feasible_count` | ≥ 200（73 速度 × 4 转矩 − 不可行点） | r03 校验 |
| `feasibility_map.infeasible_reasons.demagnetization_risk` | ≤ 25 | 单 sheet 限定 |
| `feasibility_map.infeasible_reasons.search_not_converged` | = 0 | 强制 |
| `validation.torque_discontinuity_at_transitions_nm` | ≤ 5.0 N·m | r03 强制 |
| `mode_transitions[*].id_jump_a` | r02 proxy soft gate ≤ 60 A；r03 收敛目标 ≤ 30 A | r02 warn / r03 强制 |
| `mode_transitions[*].iq_jump_a` | r02 proxy soft gate ≤ 60 A；r03 收敛目标 ≤ 30 A | r02 warn / r03 强制 |

---

## 5. DVP&R 验收映射

| DVP ID | 验证项 | 本 sheet 提供的参数 |
|---|---|---|
| S02-DV-001 | MTPA/FW/MTPV 模式切换连续性 | §2.4 模式切换阈值 + §4 mode_transitions 容差 |
| S02-DV-002 | LUT CRC 失败 | §2.6 `lut_crc` + §3 不可破坏边界 #3 |
| S02-DV-003 | LUT 版本不匹配 | §2.6 `lut_version` + §2.7 A/B 双 banks |
| S02-DV-004 | 断电恢复 | §2.7 NVM 写入完整性 |
| S02-DV-005 | 不可行区请求 | §2.5 不可行原因映射 |

DVP&R 文档：`engineering/v2/scheme-02/test_dvpr/V2-S02-TEST-lut_mode_hil-r00.md`。

---

## 6. 待落实（r02 → r03 升级清单）

1. **torque 轴扩展**：当前 LUT 仍是单 torque；r03 必须扩展为 4 点扫描，并落实 §2.3 工程窗。
2. **R_s / L_d / L_q / ψ_f 估值替换**：当前 4 个核心参数为 estimate；r03 必须由 EXP-006 nonlinear flux LUT 或 FEA 标定后替换。
3. **demag limit 估值替换**：当前 `id_min_at_25c_a = -240.0` 与 `temp_coefficient = -0.0035` 为粗估；r03 必须由 S11 thermal 与磁钢供应商曲线替换。
4. **切换跳变收敛**：当前机器绑定使用 60 A 作为 r02 proxy soft gate，文档中的 30 A 保留为 r03 强制目标；不得把 60 A 通过写成生产验收通过。
5. **NVM 预算实测**：当前 256 K + 10 K 写入预算为估值；r03 必须由 MCU NVM 数据表和 LUT 发布频率重新核算。
5. **r01 视觉更新**：T03 状态机 r01 重生后，本 sheet 顶部"概念图"路径要更新为 `-r01.png`。

---

## 7. 版本与变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；建立生产参数 → 仿真绑定主线；4 个核心电机参数仍 estimate；torque 轴扩展为 r03 必修项 |
