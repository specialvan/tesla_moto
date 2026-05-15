# V2：review-pr 工程落地差距 Wiki

日期：2026-05-15  
来源：`claude-review/docs/2026-05-15/v2_review_pr_engineering_prd.md`  
输入资料：

- `review-pr/这是奇瑞公司的可变磁通电机，技术思路非常巧妙.html`
- `review-pr/新能源汽车驱动电机系列（）——驱动电机发展趋势（扁线、油冷、多合一）.html`

---

## 1. 页面定位

本 Wiki 是 V2 PRD 的知识库版，用于把 `review-pr` 两篇外部资料沉淀成可检索、可交接的工程落地差距。

V2 不推翻 v0.3 主线，而是在 v0.3 的“弱磁 + 连续控制 + 非线性磁链 LUT + 安全保护”之上，补齐真实电驱工程需要的两类约束：

1. 可变磁通 / 电磁调磁必须从 `psi_f` 档位假设升级为磁状态机、安全保护和状态观测问题。
2. 扁线 / 油冷 / 多合一必须从行业趋势背景升级为 G2-G6 阶段门、BOM/EDA、热管理和台架验证问题。

---

## 2. V2 总结论

| 方向 | 当前仓库已有 | 真实工程差距 | V2 定位 |
|---|---|---|---|
| 负 d 轴弱磁 | 线性 dq、控制 LUT、安全边界雏形 | 需要把热/退磁/Vdc 约束并入主线 LUT | 近期主线 |
| MTPA/FW/MTPV | 控制轨迹导出基础 | 需要二维速度-转矩 LUT、连续性、不可行原因 | 近期主线 |
| 非线性磁链 LUT | schema、插值、搜索接入证据 | 需要 FEA/实测来源和候选电机 ID | 近期主线底座 |
| 温度/退磁保护 | 简化 `Rs(T)`、`psi_f(T)`、`id_min(T)` | 需要材料/FEA/台架来源和故障注入 | 横切必做 |
| Memory Motor / 电磁调磁 | `psi_f` 档位数值假设 | 缺磁化脉冲、状态保持、观测、回退、寿命 | 研究池重点规范 |
| 扁线/油冷/多合一 | BOM/EDA 目录级雏形 | 缺绕组几何、油冷热边界、页级交付物、DVP&R | 系统工程阶段门 |

---

## 3. review-pr 条目化映射

### 3.1 资料 A：可变磁通 / 电磁调磁

| 条目 | 外部资料主张 | 当前状态 | V2 要求 |
|---|---|---|---|
| A-1 | 电磁脉冲改变等效磁通 | 仅有静态 `psi_f` 档位 | 增加磁化/去磁脉冲能量、电流、电压、时间 |
| A-2 | 低速高磁链、高速低磁链 | 弱磁与变量磁链实验分离 | 区分负 `id` 弱磁和真实磁状态改变 |
| A-3 | 磁状态需要保持和重复切换 | 无保持、漂移、寿命模型 | 定义保持时间、漂移、重复切换寿命 |
| A-4 | 无机械调磁但控制更复杂 | 无状态机和回退策略 | 定义磁状态机、禁止区、fallback state |
| A-5 | 高速收益受退磁和电压裕度约束 | 只有简化 demag limit | 将磁状态、温度、Vdc、退磁统一进入 LUT 过滤 |
| A-6 | 工程价值取决于可控可观测可保护 | 只有数值假设 | 禁止把 `psi_f` 缩放实验写成工程可行性证明 |

### 3.2 资料 B：扁线 / 油冷 / 多合一

| 条目 | 外部资料主张 | 当前状态 | V2 要求 |
|---|---|---|---|
| B-1 | 扁线提升槽满率和功率密度 | 电机参数无绕组几何 | 增加绕组类型、槽满率、导体截面、端部长度 |
| B-2 | 扁线带来 AC 铜耗、制造和 NVH 风险 | 损耗模型仍简化 | scorecard 加入 AC 铜耗、制造风险、NVH 风险 |
| B-3 | 油冷支撑高热流密度 | 只有简化温度模型 | 增加油温、流量、压力、喷油/甩油路径 |
| B-4 | 磁钢温度约束退磁边界 | `id_min(T)` 来源简化 | demag curve 必须追溯材料、FEA 或台架数据 |
| B-5 | 多合一集成耦合热、EMC、NVH、服务性 | BOM/EDA 只有目录级规划 | 输出页级 BOM/EDA、接口、接地、连接器和冷却约束 |
| B-6 | 量产放行依赖硬证据 | 仓库主要是数值仿真 | numeric simulation 不能替代 G4-G7 证据 |
| B-7 | 高效率要看系统损耗 | 未覆盖逆变器/机械/油泵/冷却惩罚 | Pareto 增加 system loss breakdown |

---

## 4. V2 功能需求索引

| ID | 名称 | 最小输出 |
|---|---|---|
| FR-1 | 磁状态机与电磁调磁研究接口 | `flux_state_id`、脉冲能量、观测可信度、fallback state |
| FR-2 | 扁线绕组与铜耗工程输入 | 绕组类型、槽满率、AC/DC 铜耗、制造风险 |
| FR-3 | 油冷与热-退磁边界输入 | 油温、流量、压力、磁钢温度、demag curve 来源 |
| FR-4 | 多合一系统接口与 BOM/EDA 页级需求 | gate driver、sensing、DC-link、oil pump、fault latch、connector 页面 |
| FR-5 | 系统损耗与 Pareto 决策升级 | copper/iron/inverter/mechanical/oil pump/cooling loss 与成熟度评分 |

---

## 5. 阶段门更新

| 阶段门 | V2 新增要求 |
|---|---|
| G0-G1 | 明确目标车型、冷却架构、是否允许磁状态切换、安全目标和故障回退 |
| G2 | 做机械调磁 vs 电磁调磁、扁线 vs 圆线、水套 vs 油冷、多合一接口 trade study |
| G3 | FEA/实测到 LUT、油冷热边界、系统损耗、磁状态机、控制 LUT 统一表达 |
| G4 | 页级 BOM/EDA、油泵/压力/温度 sensing、gate-disable、DFMEA |
| G5-G6 | 油冷覆盖率、热循环、NVH/EMC、重复切换寿命、故障注入 |
| G7 | PV/PPAP/release/change-control 证据，不得由数值仿真替代 |

---

## 6. 下一步执行优先级

### P0

1. 控制 LUT 记录模型来源、安全边界来源和不可行原因。
2. 热/退磁边界进入主线控制生成。
3. 阶段门声明当前数值实验不能替代硬件证据。
4. 扁线、油冷、多合一进入系统工程约束。

### P1

1. FEA/实测到非线性磁链 LUT 的输入规范。
2. 候选电机 scorecard。
3. 系统损耗 Pareto。
4. BOM/EDA 页级交付物清单。

### P2

1. Memory Motor / 电磁调磁状态机。
2. 磁化/去磁脉冲与安全保护。
3. 状态观测、状态保持、状态漂移和未知状态回退。
4. 机械调磁与电磁调磁 trade-off。

---

## 7. 维护规则

1. V2 PRD 是完整需求源，Wiki 是知识库索引版。
2. V2 HTML 是面向评审和汇报的阅读版。
3. 更新任一版本时，应同步更新：
   - `claude-review/docs/2026-05-15/v2_review_pr_engineering_prd.md`
   - `wiki/v2_review_pr_engineering_prd_wiki.md`
   - `claude-docs/snapshots/wiki/v2_review_pr_engineering_prd_wiki.md`
   - `claude-review/docs/2026-05-15/v2_review_pr_engineering_prd.html`
   - `claude-docs/snapshots/html/v2_review_pr_engineering_prd.html`
   - `claude-docs/evidence_manifest.md`
   - `claude-docs/wiki_html_evidence.md`

---

## 8. 最终判断

V2 的核心判断是：

> v0.3 控制主线继续推进；可变磁通必须先变成状态机和安全问题；扁线、油冷、多合一必须进入系统工程阶段门。只有把这些证据链打通，项目才可能从数值研究走向真实工程落地。
