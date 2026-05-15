# S02 PCB control I/O map page draft

方案：`mtpa_fw_mtpv_control`  
状态：`draft`  
范围：页面级 PCB 控制 I/O 草案；不是 EDA 原理图、Layout、Gerber、ODB++ 或制造发布文件。

## 1. 页级目标

S02 的 PCB 页级目标是把 MTPA/FW/MTPV LUT、模式切换、CRC 校验和标定接口所需的 MCU/NVM/ADC/通信资源映射到可评审接口。

## 2. 控制 I/O 清单

| 接口组 | 信号 / 资源 | 方向 | 用途 | 当前状态 |
|---|---|---|---|---|
| MCU PWM | `pwm_u/v/w_hi/lo` | MCU -> Gate driver | FOC 和弱磁输出 | 待 PWM 资源冻结 |
| ADC | `ia/ib/ic`, `vdc`, `temp_*` | Sensors -> MCU | LUT 可行性和安全边界输入 | 待通道分配 |
| Position | `resolver_sin/cos` 或 encoder | Sensor -> MCU | dq 变换和速度估计 | 接口待定 |
| NVM | `lut_flash`, `calib_page` | MCU <-> NVM | 控制 LUT、CRC、版本号 | 容量待确认 |
| Comms | CAN/CAN-FD, XCP/UDS | MCU <-> Vehicle | 标定、诊断和模式发布 | 协议待冻结 |

## 3. 版本与诊断字段

| 字段 | 目的 | 草案要求 |
|---|---|---|
| `lut_version` | 绑定控制 LUT 文件版本 | 上电读取并进入诊断帧 |
| `lut_crc` | 防止标定表损坏 | CRC fail 进入 fallback map |
| `mode_state` | 区分 MTPA/FW/MTPV | 可被 HIL 和日志采集 |
| `infeasible_reason` | 对齐 control LUT 不可行原因 | 输出到诊断缓冲区 |

## 4. 评审风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| NVM 容量不足 | 二维 LUT 或多温度切片无法发布 | 建立 LUT size budget |
| ADC 触发与 PWM 不一致 | 模式切换判断抖动 | 建立采样时序表 |
| CRC 失败路径不明确 | 上电可能加载错误标定 | 与控制器状态机联审 |

## 5. 禁止误读

本文件只证明 S02 控制 I/O 和 LUT 发布接口已有页面级草案；不证明 MCU 选型、PCB pin mux、BOM、Layout 或 HIL 结果已完成。
