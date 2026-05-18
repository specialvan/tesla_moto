# V2-S05 仿真证据追溯 r00

状态：`draft`。

## 1. 当前证据

| 证据 | 路径 | 可证明 | 不可证明 |
|---|---|---|---|
| EXP-003 param sweep | `experiments/exp_003_param_sweep/summary.json` | 高凸极/低磁链协同的参数趋势 | 真实 barrier/bridge 几何可行 |
| DVP 草案 | `test_dvpr/V2-S05-DVP-saturation_codesign-r00.md` | FEA、应力、铁耗、退磁、NVH 测试计划 | 已执行验证 |
| CAD/BOM/CTRL r00 | 本目录 r00 文件 | 可评审生产参数字段 | 正式 CAD/FEA 发布 |

## 2. 升级路径

1. 选择 3~5 个 rotor barrier/bridge 候选几何。
2. 为每个候选生成 FEA LUT 和应力结果。
3. 回灌 control LUT search，输出 drive-cycle scorecard。
4. 对通过候选执行 DVP 中的铁耗、退磁、NVH 和应力验证。

## 3. 下版提示词

生成 S05 evidence traceability diagram，从 EXP-003 parameter trend 到 rotor CAD candidates、FEA flux LUT、stress FEA、iron loss、demag boundary、control scorecard、DVP gate。白底工程流程图，英文标签。