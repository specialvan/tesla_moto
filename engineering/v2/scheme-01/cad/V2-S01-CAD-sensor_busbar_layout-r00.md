# S01 CAD sensor / busbar layout boundary draft

方案：`negative_d_axis_field_weakening`  
状态：`draft`  
范围：3D/CAD 封装边界草案；不是 STEP、Parasolid、SolidWorks、Motor-CAD 或制造发布文件。

## 1. 草案目标

S01 的 CAD 草案用于定义弱磁控制所需电流/Vdc/温度传感器、三相母排和安全关断相关线束的早期封装边界。

## 2. 关联图纸包

| 类型 | 路径 | 作用 |
|---|---|---|
| Controller | `../controller/V2-S01-CTRL-field_weakening_state_machine-r00.drawio` | 定义弱磁和 fault fallback 状态 |
| PCB | `../pcb/V2-S01-PCB-sensing_fault_path-r00.md` | 定义采样和 fault latch 接口 |
| BOM/EDA | `../bom_eda/V2-S01-BOM-sensing_fault_components-r00.md` | 定义器件族风险 |

## 3. 封装边界草案

| 边界项 | 当前草案 | 未决项 |
|---|---|---|
| 三相母排走向 | 逆变器到电机端子需预留电流传感器窗口 | 母排截面、叠层和固定点未定 |
| 电流传感器安装 | 需保证可拆装和 Kelvin/屏蔽路径 | 传感器类型未定 |
| 温度传感器位置 | 至少区分电机侧和逆变器侧温度输入 | 热点代表性未验证 |
| LV/HV 分区 | 低压采样线束与高压母排需有 keep-out | 爬电/电气间隙未计算 |
| Service access | fault latch/诊断接口需可接入调试 | 维修空间未定义 |

## 4. Keep-out / 装配问题

| 问题 | 影响 | 下一步 |
|---|---|---|
| 母排与传感器间隙未知 | 影响装配和绝缘 | 建立母排 CAD 初稿 |
| 温度传感器固定方式未知 | 影响热响应和可靠性 | 与 S11 热路径联审 |
| 线束弯折半径未知 | 影响封装和维修 | 定义连接器方向 |

## 5. CAD 前置输入

- 电机端子和逆变器输出端子 datum。
- 母排电流等级和绝缘层方案。
- 传感器封装尺寸、安装孔和线束出口。
- 热传感器安装点和线束路径。

## 6. 禁止误读

本文件只证明 3D/CAD 封装边界已进入页面级审查；不证明真实 STEP、Parasolid、SolidWorks、Motor-CAD/Maxwell 几何、装配公差、结构强度、热仿真、FEA 网格或制造发布已完成。
