# 可控磁通量电机技术研究方案

## 1. 研发目标

通过公开物理模型、开源工具链、仿真闭环和 agent/Codex 持续推演，开发一套面向高速工况的等效可控磁通量电机技术路线。

核心目标：

- 高速工况下降低等效合成磁链；
- 降低端电压需求和电压饱和压力；
- 对可变磁化、混合励磁、绕组重构等路线，进一步研究等效 `Ke/ψf` 的真实可调能力；
- 降低弱磁铜耗、铁耗和逆变器电压压力；
- 保持低速大转矩能力；
- 形成可仿真、可标定、可台架验证的工程闭环。

干净室原则：

- 不引用任何闭源实现；
- 不猜测特定厂商真实技术；
- 不复刻不可公开方案；
- 所有结论来自公开方程、开源工具、仿真数据或台架实验。

---

## 2. 核心物理模型

### 2.1 dq 电压方程

完整动态模型：

```text
vd = Rs * id + dλd/dt - ωe * λq
vq = Rs * iq + dλq/dt + ωe * λd
```

准稳态扫描模型：

```text
vd ≈ Rs * id - ωe * λq
vq ≈ Rs * iq + ωe * λd
```

说明：转矩-转速边界、MTPA/FW/MTPV 初版扫描可使用准稳态模型；电流环动态、磁化状态切换、绕组重构切换和故障仿真必须使用完整动态模型。

### 2.2 线性磁链模型

```text
λd = Ld * id + ψf
λq = Lq * iq
```

### 2.3 非线性磁链模型

后续升级为：

```text
λd = LUTd(id, iq, temperature)
λq = LUTq(id, iq, temperature)
```

### 2.4 转矩方程

线性模型：

```text
Te = 1.5 * p * (ψf * iq + (Ld - Lq) * id * iq)
```

非线性磁链表模型：

```text
Te = 1.5 * p * (λd * iq - λq * id)
```

说明：一旦使用 `λd/λq` LUT，控制和验证必须使用非线性转矩表达，不能继续用固定 `Ld/Lq/ψf` 的线性公式。

### 2.5 电压和电流约束

```text
sqrt(vd^2 + vq^2) <= Vmax
sqrt(id^2 + iq^2) <= Imax
ωe = p * ωm
```

首版单位约定：

- dq 变换采用幅值不变形式；
- `id/iq` 使用相电流峰值；
- `vd/vq` 使用相电压峰值；
- `Rs` 为单相电阻，并需要温度修正；
- SVPWM 线性区首版可取 `Vmax = Vdc / sqrt(3)`，过调制时另行定义利用率；
- 所有 LUT、损耗和台架数据必须显式标注坐标系与峰值/RMS 约定。

---

## 3. 技术假设树

### A. 纯控制路线

#### A1. IPMSM 负 d 轴弱磁

机理：

```text
λd = ψf + Ld * id
```

当 `id < 0` 时，定子 d 轴电流降低合成 d 轴磁链和端电压需求。注意：普通 IPMSM 弱磁不改变永磁体本身 `ψf/Ke`；只有可变磁化、混合励磁、绕组重构等路线才可能改变等效 `ψf/Ke`。

优先级：最高。

验证指标：

- 最高速电压裕度；
- 弱磁铜耗；
- 负 id 极限；
- 退磁风险；
- 高速效率。

#### A2. MTPA/FW/MTPV 连续控制

分区：

```text
低速：MTPA
中高速：Field Weakening
极高速：MTPV
```

目标：在电流圆、电压椭圆和转矩曲线之间找到最优运行点。

优先级：最高。

#### A3. SVPWM / 过调制 / 电压利用率提升

机理：提高 `Vmax` 的实际可用比例，降低弱磁压力。

注意：过调制会增加谐波、NVH 和电流畸变。

---

### B. 非线性磁路路线

#### B1. 非线性磁链表

建立：

```text
λd = f(id, iq, T)
λq = f(id, iq, T)
```

用于表达：

- d/q 轴饱和；
- 交叉饱和；
- 温度影响；
- 高电流区转矩误差。

优先级：高。

#### B2. 磁路饱和协同设计

通过 IPMSM / PMaSynRM 的转子磁桥、隔磁槽、磁钢布置，使不同电流角下磁导发生可控变化。

目标：结构不动，但有效磁路随电流状态改变。

验证：

- FEA 磁通路径；
- `Ld/Lq` 随电流变化；
- 转矩脉动；
- 转子强度；
- 磁钢退磁裕度。

---

### C. 真实可变磁链路线

#### C1. 可变磁化状态 / Memory Motor

机理：通过磁化/去磁脉冲改变 `ψf` 档位。

状态：

```text
高磁链：低速大转矩
中磁链：中速高效
低磁链：高速低端电压需求；可变磁化/混合励磁/绕组重构路线才对应低等效 Ke
```

风险：

- 磁化状态难观测；
- 脉冲电流大；
- 高温下状态漂移；
- 不可逆退磁；
- 转矩冲击。

建议：第一阶段只做仿真，不直接做硬件。

#### C2. 混合励磁

机理：

```text
ψeff = ψPM + ψfield(if)
```

通过励磁电流连续调节等效磁链。

风险：

- 励磁损耗；
- 热管理；
- 结构复杂；
- 失励/过励故障。

#### C3. 绕组重构

机理：改变绕组串并联或星三角连接，改变等效匝数和 `Ke/Kt`。

风险：

- 大电流开关；
- 切换瞬态；
- EMI；
- 绝缘压力；
- 故障安全。

---

## 4. 推荐研发路径

### Phase 0：需求冻结

输入：

- 峰值功率；
- 连续功率；
- 峰值转矩；
- 基速；
- 最高速；
- 母线电压范围；
- 最大相电流；
- 冷却条件；
- 电机包络；
- 目标工况。

输出：

- 需求规格；
- 指标体系；
- 风险边界。

---

### Phase 1：线性 dq 仿真闭环

开发内容：

- dq 电机模型；
- 电压/电流限制；
- MTPA；
- 弱磁；
- MTPV；
- 铜耗模型；
- 转矩-转速曲线；
- 高速电压裕度。

成功标准：

- 可以比较 `id=0`、MTPA、FW、MTPV；
- 可以输出最高速、基速、CPSR；
- 可以输出弱磁电流需求；
- 可以判断是否电压越限。

---

### Phase 2：非线性磁链闭环

开发内容：

- `λd(id, iq, T)` 查表；
- `λq(id, iq, T)` 查表；
- LUT 输入轴范围、单位、温度含义、插值方法和边界裁剪；
- 交叉饱和建模；
- 非线性转矩估算；
- 非线性 MTPA/MTPV LUT；
- 参数敏感性分析。

成功标准：

- 转矩估计误差降低；
- 高速电压边界更准确；
- 控制轨迹更接近真实电机能力边界。

---

### Phase 3：电磁设计协同

候选拓扑：

- 高凸极 IPMSM；
- PM-assisted SynRM；
- 低 Ke IPMSM；
- 高弱磁能力 IPMSM；
- 可变磁化状态 PM 预研；
- 混合励磁预研。

开发内容：

- Pyleecan + FEMM 参数扫描；
- SyR-e 拓扑探索；
- `Ke`、`Ld/Lq`、`ψf`、转矩脉动对比；
- 转子强度和退磁风险评估。

---

### Phase 4：可变磁链预研

仿真内容：

- 高/中/低 `ψf` 档位；
- 不同磁链状态下 MTPA/FW/MTPV；
- 高速端电压需求下降比例；
- 真实可变磁链路线的等效 Ke 下降比例；
- 低速转矩损失；
- 切换收益阈值；
- 状态误判风险。

判断：

如果可变 `ψf` 带来的高速效率提升显著大于切换代价，再考虑真实硬件路线。

EXP-002 初步结论：在当前样例参数下，直接降低 `ψf` 会显著损失目标转矩能力。100 Nm 时 `ψf=100%` 可达 6750 rpm，`ψf=85%` 降为 6000 rpm，`ψf=70%/55%` 不可达；40 Nm 低负载时 `ψf=100%` 可达 18000 rpm，`ψf=85%/70%/55%` 分别为 17500/16250/13750 rpm。说明“单纯降低 ψf”不是自动收益，必须与电机拓扑、凸极比、MTPV 轨迹、转矩需求区间和状态切换策略协同设计。

EXP-003 参数族扫描结论：已完成 `ψf/Ld/Lq/Vdc/Imax` 共 108 个缩放组合，评价点为 1000 rpm / 100 Nm 低速峰值和 12000 rpm / 60 Nm 高速目标；`Imax` 放大时同步放大搜索电流网格。当前最高分组合是 `ψf=100%`、`Ld=80%`、`Lq=160%`、`Vdc=115%`、`Imax=115%`，高速 60 Nm 点电压裕度约 4.06 V、电流裕度约 68.58 A，高速最大可行转矩约 80.12 Nm。低 `ψf=70%` 的最佳候选需要同样的高凸极比与较高 `Vdc/Imax`，进入第二名；其高速 60 Nm 点电压裕度约 5.08 V、电流裕度约 74.10 A，高速最大可行转矩约 76.09 Nm。说明低磁链路线不是单独缩小 `ψf`，而是必须与高凸极比、较高母线电压或电流能力协同，才可能保留低速转矩并获得高速电压收益。该结果仍是线性缩放族启发式排序，不代表真实电磁几何，下一步必须用 FEA/Pyleecan/SyR-e 生成非线性 `λd/λq` 表、退磁边界和铁耗/热约束复核。

---

### Phase 5：台架闭环验证

硬件优先级：

1. 低压 VESC/MESC 平台；
2. 编码器 PMSM/IPMSM；
3. 低压安全弱磁验证；
4. 后续再进入高压高速平台。

验证步骤：

- 编码器零位；
- FOC 电流环；
- 速度环；
- 参数辨识；
- MTPA；
- 弱磁；
- MTPV；
- 日志采集；
- 模型回灌。

---

## 5. 实验矩阵

| 编号 | 实验 | 输入 | 输出 | 判定 |
|---|---|---|---|---|
| EXP-01 | 线性 dq 基线 | Rs/Ld/Lq/ψf/Vdc/Imax | 转矩-转速、电压裕度 | 可完成全速域扫描 |
| EXP-02 | 弱磁扫描 | id、iq、speed | 最高速、铜耗、V裕度 | 高速不越压 |
| EXP-03 | MTPV 寻优 | speed、Imax、Vmax | 最优 id/iq | 高速转矩提升 |
| EXP-04 | 非线性磁链 | λd/λq LUT | 转矩误差、效率 | 优于线性模型 |
| EXP-05 | 可变 ψf | ψf 档位、转矩目标 | Ke、CPSR、铜耗、负 id | 当前样例显示低 ψf 会损失转矩能力，需协同设计 |
| EXP-06 | 参数族协同扫描 | ψf/Ld/Lq/Vdc/Imax 缩放族 | 候选排序、高速电压裕度、低速转矩能力 | 低 ψf 需高凸极比和 Vdc/Imax 协同 |
| EXP-07 | 热降额 | 损耗、Rth/Cth | 温升、连续功率 | 不超温 |
| EXP-08 | 工况加权 | 车辆工况 | 加权效率 | 优于基线 |
| EXP-09 | 故障边界 | 低 Vdc、高温、传感器误差 | 保护响应 | 安全降级 |

---

## 6. 关键指标

### 6.1 磁链控制能力

```text
FluxRange = (λmax - λmin) / λnom
KeRange = (Kemax - Kemin) / Kenom
CPSR = ωmax / ωbase
```

### 6.2 电压裕度

```text
MarginV = Vmax - sqrt(vd^2 + vq^2)
```

### 6.3 电流裕度

```text
MarginI = Imax - sqrt(id^2 + iq^2)
```

### 6.4 铜耗

```text
Pcu = 3 * Irms^2 * Rs
```

### 6.5 工况加权效率

```text
ηweighted = Σ wk * ηk
```

### 6.6 退磁裕度

必须覆盖：

- 高温；
- 最大负 id；
- 短路；
- 过流；
- 低 Vdc + 高转速下的电压饱和和弱磁失败；
- 高速再生、负载突卸、电池拒充下的母线过压。

安全优先级：

1. 硬件保护；
2. 退磁保护；
3. 电压/电流限制；
4. 热限制；
5. 扭矩可控性；
6. 效率优化。

MTPA/FW/MTPV 是正常工况优化策略，不能覆盖保护逻辑。

---

## 7. 开源工具链

### 控制仿真

- Python dq model；
- motulator；
- OpenModelica。

### 电磁仿真

- Pyleecan + FEMM；
- SyR-e；
- FEMM；
- Elmer FEM。

### 固件参考

- VESC；
- MESC；
- SimpleFOC 仅用于低压教学验证；
- OpenInverter 适合高压逆变器生态参考，不作为 FOC 主线。

### 数据沉淀

建议目录：

```text
wiki/
  controllable_flux_motor_research_plan.md
experiments/
  exp_001_linear_dq/
  exp_002_field_weakening/
  exp_003_param_sweep/
models/
  motor_params.json
  flux_lut_schema.json
sim/
  dq_model.py
  mtpa.py
  field_weakening.py
  mtpv.py
reports/
  figures/
  html/
```

---

## 8. Agent / Codex 并行推演任务

### Agent A：控制算法

任务：

- 实现 MTPA 求解；
- 实现电压闭环弱磁；
- 实现 MTPV 搜索；
- 输出 `id/iq` 轨迹 LUT；
- 验证电压/电流约束。

交付：

```text
sim/mtpa.py
sim/field_weakening.py
sim/mtpv.py
experiments/exp_003_param_sweep/summary.json
```

---

### Agent B：电磁参数与磁链表

任务：

- 定义电机参数 schema；
- 定义 `λd/λq` LUT schema；
- 对接 Pyleecan/FEMM 输出；
- 生成线性和非线性参数样例。

交付：

```text
models/motor_params.json
models/flux_lut_schema.json
experiments/exp_004_flux_lut/
```

---

### Agent C：损耗与热模型

任务：

- 铜耗模型；
- 铁耗近似模型；
- 逆变器损耗占位模型；
- 一阶热模型；
- 热降额策略。

交付：

```text
sim/losses.py
sim/thermal.py
experiments/exp_006_thermal/results.json
```

---

### Agent D：可变磁链模型

任务：

- `ψf` 多档模型；
- 高/中/低磁链效率对比；
- 切换收益阈值；
- 状态误判风险分析。

交付：

```text
sim/variable_flux.py
experiments/exp_005_variable_psi/
```

---

### Agent E：验证和可视化

任务：

- 生成转矩-转速曲线；
- 生成效率地图；
- 汇总实验结果；
- 更新 HTML 知识库；
- 更新 wiki。

交付：

```text
reports/figures/
reports/html/
controllable_flux_motor_kb.html
wiki/controllable_flux_motor_research_plan.md
```

---

### Codex：代码实现协作

AI/Codex 输出仅作为研发草案。任何控制策略、参数表或固件实现都必须经过人工审查、单元测试、仿真验证、低压台架验证和硬件保护验证，禁止直接部署到高压高速实机。

建议 Codex 按 wiki 拆分任务并行实现：

1. 先实现 `dq_model.py`；
2. 再实现 `mtpa.py`；
3. 再实现 `field_weakening.py`；
4. 再实现 `mtpv.py`；
5. 再实现 `losses.py` 和 `thermal.py`；
6. 最后实现可视化和实验 runner。

每个模块必须配套：

- 单元测试；
- 参数样例；
- 实验 runner；
- JSON/CSV 结果输出。

---

## 9. 第一批最小实现任务

### T1：建立电机参数 schema

字段：

```text
name
pole_pairs
Rs
Ld
Lq
psi_f
Vdc
Imax
speed_max_rpm
torque_target_nm
temperature_c
```

### T2：实现线性 dq 计算

函数：

```text
flux_d(id)
flux_q(iq)
voltage_d(id, iq, omega_e)
voltage_q(id, iq, omega_e)
torque(id, iq)
```

### T3：实现 MTPA 扫描版

先不用解析式，直接在电流圆内网格搜索最小电流转矩点。

### T4：实现弱磁扫描

给定 speed 和 torque，搜索满足电压约束的最优 `id/iq`。

### T5：实现 MTPV 扫描

给定 speed，搜索电压和电流约束下最大转矩点。

### T6：输出第一版报告

图表：

- 转矩-转速曲线；
- id/iq vs speed；
- 电压裕度 vs speed；
- 铜耗 vs speed；
- 基线 vs 弱磁 vs MTPV 对比。

---

## 10. 参考资料与状态标记

状态标记：

- `HYP`：理论假设，尚未仿真；
- `SIM`：已有仿真验证；
- `FEA`：已有有限元验证；
- `BENCH`：已有台架验证。

当前文档大部分路线处于 `HYP`，后续每个实验结果必须回填状态、参数版本和数据路径。

公开工具和资料入口：

- VESC：开源 FOC/弱磁控制固件参考；
- MESC：开源 PMSM/BLDC 控制固件参考；
- motulator：Python 电机驱动仿真；
- Pyleecan + FEMM：开源电机电磁设计与 2D FEA 工作流；
- SyR-e：同步磁阻/IPM/PMaSynRM 设计探索；
- OpenModelica：系统级电机模型和控制示例。

---

## 11. 当前推荐结论

短期最可行路线：

```text
高凸极 IPMSM / PMaSynRM
+ MTPA / FW / MTPV
+ 非线性磁链表
+ 电压利用率提升
+ 温度/退磁保护
```

中期突破路线：

```text
磁路饱和协同设计
+ 非线性控制 LUT
+ 工况加权效率优化
```

长期高风险高收益路线：

```text
可变磁化状态
或 混合励磁
或 绕组重构/多相控制
```

研发策略：

1. 先用仿真逼近理论边界；
2. 再用 FEA 填充真实磁链表；
3. 再用低压台架验证控制；
4. 最后进入真实可变磁链硬件路线。
