# gpt-image-2 生图工程包

把 12 个可控磁通量方案的图档生图工作流，沉淀到一个独立可重跑的工程包。

- 端点：OpenAI 兼容代理（通过 `GPT_IMAGE_BASE_URL` 环境变量或本地未跟踪配置提供）
- 模型：`gpt-image-2`
- 默认尺寸：1024×1024
- 输出格式：PNG（b64_json 解码）
- 依赖：`requests`，仅一个第三方库
- 执行策略：**强制严格串行**，不并发，请求之间留 sleep 间隔，失败自动重试

## 0. 边界

1. 不得在 `config/model.json` 提交真实 endpoint 或 API key；本地运行请设置 `GPT_IMAGE_BASE_URL` / `GPT_IMAGE_API_KEY`，或使用已被 `.gitignore` 忽略的 `config/model.local.json`；已泄漏 key 必须到 vendor 后台 rotate / revoke。
2. 本工程包产出的 PNG 是 **概念示意图**，不替代 EDA / CAD / FEA / 工程验证。引用时必须保留对应方案 `engineering_validated=false` 的限制声明。
3. 未经脱敏和审批，不得把工程 prompt、方案参数、DVP/安全路径上传到外部 Web 工具或第三方端点。
4. 工程包默认 **串行执行**，每张图之间 sleep 配置可调，避免触发限速与代理崩溃。
5. 生成产物落在 `outputs/<scheme>/`；每张 PNG 同目录会留一份 `-prompt.txt` 保存最终 prompt 与响应元数据，便于复刻；提交前必须检查是否包含敏感工程信息。

## 1. 目录结构

```text
gpt-image-2/
├── README.md
├── requirements.txt
├── config/
│   ├── model.json             # 模型 / 默认参数 / 重试 / sleep；真实端点和 key 用环境变量
│   └── style.json             # 全局风格 token + 负向 prompt
├── prompts/
│   ├── templates.json         # 8 类模板（T01..T08）
│   └── schemes.json           # 12 方案 × 8 图 = 96 条 placeholder 与元数据
├── gpt_image2/                # Python 包
│   ├── __init__.py
│   ├── config.py              # 加载 json
│   ├── client.py              # HTTP 调用 + 错误处理 + 指数退避
│   ├── render.py              # 模板 + placeholder → 最终 prompt
│   └── generate.py            # CLI 入口（单张 / 批量 / 烟囱）
├── outputs/
│   └── .gitkeep
└── examples/
    └── smoke_test.ps1
```

## 2. 快速上手

### 2.1 安装依赖

```powershell
python -m pip install -r gpt-image-2\requirements.txt
```

### 2.2 端点烟囱测试

最低成本验证端点 / key / 模型联通。先设置环境变量，或复制 `config/model.local.example.json` 为已被 `.gitignore` 忽略的 `config/model.local.json` 并仅在本机填入真实值：

```powershell
python -m gpt_image2.generate --smoke
```

或：

```powershell
.\gpt-image-2\examples\smoke_test.ps1
```

成功后会在 `outputs/_smoke/` 落 `smoke-r00.png` 与 `smoke-r00-prompt.txt`，并打印响应耗时。

### 2.3 单张图

按 `prompts/schemes.json` 的图 ID 生图：

```powershell
python -m gpt_image2.generate --image-id IMG-S01-T03
```

### 2.4 按方案串行

```powershell
python -m gpt_image2.generate --scheme S01
```

会顺序跑 S01 的 8 张图（默认含全部优先级），每张之间 sleep（见 `config/model.json` 的 `sleep_between_calls_seconds`）。

按优先级筛：

```powershell
python -m gpt_image2.generate --scheme S01 --priority P0
```

### 2.5 全部方案 P0 串行

```powershell
python -m gpt_image2.generate --all --priority P0
```

12 方案 × P0 优先级 2 张 = 24 张，串行跑完约 5-15 分钟（视端点速度）。

### 2.6 只渲染 prompt，不烧 API

```powershell
python -m gpt_image2.generate --image-id IMG-S01-T03 --dry-run
```

会把最终展开后的 prompt 写到 `outputs/_dry_run/<image_id>.prompt.txt`；如需复制到 Web 端工具，必须先脱敏并确认该工具获准接收项目工程信息。

### 2.7 r03 production prompt pack 生图

按单个 r03 prompt pack 干跑：

```powershell
$env:PYTHONPATH = 'gpt-image-2'
python -m gpt_image2.generate --prompt-pack engineering/v2/scheme-01/prompts/V2-S01-PROMPT-r03-production_drawing_pack.md --dry-run --output-dir gpt-image-2/outputs/_dry_run/r03_s01
```

按全部 12 个 r03 prompt pack 干跑并输出报告：

```powershell
$env:PYTHONPATH = 'gpt-image-2'
python -m gpt_image2.generate --prompt-pack-all --dry-run --report-json gpt-image-2/outputs/_dry_run/r03_report.json
```

确认无误后串行烧 API：

```powershell
$env:PYTHONPATH = 'gpt-image-2'
python -m gpt_image2.generate --prompt-pack-all --force
```

默认输出到 `outputs/SXX/r03/`，每个 r03 pack 产出 4 张图。

### 2.8 参考图改图

使用单张参考图走 `/v1/images/edits`：

```powershell
$env:PYTHONPATH = 'gpt-image-2'
python -m gpt_image2.generate --prompt-pack engineering/v2/scheme-01/prompts/V2-S01-PROMPT-r03-production_drawing_pack.md --edit-reference gpt-image-2/outputs/S01/V2-S01-ILL-T03-state_machine-r00.png --force
```

批量改图可用 `--edit-reference-dir <目录>`，脚本会按输出名查找参考图；找不到参考图时该条会报错，不会静默退化为文本生图。改图仍是 concept/proxy 图档，不代表 EDA / CAD / FEA / ASIL 验证通过。

## 3. 断点续传

`generate.py` 默认 **跳过已存在的 PNG**。如果某张失败或想重生，先删 PNG 再跑：

```powershell
Remove-Item gpt-image-2\outputs\S01\V2-S01-ILL-T03-state_machine-r00.png
python -m gpt_image2.generate --image-id IMG-S01-T03
```

加 `--force` 可不删强生：

```powershell
python -m gpt_image2.generate --image-id IMG-S01-T03 --force
```

## 4. 工作流与归档

每张图生成后落两个文件：

```text
outputs/S01/V2-S01-ILL-T03-state_machine-r00.png
outputs/S01/V2-S01-ILL-T03-state_machine-r00-prompt.txt
```

满意后手动复制到 `engineering/v2/scheme-XX/illustrations/`，作为评审锚点；同时回到 `codex-review/docs/image_worklist_2026-05-18/README.md` §5 勾掉对应复选框。

## 5. 与评审包的关系

| 文档 | 角色 |
|---|---|
| `codex-review/docs/scheme_drawing_prompt_catalog_2026-05-18.md` | 人类可读图档目录、风格基线、改图指南 |
| `codex-review/docs/image_worklist_2026-05-18/` | 96 张图就绪矩阵、归档规则、进度勾选总表 |
| `gpt-image-2/prompts/templates.json` | 8 类模板（API 自动化用） |
| `gpt-image-2/prompts/schemes.json` | 12 方案 × 8 图 placeholder 与元数据（API 自动化用） |

修改 prompt 文案时，先改 image_worklist 的 markdown（评审权威源），再同步到 `prompts/*.json`。

## 6. 故障排查

| 现象 | 处置 |
|---|---|
| 401 Unauthorized | key 错或未启用 image 权限；用 `--smoke` 验证 |
| 403 Forbidden | endpoint 不允许该模型；改 `config/model.json` 的 `model` 试 fallback（如 `gpt-image-1`） |
| 404 Not Found | path 错；当前实现走 `/v1/images/generations` |
| 429 Too Many Requests | 自动指数退避；调 `sleep_between_calls_seconds` 增加间隔 |
| 5xx | 自动重试 `max_retries` 次后报错 |
| 返回无 b64 也无 url | 端点协议差异，看 `outputs/<scheme>/<id>-prompt.txt` 末尾 `[raw response]` |
| 中文 prompt 出现乱码 | 写文件指定 `encoding='utf-8'`；本工程已默认 UTF-8 |

## 7. 当前数据覆盖

| 数据 | 状态 |
|---|---|
| 8 类模板 | 完整 |
| 12 方案 × 8 图 = 96 条 placeholder | 完整 |
| 端点烟囱测试 | 已通过（2026-05-18，PNG 1.18 MB，duration_ms ≈ 53000） |
| `--all --priority P0` dry-run | 24/24 通过 |

跑批前可用：

```powershell
$env:PYTHONPATH = '.'; python -m gpt_image2.generate --all --priority P0 --dry-run --report-json outputs\_dry_run\report.json
```

确保所有方案的 P0 都能完整渲染再开始烧 API。
