# S12 r01 提示词批包 · weighted_efficiency_pareto_selection

修订日期：2026-05-18  
方案 ID：`weighted_efficiency_pareto_selection`  
工程目录：`engineering/v2/scheme-12/`（仅 README，drive cycle 聚合方案）  
依据：reports / `models/scheme_engineering_catalog.json`

## 0. SCHEME_TITLE

| 模板 | 文本 |
|---|---|
| T01 | `S12 WEIGHTED EFFICIENCY PARETO SELECTION — SCORECARD BLOCK` |
| T02 | `S12 PARETO SCORECARD — POWER-ON SEQUENCE` |
| T03 | `S12 PARETO SCORECARD PIPELINE — STATE MACHINE` |
| T04 | `S12 SCORECARD AUDIT — CONCEPT PCB SHEET (CONCEPT ONLY)` |
| T05 | `S12 CANDIDATE PACKAGING INDEX — CONCEPT (CONCEPT ONLY)` |
| T06 | `S12 PARETO COST / RISK — BOM / EDA RISK TREE` |
| T07 | `S12 PARETO TRACEABILITY — VERIFICATION PLAN` |
| T08 | `S12 PARETO SCORECARD — PROTOCOL LINK` |

## 1. 生产参数

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| 候选方案数 | 11（S01-S11） | — | catalog |
| Drive cycle 权重 | WLTP 0.4 / CLTC 0.3 / Urban 0.2 / Highway 0.1 | — | r01 估值 |
| Score 维度 | 5（效率 / 性能 / 成本 / 体积 / 风险） | — | r01 估值 |
| Maturity score | 1-5（TRL 等价） | — | r01 工程窗 |
| Risk score | 1-5 | — | r01 工程窗 |
| Pareto 维度 | torque, loss, mass, cost, maturity | — | r01 估值 |
| Sensitivity sweep | ±20 % 权重扰动 | — | r01 估值 |

## 2. T01-T08 完整提示词

### T01 scorecard block

```text
[image_id] IMG-S12-T01-r01
[priority] P1
[size] 1792x1024
[positive prompt]
Flat scorecard pipeline diagram for S12 weighted efficiency pareto selection.
Title: "S12 WEIGHTED EFFICIENCY PARETO SELECTION — SCORECARD BLOCK".
This is NOT a motor controller chain. It is a candidate ranking pipeline.
Left inputs (4 stacked blocks): "Drive Cycle Weights (WLTP 0.4, CLTC 0.3,
Urban 0.2, Highway 0.1)", "System Losses (motor + inverter + cooling)",
"Maturity Scores (1-5, TRL equivalent)", "Risk Factors (1-5)".
Center: "Pareto Scorecard (Weighted Multi-Criteria across 5 axes:
efficiency / performance / cost / volume / risk)".
Right output: "Candidate Ranking (S01-S11 ordered, plain rectangle, no trophy icon)".
Below center: small mini chart "Pareto front" representation.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- all weight values verbatim
- NO trophy icon (replace with plain ranking rectangle)
```

### T02 sequence

```text
[image_id] IMG-S12-T02-r01
[priority] P2
[size] 1792x1024
[positive prompt]
UML sequence for S12 scorecard pipeline. Title:
"S12 PARETO SCORECARD — POWER-ON SEQUENCE".
Lifelines: Engineer, Data Repo, Scorecard Engine, Audit Log, Decision Maker.
Steps:
(1) Engineer->Data Repo "submit candidate set S01-S11 with version refs"
(2) Data Repo->Scorecard "load loss + maturity + risk + cost vectors"
(3) Scorecard self "apply weights WLTP 0.4 / CLTC 0.3 / Urban 0.2 / Highway 0.1"
(4) Scorecard self "compute 5-axis scores; pareto sweep ±20 % weight sensitivity"
(5) Scorecard->Audit Log "audit hash + version trail"
(6) Scorecard->Decision Maker "ranked S01-S11 with sensitivity bands"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- audit hash + version trail step visible
```

### T03 state machine（**P0 必修**）

```text
[image_id] IMG-S12-T03-r01
[priority] P0
[size] 1024x1024
[positive prompt]
Finite-state-machine for S12 pareto scorecard pipeline. Title:
"S12 PARETO SCORECARD PIPELINE — STATE MACHINE".
DO NOT use "MOTOR CONTROLLER SUBSYSTEM" title (this is not a motor controller).
<r01 ENUM RULE>
STATES (exactly 6):
  "Candidate intake (S01-S11)"
  "Drive cycle weighting (WLTP 0.4 / CLTC 0.3 / Urban 0.2 / Highway 0.1)"
  "System loss aggregation (motor + inverter + cooling)"
  "Maturity + risk scoring (1-5 each)"
  "Pareto ranking (5-axis sweep, ±20 % sensitivity)"
  "Trade-study output (audit hash + version trail)"
EDGES (exactly 6):
  "Candidate intake (S01-S11)" -> "Drive cycle weighting (WLTP 0.4 / CLTC 0.3 / Urban 0.2 / Highway 0.1)" : "inputs versioned"
  "Drive cycle weighting (WLTP 0.4 / CLTC 0.3 / Urban 0.2 / Highway 0.1)" -> "System loss aggregation (motor + inverter + cooling)" : "weights applied"
  "System loss aggregation (motor + inverter + cooling)" -> "Maturity + risk scoring (1-5 each)" : "losses computed"
  "Maturity + risk scoring (1-5 each)" -> "Pareto ranking (5-axis sweep, ±20 % sensitivity)" : "scores ready"
  "Pareto ranking (5-axis sweep, ±20 % sensitivity)" -> "Trade-study output (audit hash + version trail)" : "pareto sweep done"
  "Trade-study output (audit hash + version trail)" -> "Candidate intake (S01-S11)" : "recommendation issued"
Highlight no node red (pipeline has no fault state).
NO traction motor or inverter imagery anywhere in the diagram.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- title verbatim; NO motor controller imagery
- 6 states with parenthetical numeric annotations
```

### T04 PCB concept

```text
[image_id] IMG-S12-T04-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Conceptual PCB sheet for S12 audit interface. Title:
"S12 SCORECARD AUDIT — CONCEPT PCB SHEET (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
S12 does NOT introduce new hardware. Show this as a reference layout only:
Groups:
(REFERENCE) "S01-S11 candidate PCB / BOM / EDA version references (no real PCB here)"
(AUDIT) "Audit trail interface (hash, version, timestamp)"
(REGISTRY) "Version registry (candidate, weight set, pareto run)"
(EXPORT) "Trade-study export interface (csv, json)"
Add a banner: "S12 is a scorecard, not new hardware. Reference only."
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- banner explicitly says scorecard not hardware
- 4 reference groups
```

### T05 CAD packaging concept

```text
[image_id] IMG-S12-T05-r01
[priority] P2
[size] 1280x1024
[positive prompt]
Conceptual LINE illustration for S12 candidate package index.
Title: "S12 CANDIDATE PACKAGING INDEX — CONCEPT (CONCEPT ONLY)".
<r01 CONCEPT WATERMARK>
Show as 11 labeled empty rectangles in a row, each labeled with a candidate
ID (S01-S11) and 3 small attribute pills underneath: "mass", "envelope",
"cooling". Show generic units (kg, mm³, kW thermal capacity) without
specific values. Add a banner "Candidate packaging index — no real CAD geometry here.
Each box is a placeholder for the corresponding scheme's CAD package."
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 11 candidate placeholders
- banner explicit
```

### T06 BOM tree

```text
[image_id] IMG-S12-T06-r01
[priority] P2
[size] 1024x1024
[positive prompt]
BOM cost / risk tree for S12. Title: "S12 PARETO COST / RISK — BOM / EDA RISK TREE".
Root "S12 weighted_efficiency_pareto_selection".
FIXED:
- "Per-candidate BOM cost (S01-S11 cost matrix)" -> MED
- "Manufacturing risk (per-candidate)" -> MED
- "Supply risk (per-candidate)" -> HIGH
- "Controller delta cost (per-candidate vs baseline)" -> MED
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- 4 branches with FIXED risk
```

### T07 verification tree

```text
[image_id] IMG-S12-T07-r01
[priority] P2
[size] 1792x1024
[positive prompt]
Verification plan for S12. Title: "S12 PARETO TRACEABILITY — VERIFICATION PLAN".
Branches:
(S12-DV-001) "Drive cycle audit (WLTP / CLTC / Urban / Highway sources versioned)"
(S12-DV-002) "System loss audit (per-candidate motor / inverter / cooling sources)"
(S12-DV-003) "Sensitivity sweep (±20 % weight perturbation stable ranking)"
(S12-DV-004) "Evidence-path audit (every candidate has PCB / CAD / BOM / DVP traces)"
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- audit nature emphasized
- numeric ±20 % sweep visible
```

### T08 protocol link

```text
[image_id] IMG-S12-T08-r01
[priority] P2
[size] 1024x1280
[positive prompt]
Data flow block for S12. Title: "S12 PARETO SCORECARD — PROTOCOL LINK".
Vertical chain (data, not control):
"Candidate Repo (engineering/v2/scheme-XX/)" ->
"Scorecard Engine (weights + scores + pareto)" ->
"Scorecard Version + Audit Telemetry (hash, version, timestamp)" ->
"Decision Maker".
Right branches: "Audit log archive", "Trade-study export (CSV / JSON)".
Edges use generic "data pipe" labels with version + CRC annotations.
NO traction control chain anywhere.
<r01 GLOBAL POSITIVE>
[negative prompt]
<r01 GLOBAL NEGATIVE>
[acceptance]
- NO motor / inverter / FOC / SVPWM imagery
- version + audit edges visible
```

## 3. 归档勾选

| 图 ID | 优先级 | r01 PNG | prompt.txt |
|---|---|---|---|
| IMG-S12-T01-r01 | P1 | [ ] | [ ] |
| IMG-S12-T02-r01 | P2 | [ ] | [ ] |
| IMG-S12-T03-r01 | **P0** | [ ] | [ ] |
| IMG-S12-T04-r01 | P2 | [ ] | [ ] |
| IMG-S12-T05-r01 | P2 | [ ] | [ ] |
| IMG-S12-T06-r01 | P2 | [ ] | [ ] |
| IMG-S12-T07-r01 | P2 | [ ] | [ ] |
| IMG-S12-T08-r01 | P2 | [ ] | [ ] |
