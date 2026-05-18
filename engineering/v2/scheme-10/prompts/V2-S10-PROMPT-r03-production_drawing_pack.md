# V2-S10 r03 生产参数化生图提示词包

目标：把 S10 从“多相可用电流代理”升级为可审查的六相逆变器、相组封装、容错转矩分配和证据追溯工程图。

## 通用负面约束

- 不要画营销海报、概念电机或抽象电流光效。
- 不要生成虚构品牌、真实供应商 Logo 或不可读小字。
- 不要把三相逆变器重复画成多相系统。
- 所有图必须保留英文工程标签、phase isolation、xy harmonic observer、thermal balance 和 S11 safety request 标识。

## 图 1：Six-phase inverter PCB

Prompt: Generate a white-background engineering schematic titled “S10 Six-Phase Multiphase Inverter PCB”. Include six isolated gate drivers, six phase current sensors, phase voltage sensing, DC-link sensing, dual three-phase connectors, per-phase gate-disable latch, phase-group fault isolation, fuse or solid-state cutoff, PWM sampling windows, alpha-beta and xy harmonic observer signals, shield ground, and S11 safety request. Mark 6 phases, 130A per phase, fault derate below 2ms, 50% derate mode.

## 图 2：Phase-group inverter CAD package

Prompt: Generate an isometric CAD cutaway titled “S10 Six-Phase Phase-Group Inverter Package”. Show A1/B1/C1/A2/B2/C2 terminals, dual three-phase or six-phase busbar, six phase current sensors, power modules, cooling plate, thermal zones, shielded harness, service labels, phase-order keying, and fault-isolated phase-group boundaries. White background, realistic engineering CAD technical style.

## 图 3：Fault-tolerant torque allocator

Prompt: Generate a controller state-machine and block diagram titled “S10 Six-Phase Fault-Tolerant Torque Allocator”. Include Clarke transform for alpha-beta and xy subspaces, six-phase current feedback, fault phase detector, per-phase isolation, remaining-phase current allocator, torque derate, xy harmonic limiter, thermal balancer, NVH guard, service reset, and S11 safety request. Use red safety paths and blue torque-control paths.

## 图 4：Evidence traceability

Prompt: Generate a traceability flow diagram titled “S10 Evidence Chain: Multiphase Proxy to Fault-Tolerant Gate”. Flow: EXP-009 proxy -> six-phase machine model -> fault isolation model -> xy harmonic/NVH model -> thermal balance model -> DVP single-phase and phase-group fault -> gate review. Include warning callout “available-current proxy is not fault-tolerant validation”.
