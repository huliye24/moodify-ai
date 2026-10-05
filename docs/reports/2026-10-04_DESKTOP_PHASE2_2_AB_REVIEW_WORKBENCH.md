# Moodify Desktop Phase 2.2 — A/B 审听与证据工作台（实现报告）

**Date:** 2026-10-04
**Status:** IMPLEMENTED — 交互人工验收待主控执行（§8）
**Owner / final acceptance:** Codex（主控）
**CANON_CHANGE:** NO — 未改生产流程、判断权、声音契约与任何门禁；只改 REVIEW 的呈现与只读数据面
**MIP_REQUIRED:** NO
**任务包:** [`docs/plan/2026-10-04_DESKTOP_PHASE2_2_AB_REVIEW_WORKSPACE.md`](../plan/2026-10-04_DESKTOP_PHASE2_2_AB_REVIEW_WORKSPACE.md)
**前置:** [`2026-10-04_DESKTOP_ONE_CLICK_PHASE2_IMPLEMENTATION.md`](2026-10-04_DESKTOP_ONE_CLICK_PHASE2_IMPLEMENTATION.md) ·
[`2026-10-04_DESKTOP_ONE_CLICK_PHASE2_1_MODE_SWITCH.md`](2026-10-04_DESKTOP_ONE_CLICK_PHASE2_1_MODE_SWITCH.md)

---

## 1. 修改文件清单

**Desktop（呈现层）**
- `renderer/index.html`：REVIEW 区重建为审听工作台（试听身份条 + 两个候选标签 + 候选页固定结构：
  身份卡 / 波形 / 频谱 / 指标卡 / 图表 / 处理链 / 折叠复检表 / 动作 / 导出），移除旧的
  `#tuning-track`、`#tuning-actions`、`#tuning-recheck-body`
- `renderer/app.js`：新增工作台状态与渲染（`review`、`initReview`、`refreshReview`、
  `renderReviewChrome/Page/Spectra/Metrics/Charts/Chain/Table/Actions`），单 transport
  （`reviewLoadSide` / `reviewDecodeSide` / `reviewMountTransport` / `reviewSetZoom` / `applyReviewZoom`），
  选择走既有 `tuning:decision`（`nextDecisionRequestId` 支持改选），导出沿用既有门禁
- `renderer/style.css`：工作台样式 + 试听源固定色语义（原版=中性灰 / A=蓝紫 / B=橙色）

**Desktop（只读数据面）**
- `src/main.js`：新增 `tuning:evidence`（按 pair 侧返回报告 / 频谱 / 图表 / 指标卡 / 处理链，
  路径全部由 recheck + pair 产物推导并守卫）与 `tuning:charts`（按侧调用 Core 图表导出器）；
  新增 `REVIEW_CARD_METRICS`（12 张固定卡，`digits` 写死 → A/B 同精度）
- `src/preload.js`：新增 `tuningEvidence` / `tuningCharts` 两个桥接

**Core（一个真实崩溃的修复，非新能力）**
- `src/moodify/ui/report_window.py`：`select_chart_measurements` 跳过**无数值**的测量
  （真实候选报告里存在 `value: null` 的指标，旧代码 `float(None)` 直接崩溃）
- `tests/ui/test_report_window.py`：新增「不可计算的测量被跳过、不补零」测试

**测试**
- `scripts/test-main-ipc.js`：§10 工作台数据守恒与守卫（7 条，真实 Core）、§11 renderer 契约（7 条）

## 2. 新 REVIEW 信息架构

```text
[sticky] 正在试听 <原版|A（保守）|B（充分）>   当前页面：<A|B>   [原版][A·保守][B·充分]  ▶ 时间  加载态
[A · 保守] [B · 充分]                      ← 只有两个候选标签，没有第三个「原版详情」页
  ├ 身份卡：A/B · 快速完成（仅立体声） · UNCALIBRATED_ENGINEERING_DEFAULT · 「机器已处理并测量；是否更好由你试听决定」
  ├ 波形（一个 transport、三个音源、同一时间位置、缩放保留）
  ├ 频谱：原版 | 当前候选（并排、同显示尺寸、图例常驻；缺图就写缺）
  ├ 关键指标 12 张卡：原版 → 候选、Δ、单位、指标 id（Δ 只表方向，不出评分）
  ├ 检测图表：原版 | 当前候选（按需由 Core 导出器生成，按侧落盘）
  ├ 实际处理链（只读）：EQ → Compressor → [Stereo] → Limiter + Mix Graph digest + Core 硬门禁
  ├ 完整复检表（默认折叠，按当前候选过滤：仅看有变化 / 全部 / 不可对齐）
  └ [选择 A（保守）] [保留原版] · 当前选择：… · 导出对象与按钮
```

## 3. 播放源、标签页与播放位置如何同步

- **一个** WaveSurfer 实例（`review.ws`）挂在 `#rv-wave`；同一时刻只加载一个音源，
  没有三个 AudioContext、没有三个播放头。
- `review.tab`（当前页面）与 `review.playing`（当前播放源）是**两个**状态，界面同时显示，
  页签永不冒充播放源；页签上有 `当前试听 / 已选择 / 不可用` 徽章，音源按钮用
  「填充色 + 圆点 + 文字」三重表达并带 `aria-current`。
- 切换音源：先取 `review.ws.getCurrentTime()` → `reviewDecodeSide()`（最多缓存 2 条已解码 buffer）
  → `loadDecodedBuffer` → `seekTo(原位置)` → 重新应用同一缩放（`applyReviewZoom`）；
  原先在播放则继续播放。**位置绝不在切换时被归零。**
- 加载失败：显示 `加载B（充分）失败：<真实原因>`，**保持上一个可播放源**，不翻转播放身份
  （身份只在加载成功之后赋值）。加载中显示 `正在加载…`。
- 换世界 / 换 pair 时用 token + `caseDir`/`pairId` 双重守卫丢弃过期结果。

## 4. A/B 每一块证据来自哪个真实产物

| 视图 | 来源 |
|---|---|
| 原版 / A / B 音频 | `tuning:audio`（原版 = case 源；A/B = `<pair>/A|B/mix.wav`） |
| 对齐表（折叠层与指标卡） | `tuning:recheck` → `recheck.js` 从三份 Core `report.json` 摊出的对齐结果 |
| 指标卡的值/Δ/单位 | 对齐表本身（`digits` 由 main 固定 → A/B 同精度）；缺项写「不可对齐」并带 recheck 的真实原因 |
| 频谱 | 候选**自己**那次复检报告的 `scan/spectrum_log.png` / `spectrum_linear.png`（Core 扫描产物） |
| 检测图表 | 按侧调用 Core `moodify.ui.chart_export <该侧 report>` → `charts/chart_{bands,levels_db,stereo_ratios}.png` |
| 处理链、参数、digest、硬门禁 | `<pair>/<side>/plan.json` 与 `evidence.json`（Core 写的，只读展开） |
| 原版对照列 | `recheck.original`（case 自己的 report）——**绝不用原版图冒充候选图** |

**关于坐标范围（如实说明）：** 频谱与图表由 Core 的同一导出器、同一参数分别从各自 report 生成；
本层只保证「同一导出器 + 同一显示尺寸 + 图例常驻」，**不重绘、不二次缩放**——重绘就会造出第二套
分析/绘图权威（任务书 §5.5/§7 明令禁止）。若需要跨侧严格同轴的图，属于 Core 侧的导出参数需求，
记为后续工作（§9）。

## 5. 新增只读 IPC 与路径守卫

```text
tuning:evidence(caseDir, pairId)       → { ok, pair_id, mode, sides{ORIGINAL,A,B}, reports{original,A,B} }
tuning:charts(caseDir, pairId, side)   → Core 图表导出器按该侧 report 生成并返回路径
```

守卫（全部在 main 侧，渲染层递不了任意绝对路径）：

1. `caseDir` 必须经 `resolveGuardedCase`（落在 CASES_ROOT 内且含 case.json）；
2. `pairId` 必须真实存在于 `<case>/studio/tuning/`；
3. 报告路径取自该 pair 的 `recheck.json`，且 `realpath` 必须落在 **case 内**，否则
   `EVIDENCE_OUTSIDE_CASE`；
4. `side ∈ {ORIGINAL, A, B}`，否则 `BAD_SIDE`；
5. 只读：不重跑分析、不算新测量、不改 evidence；唯一写入是 Core 图表导出器把 PNG 落在
   **该报告自己的目录下**（与既有 ①检测 图表页同一机制）；
6. 二进制大图与音频**不进入任何新状态文件**（渲染层按路径引用 `file://`）。

## 6. 数据守恒与失败测试结果（真实 Core，合成音频）

| 测试 | 结论 |
|---|---|
| A 页只绑 A、B 页只绑 B | `evidence.reports.A/B/original` 与 `recheck.json` 引用逐字相同；A≠B 报告路径 |
| 音频守恒 | `tuning:audio` 三路字节 hash == `mix.wav` / case 源文件 hash；A≠B |
| 指标卡守恒 | 每张卡 ∈ alignable ∪ not_alignable；值/Δ 与对齐表逐字相同；缺项带真实原因 |
| 图表按侧 | A 的图落在 A 报告目录、原版的图落在原版目录，互不顶替 |
| 伪造 pair_id | `NO_SUCH_PAIR`，不读任何文件 |
| 越界 recheck 引用 | `EVIDENCE_OUTSIDE_CASE`（evidence 与 charts 都拒绝），且不产生新产物 |
| 缺 B 音频 | B 侧 `audio:false`（不可试听），`tuning:decision` 拒绝（`PAIR_NOT_COMPLETE`），导出保持锁定 |
| 改选 A→B→A | 三次都真的追加记录（新的 requestId），有效决定 = 最后一行，stage=CHOSEN |

真实歌曲（123.32 s / 48 kHz，副本 + 临时 cases-root，未触碰归档）排练输出：

```text
SESSION {"ok":true,"state":"REVIEW","stage":"RECHECKED"}
EVIDENCE ok: true | mode: FAST_STEREO_ONLY
 ORIGINAL audio=true spectra=2 charts(cached)=3 cards=12
 A       audio=true spectra=2 charts(cached)=0 cards=12 nodes=[eq,compressor,limiter]  gates=6/6
 B       audio=true spectra=2 charts(cached)=0 cards=12 nodes=[eq,compressor,stereo,limiter] gates=6/6
 CARD IDS IDENTICAL ACROSS PAGES: true          ← A/B 同指标、同精度，可公平比较
 示例卡：整体响度 -16.58 → A -17.03 (Δ-0.45 LUFS) / B -18.38 (Δ-1.80 LUFS)
 CHARTS A/B/ORIGINAL: 各 3 张，落在各自 report 目录
 ALIGNMENT {alignable:51, not_alignable:0, A_changed:38, B_changed:41}
 AUDIO sha[:16] 原版 c503af5c… / A e7d7099c… / B 96638405…（A≠B，且与 Core 端一致）
 ELAPSED 64s
```

## 7. 全部回归结果

```text
cd moodify-desktop && npm test
  → check-contracts ✓（DOM id 153 · 桥接 54 · IPC 53 · 事件 5 · 会话相位 5）
    test-pipeline 61/61 · test-recheck 9/9 · test-session 38/38
    test-orchestrator 20/20 · test-main-ipc 47/47（§10 工作台 7 条 + §11 契约 7 条）· test-studio 21/21
python scripts/check_repo_structure.py → OK
python -m ruff check moodify-core-package/src moodify-core-package/tests → All checks passed
python -m pytest tests/ui/test_report_window.py tests/test_tuning_pairs.py -q → 33 passed
```

**Core 崩溃修复（真实数据触发）：** 真实候选报告的 `measurements` 里存在 `value: null` 的指标，
`select_chart_measurements` 直接 `float(None)` 抛 `TypeError`，导致**任意含不可计算指标的歌曲
的图表页都打不开**（不限于候选页）。现在这类测量被跳过（不补零、不猜测），并新增测试钉住。

## 8. 人工验收截图（待主控执行）

任务书 §10 要求截图记录 A 页、B 页与三种试听源状态。本代理无图形界面与截图能力，
故**不虚构截图**；请按下列清单验收（步骤即任务书 §10）：

```text
1 进入 REVIEW：第一眼能看到「正在试听 X」与「当前页面 Y」
2 点 A 标签：页面只出现 A 与原版的频谱/指标/图表/处理链（无 B 列）
3 播放到中段，在 原版/A/B 间切换：时间位置不归零，页签与播放身份分别正确
4 A 页看到原版 vs A 的四块证据；B 页同结构、同尺度
5 展开完整表：A 页无 B 列，B 页无 A 列；筛选「仅看有变化/全部/不可对齐」可用
6 选择 A → 切到 B 试听 → 当前选择仍显示 A；改选 B、再改选原版：三次都追加成功
7 导出区显示最终选择与文件身份；未选定时导出保持锁定
```

临时排练目录（`%TEMP%\phase22-accept-*`）已清理，仓库与用户归档无残留。

## 9. HUMAN_DECISION_REQUIRED

1. **跨侧严格同轴的图**：目前频谱/图表由 Core 各自导出（同一导出器、同一显示尺寸），
   坐标轴由 Core 决定。若要求原版/候选**像素级同轴**，需要 Core 侧导出参数（例如共用同一
   y 轴范围）——这是新的 Core 契约面，未自行扩大范围。
2. **响度匹配试听**：本阶段按任务书 §4.3 不做 renderer 私有归一化；若要做「显式、可见、
   可关闭且有证据」的 gain-match，需要一个独立任务与 Core 侧依据。
3. **波形叠加原版轮廓**（§5.2 的可选开关）：本轮未做。做的话需要保证同时间轴、同幅度尺度
   且不各自自动缩放，属独立的小任务。
