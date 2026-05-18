# V2-S03 仿真/测试证据绑定 r00

状态：`draft`。

## 1. 当前可用证据

| 证据 | 路径 | 可证明 | 不可证明 |
|---|---|---|---|
| EXP-005 modulation factor | `experiments/exp_005_modulation_factor/summary.json` | 调制因子代理下的电压利用率收益 | 真实 PWM 谐波、EMC、NVH、逆变器损耗 |
| DVP 草案 | `test_dvpr/V2-S03-DVP-thd_emc_nvh-r00.md` | 测试项目和门槛定义 | 已执行测试结果 |
| PCB/CAD/CTRL/BOM r00 | 本目录相关 r00 文件 | 工程评审对象 | 真实 EDA/CAD/台架发布 |

## 2. 证据升级链路

1. 用 EXP-005 选出 `k_mod` 候选窗口。
2. 在 PWM 重建模型中输出相电流 THD、转矩纹波和开关损耗。
3. 回灌 S03 PCB/CAD 热路径，判断 deep overmod dwell 是否需要降额。
4. 进入 HIL/bench，执行 DVP 的 THD、EMC、NVH 和热冲击项。

## 3. Gate 判断

- G2：本 r00 图纸草案齐套。
- G3：PWM/损耗/热/NVH 模型与 CAD 热路径绑定。
- G4：EDA/PCB 原理图和 BOM 可审查。
- G5：DVP 执行并产生台架证据。

## 4. 下版提示词

生成 S03 overmodulation evidence traceability diagram，从 EXP-005 k_mod sweep 到 PWM harmonic model、inverter loss map、PCB/CAD thermal path、THD/EMC/NVH DVP、gate review。白底流程图，英文标签，强调“proxy simulation is not validation”。