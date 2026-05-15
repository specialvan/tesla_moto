# S11 PCB safety fault latch page draft

方案：`thermal_demag_safety_protection`  
状态：`draft`  
范围：页面级 PCB 安全链草案；不是 EDA 原理图、Layout、Gerber、ODB++、ASIL 认证或制造发布文件。

## 1. 页级目标

S11 的 PCB 页级目标是定义温度、退磁和 gate-disable 相关安全链路，使故障检测、锁存、降额和硬件关断路径可以被独立审查。

## 2. 安全链接口清单

| 接口组 | 信号 | 方向 | 安全目标 | 当前状态 |
|---|---|---|---|---|
| Magnet temperature | `pm_temp_*` | Sensor -> Safety/MCU | 退磁风险判断 | 安装点待 CAD |
| Winding/oil temperature | `winding_temp`, `oil_temp` | Sensor -> MCU | 热降额与故障触发 | 传感器类型未定 |
| Demag limiter | `id_min_allowed` | Safety logic -> Control | 限制负 d 轴电流 | 与控制 LUT 待绑定 |
| Gate disable | `gate_disable_n` | Safety latch -> Gate driver | 硬件关断 | 锁存器件未选 |
| Fault feedback | `fault_latched`, `fault_reason` | Safety latch -> MCU | 诊断与复位策略 | reason 编码待定 |

## 3. 故障分类

| 故障 | 草案动作 | 复位要求 |
|---|---|---|
| 温度 warning | 扭矩降额 | 自动恢复需滞回 |
| 温度 critical | gate-disable 或锁存降额 | 需人工/诊断复位 |
| 传感器开短路 | unknown sensor fallback | 复位前保持保守限值 |
| demag margin 低 | 限制 `id` 负向命令 | 需记录事件 |
| gate driver fault | 立即关断并锁存 | 需故障清除流程 |

## 4. 评审风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 温度传感器位置不代表磁钢热点 | 退磁保护误判 | 与 CAD/热模型联合评审 |
| gate-disable 只由 MCU 软件驱动 | 安全关断不独立 | 增加硬件 latch/watchdog 方案 |
| fault reason 不可追溯 | DVP&R 无法复现 | 定义故障编码和日志字段 |

## 5. 禁止误读

本文件只证明 S11 安全链已有页面级 PCB 草案；不证明 ASIL 分析、FMEDA、ERC/DRC、器件选型、PCB Layout 或故障注入测试已完成。
