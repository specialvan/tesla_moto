# V2 分方案工程落地 Playbook Wiki

日期：2026-05-15  
来源：`claude-review/docs/2026-05-15/v2_scheme_engineering_playbook.md`

---

## 1. 页面定位

本 Wiki 是 V2 分方案工程落地 playbook 的知识库索引版，用于快速检索每条方案的 V2 定位、下一步动作和阶段门目标。

---

## 2. 总体推进策略

V2 不把所有路线都推向硬件，而是给每条路线明确：

1. 是否进入近期主线；
2. 输入模型和输出接口；
3. BOM/EDA 与控制接口影响；
4. 缺失验证证据；
5. 进入下一门或停止推进条件。

---

## 3. 分方案 V2 定位

| 优先级 | 方案 | V2 定位 | 下一步动作 | 阶段门目标 |
|---|---|---|---|---|
| P0 | 负 d 轴弱磁 | 近期主线 | 安全边界进入 LUT、低压/高温联合扫描 | G3 主线 |
| P0 | MTPA/FW/MTPV | 控制主干出口 | 二维 control LUT、模式连续性、不行原因闭合 | G3 主线 |
| P0 | 非线性磁链 LUT | 高可信模型底座 | FEA/实测导入规范、LUT 模式生成控制 LUT | G3 主线底座 |
| P0 | 温度/退磁安全保护 | 横切强制层 | `id_min(T,fault)`、sensor fault、gate-disable 映射 | G3/G4 前置 |
| P1 | SVPWM/过调制 | 高速区增强项 | THD/NVH/损耗边界和启停窗口 | G3 候选 |
| P1 | 磁路饱和协同 | 中期候选 | candidate geometry → FEA LUT → scorecard | G2-G3 候选 |
| P1 | PMaSynRM | 中期候选拓扑 | PM fraction / ripple / stress / demag scorecard | G2-G3 候选 |
| P1 | Pareto 决策 | 统一决策出口 | 系统损耗 + 成熟度 + 风险评分 | 决策层 |
| P2 | Memory Motor | 研究池重点规范 | 磁状态机、脉冲、状态观测、未知状态回退 | 研究池规范 |
| P2 | 混合励磁 | 重硬件研究候选 | 三变量优化、field converter 损耗和故障 | 研究候选 |
| P2 | 绕组重构 | 研究池 | 切换瞬态、互锁、环流、非法状态 | 研究池 |
| P2 | 多相相组 | 容错需求牵引研究池 | fault torque allocator、资源预算、容错需求 | 研究池 |

---

## 4. 主线四件套

### 4.1 负 d 轴弱磁

- 目标：降低合成 d 轴磁链和端电压压力。
- 必补：`id_min(T,fault)`、油冷边界、Vdc_min、传感器可信度。
- 输出：control LUT 中的 voltage/current/demag/thermal margin。
- 停止条件：弱磁收益小于热/退磁风险或传感器可信度不足。

### 4.2 MTPA/FW/MTPV

- 目标：统一低速效率、中速转矩、高速电压极限。
- 必补：二维速度-转矩 LUT、mode transition、CRC、generator metadata。
- 输出：发布型 control LUT。
- 停止条件：模式边界不连续或不可行区无法解释。

### 4.3 非线性磁链 LUT

- 目标：用 FEA/实测 `lambda_d/lambda_q` 替代线性近似。
- 必补：单位、坐标、峰值/RMS、温度维度、candidate ID。
- 输出：LUT 模式控制轨迹、越界原因、误差报告。
- 停止条件：边界过窄、插值误差不可接受、来源不可信。

### 4.4 温度 / 退磁 / 安全保护

- 目标：成为所有方案进入 G4 前的强制横切层。
- 必补：磁钢温度、油温、sensor fault、gate-disable、fault latch。
- 输出：安全边界过滤、derating、fault injection 证据。
- 停止条件：任何方案不能证明故障安全，不允许进入硬件门。

---

## 5. 中期候选

### 5.1 SVPWM / 过调制

- 定位：高速区附加模式。
- 必补：THD/NVH、逆变器损耗、启停窗口、退出条件。
- 放行：收益超过普通弱磁且 EMC/NVH/热风险可控。

### 5.2 磁路饱和协同

- 定位：候选几何 → FEA LUT → 控制评分。
- 必补：barrier、bridge、FEA LUT、rotor stress、iron loss、demag map。
- 放行：FEA LUT 回灌后控制收益和结构风险都成立。

### 5.3 PMaSynRM

- 定位：高凸极低永磁占比拓扑候选。
- 必补：PM fraction、ripple、stress、demag、扁线/油冷协同。
- 放行：低 PM 成本收益不牺牲主工况效率和峰值转矩。

### 5.4 Pareto 决策

- 定位：所有路线统一决策出口。
- 必补：drive cycle、系统损耗、复杂度、成熟度、制造风险。
- 放行：结论对权重扰动稳定，且证据路径完整。

---

## 6. 研究池 guardrail

### 6.1 Memory Motor

- 禁止误判：不能用 `psi_f` 缩放代表工程可行性。
- 必补：磁状态机、脉冲能量、状态观测、未知状态回退、重复切换寿命。

### 6.2 混合励磁

- 禁止误判：不能只看 `psi_eff = psi_pm + kf * if`。
- 必补：三变量优化、field converter 损耗、field thermal、loss-of-field 故障。

### 6.3 绕组重构

- 禁止误判：不能只看静态 Ke/Kt 缩放。
- 必补：切换瞬态、环流、arc、interlock、open/short/stuck fault。

### 6.4 多相相组

- 禁止误判：不能只用可用电流降额代理。
- 必补：fault torque allocator、harmonic subspace、资源预算、容错需求。

---

## 7. 近期执行顺序

1. 主线四件套闭环：弱磁 + 控制 LUT + 非线性 LUT + 安全保护。
2. 候选 scorecard：FEA LUT、扁线、油冷、系统损耗、NVH、制造风险。
3. 研究池 guardrail：Memory Motor、混合励磁、绕组重构、多相全部设停/进条件。

---

## 8. 最终判断

V2 每个方案的深度推进，不是平均投入，而是把所有方案纳入统一工程纪律：

> 主线先闭环，候选靠 scorecard 晋级，研究池靠 guardrail 防止误判。
