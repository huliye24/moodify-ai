# MSIX Compatibility — MSIX_COMPATIBILITY

**Task:** `MOODIFY_DESKTOP_TRUST_CHAIN_001`
**Status:** `EXPERIMENTAL` — spike 计划就绪，**执行被环境阻断**（见 §5）。

> **MSIX 不得直接进入正式发布。** 本文的存在就是为了在建立 Store release 之前
> 先回答一个问题：MSIX 打包环境下，Moodify 的 PROCESS 能力是否还存在。
> 在本文给出 `FULL` 或 `PLAY_ONLY` 结论之前，Store 不作为发行渠道。

---

## 1. 为什么这个问题存在（技术背景，与我们的架构直接相关）

Moodify Desktop 的 PROCESS 依赖一条**外部进程链**：

```text
Electron 主进程
  └─ spawn(python, [script.py, args])          ← child_process
       └─ Python 解释器（外部 venv 内的 python.exe）
            ├─ import numpy / scipy / soundfile  （.venv-audio）
            ├─ import torch / demucs             （.venv-demucs）
            ├─ 读写 case 目录下的音频与 JSON
            ├─ 首次运行下载 Demucs 权重到 ~/.cache/torch
            └─ 创建并写入 studio/ 产物
```

而 MSIX 打包应用（即使声明 `runFullTrust`）会得到一套**虚拟化的文件系统视图**：
写入 `AppData` 等位置被重定向到 per-package 位置。这与上面的链路有三处潜在冲突：

1. **外部进程的路径解析**：如果传给子进程的路径来自 `__dirname`/`process.resourcesPath`，
   而该路径是 MSIX 虚拟化后的形态，外部进程可能无法解析它。
2. **在用户目录里创建并执行新的可执行文件**（Python venv 里的 `python.exe`）：
   这是 MSIX 沙箱与 Store 政策都要审视的动作。
3. **模型权重下载与缓存**：`~/.cache/torch` 在虚拟化下会落到 per-package 位置，
   行为与普通安装不同（可能重复下载、可能空间受限）。

### 1.1 已发现的公开证据（说明这不是臆测）

本次调研（web 搜索，未能取回原文——见 §5.1）找到两条直接相关的公开记录：

| 来源 | 相关性 |
|---|---|
| [DXT `${__dirname}` resolves to MSIX-virtualized path, breaking external process spawns (anthropics/claude-code #47977)](https://github.com/anthropics/claude-code/issues/47977) | **与我们的第 1 条冲突完全同型**：一个 Electron 应用在 MSIX 下因 `__dirname` 被虚拟化而**无法 spawn 外部进程**。这说明该失败模式在现实中会发生，不是理论担忧 |
| [CPython: Add link to Microsoft docs for limitations in Windows Store package (GH-24422)](https://mail.python.org/pipermail/python-checkins/2021-February/169035.html) | CPython 自己在文档里链接了「Windows Store 打包的限制」。说明 Python 在打包环境下有**已知限制**，需要逐条核对 |
| [electron-builder MSIX target](https://www.electron.build/docs/msix/) | MSIX 打包在 electron-builder 中有**当前支持**的目标（不再是旧的 `appx`）。第 2 步据此实施 |

> 这些是**旁证**，不是我们对 Moodify 的实测结论。它们的作用是确定测试重点，
> 以及在无法实测时给出一个有依据的先验。**不得**据此直接写下 `PLAY_ONLY`。

---

## 2. 测试计划（12 项，逐项可判定）

必须在 MSIX 打包并**安装后**的 Moodify 中执行。每一项都要留下可复现的证据
（命令、输出、截图或日志），不接受「看起来能跑」。

| # | 测试项 | 判定方式 | 通过标准 |
|---|---|---|---|
| 1 | 创建 `.venv-audio` | 应用内触发快速分离 | venv 目录出现且 `Scripts/python.exe` 存在 |
| 2 | 创建 `.venv-demucs` | 应用内触发模型分离安装 | 同上 |
| 3 | Python runtime 启动 | 运行 `python -c "import sys; print(sys.executable)"` | 退出码 0，路径指向已创建的 venv |
| 4 | pip / 依赖安装 | 安装 `requirements-audio.txt` | 全部 wheel 安装成功，无沙箱拒绝 |
| 5 | Demucs 启动 | `python model_separate.py <wav> --outdir <dir>` | 权重加载成功、四轨写出 |
| 6 | FFmpeg / 外部二进制 | 调用 ffmpeg（Core 报告链路依赖） | 退出码 0 |
| 7 | `child_process` / subprocess | Electron 主进程 spawn 上述任一 | 无 `ENOENT` / 权限错误 |
| 8 | 模型下载 | 首次运行的权重下载 | 下载完成且落盘 |
| 9 | 模型缓存 | 第二次运行 | 命中缓存，**不**重复下载 |
| 10 | 音频 I/O 文件系统 | 读取用户选择的音频 + 写产物 | 读写均成功，路径对用户可见/可访问 |
| 11 | 用户选择本地文件 | 文件对话框选歌 | 返回的路径可被子进程打开 |
| 12 | **PROCESS 端到端** | 一次完整链路（见 §3） | 产出可播放的成品音频 |

**注意第 12 项是唯一有决定意义的。** 前 11 项全过但第 12 项失败 → `PLAY_ONLY`。
第 12 项通过 → `FULL`。

---

## 3. 端到端判定（第 12 项的具体执行）

不能只检查「App 能启动」。必须真的跑完：

```text
输入一段音频
   ↓
① 检测（Core: moodify demo，需要 Python）
   ↓
③ 逆向分解（scripts/dsp_separate.py 或 model_separate.py，需要 Python + numpy/scipy 或 torch）
   ↓
可逆性验证（scripts/roundtrip.py）
   ↓
④ 结构（basic-pitch → MIDI，需要外部运行时）
   ↓
⑥ 复检（再次调用 Core 检测）
   ↓
⑦ 选定 → 导出成品音频
   ↓
验证产物可被播放器打开
```

**最小可接受证据：** 一次成功的导出音频文件 + 该 case 目录的产物清单 + 每一步的子进程退出码。

---

## 4. 两种结论与各自的后果

### Result A — `FULL`（PROCESS 在 MSIX 中可用）

```text
MSIX = PLAY + PROCESS
```

→ 可以开始设计 Microsoft Store 分发，并输出正式的 Store packaging proposal
（electron-builder MSIX 目标、Store 提交清单、隐私政策、能力声明）。

### Result B — `PLAY_ONLY`（PROCESS 不可用或需不可接受的妥协）

**不要 hack。不要为了 Store 改坏 Desktop 架构。**

```text
GitHub Desktop Edition（第一官方渠道）
  PLAY + PROCESS   ← 完整 Studio

Microsoft Store Edition（第二渠道）
  PLAY             ← Listener / Player
```

若采用此结论，以下**必须**做到：

1. **UI 明确说明能力区别** —— Store 版首次进入 PROCESS 相关入口时说明
   「此版本为播放版；完整制作能力见 GitHub 发行版」并给出链接。
2. **README 明确说明**。
3. **Store Description 明确说明**。
4. **禁止**两个版本同名却能力不同而不解释。

四个阶段的十二项测试中任何一项失败，都要记录**具体失败形态**——是
`ENOENT`、权限拒绝、还是路径不可解析。这决定了未来是否值得重新评估。

---

## 5. 当前状态：执行被环境阻断（不是实现缺口）

```text
MSIX_COMPATIBILITY_SPIKE: NOT EXECUTED
  BLOCKED_BY_EXTERNAL_CONFIGURATION
  原因：需要一台可安装 MSIX 包并能创建 Python venv 的 Windows 机器；
        且需要有意义的 Store 打包输出来验证。
```

### 5.1 本次未能取回的资料（如实记录）

- 本执行环境的 web fetch 无法解析外部主机（`learn.microsoft.com`、
  `electron.build`、`github.com` 均返回非公网地址），因此**只能读到搜索摘要**，
  无法阅读 MSIX 沙箱与 Packaged Desktop App 的原文。
- electron-builder 当前 MSIX 目标的确切配置语法**未核实**（只知道存在该目标）。
- 「MSIX 下 `runFullTrust` 是否允许在用户目录创建并执行新的 `python.exe`」
  这一关键问题**没有权威结论**——两条公开证据都指向「有风险」，但不构成定论。

**因此本文不给出 `FULL` / `PLAY_ONLY` 结论。** 给出结论需要真的跑一次 §2 的十二项。

### 5.2 必须保留的强约束

```text
Microsoft Store 是分发渠道，不是 Moodify 的架构所有者。
```

如果 MSIX 与 PROCESS 天然冲突，优先级是：

```text
保持 GitHub Desktop 的完整能力   >   适配 Store
```

**不得**为了让 MSIX 能跑而重写 Python 架构、移除外部运行时依赖、
或者把 PROCESS 做成只在 Store 版里缺失却不说明。

---

## 6. 与发布信任链的关系

MSIX **不在** `desktop-release.yml` / `desktop-sign.yml` 这条链里。
两条渠道各自独立的签名来源：

```text
GitHub Desktop    EXE   → SignPath Foundation   → GitHub Attestation → SHA256
Microsoft Store   MSIX  → Microsoft 代签        → Store 自身的完整性校验
```

在 §2 的十二项测试得出 `FULL` 之前，Store 渠道不启动。
本任务**不**创建任何 Store 提交物（不生成 `.msixupload`、不注册 Partner Center）。
