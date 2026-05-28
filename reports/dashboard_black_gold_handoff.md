# 可控磁通电机客户数据看板 Handoff

## 当前锁定方向

项目已锁定为黑金高级工程风格的客户数据看板。主页是 `controllable_flux_motor_kb.html`，本地地址是 `http://127.0.0.1:8000/controllable_flux_motor_kb.html`。

OpenDesign 接入标识为 `opendesign-dashboard`，规格文件是 `reports/open_design_dashboard_spec.json`。

后续 agent 必须继续保持：全中文、黑金主题、客户看板、数据可视化强、交互可下钻、算法落地有对应产物、收益前后变化可解释。

## 视觉规范

| 项目 | 规范 |
| --- | --- |
| 背景 | `#08090d` |
| 面板 | `#12141b` / 深色层级 |
| 主文字 | `#f8ecd2` |
| 次级文字 | `#b8aa8d` |
| 主色 / 金色 | `#d6b260` |
| 高亮金 | `#f3d58a` |
| 数据青 | `#37c7b4` |
| 成功绿 | `#62c486` |
| 警示橙 | `#d08b45` |
| 风险红 | `#ef6a73` |
| 分隔线 | `rgba(214, 178, 96, .28)` |

设计语言：深色工程仪表盘 + 金色层级 + 少量青、绿、橙、红数据色。不要改回浅色 SaaS、营销 Landing Page、紫蓝渐变或装饰性大卡片。

## OpenDesign 接入

- `#app-dashboard` 必须保留 `data-design-system="opendesign-dashboard"`。
- `#opendesign-status` 展示 OpenDesign 接入状态。
- `#design-handoff` 和 `#export-design-spec` 用于导出设计规格。
- `OPENDESIGN_TOKENS` 必须与 `reports/open_design_dashboard_spec.json` 保持一致。

关键组件不要改名：`#pareto-chart`、`#benefit-chart`、`#benefit-waterfall`、`#decision-grid`、`#cycle-chart`、`#reach-chart`、`#algorithm-map`、`#compare-mode`、`#weight-simulator`、`#scenario-presets`、`#interactive-insights`、`#business-case`、`#meeting-script`、`#presentation-bar`、`#benchmark-board`、`#closure-board`、`#delivery-health`。

## 交互与接口

- `/api/dashboard` 拉取候选方案、工况、铁耗、算法和验证准备清单。
- `/api/health` 和 `/api/schema` 做运行时健康与接口契约校验。
- `/api/scenario-state` 和 `/api/session-snapshot` 支持客户现场状态保存与恢复。
- `/api/customer-brief` 生成客户汇报摘要。
- `/api/decision-pack` 导出客户决策包。
- `/api/design-spec` 返回 OpenDesign 规格。

前端必须保留离线回退能力，接口失败时页面仍能展示本地数据、风险提示和导出结果。

## 内容口径

1. 客户当前推荐方案和收益。
2. 优化前后评分、铜耗、峰值可达性、高速风险变化。
3. 算法落地对应关系：MTPA/弱磁/MTPV、非线性磁链 LUT、加权工况 Pareto、Bertotti 铁耗估算、安全边界判断、控制 LUT 生成。
4. 方案对比、客户工况权重模拟、ROI 测算、客户决策讲解脚本、风险闭环任务。
5. 证据链：EXP-010、EXP-011、Wiki、OpenDesign handoff。

看板展示的是“方案筛选收益”，不能写成量产实机收益承诺。量产口径必须依赖材料、热、逆变器损耗、FEA、HIL、台架和硬件保护验证。

## 禁止跑偏

- 不要做成首页宣传页或品牌落地页。
- 不要弱化数据密度和工程证据链。
- 不要把黑金主题换成浅色、蓝紫、米色或单一金色。
- 不要删除 OpenDesign、接口联调、导出、会话保存、权重模拟、ROI、客户决策讲解脚本、风险闭环等能力。
- 不要引入不可解释的装饰图形替代真实图表。
- 不要把中文写坏成连续问号或替换字符。Windows 上改中文时必须使用 UTF-8 安全方式。

## 验证清单

```powershell
pytest tests/test_frontend_dashboard.py tests/test_dashboard_api.py -q
python -m sim.dashboard_api --browser-interaction-smoke
python -m sim.dashboard_api --browser-screenshot-smoke
```

检查重点：页面能打开，状态显示“接口已连接”或清晰的“离线回退数据”，黑金风格保持，图表非空，方案点击、权重模拟、ROI、决策包、摘要、OpenDesign 导出都可用。

## 已知实现范围

- 主文件：`controllable_flux_motor_kb.html`
- 接口：`sim/dashboard_api.py`
- 测试：`tests/test_frontend_dashboard.py`、`tests/test_dashboard_api.py`
- 规格：`reports/open_design_dashboard_spec.json`
- 截图：`reports/dashboard-smoke-desktop.png`、`reports/dashboard-smoke-mobile.png`

## 新增交付模块

- `#sensitivity-matrix`：收益敏感性矩阵，保守、当前、积极三档假设可回填 ROI 滑块。
- `#meeting-script`：客户决策讲解脚本，联动当前方案、ROI、工况权重和风险闭环。
- `#stage-gate-board`：客户验证阶段门，覆盖工况冻结、材料/FEA、HIL/台架和决策包评审。
- `#algorithm-maturity`：算法落地成熟度矩阵，按模型、数据、接口、验证和客户价值解释每个算法的客户现场落地状态。
- `#evidence-gap-priority`：证据缺口优先级看板，按风险、收益影响和验证成本排序电压裕度、退磁、铁耗、HIL/台架等补证动作。
- `#review-question-board`: 客户评审问题清单，覆盖收益、风险、算法、验证、对比等现场问题，并联动当前方案、ROI 和证据缺口。
- `#decision-pack-preview`: 客户决策包预览，把当前方案、ROI、证据缺口、评审问答和下一步动作组成可复制的客户会议材料。
- `#customer-minutes-generator`: 客户评审纪要生成，支持技术评审、商务评审和验证推进三种口径，联动当前方案、ROI、证据缺口、评审问答和阶段门行动项。
- `#validation-action-timeline`: 客户验证行动时间轴，按 T+3/T+5/T+7/T+10 节点展示责任人、证据产物、客户价值和回填目标，联动当前方案、ROI、证据缺口和评审纪要。
- `#validation-risk-heatmap`: 验证风险热力图，按影响、紧急度、责任人和回填目标排序电压裕度、退磁、铁耗、HIL/台架等验证风险。
- `#customer-acceptance-gate`: 客户验收门禁，把决策包完整度、ROI、验证排期、风险边界和客户确认汇总成可复制的签收条件。

后续新增模块必须继续遵守全中文、黑金高级风格、OpenDesign 接入、接口可联调和收益可解释的原则。
