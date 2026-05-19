# V2-S02 r03 生产参数化生图提示词包

目标：把 S02 MTPA / FW / MTPV 连续控制从 r02 参数样板升级为可审查的 LUT 发布链、NVM/CRC、模式切换连续性和证据追溯工程图。

## 通用负面约束

- 不要画营销海报、抽象控制曲线或概念车。
- 不要把 60 A r02 proxy soft gate 画成 r03 生产验收通过。
- 不要隐藏 Rs/Ld/Lq/psi_f 仍为 estimate 的事实。
- 所有图必须保留英文工程标签、r02 proxy / r03 target / evidence gap 标识。
- 明确标注 `engineering_validated = false`。

## 图 1：MTPA/FW/MTPV controller IO PCB

Prompt: Generate a white-background engineering schematic titled “S02 MTPA-FW-MTPV Controller IO and LUT Interface”. Include MCU FOC core, NVM A/B banks, LUT CRC checker, ADC current channels, Vdc sensing, resolver/encoder interface, CAN-FD, SPI to NVM, Ethernet XCP calibration, gate-driver interface, gate-disable request, and S11 demag safety input. Mark ADC 12-bit 100 kSPS, CAN-FD 5 Mbit/s, SPI 50 MHz, Ethernet XCP 100 Mbit/s, and CRC-32 IEEE 802.3. Use blue control/data paths, red safety fallback paths, and amber estimate callouts for Rs/Ld/Lq/psi_f.

## 图 2：Controller packaging and NVM thermal CAD

Prompt: Generate an isometric CAD cutaway titled “S02 LUT Controller Packaging and Thermal Boundary”. Show controller housing, MCU/NVM PCB, gate-driver PCB interface, HV/LV connector separation, calibration connector, thermal pad to housing, EMI partition, harness outlet, and service access boundary. Include callouts for NVM dual-bank update, LUT version label, CRC check on power-up, and no manufacturing release. White background, CAD technical drawing style.

## 图 3：MTPA-FW-MTPV guarded mode transition

Prompt: Generate a state-machine diagram titled “S02 Guarded MTPA-FW-MTPV Mode Transition”. Nodes: IDLE, MTPA, Field Weakening, MTPV, Infeasible Derate, Fault Fallback. Transitions labeled by voltage margin, torque axis [50,100,150,200] Nm, demagnetization_risk, current_exceeded, voltage_exceeded, LUT CRC fail, and mode reset. Add explicit callout: “r02 id/iq jump soft gate <= 60 A; r03 target <= 30 A”. Use red fallback arrows and blue normal-control arrows.

## 图 4：Evidence traceability

Prompt: Generate a traceability flow diagram titled “S02 Evidence Chain: r02 LUT Proxy to r03 Control Gate”. Flow: motor_params estimate -> control_lut generator -> torque axis expansion -> mode transition jump check -> feasibility map -> NVM CRC/version DVP -> HIL mode transition plan -> FEA/bench replacement of Rs/Ld/Lq/psi_f. Include warning callout “60 A is r02 proxy gate, not production acceptance”.
