# EXP-006 非线性磁链 LUT 实验

## 1. 目标

EXP-006 分两层：

- phase-1：验证 synthetic `lambda_d/lambda_q` LUT 的 schema、边界检查、双线性插值和非线性转矩公式；
- phase-2：把该 LUT 接入现有电压/电流约束搜索链路，验证 target torque 与 max feasible torque 搜索会真实使用非线性磁链，而不是停留在线性 dq 近似。

本实验仍是干净室 synthetic 样例，不代表 FEA 或工程释放。

## 2. 产物

### phase-1

- `summary.json`
- `nonlinear_flux_lut_results.csv`

### phase-2

- `lut_search_summary.json`
- `lut_search_scan_results.csv`

## 3. 当前结论

- phase-1 已证明：LUT 文件契约、越界拒绝、双线性插值和非线性转矩计算可复现。
- phase-2 已证明：在保持 EXP-001 线性 baseline 不变的前提下，`search.py` 可选接入 LUT 并在电压/电流约束下执行 speed sweep 搜索。
- 对当前 sample LUT：
  - `id=0` 路径下无法达到 100 Nm，因此 `id_zero_target_max_speed_rpm = null`；
  - 在 0 rpm、当前约束下，最大可行点出现在 LUT 边界内的插值搜索结果，而非简单回退到线性 dq 模型。

## 4. 仍未完成

- 仍未接入 FEA 或实测 `lambda_d/lambda_q` 数据。
- 仍未接入共享控制 LUT 导出、MTPA / FW / MTPV 切换连续性检查。
- 仍未接入铁耗、逆变器压降、热和退磁边界。

## 5. 运行方式

```powershell
python -m sim.run_nonlinear_flux_lut_experiment
python -m sim.run_nonlinear_flux_lut_search_experiment
python -m pytest -q tests/test_nonlinear_flux_lut.py tests/test_nonlinear_flux_lut_search.py
```
