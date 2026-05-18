# V2-S03 BOM/EDA 过调制逆变器风险登记 r00

状态：`draft`，用于供应链和 EDA 评审输入，不替代正式 XLSX BOM、网表或制造包。

## 1. 关键器件族

| 类别 | 生产参数字段 | 风险 | 必需证据 |
|---|---|---|---|
| Power module | voltage/current rating、switching loss、thermal resistance | 深过调制热脉冲 | datasheet + loss map + thermal stack |
| Gate driver | isolation、UVLO、DESAT、Miller clamp | 高 dv/dt 误触发 | CMTI、故障关断时序 |
| DC-link capacitor | capacitance、ESR、ripple current、lifetime | 纹波温升和寿命 | ripple calc、thermal derating |
| Busbar | inductance、insulation、creepage | 过压尖峰/EMC | 3D loop review、HiPot |
| Current sensor | bandwidth、delay、range、offset drift | 采样窗口不足 | ADC timing、calibration plan |
| EMI filter/shield | CM/DM attenuation、grounding | EMC 失败 | pre-scan plan、shield bonding |

## 2. EDA 字段要求

- 每个保护器件必须有 `ASIL_relevance`、`diagnostic_coverage`、`fault_injection_point`。
- 每个 HV 器件必须有 `voltage_rating_v`、`temperature_rating_c`、`creepage_class`。
- 每个采样链器件必须有 `gain_error_pct`、`delay_us`、`bandwidth_khz`。

## 3. 停止条件

1. 功率模块无损耗图或热阻链路。
2. Gate driver 无 DESAT/UVLO/Miller clamp 说明。
3. DC-link 电容无纹波电流与寿命降额。
4. EMC 器件无预扫计划或屏蔽连接定义。

## 4. 下版生图提示词

生成 S03 inverter BOM/EDA 风险矩阵图，展示 power module、gate driver、DC-link capacitor、laminated busbar、current sensor、EMI filter/shield 六类器件，列出 voltage/current/thermal/EMC/diagnostic 字段和 gate evidence。白底表格风格，工业工程文档质感，英文标签。