# V2-S06 仿真证据追溯 r00

状态：`draft`。

## 1. 当前证据

| 证据 | 路径 | 可证明 | 不可证明 |
|---|---|---|---|
| EXP-003 param sweep | `experiments/exp_003_param_sweep/summary.json` | 高凸极、低磁链、Vdc/Imax 协同趋势 | 真实 PMaSynRM 拓扑可制造 |
| DVP 草案 | `test_dvpr/V2-S06-DVP-pmasynrm_validation-r00.md` | torque ripple、应力、退磁、热、NVH 验证计划 | 已执行验证 |
| CAD/CTRL/BOM r00 | 本目录 r00 文件 | 生产参数字段和评审对象 | 正式拓扑发布 |

## 2. 升级链路

1. 以 PM fraction 和 saliency ratio 定义候选拓扑。
2. 生成 rotor/stator CAD 和 FEA LUT。
3. 回灌控制 LUT，验证 MTPA/MTPV/退磁边界。
4. 对候选进行 S12 drive-cycle 和成本风险 Pareto。

## 3. 下版提示词

生成 S06 traceability diagram，从 EXP-003 saliency trend 到 low-PM CAD topology、FEA LUT、MTPA/MTPV control map、demag/thermal guard、BOM cost risk、DVP gate。白底流程图，英文标签。