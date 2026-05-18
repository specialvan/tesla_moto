# V2-S03 控制器过调制状态机草案 r00

方案：S03 SVPWM / 过调制  
状态：`draft`，用于控制评审和生图输入，不替代 Simulink/量产代码。

## 1. 状态机

| 状态 | 进入条件 | 退出条件 | 输出限制 |
|---|---|---|---|
| Linear SVPWM | `k_mod <= 1.00` 且电压裕度充足 | 电压裕度低于阈值 | 常规电流采样窗口 |
| Overmodulation-1 | `1.00 < k_mod <= 1.10` 且 THD/NVH 许可 | THD、温升或电压裕度触发 | 限制 `di/dt` 和采样重建 |
| Overmodulation-2 | `1.10 < k_mod <= 1.15` 且高速转矩请求有效 | 任一 EMC/NVH/热保护触发 | 限制持续时间和转矩斜率 |
| Six-step guarded | 短时高速逃逸或诊断工况 | 当前环失锁、故障或超时 | 仅允许受控降额，不作为默认量产模式 |
| Fallback linear | 采样异常、fault latch、S11 safety request | 故障清除并重新校验 | 退回线性 SVPWM 或降扭 |

## 2. 输入信号

- `speed_rpm`
- `torque_request_nm`
- `vdc_v`
- `voltage_margin_v`
- `phase_current_valid`
- `thd_estimate_pct`
- `inverter_temp_c`
- `emc_guard_active`
- `safety_gate_disable_request`

## 3. 标定参数

| 标定名 | 初值 | 单位 | 说明 |
|---|---:|---|---|
| `KMOD_OVERMOD_1_ENTRY` | 1.00 | ratio | 进入浅过调制 |
| `KMOD_OVERMOD_2_ENTRY` | 1.10 | ratio | 进入深过调制 |
| `KMOD_MAX_ALLOWED` | 1.15 | ratio | 绝对上限 |
| `OVERMOD_MAX_DWELL_MS` | 500 | ms | 深过调制持续时间上限 |
| `THD_WARN_PCT` | 8 | % | 进入 NVH/EMC 复核 |
| `INV_TEMP_DERATE_C` | 115 | °C | 逆变器降额入口 |

## 4. 验收闭环

- EXP-005 只能证明电压利用率代理收益，不能替代 THD、EMC、NVH 和逆变器损耗验证。
- 状态切换必须输出 `from_mode/to_mode/k_mod/id/iq/torque_jump` 日志。
- 任一 fault latch 或 S11 安全请求必须优先于过调制收益。

## 5. 下版生图提示词

生成控制器状态机工程图，主题为“S03 SVPWM overmodulation guarded state machine”。节点包括 Linear SVPWM、Overmodulation-1、Overmodulation-2、Six-step guarded、Fallback linear、Fault shutdown。边上标注 k_mod、voltage margin、THD/NVH/EMC guard、inverter temperature、sampling valid、gate-disable request。画面使用白底、蓝灰色状态框、红色安全回退边、英文标签、可读箭头。