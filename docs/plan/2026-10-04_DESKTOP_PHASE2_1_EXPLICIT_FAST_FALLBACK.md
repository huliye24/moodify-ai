# Moodify Desktop Phase 2.1 — 深度受阻时显式切换快速完成

**Date:** 2026-10-04  
**Status:** IMPLEMENTATION BRIEF — HUMAN APPROVED  
**Owner / final acceptance:** Codex（主控）  
**Implementation delegate:** DeepSeek / Claude Code  
**CANON_CHANGE:** YES  
**MIP_REQUIRED:** NO — 不改变 Core 音频契约，仅修改 Studio 模式选择与门禁语义

## 0. 人类裁定

2026-10-04，人类批准以下产品规则：

> 当深度完成的分轨与 MIDI 已存在，但深度路径因可逆性未通过、缺少
> `studio/roundtrip.json` 或逐轨 Core 能力未就绪而无法继续时，Desktop 必须继续提供
> **「切换到快速完成（仅立体声）」**。切换必须由用户显式确认，绝不自动降级。

本裁定解决已在真实歌曲测试中复现的死路：

```text
检测完成
  → 自动完成分轨与 MIDI
  → 系统进入 DEEP
  → roundtrip / 逐轨 Core 未就绪
  → canTune = false
  → 旧规则 canRequestQuick = false
  → 用户既不能深度完成，也不能选择快速完成
```

这不是用户操作错误，而是门禁组合产生的产品死路。

## 1. 执行前必须阅读

1. `AGENTS.md`
2. `docs/canon/CURRENT_CANON.md`
3. `docs/canon/AUTHORITY_ORDER.md`
4. `docs/canon/PRODUCT_DEFINITION_V3.md`
5. `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`
6. `docs/plan/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_REAL_AB.md`
7. `docs/reports/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_IMPLEMENTATION.md`

不得重做 Phase 2 的 Core A/B 引擎、复检、选择或导出。

## 2. 唯一产品结果

让截图中的状态可以继续：

```text
深度完成
可逆性验证缺失 / 未通过
深度修音能力未就绪

[切换到快速完成（仅立体声）]
```

用户点击并确认后：

```text
记录 QUICK_STEREO_ONLY
  → 模式徽章变为「快速（仅立体声）」
  → ②逆向分解、③结构、可逆性在本模式显示 skipped
  → ④使用现有 fast-stereo-pair Core 能力
  → 自动复检
  → 原版 / A / B 人工试听与选择
  → 导出
```

已有 stems、MIDI、score 和失败的 roundtrip 证据必须保留；切换模式不是删除深度资产。

## 3. Canon 修改

先修改 `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`，并更新
`docs/canon/CANON_CHANGELOG.md`。

### 3.1 Why

旧的“只要 `deepReady` 就隐藏快速入口”会在深度 Core 尚未就绪时制造不可恢复死路，违反：

- 第一个产品目标必须形成可靠完成循环；
- 失败必须可见、可恢复；
- 快速路径可以存在，但必须由人显式选择；
- AI 不得通过自动降级替人改变完成模式。

### 3.2 新权威规则

深度优先改为：

```text
深度路径真实可执行 → 默认保持 DEEP
深度路径受阻       → 显示显式快速完成入口
用户未选择         → 不生成快速候选
用户明确选择       → 记录 FAST_STEREO_ONLY，并按快速路径继续
```

“存在 stems + MIDI”只证明深度前置资产存在，不再等价于“深度路径当前可执行”。

建议用以下概念避免继续混淆：

```text
deepAssetsReady = analyzed ∧ separated ∧ structured
deepExecutable  = deepAssetsReady ∧ reversible ∧ deep Core capability available
fastAvailable   = analyzed ∧ fast-stereo-pair capability available
```

快速入口的出现条件应基于 `!deepExecutable`，不能继续基于 `!deepAssetsReady`。

### 3.3 Migration / rollback

- 不迁移、不删除既有 case 产物；阶段仍由磁盘推导。
- 既有 `finish_mode.json` schema 不变。
- 回滚只需恢复旧门禁与 UI；Core、pair、decision、recheck 产物均兼容。
- Canon changelog 必须记录旧语义、死路证据、新语义与回滚方式。

## 4. 实现范围

### 4.1 `src/pipeline.js`

修正模式门禁，至少满足：

- 不再使用 `deepReady` 单独决定快速入口是否消失；
- 深度可逆性缺失或失败时，`canRequestQuick === true`；
- 深度 Core capability 为 unavailable 时，`canRequestQuick === true`；
- 用户显式选择快速后，`canTuneQuick === true`，即使 stems 与 MIDI 已存在；
- 快速模式下 `mode === FAST_STEREO_ONLY`，不得再被 `deepReady` 覆盖回 DEEP；
- 快速模式不改变或伪造 `reversible`；
- 用户未选择时绝不自动生成 A/B；
- 已有完整 A/B、复检或有效选择时，不出现破坏当前进度的模式切换提示。

不要新增第二套状态机。`pipeline.js` 继续是唯一阶段与门禁权威。

### 4.2 `src/session.js`

模式投影必须与新门禁一致：

- 深度受阻时返回 `canRequestQuick: true`；
- 切换后 ②逆向分解、③结构、可逆性显示 `skipped`，但磁盘资产不删除；
- 阻断原因必须明确区分：
  - 深度能力未就绪；
  - 用户可以显式切换快速完成；
- 不得把“可切换”显示成“系统已经自动降级”。

### 4.3 `src/main.js`

复用现有 `pipeline:setFinishMode` 与 `renderFastPair()`：

- 允许有 stems / MIDI 的 case 写入 `QUICK_STEREO_ONLY`；
- 点击切换只记录模式，不立即生成音频；
- 后续仍由同一个“开始完成”调用现有 Core `tuning render-pair`；
- 不删除、覆盖或移动深度路径产物；
- 不新增 Core 命令，不修改 DSP 参数。

### 4.4 Renderer

在当前“能力未就绪”区域显示主要补救动作：

```text
深度完成暂不可用
可逆性验证或逐轨处理能力尚未就绪。你可以保留现有分解结果，改用整轨两档完成。

[切换到快速完成（仅立体声）]
```

点击后需要一次简洁确认：

```text
快速完成不会使用分轨进行音准或节奏修正；仍会生成 A/B、复检并由你选择。
```

确认后：

- 模式徽章立即更新；
- “开始完成”可用；
- 不再显示深度 roundtrip 为当前模式阻断；
- 深度资产仍可在详情中看到，不得伪装成不存在。

## 5. 禁止行为

- 禁止自动切换为快速模式；
- 禁止用户点击“开始完成”时静默降级；
- 禁止删除 stems、MIDI、score、roundtrip 或失败证据；
- 禁止伪造 `roundtrip.passed = true`；
- 禁止为了消除提示而开放深度 ④修音；
- 禁止修改 Phase 2 A/B DSP 参数；
- 禁止新增第二套编排器、状态机或 DSP；
- 禁止扩大到 server、cloud、account、Android 或 Network；
- 禁止把快速完成描述为深度完成或逐轨修音。

## 6. 必须新增的测试

### 6.1 Pipeline

至少覆盖：

1. analyzed、无 stems/MIDI：可以请求快速完成；
2. stems + MIDI 存在、无 roundtrip：可以请求快速完成；
3. roundtrip `passed: false`：可以请求快速完成；
4. roundtrip `passed: true`，但深度 Core capability unavailable：可以请求快速完成；
5. 用户未选择：`canTuneQuick === false`，不生成 pair；
6. 上述任一阻断状态中显式选择：`mode === FAST_STEREO_ONLY` 且 `canTuneQuick === true`；
7. 快速模式不改变 `reversible`，不删除任何深度资产；
8. 深度路径未来真实可执行时，仍默认 DEEP，不自动显示为 FAST；
9. 已有完成中的 pair / recheck / decision 不被模式选择倒退或破坏。

### 6.2 Session / orchestrator

- 截图对应状态下，一键启动先停在真实深度阻断，不自动降级；
- 显式切换后再次启动，调用 `render-pair` 恰好一次；
- 自动复检后进入 REVIEW；
- 重启 Desktop 后从 `finish_mode.json` 恢复快速模式；
- 快速 Core 失败仍进入 `BLOCKED`，并允许真实重试。

### 6.3 Main IPC / Renderer contract

- 深度受阻时按钮可见；
- 确认前不写 `finish_mode.json`；
- 确认后只写模式，不生成 pair；
- 按钮文案不得暗示逐轨、音准或节奏修正；
- 模式徽章和 skipped 相位与投影一致。

## 7. 回归与人工复验

必须通过：

```text
cd moodify-desktop && npm test
python scripts/check_repo_structure.py
python -m ruff check moodify-core-package/src moodify-core-package/tests
```

人工复验必须使用已经复现死路的真实 case：

```text
Je ne blesserai pas ta fragilité.wav
  → 已有分轨 + MIDI
  → 缺 roundtrip / 深度能力未就绪
  → 出现「切换到快速完成（仅立体声）」
  → 用户确认
  → 开始完成
  → A/B 真实生成
  → 自动复检
  → 原版/A/B 可试听
  → 人工选择后导出
```

不要提交该私有音频或生成的大型音频产物。自动化测试继续使用短合成音频。

## 8. Definition of Done

只有同时满足以下条件才完成：

```text
截图中的死路被消除
深度路径没有被虚假解锁
快速模式仍需人显式确认
有 stems/MIDI 的 case 也能切换快速模式
切换不删除任何深度资产或证据
切换本身不生成音频
同一“开始完成”继续 Phase 2 真实 A/B 闭环
模式、阶段、按钮、磁盘事实一致
Canon 与 changelog 已同步
新增测试和全部回归通过
```

## 9. 交付报告

执行代理必须报告：

1. 修改文件清单；
2. Canon change 的 why / evidence / authority files / migration / rollback；
3. 旧门禁与新门禁的精确差异；
4. 截图 case 的人工复验结果；
5. 新增测试及全部回归结果；
6. 是否留下任何新的 `HUMAN_DECISION_REQUIRED`。

最终是否通过由主控独立验收，执行代理自评不构成完成。
