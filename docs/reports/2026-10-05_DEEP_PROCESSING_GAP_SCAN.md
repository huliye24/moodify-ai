# 深度处理链路缺失模块扫描 — DEEP-PROCESSING-GAP-SCAN-001

**Date:** 2026-10-05
**Scope:** Studio 六阶段 `检测 → 问题 → 分轨 → 结构 → 方案 → 成品`（`moodify-desktop/src/pipeline.js`）
**Method:** 磁盘产物清点（24 个真实 case）+ 本机运行时复现 + 仓库历史检索
**Status:** 扫描结论 + 修复记录。本文件是**事实记录**，不是权威；权威见 root `AGENTS.md` 与 `docs/canon/*`。

---

## 0. 结论先说

深度处理之所以「还是有问题」，**不是界面问题，是四类空缺叠加**：

```text
① 环境层空缺   → 三个外部运行时全缺；全局 python 是坏的；包被指到另一个 checkout
② 科学层空缺   → 没有真实分离引擎、没有音转 MIDI、没有任何结构/节拍分析
③ 闭环层空缺   → 复检/修音/A-B 决策的整套实现已写好但没进主线（codex/studio-v4-latest）
④ 门禁层空缺   → 可逆性只写在文档里，没有任何代码产出它
```

这不是「组织能力不足」，**是集成失败**：

- ③ 的代码已经存在（一个 commit、227 文件、+2213 行渲染层），停在一个**未合并**分支上；
- ② 的成熟开源项目全部存在，且本机已经装好了其中最重要的一个（Demucs 4.0.1），
  **只是从未接线**；
- ① 是纯粹的环境配置问题，但它是**当前最致命的一环**：它让 ②③ 全部表现为失败。

---

## 1. 逐阶段现状（修复前，以证据为准）

| 阶段 | 界面 | 磁盘产物 | 修复前真实可用性 | 阻断原因 |
|---|---|---|---|---|
| ① 检测 ANALYZE | ✅ | `report.json` 等 | **可用** | — |
| ② 问题 DIAGNOSE | ✅ | `diagnosis.json` | 结构可用，内容常空 | Core 只有 2 条 finding 规则（V4 已裁定②退场） |
| ③ 逆向分解 SEPARATE | ✅ | `stems/*.wav` | **❌ 必崩** | `DEPENDENCY_MISSING` + librosa/pandas ABI |
| ④ 结构 STRUCTURE | ✅ | `midi/*.mid` | **❌ 不可用** | basic-pitch / music21 未安装；无节拍/段落分析 |
| ⑤ 方案 PLAN | ✅ | `plans/*.json` | ⚠️ 空壳 | 无 AI 规划器（V4 已改为 ④修音/⑤复合） |
| ⑥ 成品 FINISH | ✅ | `versions/ai_*/` | 仅快速完成可用 | 无复检；`export_record` 互相覆盖 |
| **可逆性门禁** | ❌ | `roundtrip.json` | **❌ 不存在** | 只在 V4 文档与测试里，无产出代码 |

### 1.1 现场复现（本机，2026-10-05，修复前）

```text
$ node -e "require('.../runtime.js').resolveRuntime('basic-pitch')"
  → DEPENDENCY_MISSING 缺少必需的 Moodify 外部运行时：basic-pitch
$ node -e "...resolveRuntime('score')"
  → DEPENDENCY_MISSING

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
  子命令含 tuning ← 该子命令**不在本仓库 main 的 release_cli.py 里**
```

`moodify` 是以 editable 方式装到全局 site-packages 的，指向 `E:\moodify\moodify-core-package\src`。
后果：桌面壳调用的 Core **不是本仓库这份代码**。
`E:\moodify` 与 `E:\moodify-local` 的分叉点，正是那个未合并的 V4 提交。

### 1.3 24 个真实 case 的产物清点（修复前）

```text
深链完整（stems + midi + score）:   6 个
有 stems 无 midi:                   1 个
有 studio/plans/*.json:             0 个   ← ⑤ 方案从未被产物证明成功过
studio/roundtrip.json:              0 个   ← 可逆性门禁从未产出过
studio/versions/ai_*:               1 个（该 case 无 stems / 无 midi，走的是快速完成）
```

**`plans/` 与 `roundtrip.json` 全空**是本扫描最硬的事实：深度路径在真实使用中**从未走通过**。

---

## 2. 缺失模块清单（按层）+ 处置

### 2.1 环境层（P0，曾是最致命）

| 缺失 | 修复前 | 处置 |
|---|---|---|
| 运行时环境层 | 无任何 `.venv-*`；`MOODIFY_PYTHON` 未设 → 用全局 python | ✅ 新建 `.venv-audio` / `.venv-demucs` / `.venv-basic-pitch` |
| 依赖版本钉死 | 全局 numpy 2.4.6 与 pandas/sklearn ABI 不兼容 | ✅ 音频链**不再引入** sklearn/pandas/librosa |
| 运行时清单 | `RUNTIMES` 只有 basic-pitch / score | ✅ 新增 `audio` / `demucs`，`score` 复用转写运行时 |
| 能力可查询 | 无 | ✅ `probeRuntime` / `capabilities:probe` + 安装提示 |
| Core 解析隔离 | 可编辑安装指向 `E:\moodify` | ⚠️ **未改**（见 §5 未决） |

### 2.2 科学层（P1）— 已补齐

| 缺失模块 | 现状 | 补齐方式 |
|---|---|---|
| **真实源分离** | 只有 DSP 中置估计 + HPSS | ✅ `model_separate.py` → Demucs htdemucs（MIT），四轨 |
| **快速分离可用性** | librosa 导入链必崩 | ✅ `dsp_separate.py` 用 scipy 中值滤波自实现 HPSS，零重依赖 |
| **音频 → MIDI** | 无（未安装） | ✅ `.venv-basic-pitch`，实测 30s → MIDI 29s |
| **节拍 / BPM** | 无 | ✅ `structure.py`：自相关 + 倍频消歧（实测 127.84 BPM 正确） |
| **段落边界** | 无（Core 只有数据类型，无实现） | ✅ `structure.py`：自相似矩阵 + checkerboard novelty（实测 8 段） |
| **可逆性验证** | 只在文档/测试里 | ✅ `roundtrip.py` → `studio/roundtrip.json`，按划分验、带控制组 |
| MIDI 清理 / 量化 | 无 | ⚠️ 未做（见 §5） |
| 调性 / 和弦 | 无 | ⚠️ 未做（见 §5） |
| 完整诊断规则集 | Core 18 参数引擎够不到 | ⚠️ 维持 `HUMAN_DECISION_REQUIRED` |

### 2.3 闭环层（P1）— **已合并**

`origin/codex/studio-v4-latest` = `d6d203b5`（2026-10-05，227 files，+22k 行）已合入
`studio-v4-science`，并解决 3 处冲突（`main.js` ×2、`package.json`、`CANON_CHANGELOG.md`）：

| 模块 | 作用 |
|---|---|
| `src/orchestrator.js` | 完成会话调度循环（每轮重新推导，同一步只试一次） |
| `src/session.js` | 内部阶段 → 用户相位的投影 + 阻断原因分类 |
| `src/tuning.js` | ④修音 / ⑤复合 的**成对 A/B 产物层** + ⑦选定三出口账本 |
| `src/recheck.js` | ⑥复检：原版/A/B 三份 `report.json` 逐指标对齐表 |
| `src/keepsake.js` | 完成时刻留存（非权威表现层） |
| `src/history-sync/` | 个人历史同步（含 Supabase 迁移 + RLS 测试） |
| `core/tuning.py` | Core 侧配对渲染（MIP-0002） |
| `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md` | 521 行流程契约 |

**合并时发现并修掉的既有缺陷**：V4 的 `main.js` 引用了 `VENVS` / `pyExe` 两个**从未定义**的
标识符（`separateStems` / `transcribeMidi` / `convertScore` 三处）——那是 V3 遗留，任何一次
真实调用都会 `ReferenceError`。已统一改走 `runtime.js` 的解析入口。

---

## 3. 可补齐的成熟开源项目（GitHub）

选型遵守 `docs/canon/TECHNOLOGY_PRINCIPLES.md`：`existing > standard library > mature OSS > custom`。

| 缺口 | 项目 | 许可 | 本机状态 | 采纳 |
|---|---|---|---|---|
| 真实 4 轨分离 | [adefossez/demucs](https://github.com/adefossez/demucs)（`htdemucs`） | MIT | ✅ 实测 CPU RTF 2.2–3.6× | **已引入**（外部运行时） |
| 音频 → MIDI | [spotify/basic-pitch](https://github.com/spotify/basic-pitch) | Apache-2.0 | ✅ 实测 30s→MIDI 29s | **已引入** |
| MIDI → 曲谱 | [cuthbertLab/music21](https://github.com/cuthbertLab/music21) | BSD-3 | ✅ 实测通过 | **已引入** |
| 节拍/结构 | [librosa](https://github.com/librosa/librosa) | ISC | 已装但**刻意不用**（见下） | 用 scipy 自实现 |
| 更高质量分离 | [lucidrains/BS-RoFormer](https://github.com/lucidrains/BS-RoFormer) | MIT（权重另议） | 未装 | 后续「精分离」档（待裁决） |
| 段落检测 | [taejunkim/all-in-one](https://github.com/taejunkim/all-in-one) | MIT | 未装 | 备选；当前用 scipy 自相似矩阵 |
| 曲谱渲染 | [opensheetmusicdisplay](https://github.com/opensheetmusicdisplay/opensheetmusicdisplay) | BSD-3 | 已 vendor 在仓库内 | 保持不变 |

**为什么刻意不用 librosa 做 HPSS**：`librosa.decompose` 的导入链会拉进 sklearn → pandas，
而 pandas 的 C-ABI 在 numpy 2.x 上会崩（这正是本故障的根因）。HPSS 本身只需要中值滤波，
`scipy.ndimage` 就够。**把一段能力从「依赖 3 个易碎的重库」变成「依赖 1 个稳定库」，
是本次修复里价值最高的一处。**

### 引入方式（关于「把代码引入我的项目」）

这些项目**不以源码 vendoring 方式拷进仓库**，而是**声明为受版本约束的外部运行时**，
由 `moodify-desktop/src/runtime.js` 解析、由 `main.js` 编排 —— 这正是仓库**既有**的约定。

| 运行时 | venv | 上游 | 许可 | 安装 |
|---|---|---|---|---|
| `audio` | `.venv-audio` | 无（numpy+scipy+soundfile） | — | `requirements-audio.txt` |
| `demucs` | `.venv-demucs` | adefossez/demucs | MIT | `requirements-demucs.txt` |
| `basic-pitch` | `.venv-basic-pitch` | spotify/basic-pitch + cuthbertLab/music21 | Apache-2.0 / BSD-3 | `requirements-transcribe.txt` |

理由：复制 Demucs 源码进仓库 = 把 3 万行上游代码变成我们的维护责任，且与「One Core」冲突；
声明为外部运行时 = 上游可独立升级，我们只维护**接口与诚实边界**。

---

## 4. 本次已实施的补齐

### 4.1 新增模块

| 文件 | 作用 | 关键诚实边界 |
|---|---|---|
| `moodify-desktop/scripts/model_separate.py` | Demucs 四轨分离 | `engine_grade = MODEL_SEPARATION_NOT_VERIFIED_AGAINST_ORIGINAL_STEMS`：原分轨不可知 |
| `moodify-desktop/scripts/roundtrip.py` | 可逆性验证 → `studio/roundtrip.json` | **`passed` 只表示重建一致，不表示分轨质量**；产物自带平凡控制组证明这一点 |
| `moodify-desktop/scripts/structure.py` | 速度/拍点/段落/能量 → `studio/structure.json` | 段落只有**位置编号**，没有主歌/副歌标签；`judgment_boundary` 明写 |
| `moodify-desktop/scripts/requirements-{audio,demucs,transcribe}.txt` | 三个运行时的钉死依赖 + 安装说明 | — |
| `moodify-desktop/scripts/test-deep-chain.js` | **真的跑那条链**的回归测试（20 项） | 合成 fixture，不引入私有音频 |

### 4.2 修改

| 文件 | 改动 |
|---|---|
| `scripts/dsp_separate.py` | 去掉 librosa 依赖，scipy 中值滤波自实现 HPSS；manifest 新增 `partition` 声明 |
| `src/runtime.js` | 新增 `audio` / `demucs` 运行时；`probeRuntime` / `probeAllRuntimes` / `installHint`；`score` 复用转写运行时 |
| `src/main.js` | 修掉 `VENVS`/`pyExe` 未定义；`separateStems(caseDir, mode)` 双引擎；新增 `checkRoundtrip` / `structureAnalysis` / `sessionSeparate`；4 个新 IPC |
| `src/pipeline.js` | `stems.grade` 改为**来自 manifest**（不再写死预览级）；`ctx.structure`；可逆性块带 null 深度/划分/解释；能力清单诚实拆分 |
| `src/preload.js` | 暴露新桥接（stems roundtrip / engine / structure / capabilities probe） |
| `renderer/index.html` + `app.js` | 引擎下拉（自动/模型/快速）、可逆性验证按钮、降级如实标注 |
| `scripts/test-pipeline.js` | 覆盖新的能力登记（含「壳侧 vs Core 侧可逆性不得互相顶替」） |
| `scripts/test-main-ipc.js` | 收尾显式 `process.exit(0)`——此前断言全过后进程**永不退出**，`npm test` 会挂起并攒孤儿进程 |
| `package.json` | 测试链纳入 `test-deep-chain.js` |

### 4.3 实测证据（本机，2026-10-05）

```text
快速分离（DSP，387s 全曲）      112s，四轨 wav，无崩溃（修复前必崩）
模型分离（Demucs，30s 片段）     84s ≈ 2.4× 实时，四轨 drums/bass/other/vocals
可逆性 · DSP 划分               null −74.1 dB，correlation 1.0000，阈值 −40 → passed
可逆性 · Demucs 四轨            null −32.7 dB，correlation 0.9997，scale 1.001，阈值 −25 → passed
结构分析（387s 全曲）            9.4s：BPM 127.84（倍频已消歧）、824 拍、8 段
音频 → MIDI（30s）              29.3s（需 PYTHONUTF8=1，否则 GBK 崩在 ✨ 字符上）
MIDI → MusicXML                 通过
桌面测试全量（npm test）          exit 0，0 failed
                                 check-contracts（DOM 183 · 桥接 62 · IPC 63）
                                 test-pipeline 63 · test-recheck 9 · test-session 38
                                 test-keepsake 23 · test-sync 25 · test-orchestrator 20
                                 test-main-ipc 67 · test-studio 21 · test-runtime（全部）
                                 test-deep-chain 20（新增，真的跑那条链）
```

### 4.4 修复过程中被测试抓出的**我自己的**错误（如实记录）

| 错误 | 症状 | 纠正 |
|---|---|---|
| 把两套重叠划分相加 | DSP 四轨相加 = 2×原版 → 报 null −16.9 dB「不可逆」假象 | 引擎在 manifest 声明 `partition`；验证按划分进行 |
| 不比较采样率 | 模型轨 44.1 kHz vs 原版 48 kHz → correlation 0.004 的假失败 | `roundtrip.py` 先对齐采样率再比较 |
| 单一阈值卡两种引擎 | Demucs 正常残差 −33 dB 被 −40 dB 判成不可逆 | 阈值按引擎取默认值并写明理由 |
| RMS 从 STFT 幅度反推 | 电平低报十几 dB（真实 −15 dBFS 被算成 −61 dBFS） | 改用时域分块 RMS，dBFS 以满幅 1.0 为参考 |

**这四条都是「看起来像严肃测量结论」的错数**——比没有数字更糟。它们全部由
`test-deep-chain.js` 与真实音频复现抓出，这也是为什么这个测试必须真的跑那条链。

### 4.5 差点发生的事故：`.venv-audio` / `.venv-demucs` 不在任何忽略规则里

`.gitignore` 只逐条列了 `/.venv-core/`、`/.venv-score/`、`.venv-basic-pitch/`。
本次新建的两个运行时目录**不被任何规则匹配**，`git status` 直接把它们报成未跟踪：

```text
?? .venv-audio/      209 MB
?? .venv-demucs/      22 MB
```

即一次 `git add -A` 会提交 231 MB 的解释器。已改为通配 `/.venv-*/` 一次性覆盖整个命名空间
（并保留原有逐条规则）。验证方式不是读规则，而是模拟真实的粗心操作：

```text
$ git add -An | Select-String venv      → 无输出（无法被 add 进去）
$ git check-ignore -v .venv-probe-test  → .gitignore:60:/.venv-*/   ✓
```

这与仓库历史上「`*.png` 静默吞掉品牌资产」是同一类故障：**逐条列举跟不上新增目录**。
`AGENTS.md` 已经要求「新增任何非 `.py` 文件前先 `git check-ignore -v`」，
本次是这个要求的第一次真正生效。

---

## 5. 未完成 / 需人类裁决

1. **Core 的可编辑安装指向 `E:\moodify`**，桌面跑的不是本仓库这份 Core。这不是本任务的
   授权范围（属于环境与发布配置），但它是**下一个会咬人的问题**：
   `release_cli.py` 已出现版本漂移（`tuning` 子命令只存在于其中一个 checkout）。
2. **逐轨修音 / 多轨复合**（`stem-tuning` / `multi-stem-compose`）Core 仍无能力。
   可逆性门禁现在能产出并通过，但 ④修音 依旧被 `TUNABLE_CORE_NOT_AVAILABLE` 如实拒绝。
   → 见 `protocol/mips/MIP-0002-stem-tuning-loop.md`。
3. **「精分离」档**是否上 BS-RoFormer（质量更高、依赖更重）——待裁决。
4. **MIDI 清理/量化/合并、调性/和弦**未做：Basic Pitch 输出是原始转写，未做量化与合并，
   也没有调性估计。这几项是 ④修音 的输入质量前提。
5. **`apps/android` 已按 V4 裁决删除**（`CANON_CHANGE = YES`，记录在 `CANON_CHANGELOG.md`）。

---

## 6. 本次变更的性质

```text
CANON_CHANGE = YES
```

原因：合并 `codex/studio-v4-latest` 带入 **Creator 侧流程变更**（V3 六阶段 →
V4 八阶段：检测 → 逆向分解 → 结构 → 修音 → 复合 → 复检 → 选定 → 导出），
②问题 退场、`AGENTS.md` 产品方向条款更新、新增身份/历史同步（`deployment/supabase/`）。

- **why / evidence / migration / rollback**：见 `CANON_CHANGELOG.md` 的两条既有记录
  （V4 流程、Android 收敛）；本次合并**未新增** Canon 决策，只是把已记录的决策合入主线。
- **受影响权威文件**：`AGENTS.md`、`docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`、
  `CANON_CHANGELOG.md`、`PRODUCT_DEFINITION_V3.md`、`AUTHORITY_ORDER.md`、`REPOSITORY_STATUS.md`。
- **科学层新增不以 Canon 变更方式生效**：新模块是**执行能力**（AI 执行权范围内），
  不改变产品定义；它们的诚实边界写在产物里随数据流转。
