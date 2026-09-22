# AGENTS.md — Moodify Repository Authority

This file defines the canonical context for AI coding agents working in this repository.

## Product Identity

**External product:** Moodify Sound Protocol — AI / Agent 可通过 CLI 调用的声音处理协议；一个共享 Core，CLI 为首要执行接口，App 为播放/审听接口。协议 v0.1 的实际边界见 `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md`。

**Core actions:** CLI `PROCESS`; App `PLAY` / review. Both use the same Core.

```text
Agent / human -> MSP job -> Moodify CLI -> shared Core -> processed audio + evidence -> human review
```

**Internal systems:**

- Moodify Ear / Auditory Intelligence — 内部听觉、判断、验证与研究系统
- Cloud Production System — Intake → Analyze → Stem → Judge → Intervene → Render → Verify → Evidence
- Classic Reconstruction — 内部生产哲学（宪法 v1.0，决策驱动受控重建）

Ear 是 Moodify 的内部听觉智力，不是对外产品面。不得把 MSP/0.1 的预设处理误称为自动母带或已完成的专业验证；不得建立第二套 DSP Core。

## Canon Reference

进入本仓库先读：

1. `AGENTS.md`（本文件）
2. `docs/canon/CURRENT_CANON.md`
3. `docs/canon/PRODUCT_BOUNDARY.md`
4. `docs/canon/AUTHORITY_ORDER.md`
5. `docs/REPOSITORY_STATUS.md`

Public brand language and public-site roles then resolve through `docs/brand/public/README.md` and its authority set. The highest topic-specific Public Brand authority is `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md`.

内部系统权威与既有政策见 `docs/canon/INTERNAL_SYSTEMS.md`、`docs/LEGACY_AND_EXPERIMENTAL_POLICY.md`。

## Important Distinction

- 对外：Moodify Sound Protocol；AI / Agent 通过 CLI 提交显式作业，App 负责播放与人工审听。
- 内部：Ear / analysis / stem / judgment / intervention / preset decision / verification / evidence / learning / cloud production。复杂度由 Moodify 承担。
- 内部处理复杂度不是对外卖点。
- Public Form 品牌信念：**每一种声音，都值得被世界听见。 / Every voice deserves to be heard.**
- 产品原则：**Listen. Then Play.**；用户动作：**Play.**

## Three Disciplines

- **WSE — Wave-Spectral Evolution**: what happened in the sound?
- **MSE — Musical-Structural Engineering**: what is the musical structure?
- **PPE — Production Process Engineering**: how is the result produced, verified and recovered reliably?

## Asset Loop

```text
Production Case
  -> Measurement Record
  -> Evidence Artifact
  -> Theory Update
  -> Rule Update
  -> Next Production Case
```

## Authority Order

When instructions conflict, prefer:

1. current explicit human instruction;
2. root `AGENTS.md`;
3. `docs/canon/*`（CURRENT_CANON / PRODUCT_BOUNDARY / INTERNAL_SYSTEMS / AUTHORITY_ORDER / CURRENT_ARCHITECTURE）;
4. verified runtime evidence（W01-P00 Evidence Index 等）;
5. canonical main behavior and tests;
6. current subsystem documentation;
7. experimental documentation;
8. historical / legacy documentation.

Historical documents do not override current Canon. A LEGACY / HISTORICAL document cannot promote itself back to Canon through its own text.

## Agent Rules

- 不创建第二个公开产品身份（Ear 不得再次升级为公开产品）。
- 不创建第二套 authoritative state machine。
- 不创建第二套 Job authority。
- 不以"功能很多"作为产品价值。
- 不把内部处理复杂度暴露给用户作为卖点。
- 不因文档冲突而自行做产品哲学决策——写 `HUMAN_DECISION_REQUIRED`。
- 不把历史文档当作当前 authority。
- 不虚构云端/生产能力：未验证不写成已运行（Canon 与事实分离，R6/R10）。

## Canon Change Rule

改变以下任何内容的任务必须声明 `CANON_CHANGE = YES`，并说明 why / evidence / affected authority files / migration / rollback：

- 对外产品身份
- 内部/外部能力边界
- state machine authority
- evidence authority
- cloud control authority
- data authority

普通功能任务不能静默修改 Canon。变更记录进入 `docs/canon/CANON_CHANGELOG.md`。

## Change Discipline

Before coding:

1. identify the canonical subsystem;
2. identify whether the change is canonical, experimental or legacy;
3. inspect existing tests;
4. preserve evidence and reproducibility.

Do not:

- mass-delete legacy code without an explicit cleanup task;
- merge stale branches wholesale;
- add duplicate orchestration systems;
- introduce a second authoritative state machine;
- claim experimental metrics are validated production truth;
- remove human authority where the system still depends on listening judgment;
- introduce secrets, private audio or generated heavy artifacts.

## Judgment Authority

Moodify uses **scoped machine authority with explicit human escalation**:

- a machine may decide only inside a validated, versioned and explicitly authorized scope;
- an out-of-scope, insufficient-evidence, uncertain or unresolved perceptual case must produce
  `HUMAN_REQUIRED`, `INCONCLUSIVE` or a defined failure state;
- automation must not suppress escalation merely to keep the loop unattended;
- a human decision must record its reviewer, scope, time and supporting evidence.

## Definition of Done

A code change is not complete merely because it runs.

It should answer:

- What case does this serve?
- What is measured?
- What evidence is produced?
- How is the result verified?
- What happens on failure?
- Is the result reusable in the next case?
