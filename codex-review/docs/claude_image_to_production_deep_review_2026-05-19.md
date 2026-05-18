# Claude 图档生产化深度评审与打回意见

评审日期：2026-05-19  
评审包：`codex-review/docs`  
评审对象：Claude 产出的 V2 方案图档、生图评审、r01 提示词、r02 参数化文档、仿真绑定、工程图纸草案  
打回目标：要求 Claude 区分“概念图/提示词/参数表/仿真绑定/真实生产图纸”，并把下一轮工作从继续出图切到可验证工程交付物。

## 1. 总体判定

Claude 没有完成“把图档升级为带生产参数的真实图纸”。当前完成的是：

- 已生成 12 个方案的 r00 案例图和 r01 修订提示词；
- 已对 r00 生图做深度评审，并记录 P0/P1/P2 问题；
- 已建立部分 r02 生产参数 sheet 和 `sim_binding-r02.json`；
- 已用 pytest 证明若干绑定能调用现有仿真 runner；
- 已在多处文档中声明 `engineering_validated=false`。

但这些不等于真实 PCB、控制器电路图、CAD、BOM、EDA 或 FEA 交付物。现阶段仍应判定为：

```text
concept_image + prompt + parameter_proxy + simulation_binding
!= production drawing
!= manufacturing release
!= FEA/HIL/bench validation
```

本轮 Codex 打回意见：Claude 的图档工作可以作为概念审查和后续参数化入口，但不能作为生产图纸或仿真验证完成证据。下一轮必须先补“真实工程参数源、可执行仿真门禁、EDA/CAD/FEA 源文件边界”，再谈继续扩图。

## 2. 四项用户目标完成度核对

| 用户目标 | Claude 当前完成度 | 证据 | Codex 判定 |
|---|---:|---|---|
| 深度推进方案落地 | 部分完成 | `engineering/v2/scheme-*`、`models/scheme_simulation_coverage.json`、`tests/test_scheme_*` | 有目录、参数绑定和代理实验，但多数仍是 estimate / synthetic / proxy / research pool |
| 深度评审生图 | 已完成 | `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.md` | 对 96 张 r00 PNG 做了工程语义、风格、边界违规评审 |
| 落下版提示词 | 已完成 | `codex-review/docs/scheme_drawing_prompts_r01_batch/` | r01 prompt catalog 已落地，含全局约束和逐方案提示词 |
| 把图档升级为带生产参数的真实图纸 | 未完成 | `engineering/v2/*/{pcb,cad,controller,bom_eda}`、`production_parameters_digest.md` | 只有页面级草案与参数表，不是 STEP、EDA、Gerber、ODB++、FEA mesh、制造图纸 |

## 3. 关键证据

### 3.1 生图评审已经存在

`claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.md` 已覆盖：

- 12 个方案 × 8 模板 = 96 张 r00 PNG；
- P0/P1/P2 分类；
- T03 状态机错连、T05 CAD 写实化、真实材料牌号误入、通用标题泄漏等问题；
- 明确声明 r00/r01 PNG 不能提升 `engineering_validated`。

结论：Claude 做了深度评审生图，但评审对象是“图片与提示词的一致性”，不是“图纸可生产性”。

### 3.2 r01 提示词已经落地

`codex-review/docs/scheme_drawing_prompts_r01_batch/` 下已有：

- `_globals.md`
- `scheme-01-r01.md` 到 `scheme-12-r01.md`
- `production_parameters_digest.md`

结论：提示词落地完成，但提示词只能约束生成图外观与概念标注，不能生成真实 EDA/CAD/FEA 源文件。

### 3.3 r02 参数化有样板，但不是生产图纸

S02 已有相对完整的 r02 样板：

- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-control-r02.md`
- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-verification-r02.md`
- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json`
- `tests/test_scheme_02_lut_acceptance.py`
- `tests/test_scheme_p0_lut_acceptance.py`

这说明 Claude/Codex 已经开始把参数接入仿真。但 S02 仍存在：

- `Rs/Ld/Lq/psi_f` 仍是 estimate；
- demag limit 仍是估算曲线；
- S02 文档要求 jump ≤ 30 A，但 sim binding 实际放宽到 60 A；
- DTC、NVM、HIL 项仍是文档映射，不是硬件验证。

结论：S02 可作为“参数化闭环样板”，不能作为生产图纸样板。

### 3.4 PCB/CAD 文档主动声明不是制造文件

多个工程草案明确写明边界：

- `engineering/v2/scheme-02/cad/V2-S02-CAD-controller_packaging-r00.md`：不是 STEP、Parasolid、SolidWorks、Motor-CAD 或制造发布文件；
- `engineering/v2/scheme-02/pcb/V2-S02-PCB-control_io_map-r00.md`：不是 EDA 原理图、Layout、Gerber、ODB++；
- `engineering/v2/scheme-04/cad/V2-S04-CAD-fea_geometry_source-r00.md`：不是 Motor-CAD、Maxwell 或 FEA 网格文件；
- `engineering/v2/scheme-01/pcb/V2-S01-PCB-sensing_fault_path-r00.md`：不证明 ERC/DRC、隔离距离、热设计、BOM、Layout 或制造文件完成。

结论：这些文件是页面级审查草案，不是生产图纸。

## 4. 本轮 Review Findings 固化

### F-001：S02 仿真验收阈值被机器绑定放宽

证据：

- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-control-r02.md`
- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-verification-r02.md`
- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json`

问题：

S02 文档要求 mode transition 的 `id_jump_a` / `iq_jump_a` ≤ 30 A，但机器可读绑定实际设置为 60 A。pytest 按 JSON 执行，因此会出现“文档严格、测试宽松”的错觉。

打回要求：

- Claude 必须统一 markdown、JSON、pytest 三处阈值；
- 如果暂时必须放宽到 60 A，文档必须改成 r02 soft gate，并明确 r03 收敛目标为 30 A；
- 不允许把当前 60 A 通过写成 r03 生产验收通过。

### F-002：`passed_numeric_simulation` 命名过度承诺

证据：

- `models/scheme_simulation_coverage.json`

问题：

12 个方案均标为 `passed_numeric_simulation`，但多处 coverage note 写明仍是 synthetic LUT、scaled Ld/Lq proxy、virtual psi_f、research pool 或说明性工况。这会被误读为“仿真验证已经完成”。

打回要求：

将状态拆分为至少四类：

```text
binding_smoke_passed
numeric_proxy_passed
physics_model_validated
engineering_validated
```

现阶段大多数方案只能是前两类，不能写成工程仿真验证完成。

### F-003：S04 nonlinear flux LUT 验收过弱

证据：

- `engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json`
- `models/flux_lut_sample.json`

问题：

S04 只要求 `feasible_points_min = 1`，并允许 `search_not_converged` / `out_of_flux_lut_bounds` 作为 soft check 到 200。这只能证明代码路径可跑，不能证明非线性磁链 LUT 可用于控制或 FEA 相关性验证。

打回要求：

- 先把 `flux_lut_sample.json` 标为 synthetic smoke fixture；
- 引入 FEA-derived 30×30×T LUT 前，不得称为 nonlinear flux engineering validation；
- r03 必须至少验证 LUT bounds、插值残差、温度切片、控制搜索可行点比例、fallback 触发率。

### F-004：图纸仍是页面级草案

证据：

- `engineering/v2/scheme-02/cad/V2-S02-CAD-controller_packaging-r00.md`
- `engineering/v2/scheme-02/pcb/V2-S02-PCB-control_io_map-r00.md`

问题：

CAD/PCB 文档明确声明不是 STEP、EDA、Gerber、ODB++、FEA 网格或制造发布文件，因此不能作为生产参数或制造输入。

打回要求：

Claude 下一轮必须把每类图纸拆成：

- `concept_drawing`
- `parameter_sheet`
- `source_design_file`
- `simulation_input`
- `manufacturing_release`

当前文件只能放在 `concept_drawing` 或 `parameter_sheet` 档位。

### F-005：文档与实际代码状态不同步

证据：

- `engineering/v2/scheme-02/parameters/V2-S02-PARAM-verification-r02.md`
- `tests/test_scheme_02_lut_acceptance.py`
- `tests/test_scheme_p0_lut_acceptance.py`

问题：

验证文档写着 r02 不引入新代码、pytest 下一档再写，但仓库已经有 S02-only 和 P0 参数化 pytest。阶段边界混乱。

打回要求：

- Claude 必须更新 r02/r03 定义；
- 已存在的 pytest 要登记为当前事实；
- 后续文档不得写“计划增加”已经存在的文件。

## 5. 当前测试验证记录

本轮 Codex 执行了关键测试：

```text
pytest -vv tests/test_scheme_02_lut_acceptance.py
结果：3 passed

pytest -vv tests/test_scheme_p0_lut_acceptance.py
结果：12 passed

pytest -vv tests/test_scheme_experiment_acceptance.py
结果：24 passed
```

全量测试：

```text
pytest -q
结果：约 124 秒超时，并触发 Windows gbk stdout flush 问题
```

评审含义：

- 分组验收能证明 binding 可调用 runner；
- 不能证明真实生产参数已闭环；
- 全量验证链条仍需瘦身或分组，否则不适合作为稳定门禁。

## 6. Claude 下一轮必须返工的交付物

### P0：先修正状态口径

1. 修改 `models/scheme_simulation_coverage.json`，拆分状态，不再把所有方案统一写成 `passed_numeric_simulation`。
2. 对 synthetic / proxy / research pool 的方案增加机器可读字段：

```json
{
  "model_maturity": "synthetic_fixture|proxy_model|research_pool|physics_model",
  "production_drawing_ready": false,
  "manufacturing_release_ready": false,
  "engineering_validated": false
}
```

3. 更新 README、handoff、roadmap 中所有“已验证”表述。

### P0：统一 S02 验收阈值

1. 统一 `control-r02.md`、`verification-r02.md`、`sim_binding-r02.json`、pytest 的 jump 阈值；
2. 如果使用 60 A，必须标成 r02 proxy gate；
3. 如果目标是 30 A，pytest 必须按 30 A fail/pass。

### P0：重定义 S04 LUT 门禁

1. `feasible_points_min=1` 只能作为 smoke test；
2. 引入 FEA LUT 前，S04 状态只能是 `binding_smoke_passed`；
3. r03 门禁必须要求 FEA-derived LUT、温度切片、bounds 覆盖、fallback 率、残差阈值。

### P1：建立真实图纸交付物矩阵

每个方案必须新增或补齐以下矩阵：

| 类别 | 当前文件可否满足 | Claude 必须补的真实交付物 |
|---|---:|---|
| PCB | 否 | 原理图源、网表、BOM、封装库、Layout、DRC/ERC、Gerber/ODB++ |
| Controller | 部分 | 状态机源、控制参数、代码接口、故障注入、HIL 脚本 |
| CAD | 否 | STEP/Parasolid/SolidWorks/Motor-CAD 几何、datum、尺寸、公差 |
| FEA | 否 | Maxwell/Motor-CAD 模型、网格、材料、边界条件、求解设置、结果 LUT |
| DVP&R | 部分 | 测试脚本、输入数据、pass/fail 阈值、结果报告 |

### P1：把图片降级为审查锚点

所有 PNG、r01 prompt、图档目录必须显式标注：

```text
concept only
not a manufacturing drawing
not a simulation source
not an engineering validation artifact
```

图片可以引用 r02 参数表，但不能反向成为参数来源。

### P1：补充证据索引

Claude 必须把以下路径加入证据索引或工程包索引：

- `claude-review/docs/2026-05-18/v2_image_pack_r00_deep_review.md`
- `claude-review/docs/2026-05-18/v2_image_pack_r02_production_roadmap.md`
- `codex-review/docs/scheme_drawing_prompts_r01_batch/`
- `engineering/v2/scheme-*/parameters/*sim_binding-r02.json`
- `tests/test_scheme_02_lut_acceptance.py`
- `tests/test_scheme_p0_lut_acceptance.py`
- `tests/test_scheme_experiment_acceptance.py`

## 7. 打回 Claude 的验收标准

Claude 下一轮提交只有满足以下条件，才算“图档生产化推进有效”：

1. 每个方案明确标出当前档位：concept / parameterized / simulation-bound / physics-validated / production-ready。
2. 每个 `production parameter` 都有单位、公差、来源和 maturity，不允许 silent estimate。
3. 每个 `sim_binding` 的阈值和 markdown 文档一致。
4. 每个 pytest 是真实门禁，不只是字段存在检查。
5. PCB/CAD/Controller 不再被称为真实图纸，除非有对应源文件和制造/仿真输入。
6. `engineering_validated=false` 必须保持，直到 FEA + HIL + bench + manufacturing evidence 齐备。
7. r01 PNG 只能作为 concept anchor，不参与验收。

## 8. 建议 Claude 下一步执行顺序

1. 先修状态命名和 maturity 字段，防止误导。
2. 修 S02 阈值一致性，把 S02 做成唯一闭环样板。
3. 修 S04 LUT 门禁，明确 synthetic fixture 与 FEA LUT 的边界。
4. 建立真实图纸交付物矩阵，不继续把 markdown 草案称为 PCB/CAD 图纸。
5. 再补 S01/S11 的安全与退磁参数源。
6. 最后再回头生成 r01/r02 图片；图片只服务审查，不服务验收。

## 9. 最终打回结论

Claude 已经完成“概念图管理”和“提示词工程化”的大部分工作，也开始把部分方案接入参数化仿真。但用户要求的是“深度推进方案落地 + 图档升级为带生产参数的真实图纸”，当前交付还没有达到。

本轮应打回 Claude，要求其停止把生图成果包装成工程图纸成果，改为交付真实参数源、仿真门禁、EDA/CAD/FEA 源文件矩阵和可审计的 maturity 状态。

