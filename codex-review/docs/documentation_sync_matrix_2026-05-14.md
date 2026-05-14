# Claude / Codex 文档同步矩阵

评审日期：2026-05-14

## 1. 同步目标

当前仓库存在多套面向接手者的入口：`claude-docs/`、`codex-docs/`、wiki、HTML、coverage JSON、experiments summary、reports。最新事实源已经推进到 EXP-001 到 EXP-010 均有 `passed_numeric_simulation` 代理覆盖，但文档入口并未完全同步。

本矩阵用于规定下一轮文档修复时每个文件应如何对齐，避免只改一个入口导致新的漂移。

## 2. 权威事实源排序

| 优先级 | 事实源 | 使用方式 |
|---|---|---|
| S0 | `models/scheme_simulation_coverage.json` | 当前方案状态、测试、产物和下一步建模项的结构化事实源 |
| S0 | `experiments/exp_*/summary.json` | 每个实验的 `parameter_source`、`model_scope`、`model_limitations`、`engineering_validated` 事实源 |
| S0 | `sim/` runner 与模型源码 | 判断实验是否真正可重跑 |
| S0 | `tests/` | 判断数值代理是否有自动化覆盖 |
| S1 | `claude-docs/evidence_manifest.md` | 人类审计入口，应完整索引 S0 事实源 |
| S1 | `claude-docs/simulation_traceability.md` | 人类可读的方案-实验-测试矩阵，应由 S0 反推 |
| S2 | `wiki/controllable_flux_motor_research_plan.md` | 研发叙事和路线图，应同步当前实验编号 |
| S2 | `controllable_flux_motor_kb.html` | 展示入口，应同步 wiki 和 coverage 当前状态 |
| S3 | `codex-docs/` | 历史分支知识库或需显式更新为当前状态 |

## 3. 当前文件级修复矩阵

| 文件 | 当前问题 | 应更新为 | 优先级 |
|---|---|---|---|
| `claude-docs/README.md` | 当前落地实验仍写 EXP-001/002/003/004/006，且说 EXP-005/007-010 不属于主线完成闭环 | 写明 EXP-001 到 EXP-010 已具备可重跑数值代理；同时强调全部不是工程验证 | P0 |
| `claude-docs/handoff_context.md` | 当前状态、能力表和后续优先级未纳入 EXP-005/007/008/009/010 | 增加 EXP-005、EXP-007、EXP-008、EXP-009、EXP-010；EXP-006 表述保持“synthetic LUT，未接入共享控制搜索”除非对应 runner 已落地 | P0 |
| `claude-docs/evidence_manifest.md` | 仿真实验证据只列 EXP-001 到 EXP-004 | 增加 EXP-005 到 EXP-010；增加 EXP-006 summary/CSV/schema/sample；更新关键结论和缺口证据 | P0 |
| `claude-docs/simulation_traceability.md` | 映射表接近最新，但“下一批最小实验包”仍像待开发 | 改成“已落地代理实验与下一步高保真升级”；修正不存在的 `tests/test_control_search.py` 引用 | P0 |
| `claude-docs/wiki_html_evidence.md` | 仍写 HTML 已同步 EXP-003 结论 | 改写为 HTML 活动源当前滞后，或在更新 HTML 后写明已同步 EXP-001 到 EXP-010 | P1 |
| `wiki/controllable_flux_motor_research_plan.md` | 实验矩阵仍是早期 EXP-01 到 EXP-08/09 规划编号 | 新增或替换为实际 EXP-001 到 EXP-010 表，保留旧路线图时标注历史规划 | P1 |
| `controllable_flux_motor_kb.html` | 展示矩阵只到 EXP-07 且编号与当前实验目录不一致 | 增加 EXP-005 到 EXP-010 卡片；对每项标注 proxy/synthetic/engineering_validated=false | P1 |
| `claude-docs/snapshots/wiki/*` | 若活动 wiki 更新则快照过期 | 复制最新活动 wiki，并更新 manifest | P1 |
| `claude-docs/snapshots/html/*` | 若活动 HTML 更新则快照过期 | 复制最新 HTML，并更新 manifest | P1 |
| `codex-docs/README.md` | 仍写 EXP-005 到 EXP-010 是后续建模方向 | 若继续维护，应更新；若作为历史包，应标注“历史分支状态” | P1 |
| `codex-docs/handoff_context.md` | 写 EXP-001 到 EXP-010 全部具备入口，但又说 nonlinear_flux_lut 唯一缺位 | 更新 EXP-006 状态，或标记为旧分支 handoff | P1 |
| `codex-docs/simulation_traceability.md` | 状态数量为 11 numeric / 1 needs，与当前 coverage 12 numeric 不一致 | 同步数量和 EXP-006 行，或标记历史 | P1 |
| `codex-docs/wiki_html_evidence.md` | 仍写 EXP-005 到 EXP-010 是下一步建模缺口 | 同步或标记历史 | P2 |

## 4. EXP-001 到 EXP-010 当前口径

| 实验 | 当前口径 | 必须保留的限制 |
|---|---|---|
| EXP-001 | 线性 dq 基线和共享搜索基线 | 不含非线性 LUT、铁耗、逆变器损耗、热耦合 |
| EXP-002 | 虚拟 `psi_f` 档位扫描 | 不等同真实 memory motor 磁化状态 |
| EXP-003 | 参数族缩放代理 | 不是真实电磁几何推荐 |
| EXP-004 | 温度、Vdc 降额、简化退磁边界 | 简化退磁线需磁钢/FEA/台架数据替换 |
| EXP-005 | 过调制电压利用率参数扫描 | 谐波、电流纹波、损耗和 EMI 仍为参数化代理 |
| EXP-006 | synthetic `lambda_d/lambda_q` LUT 插值、非线性转矩证明和工作树 phase-2 受约束搜索 | LUT 非 FEA/测量来源，仍未导出共享控制 LUT，也未接入热/退磁/损耗闭环 |
| EXP-007 | 混合励磁等效磁链和励磁铜耗代理 | 无励磁动态、热耦合、转子漏磁和励磁机模型 |
| EXP-008 | 绕组重构参数缩放和切换连续性代理 | 无开关暂态、环流、绝缘和热分配模型 |
| EXP-009 | 多相相组电流降额代理 | 无谐波子空间、零序偏移、相级热 RC |
| EXP-010 | 说明性 drive cycle 下铜耗 Pareto 排序 | 无真实工况、铁耗、机械损耗、逆变器损耗 |

## 5. EXP-006 搜索闭环补充核验

评审期间观察到并继续核验了 EXP-006 phase-2 工作树闭环。该闭环包含 `tests/test_nonlinear_flux_lut_search.py`，它引用：

- `sim.run_nonlinear_flux_lut_search_experiment.run`
- `make_candidate(..., flux_lut=lut)`
- `find_min_current_for_torque(..., flux_lut=lut)`
- `find_max_torque_feasible(..., flux_lut=lut)`
- `find_id_zero_candidate(..., flux_lut=lut)`

最新核验结果为：

| 项 | 当前状态 | 结论 |
|---|---|---|
| `sim/run_nonlinear_flux_lut_search_experiment.py` | 工作树中已存在 | phase-2 runner 已形成 |
| `sim/search.py` `make_candidate` | 工作树中已支持可选 `flux_lut` 参数 | 可按 LUT 计算非线性转矩与电压 |
| `sim/search.py` 搜索函数 | 工作树中已支持可选 `flux_lut` 参数并裁剪 grid 到 LUT 边界 | phase-2 已能进入受约束搜索链路 |
| `experiments/exp_006_nonlinear_flux_lut/lut_search_summary.json` | 工作树中已存在 | 可纳入 manifest，但必须保留 synthetic / 非工程验证口径 |
| targeted pytest | `python -m pytest tests/test_nonlinear_flux_lut.py tests/test_nonlinear_flux_lut_search.py tests/test_exp_001_runner.py -q` 返回 17 passed | phase-2 工作树闭环通过局部验证 |

因此，当前文档应写：EXP-006 已完成 synthetic LUT schema、边界检查、双线性插值、非线性转矩数值证明，并且工作树中已经形成 phase-2 受约束搜索闭环。仍必须说明它尚未使用 FEA/实测 LUT，尚未导出共享控制 LUT，也尚未接入热、退磁、铁耗、逆变器压降和工程验证。

## 6. 推荐提交拆分

| 提交 | 内容 | 目的 |
|---|---|---|
| Commit A | `codex-review/docs` 新评审包 | 固化本轮评审，不混入业务修复 |
| Commit B | 工具链文档 PyAEDT/PyFluent/Fluent 澄清 | 冻结已有未提交工具链修改 |
| Commit C | 修复 coverage 测试路径与测试存在性校验 | 消除 P0 证据链断点 |
| Commit D | 更新 `claude-docs/` README/handoff/manifest/traceability | 恢复 Claude 知识库入口一致性 |
| Commit E | 更新 wiki、HTML、snapshots、wiki_html_evidence | 恢复过程文档和展示入口一致性 |
| Commit F | EXP-006 LUT search runner、search.py 支持、测试和产物 | 将工作树 phase-2 可运行闭环单独提交并同步文档 |
