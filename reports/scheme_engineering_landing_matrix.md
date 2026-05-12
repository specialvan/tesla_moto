# 可控磁通量方案工程落地矩阵

本文把每条技术路线从概念方案落到工程交付物。每个方案必须具备模型、实验、验收标准、失败模式、阶段门和交付件，才允许进入下一阶段。

| 方案 ID | 工程定位 | 必须具备的落地能力 | 当前阶段门 |
|---|---|---|---|
| `negative_d_axis_field_weakening` | 控制型等效控磁主线 | dq 模型、负 id 扫描、Vdc_min 扫描、退磁边界 | 通过高温/低压/id_min(T) 后进入台架 |
| `mtpa_fw_mtpv_control` | 全速域控制轨迹 | MTPA/FW/MTPV LUT、不可行区标记、降额策略 | LUT 连续性和转矩台阶合格后进入标定 |
| `svpwm_overmodulation_voltage_utilization` | 逆变器电压利用增强 | 调制因子扫描、谐波损耗估算、NVH 预筛 | 证明净效率收益后进入控制实现 |
| `nonlinear_flux_lut` | 磁链数据主线 | LUT schema、插值器、边界裁剪、非线性转矩公式 | schema 和越界行为测试通过后接 FEA |
| `magnetic_saturation_codesign` | 电磁协同设计 | FEA 候选、磁链表回灌、强度/退磁评分 | FEA-LUT 回灌后优于基线才细化 |
| `pmasynrm_high_saliency_low_pm` | 低 Ke 高凸极拓扑 | 永磁占比扫描、凸极比扫描、转矩脉动筛选 | 低速转矩、高速裕度和 NVH 同时合格 |
| `variable_magnetization_memory_motor` | 真实可变磁链预研 | 多档 ψf 仿真、状态误判表、脉冲能量估算 | 状态观测和脉冲应力路径明确前不进硬件 |
| `hybrid_excitation` | 连续真实调磁预研 | if 扫描、励磁损耗、热模型、失励故障 | 总损耗优于弱磁主线才继续 |
| `winding_reconfiguration` | 真实 Ke/Kt 重构预研 | 多配置参数、切换点、瞬态和故障分析 | 收益覆盖高压开关复杂度才继续 |
| `multiphase_phase_group_control` | 架构/容错路线 | 相组模型、缺相能力、热分配、谐波控制 | 产品明确需要容错或相组收益才继续 |
| `thermal_demag_safety_protection` | 横向安全层 | Rs(T)、ψf(T)、id_min(T)、热降额、故障边界 | 所有方案进入台架前必须具备 |
| `weighted_efficiency_pareto_selection` | 决策层 | 工况权重、加权效率、风险复杂度、Pareto 前沿 | 任一方案升级前必须通过 scorecard |

## 落地顺序

1. 先把 `negative_d_axis_field_weakening`、`mtpa_fw_mtpv_control` 和 `thermal_demag_safety_protection` 串成闭环。
2. 再接入 `nonlinear_flux_lut`，把线性模型升级成可回灌 FEA/台架数据的模型。
3. 然后用 `weighted_efficiency_pareto_selection` 对比主线、增强线和预研线。
4. 最后只把 scorecard 明确胜出的方案推进到驱动硬件、台架或样机设计。

## 强制要求

- 所有方案必须有可运行脚本或可追溯数据文件。
- 所有图表必须标明单位、坐标系和模型边界。
- 所有驱动方案必须有驱动设计图、上电时序图和协议链路图。
- 高压实机前必须完成安全保护层，不允许只凭效率优化结果上电。
