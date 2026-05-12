# Codex 开发线评审深度梳理

## 1. 背景

Claude 返回的评审对象是 `codex-review-line` 中的 Codex 文档、早期 EXP-001 兼容入口和 V2 数值闭环复核记录。评审核心不是否定 Codex 产出，而是要求区分两条职责线：

- Claude 主线：正式模型、runner、实验输出、覆盖目录和测试闭环；
- Codex 线：技术复核、方案拆解、风险门槛和下一步建议。

本梳理基于当前 `claude-mainline` 工作树重新核验，避免把评审中的分支事实误套到当前主线。

## 2. 当前主线事实核验

| 核验项 | 当前主线结果 | 结论 |
|---|---|---|
| `sim/control_search.py` | 不存在 | 重复搜索入口未进入当前主线 |
| `experiments/exp_001_linear_dq/run.py` | 不存在 | 第二套 EXP-001 runner 未进入当前主线 |
| `tests/test_control_search.py` | 不存在 | Codex smoke test 未绑定当前主线 |
| `codex-reviwe/phase1_linear_dq_implementation_plan.md` | 不存在 | 外部 agent skill 指令未污染当前主线文档 |
| EXP-005 到 EXP-010 | 当前主线不存在 | 仍属于后续数值建模方向 |
| `models/scheme_simulation_coverage.json` | 6 数值、5 待建模、1 架构验证 | 当前主线没有宣称 12 项全数值闭环 |

结论：评审指出的问题主要是“合并风险”，不是当前主线已存在的运行时缺陷。

## 3. 评审项逐条处置

### 3.1 代码入口分叉风险

评审意见：不要把 `sim/control_search.py` 与 `experiments/exp_001_linear_dq/run.py` 作为第二套正式入口长期保留。

核验结果：当前主线不存在这两个文件。

处置：

- 当前无需删除代码；
- 后续如从 Codex 分支 cherry-pick，必须排除这两个入口；
- 若确需保留历史实现，只能放入 `legacy/` 或 `codex_compat/`，并明确不参与正式实验产物。

验收标准：

- `sim/run_linear_dq_experiment.py` 仍是 EXP-001 唯一正式 runner；
- `experiments/exp_001_linear_dq/summary.json` 和 `scan_results.csv` 只由正式 runner 生成；
- README / handoff 不引用第二套入口。

### 3.2 `control_search.py` 网格不可追溯

评审意见：Codex 早期接口用 `i_max_a/current_step_a` 生成候选点，不如主线 `GridSpec` 可追溯。

核验结果：当前主线使用 `sim/search.py` 的 `GridSpec`，参数来自 `models/motor_params.json`。

处置：

- 保持 `GridSpec` 为唯一搜索网格接口；
- 后续所有 EXP-005..010 扩展都应复用或显式扩展 `GridSpec`；
- 不引入隐式圆内扫描作为正式接口。

验收标准：

- 新 runner 的 grid 来源可追溯到参数文件或显式实验配置；
- 退磁、温度、电流边界可以在候选过滤阶段注入；
- 测试能验证非法 grid 和边界 grid 行为。

### 3.3 Codex 早期测试断言偏弱

评审意见：`tests/test_control_search.py` 只验证可行性，不验证最优性、schema 稳定性和主线一致性。

核验结果：当前主线不包含该测试。

处置：

- 不直接吸收 `tests/test_control_search.py`；
- 可将测试意图改写到主线测试：
  - 最小电流点验证；
  - 最大可行转矩点验证；
  - 空结果 schema 验证；
  - 与 `models/motor_params.json` grid 的一致性验证。

验收标准：

- 测试绑定 `sim/search.py`；
- 测试断言包含排序目标，而不仅是 feasible；
- 测试覆盖不可达工况和边界速度。

### 3.4 外部 agent skill 指令污染项目文档

评审意见：`phase1_linear_dq_implementation_plan.md` 中的 `REQUIRED SUB-SKILL` 不应作为项目长期规范。

核验结果：当前主线不存在该文件。

处置：

- 当前无需修改；
- 若未来恢复该文档，需要删除 agent 执行指令，改成普通工程实施步骤；
- 项目文档只描述工程流程，不绑定某个 agent 的本地技能系统。

验收标准：

- 项目文档中不出现 `REQUIRED SUB-SKILL`；
- agent 工作流只保留在会话或工具层，不写入长期工程规范。

### 3.5 V2 参数化模型误读风险

评审意见：`v2_numeric_simulation_closure.md` 中 EXP-005 到 EXP-010 的结论依赖 v0 参数化模型，不能作为设计定论。

核验结果：当前主线没有 EXP-005 到 EXP-010 正式实现，`claude-docs` 也明确写了这些不属于当前主线正式数值闭环。

处置：

- 继续保持 `engineering_validated=false` 口径；
- EXP-005 到 EXP-010 进入主线时，必须增加模型成熟度字段；
- Pareto 排名只作为筛选器，不作为设计释放结论。

验收标准：

- 每个 summary 显式写明 `parameter_source`、`model_scope`、`model_limitations`；
- 方案报告中不写“最优设计”，只写“当前参数化模型下的排序/边界”；
- 后续 FEA/台架数据进入前，不升级为工程验证。

## 4. 对当前 Claude 主线的影响

当前无需做破坏性删除或大规模重构。需要做的是把评审结论转为守门规则：

1. EXP-001 入口唯一：`sim/run_linear_dq_experiment.py`。
2. 搜索接口唯一：`sim/search.py` + `GridSpec`。
3. Codex 文档可作为评审资料进入知识库。
4. Codex 代码只按功能切片迁移，不按目录整体合并。
5. 后续 EXP-005..010 必须在 Claude 主线重新按 TDD、summary、CSV、coverage 目录闭环。

## 5. 后续执行优先级

| 优先级 | 行动 | 原因 |
|---|---|---|
| P0 | 保持 EXP-001 唯一 runner | 避免实验产物 schema 分叉 |
| P0 | 禁止直接合入 `sim/control_search.py` | 与主线搜索模型重复 |
| P1 | 把 Codex 测试意图改写到主线搜索测试 | 提升最优性和边界行为保障 |
| P1 | 给后续 EXP-005..010 增加 `model_maturity` 字段 | 防止 v0 模型被误读 |
| P2 | 将 Codex 文档门槛转成 checklist/stage-gate JSON | 提高评审自动化程度 |

## 6. 决策记录

本轮采纳评审中的技术判断：

- 采纳：Codex 文档作为研发评审资料保留；
- 采纳：不把 Codex 第二套 EXP-001 入口并入主线；
- 采纳：测试意图需要改写后吸收；
- 采纳：v0 参数化结论不得作为工程设计结论；
- 暂缓：EXP-005..010 数值模型迁移，需按 Claude 主线接口重新实施。
