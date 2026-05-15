# S01 PCB sensing / fault path page draft

方案：`negative_d_axis_field_weakening`  
状态：`draft`  
范围：页面级 PCB 接口草案；不是 EDA 原理图、Layout、Gerber、ODB++ 或制造发布文件。

## 1. 页级目标

S01 的 PCB 页级目标是把弱磁控制所需观测量、fault latch 和硬件关断路径在电气接口上闭合，支撑 `V2-S01-CTRL-field_weakening_state_machine-r00.drawio` 的状态机评审。

## 2. 信号 / 接口清单

| 接口组 | 信号 | 方向 | 采样/动作目标 | 当前状态 |
|---|---|---|---|---|
| Phase current | `ia/ib/ic` | Power stage -> MCU ADC | 弱磁电流环、过流诊断 | 待选型 |
| DC bus | `vdc_sense` | DC link -> MCU ADC | 电压裕度和过调制边界 | 待分压设计 |
| Temperature | `motor_temp`, `inverter_temp` | Sensor -> MCU ADC | `id_min(T,fault)` 限幅输入 | 待传感器布置 |
| Gate disable | `gate_disable_n` | MCU/Safety -> Gate driver | fault fallback 硬件关断 | 待锁存方案 |
| Fault latch | `fault_latched` | Safety latch -> MCU | 区分可恢复与锁存故障 | 待诊断覆盖 |

## 3. 页级约束

| 约束 | 草案要求 | 未决项 |
|---|---|---|
| 采样同步 | 电流采样需与 PWM 中点或安全采样窗口绑定 | PWM 频率和 ADC 触发尚未冻结 |
| Kelvin 采样 | 分流/霍尔传感器回路需避免功率回流耦合 | 传感器类型未定 |
| 安全关断 | `gate_disable_n` 必须不依赖主循环软件执行 | 硬件锁存器件未选型 |
| 诊断路径 | ADC 越界、传感器开短路和 latch 状态必须可读回 | 诊断阈值未标定 |

## 4. 评审风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 采样延迟过大 | 弱磁区电压裕度判断滞后 | 建立 ADC/PWM 时序预算 |
| 温度输入不可信 | `id_min(T,fault)` 限幅失效 | 与 S11 安全页复用温度诊断 |
| gate disable 未硬件锁存 | 故障时可能依赖固件循环 | 输出锁存与看门狗页级设计 |

## 5. 禁止误读

本文件只证明 S01 PCB 采样与故障路径已有页面级审查草案；不证明 ERC/DRC、隔离距离、热设计、BOM、Layout 或制造文件已完成。
