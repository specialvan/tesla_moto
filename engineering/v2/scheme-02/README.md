# S02 MTPA / FW / MTPV 连续控制图纸包

方案 ID：`mtpa_fw_mtpv_control`

## 必需交付物

| 分类 | 必需文件 | 当前状态 | 下一步 |
|---|---|---|---|
| PCB | `pcb/V2-S02-PCB-control_io_map-r00.md` | draft | 已落地 MCU/NVM、ADC、位置、通信和 LUT 版本诊断页面级草案 |
| 3D/CAD | `cad/V2-S02-CAD-controller_packaging-r00.step` | missing | 定义控制器壳体、接插件、线束和散热路径 |
| Controller | `controller/V2-S02-CTRL-mode_transition_lut-r00.drawio` | draft | 已落地 MTPA/FW/MTPV 模式切换、LUT CRC 和 fallback 状态机草图 |
| BOM/EDA | `bom_eda/V2-S02-EDA-controller_core_bom-r00.xlsx` | missing | 列出 MCU、NVM、采样链和标定接口器件 |
| Test/DVP | `test_dvpr/V2-S02-TEST-lut_mode_hil-r00.md` | missing | 定义 HIL 模式切换、CRC 和断电恢复测试 |
| Simulation | `simulation/V2-S02-SIM-lut_transition_trace-r00.md` | missing | 关联 MTPA/FW/MTPV LUT 连续性和不可行区仿真证据 |

## 现有证据

- `models/control_lut.json` 提供当前控制 LUT 数据。
- `sim/run_control_lut_generator.py` 提供 LUT 生成入口。

## 当前判断

控制数据链已启动，但控制器图纸包和硬件接口图尚未落地。
