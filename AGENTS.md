# AGENTS.md — Moodify Repository Authority

This file defines the canonical context for AI coding agents working in this repository.

## Product Identity

**External product:** Moodify Music / Moodify Player

**Core user action:** PLAY

```text
Source / Cloud-prepared Track -> Moodify -> PLAY
```

**Internal systems:**

- Moodify Ear / Auditory Intelligence — 内部听觉、判断、验证与研究系统
- Cloud Production System — Intake → Analyze → Stem → Judge → Intervene → Render → Verify → Evidence
- Classic Reconstruction — 内部生产哲学（宪法 v1.0，决策驱动受控重建）

Ear 是 Moodify 的内部听觉智力，不是对外产品面。Do not regress the repository identity back to "The Ear of AI" as a public product, "AI music post-processing", "automatic mastering", or a preset/DSP product. Do not create a second public product identity alongside Moodify Music / Player.

## Canon Reference

进入本仓库先读：

1. `AGENTS.md`（本文件）
2. `docs/canon/CURRENT_CANON.md`（Moodify Music / Player 对外产品面）
3. `docs/mood/CURRENT_CANON.md`（MOOD WORLD + PROTOCOL + PORTAL）
4. `docs/canon/PRODUCT_BOUNDARY.md`
5. `docs/canon/AUTHORITY_ORDER.md`
6. `docs/REPOSITORY_STATUS.md`

Public brand language and public-site roles then resolve through `docs/brand/public/README.md` and its authority set. The highest topic-specific Public Brand authority is `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md`.

内部系统权威与既有政策见 `docs/canon/INTERNAL_SYSTEMS.md`、`docs/LEGACY_AND_EXPERIMENTAL_POLICY.md`。

## MOOD Protocol

MOOD 是一个开放的 Web3 数字世界，由 **WORLD + PROTOCOL + PORTAL** 三层构成：

```text
MOOD = WORLD + PROTOCOL + PORTAL
Token is not the product.
Token is not the protocol.
Token is not the world.
MOOD Token = future economic layer (NOT ACTIVATED).
```

- **WORLD**：MOOD 总体世界，包含 Portal + Protocol + future Token。
- **Moodify Protocol**：贡献、声誉、节点、透明度等协议层（MPF-001..005）。
- **PORTAL**：`crestwavecoin.com`（WORLD 入口，PLANNED）。
- **Moodify**：Genesis Application（Moodify Music / Player，运行在 MOOD 之上）。

Token 激活条件：G0–G11 全部 PASS（见 `docs/mood/TOKEN_LAUNCH_GATE.md`）。

## Important Distinction

- 对外：Moodify Music / Player，用户只做 PLAY。
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
- 不将 MOOD 错误描述为单一 Token 产品（见 `docs/mood/CURRENT_CANON.md`）。
- 不在 Token Launch Gate（G0–G11）未全部 PASS 前实现 MOOD Token 激活（见 `docs/mood/TOKEN_LAUNCH_GATE.md`）。
- 不整条 merge `codex/mood-mainnet-integration-009`（见 `docs/mood/IN_FLIGHT_CHANGE_REGISTER.md`）。
- 不将历史 Genesis v1.0 实现自动当作 MOOD Token Canon（见 `docs/mood/ASSET_CLASSIFICATION.md`）。

## Canon Change Rule

改变以下任何内容的任务必须声明 `CANON_CHANGE = YES`，并说明 why / evidence / affected authority files / migration / rollback：

- 对外产品身份
- 内部/外部能力边界
- state machine authority
- evidence authority
- cloud control authority
- data authority
- Token 是否进入激活路径（包括新增 Token 官方 CA、Token 发布、Token 经济参数）

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
