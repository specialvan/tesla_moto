# Maxwell / Motor-CAD 电机仿真设计落地方案

## 1. 结论

当前可控磁通量电机项目建议采用：

```text
Ansys Motor-CAD + Ansys Maxwell 2D/3D 作为工程主线
Pyleecan/FEMM/SyR-e 作为开源前置验证与干净室复核
MATLAB/Simulink + Python 作为控制、系统级和自动化数据闭环
```

正确分工：

- Motor-CAD：快速尺寸设计、热/效率地图预筛、参数族扫描。
- Maxwell 2D：主电磁 FEA，输出反电势、转矩、Ld/Lq、`lambda_d/lambda_q`、铁耗、退磁裕度。
- Maxwell 3D：端部效应、斜槽/斜极、局部饱和、端部漏磁、复杂结构复核。
- Simulink/Python：FOC、SVPWM、MTPA、弱磁、MTPV、热降额、系统级闭环。
- Pyleecan/FEMM/SyR-e：开源参考、候选拓扑预筛、干净室可复现验证。

## 2. 推荐总流程

```text
需求冻结
  ↓
Motor-CAD 初始电机设计
  ↓
Maxwell 2D 电磁有限元验证
  ↓
导出 Ke、Kt、Ld/Lq、lambda_d/lambda_q、铁耗、转矩脉动、退磁裕度
  ↓
Python / Simulink 控制仿真
  ↓
MTPA / 弱磁 / MTPV / SVPWM / 热降额策略
  ↓
Maxwell 3D / Mechanical / 热仿真复核
  ↓
中文技术报告、参数表、仿真图、控制策略和下一轮优化
```

## 3. 分阶段落地方案

### Phase A：需求与边界冻结

输入：峰值转矩、连续转矩、峰值功率、连续功率、最高转速、基速、DC 母线电压范围、最大相电流、冷却条件、电机外径/叠长/轴径/安装空间、目标工况权重、成本和材料约束。

输出：`target_spec.md`、电机类型初选、极槽方案候选、安全边界定义、仿真验收指标。

### Phase B：Motor-CAD 快速预设计

目标：快速筛选尺寸、极槽、绕组、磁钢、热路径和效率地图。

输出：初始几何尺寸、极槽组合、绕组方案、磁钢厚度和布置、初步效率地图、连续功率热能力、导出到 Maxwell 的候选方案。

### Phase C：Maxwell 2D 主电磁仿真

必须完成：空载磁密分布、空载反电势 `Ke`、齿槽转矩、负载转矩、转矩脉动、`Ld/Lq` 参数识别、`lambda_d(id, iq)` / `lambda_q(id, iq)` 扫描、铁耗、铜耗、退磁裕度、不同温度下磁钢工作点。

输出文件建议：

```text
maxwell/2d/results/back_emf.csv
maxwell/2d/results/cogging_torque.csv
maxwell/2d/results/torque_map.csv
maxwell/2d/results/lambda_dq_map.csv
maxwell/2d/results/ld_lq_map.csv
maxwell/2d/results/iron_loss_map.csv
maxwell/2d/results/demag_margin.csv
```

### Phase D：控制仿真闭环

把 Maxwell / Motor-CAD 输出接入现有 Python 和 Simulink 控制模型。

当前项目最优先：

```text
lambda_d/lambda_q LUT
→ 非线性转矩模型
→ MTPA/FW/MTPV 查表
→ 电压/电流/退磁/热约束
→ 工况加权效率
```

### Phase E：热、结构和 NVH 复核

- 热分析：绕组铜耗、铁耗、磁钢涡流损耗、轴承/风摩损耗、壳体/水套/油冷或风冷路径、连续功率温升、热降额曲线。
- 结构分析：转子最高速应力、磁钢固定安全系数、磁桥强度、套筒或胶层约束、模态。
- NVH：齿槽转矩、转矩脉动、径向电磁力波、定子模态耦合风险、SVPWM/过调制谐波影响。

## 4. 与当前 EXP-001~EXP-004 的衔接

| 当前实验 | 当前模型 | Maxwell/Motor-CAD 后续替换 |
|---|---|---|
| EXP-001 | 线性 dq | 用真实 `Ld/Lq/Ke/Rs` 标定基线 |
| EXP-002 | 虚拟 `psi_f` 缩放 | 用不同磁钢/磁化状态/拓扑输出真实 `Ke/psi_f` |
| EXP-003 | `psi_f/Ld/Lq/Vdc/Imax` 独立缩放 | 用真实 FEA 参数族替换缩放代理 |
| EXP-004 | 简化热/退磁边界 | 用 Motor-CAD 热和 Maxwell 退磁结果替换简化线 |

核心新增证据：

```text
lambda_d(id, iq, T)
lambda_q(id, iq, T)
Ke(speed, T)
Tavg(id, iq)
Tripple(id, iq)
IronLoss(speed, id, iq)
DemagMargin(id, iq, T)
```

## 5. 当前项目的第一优先级

```text
高凸极 IPMSM / PMaSynRM
+ Maxwell 2D lambda_d/lambda_q FEA
+ Motor-CAD 热/效率地图
+ Python/Simulink MTPA/FW/MTPV
+ 退磁与热安全边界
```

第一轮交付物：Motor-CAD 初始设计文件、Maxwell 2D 参数化模型、`lambda_d/lambda_q` LUT、转矩-转速曲线、效率地图、退磁裕度表、Python/Simulink 控制闭环、中文电磁 + 控制 + 热安全技术报告。

## 6. 风险边界

- Maxwell / Motor-CAD 输出仍需网格无关性检查和材料参数确认。
- 2D 结果不能完全替代 3D 端部、斜槽和局部结构效应。
- 开源项目只能作为参考和复核，不能直接替代正式工程验证。
- Simulink 控制通过不代表实机可直接上高压。
- 所有高压高速测试必须经过硬件保护、低压台架、绝缘、热、过速、过压和退磁验证。
