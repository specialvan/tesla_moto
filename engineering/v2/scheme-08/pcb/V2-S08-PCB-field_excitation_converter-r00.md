# V2-S08 PCB 励磁变换器草案 r00

方案：S08 混合励磁  
状态：`draft`，用于 EDA/隔离/安全评审输入，不替代正式 PCB 文件。

## 1. 电气页

| 页 | 必含电路 | 生产参数 |
|---|---|---|
| Field DC/DC | 48 V 励磁输入、升降压/全桥、母线保护 | field current -20 A 到 30 A 初值 |
| Field sensing | 励磁电流、电压、绕组温度 | 电流环与热保护闭环 |
| Isolation | HV/LV 隔离、电源隔离、通信隔离 | 隔离耐压按牵引系统等级评审 |
| Loss-of-field | open/short 检测、失励 latch、S11 request | loss-of-field 检出 <5 ms |
| Gate interface | field PWM、enable、fault feedback | 与 traction torque derate 联动 |

## 2. 布局边界

- 励磁功率回路和控制采样链必须分区。
- field current shunt/Hall 到 ADC 路径必须标注滤波与诊断注入点。
- 失励故障输出必须有硬件 latch，不只依赖软件。

## 3. G3 禁止通过项

- 无励磁电流闭环采样。
- 无 loss-of-field 检测链。
- 无隔离边界、爬电距离或故障回退输出。
- 只画 48 V 电源框，不画励磁功率级。

## 4. 下版生图提示词

Generate a white-background engineering schematic titled “S08 Hybrid Excitation Field Converter PCB”. Include 48V field supply, bidirectional field DC/DC or H-bridge, field winding connector, field current sensing, field voltage sensing, winding temperature input, isolated power, isolated communication, loss-of-field detector, hardware fault latch, traction torque derate request, and S11 safety request. Use red fault path, blue control path, amber thermal callouts, readable English labels.
