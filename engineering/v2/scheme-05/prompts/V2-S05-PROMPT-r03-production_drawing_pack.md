# V2-S05 r03 生产参数化生图提示词包

目标：把 S05 从参数缩放/scorecard 方案升级为可审查的 rotor barrier、FEA LUT、材料 BOM 和 DVP 证据图。

## 通用负面约束

- 不要只画磁力线概念图，必须有 barrier/bridge/rib/magnet pocket 标注。
- 不要把 EXP-003 参数趋势画成真实几何验证。
- 不要省略 stress、demag、iron loss、manufacturing risk。

## 图 1：Rotor barrier/bridge CAD+FEA

Prompt: Generate a four-panel engineering drawing titled “S05 Magnetic Saturation Co-design Geometry”. Panels: rotor cross-section with barrier/bridge/rib/magnet pocket/airgap labels; flux density overlay; high-speed stress hotspot overlay; manufacturing minimum web and bridge width callouts. White background, CAD/FEA technical style, English labels.

## 图 2：Saturation scorecard flow

Prompt: Generate a flowchart titled “S05 Saturation Co-design Scorecard”. Flow: Geometry Candidate Version -> Maxwell/Motor-CAD Nonlinear Flux LUT -> Constrained id/iq Search -> Drive-cycle Weighted Efficiency -> Torque Ripple -> Iron Loss -> Demag Margin -> Rotor Stress -> Manufacturing Risk -> Gate Decision. Red stop gates, blue data flow, white background.

## 图 3：Magnetic stack BOM risk table

Prompt: Generate a technical BOM risk matrix titled “S05 Magnetic Stack BOM and Manufacturing Risk”. Rows: electrical steel, magnet, lamination tooling, rotor assembly, sensor interface. Columns: production parameter, risk, required evidence, gate status. Use readable English labels and engineering document styling.

## 图 4：Evidence traceability

Prompt: Generate a traceability diagram titled “S05 Evidence Chain: Parameter Trend to FEA-backed Candidate”. Flow: EXP-003 parameter trend -> rotor CAD candidates -> FEA flux LUT -> stress FEA -> iron loss -> demag boundary -> control scorecard -> DVP gate. Include callout “no parameter-scaling shortcut”.