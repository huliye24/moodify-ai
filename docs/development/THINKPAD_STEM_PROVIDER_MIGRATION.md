# ThinkPad 005 — Stem Separation → Core Capability Contract（迁移预备）

**Task:** MOODIFY THINKPAD HEAVY LANE 005（§2 门禁未解锁，本文档为只读预备）
**Branch:** `feat/thinkpad-core-separation-005`（本文件是**唯一**产物；实现未开始）
**Date:** 2026-10-10
**方法:** 每个结论标注来源（文件 + 行号 / 测试名）。桌面语义被表征、不被本线占有；未实现的部分如实标注 PENDING。

---

## 0. 依赖门禁状态（§2）—— 实现未开始的原因

| 门禁项 | 状态 | 证据（2026-10-10 复核） |
|---|---|---|
| PR #49 | ✅ MERGED 2026-10-05 | 分离脚本与运行时需求已定型（`requirements-audio.txt` / `requirements-demucs.txt` / `requirements-transcribe.txt`） |
| THINKPAD 003（#67） | ❌ OPEN | runtime-probe 契约未合并；"frozen for this task" 分支未启用（人类 2026-10-10 裁定：等待 #67 合并） |

**人类裁定：等待门禁。** 实现须在 #67 合并后从更新后的 main 出发；本分支届时可 rebase 复用本文件。

## 1. 现状调用链（Desktop-owned，before）

```text
renderer / orchestrator
  → ipcMain 'stems:run' (main.js:739)
  → separateStems(caseDir, mode) (main.js:1166)
      mode ∈ {auto(默认), model, dsp}       ← 用户偏好落盘（stems:engine:set, main.js:750）
      modelProbe = probeRuntime('demucs')   ← **Desktop 自己的运行时探针**（runtime.js:161）
      engine = dsp | model | (auto → 可用则 model，否则 dsp + downgraded 标记)
      model: resolveRuntime('demucs').python  + model_separate.py <src> --outdir <case>/stems
      dsp:   resolveRuntime('audio').python   + dsp_separate.py  <src> --outdir <case>/stems
      runLong('stems', …)                   ← 流式进度、同类单飞；**没有超时**（main.js:659）
      'ok' = 子进程退出码                    ← 语义成功由 Desktop 自行定义
  → 另有 stems:roundtrip (main.js:1219)：resolveRuntime('audio') + roundtrip.py → studio/roundtrip.json
  → UI 探针：'stems:engine:get' / 'capabilities:probe'（probeAllRuntimes）
```

**这就是 005 要搬走的权威**：provider 选择（auto/降级/偏好）、运行时可用性判断（probeRuntime）、
成功判定（退出码）目前全部在 Desktop（`main.js` + `runtime.js`）。Core 侧目前对分离只有**声明**没有执行：
`moodify.preview_separation`（builtin.py:114），且其声明内容与实现已漂移（见 §3）。

## 2. 两个引擎的产物契约（现状，逐行核实）

| | 引擎 A `dsp_separate.py`（预览级） | 引擎 B `model_separate.py`（模型级） |
|---|---|---|
| 依赖 | numpy + soundfile + scipy（**刻意去 librosa**，:9-18） | numpy + soundfile + torch + demucs（+librosa 仅在采样率≠44.1k 时重采样） |
| 缺依赖行为 | 无显式处理（traceback → 退出码非 0） | 显式 `DEPENDENCY_MISSING` JSON + exit 2（:65,:77） |
| 输出轨 | `vocals / instrumental / harmonic / percussive` —— **两套相互重叠的完整划分**（:164-172） | `drums / bass / other / vocals` —— 一套四轨完整划分（:146-150） |
| partition 声明 | primary=[vocals,instrumental]，alternates=[[harmonic,percussive]] | primary=四轨，alternates=[] |
| grade | `PREVIEW_NOT_MASTERING_GRADE`（:152） | `MODEL_SEPARATION_NOT_VERIFIED_AGAINST_ORIGINAL_STEMS`（:135） |
| source 哈希 | `source_sha256` ✓ | `source_sha256` ✓ |
| **stem 哈希** | **不记录** | **不记录** | §5D 要求补 |
| 采样率 | 保持输入 | **重采样到 44.1k**（:95-99；roundtrip 已知此差异并补偿） |
| 模型下载 | 无 | **首次运行静默下载 htdemucs 权重**（:10 注释，缓存 ~/.cache/torch） | §9 禁止静默下载——须显式化 |
| 设备 | — | device auto/cpu/cuda；`inference_elapsed_s` 记录 |
| 进度输出 | 人读行 + 末行一个 JSON | 同 |

`roundtrip.py`（壳侧验证，385 行）：读 `stems/manifest.json` 的 `partition` 声明，按划分求和 vs 原版，
采样率差异显式重采样（:58-74），输出 `studio/roundtrip.json`（`passed` + `measurement` + 平凡分解对照组）。
它**测的是重建一致性，不是分离质量**（:8-21 自我声明）。

## 3. Provider 声明现状与缺口（§4 Provider truth）

| 需要的声明 | 现状 | 缺口 |
|---|---|---|
| `moodify.preview_separator`（任务示例名） | 注册表里是 **`moodify.preview_separation`**（CLI 类、EXPERIMENTAL） | 命名与真源以注册表为准；示例名不采用 |
| 运行时需求 | 声明 `.venv-basic-pitch`+librosa —— **已漂移**：实际跑 `.venv-audio`+numpy/soundfile/scipy（CLR-003 已记录） | 随实现修正（或在 MIP 里统一） |
| 模型分离 provider | **不存在**（注册表无 demucs/hdemucs 条目） | 需要新增声明（`moodify.demucs_local` 或同等物）——**新增 provider = registry schema 面变更 → MIP** |
| license | preview: GPL-3.0（Moodify 代码）；demucs: MIT 代码 + htdemucs 权重 | 注册表有 code/weights_license 字段 ✓ |
| determinism | preview: DETERMINISTIC；demucs: 需声明（GPU/CPU、模型版本） | Provider.determinism 字段存在，取值待定 |
| **output stem schema** | 注册表 **无此字段**（`Provider` 模型 315 行，无 stems/grade/formats/failure modes） | §4B 要求 → 设计裁决（见 §5 决策 2） |
| **quality/grade label** | 在脚本 manifest 里（两个 grade 字符串），不在注册表 | 同上 |
| **supported sample formats** | 注册表无；脚本实际吃 soundfile 能读的一切 | 同上 |
| **failure modes** | FailureCode 词汇表存在，但 provider 未声明它用哪些 | 可随输出契约记录 |
| **provenance fields** | manifest 已含 source_sha256/engine/upstream/py 版本；缺 stem 哈希与时间戳统一形状 | 输出契约补齐 |

## 4. 迁移设计草案（§5，**未实现**）

### 4.1 执行契约（§5A）

```text
输入:  capability_id = "stem.separate"；source artifact（+hash）；policy 或显式
       authorized provider；parameters（engine 偏好等）；output_dir；deadline
输出:  provider_id + provider_version；runtime evidence（引用 THINKPAD 003 探针结果）；
       input hashes；output artifact hashes（含每个 stem）；stem manifest（partition+grade）；
       execution status；warnings；timings；failure（FailureCode + details）
```

落点：新 Core 模块（草案 `moodify/capabilities/execution.py` 或 `moodify/separation/`），
**调用** router（`select_provider("stem.separate", policy)`）与 runtime probe（`moodify.runtime`），
不复制任何 DSP/模型逻辑——provider adapter 以子进程方式调用现有两个脚本（§5B 明确允许）。

### 4.2 Provider adapters（§5B）

```text
adapter preview : runtime = .venv-audio（CLR-003 修正后）→ dsp_separate.py 子进程
adapter demucs  : runtime = .venv-demucs → model_separate.py 子进程（权重缓存状态显式化）
```

每个 adapter：显式 timeout（runLong 目前**没有**）、stdin DEVNULL、输出截断、末行 JSON 解析、
`DEPENDENCY_MISSING` 透传、产物落盘后**验证 + 哈希**（§5D）。

### 4.3 运行时预检（§5C）—— 复用 003，不另造

```text
router 资格（policy 驱动，含用户 engine 偏好作为 preferred/excluded）→ THINKPAD 003 探针
→ AVAILABLE 才执行；否则显式失败：
  NO_ELIGIBLE_PROVIDER        → FailureCode.PROVIDER_UNAVAILABLE（router 已给出）
  PROVIDER_RUNTIME_UNAVAILABLE → FailureCode.DEPENDENCY_MISSING（runtime truth 缺失）
  EXECUTION_FAILED / TIMEOUT  → 现有码
  OUTPUT_CONTRACT_VIOLATION   → FailureCode.INTEGRITY_ERROR（哈希/清单不符）
```

**不新增 failure code**：现有 `FailureCode` 词汇表（failures.py:22）已覆盖全部四类；新增码 = 契约变更，非必要不做。

### 4.4 输出验证（§5D）

逐条：stem 存在/可读（soundfile 头读，不解码全部样本）→ sr/channels 记录 → 路径必须落在 output_dir 内
（realpath containment）→ manifest 的 stems 映射与磁盘一致 → 每个 stem 记 sha256+bytes →
`roundtrip.json`（若 case 已有，或以 `--roundtrip` 调用现有脚本）作为**引用**附上 → grade 只来自 manifest，
绝不从 UI 假设。

### 4.5 Desktop 兼容适配（§5E）—— 最小改动

`separateStems()` 改为调用 Core CLI（`moodify stems separate …`），**保留**：用户 engine 偏好语义
（作为 policy 输入）、downgraded 提示形状、runLong 进度转发、单飞。删除的是 Desktop 自己做的
provider 选择与成功判定。**这是本线第一次有意触碰 Desktop 代码**（前序任务均为 cross-lane 记录）；
改动限定在 `main.js` 的分离调用路径 + 配套测试，不做 UI 重设计。

### 4.6 CLI 直连（§5F）

新子命令草案（`moodify stems separate <audio> --outdir … [--provider …] [--engine-preference …] --json`），
与 Desktop 走**同一个**执行函数。**注意**：新增 Core 执行契约属于 AGENTS.md 的 MIP 范畴（"core
behavior contract"）——实现时随附 `protocol/mips/MIP-0003-…（DRAFT）`，或在 PR 里论证 0.1 为内部边界。
**决策 1**（留给 mainline/实现时）：执行契约 MIP 随实现起草 vs 先内部化。

### 4.7 设计决策清单（实现前须裁）

1. 执行契约是否走 MIP（§4.6）。
2. §4B 的 provider 扩展字段（stem schema/grade/formats/failure modes/provenance）放**注册表**（MIP 改
   schema）还是执行层 descriptor（避免双源：必须二选一，不得两处都声明）。
3. demucs provider 的 determinism 取值（模型+设备+版本 → 大概率 CONDITIONALLY_DETERMINISTIC）。
4. 首跑权重下载：暴露（preflight 报告 weights cached/not）为主，禁止静默下载是产品决策——
   完全阻断下载需要 mainline 裁定（既有行为改变）。
5. roundtrip 在 0.1 里"引用已有产物"还是"可选调用"（§4.4 倾向：引用为默认，`--roundtrip` 为显式开关）。

## 5. ThinkPad 工作量证据计划（§6）—— **PENDING（门禁后执行）**

| 用例 | 输入 | 引擎 | 必录 |
|---|---|---|---|
| 短样 | ≤10 s | preview | wall time / peak process-tree memory / CPU 观察 / stem 数 / sr / stem hashes / roundtrip |
| 30–60 s 代表性音频 | 30–60 s | preview + model（若 .venv-demucs 就绪） | 同上 + inference_elapsed_s |
| 较长曲目 | ≥3 min | preview（model 视 RTF 决定） | 同上 |

方法：wall time = 外层计时；peak memory = 进程树峰值（Windows 用 `Get-Process`/psutil，实现时定并如实标注口径）；
CPU 观察 = 任务管理器/`Get-Counter` 采样，仅作观察不作质量分。**速度不是质量分**（§6）。
本机 `.venv-demucs` 当前**不存在**（THINKPAD_RUNTIME_ARCHITECTURE §5：Demucs 未建运行时）；model 引擎证据取决于
门禁后是否按 `requirements-demucs.txt` 建设运行时——**若未建，如实报告 preview-only，不发明 model 数据**。

## 6. 测试与验收映射（§7 → 实现清单）

| §7 要求 | 落点 |
|---|---|
| provider selection / runtime unavailable | Core 单测：router+execution 合约（monkeypatch probe） |
| preview 成功 / model 成功 | Core 集成（preview）＋ model 视运行时（可标 integration） |
| provider crash / timeout / missing stem / corrupt stem | 合成 provider 子进程 + 篡改产物 |
| path traversal / manifest mismatch | 输出验证单测（复用 002 的 containment 手法） |
| provenance recorded | 输出契约断言（hashes+版本+timings） |
| Desktop adapter 用 Core 路径 / 无第二语义 | Desktop 侧测试（CI 跑）+ 源码检查（无独立 provider 选择残留） |
| CLI 同路径 | CLI 测试与 Desktop 调用同一函数断言 |

全量 Core 回归 + 相关 Desktop 测试（CI）必跑；本机无 Node（§表征 004 已记）。

## 7. 门禁解除后的执行顺序

1. rebase 本分支到更新后的 main（含 #67）；核对探针 API 与本文档 §4.3 一致；
2. 裁 §4.7 五决策（含 MIP 判定）→ 实现执行契约 + adapters + 验证 + CLI；
3. Desktop 最小适配（§4.5）+ 两侧测试；
4. ThinkPad 基准（§5 表）+ 填写本文件的 PENDING 部分；
5. 全量回归 → PR（标题按 §10）。

## 8. 范围声明

只读预备：未创建/修改任何 Core/Desktop 代码，未跑分离执行（避免在门禁前制造未冻结语义的产物）。
