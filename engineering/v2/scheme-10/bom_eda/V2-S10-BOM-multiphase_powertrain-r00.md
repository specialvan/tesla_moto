# V2-S10 BOM/EDA 多相动力链草案 r00

方案：S10 多相 / 相组控制  
状态：`draft`，用于 BOM/EDA 风险拆解，不替代采购发布。

## 1. BOM 分类

| 类别 | 关键器件 | 参数字段 | 风险 |
|---|---|---|---|
| Power stage | six-phase module / dual three-phase module | voltage, current per phase, thermal resistance | 成本、封装和热均衡 |
| Gate drive | isolated gate driver x6 | isolation, DESAT, UVLO, Miller clamp | 单相故障误扩散 |
| Current sensing | six phase sensors | bandwidth, accuracy, isolation | xy 子空间观测不足 |
| Fault isolation | fuse, solid-state cutoff, latch | trip time, reset policy, diagnostic coverage | 切除不彻底 |
| Connector/harness | six-phase connector, shielded cable | current, phase keying, vibration | 相序错误和 NVH |
| Thermal sensors | module/phase-group sensors | response time, placement | 单相热点漏检 |

## 2. EDA 约束

- 六相 net name、connector pinout、采样通道必须一一对应。
- 每相 gate-disable latch 独立，同时接入总 safety shutdown。
- alpha-beta 与 xy observer 所需信号必须在 EDA 中明确输出。

## 3. G3 禁止通过项

- BOM 只按三相系统列料。
- 无每相采样和 gate fault 诊断。
- 无 phase keying / 防错连接器。
- 无服务复位策略或故障相隔离器件。
