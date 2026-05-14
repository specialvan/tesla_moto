# 高保真仿真工具链选型与 GitHub 参考项目

## 1. 结论

Claude 主线采用分层工具链，不押注单一软件：

| 层级 | 推荐工具 | 用途 | 输出 |
|---|---|---|---|
| L0 系统/控制预研 | Python dq / MATLAB / Simulink / motulator | FOC、SVPWM、MTPA、弱磁、MTPV、MRAS、无速度传感器控制 | 控制策略、边界趋势、初始 LUT |
| L1 快速电机设计 | Ansys Motor-CAD | 拓扑、尺寸、绕组、热、损耗、效率图、驱动循环 | 初始几何、效率图、热边界、候选设计 |
| L2 高保真电磁 | Ansys Maxwell 2D/3D | PMSM/BLDC/SRM/IM/DC/直线电机电磁 FEA | 反电势、齿槽转矩、转矩脉动、LUT、退磁、铁耗、力波 |
| L3 多物理 | Maxwell + Motor-CAD + Mechanical / Fluent / Icepak / NVH | 热、结构、振动噪声、冷却和应力闭环 | 热包络、NVH、转子应力、冷却方案 |
| L4 控制/HIL/嵌入式 | Simulink / Motor Control Blockset / MCU SDK / HIL | 代码生成、半实物、控制器验证 | FOC/SVPWM/弱磁代码、HIL 测试报告 |

关键判断：

- “Maxwell 电机仿真设计”和“Ansys Maxwell”工程上应视为同一高保真电磁 FEA 路线。
- Motor-CAD 不是 Maxwell 的替代品，而是前期快速设计和多物理初筛工具。
- Maxwell 负责最终电磁可信度，Motor-CAD 负责快速拓扑、效率、热和初步 NVH 风险筛选。
- MATLAB/Simulink 负责控制、功率电子、HIL 和报告级仿真。
- PyAEDT 是 Python 自动化 Maxwell / AEDT 的主入口；PyFluent 是 Python 自动化 Fluent 的主入口，适合水套、油冷、风冷、流阻和换热 CFD，不用于直接控制 Maxwell 电磁求解。
- Pyleecan/FEMM/SyR-e/motulator 等开源项目用于可复核基准、二次开发和算法回归，不直接替代商业 FEA 的工程释放。

## 2. GitHub 参考项目清单

| 项目 | 链接 | 可参考内容 | 适用方式 |
|---|---|---|---|
| PyAEDT | https://github.com/ansys/pyaedt | Python 自动化 AEDT，覆盖 Maxwell 2D/3D/RMxprt | 自动建模、批量扫参、导出 Maxwell 结果 |
| PyMotorCAD | https://github.com/ansys/pymotorcad | Python 控制 Motor-CAD，本地或远程连接 Motor-CAD 实例 | 自动生成 Motor-CAD 参数族、效率图、热分析 |
| PyFluent | https://github.com/ansys/pyfluent | Python 自动化 Ansys Fluent | 冷却流道、油冷/水冷/风冷、换热和压降 CFD；接收 Maxwell/Motor-CAD 损耗作为热源 |
| Pyleecan | https://github.com/Eomys/pyleecan | 开源电机多物理设计与优化框架，集成 FEMM/GMSH | 复现实验、开源基线、非商业建模参考 |
| SyR-e | https://github.com/SyR-e/syre_public | Matlab/Octave 电机设计平台，覆盖 SynRM、PMaSynRM、IPM、SPM | 高凸极、PMaSynRM、低永磁路线参考 |
| FEMM | https://github.com/cenit/FEMM | 2D 磁场有限元求解器 | 开源复核和低成本教学验证 |
| motulator | https://github.com/Aalto-Electric-Drives/motulator | Python 电机驱动和并网变换器仿真，含 PMSM 控制示例 | 控制算法回归、FOC/弱磁/MTPV 策略验证 |
| MathWorks FOC-of-PMSM | https://github.com/mathworks/FOC-of-PMSM | 基于 NXP 开发套件的 PMSM/BLDC FOC 示例 | Simulink 控制、代码生成、MCU 上板链路参考 |
| MathWorks PMSM Drive Optimization | https://github.com/mathworks/pmsm-drive-optimization | PMSM 驱动模型和控制参数优化 | 驱动效率、控制参数优化参考 |
| FOC_PMSM | https://github.com/juancnustes/FOC_PMSM | PMSM FOC Simulink 模型 | 学习型 FOC 仿真结构参考 |
| SVPWM Inverter Simulink | https://github.com/ACHKHE/Simulation-of-SVPWM-Inverter-on-Simulink-MATLAB | SVPWM 逆变器仿真 | 调制策略和逆变器模型参考 |
| BLDC Motor Control FOC | https://github.com/EFeru/bldc-motor-control-FOC | BLDC/FOC Simulink 和硬件部署参考 | BLDC/FOC 控制迁移参考 |
| SimpleFOC / Arduino-FOC | https://github.com/simplefoc/Arduino-FOC | BLDC/Stepper FOC 控制库 | 低压样机、控制概念验证、快速硬件试验 |
| FPGA-FOC | https://github.com/WangXuan95/FPGA-FOC | FPGA FOC/SVPWM | 高速控制实现参考 |
| PMSM Maxwell 优化案例 | https://github.com/toohidsharifi/Optimal-design-of-Permanent-Magnet-Synchronous-Motor | MATLAB + Ansys Maxwell 耦合优化 PMSM | Maxwell 优化流程参考 |
| SRM 优化案例 | https://github.com/toohidsharifi/Optimal-design-of-switch-reluctance-motor | 开关磁阻电机转矩脉动优化 | SRM 优化参考 |

## 3. 不同电机类型的落地路线

| 电机类型 | 初筛 | 高保真 | 控制验证 | 关键输出 |
|---|---|---|---|---|
| 永磁同步电机 PMSM/IPMSM | Motor-CAD + dq | Maxwell 2D/3D | Simulink / motulator | `lambda_d/lambda_q`、效率图、弱磁边界 |
| BLDC | Motor-CAD | Maxwell 2D | SimpleFOC / Simulink | 反电势、换相/FOC 对比、转矩脉动 |
| 开关磁阻电机 SRM | Motor-CAD 初筛 | Maxwell 2D/3D | Simulink | `L(theta,i)`、转矩脉动、噪声 |
| 异步电机 IM | Motor-CAD | Maxwell 2D/3D | motulator / Simulink | 等效电路、损耗图、热包络 |
| 直流电机 | Maxwell 2D | Maxwell 3D 局部 | Simulink | 换向、磁路、损耗 |
| 直线电机 | Maxwell 2D/3D | Maxwell 3D | Simulink | 推力、端部效应、力波 |
| 主驱电机 | Motor-CAD | Maxwell + Mechanical + CFD/NVH | Simulink/HIL | 峰值/连续能力、热、NVH、结构应力 |

## 4. 对当前 EXP-001 到 EXP-004 的升级映射

| 当前实验 | 下一阶段工具 | 升级目标 |
|---|---|---|
| EXP-001 线性 dq | Maxwell + Motor-CAD | 用 FEA/性能图替代固定 `Ld/Lq/psi_f` |
| EXP-002 可变磁链 | Maxwell | 建立不同磁化状态或低 Ke 候选拓扑的真实磁链图 |
| EXP-003 参数族 | Motor-CAD + Maxwell | 用几何族替代缩放参数族 |
| EXP-004 热/退磁 | Maxwell + Motor-CAD Thermal | 用磁钢退磁曲线和温度场替代简化 `id_min(T)` |

## 5. 质量门槛

- 几何、材料、叠压系数、磁钢牌号、温度、绕组连接必须显式版本化。
- 2D 模型必须说明周期边界、端部修正和斜极处理。
- 3D 模型必须说明端部效应、端部绕组、冷却结构和网格收敛。
- 输出至少包括反电势、平均转矩、转矩脉动、齿槽转矩、铁耗、铜耗、效率图、退磁裕度、`lambda_d/lambda_q`。
- 热模型必须区分峰值工况、连续工况和驱动循环。
- 转子应力必须覆盖最高转速、过速安全系数和磁钢保持结构。
- FOC/SVPWM/MTPA/弱磁必须与电机 LUT、逆变器电压限制、电流限制和温度限制一致。

## 6. 中文报告交付要求

中文仿真设计技术报告至少包含：设计目标和输入约束、工具链和版本、电机几何和材料、电磁仿真设置、热/结构/NVH 设置、控制策略和功率电子模型、结果表和图、与 EXP-001 到 EXP-004 的追踪关系、风险限制和下一步台架验证计划、附录脚本参数和数据导出路径。
