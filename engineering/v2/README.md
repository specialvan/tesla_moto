# V2 工程图纸包索引

本目录用于把 V2 分方案物理工程交付物矩阵落到可审计的仓库路径。当前只放置 README 索引，不伪造 PCB、3D/CAD、EDA、控制器图或测试报告文件。

关联文档：

- `claude-review/docs/2026-05-15/v2_scheme_physical_deliverables_matrix.md`
- `reports/scheme_driver_power_protocol_diagrams.md`
- `reports/scheme_bom_eda_integration_design.md`

## 1. 目录规则

每个方案目录后续按以下结构扩展：

```text
scheme-XX/
  pcb/
  cad/
  controller/
  bom_eda/
  simulation/
  test_dvpr/
  gate_review/
```

当前阶段已创建 `scheme-XX/README.md` 和各分类空目录锚点，用于记录必需图纸、当前状态和下一步动作；`.gitkeep` 只证明目录已落位，不代表图纸已交付。

## 2. 12 个方案入口

| ID | 方案 | 目录 | 当前图纸包状态 |
|---|---|---|---|
| S01 | 负 d 轴弱磁 | `scheme-01/` | README 索引已建，图纸未落地 |
| S02 | MTPA/FW/MTPV 连续控制 | `scheme-02/` | README 索引已建，图纸未落地 |
| S03 | SVPWM/过调制 | `scheme-03/` | README 索引已建，图纸未落地 |
| S04 | 非线性磁链 LUT | `scheme-04/` | README 索引已建，图纸未落地 |
| S05 | 磁路饱和协同设计 | `scheme-05/` | README 索引已建，图纸未落地 |
| S06 | PMaSynRM / 高凸极低永磁占比 | `scheme-06/` | README 索引已建，图纸未落地 |
| S07 | 可变磁化状态 / Memory Motor | `scheme-07/` | README 索引已建，图纸未落地 |
| S08 | 混合励磁 | `scheme-08/` | README 索引已建，图纸未落地 |
| S09 | 绕组重构 | `scheme-09/` | README 索引已建，图纸未落地 |
| S10 | 多相 / 相组控制 | `scheme-10/` | README 索引已建，图纸未落地 |
| S11 | 温度 / 退磁 / 安全保护 | `scheme-11/` | README 索引已建，图纸未落地 |
| S12 | 工况加权效率 / Pareto 选择 | `scheme-12/` | README 索引已建，图纸未落地 |

## 3. 当前结论

本目录目前证明的是：V2 已经有了每个方案图纸包的仓库落点和审计索引。

本目录目前尚未证明：任何方案已有正式 PCB、3D/CAD、控制器图、BOM/EDA、DVP&R、DFMEA 或制造发布文件。
