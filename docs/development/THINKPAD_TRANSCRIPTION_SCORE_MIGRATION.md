# ThinkPad 006 — Transcription & Score → Core Capability Contracts（迁移预备）

**Task:** MOODIFY THINKPAD HEAVY LANE 006（§2 门禁未解锁，本文档为只读预备）
**Branch:** `feat/thinkpad-transcription-score-006`（本文件是**唯一**产物；实现未开始）
**Date:** 2026-10-10
**方法:** 每个结论标注来源（文件 + 行号）；调用点按任务要求逐一定位，不假设文件名。PENDING 部分不预填。

---

## 0. 依赖门禁状态（§2）—— 实现未开始的原因

| 门禁/条件 | 状态 | 证据（2026-10-10 复核） |
|---|---|---|
| PR #49 | ✅ MERGED 2026-10-05 | `requirements-transcribe.txt` 等已定型 |
| THINKPAD 003（#67） | ❌ OPEN（**硬门禁**） | runtime-probe 契约未合并；等待裁定沿用 004/005 先例（人类两次选择"等待门禁"） |
| "Prefer starting after THINKPAD 005 is stable"（软偏好） | ❌ 未满足 | 005 自身门禁阻塞（等 #67），执行模式尚未建立——现在实现 006 就会**另造一套**执行架构，正是 §2 想避免的 |

人类先例（2026-10-09/10 两次裁定）：等待门禁 + 只读预备。本文档即预备产物；如需例外放行请明确指示。

## 1. 现状调用链（Desktop-owned，before）—— 精确入口点

```text
自动链 / 手动触发
  sessionStructure(dir) (main.js:1893)        ← 编排器的「结构」步
    ├─ transcribeMidi(dir, src) (main.js:1290)     ← **必需**；失败则整步失败
    │     守卫: 输入必须是世界源或 case 内文件（:1294）
    │     运行时: resolveRuntimeTool('basic-pitch','basic-pitch')
    │             → .venv-basic-pitch/Scripts/basic-pitch.exe（runtime.js:53-58）
    │     命令: basic-pitch --save-midi --model-serialization onnx <outdir> <audio> (main.js:1300-1301)
    │     输出: <case>/midi/*.mid（basename `_basic_pitch` 后缀由工具自己命名；:1307 按前缀扫描回找）
    │     成功判定: **退出码**（runLong res.ok）——无产物验证、无哈希
    ├─ structureAnalysis(dir) (main.js:1252)        ← 失败不阻断，如实回报（:1907）
    └─ convertScore(dir, midi) (main.js:1314)       ← 失败不阻断（scoreSkipped，:1909；"MIDI 才是机器可读结构"）
          守卫: MIDI 必须在 case 目录内（:1316）
          运行时: resolveRuntime('score').python → **别名 .venv-basic-pitch**（main.js:1323；runtime.js:60-66）
          命令: moodify-desktop/scripts/midi_to_musicxml.py <midi> <out.musicxml> (main.js:1325-1326)
          输出: <case>/score/<base>.musicxml
          成功判定: **退出码**；无产物验证、无哈希
```

**两个能力入口已天然分离**（§4 要求）：转写 = basic-pitch CLI；曲谱 = `midi_to_musicxml.py`（内部 `from music21 import converter`）。路径守卫已存在（containment 检查在两端都有）。

## 2. Provider / runtime 现状与缺口

| provider | 注册表声明（builtin.py） | 运行时（实测/代码） | 缺口 |
|---|---|---|---|
| `basic_pitch.local` | CONNECTED_UNTESTED / MODEL / Apache-2.0 / CONDITIONALLY_DETERMINISTIC / `basic-pitch==0.4.0` + `.venv-basic-pitch`（:165-179） | `.venv-basic-pitch` 实装 basic-pitch 0.4.0（onnxruntime 1.23.2，权重随 wheel）；CLI `--save-midi --model-serialization onnx`；**GBK 陷阱：必须 PYTHONUTF8=1**（emoji 打印崩溃，THINKPAD_RUNTIME_ARCHITECTURE §3） | 无 provider_version 记录进产物；无输出哈希；无参数记录 |
| `music21.local` | CONNECTED_UNTESTED / LIBRARY / BSD-3-Clause / DETERMINISTIC / `.venv-score`（:181-195） | **CLR-004 漂移**：桌面 score 运行时别名到 `.venv-basic-pitch`，而 2026-10-09 实测该 venv **没有 music21**（ModuleNotFoundError）；music21 9.9.2 在 `.venv-score` | 桌面曲谱路径**本机当前不可用**（实测）；声明/实现/机器三方不一致——006 不得在 Core 里复制这套别名，须走 003 探针 + 声明真相 |

**§5B 的落点**：运行时定位走 THINKPAD 003 的 `moodify.runtime`（`venv_candidates` 已实现 env 覆盖 + repo-root 默认，与 runtime.js 语义同构）；**不在 Desktop 新增定位器**，也不在 Core 复制 Desktop 的 `probeRuntime`。

## 3. 与 §5A 契约的差距（现状 → 目标）

| §5A 字段 | 转写现状 | 曲谱现状 |
|---|---|---|
| source/input hash | ❌ 无（音频路径散落于参数） | ❌ 无（MIDI 哈希未记） |
| provider_id / version | ❌（只有运行时路径） | ❌ |
| runtime version | 部分（basic-pitch 0.4.0 仅存在于安装处，不进产物） | ❌ |
| parameters | 在命令行里（onnx 序列化），不进产物 | ❌ |
| 输出哈希 | ❌ | ❌ |
| timing | 仅有 runLong 进度日志，不进产物 | 同 |
| warnings | ❌ | 曲谱失败原因仅内存回传（:1909），不落盘 |

**结论：两个阶段目前都是"退出码即成功、无 provenance"。** 006 的执行契约（复用 005 模式）把它们升级为 `route → probe → execute → validate → hash → provenance`。

## 4. 契约设计草案（§5，**未实现**）

### 4.1 两个能力边界（§4 强制分离）

```text
midi.transcribe:  audio artifact (+hash) → MIDI artifact (+hash) + provenance
score.generate:   MIDI artifact (+hash)  → MusicXML artifact (+hash) + provenance
```

不为两者建"一体化 understand"命令；转写成功/曲谱失败是合法终态（现状 sessionStructure 的
"scoreSkipped 不阻断"语义由契约保留：调用方决定可选项，能力层如实报每个的结果）。

### 4.2 验证规则（§5D；**零新依赖**设计）

```text
MIDI:      stdlib 解析 MThd chunk（format/ntrks/division）+ 至少一个 MTrk 且事件非空；
           路径 containment（realpath 必须落在 output_dir 内）；记 size+sha256。
MusicXML:  xml.etree 解析（well-formed）+ 根元素属 MusicXML 家族（score-partwise/score-timewise）；
           input MIDI hash 必须链接；路径 containment。
```

理由：Core venv 无 mido/music21，引入新依赖违反 `existing > … > custom` 的举证责任方向；头部/事件级解析足以证明**技术可读**，且明确不证明音乐正确（§5E）。
（待裁决策 1：是否在实现时改用更严的完整事件校验——若 music21 迁移进 Core 再议。）

### 4.3 provenance / FAILURE / REUSE

- 输出契约沿用 005 的执行边界草案：`provider_id / provider_version / runtime evidence（003 探针引用）/ input hashes / output hashes / parameters / timings / warnings / execution_status`。
- 失败映射复用现有 `FailureCode`：运行时缺失→`DEPENDENCY_MISSING`；无资格 provider→`PROVIDER_UNAVAILABLE`；崩溃→`EXECUTION_FAILED`；超时→`TIMEOUT`；产物不合法→`INTEGRITY_ERROR`。**不新增码。**
- **复用（§5F）**：现状**不存在**任何 reuse 语义（无 provenance 可比）。契约落地后，复用键 = `input_hash + provider_id + provider_version + parameters + capability_id` 全匹配；命中则 `execution_status = REUSED` 并保留被复用产物的原始 `executed_at`。
  待裁决策 2：0.1 是否实现复用（倾向：**实现只读"可复用"判定 + 显式 REUSED**，因为 §5F 的核心是"绝不假装复用是新执行"；但若 005 的模式未定，先用契约字段占位、行为面延后）。
- **质量边界（§5E，PR 必含）**：`parseable MIDI ≠ 转写正确`；`parseable MusicXML ≠ 曲谱正确`；**不发明 accuracy 百分比**（无 ground-truth 数据集）。

### 4.4 CLI / Desktop parity（§5G）

- CLI 草案：`moodify midi transcribe <audio> --outdir …` / `moodify score generate <midi> --outdir …`（或并入 005 的 `stems`-风格子命令组；实现时与 005 统一命名）。
- Desktop：`transcribeMidi`/`convertScore` 改调 Core（保留：输入守卫语义、`scoreSkipped` 不阻断语义、runLong 进度、单飞）；Desktop **不得**在 Core 验证失败时自行宣布成功（§5G 最后一句——当前"退出码即成功"正是要删掉的行为）。
- 与 005 的关系（§2 软偏好）：006 复用 005 建立的执行边界与测试骨架；**在 005 之前实现 = 另造框架**，正是不做实现的原因之一。

## 5. ThinkPad 证据计划（§6）—— **PENDING（门禁后执行）**

| 输入（≥3，不新增大文件） | 内容 | 必录 |
|---|---|---|
| 简单器乐（带音高） | 如仓库既有小样或生成的小段 | 转写/曲谱 wall time（分列）、进程树峰值内存、产物尺寸、哈希、冷/热差 |
| 复调/较复杂 | 同上 | 同上（**不评准确率**——只报技术事实） |
| 人声/混合内容 | 同上 | 已知失败样例：有无人声对 MIDI 事件密度的影响如实记录，不下结论 |

已知失败样例（实现时逐一实测并记入）：GBK 未设 PYTHONUTF8 的崩溃形态；`.venv-score` 缺失/别名 venv 无 music21（CLR-004 形态）；空/极短音频；不可读 MIDI 交给曲谱阶段。
测量工具与方法在实现时定并如实标注口径；**哈希确定性**只在期望确定处断言（temperature/设备无关的 CLI 应逐字节确定——实测后如实写）。

## 6. 测试映射（§7 → 实现清单）

| §7 要求 | 落点 |
|---|---|
| runtime unavailable | 探针 mock → DEPENDENCY_MISSING |
| 转写成功 / 崩溃 / 超时 | 合成 provider 子进程（沿用 005 骨架） |
| invalid MIDI 输出 / invalid XML | 篡改产物 → INTEGRITY_ERROR |
| 曲谱成功 | 集成（有 music21 运行时的机器） |
| mismatched input hash | provenance 校验 |
| reuse 仅当 provenance 匹配 / 参数变化阻止复用 | 复用单测（若实现） |
| CLI 与 Desktop 同状态 | 同函数断言 + Desktop 侧测试（CI，本机无 Node） |
| Desktop 无重复运行时定位器 | 源码级检查（无 resolveRuntime 新副本；旧路径仅剩调用壳） |
| 确定性 JSON | 归一化输出测试 |

全量 Core 回归 + ruff 必跑；Desktop 相关测试在 CI。

## 7. 待裁决策（实现前）

1. MIDI 验证深度：stdlib 头部/事件级（倾向）vs 完整解析（需新依赖）。
2. 复用：只读判定 + `REUSED` 状态即落地（倾向）vs 行为面延后。
3. 执行契约的 MIP 判定与 006/005 共用一份（005 计划 §4.7 决策 1 同题）。
4. CLI 命名空间：独立 `midi`/`score` 子命令 vs 与 005 统一 `capability`-风格入口。

## 8. 范围声明

只读预备：未创建/修改任何 Core/Desktop 代码，未执行转写或曲谱转换。实现顺序建议：**#67 合并 → 005 实现落地 → 006 rebase 后复用同一执行模式**（§2 的显式偏好）。
