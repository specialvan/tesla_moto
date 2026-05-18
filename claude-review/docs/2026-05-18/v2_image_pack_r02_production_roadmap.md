# V2 方案图档生产参数化深推路线

日期：2026-05-18
目标：把 12 方案的图档体系从"概念可视化"升级为"可落地、带生产参数、能进入仿真测试的真实图纸"
事实源：
- `models/motor_params.json` `models/control_lut.json` `models/control_lut_schema.json`
- `sim/run_control_lut_generator.py` `tests/test_control_lut_generator.py`
- `engineering/v2/scheme-XX/` PCB/CAD/Controller/BOM/Test 草案
- `gpt-image-2/outputs/` r00 96 张概念 PNG

---

## 0. 路线决策（用户目标）

> 所有图档不是简单演示，要持续深度推进，按对应方案的深挖理解，变成可落地带生产参数的真实图纸，能完成后续的仿真测试。

按此目标，每个方案的"图档"不再等价于"一张 PNG"，而是由 **图像 + 生产参数表 + 仿真接口** 三件组成的复合资产。每件资产都必须可审计、可重生、可被仿真链路读取。

---

## 1. 四档深推梯度

| 档位 | 名称 | 交付物 | 工程使命 | 用户可见的"图档" |
|---|---|---|---|---|
| **r00** | 概念可视化 | `gpt-image-2/outputs/SXX/...-r00.png` + `-prompt.txt` | 评审/汇报锚点 | 96 张 PNG |
| **r01** | 风格收敛 + 工程语义对齐 | `...-r01.png` + r01 prompt | 修正状态机错连、删真实牌号、加 CONCEPT 水印 | 96 张 r01 PNG |
| **r02** | 生产参数化（**当前推进点**） | `engineering/v2/scheme-XX/<category>/V2-SXX-<DOMAIN>-...-r02.{md,json,csv}` | 每张概念图配套一份"生产参数 sheet"，含 SI 单位数值、公差、阈值、温度范围、寿命循环 | r02 sheet 文档（与 PNG 并列归档） |
| **r03** | 仿真闭环 | `sim/run_scheme_XX_*.py` + `tests/test_scheme_XX_*.py` + `models/scheme_XX_lut.json` | 生产参数→仿真入口→pytest 自动验证 pass/fail | 数值仿真曲线 + JSON 输出 |

> r02 是当前推进的核心；r03 是 r02 落地后立即承接的下一档。  
> r00/r01 不被废弃，仍作为评审视觉锚点共存。

---

## 2. r02 生产参数 sheet 通用模板

每方案在 `engineering/v2/scheme-XX/parameters/` 下新建（首次写入即建立目录）：

```text
engineering/v2/scheme-XX/parameters/
  V2-SXX-PARAM-electrical-r02.md      # 电气生产参数
  V2-SXX-PARAM-mechanical-r02.md      # 机械 / CAD 生产参数
  V2-SXX-PARAM-thermal-r02.md         # 温度 / 散热生产参数
  V2-SXX-PARAM-control-r02.md         # 控制算法 / LUT 生产参数
  V2-SXX-PARAM-safety-r02.md          # 安全 / 故障路径生产参数
  V2-SXX-PARAM-verification-r02.md    # DVP&R pass/fail 阈值
  V2-SXX-PARAM-sim_binding-r02.json   # 仿真接口绑定（路径 + 入参 + 期望产物）
```

### 2.1 每张 sheet 通用骨架

```markdown
# V2-SXX-PARAM-<domain>-r02

方案：<scheme_id>
domain：<electrical|mechanical|thermal|control|safety|verification>
关联图：<相对路径 PNG / drawio / mermaid>
仿真入口：<sim/run_*.py>
DVP&R 入口：<engineering/v2/scheme-XX/test_dvpr/*.md>

## 1. 适用边界
- 适用版本、温度、电压、转速、转矩
- 哪些工程结论可被认定，哪些不可

## 2. 生产参数（带 SI 单位 + 公差 + 来源）
| 参数 | 符号 | 标称值 | 公差 | 单位 | 来源 | 阶段门 |
|---|---|---|---|---|---|---|

## 3. 不可破坏边界
- 不得越过的物理上限、ASIL/安全限值、温度/退磁边界

## 4. 仿真绑定
- 仿真入口 + 入参 JSON / CSV 路径 + 期望 pass 条件

## 5. 待落实
- 哪些值仍是估值；下一步如何替换为 FEA/台架数据
```

### 2.2 强制字段

| 字段 | 强制要求 |
|---|---|
| 每个数值 | 必须带单位与公差 |
| 每个参数 | 必须有来源（仿真 / FEA / 台架 / 文献 / 估值），并标 `Stage Gate` |
| 每个 sheet | 必须列"不可破坏边界" |
| 每个 sheet | 必须给仿真绑定路径 |

### 2.3 不可破坏边界（继承 r00/r01 并扩展）

1. r02 仍保持 `engineering_validated=false`，**只有** r03 仿真闭环通过后才能在覆盖目录上标记 `passed_numeric_simulation`；FEA / 台架实测仍属于更后档。
2. 估值（estimate）必须被显式标注 `source: estimate`，不得伪装为台架值。
3. 所有生产参数变更必须在草案 / `.drawio` / mermaid 源回溯；不允许 r02 sheet 与草案出现"先于源"的数值。

---

## 3. 12 方案 r02 推进矩阵

| 方案 | 当前可启动 r02 | 优先级 | 关键 sheet |
|---|---|---|---|
| S01 negative_d_axis_field_weakening | 是（已有 PCB/CAD/Controller/BOM/DVP 草案） | **P0** | electrical / control / safety |
| S02 mtpa_fw_mtpv_control | 是（草案 + `control_lut.json` + `motor_params.json`） | **P0** | control / verification（首份示范） |
| S03 svpwm_overmodulation | 部分（仅 README，需先补 PCB/CAD 草案） | P1 | electrical / verification |
| S04 nonlinear_flux_lut | 是（已有草案 + EXP-006 phase-2 通过） | **P0** | control / verification（FEA LUT 入口） |
| S05 magnetic_saturation_codesign | 部分（仅 README） | P2 | mechanical / verification |
| S06 pmasynrm_high_saliency_low_pm | 部分（仅 README） | P2 | mechanical / electrical |
| S07 variable_magnetization_memory_motor | 部分（仅 README，研究池） | P2 | safety / verification（标 research_pool） |
| S08 hybrid_excitation | 部分（仅 README，研究池） | P2 | electrical / control |
| S09 winding_reconfiguration | 部分（仅 README，研究池） | P2 | safety / electrical |
| S10 multiphase_phase_group_control | 部分（仅 README，研究池） | P2 | electrical / safety |
| S11 thermal_demag_safety_protection | 是（已有 PCB/CAD/Controller/BOM/DVP 草案） | **P0** | thermal / safety / verification |
| S12 weighted_efficiency_pareto_selection | 部分（仅 README，工况权重） | P1 | verification（聚合候选） |

### 3.1 P0 启动顺序（建议）

| 顺序 | 方案 | 理由 |
|---|---|---|
| 1 | S02 mtpa_fw_mtpv_control | 控制 LUT 已有 JSON、仿真入口已 ready、可立即验证 r02→r03 链路 |
| 2 | S04 nonlinear_flux_lut | EXP-006 phase-2 已通过、flux_lut_sample.json 可承接 |
| 3 | S11 thermal_demag_safety_protection | 复用 control LUT 的退磁限制接口，统一安全语义 |
| 4 | S01 negative_d_axis_field_weakening | 弱磁/id_min 安全限值可绑定 S11 thermal 表 |

---

## 4. r02 与 r01 / 仿真的衔接

```text
r00 concept PNG  ─┐
                  ├─→ r01 prompt 收敛 (codex-review/docs/...r01.md)
                  │     ├─→ r01 PNG（视觉合格）
                  │     └─→ 引用至 r02 parameter sheet 作为视觉锚点
                  │
                  └─→ r02 production parameter sheet
                        ├─→ engineering/v2/scheme-XX/parameters/V2-SXX-PARAM-*.md
                        ├─→ engineering/v2/scheme-XX/parameters/V2-SXX-PARAM-sim_binding-r02.json
                        └─→ r03 仿真闭环
                              ├─→ sim/run_scheme_XX_*.py 读 sim_binding-r02.json
                              ├─→ tests/test_scheme_XX_*.py pytest 校验 pass/fail
                              └─→ models/scheme_simulation_coverage.json 翻转状态
```

### 4.1 与现有 control LUT 链路的直接复用

- `sim/run_control_lut_generator.py` 已经支持 `model_type / lut_path / temperature_c / demag_limit / torque_axis_nm` 等入参；这正是 r02 sheet 的接口。
- S02 r02 sheet 的 `sim_binding-r02.json` 可写：

```json
{
  "entry": "sim.run_control_lut_generator",
  "function": "run",
  "kwargs": {
    "motor_params_path": "models/motor_params.json",
    "torque_axis_nm": [50.0, 100.0, 150.0, 200.0],
    "temperature_c": 80.0,
    "demag_limit": {"id_min_at_25c_a": -240.0, "temp_coefficient": -0.0035}
  },
  "expect": {
    "mode_counts": {"INFEASIBLE_max": 0},
    "feasibility_map.infeasible_reasons.demagnetization_risk_max": 8,
    "validation.torque_discontinuity_at_transitions_nm_max": 5.0
  }
}
```

- r03 pytest 用 `pytest tests/test_scheme_02_lut_acceptance.py` 自动跑这条 binding，落到 `models/scheme_simulation_coverage.json`。

### 4.2 与 r01 视觉的反向引用

- 每张 r02 sheet 顶部必须引用对应 r01 PNG（即便 r01 尚未重生，先引 r00），保证审计可视化。
- r01 PNG 上的 CONCEPT watermark 不会因为 r02 sheet 而消失；视觉永远是概念，**参数才是工程**。

---

## 5. r03 仿真闭环准入条件（提前定义）

为防止 r02 sheet 写成"无人读的文字"，r03 仿真闭环对每个 sheet 提出以下准入：

1. **可执行**：`sim_binding-r02.json` 必须能被 `sim.run_scheme_XX_*.py` 或 `pytest tests/test_scheme_XX_*.py` 读取，无人工拼接。
2. **可校验**：`expect` 必须给数值阈值（不是"看起来合理"）。
3. **可回归**：每次参数变更走 git；pytest 必须能跑通新旧两套以做差异化测试。
4. **覆盖矩阵**：r03 通过即在 `models/scheme_simulation_coverage.json` 的对应方案标 `passed_numeric_simulation`，标 `engineering_validated=false`。

---

## 6. r02 示范交付（本轮启动）

| 交付物 | 路径 | 说明 |
|---|---|---|
| S02 control sheet 示范 | `engineering/v2/scheme-02/parameters/V2-S02-PARAM-control-r02.md` | 首份完整生产参数 sheet，含 LUT 阈值、模式切换、CRC、NVM、温度修正 |
| S02 sim_binding 示范 | `engineering/v2/scheme-02/parameters/V2-S02-PARAM-sim_binding-r02.json` | 直接绑 `sim/run_control_lut_generator.py:run` |
| S02 verification sheet 示范 | `engineering/v2/scheme-02/parameters/V2-S02-PARAM-verification-r02.md` | DVP&R 验收阈值与 pytest 期望 |
| 本路线图 | `claude-review/docs/2026-05-18/v2_image_pack_r02_production_roadmap.md` | 12 方案 r02→r03 全图 |

S02 的示范交付是路线可执行性证明；其他 11 方案按 §3.1 排序逐方案推进。

---

## 7. 风险与控制

| 风险 | 影响 | 控制 |
|---|---|---|
| 把估值写成台架值 | r02 误升为工程验证 | 强制 `source` 字段 + code review 禁止 silent estimate |
| sim_binding-r02.json 与代码漂移 | r03 仿真假绿 | pytest 校验 binding 路径与函数签名 |
| 12 方案同时推 r02 导致质量稀释 | r02 表面化、不能进入 r03 | 按 §3.1 P0 顺序，确认 r03 可跑后再推下一方案 |
| r02 sheet 与草案 / drawio 数值不一致 | 数据双源不一致 | r02 sheet 内引用草案路径，PR 阶段做 diff 检查 |
| 用户期望 r02 立即等价于工程发布 | 误把 r02 解读为可量产 | r02 顶部强制 `engineering_validated=false` 声明 |

---

## 8. 不可破坏边界

1. **r02 不替代 EDA / CAD / FEA / HIL**：r02 是参数表，不是 schematic / STEP / FEA mesh。
2. **r03 不替代台架**：r03 是数值仿真闭环，不是台架实测。
3. **生图 PNG 永远是概念**：即使 r01 / r02 / r03 推进，r00 / r01 PNG 仍带 CONCEPT 水印。
4. **真实牌号仍禁用**：r02 sheet 的"来源"字段允许 brand-agnostic family 描述（如 "automotive-grade NTC"），不允许具体型号（如 NCP21XV103J03RA）。
5. **`engineering_validated`**：仅当 r03 通过 + FEA 回灌 + 台架样件实测齐备时才可翻转，r02 / r03 自身不翻转。

---

## 9. 下一步

| 行动 | 责任 | 状态 |
|---|---|---|
| S02 r02 三张示范 sheet 落地 | Claude（本轮） | 进行中 |
| S04 / S11 / S01 r02 sheet 推进 | 下一轮 Claude / Codex | 待执行 |
| r03 sim_binding pytest harness | 下一轮代码变更 | 待规划 |
| 工作目录中现有 V2 P0 DVP&R 草案与 v0.3 control LUT 闭环代码提交 | 与 r02 路线分开 commit | 待执行 |
| r01 P0 8 张重生 | 用户手动 | 待执行 |
