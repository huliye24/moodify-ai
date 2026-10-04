# ECOSYSTEM 001 — Capability Ecosystem Map 执行报告

> **任务：** ECOSYSTEM 001 — Moodify Capability Ecosystem Map
> **分支：** `codex/ecosystem-001-capability-map`（基于 `main` `01edc902`）
> **提交：** `347f6ef88acb6b2d7f591e9136fb84deb0cffec0`
> **日期：** 2026-10-04
> **约束：** `Code Changes: NOT ALLOWED` · `Primary Output: Documentation only`
> **交付物：** `docs/ecosystem/` 下三份文档（本报告不复述其内容）

---

## 1. 方法与顺序

任务书 §4 要求**先读仓库再外部调研**。这个顺序不是形式 —— 它在本轮纠正了两个错误
假设，如果顺序反了，这两条错误会直接写进战略文档。

```text
① 只读仓库审计（子代理，全仓扫描）
        ↓  先确定「我们到底有什么」
② 外部调研（官方仓库 / 文档 / 标准组织优先）
        ↓  再确定「外面有什么」
③ 两者对齐后写 BUILD / INTEGRATE / DELEGATE
```

### 审计纠正的两处

| 我原本的假设 | 审计事实 |
| --- | --- |
| 仓库没有云端分轨集成 | **有** —— `moodify/stems/client.py` 的 `LalalClient`，10-stem 目录，但 `CONNECTED_UNTESTED` |
| `moodify/lyric_align` 存在 | **main 上不存在**，歌词对齐 ABSENT |

### 审计给出的一条方法论结论

**文件存在 ≠ 能力存在。** 两处硬证据：

```text
auditory/structure.py:41   tempo_bpm: float | None = None     ← 声明
auditory/structure.py:75   （序列化）                          ← 全仓库仅此两处
                           从未被赋值

grep "Section(" / "StructureContext("   →  0 个构造点
grep "beat_track"                       →  0 处
```

`StructureContext` 有类型、有阈值常量、有查询函数 —— **唯独没有任何东西构造它。**

更值得警惕的是 `auditory/inventory.py`：**它本身就是过时的**，分类表里列着
`capability_registry`、`adapters`、`ports`、`storage` 等在本分支上不存在的模块。
**如果照它的字面去建能力地图，产出的就是虚构。**

---

## 2. 外部调研：论点被 2026 年的现实印证

任务书的中心论点是「模型会变，能力要留下」。调研发现，**三个最显眼的候选引擎正好
呈现了「直接耦合就会坏掉」的形态**：

| 引擎 | 2026 实况 | 若直接耦合的后果 |
| --- | --- | --- |
| Demucs | Meta 原 repo 进入有限维护；维护线是作者的 fork `adefossez/demucs` v4.1.0（2026-07），**推理已移除 torchaudio**，权重迁至 HF safetensors | repo 级依赖会在迁移时断掉 |
| madmom | PyPI 发布约 8 年未更新，Cython 扩展在现代 Python/numpy 上装不上；**预训练权重是 CC BY-NC-SA 4.0（禁商用）** | 「pip install 就能用」既装不上、也不可商用 |
| MSAF | 仍在更新，但有 2026 项目发现它**在现代 SciPy 上导入失败** | 章节检测会在某次依赖升级后静默失效 |

**这三条同时是支持本架构的证据，而不是反对采纳 provider 的理由。** 它们说明的
不是「别用外部引擎」，而是「**别把外部引擎焊进核心**」—— 每一条都指向同一个答案：

```text
       模型会换                能力留下
  ┌──────────────────────┐  ┌──────────────────────┐
  │ demucs → bs-roformer │  │    stem.separate     │
  │ basic-pitch → 下一个 │⇒ │   midi.transcribe    │
  │ whisper → 下一个     │  │     lyrics.align     │
  └──────────────────────┘  └──────────────────────┘
```

### 三条直接影响判断的发现

**① 许可证陷阱：代码许可 ≠ 权重许可。** madmom 的预训练权重、Open-Unmix 的 UMXL
权重都是 **CC BY-NC-SA（非商用）**；BS-RoFormer 的许可不明。只声明 `license: MIT`
的 manifest 不是不完整，是**主动误导**。这条直接写进了 manifest 草案 —— `license`
被拆成 `code` 与 `weights` 两栏，外加 `commercial_use` / `redistribution` 显式枚举。

**② MCP 音乐生态已经很拥挤，DAW 控制从「也许自建」直接改判 DELEGATE。**
调研找到 REAPER-MCP（~181 工具）、Waveform-MCP（150+）、Ableton（两份独立实现）、
Csound、SuperCollider，活跃到 2026，其中一份已跟到 MCP 协议版 `2026-07-28`。
**自建 DAW 控制 = 从头造一个别人已经造了好几遍的东西。**

反过来看更重要：**那个生态里没有证据、溯源、测量权威、会累积状态的项目** —— 那才
是 Moodify 的位置，也印证了「可被 MCP 调用」是最便宜的发行渠道。

**③ 标准版的取舍有了依据。** MusicXML 是 W3C CG 标准（2015 起），最新 4.0（2021-06），
270+ 程序支持，「成熟但难演进」—— **正是应该依赖的那种无聊而稳定的东西**。
AAF 是现行标准但 Reaper 至今无原生支持、且不携带路由/配色/会话结构 → DEFER。

---

## 3. 核心结论

**Moodify 的 CANONICAL 强项集中在「信任层」，缺口集中在「内容引擎」。**

| 状态 | 数量 | 分布 |
| --- | ---: | --- |
| CANONICAL | 7 | decode · auditory 分析 · 响度/真峰/立体声/频谱 · 验证 · 溯源与证据 · 云节点队列 · 本地执行 |
| IMPLEMENTED_NOT_CANONICAL | 6 | MIDI · 曲谱 · A/B · 削波峰修复 · 导出 · Agent 集成 |
| PARTIAL | 5 | 音高检测 · 节奏 · 结构 · 元数据 · 能力注册表 |
| EXPERIMENTAL | 3 | 分离 · 混音 · 母带 |
| LEGACY | 1 | `v01_*` 预设链 |
| ABSENT | 8+ | 时值校正 · 和声 · 乐器识别 · 歌词 · 降噪/修复 · DAW · 插件宿主 · Project Model |

**这个分布是有利的**：策略要求的正是「在已经强的地方加倍」。

### 反向价值原则（§32 的答案）

> 模型越强 → 单个输出越不可自证可信 → **证据 / 验证 / 溯源的价值上升**。

| 层 | 随模型变强而增值？ | 裁决 |
| --- | --- | --- |
| Project Model · 能力 ID · 契约 · 路由 · 协议 · Graph · 证据 · 验证 · SDK | **是** | **OWN** |
| GUI | 只间接 | 维护 |
| **DSP 模型** | **反向贬值** | **绝不自有** |

这与 HOTFIX 000 的教训同构 —— 一个「貌似合理但错误」的数字比一次响亮失败更危险。
放到生态尺度：**一个自信而错误的分轨，不是靠换个更好的供应商能发现的，是靠验证层。**

---

## 4. 五个 P0 缺口

1. **Provider 抽象 + 能力注册表** —— 今天只有若干专门 registry，加一个**过时的**
   inventory。没有它，每个集成都是手写一次性代码，§9 反锁定规则无从执行。
2. **节奏 / 结构理解** —— 类型有、生产者零（见 §1）。Agent 无法对感知不到段落和
   速度的歌曲做制作决策。这是相对战略需求**最大的能力缺口**。
3. **Project Model 不在 `main`** —— 在 `codex/project-model-001`（`4aba0f53`）；
   `main` 上 `moodify/project/` 只有陈旧 `.pyc`。**「Projects accumulate state」
   目前是空的。**
4. **转写域最弱** —— MIDI/曲谱 IMPLEMENTED_NOT_CANONICAL 且只从桌面壳外部调用；
   歌词、和弦 ABSENT。
5. **`stem.separate` 三条半路径无契约** —— LALAL 客户端（`CONNECTED_UNTESTED`）、
   自述预览级的 DSP 脚本、**仅声明未下载**的 Demucs extra。

---

## 5. 交付物

```text
docs/ecosystem/MOODIFY_CAPABILITY_ECOSYSTEM_MAP_001.md      704 行 · 16 节
docs/ecosystem/MOODIFY_CAPABILITY_MATRIX_001.md             203 行 · 45 能力行
docs/ecosystem/MOODIFY_PROVIDER_MANIFEST_DRAFT_001.md       180 行 · 标 DRAFT
```

三者均显式声明 **"Strategy input — not runtime truth"**，与仓库既有的
R6/R10 纪律一致（如 `MOODIFY_PROFESSIONAL_FINISHING_V1.md` 的 TARGET 声明）。

---

## 6. 验证（§27 / §35 负向要求）

```text
DOCS_ONLY = YES
```

已逐项核对：

| 项 | 结果 |
| --- | --- |
| `git status` 除 `docs/ecosystem/` 外无改动 | ✅ |
| `pyproject.toml` / `requirements*.txt` / `package.json` 未动 | ✅ |
| `Dockerfile` / `docker-compose.yml` 未动 | ✅ |
| 无 pip / npm install | ✅ |
| 无 vendored 二进制 | ✅ |
| 无权重下载 | ✅ |
| 新增 `.md` 未被 `.gitignore` 吞掉（check-ignore 逐个确认） | ✅ |

---

## 7. 风险

1. **许可证陷阱（最高）** —— 代码宽松 ≠ 权重宽松。任何 P0 provider 采纳前必须
   **逐模型核权重许可**，并确认 `commercial_use`。
2. **单一来源** —— LALAL.AI 是目前唯一的云分轨。已标 `SINGLE_SOURCE_ACCEPTED`
   并写明风险，**没有让它当默认隐身**。
3. **维护脆弱性** —— Demucs / madmom / MSAF 三例说明这个领域的引擎会烂。这要求
   §9 的反锁定规则必须真正执行，尤其：**任何可选 provider 全卸载后，项目仍能
   打开、验证、导出。** 这条是承重的 —— 如果丢一个 provider 就能让项目报废，
   抽象就失败了。
4. **文档化能力与代码漂移** —— `inventory.py` 是活证据。本能力地图也会腐烂，
   除非有东西持续校验它（这正是缺口 #1 的一部分理由）。
5. **DAW/标准行未经 Moodify 实测** —— 矩阵中这些行是**规划输入，不是支持声明**，
   文档内已显式标注；商业定价数字各来源冲突，决策前须重新核实。

---

## 8. 下一步建议（只推荐一个，未启动）

### Capability Registry + 稳定 capability ID + 失败词汇表

**理由：** 它是本报告中其余每一个行动项的**契约层前提**。今天没有任何地方可以声明
「`stem.separate` 存在、这些 provider 实现它、这些是它的失败码」。

**为什么是它而不是别的：**

- 纯 Core、**无 GPU、无许可证风险、可完全离线**完成；
- 与 §3 的裁决一致（能力 ID 与注册表是「随模型变强而增值」的层）；
- 它让 §9 的反锁定规则**可执行**，而不是停留在文档里的原则；
- 它也顺带修掉缺口 #1 中那个**过时的 `inventory.py`**。

**明确不推荐先做** `stem.separate` 或 `structure.analyze`：前者是拥挤、吃 GPU、
许可证一团乱的方向；后者需要先有能注册它的地方。

---

## 9. 提交

```text
347f6ef88acb6b2d7f591e9136fb84deb0cffec0
docs(ecosystem): add the capability ecosystem map 001
```

分支 `codex/ecosystem-001-capability-map`，基于 `main` `01edc902`，**已提交未推送**，
工作区干净。

### 会话内其他未推送分支（供交接参考）

```text
codex/project-model-001           4aba0f53   TASK 001 Project Model 0.1
codex/hotfix-000-measurement-...  ca0c4805 → f9c7e348   HOTFIX 000（含报告）
```

**本报告把 Project Model 列为 P0 累积层，但它尚未进入 `main`。** 生态地图中
「Projects accumulate state」这一句，取决于上述分支是否合并。

---

## 10. 外部事实的来源与置信度

完整来源清单见 `MOODIFY_CAPABILITY_ECOSYSTEM_MAP_001.md` 附录。要点：

- 采信优先级：**标准组织 / 官方仓库 / 厂商文档**。社区来源（论坛）**仅用于实现
  经验**，凡引用处均已在正文标注。
- **置信度说明：** 商业定价各来源互相冲突，须重新核实；Moises 的公开 API 状态
  在来源之间**互相矛盾**，标记为未验证；DAW 能力行是规划输入，非 Moodify 实测。
- 所有外部事实标注采集日期 **2026-10-04**。该领域的引擎生命周期以月计（见 §2），
  **本报告的外部部分有明确保质期。**
