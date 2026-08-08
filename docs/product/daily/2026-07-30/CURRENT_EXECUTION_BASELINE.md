# Moodify 当前执行基线｜D1-01

**记录日期：2026-07-30**  
**任务：D1-01｜确认主线入口、环境、测试命令和输出目录**  
**门禁结果：G1 PASS**

## 1. 仓库与版本事实

| 项目 | 当前事实 | 证据命令 |
|---|---|---|
| 仓库根目录 | `E:\moodify` | `git rev-parse --show-toplevel` |
| 当前分支 | `codex/mainline-cloud-dev-20260603` | `git branch --show-current` |
| 当前HEAD | `b4bb5ef1d511169f315e10d18f4d6a27827d67e9` | `git rev-parse HEAD` |
| 最近发布标签 | `v2.0.0-mvp` | `git describe --tags --always --dirty` |
| 工作区状态 | `v2.0.0-mvp-dirty`，存在未提交和未跟踪文件 | `git status --short` |

解释：`v2.0.0-mvp`是已封存的发布基线；当前目录是在该基线上继续工作的脏工作区。后续运行证据必须同时记录HEAD和dirty状态，不能将当前未提交代码自动视为发布版本。

## 2. 本机运行环境

| 项目 | 当前事实 | 验证状态 |
|---|---|---|
| 默认Python | `C:\Program Files\Python311\python.exe` | 已读取 |
| Python版本 | `3.11.9` | 满足项目`>=3.10`要求 |
| 其他可见Python | `D:\Anaconda\python.exe`、WindowsApps占位入口 | 不作为本轮默认环境 |
| Core包版本 | `2.0.0` | 来自`moodify-core-package/pyproject.toml` |
| Core CLI | `moodify`可调用 | `moodify --help`成功返回 |

已知环境问题：Core CLI中文帮助在当前PowerShell终端出现编码乱码。CLI本身返回成功，但该现象尚未归因，不能宣称终端显示完全正常。

## 3. 三个主要执行入口

### 3.1 Moodify Core

代码入口：

```text
moodify-core-package/src/moodify/cli.py
moodify-core-package/src/moodify/v01_pipeline.py
moodify-core-package/src/moodify/api/main.py
```

命令入口由`pyproject.toml`声明：

```text
moodify = moodify.cli:main
```

当前CLI包含`analyze`、`process`、`batch`、`presets`、`serve`及历史兼容命令。它是声音分析与处理能力的直接入口。

### 3.2 Moodify Runtime

代码入口：

```text
moodify_runtime/cli.py
moodify_runtime/operator_api.py
moodify_runtime/config.py
```

推荐模块调用形式：

```powershell
python -m moodify_runtime.cli <command>
```

Runtime负责注册、计划、队列、执行、报告、Operator Job、Delivery、Craft、Scheduler、Calibration和Data Loop。命令定义已从`moodify_runtime/cli.py`确认，但D1-01不把“命令已定义”写成“全部命令已在本机运行验证”。

### 3.3 Workspace v2

API聚合入口：

```text
moodify-core-package/src/moodify/api/main.py
```

Workspace路由：

```text
moodify-core-package/src/moodify/api/routes/workspace_projects.py
```

Workspace持久化根默认由环境变量指定：

```powershell
$env:MOODIFY_WORKSPACE_ROOT = "data/workspace_v2"
```

服务启动命令来自`docs/product/MOODIFY_V2_RUNBOOK.md`：

```powershell
python -m uvicorn moodify.api.main:app --host 0.0.0.0 --port 8000
```

运行条件：工作目录应为`E:\moodify\moodify-core-package`，或等效地确保`moodify`包和仓库根`moodify_runtime`均在Python导入路径中。

## 4. 内部Operator API入口

服务入口：

```powershell
python -m uvicorn moodify_runtime.operator_api:app --host 0.0.0.0 --port 8700
```

工作目录：

```text
E:\moodify
```

来源：`moodify_runtime/operator_api.py`模块说明和`docs/STUDIO_OS_ALPHA_RUNBOOK.md`。该控制台只用于内部运维、验证和异常处理，不是创作者前端。

## 5. 测试命令基线

### 5.1 Core完整测试

```powershell
Set-Location E:\moodify
python -m pytest moodify-core-package/tests -q
```

### 5.2 Runtime完整测试

```powershell
Set-Location E:\moodify
python -m pytest moodify_runtime/tests -q
```

### 5.3 Workspace v2关键测试

Workspace测试位于Core测试集合中。D1-04执行前将根据测试文件名冻结最小子集，不在D1-01提前声称当前仍为179/179通过。

### 5.4 Core CLI最小检查

```powershell
Set-Location E:\moodify
moodify --help
moodify presets
```

本节命令是执行基线；具体通过数和返回码必须由D1-04当前运行产生。

## 6. 存储与输出边界

### 6.1 Workspace v2项目数据

默认根目录：

```text
E:\moodify\data\workspace_v2
```

项目内包含`sources`、`diagnostics`、`processing`、`threads`、`plans`、`versions`和`archive`。这些内容属于项目历史和版本证据，只允许追加或通过正式接口更新，不得手工覆盖历史版本。

### 6.2 Runtime数据

默认配置来自`moodify_runtime/config.py`：

```text
E:\moodify\data\moodify_runtime
E:\moodify\data\night_inputs
E:\moodify\data\moodify_runtime\input_registry.jsonl
E:\moodify\data\moodify_runtime\run_queue.jsonl
E:\moodify\data\moodify_runtime\operator_jobs.jsonl
E:\moodify\data\moodify_runtime\operator_job_details
E:\moodify\data\moodify_runtime\operator_deliveries.jsonl
```

### 6.3 运行输出与报告

```text
E:\moodify\outputs\daily_runs
E:\moodify\reports\daily_runs
E:\moodify\reports\operator_runs
E:\moodify\outputs
```

任务必须使用独立运行目录，不得把新证据混入旧运行目录。

### 6.4 当前规划资产

```text
E:\moodify\docs\product\daily\2026-07-30
E:\moodify\outputs\weekly-plan-20260730
```

## 7. 禁止覆盖或清理的资产

在完成D1-02资产分类前，以下目录全部按“用户或历史资产”处理：

```text
E:\moodify\pre-music
E:\moodify\music
E:\moodify\local_audio_assets
E:\moodify\uploads
E:\moodify\treatment_records
E:\moodify\listening_test
E:\moodify\inspector_reports
E:\moodify\calibration_reports
E:\moodify\data
E:\moodify\cloud_data
E:\moodify\output
E:\moodify\outputs
E:\moodify\reports
```

不得递归删除、批量移动、重命名或覆盖其中内容。本轮新产物必须进入日期或运行ID隔离的子目录。

## 8. G1验收

| 检查项 | 结果 | 证据 |
|---|---|---|
| 仓库路径、分支、HEAD可追踪 | PASS | 第1节 |
| 当前发布基线与历史关系明确 | PASS | 第1节 |
| Core、Runtime、Workspace入口齐全 | PASS | 第3节 |
| 测试命令可复制且工作目录明确 | PASS | 第5节 |
| 服务/API启动命令有来源 | PASS | 第3、4节 |
| 输入、输出、证据和临时边界清楚 | PASS | 第6节 |
| 不得覆盖或删除的资产明确 | PASS | 第7节 |
| 文档能力与本机验证状态分离 | PASS | 全文状态措辞 |

**G1结论：PASS。D1-01完成，可以进入D1-02。**

