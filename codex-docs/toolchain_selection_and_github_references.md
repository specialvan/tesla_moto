# 高保真仿真工具链选型与 GitHub 参考项目

## 1. 结论

Codex 侧仿真方案不应只押注单一工具。推荐采用分层工具链：

| 层级 | 推荐工具 | 用途 | 进入条件 | 输出 |
|---|---|---|---|---|
| L0 系统/控制预研 | Python dq / MATLAB / Simulink / motulator | 快速验证 FOC、SVPWM、MTPA、弱磁、MTPV、MRAS、无速度传感器控制 | 参数还未冻结 | 控制策略、边界趋势、初始 LUT |
| L1 快速电机设计 | Ansys Motor-CAD | 拓扑、尺寸、绕组、热、损耗、效率图、驱动循环 | 已有目标功率/扭矩/速度/电压 | 初始几何、效率图、热边界、候选设计 |
| L2 高保真电磁 | Ansys Maxwell 2D/3D | PMSM/BLDC/SRM/IM/DC/直线电机电磁 FEA | 候选设计需要工程判定 | 反电势、齿槽转矩、转矩脉动、LUT、退磁、铁耗、力波 |
| L3 多物理 | Maxwell + Motor-CAD + Mechanical / CFD / Icepak / NVH | 热、结构、振动噪声、冷却和应力闭环 | L2 结果已稳定 | 热包络、NVH、转子应力、冷却方案 |
| L4 控制/HIL/嵌入式 | Simulink / Motor Control Blockset / MCU SDK / HIL | 代码生成、半实物、控制器验证 | 控制策略需要上板 | FOC/SVPWM/弱磁代码、HIL 测试报告 |

关键判断：

- “Maxwell 电机仿真设计”和“Ansys Maxwell”工程上应视为同一高保真电磁 FEA 路线。
- Motor-CAD 不是 Maxwell 的替代品，而是前期快速设计和多物理初筛工具。
- Maxwell 负责最终电磁可信度，Motor-CAD 负责快速拓扑和效率/热/NVH 初筛。
- MATLAB/Simulink 负责控制、功率电子、HIL 和报告级仿真。
- Pyleecan/FEMM/motulator 等开源项目用于可复核基准、二次开发和算法回归，不直接替代商业 FEA 的工程释放。

## 2. 工具能力分工

### 2.1 Ansys Maxwell

用途：

- PMSM、BLDC、开关磁阻电机、异步电机、直流电机、直线电机的 2D/3D 电磁 FEA；
- 反电势、齿槽转矩、平均转矩、转矩脉动；
- `Ld/Lq`、非线性 `lambda_d/lambda_q` LUT；
- 永磁体退磁、铁耗、AC loss、力波、磁致伸缩/NVH 输入；
- 与 Mechanical、Icepak、CFD、Motion、Twin Builder 等工具联动。

项目中应作为：

- 电磁设计最终判定工具；
- EXP-006 非线性磁链 LUT 的真实数据来源；
- EXP-004 退磁边界的真实数据来源；
- EXP-009 多相相组失效下开相电压矢量和力波验证工具。

### 2.2 Ansys Motor-CAD

用途：

- 初始电机拓扑和尺寸快速建模；
- 电磁、热、机械、效率图、连续/峰值转矩速度曲线；
- 驱动循环、温度相关性能、弱磁能力初筛；
- 与 Maxwell 做高保真电磁联动。

项目中应作为：

- EXP-003 参数族从“缩放代理”升级为“几何候选族”的入口；
- EXP-005 过调制/效率图联合评估的性能图来源；
- EXP-007 混合励磁热包络和励磁损耗评估入口；
- EXP-008 绕组重构热、损耗和效率包络初筛入口。

### 2.3 MATLAB / Simulink

用途：

- FOC、SVPWM、SPWM、弱磁、MTPA、MTPV、MRAS、无速度传感器控制；
- 三相 PWM 整流器、逆变器、buck/boost、隔离变换器、开关电源；
- 控制器离散化、代码生成、HIL、数据导出 Excel；
- Multisim/电路理论/模电/数电实验类模型可作为电路级教学和局部验证补充。

项目中应作为：

- 控制策略验证和 HIL 主线；
- EXP-010 Pareto 评分中的驱动循环和控制约束来源；
- EDA/BOM 前的电源、采样、调制、保护逻辑验证平台。

## 3. GitHub 参考项目清单

| 项目 | 链接 | 可参考内容 | 适用方式 |
|---|---|---|---|
| PyAEDT | https://github.com/ansys/pyaedt | Python 自动化 AEDT，覆盖 Maxwell 2D/3D/RMxprt | 自动建模、批量扫参、导出 Maxwell 结果 |
| PyMotorCAD | https://github.com/ansys/pymotorcad | Python 控制 Motor-CAD，本地或远程连接 Motor-CAD 实例 | 自动生成 Motor-CAD 参数族、效率图、热分析 |
| Pyleecan | https://github.com/Eomys/pyleecan | 开源电机多物理设计与优化框架，集成 FEMM/GMSH | 复现实验、开源基线、非商业建模参考 |
| motulator | https://github.com/Aalto-Electric-Drives/motulator | Python 电机驱动和并网变换器仿真，含 PMSM 等模型和控制示例 | 控制算法回归、FOC/弱磁/MTPV 策略验证 |
| MathWorks FOC-of-PMSM | https://github.com/mathworks/FOC-of-PMSM | 基于 NXP 开发套件的 PMSM/BLDC FOC 示例 | Simulink 控制、代码生成、MCU 上板链路参考 |
| Microchip PMSM FOC Simulink IPS | https://github.com/microchip-pic-avr-solutions/matlab-mclv48v300w-33ak128mc106-pmsm-foc-ips | PMSM FOC 的 MATLAB/Simulink 模型 | 传感器 FOC、硬件接口、报告模板参考 |
| Microchip PMSM FOC Simulink SMO | https://github.com/microchip-pic-avr-solutions/matlab-mclv48v300w-33ak128mc106-pmsm-foc-smo | 基于滑模观测器的无感 FOC Simulink 模型 | 无速度传感器、SMO、参数调试参考 |
| Microchip AN1292 dsPIC PMSM FOC | https://github.com/microchip-pic-avr-solutions/mclv-48v-300w-an1292-dspic33ck256mc506 | PMSM 传感器less FOC 与 PLL estimator / field weakening 应用 | 嵌入式 FOC、弱磁、固件结构参考 |
| SimpleFOC / Arduino-FOC | https://github.com/simplefoc/Arduino-FOC | BLDC/Stepper FOC 控制库，硬件组合覆盖广 | 低压样机、控制概念验证、快速硬件试验 |

## 4. 不同电机类型的落地路线

| 电机类型 | 初筛 | 高保真 | 控制验证 | 关键输出 |
|---|---|---|---|---|
| 永磁同步电机 PMSM/IPMSM | Motor-CAD + dq | Maxwell 2D/3D | Simulink / motulator | `lambda_d/lambda_q`、效率图、弱磁边界 |
| BLDC | Motor-CAD | Maxwell 2D | SimpleFOC / Simulink | 反电势、换相/FOC 对比、转矩脉动 |
| 开关磁阻电机 SRM | Motor-CAD 初筛 | Maxwell 2D/3D | Simulink | `L(theta,i)`、转矩脉动、噪声 |
| 异步电机 IM | Motor-CAD | Maxwell 2D/3D | motulator / Simulink | 等效电路、损耗图、热包络 |
| 直流电机 | Maxwell 2D | Maxwell 3D 局部 | Simulink | 换向、磁路、损耗 |
| 直线电机 | Maxwell 2D/3D | Maxwell 3D | Simulink | 推力、端部效应、力波 |
| 主驱电机 | Motor-CAD | Maxwell + Mechanical + CFD/NVH | Simulink/HIL | 峰值/连续能力、热、NVH、结构应力 |

## 5. 对当前 EXP-001 到 EXP-010 的升级映射

| 当前实验 | 下一阶段工具 | 升级目标 |
|---|---|---|
| EXP-001 线性 dq | Maxwell + Motor-CAD | 用 FEA/性能图替代固定 `Ld/Lq/psi_f` |
| EXP-002 可变磁链 | Maxwell | 建立不同磁化状态的真实磁链图 |
| EXP-003 参数族 | Motor-CAD + Maxwell | 用几何族替代缩放参数族 |
| EXP-004 热/退磁 | Maxwell + Motor-CAD Thermal | 用磁钢退磁曲线和温度场替代简化 `id_min(T)` |
| EXP-005 过调制 | Simulink + Maxwell loss map | 加入 PWM 波形、电流纹波、器件损耗 |
| EXP-006 非线性 LUT | Maxwell 2D/3D | 输出 `lambda_d/lambda_q(id,iq,T)` |
| EXP-007 混合励磁 | Maxwell + Motor-CAD Thermal | 励磁绕组、热耦合、效率收益 |
| EXP-008 绕组重构 | Maxwell + Motor-CAD | 多接法绕组参数、切换瞬态风险 |
| EXP-009 多相相组 | Maxwell + Simulink | 开相电压矢量、相组降额、力波/NVH |
| EXP-010 Pareto | Motor-CAD maps + Simulink drive cycle | 工况能耗、成本、质量和风险评分 |

## 6. 质量门槛

### 6.1 电磁仿真

- 几何、材料、叠压系数、磁钢牌号、温度、绕组连接必须显式版本化。
- 2D 模型必须说明周期边界、端部修正和斜极处理。
- 3D 模型必须说明端部效应、端部绕组、冷却结构和网格收敛。
- 输出至少包括：反电势、平均转矩、转矩脉动、齿槽转矩、铁耗、铜耗、效率图、退磁裕度、`lambda_d/lambda_q`。

### 6.2 热/结构/NVH

- 热模型必须区分峰值工况、连续工况和驱动循环。
- 转子应力必须覆盖最高转速、过速安全系数和磁钢保持结构。
- NVH 必须从 Maxwell 力波或 Motor-CAD NVH 输入追溯，不允许只做经验判断。

### 6.3 控制和电力电子

- FOC/SVPWM/MTPA/弱磁必须与电机 LUT、逆变器电压限制、电流限制和温度限制一致。
- 无速度传感器方案必须给出低速启动、切换、失锁和重捕获策略。
- HIL/半实物必须包含过流、过压、欠压、过温、编码器/传感器故障、相缺失。

### 6.4 报告交付

中文仿真设计技术报告至少包含：

1. 设计目标和输入约束；
2. 工具链和版本；
3. 电机几何和材料；
4. 电磁仿真设置；
5. 热/结构/NVH 设置；
6. 控制策略和功率电子模型；
7. 结果表和图；
8. 与 EXP-001 到 EXP-010 的追踪关系；
9. 风险、限制和下一步台架验证计划；
10. 附录：脚本、参数、模型版本、数据导出路径。

## 7. 当前决策

Codex 侧采用：

```text
Motor-CAD 快速多物理筛选
  -> Maxwell 2D/3D 高保真电磁验证
  -> Simulink / motulator 控制与功率电子验证
  -> Mechanical / CFD / Icepak / NVH 多物理闭环
  -> HIL / 台架验证
```

开源 GitHub 项目只作为参考实现、回归基准和报告证据来源；最终工程释放必须依赖可追溯的商业 FEA、台架和设计评审数据。

## 8. 外部资料来源

- Ansys Maxwell: https://www.ansys.com/products/electronics/ansys-maxwell
- Ansys Motor-CAD: https://www.ansys.com/products/electronics/ansys-motor-cad
- PyAEDT: https://github.com/ansys/pyaedt
- PyMotorCAD: https://github.com/ansys/pymotorcad
- Pyleecan: https://github.com/Eomys/pyleecan
- motulator: https://github.com/Aalto-Electric-Drives/motulator
- MathWorks FOC-of-PMSM: https://github.com/mathworks/FOC-of-PMSM
- Microchip PMSM FOC examples: https://github.com/microchip-pic-avr-solutions
- SimpleFOC: https://github.com/simplefoc/Arduino-FOC
