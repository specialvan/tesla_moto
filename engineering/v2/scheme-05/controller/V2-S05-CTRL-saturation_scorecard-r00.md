# V2-S05 控制器/scorecard 饱和协同草案 r00

状态：`draft`。

## 1. 输入输出链路

```text
candidate geometry version
  -> Maxwell/Motor-CAD nonlinear flux LUT
  -> constrained id/iq search
  -> drive-cycle weighted score
  -> stress/demag/NVH penalty
  -> engineering recommendation or stop
```

## 2. Scorecard 字段

| 字段 | 单位 | 来源 | Gate |
|---|---:|---|---|
| `weighted_efficiency_gain_pct` | % | drive-cycle simulation | G3 |
| `peak_torque_margin_nm` | Nm | FEA + control search | G3 |
| `torque_ripple_pct` | % | FEA/NVH proxy | G3 |
| `iron_loss_delta_w` | W | iron loss model | G3 |
| `demag_margin_pct` | % | S11 boundary | G4 |
| `stress_safety_factor` | ratio | rotor stress FEA | G4 |
| `manufacturing_risk_score` | 1~5 | process review | G4 |

## 3. 控制器约束

- 控制 LUT 必须使用 FEA 回灌的非线性磁链表。
- MTPA/MTPV 轨迹必须输出可审查的 `id/iq` 连续性和 torque jump。
- 若任一候选在 S11 退磁边界下不可行，scorecard 自动降级。

## 4. 下版生图提示词

生成 S05 saturation co-design scorecard flowchart，展示 Geometry Candidate、FEA Flux LUT、Constrained id/iq Search、Drive-cycle Weighted Efficiency、Torque Ripple、Iron Loss、Demag Margin、Rotor Stress、Manufacturing Risk、Gate Decision。白底流程图，英文标签，红色 stop gates，蓝色数据流。