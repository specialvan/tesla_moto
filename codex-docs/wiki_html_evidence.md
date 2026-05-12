# Wiki / HTML 关键证据留痕

## 1. 留痕目标

本文件记录可控磁通量电机技术开发中的 wiki 和 HTML 知识库证据，解决三个问题：

1. 下一位接手者知道原始研发叙事从哪里来；
2. 关键知识库文件有快照和哈希，可检查是否漂移；
3. 后续文档引用 wiki/html 时能区分“原始证据”和“当前结论”。

## 2. Wiki 快照

- 原始路径：`wiki/controllable_flux_motor_research_plan.md`
- 快照路径：`codex-docs/snapshots/wiki/controllable_flux_motor_research_plan.md`
- SHA256：`2C16230F519501E80B18BCF44D7DAA0100224E96B436B25D9A50730F5E2661FB`

覆盖内容：

- 研发目标；
- dq 电压方程、线性/非线性磁链模型；
- 转矩公式；
- 电压/电流约束；
- 技术假设树；
- 控制型、磁路型、真实可变磁链型路线。

## 3. HTML 知识库快照

- 原始路径：`controllable_flux_motor_kb.html`
- 快照路径：`codex-docs/snapshots/html/controllable_flux_motor_kb.html`
- SHA256：`7759CFC7153CD26668DA10E6FF82E694B8434DF06423B496D2D4C4AD2E8F1A16`

覆盖内容：

- 页面化知识库；
- 方案路线图；
- 研发资料的可视化入口；
- 后续可作为浏览器侧评审证据。

## 4. 与当前 Codex 文档的关系

| 层级 | 文件 | 角色 |
|---|---|---|
| 原始知识 | `snapshots/wiki/controllable_flux_motor_research_plan.md` | 保存初始研发框架 |
| 页面证据 | `snapshots/html/controllable_flux_motor_kb.html` | 保存可视化知识库 |
| 工程落地 | `reports/*.md` | 驱动、BOM、EDA、协议和 stage-gate |
| 数值闭环 | `experiments/exp_001_*` 到 `experiments/exp_010_*` | 当前分支已落地的可复现实验结果 |
| 成熟度缺口 | `models/scheme_simulation_coverage.json` | 每种方案的后续模型升级方向 |

## 5. 后续维护

如果 wiki 或 HTML 发生更新：

1. 复制新版本到 `codex-docs/snapshots/`；
2. 更新本文件的路径和 SHA256；
3. 更新 `evidence_manifest.md`；
4. 在提交信息里说明快照来源和变更原因。
