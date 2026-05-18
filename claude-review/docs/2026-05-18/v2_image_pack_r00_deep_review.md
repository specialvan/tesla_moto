# V2 方案生图包 r00 深度评审

日期：2026-05-18
评审范围：`gpt-image-2/outputs/S01..S12/V2-SXX-ILL-T01..T08-...-r00.png`（12 方案 × 8 模板 = 96 张）
事实源：`codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18.md`、`codex-review/docs/image_worklist_2026-05-18/scheme-01..12.md`、`gpt-image-2/config/style.json`、`gpt-image-2/outputs/_reports/full_run_2026-05-18.log`

---

## 0. 评审边界（不可破坏）

1. 本评审只判定 r00 96 张生图相对 r00 提示词与不可破坏边界的对齐度，**不会**因为生图美化把 `engineering_validated` 改成 `true`。
2. 评审结论仅服务于 r01 提示词收敛；任何"看起来很像真实 PCB/EDA/STEP"的图必须在 r01 中加 `concept-` 前缀提醒或显式 disclaimer。
3. 评审采用"工程语义对照 + 风格基线对照 + 边界违规枚举"三轴，与 `.drawio`/Mermaid 源文件保持回溯。
4. 评审过程**未**执行新的生图调用；产物仍是 r00 一轮的 96 张 PNG。

---

## 1. 评审方法

| 维度 | 判定准则 | 失败定义 |
|---|---|---|
| 工程语义 | 节点/状态/转移/信号与 prompt 差分 token、`.drawio` / mermaid 源一致 | 缺漏 / 错连 / 状态机逻辑反向 |
| 风格基线 | 深色底 + 金线 + 浅蓝填充 + 英文标签 | 灰底/纯白/低对比/中文渗入 |
| 不可破坏边界 | 无真实零件号、无 logo、无 marketing、CAD/PCB 标注 "concept" | 出现 M270-35A 等具体牌号、看起来像真实 STEP |
| 方案差分度 | 同模板下各方案能看出方案特征（非通用图复用） | T01/T03 等仅替换标题，主体一致 |
| 图面可读性 | 字号、留白、箭头不重叠、长宽比贴合 prompt | 拥挤、压字、16:9 被吞为 1:1 |

每个失败项划入：BLOCKER（违反不可破坏边界 / 工程语义错）、HIGH（缺漏关键转移 / 风格基线偏差）、MEDIUM（密度过高 / 长宽比错）、LOW（装饰性 / 排版细节）。

---

## 2. 总体结论

| 类别 | 评级 | 说明 |
|---|---|---|
| 总体可用度 | 70%（评审可视化锚点合格，工程语义需 r01 收敛） | T01/T03 主线可直接用于评审 PPT；T05/T04 需要 r01 重做 |
| 风格一致度 | 65%（夜色/金线基线达成，但 T05/T07 出现真实化渲染） | 需要在 r01 全局正向 token 中显式禁用"photo render of motor/PCB" |
| 边界违规率 | 8 / 96 张存在 BLOCKER 级违规（多集中在 T05） | r01 必须扩展负向 prompt，禁止真实材料牌号、真实尺寸标注 |
| 工程语义对齐度 | T03 状态机有 11 处缺漏或反向（详见 §4） | r01 必须把 prompt 升级为"显式枚举所有有向边" |
| 方案差分度 | T03 中 S05/S06/S12 出现"MOTOR CONTROLLER SUBSYSTEM"标题，泄漏通用模板 | r01 必须强制 scheme-specific title token |

---

## 3. 共性问题登记

| ID | 问题 | 影响张数（估计） | 严重度 | r01 对策 |
|---|---|---|---|---|
| GEN-01 | 通用标题泄漏（"MOTOR CONTROLLER SUBSYSTEM"）出现在非控制器类方案 T03 上 | S05/S06/S12 T03 等 | HIGH | r01 每条 prompt 末尾加 `Title bar text MUST be: <SCHEME_TITLE>` |
| GEN-02 | 16:9 / 4:3 长宽比指令被默认 1024×1024 配置覆盖 | T01/T02/T07/T08 共 48 张 | MEDIUM | 在 `gpt-image-2/prompts/schemes.json` 单条覆盖 size；prompt 内的"aspect ratio"语言只作 layout 提示 |
| GEN-03 | T05 出现真实材料牌号（M270-35A、ADC12、C11000、NdFeB、SmCo） | S04/S07/S08 等 | BLOCKER | r01 负向 prompt 扩展：`no specific steel grades, no real material designations, no engineering dimension callouts in mm` |
| GEN-04 | T05 整体呈现近写真级 3D 渲染，不像 concept | S07/S08 尤甚 | BLOCKER | r01 强制 `flat isometric line illustration, no shading, no surface texture, no metallic reflection` |
| GEN-05 | T03 状态/转移与 prompt 差分 token 不完全对应（缺转移、加状态） | S01/S05/S06/S08 至少 4 张 | HIGH | r01 每条 prompt 加 `Exactly N states and M directed edges as listed below; no extra states; every edge must carry the label string verbatim` |
| GEN-06 | 节点填充未达 pale blue，部分为深灰 / 黄棕 | T04/T03 多张 | MEDIUM | r01 显式 hex 颜色：`node fill hex #B6C7E0, node stroke hex #D8A638, background hex #0B1A33` |
| GEN-07 | 安全/故障状态未做视觉区分（红色描边或填充） | T03 S01/S04/S06/S10/S11 | MEDIUM | r01 在差分 token 中标记 `Highlight fault/fallback state with red-tinted stroke #C0392B` |
| GEN-08 | 协议链路 T08 bus label 不完整（出现 "Internal Bus" 占位） | S02/S01 等 | LOW | r01 加 `Every arrow must carry an explicit bus label such as CAN-FD, SPI, FlexRay, Ethernet/XCP; do not use generic Internal Bus` |
| GEN-09 | BOM 树 T06 risk pill 准确性差异（同族器件 LOW/MED/HIGH 不一致于 BOM markdown） | S01/S11 BOM 树 | LOW | r01 在差分 token 中固化 per-leaf risk 等级，限制模型自由发挥 |
| GEN-10 | 时序图 T02 文字过密、活动条不显 | S01 T02 等 | MEDIUM | r01 改 prompt：`Use thicker activation bars on MCU lifeline; allow up to 16:9 aspect ratio with horizontal spacing` |
| GEN-11 | T07 verification tree 出现 `TST-xxx-xxx` 编号但与 DVP&R markdown ID 不一致 | S11 T07 | LOW | r01 在差分 token 中显式给出每个 TST 编号，与 `engineering/v2/scheme-XX/test_dvpr/*.md` ID 同步 |
| GEN-12 | 部分 T04 PCB 图密度过高、字号过小、无 concept 提示 | S04/S11 T04 | MEDIUM | r01 加 `Reduce signal labels to <= 20 short tokens; keep one large CONCEPT ONLY watermark in top-right` |

---

## 4. 12 方案逐方案评审

每个方案给出 8 张 T01..T08 的关键发现与 r01 优先级（P0=必修，P1=建议修，P2=可保留）。

### 4.1 S01 `negative_d_axis_field_weakening`

| 模板 | 关键发现 | r01 优先级 | 备注 |
|---|---|---|---|
| T01 driver | Limiter 子块、Temp/Vdc 反馈线已落；但长宽比落到 1:1，PWM/6x 标签略多 | P1 | 收紧 size 配置为 1792x1024 |
| T02 sequence | 8 条信令命中，但 ID_MIN(T) load 的 self-loop 文本与 INVERTER 列冲撞 | P1 | r01 加 `keep self-loop labels left of MCU lifeline` |
| T03 state | 6 状态全到位；缺关键 `V margin < limit` 转移，仍可读懂 FW 进入路径但无显式触发条件 | **P0** | r01 prompt 锁死全部 7 条转移 + 红色 fault 描边 |
| T04 PCB | 5 个功能组齐全，gate_disable_n 醒目；密度尚可，缺 `CONCEPT ONLY` watermark | P1 | r01 加 watermark 强制 |
| T05 CAD | 三相母排、传感器窗口、LV/HV keep-out 都看到；右下偏 3D render，需弱化 | P1 | r01 强制 line illustration |
| T06 BOM tree | 5 分支 + LOW/MED/HIGH 胶囊清晰，符合 catalog；HIGH 项与 BOM markdown 待对齐 | P2 | r01 固化 per-leaf 风险标 |
| T07 Test tree | 4 axis × 2 leaf 整齐；缺 DVP IDs `S01-DV-001..005` 落到节点 | P2 | r01 加 DVP id binding |
| T08 protocol | VCU/MCU/Limiter/FOC/SVPWM 链清晰，UDS/XCP+Calibration 旁路；MCU→Limiter 用了 dashed 易误读 | P2 | r01 改为 solid solid + 显式 `signal: V_bus, I_phase, T_magnet` 标签 |

### 4.2 S02 `mtpa_fw_mtpv_control`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | MTPA/FW/MTPV LUT 块直观；缺 LUT CRC / NVM 路径显式标 | P1 |
| T02 sequence | 命中关键 NVM→LUT load 行，但 LUT CRC 校验未单独成行 | P1 |
| T03 state | 6 状态命中；`mode reset` 转移指向 Derate，与 catalog 应指向 MTPA idle 不符 | **P0** |
| T04 PCB | MCU+NVM、ADC、resolver 接口、CAN 收发都到位；缺 LUT version diagnostic 节点 | P1 |
| T05 CAD | 控制器壳体外观偏 3D render，散热路径模糊 | P1 |
| T06 BOM | 5 分支命中；NVM 行未拆出 LUT release infra | P2 |
| T07 Test tree | HIL / CRC / Power-off / Mode continuity 4 axis 命中；缺 NVM endurance leaf | P2 |
| T08 protocol | Mode Selector 块准确，但 internal bus 用了 "INTERNAL BUS" 占位 | P1 |

### 4.3 S03 `svpwm_overmodulation_voltage_utilization`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | SVPWM/Overmodulation/Six-Step Selector 子块、THD/NVH Monitor 反馈都到位；可读 | P2 |
| T02 sequence | sequence 缺少"voltage utilization rising"信号，整体偏简 | P1 |
| T03 state | 6 状态命中，但 `voltage utilization rising` 在 Linear→Region 1 与 Region 1→Region 2 重复使用；`Vdc recovered` 多向重复 | **P0** |
| T04 PCB | Gate driver/EMC 滤波/DC-link/Busbar 命中；缺 dead-time 控制电路单独标 | P1 |
| T05 CAD | 模块外观偏 3D；DC-link 与 heatsink 接触面不清 | P1 |
| T06 BOM | 5 分支命中 | P2 |
| T07 Test tree | THD / EMC / NVH / Loss 命中；缺热冲击叶 | P2 |
| T08 protocol | THD/NVH 监控通道单独列出，good | P2 |

### 4.4 S04 `nonlinear_flux_lut`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | Nonlinear Flux LUT Observer 子块带 surface 缩略图，质量最高 | P2 |
| T02 sequence | sequence 中缺 LUT bounds 检查行 | P1 |
| T03 state | 6 状态命中，`recover to LUT` 与 `out-of-bounds detected` 闭环合理 | P2 |
| T04 PCB | LUT observer inputs 拆成多列，但密度过高、字号过小，整体偏 over-engineered | **P0** |
| T05 CAD | 出现 `M270-35A`、`NdFeB`、`ADC12`、`C11000` 等真实材料/工程牌号；mm 单位标注；3D 仿真感强 | **P0 BLOCKER** |
| T06 BOM | 5 分支命中 | P2 |
| T07 Test tree | 5 axis 命中；缺 FEA correlation residual 指标 leaf | P2 |
| T08 protocol | LUT version + bounds telemetry 通道清晰 | P2 |

### 4.5 S05 `magnetic_saturation_codesign`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | candidate→FEA→scorecard 流向清晰，但与 motor 电气主链耦合稍弱 | P1 |
| T02 sequence | sequence 主题与方案不贴合（依然是 traction inverter power-on） | P1 |
| T03 state | 顶部出现"MOTOR CONTROLLER SUBSYSTEM – FINITE STATE MACHINE"通用标题，**与本方案不是控制器无关，是 codesign 流水线** | **P0 GEN-01** |
| T04 PCB | saturation observer / bench ingestion 命中 | P2 |
| T05 CAD | barrier/bridge/lamination 等截面要素命中，但 3D 仿真感强 | P1 |
| T06 BOM | 4 分支命中 | P2 |
| T07 Test tree | 5 axis 命中；FEA correlation 命中 | P2 |
| T08 protocol | candidate ID + score versioning 命中 | P2 |

### 4.6 S06 `pmasynrm_high_saliency_low_pm`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | high-saliency 控制块 + demag boundary monitor 命中 | P2 |
| T02 sequence | sequence 与方案脱节，主题偏 traction inverter 默认 | P1 |
| T03 state | 命中 5 状态，但模型自行追加 `Fault Fallback` 第 6 状态（catalog 未列出），且通用标题 | **P0 GEN-01 + GEN-05** |
| T04 PCB | 高凸极控制输入 / demag diagnostic / position interface 命中 | P2 |
| T05 CAD | PM fraction + flux barrier + bridge + hairpin slot 命中；3D 仿真感强 | P1 |
| T06 BOM | 4 分支命中 | P2 |
| T07 Test tree | 5 axis 命中 | P2 |
| T08 protocol | saliency 控制 telemetry + demag warning 命中 | P2 |

### 4.7 S07 `variable_magnetization_memory_motor`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | 磁化脉冲驱动 + 储能 bank + interlock 命中；但缺 `research-pool concept` 水印 | P1 |
| T02 sequence | sequence 与方案脱节 | P1 |
| T03 state | 7 状态全列；`safe retreat` 自循环重复指向 `Safe retreat` 让闭环失效 | P1 |
| T04 PCB | pulse cap bank / bi-directional driver / isolation / interlock 命中 | P2 |
| T05 CAD | 出现 `M235-35A`、`35PN440`、`SmCo`、`NdFeB`、`420mm × 290mm × 130mm` 等真实牌号与尺寸，且整体是高写实 3D motor render | **P0 BLOCKER GEN-03 + GEN-04** |
| T06 BOM | pulse power / energy storage / magnet / observer / isolation 5 分支命中 | P2 |
| T07 Test tree | 5 axis 命中 | P2 |
| T08 protocol | flux state + lifetime cycle counter telemetry 命中；但缺 `research-pool` 水印 | P1 |

### 4.8 S08 `hybrid_excitation`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | field DC/DC + field winding + loss-of-field 命中 | P2 |
| T02 sequence | sequence 与方案脱节，仍以默认 traction power-on 为主 | P1 |
| T03 state | **状态机箭头方向错误**：`if reference set` 直接连到 `Loss-of-field detected`，`recover` 从 PM-only 回到 Three-variable control（应为回到 Idle） | **P0 GEN-05** |
| T04 PCB | field converter / current sense / loss-of-field / isolation 命中 | P2 |
| T05 CAD | 高写实 3D motor render，出现 brushless exciter 与详细 cross-section；偏 marketing | **P0 BLOCKER GEN-04** |
| T06 BOM | field power / winding / insulation / connectors / sensors 5 分支命中 | P2 |
| T07 Test tree | 4 axis 命中 | P2 |
| T08 protocol | field current + loss-of-field telemetry 命中 | P2 |

### 4.9 S09 `winding_reconfiguration`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | switch matrix / interlock / arc suppression 命中 | P2 |
| T02 sequence | sequence 与方案脱节 | P1 |
| T03 state | 6 状态命中；但 `Switch in progress` → `Circulating-current detected` 与 `arc suppression triggered` 标签解读暧昧，建议补 `then return to safe state` | P1 |
| T04 PCB | contactor/SSR driver / interlock / arc suppression / gate-disable backup 命中 | P2 |
| T05 CAD | 端部 / 重构开关 / 绝缘 / 线束 命中；偏写实 3D | P1 |
| T06 BOM | switches / interlock / harness / sensing 4 分支命中 | P2 |
| T07 Test tree | 4 axis 命中 | P2 |
| T08 protocol | winding config + switch state telemetry 命中 | P2 |

### 4.10 S10 `multiphase_phase_group_control`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | multiphase inverter + per-phase-group sense + fault torque allocator + harmonic subspace 命中 | P2 |
| T02 sequence | sequence 与方案脱节 | P1 |
| T03 state | 5 状态命中；`fault cleared` 从 Shut down 回 Healthy 是有问题的，正常 shut down 后需 service intervention | P1 |
| T04 PCB | multiphase inverter stage / per-phase group sense / isolation / phase-cutoff 命中 | P2 |
| T05 CAD | 多相端子 / 线束 / 相组封装 命中；偏写实 3D | P1 |
| T06 BOM | multiphase power module / sensing / connectors / harness / isolation 5 分支命中 | P2 |
| T07 Test tree | 5 axis 命中 | P2 |
| T08 protocol | phase health + harmonic subspace telemetry 命中 | P2 |

### 4.11 S11 `thermal_demag_safety_protection`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | Safety Supervisor 块（输入：磁钢温/绕组温/油温/Vdc/电流/转速）+ Gate Disable + Fault Status 输出，结构最完整 | P2 |
| T02 sequence | sequence 与方案脱节 | P1 |
| T03 state | 6 状态命中；`latch reset only by service` 标在 Latched fault → Normal 闭环上良好 | P2 |
| T04 PCB | sensor front-ends / fault latch / gate-disable HW / classification readback 命中；但节点填充偏深灰，未达 pale blue | P1（GEN-06） |
| T05 CAD | 磁钢/绕组/油温传感器 + 控制器 heatsink + 服务可达性命中；偏 3D 仿真感 | P1 |
| T06 BOM | 5 分支命中 | P2 |
| T07 Test tree | 5 axis + TST IDs（TST-THM-001…TST-LAT-005）整齐；但 TST IDs 与 `V2-S11-DVP-safety_fault_injection-r00.md` 的 `S11-DV-001..005` 不一致 | P1（GEN-11） |
| T08 protocol | safety fault classification + latch state telemetry 命中 | P2 |

### 4.12 S12 `weighted_efficiency_pareto_selection`

| 模板 | 关键发现 | r01 优先级 |
|---|---|---|
| T01 driver | Pareto Scorecard 主块 + 4 类输入 + 候选 ranking 输出非常清晰；trophy icon 略 marketing | P2 |
| T02 sequence | sequence 与方案脱节，缺 weight 版本与审计行 | P1 |
| T03 state | 顶部"MOTOR CONTROLLER SUBSYSTEM – FINITE-STATE MACHINE"标题严重失配（方案是 scorecard，非控制器） | **P0 GEN-01** |
| T04 PCB | 候选 BOM / 审计接口 / 版本注册 命中 | P2 |
| T05 CAD | 候选封装索引 命中 | P2 |
| T06 BOM | 4 分支命中 | P2 |
| T07 Test tree | drive cycle / system loss / sensitivity / evidence audit 4 axis 命中 | P2 |
| T08 protocol | scorecard version + audit telemetry 命中 | P2 |

---

## 5. r01 推进决策

| 决策 | 内容 |
|---|---|
| D-01 | 96 张中 **P0 必修 8 张**（S01/S02/S03/S04 T03，S04/S07/S08 T05，S05/S06/S12 T03 标题，S04 T04） |
| D-02 | **P1 建议修 40 张**，集中在 T02 sequence 与 T05 CAD 写实化弱化 |
| D-03 | **P2 可保留 48 张**，r00 已具备评审可视化锚点能力 |
| D-04 | r01 须扩展全局 negative prompt（GEN-03 / GEN-04） |
| D-05 | r01 须扩展全局 positive prompt（GEN-06 hex 颜色 + GEN-01 title token） |
| D-06 | r01 须按模板补 prompt 模式语句（GEN-05 显式枚举边）|
| D-07 | `gpt-image-2/prompts/schemes.json` 单条覆盖 size，落实 16:9 / 4:3 长宽比（GEN-02） |
| D-08 | 评审报告 + r01 prompt catalog 入 git；HTML/wiki 同步 |

---

## 6. r01 关键工程口径

1. r01 仍服务于"概念示意 / 评审可视化"，**不**晋级 EDA/CAD/FEA 输出。
2. r01 必须保留 `engineering_validated=false` 假设；任何被 r01 改善的 T05 写实化都仅是降低误读风险，不等于工程证据。
3. r01 必须保留 r00 PNG，归档为 `gpt-image-2/outputs/SXX/...-r00.png`，新版图按 `-r01.png` 命名落到同目录。
4. r01 prompt catalog 与 image worklist 分册必须双更新，避免漂移。
5. 评审与 r01 提示词包 git 提交按"docs: V2 生图包 r00 深度评审"与"docs: V2 生图包 r01 提示词"分别落地。

---

## 7. 待办与移交

| 待办 | 落点 | 责任 |
|---|---|---|
| 写 r01 prompt catalog | `codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18_r01.md` | Claude（本轮） |
| 更新分册增补 r01 提示词 | `codex-review/docs/image_worklist_2026-05-18/scheme-XX.md` 新增 `## r01 修订提示词` 节 | Claude（本轮） |
| 评审报告 HTML 同步 | `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.html` | Claude（本轮） |
| wiki 同步 | `wiki/v2_image_pack_review.md` | Claude（本轮） |
| 调整 `gpt-image-2/prompts/schemes.json` 长宽比 | T01/T02/T07/T08 单条 size 覆盖 | 下一轮（待用户确认） |
| 重生 P0 必修 8 张 | r01 提示词逐张回灌生图工具 | 下一轮（用户手动） |

---

## 8. 禁止误读

- 本报告判定的是 **生图与提示词的对齐度**，不是 **图与真实工程交付物的等价**。
- r00 96 张 PNG **不替代** PCB/EDA/CAD/FEA/HIL 任何文件；图面上的所有"看起来很专业"的标注都是 LLM 生成的近似。
- r01 提示词收敛后，若仍出现真实牌号或写实 render，**需立即拒收并重生**，不得入库。
- 本报告不修改 `engineering/v2/scheme-XX/` 任何 markdown 草案；任何方案语义改动必须先回到草案与 `.drawio` 源。
