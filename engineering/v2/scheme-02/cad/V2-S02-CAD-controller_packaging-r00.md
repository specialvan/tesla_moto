# S02 CAD controller packaging boundary draft

方案：`mtpa_fw_mtpv_control`  
状态：`draft`  
范围：3D/CAD 封装边界草案；不是 STEP、Parasolid、SolidWorks、Motor-CAD 或制造发布文件。

## 1. 草案目标

S02 的 CAD 草案用于定义控制器壳体、MCU/NVM/通信接口、接插件、线束出口和散热路径的早期封装约束。

## 2. 关联图纸包

| 类型 | 路径 | 作用 |
|---|---|---|
| Controller | `../controller/V2-S02-CTRL-mode_transition_lut-r00.drawio` | 定义 MTPA/FW/MTPV 模式切换 |
| PCB | `../pcb/V2-S02-PCB-control_io_map-r00.md` | 定义 MCU/NVM/ADC/通信接口 |
| BOM/EDA | `../bom_eda/V2-S02-EDA-controller_core_bom-r00.md` | 定义控制核心器件族风险 |

## 3. 封装边界草案

| 边界项 | 当前草案 | 未决项 |
|---|---|---|
| 控制器壳体 | 需容纳 MCU、NVM、通信和采样连接器区域 | 壳体尺寸和安装 datum 未定 |
| 接插件方向 | CAN、调试口和传感器线束需避免 HV 母排干扰 | 连接器规格未定 |
| 散热路径 | MCU/收发器/NVM 热路径需到壳体或冷却板 | 热耗散功率未估算 |
| 维修访问 | 标定/调试接口需可服务 | 服务面和防水等级未定 |
| EMI 分区 | 通信、ADC 和 PWM 输出需分区 | 屏蔽和接地策略未定 |

## 4. Keep-out / 装配问题

| 问题 | 影响 | 下一步 |
|---|---|---|
| 线束半径未知 | 影响整车布置和维修 | 定义 harness bend radius |
| 控制器散热界面未知 | 影响 LUT 高负载稳定性 | 建立热耗预算 |
| 调试口位置未知 | 影响 HIL/台架标定 | 定义 service access envelope |

## 5. CAD 前置输入

- 控制器 PCB 外形与安装孔草案。
- 接插件型号、出线方向和防水等级。
- MCU/NVM/通信器件热耗估算。
- 整车控制器安装 datum 和线束约束。

## 6. 禁止误读

本文件只证明 3D/CAD 封装边界已进入页面级审查；不证明真实 STEP、Parasolid、SolidWorks、Motor-CAD/Maxwell 几何、装配公差、结构强度、热仿真、FEA 网格或制造发布已完成。
