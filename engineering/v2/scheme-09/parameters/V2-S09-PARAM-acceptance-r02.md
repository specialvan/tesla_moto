# V2-S09-PARAM-acceptance-r02 · RESEARCH POOL

方案：`winding_reconfiguration`
domain：electrical + safety + verification（合并 sheet，**研究池**）
关联：
- 仿真入口：`sim.run_winding_reconfiguration_experiment.run`
- 仿真绑定：`engineering/v2/scheme-09/parameters/V2-S09-PARAM-sim_binding-r02.json`
- DVP&R 草案：`engineering/v2/scheme-09/test_dvpr/V2-S09-DVP-switching_transient-r00.md`
- r01 视觉：`codex-review/docs/scheme_drawing_prompts_r01_batch/scheme-09-r01.md`

> **研究池声明**：EXP-008 仅 Ke/Kt 静态缩放代理。

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| 切换状态数 | 2（A=星形 / B=三角形等价） |
| Ke/Kt 配置 B | A × 1.73 | EXP-008 |
| 工程结论可认定 | 切换速度下的连续性检查（静态缩放） |
| 不可认定 | 接触器开关瞬态、电弧、环流、寿命 |

`engineering_validated = false`，research pool。

## 2. 研究池占位参数

| 参数 | 标称 | 单位 | 备注 |
|---|---|---|---|
| HV 接触器额定 | 800 V / 300 A | — | r01 estimate |
| Zero-torque window | 50-200 | ms | r01 estimate |
| 互锁验证延迟 | < 1 | ms | r01 estimate |
| 环流检测阈值 | 5 | A | r01 estimate |
| Arc 抑制 | 必需 | — | 工程占位 |

## 3. 不可破坏边界

1. **零扭矩窗口必须前置**：切换前必须 zero-torque 验证。
2. **非法状态 = 服务复位**：禁止自动 reset。
3. **互锁优先**：硬件互锁不依赖软件主循环。
4. `engineering_validated` 不翻。

## 4. 仿真绑定

```python
from sim.run_winding_reconfiguration_experiment import run
output = run()
```

期望产物：
- `experiment == "exp_008_winding_reconfiguration"`
- `configs ≥ 2`
- `transitions ≥ 1`
- `recommended_config` 存在
- `row_count ≥ 1`

## 5. DVP&R 验收映射

| DVP ID | 验证项 | 本 sheet 提供 |
|---|---|---|
| S09-DV-001 | 切换瞬态（zero-torque 50-200 ms） | §2 window |
| S09-DV-002 | 环流 < 5 A | §2 阈值 |
| S09-DV-003 | 电弧 / 绝缘 @ 800 V | §2 接触器额定 |
| S09-DV-004 | 非法状态 fallback < 1 ms | §2 互锁延迟 |

## 6. r02 → r03 升级清单

1. EXP-008 升级为接触器瞬态 + 环流 + 并联热分担模型。
2. 引入 arc suppression 电路模型。
3. 寿命与维修分析。
4. **保留研究池标识**。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；驱动 EXP-008 Ke/Kt 缩放代理 |
