# V2-S03 PCB Gate/PWM/EMC 页级图纸草案 r00

方案：S03 SVPWM / 过调制  
状态：`draft`，用于设计评审输入，不替代正式 Altium/KiCad 原理图、Layout、Gerber 或 EMC 报告。

## 1. 生产参数边界

| 参数 | r00 目标 | 约束来源 | 评审动作 |
|---|---:|---|---|
| DC bus 标称 | 360 V | `models/motor_params.json` / EXP-005 | 与 DC-link 电容耐压、纹波和热模型绑定 |
| 调制因子窗口 | `k_mod <= 1.15` | `experiments/exp_005_modulation_factor/summary.json` | 超过线性区必须触发 THD/NVH/EMC 复核 |
| PWM 采样窗口 | 中点采样优先，过调制区重建降级 | 控制器状态机 | 标注电流采样盲区和 fallback |
| Gate-disable 链路 | 硬件优先关断 | S11 safety chain | 与 fault latch、DC-link UV/OV、过温闭合 |
| EMC 风险等级 | high | 过调制边沿与六步切换 | 必须进入 G4 EMC 预扫 |

## 2. PCB 页面分解

| 页 | 页名 | 必含对象 | 禁止缺项 |
|---|---|---|---|
| S03-PCB-01 | Gate driver isolated power | 隔离电源、UVLO、DESAT/OC、Miller clamp | 无 UVLO 或无关断回读 |
| S03-PCB-02 | Phase current sampling | 三相电流、采样保持、ADC 同步触发 | 无过调制采样窗口标注 |
| S03-PCB-03 | DC-link sensing | Vdc 分压、纹波采样、OV/UV 比较器 | 无硬件阈值和软件阈值关系 |
| S03-PCB-04 | PWM/EMC boundary | gate resistor、snubber、共模路径、屏蔽接地 | 无 dv/dt 控制策略 |
| S03-PCB-05 | Fault latch interface | gate-disable、fault feedback、S11 安全链接口 | 软件关断替代硬件关断 |

## 3. 版图约束

- Gate driver 到功率模块回路必须短、对称、可量测。
- 相电流采样路径与高 dv/dt 节点分区布线。
- DC-link 电容、母排和功率模块的高频回路必须在 CAD 包中同步标注。
- 过调制/六步模式不得绕过硬件过流、DESAT、UVLO 和 gate-disable。

## 4. DRC/ERC 进入条件

1. 每个 gate 输出具备驱动阻值、下拉、Miller 抑制和故障回读字段。
2. 每个采样通道具备量程、带宽、延迟、温漂和 ADC 同步约束。
3. 每个保护阈值具备硬件值、软件值、标定名和测试注入点。
4. EMC 页能追踪到屏蔽、接地、滤波和线束出口。

## 5. 下版生图/EDA 提示词

生成一页汽车牵引逆变器 PCB 原理图风格工程图，主题为“S03 SVPWM overmodulation gate/PWM/EMC interface”。画面包含隔离 gate driver、三相电流采样、DC-link 采样、UVLO/DESAT、gate-disable fault latch、EMI 滤波和屏蔽接地分区。所有信号用英文工程标签标注，突出 PWM sampling window、overmodulation fallback、hardware shutdown path。要求白底、细线、可读标注、无营销风格、无虚构品牌。