# S04 PCB LUT observer inputs page draft

方案：`nonlinear_flux_lut`  
状态：`draft`  
范围：页面级 PCB 观测输入草案；不是 EDA 原理图、Layout、Gerber、ODB++ 或制造发布文件。

## 1. 页级目标

S04 的 PCB 页级目标是定义非线性磁链 LUT 插值和 Fallback 所需观测输入，保证 `id/iq/temperature/position/Vdc` 的精度、时序和诊断路径能被评审。

## 2. LUT 输入信号预算

| 输入 | 来源 | 用途 | 草案要求 | 当前缺口 |
|---|---|---|---|---|
| `id/iq` | 相电流 + dq 变换 | LUT 插值坐标 | 电流采样误差需进入 LUT 误差预算 | 传感器精度未选 |
| `theta_e` | resolver/encoder | dq 坐标变换 | 角度延迟需可估算 | 位置接口未定 |
| `temperature_c` | motor/inverter sensor | 温度修正和 LUT 切片选择 | 开短路诊断必需 | 传感器安装点未定 |
| `vdc` | DC bus sense | 电压可行性判断 | 分压误差进入 voltage margin | 分压/隔离未定 |

## 3. 边界与 fallback 信号

| 信号 | 目的 | 草案动作 |
|---|---|---|
| `lut_bounds_valid` | 防止外推误用 | 越界时拒绝或 clamp |
| `observer_plausible` | 防止传感器漂移误导 LUT | 进入 linear dq fallback |
| `residual_high` | FEA/台架残差监控 | 降额并记录事件 |
| `fallback_active` | 诊断和台架复现 | 输出到日志/诊断帧 |

## 4. 评审风险

| 风险 | 影响 | 下一步 |
|---|---|---|
| 采样误差未进入 LUT 预算 | 非线性 LUT 可能产生错误转矩预测 | 建立误差预算表 |
| 位置延迟未建模 | 高速区 dq 坐标偏移 | 与控制 loop spec 联审 |
| 温度点与 FEA 不一致 | LUT 切片选择失效 | 绑定 FEA 几何和传感器位置 |

## 5. 禁止误读

本文件只证明 S04 LUT 观测输入已有页面级 PCB 草案；不证明真实 FEA 几何、采样链 BOM、传感器安装 CAD 或台架相关性已完成。
