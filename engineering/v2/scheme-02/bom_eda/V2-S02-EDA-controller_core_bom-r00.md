# S02 BOM/EDA controller core risk draft

方案：`mtpa_fw_mtpv_control`  
状态：`draft`  
范围：BOM/EDA 风险登记草案；不是 XLSX BOM、EDA netlist、采购清单或制造发布文件。

## 1. 草案目标

S02 的 BOM/EDA 草案用于识别 MTPA/FW/MTPV 控制核心所需 MCU、NVM、ADC、位置接口和通信器件风险，支撑 LUT 发布与 HIL 测试规划。

## 2. 器件族风险清单

| 器件族 | 作用 | 主要风险 | 下一步 |
|---|---|---|---|
| MCU / timer PWM | FOC、模式切换和诊断 | PWM/ADC 资源不足 | 建立 pin mux 和时序预算 |
| NVM / flash | LUT、CRC、版本号和标定页 | 容量、擦写寿命、掉电一致性 | 估算 LUT size 和写入策略 |
| Resolver / encoder front-end | 位置和速度估计 | 延迟和噪声影响 MTPV | 确定接口芯片和滤波 |
| CAN/CAN-FD transceiver | 标定、诊断和模式发布 | EMC、唤醒、总线故障策略未定 | 对齐整车诊断需求 |
| ADC reference / front-end | 电流/Vdc/温度采样 | 参考漂移导致模式抖动 | 建立采样链误差预算 |

## 3. EDA 页面映射

| EDA 页 | S02 需求 | 当前状态 |
|---|---|---|
| `06_MCU_Control` | MCU、PWM、ADC、NVM、时钟、复位 | 待原理图 |
| `08_Comms_Debug` | CAN/CAN-FD、XCP/UDS、调试口 | 待原理图 |
| `04_Current_Voltage_Sense` | 控制 LUT 输入采样 | 待原理图 |

## 4. 验收前置条件

- 完成 LUT 容量、CRC 和版本字段预算。
- 输出 MCU pin mux、ADC trigger 和 PWM 资源表。
- 明确通信诊断与 fallback map 发布路径。
- 与 `V2-S02-PCB-control_io_map-r00.md` 和控制器状态机闭合。

## 5. 禁止误读

本文件只证明 BOM/EDA 风险已进入页面级审查；不证明真实 XLSX BOM、EDA 原理图、netlist、封装库、pick-place、Gerber、ODB++、成本报价、供应链冻结或制造发布已完成。
