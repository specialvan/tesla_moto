# S04 CAD FEA geometry source boundary draft

方案：`nonlinear_flux_lut`  
状态：`draft`  
范围：3D/CAD/FEA 几何源边界草案；不是 STEP、Parasolid、SolidWorks、Motor-CAD、Maxwell 或 FEA 网格文件。

## 1. 草案目标

S04 的 CAD 草案用于定义非线性磁链 LUT 所需 FEA 几何源、dq 坐标、材料、传感器位置和版本绑定边界。

## 2. 关联图纸包

| 类型 | 路径 | 作用 |
|---|---|---|
| Controller | `../controller/V2-S04-CTRL-flux_lut_interpolation-r00.drawio` | 定义 LUT 插值和 fallback |
| PCB | `../pcb/V2-S04-PCB-lut_observer_inputs-r00.md` | 定义 LUT 观测输入 |
| BOM/EDA | `../bom_eda/V2-S04-BOM-lut_sensor_chain-r00.md` | 定义观测链器件族风险 |

## 3. 几何源边界草案

| 边界项 | 当前草案 | 未决项 |
|---|---|---|
| FEA 几何版本 | LUT 必须绑定几何源版本和单位 | 尚无 Motor-CAD/Maxwell 几何 |
| dq 坐标定义 | `id/iq` 坐标方向需与控制器一致 | 坐标零位和角度约定未冻结 |
| 材料表 | 磁钢、硅钢、铜、温度曲线需版本化 | 材料牌号和 BH 曲线未定 |
| 网格/边界条件 | LUT 生成需记录网格和求解设置 | 尚无 FEA 网格 |
| 传感器位置 | 温度/位置输入需映射到几何位置 | 传感器 CAD 未定义 |

## 4. Keep-out / 装配问题

| 问题 | 影响 | 下一步 |
|---|---|---|
| 几何版本未冻结 | LUT 不能工程发布 | 建立 CAD/FEA version tag |
| 材料曲线缺失 | 磁链表不可信 | 引入材料数据源 |
| 传感器位置未绑定 | 温度修正无工程含义 | 与 S11 热路径联审 |

## 5. CAD 前置输入

- Motor-CAD/Maxwell 几何源路径和版本号。
- 材料牌号、温度曲线和坐标约定。
- FEA 网格、边界条件、求解设置记录。
- 与 `models/flux_lut_sample.json` 的 schema 映射关系。

## 6. 禁止误读

本文件只证明 3D/CAD 封装边界已进入页面级审查；不证明真实 STEP、Parasolid、SolidWorks、Motor-CAD/Maxwell 几何、装配公差、结构强度、热仿真、FEA 网格或制造发布已完成。
