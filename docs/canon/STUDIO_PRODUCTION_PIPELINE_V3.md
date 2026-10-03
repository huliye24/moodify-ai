# STUDIO PRODUCTION PIPELINE V3 — Moodify

**Version:** 3.0
**Date:** 2026-10-03
**Status:** **DEFINED** — 流程与产物契约。执行范围见 §7。
**Authority:** root `AGENTS.md` → `docs/canon/*`
**Related:** [PRODUCT_DEFINITION_V3.md](PRODUCT_DEFINITION_V3.md) · [TECHNOLOGY_PRINCIPLES.md](TECHNOLOGY_PRINCIPLES.md) · [../protocol/MOODIFY_STUDIO_CONTEXT_0_1.md](../protocol/MOODIFY_STUDIO_CONTEXT_0_1.md)

---

## 0. 核心原则

> **Understand first. Decompose second. Process last.**
> 先理解，再分解，最后处理。

早期 Studio 允许「分析完立刻选一个预设处理立体声母带」。**那对母带来说太早了。**
一首歌应当先被听懂、被分解、结构被恢复，然后才进入 AI 辅助的完成阶段。

三个预设（`clean_master` / `warm_vocal` / `wide_space`）**没有消失**，
它们只是从「流程的第一步」下移为「最后一步的工具」。**工具不是流程。**

---

## 1. 规范流程

```text
①  检测  ANALYZE      数据 / 频谱 / 图表
②  问题  DIAGNOSE     Core 发现了什么 + 该保护什么
③  分轨  SEPARATE     快速分离（预览级，见 §5）
④  结构  STRUCTURE    MIDI / 曲谱
⑤  方案  PLAN         上下文包 + 处理方案
⑥  成品  FINISH       执行 → 试听 → 选择 → 导出
```

人类视角的措辞（§17）：**继续分析 → 查看问题 → 开始分轨 → 提取结构 → 生成处理方案 → 执行方案 → 试听成品**。
AI 出现在**规划与执行**阶段，不早于系统拥有足够上下文之前。

---

## 2. 职责边界

| 角色 | 做 | 不做 |
|---|---|---|
| **AI** | 读结构化证据（analysis / diagnosis / stems / MIDI / 能力清单），产出结构化完成方案 | **不充当 DSP 引擎**；不发明测量事实 |
| **Core** | 执行 EQ / 压缩 / 动态 / 立体声 / 响度 / 渲染 / 校验（经既有确定性工具） | 不做产品判断 |
| **人** | 决定保留原版还是候选、重试、编辑方案、发布 | 不需要懂参数 |

**没有任何 AI 候选会被自动称为「完成」。**

---

## 3. 阶段状态由产物推导

`<case>/studio/pipeline.json` 只是**记录**，不是权威。每次读取都从磁盘产物重新推导：

```text
ANALYZED    ← report.json 存在
DIAGNOSED   ← studio/diagnosis.json 存在
SEPARATED   ← stems/*.wav 存在            （可选）
STRUCTURED  ← midi/ 或 score/ 非空         （可选）
PLANNED     ← studio/plans/*.json 存在
RENDERED    ← studio/versions/ai_* 存在
VERIFIED    ← studio/verification/ 有记录  （可选）
CHOSEN      ← studio/selection.json 存在
EXPORTED    ← studio/export/ 有记录
```

**为什么推导而不是推进**：删掉 stems 目录后状态必须自动退回。
一个写着「已分轨」而文件已不在的状态，正是本仓库反复清理的那类谎报。

`READY_FOR_PLAN` 是**就绪度**（= analyzed ∧ diagnosed），不是用户做过的动作，
因此它**不出现在阶段游标里**，只作为门禁事实 —— 否则每个分析+诊断过的 case 都会
自称「可以出方案」，跳过 ③④，宣称用户没做过的进度。

---

## 4. 门禁

```text
硬门禁：进 ⑤ 方案 / ⑥ 成品 需要 ANALYZED + DIAGNOSED
软门禁：规范「深度完成」还期望 SEPARATED + STRUCTURED
快速路径：允许跳过分离与结构，但 UI 必须显式标注
```

完成模式徽章只有两种，且**必须显示**：

```text
深度完成
快速（仅立体声）
```

**不标注就是骗人**——跳过分离是合法选择，但用户必须知道自己走的是哪条路。

---

## 5. 分离的诚实边界

`moodify-desktop/scripts/dsp_separate.py` 是 **DSP 中置估计 + HPSS**，
**不是模型分离**：有人声残留与伪影，**不构成母带级分轨**。

这句话**已经写在产物的 `engine_note` 里**，随数据一起流动，UI 直接呈现：

```json
{ "engine": "dsp_center_hpss",
  "engine_note": "非模型快速分离：中置声道估计 + HPSS 谱分解；有人声残留与伪影，
                  供快速观察/选段试听/MIDI 前处理，不构成母带级分轨。" }
```

其输出**不得**作为对分轨做破坏性最终处理的唯一依据而不告知用户。
未来「精细分离」应使用**成熟公开引擎**，不自研模型（本版本不实现）。

---

## 6. MIDI / 曲谱是上下文，不是真值

从混合音频提取的 MIDI / MusicXML 是**近似**。它们用于帮助理解旋律、音高走向、
音符密度、乐句、节奏与段落结构——**不得**当作原始作曲的精确重建。

证据优先级：

```text
音频证据 > 分轨音频 > 测量特征 > MIDI / 曲谱解读
```

---

## 7. 本版本（TASK 002A）实际实现范围

```text
✓ 重排流程（预设下移到 ⑥）
✓ 新增 ② 问题（diagnosis.json，严格投影自 Core 证据）
✓ 把既有 ③ 分轨 / ④ 结构 接进主流程
✓ 新增 ⑤ 方案（context.json + Core 草稿方案）
✓ 阶段推导 + 门禁 + 完成模式标注
✗ 任意 AI 计划的完整执行（留待 TASK 002C）
✗ 精细分离引擎
✗ 移动端同步 / 网络
```

---

## 8. 后续校验要求

处理之后必须：

```text
候选 → 重新检测 → 与原版对比 → 校验证据 → 人做 A/B → 才算完成
```

**绝不** `AI 处理 → 自动完成`。既有命题不变：

> **Generated is not finished.**

---

## 9. 已知限制（如实记录）

**诊断通常很薄。** Core 的 `report.json:findings[]` 目前只能产出两种：

```text
CLIPPING_PRESENT            (BLOCKING)
TRUE_PEAK_MARGIN_EXCEEDED   (WARNING)
```

而且在 18 个真实 case 中 **17 个 `findings` 为空**。因此 ② 问题 阶段经常无事可说。

UI 与 `diagnosis.json` 因此**必须**说「**当前规则未发现技术问题**」，
**绝不**说「这首歌没问题」——两者是不同的命题。
`diagnosis.json.finding_rule_coverage.note` 随产物一起携带这句话。

Core 另有 18 参数诊断引擎（`moodify/diagnosis/`），但桌面够不到，
且只挂在标着 `(Legacy) Old diagnosis engine` 的 `moodify legacy-analyze` 上。
接入它等于引入**第二套诊断权威**，与 `AGENTS.md` 冲突，故未接 → 见 HUMAN_DECISION。
