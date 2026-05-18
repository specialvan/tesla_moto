# S02 DVP&R LUT mode HIL draft

方案：`mtpa_fw_mtpv_control`  
状态：`draft / planned / not executed / not validated`  
范围：DVP&R / HIL 测试协议草案；不是 HIL 执行结果、台架报告或工程验证结论。

## 1. 草案目标

S02 测试草案用于规划 MTPA/FW/MTPV 模式切换、LUT CRC、版本控制、断电恢复和不可行区 fallback 的 HIL 验证。

## 2. 输入证据

| 类型 | 路径 |
|---|---|
| Controller | `../controller/V2-S02-CTRL-mode_transition_lut-r00.drawio` |
| PCB | `../pcb/V2-S02-PCB-control_io_map-r00.md` |
| BOM/EDA | `../bom_eda/V2-S02-EDA-controller_core_bom-r00.md` |
| CAD | `../cad/V2-S02-CAD-controller_packaging-r00.md` |

## 3. Draft DVP&R 矩阵

| ID | 验证项 | 方法 | 期望证据 | 状态 |
|---|---|---|---|---|
| S02-DV-001 | MTPA/FW/MTPV 模式切换连续性 | HIL planned | `mode_state`、`id/iq` jump、torque jump 日志 | planned |
| S02-DV-002 | LUT CRC 失败 | Fault injection planned | fallback map 激活和 DTC 记录 | planned |
| S02-DV-003 | LUT 版本不匹配 | HIL planned | 上电拒绝加载和诊断帧 | planned |
| S02-DV-004 | 断电恢复 | HIL planned | NVM 读取、CRC、mode reset 记录 | planned |
| S02-DV-005 | 不可行区请求 | SIL/HIL planned | infeasible reason 与降额动作记录 | planned |

## 4. 验收前置条件

- 控制 LUT schema 与 HIL 信号表冻结。
- `lut_version`、`lut_crc`、`mode_state` 可被日志采集。
- NVM 写入/读取策略进入测试夹具。
- HIL 模型覆盖速度、转矩、Vdc 和温度输入。

## 5. 未决风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| LUT 维度继续变化 | HIL 脚本不稳定 | 冻结测试 schema |
| NVM 时序未定义 | 断电恢复不可测 | 定义电源循环序列 |
| 模式切换阈值未标定 | jump 验收无基准 | 建立阈值表 |

## 6. 禁止误读

本文件只证明 DVP&R / 测试计划已进入页面级审查；不证明测试已执行、台架已搭建、HIL 已运行、样件已制造、数据已通过、功能安全已认证或工程验证已完成。
