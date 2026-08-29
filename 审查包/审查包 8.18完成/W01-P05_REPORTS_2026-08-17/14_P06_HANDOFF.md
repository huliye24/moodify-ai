# 14 — P06 Handoff

**From:** W01-P05（Cloud Audio Compute Pipeline）→ **To:** W01-P06（Delivery + PLAY）

## 已固定（P06 不再处理音频计算）

- 唯一 canonical pipeline：ACQUIRE→VALIDATE→STEM(optional)→ANALYZE→JUDGE→INTERVENE/BYPASS→PROFILE→RENDER→VERIFY→REGISTER→CompletionCandidate
- stage vocabulary（10 阶段）+ StageResult 结构
- pipeline version / production fingerprint / profile 版本化
- failure 映射（P04 taxonomy）
- scratch 生命周期
- CompletionCandidate 契约（ready_candidate_object_id）

## P06 从 P05 接收（§26）

| 项 | 来源 |
|---|---|
| READY candidate / final render identity | CompletionCandidate.ready_candidate_object_id（P04 complete 后） |
| object ref | objects 表（bucket/object_key） |
| duration / format / playback metadata | VALIDATE/VERIFY metrics（candidate.stage_results） |
| verification evidence | evidence object + evidence 表 |
| access classification | P03 数据类（RENDER=私有/受控） |
| track metadata | tracks 表 |
| version identity | pipeline_version / production_fingerprint / profile_version |

## P06 必须回答的唯一问题

> 一个已经被系统确认 READY 的音频对象，怎样安全、稳定、低摩擦地送到 Android 并完成 PLAY？

## P06 必答清单

| # | 问题 | 前置约束 |
|---|---|---|
| 1 | READY 对象如何变成用户可播放 render_final（artifact_type 语义：render_candidate → render_final） | P05 §19：默认 render_candidate，发布流程决定 final |
| 2 | 播放 URL / 限时签名（BFF 签发，P02 NW-03 target） | 客户端不持长期凭据（R7/INV-13） |
| 3 | Android resolveUrl → 新交付面 | 现状静态 URL（P00 E18 §24） |
| 4 | 播放 metadata（时长/格式/专辑等） | candidate 内嵌 + tracks 表 |
| 5 | 公网命名/品牌（CD-011 HUMAN_DECISION_REQUIRED） | 用户裁决 |

## 阻塞项

- 真实 worker 循环（claim→run→complete 的常驻进程）未实现（P05 后）；P06/P08 视需要。
- render_final 语义（候选→正式）待 P06 定义。
