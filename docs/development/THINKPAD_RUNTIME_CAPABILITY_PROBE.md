# ThinkPad 003 — Runtime Capability Probe 0.1 证据

**Task:** MOODIFY THINKPAD HEAVY LANE 003
**Branch:** `feat/thinkpad-runtime-probe-003`
**Date:** 2026-10-09
**Machine:** ThinkPad（`D:\moodify-ai`，Windows 11，Python 3.10.10；基线见 `THINKPAD_NODE_BASELINE.md`）
**方法注记:** 本文所有数字均为本机实测（命令随附）；未测量的项如实标注。探针不执行生产能力、不安装、不下载模型。

---

## 1. 层边界（本任务的核心约束）

```text
DECLARATION  provider 声明需要什么        moodify.capabilities.models   （未改动）
ROUTING      哪个声明 provider 合规可用    moodify.capabilities.router   （未改动）
PROBING      这台机器现在能否真的跑它      moodify.runtime               （本次新增）
EXECUTION    真的运行                      （不存在）
```

三者是三个函数、三个包：`runtime → capabilities` 单向依赖（有测试钉住：`moodify.capabilities`
导入后 `moodify.runtime` 不在 `sys.modules`；capabilities 源码不含 `moodify.runtime`）。
探针**调用** router 做 eligibility join，从不修改它。

## 2. Provider / runtime 实测矩阵（2026-10-09，`runtime_report()` 默认策略）

命令：

```bash
cd moodify-core-package
PYTHONUTF8=1 .venv/Scripts/python.exe -c "from moodify.runtime import runtime_report; import json; print(json.dumps(runtime_report().model_dump(mode='json'), indent=1, ensure_ascii=False))"
```

| provider | runtime_kind | probe_status | 关键证据（requirement → 实测） |
|---|---|---|---|
| `moodify.auditory` | python_in_process | **AVAILABLE** | numpy 2.2.6 · scipy 1.15.3 · librosa 0.11.0 · soundfile 0.13.1（全部 import ✓） |
| `moodify.intervention` | python_in_process | **AVAILABLE** | numpy 2.2.6 ✓ |
| `moodify.mix_graph` | python_in_process | **AVAILABLE** | pedalboard 0.9.23 · numpy · scipy ✓（声明 EXPERIMENTAL → 默认策略不 eligible） |
| `moodify.release` | python_in_process | **AVAILABLE** | soundfile 0.13.1 ✓ |
| `moodify.preview_separation` | external_venv | **AVAILABLE** | `.venv-basic-pitch` interpreter 3.10.10 ✓ · librosa ✓ · soundfile 0.14.0 ✓（声明漂移见 §8） |
| `ffmpeg.system` | system_binary | **AVAILABLE** | ffmpeg + ffprobe 经运行时自身的解析器解析（winget 路径）；`-version` ✓ |
| `lalal.cloud` | remote_service | **UNKNOWN（设计内）** | network / API key 由 `UnsupportedCheck` 拒绝探测 —— 见 §7 |
| `basic_pitch.local` | external_venv | **AVAILABLE** | `.venv-basic-pitch` interpreter 3.10.10 ✓ · basic-pitch 0.4.0 == 声明 pin ✓ |
| `music21.local` | external_venv | **AVAILABLE** | `.venv-score` interpreter 3.10.10 ✓ · music21 9.9.2 ✓（声明漂移见 §8） |

汇总（实测输出）：

```json
{"probe_status_counts": {"AVAILABLE": 8, "UNAVAILABLE": 0, "DEGRADED": 0, "UNKNOWN": 1},
 "runnable_now": ["ffmpeg.system", "moodify.auditory", "moodify.intervention", "moodify.release"],
 "eligible_not_available": [],
 "installed_not_eligible": ["basic_pitch.local", "moodify.mix_graph", "moodify.preview_separation", "music21.local"]}
```

四种合法状态都在实机出现：eligible+available（`runnable_now`）、eligible+unavailable（空集——
本次机器没有这种情况）、ineligible+installed（四个非 ACTIVE 声明）、unknown-by-design（lalal.cloud）。

## 3. Probe 命令（可复现）

```bash
# 1) 既有诊断接口（本任务未新建命令；doctor 的 JSON 增加 runtime_probe 块）
cd moodify-core-package && PYTHONUTF8=1 .venv/Scripts/python.exe -m moodify.release_cli  # 或安装后的 moodify doctor

# 2) Core API
PYTHONUTF8=1 .venv/Scripts/python.exe -c "
from moodify.runtime import probe_providers, runtime_report
probe_providers()          # 纯运行时事实（无策略）
runtime_report()           # + router eligibility join"
```

## 4. 探针耗时（2026-10-09 实测，条件写清）

| 条件 | 数值 |
|---|---|
| 全量首测（文件缓存冷：`import basic_pitch` 2.29 s + `import music21` 5.42 s + ffmpeg） | ≈ **7.7 s** |
| 同机连跑 5 次（热）duration_s | 2.057 / 2.002 / 1.983 / 2.003 / 1.899 → **均值 1.99 s** |
| `moodify doctor` 冷进程墙钟 | 4.17 s（其中 probe 2.0 s） |
| per-provider（热） | basic_pitch 0.469 · music21 0.847 · ffmpeg 0.181 · preview_separation 0.375 · 其余 ≤0.011 |

主要成本是**两个外部 venv 的 import 子进程**（每个 venv 一个子进程，非每包一个）。

**缓存决策（§6E）：0.1 不建缓存。** 依据：热态 ≈2 s、冷态上限 ≈8 s——一次显式诊断的
可接受成本；而缓存会把「现在能不能跑」变成「上一次能不能跑」，正是任务禁止的
"turn unavailable into available without evidence" 风险面，且需要身份键（venv 解释器 +
site-packages mtime）与 `--refresh` 的额外复杂度。测试
`test_two_probe_runs_are_two_runs_no_hidden_cache` 反向钉死：两次调用每个 adapter 都真实重跑，
`checked_at` 各自如实。

## 5. 失败样例（真实输出）

**(a) 真实失败：把 `music21.local` 按桌面实际解析的 venv 探测**（`MOODIFY_VENV_SCORE=.venv-basic-pitch`）：

```text
status: UNAVAILABLE
  SATISFIED  python>=3.10               venv interpreter runs python 3.10.10
  MISSING    music21                    import music21 failed: ModuleNotFoundError: No module named 'music21'
  SATISFIED  external venv .venv-score  interpreter ran at D:\moodify-ai\.venv-basic-pitch
```

对照：按**声明**的 `.venv-score` 探测 = AVAILABLE。这两个输出合起来就是 §8 漂移的实测证明。

**(b) 缺失可执行**（测试 `test_missing_executable_is_unavailable_and_names_the_fix`，monkeypatch 解析器）：
两条 requirement → `MISSING`，provider → `UNAVAILABLE`，remedy 含 "install ffmpeg"。

**(c) 版本 pin 不符**（测试 `test_version_mismatch_degrades_rather_than_denies`）：
`numpy==0.0.1` 对已装 2.2.6 → `MISMATCH` → provider `DEGRADED`（存在但不是声明钉的版本——
"缺失"与"版本不符"是两件事）。

**(d) 坏版本输出**（测试）：可执行文件跑通但 `-version` 无输出 → requirement `SATISFIED` +
warning "no parseable output"（二进制确实能跑；版本字符串拿不到如实说）。

**(e) 超时**（测试）：`TimeoutExpired` → requirement `UNKNOWN` → provider `UNKNOWN`
（时间到不等于缺失——见 §6）。

## 6. 超时与进程卫生（每个子进程，全部显式）

| 项 | 值 |
|---|---|
| 可执行版本探针超时 | 15 s |
| venv import 探针超时 | 60 s（music21 冷启动 5.4 s 的 10 倍余量） |
| 终止 | `subprocess.run(timeout=…)` 在超时处杀死子进程后才抛 `TimeoutExpired`（无残留孤儿） |
| stdin | `DEVNULL`（子进程不可能等待输入） |
| 输出 | stdout/stderr 全部捕获；总量截断 2000 字符，版本行 120 字符 |
| 参数 | 仅参数数组，绝无 shell 字符串（测试断言 `isinstance(args, list)`、无 `shell=True`） |
| 环境 | python 子进程强制 `PYTHONUTF8=1` + `PYTHONIOENCODING=utf-8`（GBK 陷阱，`THINKPAD_RUNTIME_ARCHITECTURE.md` §3）；有测试钉住 |
| 网络/模型 | 探针子进程是固定 import-only 脚本，源码不含 socket/urllib/http/requests；in-process 部分在 socket 被封死的测试下照常完成。无下载、无推理 |

## 7. 探针**不**证明什么（与 §7 要求逐条对应）

```text
basic_pitch import 成功        ≠  转写质量好
ffmpeg -version 成功           ≠  该机器能完成一次渲染
music21 import 成功            ≠  MusicXML 解析语义正确
probe AVAILABLE                ≠  policy eligible（两层，有测试）
checked_at 是「探测那一刻」     ≠  「此后一直如此」（每次探测都是新事实，无缓存）
```

- **网络与凭据从不探测**：`lalal.cloud` 的两条 requirement 是 `UnsupportedCheck` →
  `UNKNOWN`（设计内），不是 `UNAVAILABLE`——"没测"不是"测出不行"。
- **声明与实现漂移时，探针验证的是声明**；漂移本身是发现（§8），不是探针的错误。
- 探针不执行生产能力、不安装依赖、不下载模型、不改 provider 排序、不碰 Canon。

## 8. 声明 vs 实现漂移（探针层的第一批真实发现）

| # | 声明（`builtin.py`） | 实现（桌面当前代码） | 本机实测 | 记录 |
|---|---|---|---|---|
| 1 | `moodify.preview_separation` → `external venv .venv-basic-pitch` + `librosa` | `dsp_separate.py` 跑在 `resolveRuntime('audio')` = `.venv-audio`（`main.js:1187`；脚本只 import numpy/soundfile/scipy） | `.venv-audio` **不存在**；探针按声明（`.venv-basic-pitch`）全 SATISFIED | CLR-003 |
| 2 | `music21.local` → `external venv .venv-score` | `score:run` 用 `resolveRuntime('score')` = `.venv-basic-pitch`（runtime.js 别名；requirements-transcribe.txt 含 music21） | `.venv-score` 有 music21 9.9.2；`.venv-basic-pitch` **没有** → 桌面曲谱路径在本机不可用（§5a 实测） | CLR-004 |

两条都**不**在重活线修复（声明归 Core、布局归桌面，对齐是 mainline 决定）；
`docs/development/CROSS_LANE_REQUESTS.md` 有完整上下文。

## 9. 测试与验收

```text
tests/test_runtime_probe.py — 27 tests
  A 可执行：真实 ffmpeg/ffprobe（机器验证）· 缺失 · 超时 · 坏版本输出
  B import：可用 · 缺失 · pin 不符(DEGRADED) · pin 相符 · 版本比较为数值比较
  C venv：超时→UNKNOWN · 存在但 import 坏→UNAVAILABLE · 不存在→三条 MISSING+remedy
          · 真实 .venv-basic-pitch 机器验证（无 venv 的机器 skip）
  D unsupported→UNKNOWN · 无 spec→UNKNOWN 不猜测
  E 四态 join：eligible+unavailable / installed+ineligible / eligible+available
  F 无隐藏缓存（两次真实重跑）· 归一化输出确定性 · registry 快照不变
    · capabilities 层不引用探针（源码级）· 子进程导入 capabilities 不加载 runtime
  G spec 覆盖不变量（每个内置 provider 的 requirement 字符串与声明逐字逐序一致）
    · 每个子进程有 timeout/capture/stdin=DEVNULL/参数数组 · PYTHONUTF8 环境
    · 本地探测不碰网络（socket 封死仍通过）
```

覆盖不变量是这张表的保险丝：改声明不改 spec（或反之）会让测试失败，"声明"与"被验证"
不可能悄悄分叉。

## 10. 本任务非目标（确认未做）

不执行生产能力 · 不自动安装 · 不下载模型 · 不因基准速度改 provider 排序 · 不改 Canon ·
不改 Desktop UI · 不声称运行时可用等于生产质量。
