# Claude 对 Codex 开发线的评审

评审日期：2026-05-13
评审对象：`codex-review-line` 分支中的 Codex 文档、早期 EXP-001 兼容入口和 V2 数值闭环复核记录
对照基线：`claude-mainline`

## 1. 总体结论

Codex 开发线的主要价值在于“评审、拆解、推进计划和风险边界定义”，不适合作为当前正式仿真主线直接合并。它准确指出了 Claude 主线 V1 的可信边界、重复入口风险和 V2 优先级，并把可控磁通量方案拆到可验证假设、输入变量、实验判据和退出门槛层级。

建议保留 Codex 文档作为研发评审资料；代码侧只选择性吸收测试用例和接口命名思路，不应把 `sim/control_search.py` 与 `experiments/exp_001_linear_dq/run.py` 作为第二套正式入口长期保留。

## 2. 已评审范围

| 类型 | 路径 | 评审结论 |
|---|---|---|
| 深度技术评审 | `codex-reviwe/controllable_flux_motor_deep_review.md` | 内容完整，路线分层合理，可作为方案评审基线 |
| 逐方案拆解 | `codex-reviwe/controllable_flux_motor_scheme_dissection.md` | 对物理量、代价转移、必做实验和停止条件拆解充分 |
| Phase 1 实现计划 | `codex-reviwe/phase1_linear_dq_implementation_plan.md` | TDD 步骤清晰，但引用外部 agent skill 语句不适合作为项目内长期规范 |
| V1/V2 复核 | `codex-reviwe/v1_simulation_review_and_v2_plan.md` | 对 V1 结果和接口分叉风险判断准确 |
| V2 闭环记录 | `codex-reviwe/v2_numeric_simulation_closure.md` | 能覆盖 EXP-005 至 EXP-010 的工程门槛，但更像评审摘要，不是实现源 |
| 早期搜索接口 | `sim/control_search.py` | 可读、可测试，但与 `sim/search.py` 重复，存在维护分叉风险 |
| 早期实验入口 | `experiments/exp_001_linear_dq/run.py` | 可生成 JSON/CSV，但输出 schema 与正式 EXP-001 不一致 |
| 早期测试 | `tests/test_control_search.py` | 覆盖基本可行性，但断言偏弱，不能验证最优性或与主线一致性 |

## 3. Codex 开发线的优点

### 3.1 方向判断准确

Codex 明确区分了三类控磁通路线：

1. 控制型等效控磁：负 d 轴弱磁、MTPV、过调制。
2. 磁路型等效控磁：高凸极 IPMSM、PMaSynRM、磁桥/隔磁槽优化。
3. 真实可变磁链：Memory Motor、混合励磁、绕组重构、多相/多绕组结构。

这个分类避免了把普通弱磁误称为“改变永磁体 `ψf/Ke`”的概念混淆，适合作为后续评审约束。

### 3.2 对 V1 边界的判断清楚

`v1_simulation_review_and_v2_plan.md` 把 V1 定位为“边界探测器”，不是“设计定案器”。这个判断正确。V1 只能回答线性 `Rs/Ld/Lq/ψf` 下的准稳态电压/电流可行性，不能回答饱和、铁耗、逆变器损耗、热漂移、退磁和台架可标定性。

### 3.3 V2 优先级合理

Codex 建议 V2 先补：

- 温度修正：`Rs(T)`、`ψf(T)`；
- 退磁边界：`id_min(T)`；
- 非线性磁链 LUT schema；
- 方案 scorecard。

这些优先级与 Claude 主线后续 EXP-004、EXP-006、EXP-010 的推进方向一致。

### 3.4 文档颗粒度高

`controllable_flux_motor_scheme_dissection.md` 对每条路线都拆到了：

- 改变什么物理量；
- 不改变什么物理量；
- 为什么改善高速区；
- 代价转移到哪里；
- 需要哪些模型和数据；
- 应设计哪些实验；
- 继续/停止判据。

这比单纯路线枚举更接近工程评审资料。

## 4. 主要问题与风险

### 4.1 代码入口分叉风险高

Codex 线新增了：

- `sim/control_search.py`
- `experiments/exp_001_linear_dq/run.py`
- `tests/test_control_search.py`

但 Claude 主线已有正式入口：

- `sim/search.py`
- `sim/run_linear_dq_experiment.py`
- `tests/test_exp_001_runner.py`

两套实现都会扫描 `id/iq`，都会生成 EXP-001 类结果，但命名、输出 schema、搜索网格来源和摘要结构不同。继续并存会导致：

1. 后续修 bug 时只修一套；
2. 实验结果被不同 runner 覆盖；
3. 文档、测试和 CSV schema 逐渐不一致；
4. V2 引入 LUT、热、损耗后重复成本放大。

结论：Codex 早期入口不应作为正式入口合并到主线。

### 4.2 `control_search.py` 的网格定义不如主线可追溯

`sim/control_search.py` 使用 `i_max_a` 和 `current_step_a` 即时生成 `id <= 0, iq >= 0` 的圆内候选点。优点是简单，但缺少主线 `GridSpec` 的显式边界：

- 无法独立配置 `id_min_a/id_max_a/iq_min_a/iq_max_a`；
- 不容易纳入退磁 `id_min(T)` 或工程边界；
- 不记录 grid 来源，不利于复现实验；
- 与 `models/motor_params.json` 中的 grid 配置脱节。

建议只保留主线 `sim/search.py` 的 `GridSpec` 模式。

### 4.3 Codex 早期测试断言偏弱

`tests/test_control_search.py` 主要检查：

- 结果 feasible；
- 电压/电流不超限；
- 转矩大于目标或大于 0。

缺少以下验证：

- 是否真的选到最小电流点；
- MTPV 是否与主线最大可行转矩一致；
- 与 `sim/search.py` 在同一 grid 下的结果差异；
- 空结果 schema 是否安全；
- 极端参数、非法参数、边界速度的行为。

所以它适合作为早期 smoke test，不适合作为正式数值正确性保障。

### 4.4 `phase1_linear_dq_implementation_plan.md` 含有外部执行提示

文件第 3 行包含：

```text
REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development ...
```

这类提示对当时 agent 执行有用，但不属于项目长期研发文档。建议后续归档时删除或改写为普通实施说明，避免污染项目规范。

### 4.5 V2 闭环文档部分结论依赖当前简化模型

`v2_numeric_simulation_closure.md` 对 EXP-005 至 EXP-010 的数值发现是有用摘要，但其中结论仍依赖 v0 参数化模型。例如：

- `k_mod=1.04` 最优依赖当前谐波/损耗惩罚系数；
- 混合励磁 `if=0 A` 最优依赖假设的 `kf` 和励磁电阻；
- 绕组重构基准配置最优依赖参数化 turns/resistance/current scale；
- 加权 Pareto 排名依赖人为权重。

文档已经声明 `engineering_validated=false`，但后续引用时仍要避免把这些排名当成设计结论。

## 5. 建议处理方案

### 5.1 文档侧：保留并纳入评审资料

建议保留以下文档，但目录名可后续从 `codex-reviwe` 修正为 `codex-review`：

- `controllable_flux_motor_deep_review.md`
- `controllable_flux_motor_scheme_dissection.md`
- `v1_simulation_review_and_v2_plan.md`
- `v2_numeric_simulation_closure.md`

其中 `phase1_linear_dq_implementation_plan.md` 建议保留为历史实施计划，但移除外部 agent skill 指令。

### 5.2 代码侧：不要直接合并第二套 EXP-001 入口

不建议把以下文件并入 Claude 主线正式路径：

- `sim/control_search.py`
- `experiments/exp_001_linear_dq/run.py`

如果需要保留，可采取二选一：

1. 移入 `legacy/` 或 `codex_compat/`，明确只作历史兼容；
2. 删除实现，只保留 Codex 文档中对分叉风险的说明。

### 5.3 测试侧：吸收意图，不吸收重复实现

可以把 `tests/test_control_search.py` 的测试意图转成主线测试：

- 用 `sim/search.py` 验证最小电流点；
- 用 `find_max_torque_feasible` 验证 MTPV 风格点；
- 加一个“同一 grid 下主线输出 schema 稳定”的测试。

不要让主线测试依赖 `experiments/exp_001_linear_dq/run.py`。

### 5.4 后续优先工作

1. 收敛 EXP-001 唯一入口：继续以 `sim/run_linear_dq_experiment.py` 为准。
2. 把 Codex 文档中的门槛转成 checklist 或 stage-gate JSON。
3. 将 `v2_numeric_simulation_closure.md` 中的工程字段建议映射到实际输出 schema：`k_mod_limit`、`id_min_allowed`、`field_current_cmd`、`winding_config_state`、`phase_group_health`、`pareto_score_version`。
4. 对 EXP-005 至 EXP-010 增加“模型有效性等级”字段，避免结果被误读为工程验证。

## 6. 合并建议

| 项目 | 建议 | 理由 |
|---|---|---|
| Codex 深度评审文档 | 合并/保留 | 方案拆解和风险边界价值高 |
| V1/V2 推进计划 | 合并/保留 | 与 Claude 主线推进一致，可作为复核依据 |
| V2 闭环记录 | 合并/保留 | 可作为 EXP-005 至 EXP-010 的评审摘要 |
| `sim/control_search.py` | 不直接合并 | 与 `sim/search.py` 重复，维护分叉 |
| `experiments/exp_001_linear_dq/run.py` | 不直接合并 | 与正式 runner 输出 schema 不一致 |
| `tests/test_control_search.py` | 改写后吸收 | 测试意图有价值，但应绑定主线接口 |

## 7. 最终判定

Codex 开发线适合作为“研发评审与计划线”，不适合作为“正式仿真实现线”。

建议当前项目保持：

- Claude 主线：负责正式模型、runner、实验输出、覆盖目录和测试闭环；
- Codex 线：负责技术复核、方案拆解、风险门槛和下一步建议；
- 合并时以文档和 checklist 为主，代码只选择性迁移测试意图，避免重复入口。
