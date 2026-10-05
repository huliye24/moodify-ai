# Moodify Desktop Phase 2.3 — 完成时刻与作品留存（实现报告）

**Date:** 2026-10-04
**Status:** IMPLEMENTED — 完成层/安静聆听/作品卡的**截图与人工验收待主控执行**（§7）
**Owner / final acceptance:** Codex（主控）
**CANON_CHANGE:** NO — 未改声音流程、选择权威、导出门禁与任何 Core 契约
**MIP_REQUIRED:** NO
**任务包:** [`docs/plan/2026-10-04_DESKTOP_PHASE2_3_FINISHING_POLISH.md`](../plan/2026-10-04_DESKTOP_PHASE2_3_FINISHING_POLISH.md)
**前置:** [`2026-10-04_DESKTOP_PHASE2_2_AB_REVIEW_WORKBENCH.md`](2026-10-04_DESKTOP_PHASE2_2_AB_REVIEW_WORKBENCH.md)（REVIEW 工作台，已实现）

---

## 1. 修改文件清单

**留存层（新的非权威产物）**
- `src/keepsake.js`（新）：`<case>/studio/keepsake.json` 的读写（临时文件 + 原子替换）、
  一句话边界（280 码位 / 4 行）、波形印记归一化（固定 600 桶、限幅、3 位小数）、
  文件名清洗、**作品卡模型**（只有标题/选择/日期/文字）
- `src/main.js`：`completionState()`（完成状态投影：由 ⑦ 准入 + 该侧音频存在推导）与
  5 个 IPC：`keepsake:state` / `keepsake:sync` / `keepsake:inscription` / `keepsake:imprint` /
  `keepsake:saveCard`
- `src/preload.js`：5 个桥接

**完成层（界面）**
- `renderer/index.html`：`#completion`（标题 / 版本 / 波形印记 canvas / 日期 / 从头听 /
  导出音频 / 保存作品卡 / 查看制作详情 / 留一句话 / 安静聆听条 / 就地状态与警告）
- `renderer/app.js`：完成层渲染、波形印记（从**已解码的最终音频**取峰值）、作品卡 canvas 绘制、
  安静聆听、Esc/返回、就地的保存与文字状态；`applyWorkspaceMode()` 决定完成层与 A/B 审听谁在前面；
  选定成功后自然收束到完成层；导出反馈同时写入两层
- `renderer/style.css`：完成层排版（留白、两种字号层级、少量控件）、`prefers-reduced-motion`、
  安静聆听（隐去侧栏与流程）、微交互与焦点、800px 以上不横向滚动

**测试**
- `scripts/test-keepsake.js`（新，23 条）：留存记录的边界、原子性、隔离、投影、韧性、印记确定性、
  卡片隐私
- `scripts/test-main-ipc.js` §12（完成门禁/留存/作品卡，真实 Core，10 条）+ §13（完成层 renderer 契约，10 条）
- `package.json`：`npm test` 纳入 `test-keepsake.js`

## 2. keepsake 数据结构与非权威边界

```json
{
  "schema": "moodify.studio.keepsake/0.1",
  "case_id": "<case 目录名>",
  "decision_request_id": "keep:<pair>:<kept>:<n>",
  "selected": "A | B | ORIGINAL | null",
  "completed_at": "ISO-8601（取自 decision.at）",
  "inscription": "≤ 280 码位、≤ 4 行",
  "imprint": [600 个 0..1 的小数],
  "updated_at": "ISO-8601"
}
```

- **不是完成状态的权威。** 完成与否由 `pipeline`（磁盘产物）+ `tuning.decisionBacked()`
  （⑦ 准入：pair 存在 + A/B 两侧候选 + 真实复检）推导。测试钉住：先塞一条 keepsake 也不能让阶段
  前进或解锁导出；记下完成、随后删掉 `recheck.json` 或候选，完成层立即失效。
- `selected` 是当前有效 decision 的**投影**（`keepsake:sync` 写入）；decision 变化时更新，
  一句话与印记保留；decision 失效时完成层消失但文字不删。
- 写入路径只有一个：`<case>/studio/keepsake.json`（临时文件 + rename）。
  不存音频字节、不存图片 base64、不存 report / hash 大表；整份文件 < 8 KB（有测试）。
- 读失败（损坏 JSON / schema 不符）只返回可诊断原因，声音流程与导出不受影响。
- **迁移/兼容：** 新文件，无历史版本；不修改 `decisions.jsonl`、`pipeline.json`、`finish_mode.json`。
  删除该文件只会让完成层失去「一句话/印记」（完成状态仍由产物推导），无副作用。
  印记是新增字段：旧记录没有它时，完成层从最终音频重算一次再写回（同一段音频 → 同一形状）。

## 3. 完成层 / 安静聆听 / 作品卡

**进入条件**（全部由既有事实推导，无新权威字段）：有效 pair + A/B 两侧完整 + 真实 recheck + 有效 decision。

**完成层首屏**（无庆祝弹层、无提示音、无掌声）：

```text
        歌曲标题
     A（保守）· 快速完成            ← 小型事实标签；保留原版时显示「保留原版」
   ───── 波形印记（无刻度/网格/游标）─────
        2026.10.04
        ▶ 从头听
  导出音频   保存作品卡   查看制作详情
        留一句话
```

- 音频不可用时就地显示「…音频不可用（文件可能被移动或删除）」，**绝不用别的版本替代**；印记仍在。
- 首页不含 LUFS 表、pair_id、schema、hash、Core 命令或能力说明（有静态测试逐字校验）。
- 从 REVIEW 收束：320 ms 的轻微位移+淡入（`prefers-reduced-motion` 下直接切换），焦点落到
  「从头听」但**不自动播放**。
- 「保留原版」显示为保留原版，不伪装成处理版本。

**安静聆听**：隐去侧栏、顶栏、次级动作与文字入口，只留标题、版本、印记与 transport
（播放/暂停、时间、音量、返回作品）；`Esc` 或「返回作品」退出；不进入系统全屏、不抢焦点、不阻止切窗口。
音量只是试听音量（`setVolume`），不改文件、不做响度归一化。

**作品卡**：1600×1000 PNG，本地 canvas 确定性绘制（无随机、无生成式图像服务），内容只有
Moodify 标识 + 标题 + 最终选择 + 波形印记 + 完成日期 + 可选的一句话；点击保存才开系统对话框，
默认文件名 `<歌曲名> — Moodify.png`（非法字符已清洗），取消不算失败，不自动上传、不写入 case。

## 4. 波形印记如何由真实最终音频确定性生成

1. 取「最终选择」的真实音频 → 走 **Phase 2.2 的同一解码路径**（`reviewDecodeSide`，同一缓存）；
2. `imprintPeaksFromBuffer(buffer, 600)`：把解码后的各声道样本摊成 600 个桶的最大绝对值
   —— 纯循环，无 `Math.random`、无 `Date.now`、无时钟/随机种子（有测试断言）；
3. `keepsake:imprint` 在 main 侧做定长/限幅(0..1)/3 位小数归一化后落盘；
4. 完成层 canvas 与作品卡 canvas 都用这同一串数字绘制（`paintImprint` 与卡片绘制同算法、同形状）；
5. 同一段音频 → 同一串数字（有测试）；窗口缩放只重画同一串数字，不改变形状。

## 5. 播放器复用证明

- `app.js` 里 **`reviewMountTransport` 只创建一次** `WaveSurfer`（`if (!review.ws)` 守卫）；
- 完成层与安静聆听**不新建**播放器或 `AudioContext`：`completionListenFromStart`、
  `ensureSelectedAudioDecoded`、`completionEnterQuiet/ExitQuiet`、`completionSaveCard` 都有静态断言；
- 同一个 transport 同时驱动两层的时间显示（`timeupdate` 同时写 `#rv-time` 与 `#cp-time`）、
  播放/暂停图标与曲终状态；「从头听」= 载入**最终选择**那一侧 → `seekTo(0)` → 播放；
- 选择 ORIGINAL 时载入的是 case 源（测试断言 `keepsake:state.audioPath` 与 `tuning:audio` 字节
  的 sha256 与磁盘文件一致，绝不落到 A/B）。

## 6. PNG 隐私字段检查

- 渲染层绘制卡片时**只能**读 `keepsake:state.card`（`title / selectionLabel / versionLabel /
  dateLabel / inscription`）与印记；静态测试断言卡片函数里不出现 `caseDir` / `pairId` / `sha256` /
  `hash` / `reportPath` / `evidencePath`；
- main 侧 `cardModel()` 是唯一来源，测试断言其中不含 case_id / pair_id / 64 位 hash / 绝对路径；
- 保存通道只接收**已画好的 PNG 字节**，不接收任何路径或 id；默认文件名来自清洗后的标题。

## 7. 人工验收（截图待主控）

本代理无图形界面与截图能力，**不伪造截图**。请按任务书 §14 验收：

```text
1 选择成功后自然进入完成层（无庆祝弹窗）
2 首屏只有标题/版本/印记/日期与核心动作
3 点「从头听」→ 确认播的就是最终选择，位置从 0 开始（且没有自动播放）
4 播完保持安静（无下一首、无推荐）
5 写一句含中文与重音字符的话 → 重启后仍在
6 保存作品卡 → PNG 清晰、无技术隐私字段
7 「查看制作详情」→ A/B 证据完整
8 改选另一版本 → 版本更新、私人文字保留
9 重新打开 case → 默认落在完成层
10 移走最终音频 → 不播放错误版本，显示音频不可用、文字保留
```

本代理已用**真实歌曲副本**（123.32 s / 48 kHz，临时 cases-root，未触碰用户归档）跑通了
数据与门禁侧，输出逐字如下（46 s）：

```text
SESSION: REVIEW | pair: tune_20261004144436971_kfkg
BEFORE DECISION: {ok:true, complete:false, reason:"NO_DECISION", title:"Je ne blesserai pas ta fragilité", …}
DECISION ok: true  A
SYNC ok: true
INSCRIPTION ok: true | chars: 39            ← 「…fragilité — é中文😀」按码位计
IMPRINT: true | buckets: 600 | head: 0.088,0.175,0.262,0.346,0.427
COMPLETION: {complete:true, selected:"A", selectedLabel:"A（保守）", tierLabel:"快速完成（仅立体声）",
             title:"Je ne blesserai pas ta fragilité", completedAt:"2026-10-04T14:45:22.739Z",
             audioAvailable:true, keepsakeError:null}
CARD MODEL: {title:"Je ne blesserai pas ta fragilité", selectionLabel:"A（保守）",
             versionLabel:"快速完成（仅立体声）", dateLabel:"2026.10.04", inscription:"…"}
PRIVACY: no pair id / no case id / no path / no hash → 全为 true
SAVE CARD (用户取消): {ok:false, canceled:true} | 默认文件名: Je ne blesserai pas ta fragilité — Moodify.png
KEEPSAKE FILE: 6853 bytes
STAGE: CHOSEN | canExport: true             ← 完成状态来自 decision，keepsake 只是留存
```

视觉与交互（完成层外观、安静聆听、作品卡成品图）需要人眼确认 —— 见上表 10 步。

## 8. 测试结果

```text
cd moodify-desktop && npm test
  → check-contracts ✓（DOM id 179 · 桥接 59 · IPC 58 · 事件 5 · 会话相位 5）
    test-pipeline 61/61 · test-recheck 9/9 · test-session 38/38 · test-keepsake 23/23
    test-orchestrator 20/20 · test-main-ipc 67/67（§12 完成层 10 条 + §13 契约 10 条）· test-studio 21/21
python scripts/check_repo_structure.py → OK
python -m ruff check moodify-core-package/src moodify-core-package/tests → All checks passed
```

覆盖到的关键纪律：无 decision / 假 decision / 候选或复检被删 → 完成层不出现或立即失效；
keepsake 不能解锁 CHOSEN 与导出；A/B/ORIGINAL 三出口都能进入完成层；一句话的码位与行数边界、
改选保留、失效不删、损坏不阻断、重启恢复；印记定长可复算；作品卡取消不写文件、确认后写入的正是
那些字节且被 Pillow 解码为 1600×1000 PNG；完成层与制作详情双向进入；单 transport 复用；
曲终安静；安静聆听的 Esc 与返回；reduced-motion 的 CSS 与 JS 分支；首屏无技术字样与营销词。

## 9. HUMAN_DECISION_REQUIRED

1. **作品卡的品牌标识位置/尺寸**：目前用现有 `assets/moodify_logo.png` 左上角 180 px 宽。
   若要固定版式（例如居中或加字标），需要一次视觉裁定。
2. **作品卡是否提供第二个尺寸**（如 1080×1350 竖版）供手机查看；任务书只要求 1600×1000 或等比例。
3. **安静聆听是否要在歌曲结束后自动退出**：目前保持安静、停在原地（更符合「不自动做任何事」），
   若希望自动返回作品页需要人类确认。
4. **完成层是否需要「另存为副本」或「复制文字」**：本轮未做（任务书未列，且属新动作面）。
