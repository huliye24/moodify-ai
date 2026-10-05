# 深度处理链路缺失模块扫描 — DEEP-PROCESSING-GAP-SCAN-001

**Date:** 2026-10-05
**Scope:** Studio 六阶段 `检测 → 问题 → 分轨 → 结构 → 方案 → 成品`（`moodify-desktop/src/pipeline.js`）
**Method:** 磁盘产物清点（24 个真实 case）+ 本机运行时复现 + 仓库历史检索
**Status:** 扫描结论。本文件是**事实记录**，不是权威；权威见 root `AGENTS.md` 与 `docs/canon/*`。

---

## 0. 结论先说

深度处理之所以「还是有问题」，**不是界面问题，是四类空缺叠加**：

```text
① 环境层空缺   → 三个外部运行时全缺；全局 python 是坏的；包被指到另一个 checkout
② 科学层空缺   → 没有真实分离引擎、没有音转 MIDI、没有任何结构/节拍分析
③ 闭环层空缺   → 复检/修音/A-B 决策的整套实现**已写好但没进主线**（codex/studio-v4-latest）
④ 证据层空缺   → Core 只有 2 条 finding 规则；绝大多数 case 的诊断是空的
```

这不是组织能力不足的问题，**是集成失败**：

- ③ 的代码已经存在（一个 commit、227 文件、+2213 行渲染层），停在一个**未合并**分支上；
- ② 的成熟开源项目全部存在，且本机已经装好了其中最重要的一个（Demucs 4.0.1），
  **只是从未接线**；
- ① 是纯粹的环境配置问题，但它是**当前最致命的一环**：它让 ②③ 全部表现为失败。

---

## 1. 逐阶段现状（以证据为准）

| 阶段 | 界面 | 磁盘产物 | 真实可用性 | 阻断原因 |
|---|---|---|---|---|
| ① 检测 ANALYZE | ✅ | `report.json` 等 | **可用** | — |
| ② 问题 DIAGNOSE | ✅ | `diagnosis.json` | **结构可用，内容常空** | Core 只有 2 条 finding 规则 |
| ③ 分轨 SEPARATE | ✅ | `stems/*.wav` | **❌ 必崩** | `DEPENDENCY_MISSING` + librosa/pandas ABI |
| ④ 结构 STRUCTURE | ✅ | `midi/*.mid` | **❌ 不可用** | basic-pitch / music21 未安装；无节拍/段落分析 |
| ⑤ 方案 PLAN | ✅ | `plans/*.json` | **⚠️ 只剩空壳** | 无 AI 规划器；写入的是 Core 草稿的复制 |
| ⑥ 成品 FINISH | ✅ | `versions/ai_*/` | **仅快速完成可用** | 无任意方案渲染；无复检；`export_record` 互相覆盖 |

### 1.1 现场复现（本机，2026-10-05）

```text
$ node -e "require('.../runtime.js').resolveRuntime('basic-pitch')"
  → DEPENDENCY_MISSING 缺少必需的 Moodify 外部运行时：basic-pitch
$ node -e "...resolveRuntime('score')"
  → DEPENDENCY_MISSING 缺少必需的 Moodify 外部运行时：score

$ python moodify-desktop/scripts/dsp_separate.py <real.wav> --outdir <case>/stems
  → ValueError: numpy.dtype size changed, may indicate binary incompatibility.
    Expected 96 from C header, got 88 from PyObject
    （librosa.decompose.hpss → sklearn → pandas 导入链崩溃）
```

`runtime.js` 的候选目录 `.venv-basic-pitch` / `.venv-score`：**在磁盘上不存在**。

### 1.2 包指向了另一个 checkout（隐蔽但严重）

```text
python -c "import moodify; print(moodify.__file__)"
  → E:\moodify\moodify-core-package\src\moodify\__init__.py     ← 不是 E:\moodify-local

$ python -m moodify.release_cli --help
  子命令含 tuning ← 该子命令**不在本仓库的 release_cli.py 里**
```

`moodify` 是以 editable 方式装到全局 site-packages 的，指向 `E:\moodify\moodify-core-package\src`。
后果：桌面壳调用的 Core **不是本仓库这份代码**，「本仓库行为」与「实际运行行为」已经分叉。
`E:\moodify` 与 `E:\moodify-local` 唯一的分叉点，就是那个未合并的 V4 提交。

### 1.3 24 个真实 case 的产物清点

```text
深链完整（stems + midi + score）:   6 个
有 stems 无 midi:                   1 个
有 studio/plans/*.json:             0 个   ← ⑤ 方案从未被产物证明成功过
studio/versions/ai_*:               1 个（该 case 无 stems / 无 midi，走的是快速完成）
```

**`plans/` 全空**是本扫描最硬的一条事实：⑥ 深度完成的门禁要求 `studio/plans/*.json` 存在，
而 24 个真实 case 里一个都没有 —— 深度路径在真实使用中**从未走通过**。

---

## 2. 缺失模块清单（按层）

### 2.1 环境层（P0，当前最致命）

| 缺失 | 现状 | 影响 |
|---|---|---|
| 运行时环境层 | 无任何 `.venv-*`；`MOODIFY_PYTHON` 未设 → 用全局 python | 所有外部能力直接 `DEPENDENCY_MISSING` |
| 依赖版本钉死 | 全局 numpy 2.4.6 与 pandas/sklearn 二进制不兼容 | `dsp_separate.py` 必崩 |
| Core 解析隔离 | `moodify` 可编辑安装指向 `E:\moodify` | 跑的不是本仓库代码 |
| 打包内运行时 | `package.json` 的 `files` 不含任何运行时 | 安装包在用户机器上同样没有能力 |

### 2.2 科学层（P1）

| 缺失模块 | 应该做什么 | 当前替代品 | 替代品的诚实边界 |
|---|---|---|---|
| **真实源分离** | 4 轨（鼓/贝斯/人声/其他）神经网络分离 | `dsp_separate.py`（中置估计 + HPSS） | 自己写明「非模型、有残留与伪影、不构成母带级分轨」 |
| **音频 → MIDI** | 复音转写 | 无 | ④ 结构阶段事实上不可达 |
| **节拍 / 下拍 / BPM** | 结构的基础 | 无 | ⑤ 方案无法知道歌曲的节奏骨架 |
| **段落边界（intro/verse/chorus…）** | 让方案能按段处理 | 无 | Core 有 `auditory/structure.py` 的数据类型，**没有任何检测实现** |
| **调性 / 和弦 / 音域** | 方案的可解释依据 | 无 | — |
| **MIDI 清理 / 量化 / 合并** | 把转写结果变成可用结构 | 无 | — |
| **完整诊断规则集** | 让 ② 有问题可说 | Core 18 参数引擎（桌面够不到） | 接入即引入第二诊断权威 → 需人类裁决 |

### 2.3 闭环层（P1）— **已实现，未合并**

`origin/codex/studio-v4-latest` = `d6d203b5`（2026-10-05 11:05，227 files，+22k 行）：

| 模块 | 作用 |
|---|---|
| `src/orchestrator.js` | 完成会话调度循环（每轮重新推导，同一步只试一次） |
| `src/session.js` | 8 内部阶段 → 6 用户相位的投影 + 阻断原因分类 |
| `src/tuning.js` | ④修音 / ⑤复合 的**成对 A/B 产物层** + ⑦选定三出口账本（A/B/保留原版） |
| `src/recheck.js` | ⑥复检：原版/A/B 三份 `report.json` 逐指标对齐表 |
| `src/keepsake.js` | 完成时刻留存（非权威表现层） |
| `src/history-sync/` | 个人历史同步（含 Supabase 迁移 + RLS 测试） |
| `core/tuning.py` | Core 侧配对渲染（MIP-0002） |
| `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md` | 521 行流程契约 |

分叉量：**领先 main 1 个提交，落后 main 35 个提交**，merge-base = `1d53f234`（在本仓库历史内）。
即：它可以被合并，但需要一次真实的集成（不是 fast-forward）。

### 2.4 其他真实缺陷（非缺失模块，但同样致命）

| 缺陷 | 位置 | 后果 |
|---|---|---|
| 导出记录固定文件名 | `main.js` → `export/export_record.json` | 第二次导出**静默覆盖**第一次的记录 |
| `pipeline.json` schema 双版本 | 磁盘上有 `0.2`（含 `reversible/tuned/composed/rechecked`） | V4 的字段被当前代码丢弃，历史不可读 |
| 遗留脚本落在 case 世界内 | `case_92b5a1d1...` 内有 `_diag.py` `_write_plan.py` 等 | 人肉绕过 UI 的证据：UI 到不了的地方只能靠手写脚本 |

---

## 3. 可补齐的成熟开源项目（GitHub）

选型遵守 `docs/canon/TECHNOLOGY_PRINCIPLES.md`：`existing > standard library > mature OSS > custom`。

| 缺口 | 项目 | 许可 | 本机状态 | 建议 |
|---|---|---|---|---|
| 真实 4 轨分离 | [adefossez/demucs](https://github.com/adefossez/demucs)（`htdemucs`） | MIT | **已安装 4.0.1，权重已缓存，实测 CPU RTF 2.2–3.6x** | **首选**，已实测通过 |
| 更高质量分离 | [lucidrains/BS-RoFormer](https://github.com/lucidrains/BS-RoFormer) | MIT（权重另议） | 未装 | 后续「精分离」档 |
| 音频 → MIDI | [spotify/basic-pitch](https://github.com/spotify/basic-pitch) | Apache-2.0 | **未装** | **首选**（仓库早已声明要用它） |
| MIDI → 曲谱 | [cuthbertLab/music21](https://github.com/cuthbertLab/music21) | BSD-3 | **未装** | **首选**（仓库早已声明要用它） |
| 节拍/BPM/onset | [librosa](https://github.com/librosa/librosa) | ISC | 已装 0.11.0 | 用 `.beat` / `.onset`（**绕开**会崩的 `.decompose`） |
| 段落结构 | [taejunkim/all-in-one](https://github.com/taejunkim/all-in-one)（All-In-One Music Structure Analyzer） | MIT | 未装 | 段落检测候选；需评估依赖重量 |
| 单音高提取兜底 | librosa `pyin` | ISC | 已装 | basic-pitch 不可用时的旋律兜底（诚实标注为单音） |
| 前端曲谱渲染 | [opensheetmusicdisplay](https://github.com/opensheetmusicdisplay/opensheetmusicdisplay) | BSD-3 | **已 vendor 在仓库内** | 保持不变 |

### 引入方式（关于「把代码引入我的项目」）

`AGENTS.md` 与技术原则要求**不造第二套 Core、不自研模型**。因此这些项目**不以源码 vendoring 方式拷进仓库**，
而是**声明为受版本约束的外部运行时**，由 `moodify-desktop/src/runtime.js` 解析、由 `main.js` 编排 ——
这正是仓库**既有**的约定（`dsp_separate.py` 注释、`RUNTIMES` 清单、`requirements.lock.txt`）。

这样做的理由：

- 复制 Demucs 源码进仓库 = 把 3 万行上游代码变成我们的维护责任，且与「One Core」冲突；
- 声明为外部运行时 = 上游可独立升级，我们只维护**接口与诚实边界**；
- 仓库已有的 `.gitignore` 与结构守卫也不会接受 vendored 大包。

---

## 4. 本次已实施的补齐

见下一节「Implementation Log」。本文件在实施完成后回填。

---

## 5. 需人类裁决

1. **是否合并 `codex/studio-v4-latest`**（227 文件 / +22k 行，含新 Canon V4、新增 Supabase 依赖、个人身份历史）。
   这是**产品面变更**（新增账号/历史同步），不是普通功能任务 → `HUMAN_DECISION_REQUIRED`。
2. Core 18 参数诊断引擎是否接入桌面（会引入第二套诊断权威的可能）→ 维持 `HUMAN_DECISION_REQUIRED`。
3. 「精分离」档用 BS-RoFormer（质量更高，依赖更重）还是停在 htdemucs。
