# Moodify Desktop — 一键完成机 Phase 2：第一条真实 A/B 闭环

**Date:** 2026-10-04  
**Status:** IMPLEMENTATION BRIEF  
**Owner / final acceptance:** Codex（主控）  
**Implementation delegate:** DeepSeek / Claude Code  
**CANON_CHANGE:** NO  
**MIP_REQUIRED:** YES — 开始实现前先把本任务的 Core 契约并入并更新 `MIP-0002`

## 0. 执行前必须阅读

1. `AGENTS.md`
2. `docs/canon/CURRENT_CANON.md`
3. `docs/canon/PRODUCT_BOUNDARY.md`
4. `docs/canon/AUTHORITY_ORDER.md`
5. `docs/canon/PRODUCT_DEFINITION_V3.md`
6. `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`
7. `docs/plan/2026-10-04_DESKTOP_ONE_CLICK_PHASE1.md`
8. `protocol/mips/MIP-0002-stem-tuning-loop.md`

Phase 1 已验收：Desktop 已有一键编排骨架、真实失败投影、恢复能力和严格的 A/B 选择门禁。
Phase 2 不重做这些基础。

## 1. 本阶段的唯一产品结果

> **让一首真实歌曲第一次从 Desktop 走到两个真实可听候选：原版 / A（保守） / B（充分），完成复检后由人选择并导出。**

Phase 2 优先打通 Canon 已允许的 **快速完成（仅立体声）**：

```text
导入歌曲
  → 用户显式选择「快速完成（仅立体声）」
  → Core 生成 A / B 两个整曲候选
  → Core 对 A / B 分别重跑检测
  → Desktop 对齐 原版 / A / B
  → 人试听并选择 A / B / 保留原版
  → 导出
```

这是第一条真实纵向闭环，不是假装已经完成深度逐轨修音。

## 2. 为什么先做快速路径

深度路径仍依赖三个尚未具备或未证明的能力：

1. 分解 → 无处理复合的可逆性验证；
2. 以 MIDI 为参考的逐轨音准与节奏修正；
3. 逐轨处理后的多轨复合。

直接在预览级分轨上实现“深度完成”，会把尚未验证的处理写成产品能力。快速路径不使用 MIDI，
不声称修正音准或节奏，只对原始立体声整轨生成两档处理，因此能先验证最重要的用户闭环：

```text
生成两个完整候选 → 复检 → 人听 → 三出口 → 导出
```

深度路径继续显示 `TUNABLE_CORE_NOT_AVAILABLE`，不得因为快速路径可用而被自动解锁。

## 3. Gate 0 — 先更新 MIP，不得静默增加 Core 契约

本任务新增或冻结 Core 行为契约，因此实现前必须更新 `MIP-0002`，至少加入：

- `FAST_STEREO_ONLY` 的输入、输出和失败契约；
- 两档 tier descriptor；
- A/B 必须成对、失败时不得留下可被识别为完整 pair 的产物；
- evidence 字段、校准状态和版本；
- 与既有 `mix_graph` 的复用关系；
- 回滚与兼容性；
- 本阶段不包含逐轨音准/节奏修正的边界。

MIP 可以在本阶段保持 `DRAFT`，但实现只能作为 **EXPERIMENTAL reference implementation**，
不得在证据不足时把 MIP 标成 `ACCEPTED` 或把参数称为已验证。

## 4. Core 契约

### 4.1 新增稳定调用面

建议 CLI 形态：

```text
moodify tuning render-pair \
  --mode fast-stereo-only \
  --source <song.wav> \
  --output-dir <pair_dir>
```

也可以采用与现有 CLI 风格更一致的等价命令，但必须满足：

- 真正能力位于 `moodify-core-package/`；
- Desktop 只调用 Core，不包含 DSP 参数或音频算法；
- 同一 Core API 可被 CLI 和未来其他 interface 调用；
- 命令一次生成**一对**候选，不允许只成功一边后返回成功。

### 4.2 两档定义

```text
A = conservative  保守完成
B = full          充分完成
```

每档必须携带：

```json
{
  "tier": "conservative | full",
  "mode": "FAST_STEREO_ONLY",
  "calibration_status": "UNCALIBRATED_ENGINEERING_DEFAULT",
  "parameters": {},
  "preserve": [],
  "engine_version": "<version>"
}
```

纪律：

- A/B 参数必须显式记录，不能只写“强一点”；
- 不得重新使用 `clean_master` / `warm_vocal` / `wide_space` 作为产品选择或 tier 名称；
- 可以复用现有 `mix_graph` primitives 与 provider，但必须生成新的两档 descriptor；
- 两档未经过人类校准前始终标记 `UNCALIBRATED_ENGINEERING_DEFAULT`；
- 不得把 B 命名为“更好”，只能叫“充分”或“变化更明显”。

### 4.3 允许的处理

快速路径只允许整轨混音处理，例如现有 Core 已支持且能留下 Mix Graph 的：

- gain；
- EQ；
- compressor；
- limiter；
- stereo/spatial（仅在既有 Core provider 支持范围内）。

快速路径明确禁止声称：

- 做了逐轨处理；
- 修正了音准；
- 修正了节奏；
- 恢复了原分轨；
- 保护了未被 `preserve` 记录的感知特征。

### 4.4 原子产物

成功后必须形成：

```text
<case>/studio/tuning/<pair_id>/
  pair.json
  A/
    plan.json
    tuned/source.wav
    mix.wav
    evidence.json
  B/
    plan.json
    tuned/source.wav
    mix.wav
    evidence.json
```

`pair.json` 至少记录：

```json
{
  "schema": "moodify.studio.tuning-pair/0.1",
  "pair_id": "...",
  "mode": "FAST_STEREO_ONLY",
  "source": "...",
  "source_sha256": "...",
  "tiers": { "A": "conservative", "B": "full" },
  "calibration_status": "UNCALIBRATED_ENGINEERING_DEFAULT",
  "created_at": "..."
}
```

写入规则：

- 先写临时 attempt 目录；
- A、B、evidence 全部成功后再原子发布成正式 pair；
- 任一侧失败，正式 `tuning/<pair_id>` 不得呈现为完整 pair；
- 不覆盖旧 pair；重复执行产生新 pair；
- 不覆盖源音频。

## 5. Evidence 与硬验证

A、B 各自必须携带独立 evidence，至少包含：

- source/output SHA-256；
- Core 与 engine 版本；
- tier descriptor 与全部实际参数；
- Mix Graph digest；
- before / after 测量；
- duration、sample rate、channels；
- finite 检查（无 NaN / Inf）；
- peak gate；
- `review_required: true`；
- `calibration_status`。

最低硬门禁：

```text
输出文件存在且可解码
duration 差异在明确容差内
sample rate 保持
channel count 保持
无 NaN / Inf
峰值不越过 Core 已声明的安全门禁
A/B 均完成才发布 pair
```

不得新增一个未经来源化的“听感分数”来决定 A 或 B 更好。

## 6. Desktop 接线

### 6.1 显式选择快速路径

保持现有 Canon：快速完成不能自动成为默认路径。用户必须执行一次明确动作：

```text
深度完成目前不可用
[使用快速完成（仅立体声）]
```

选择继续记录到：

```text
<case>/studio/finish_mode.json
```

并在主界面持续显示模式徽章：`快速（仅立体声）`。

### 6.2 一键编排

显式选择快速路径后，同一个 `开始完成` 必须自动：

1. 调用 Core 生成整轨 A/B；
2. 确认 pair 两侧与 evidence 齐备；
3. 对 A、B 各运行一次完整 analyze；
4. 生成三方 `recheck.json`；
5. 进入 `REVIEW`；
6. 展示原版 / A / B 同位置试听；
7. 等待人选择，不自动选择；
8. 选择后允许导出。

不得重新创建第二个编排器。继续使用：

- `src/orchestrator.js`：调度；
- `src/session.js`：投影和失败记录；
- `src/pipeline.js`：唯一阶段/门禁权威；
- `src/tuning.js`：pair 与选择门禁；
- `src/recheck.js`：三方对齐。

### 6.3 失败体验

任何失败必须进入现有 `STEP_FAILED` 记录，并显示：

- 失败在哪一阶段；
- Core 返回的真实原因；
- 是否可重试；
- 是否留下临时产物；
- A/B 是否未生成。

不得在 A 成功、B 失败时进入 `REVIEW`。

## 7. 深度路径与可逆性验证

Phase 2 同时允许实现**独立的可逆性测量原语**，但它不是本阶段 A/B 闭环的前置：

```text
moodify tuning roundtrip \
  --source <original.wav> \
  --stems <stems_dir> \
  --out <roundtrip.json>
```

要求：

- 真实复合已有 stems，不得读取未知原分轨；
- 记录 correlation、sample/max error、时长/SR/声道一致性等实际测量；
- 阈值必须带来源与校准状态；
- 没有被批准的阈值时，不得为了打开门禁随意写 `passed: true`；
- 若当前预览分离无法通过，应如实产出 `passed: false`；
- 深度修音继续保持锁定。

如果无法提出有来源的 `passed` 判据，本阶段可以只产出测量事实和 `INCONCLUSIVE`，并将
`passed` 保持为 `false`。不得为了让流程好看而伪造通过。

## 8. 测试要求

### 8.1 Core 单元测试

- 两档 descriptor schema；
- 不接受未知 tier / mode；
- 参数与 calibration status 全量进入 evidence；
- A/B 原子发布；
- 单边失败不形成正式 pair；
- 拒绝覆盖既有输出；
- hashes 与 graph digest 可复算；
- duration/SR/channels/finite/peak 门禁。

### 8.2 真实音频集成测试

至少使用一个仓库可生成的短合成音频，不提交重 WAV：

```text
Core render-pair
  → A.wav / B.wav 可解码
  → A 与 B hash 不同
  → 两边 evidence 可复算
  → 两边完整 analyze 成功
  → recheck.json 三方守恒
```

测试不得只创建空文件或手写假 report。

### 8.3 Desktop 主进程测试

- 未显式选择快速路径时不自动使用快速模式；
- 显式选择后从当前产物继续；
- render-pair 只调用一次；
- A/B 单边失败 → `BLOCKED`；
- 完整 pair → 自动复检 → `REVIEW`；
- 没有人工选择不能导出；
- A / B / ORIGINAL 都必须经过同一门禁；
- 重复启动不覆盖旧 pair；
- 失败后重试不把临时 attempt 误认成正式 pair。

### 8.4 回归

必须通过：

```text
cd moodify-desktop && npm test
python scripts/check_repo_structure.py
Core 相关 pytest
```

## 9. Definition of Done

Phase 2 只有同时满足以下条件才完成：

```text
真实音频进入 Desktop
用户显式选择快速完成
一次“开始完成”真实调用 Core
A / B 两个完整且不同的 WAV 产出
A / B 各有参数、Mix Graph 与 evidence
A / B 自动复检并进入 REVIEW
人可同位置试听原版 / A / B
没有人工选择不能导出
A / B / ORIGINAL 三出口均可正确落账并导出
失败可见、可重试、不留假完成产物
全部测试与结构检查通过
```

仅有 mock、空 WAV、手写 report、前端占位或“接口已预留”不算完成。

## 10. 明确不做

- 不实现逐轨音准修正；
- 不实现逐轨节奏修正；
- 不宣称多轨复合已经优于原版；
- 不把快速路径自动设为默认；
- 不重新引入三个旧预设作为产品面；
- 不新增服务器、账户、云存储、社交或网络功能；
- 不重写 Desktop；
- 不修改 Android；
- 不删除旧 Studio / research 文件；
- 不用 AI 自动选择 A 或 B；
- 不把“生成”显示成“完成”。

## 11. 停止条件

出现以下任一情况，停止实现并报告，不得绕过：

- 必须新增第二套 DSP 或在 Desktop 写声音算法；
- 现有 Mix Graph 无法表达两档而需要改变产品定义；
- A/B 参数需要新的听觉裁定；
- 没有来源可以定义安全门禁；
- 真实音频测试发现两档相同或输出不可解码；
- Evidence 无法证明实际执行了哪些参数；
- 为通过流程必须伪造 `passed: true`、report 或候选文件；
- 需要扩大到 server / cloud / account / network。

需要人类方向决策时写 `HUMAN_DECISION_REQUIRED`，不要自行扩大范围。

## 12. 交付报告

执行代理完成后必须提供：

1. 修改文件清单；
2. MIP-0002 增补内容；
3. Core 命令及契约；
4. A/B 两档的实际参数与校准状态；
5. 真实音频运行记录与产物路径；
6. evidence 摘要与 hashes；
7. Desktop 完整操作路径；
8. 失败注入测试结果；
9. 全部测试命令与结果；
10. 尚未实现的深度路径能力；
11. 所有 `HUMAN_DECISION_REQUIRED`。

最终是否通过由主控独立验收，执行代理自评不构成完成。
