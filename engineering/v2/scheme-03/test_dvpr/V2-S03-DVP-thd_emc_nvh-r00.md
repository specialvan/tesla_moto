# S03 DVP&R THD / EMC / NVH draft

方案：`svpwm_overmodulation_voltage_utilization`
状态：`draft / planned / not executed / not validated`
范围：DVP&R / 调制损耗与谐波测试协议草案；不是 HIL / EMC chamber / 台架结果。

## 1. 草案目标

S03 测试草案用于规划 SVPWM / 过调制 / 六步运行的 THD、EMC、NVH 与逆变器损耗验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S03-CTRL-overmodulation_state_machine-r00.drawio`（待落地） |
| PCB | `../pcb/V2-S03-PCB-gate_pwm_emc-r00.pdf`（待落地） |
| BOM/EDA | `../bom_eda/V2-S03-BOM-inverter_overmodulation-r00.xlsx`（待落地） |
| Parameters | `../parameters/V2-S03-PARAM-acceptance-r02.md` |
| Sim binding | `../parameters/V2-S03-PARAM-sim_binding-r02.json` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S03-DV-001 | THD 测量 | Bench planned | THD ≤ 8 % @ 各 k_mod 点 | planned |
| S03-DV-002 | EMC 合规 EN 55025 Class 5 | Chamber planned | EMI 频谱、传导/辐射记录 | planned |
| S03-DV-003 | NVH 扭矩纹波 ≤ 3 % | Bench planned | 扭矩纹波 vs k_mod 曲线 | planned |
| S03-DV-004 | 逆变器损耗 sweep | Bench planned | 损耗 vs k_mod / 速度 | planned |
| S03-DV-005 | 六步运行热应力 | Bench planned | junction T < 150 °C | planned |

## 4. 验收前置条件

- f_sw = 10 kHz / dead-time = 1.5 μs 冻结。
- THD / EMC / NVH 测量仪器准入。
- 六步运行有限时长（≤ 30 s 单次）和恢复策略冻结。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 六步导致磁钢热点温升 | 退磁风险，与 S11 联动 | 建立 thermal correlation |
| EMC 滤波器尺寸超预算 | PCB / 包装压力 | EMC chamber 早期定测 |
| THD 与 NVH 阈值未台架标定 | 验收无基准 | r03 标定 |

## 6. 禁止误读

本文件只证明 DVP&R / 测试计划已进入页面级审查；不证明测试已执行、台架已搭建、HIL 已运行、样件已制造、数据已通过、功能安全已认证或工程验证已完成。
