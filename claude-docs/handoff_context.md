# Claude 开发上下文 Handoff

## 1. 当前工作线

- 主线分支：`claude-mainline`
- 主要目标：以干净室方式推进可控磁通量电机技术开发，把公开物理模型、仿真闭环、工程路线和证据链沉淀为可继续开发的主线知识库。
- 当前状态：EXP-001 到 EXP-011 是 Claude 主线当前已落地的可重跑数值/代理实验范围；EXP-006 仍是 synthetic `lambda_d/lambda_q` LUT 与受约束搜索，EXP-011 是 Bertotti 三项简化铁耗风险扫描，不能替代材料、FEA、HIL 或台架验证。
- 本目录目的：让后续 agent / 工程师快速恢复上下文，定位仿真入口、证据路径、工程边界和下一步技术任务。

## 2. 干净室边界

Claude 主线只允许基于以下来源形成结论：

- 公开 dq 方程和电机控制理论；
- 本仓库 Python 仿真代码、测试和产物；
- 开源工具链方向，如 Pyleecan、FEMM、SyR-e、motulator、VESC、MESC；
- 后续可补充的 FEA、HIL、台架和热/EMC/安规验证数据。

禁止：

- 复制闭源实现；
- 猜测 Tesla、BYD 或其他厂商内部方案；
- 把 AI/Codex 草案直接视为工程结论；
- 绕过退磁、热、过压、绝缘和故障安全验证。

## 3. 已完成的主线能力

| 能力 | 证据 |
|---|---|
| wiki 研发框架 | `wiki/controllable_flux_motor_research_plan.md` |
| HTML 知识库 | `controllable_flux_motor_kb.html` |
| 线性 dq 基线 | `experiments/exp_001_linear_dq/README.md` |
| 虚拟可变磁链扫描 | `experiments/exp_002_variable_flux/README.md` |
| 参数族协同扫描 | `experiments/exp_003_param_sweep/README.md` |
| 热/退磁安全边界 | `experiments/exp_004_safety_boundaries/summary.json` |
| 非线性 `lambda_d/lambda_q` LUT | `experiments/exp_006_nonlinear_flux_lut/summary.json` |
| 加权效率 Pareto | `experiments/exp_010_weighted_efficiency_pareto/summary.json` |
| Bertotti 铁耗扫描 | `experiments/exp_011_iron_loss/summary.json` |
| 工程落地矩阵 | `reports/scheme_engineering_landing_matrix.md` |
| 驱动、上电时序、协议图 | `reports/scheme_driver_power_protocol_diagrams.md` |
| BOM / EDA 集成设计 | `reports/scheme_bom_eda_integration_design.md` |
| 成熟业界 stage-gate 流程 | `reports/scheme_industry_design_stage_gate_process.md` |
| 仿真覆盖目录 | `models/scheme_simulation_coverage.json` |

## 4. 当前已落地仿真

| 实验 | 作用 | 当前结论 |
|---|---|---|
| EXP-001 | 线性 dq 基线、负 d 轴弱磁、最小电流目标转矩和最大可行转矩扫描 | 100 Nm 目标在基线下可达 6750 rpm，最大可行正转矩点可扫到 18000 rpm |
| EXP-002 | 可变磁链 / memory motor 虚拟 `psi_f` 状态扫描 | 直接降低 `psi_f` 会显著损失目标转矩能力，不能单独视为收益 |
| EXP-003 | `psi_f/Ld/Lq/Vdc/Imax` 参数族扫描 | 最优为 `psi1.00_ld0.80_lq1.60_vdc1.15_imax1.15`，低磁链候选必须协同高凸极比和更高 `Vdc/Imax` |
| EXP-004 | 温度、Vdc 降额、简化退磁边界 | 已建立安全边界数值入口，但需要真实磁钢/FEA 数据替换简化退磁线 |
| EXP-006 | synthetic `lambda_d/lambda_q` LUT 插值与非线性转矩证明 | 已建立 schema、边界检查、双线性插值和非线性转矩数值入口，但尚未接入电压约束控制搜索 |
| EXP-010 | 示意工况加权效率 Pareto | 已可重跑候选路线排序，但评分仍是 proxy，不含实测工况、铁耗、机械损耗和逆变器损耗闭环 |
| EXP-011 | Bertotti 三项简化铁耗扫描 | 已输出 `freq_out_of_range_points` 和有效频率 KPI，用于暴露高速铁耗风险；系数仍是干净室假设 |

## 4.1 r02/r03 成熟度口径

- 12 份 r02 sim_binding 是当前机器可读仿真绑定，字段包括 `simulation_status`、`model_maturity` 和 `gate_class`。
- r02-sim 局部图档批包仅保留 S02/S04 历史证据，已由 12 份 r03 production drawing pack 归档替代。
- r03 production drawing pack 继承 `SIM ANCHOR`、pytest gate、`model_maturity`、`next_simulation_step` 与 `engineering_validated=false` 护栏。
- 相关测试：`tests/test_r02_sim_batch_archival.py`、`tests/test_r03_prompt_simulation_anchor.py`、`tests/test_r03_prompt_maturity.py`。

## 5. 后续优先级

1. 把 `negative_d_axis_field_weakening`、`mtpa_fw_mtpv_control`、`thermal_demag_safety_protection` 串成更完整控制 LUT 与安全边界闭环。
2. 把 EXP-006 的 synthetic `lambda_d/lambda_q` LUT 从独立插值与非线性转矩证明推进到 FEA/测量数据回灌，并接入电压约束控制搜索。
3. 用 Pyleecan/FEMM/SyR-e 或等效 FEA 数据替换 EXP-003 的独立缩放代理。
4. 引入铁耗、逆变器损耗、热模型和工况加权 Pareto 评分。
5. 按 `claude-review/docs/2026-05-20/v2_high_speed_back_emf_pending_scheme_deep_dive.md` 暂存结论，新增两挡电驱、绕组重构、小范围混合励磁和可变磁化的统一总损耗 scorecard。
6. 仅在仿真收益明确且安全边界充分后，再进入低压台架验证。

## 6. 接手时优先检查

1. 先读 `claude-docs/README.md`。
2. 再读 `claude-docs/evidence_manifest.md`，确认快照和活动证据路径。
3. 打开 `models/scheme_simulation_coverage.json`，确认每个方案状态和下一步建模项。
4. 运行 `python -m pytest -q` 验证主线测试。
5. 若测试生成 CSV/JSON 差异，先判断是否为预期实验产物变化，不要盲目提交。
