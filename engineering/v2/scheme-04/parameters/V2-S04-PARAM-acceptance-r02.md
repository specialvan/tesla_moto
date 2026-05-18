# V2-S04-PARAM-acceptance-r02

方案：`nonlinear_flux_lut`
domain：control + verification（合并 sheet）
关联：
- 控制器源：`engineering/v2/scheme-04/controller/V2-S04-CTRL-flux_lut_interpolation-r00.drawio`
- PCB 草案：`engineering/v2/scheme-04/pcb/V2-S04-PCB-lut_observer_inputs-r00.md`
- DVP&R 草案：`engineering/v2/scheme-04/test_dvpr/V2-S04-TEST-flux_lut_correlation-r00.md`
- r01 视觉：`gpt-image-2/outputs/S04/V2-S04-ILL-T01-driver_block-r00.png` 与 r01 prompt
- 仿真入口：`sim.run_control_lut_generator.run`（`model_type="nonlinear_flux_lut"`）
- 仿真绑定：`engineering/v2/scheme-04/parameters/V2-S04-PARAM-sim_binding-r02.json`
- 数据底座：`models/flux_lut_sample.json`（合成样本，待 FEA 替换）

---

## 1. 适用边界

| 维度 | 范围 |
|---|---|
| LUT 输入 axes | id ∈ [-200, 0] A, iq ∈ [0, 200] A（来自 `flux_lut_sample.json` 默认） |
| LUT 输出 | λ_d, λ_q (Wb) |
| Vdc | 360 V 标称 |
| 温度 | 25 °C 标称（合成 LUT 不带温度切片） |
| 工程结论可认定 | LUT 边界检查、双线性插值一致性、fallback 行为 |
| 不可认定 | FEA 回灌、台架反标定、实际饱和地图 |

`engineering_validated = false`。`flux_lut_sample.json` 仅为合成样本，r02 / r03 必须替换为 FEA 或台架 LUT。

## 2. LUT 生产参数

### 2.1 输入 axes（来自 `flux_lut_sample.json`）

| 字段 | 范围 | 节点 |
|---|---|---|
| `id_axis_a` | [-200.0, 0.0] | 3 节点 |
| `iq_axis_a` | [0.0, 200.0] | 3 节点 |

> 合成 LUT 仅 3×3，r03 必须升级到 ≥ 30×30。

### 2.2 输出 / 插值

| 项 | 值 | 来源 |
|---|---|---|
| 输出量 | λ_d, λ_q | exp-006 |
| 插值方式 | 双线性 | drawio |
| 越界策略 | clamp + fallback to linear dq | drawio |
| residual high 阈值 | 12 % | r01 工程窗 |
| LUT CRC | CRC-32 IEEE 802.3 | r02 工程窗 |

### 2.3 LUT 输入 PCB / 采样精度

| 信号 | 精度 | 用途 |
|---|---|---|
| `id/iq` | 12-bit ADC ±0.5 % FS | LUT 插值坐标 |
| `theta_e` | resolver delay ≤ 60 μs | dq 变换 |
| `T` | 检测延迟 ≤ 1 ms | 温度切片选择（合成 LUT 不带 T 切片，r03 引入） |
| `vdc` | 12-bit ADC ±1 % FS | 可行性判断 |

## 3. 不可破坏边界

1. 合成 LUT 不代表真实饱和地图；任何 r02 仿真结论必须保留"sample-only"标识。
2. `lut_path` 必须解析到项目根目录内，外部绝对路径将被 `run()` 拒收。
3. 越界 fallback 必须 active，禁止外推。
4. `engineering_validated` 不翻。

## 4. 仿真绑定

```python
from sim.run_control_lut_generator import run
output = run(
    model_type="nonlinear_flux_lut",
    lut_path=Path("models/flux_lut_sample.json"),
    torque_axis_nm=[50.0, 80.0],
    torque_step_nm=30.0,
)
```

期望产物：
- `model_source.model_type == "nonlinear_flux_lut"`
- `model_source.flux_lut_ref == "models/flux_lut_sample.json"`
- `feasibility_map.infeasible_reasons.out_of_flux_lut_bounds` 反映 LUT 边界（r02 估值 ≥ 0）
- `feasibility_map.infeasible_reasons.search_not_converged` 由合成 LUT 范围决定（soft check）

## 5. DVP&R 验收映射

| DVP ID | 本 sheet 提供 |
|---|---|
| S04-DV-001 LUT 边界检查 | §4 out_of_flux_lut_bounds |
| S04-DV-002 双线性插值一致性 | §2.2 插值方式 + r03 pytest |
| S04-DV-003 FEA 几何版本绑定 | §2.1 axes + flux_lut_sample.json schema version |
| S04-DV-004 台架反标定相关性 | r03 / bench |
| S04-DV-005 residual high fallback | §2.2 residual 阈值 |

## 6. 升级清单（r02 → r03）

1. 合成 `flux_lut_sample.json` 替换为 FEA 导出的 ≥ 30×30 LUT。
2. 引入温度切片（≥ 5 个 T 点）。
3. 接入 EXP-006 nonlinear flux LUT phase-3。
4. residual high 阈值（12 %）由台架数据替换。

## 7. 版本变更

| 日期 | 修订 | 说明 |
|---|---|---|
| 2026-05-18 | r02 | 首次发布；驱动 sim.run_control_lut_generator 的 nonlinear LUT 分支 |
