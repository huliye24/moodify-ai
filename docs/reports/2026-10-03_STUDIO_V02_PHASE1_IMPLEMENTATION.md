# Moodify Studio v0.2 第 1 期 — 实现说明

**日期：** 2026-10-03
**分支：** `deepseek/moodify-studio-v02-phase1`
**依据：** `Moodify Studio 产品定义（v0.2）`，状态 `APPROVED_BY_HUMAN`
**范围：** §7 第 1 期（本地最小可用）

---

## 1. 一句话结论

**第 1 期需要的 Core 能力全都已经存在，本次做的是接线，不是造引擎。**
后处理 = Core 的 `protocol process` 作业；导出 = Core 的 `finishing export`。
渲染层没有实现任何 DSP、没有计算响度、没有替用户做选择。

---

## 2. 缺口清单（§9 要求，实现前先给）

### 已存在，直接复用（未重造）

| 能力 | 位置 |
|---|---|
| 后处理执行 | `moodify-core-package/src/moodify/v01_pipeline.py:22` `process_audio()` |
| 协议作业执行 | `sound_protocol.py:129` `execute_job()` → `{status:"processed_review_required", source_sha256, output_sha256, core_parameters, diagnosis}` |
| 作业校验 | `sound_protocol.py:35` `validate_job()`（已内置「拒绝覆盖已存在输出」） |
| 预设 | `v01_presets.py`：`clean_master` / `warm_vocal` / `wide_space` |
| 导出编码 | `mix_graph/session.py:154` `export_delivery()` |
| 波形/播放 | `renderer/vendor/wavesurfer.min.js`（已 vendored） |
| 拖入音频、档案、图表、频谱 | `app.js` 既有函数 |

### 缺失，本次新建

| # | 缺口 | 实现 |
|---|---|---|
| G1 | 桌面**从未调用** MSP `process` 路径（13 处 Python 调用无一是它） | `src/backends/local.js` |
| G2 | 只有固定 A/B 二元组，无多版本列表 | `src/studio.js` + `view-studio` |
| G3 | 渲染产物无法试听（波形只加载源） | `mountStudioWave()` |
| G4 | GUI **完全没有**导出能力 | `studio:export`（复用 `export_delivery`） |
| G5 | 没有「选目标 → 一键处理」 | `studio:targets` / `studio:process` |
| G6 | 不显示 `processed_review_required` | 版本徽章「已处理，待人确认」 |
| G7 | 无 Backend 抽象（§3 硬要求） | `src/backends/{index,local}.js` |
| G8 | 无版本目录模型（§6） | `<case>/studio/versions/…` |
| G9 | `streaming_ready` 目标不存在 | 见 §4 D3 |
| G10 | desktop 不在任何 CI | `.github/workflows/studio.yml` + `npm test` |

---

## 3. D1 — case 模型：复用现有 case，不另起一套

产品书 §6 画的是 `case_id/{source.*, meta.json, versions/, selection.json, export/}`；
但 Core 的 `analyze_to_case` 已经为同一个目录产出
`<case>/{case.json, scan/, measurements.json, evidence.json, report.json|md|html}`。

**实现：版本层作为子树挂进现有 case**，不新建第二套 case 根：

```text
<case>/                      # Core 的 case，原样不动
  case.json  scan/  report.json …
  studio/                    # Studio 的版本层（本包新增）
    meta.json
    versions/
      ai_<attempt_id>/
        job.json
        out/<stem>_<preset>.wav
        evidence.json
    selection.json
    export/
```

**理由：** §5 要求复用已有能力；另起一套 case 根会造出两个都叫「case」、形状却不同的东西——
正是本仓库把 `protocol/` 变成两个协议那类错误。Core 仍是「case 是什么」与「处理做什么」的唯一权威；
Studio 只拥有「有哪些版本」和「人选了哪一版」。

原版是**指针**不是副本（复用 `source_path.json`），不重复占用磁盘。

---

## 4. D2 / D3 — 两处「不做」的判断

### D2：第 1 期不做 A/B，只做「原版 + 1 个 AI 版」

产品书 §5 说「同一目标下允许 1～2 组有限参数变体（**若 Core 支持**）；不支持则先做单版本 + 原版」；
§7 第 1 期只要求「至少 1 个 AI 版」，**A/B 明确排在 第 2 期**。

Core 的三个预设是固定 15 参数，**没有参数变体接口**。凭空造变体等于新增一套「什么更好听」的
音频权威，属 `AGENTS.md` 保留给人类的范围。故按文档自己的分期执行。

### D3：`streaming_ready` 第 1 期**不假装存在**

产品书 §2.1 列了 4 个目标，Core 只有 3 个预设。把它映射到 `clean_master` 而不说明，
等于按钮说「更适合流媒体」实际跑的是通用预设——**UI 承诺了它没做的事**。

**实现：** 只给 3 个真实目标；`streaming_ready` 显示为「即将推出」且**禁用**。
新增真正的 `streaming_ready` 预设需要定 15 个参数值，即决定「什么叫更适合流媒体」——
这是「什么叫更好听」的判断，**需人类确认参数后再加**。

---

## 5. 与现有代码的冲突点（§9 要求注明）

**没有发现需要偏离产品原则的冲突。** 两处需要说明：

1. **case 布局**（§3 上文）：产品书 §6 的图示与 Core 既有 case 布局不同。
   按 §5「复用已有能力」的优先级，采用子树方案并在 `src/studio.js` 顶部写明。
2. **`streaming_ready`**（§4 D3）：产品书 §2.1 的目标清单超出 Core 现有预设。
   按 §1.3「必须可对比、可回退」与「不虚构」的精神，标记为未实现而非静默映射。

既有 `compare`/`finishing` A/B 研究面板**未改动**——它是另一条路径（Mix Graph 渲染 + 研究账本），
本次不动它，避免同时改两套流程。

---

## 6. 验证

### 已验证（可复现）

| 项 | 结果 |
|---|---|
| `node scripts/check-contracts.js` | **通过** — DOM id 95→109、桥接 40→47、IPC 38→45 |
| `node scripts/test-studio.js` | **21 passed, 0 failed** |
| 真实音频端到端 | `validate → process → output.wav + evidence.json`，`status == processed_review_required` |
| 覆盖守卫 | 同一 attempt 目录重跑被 Core 拒绝（`refusing to overwrite`） |
| 「再试一次」 | 第二次尝试新增版本、不动第一版（3 个版本：原版 + 2 次尝试） |
| 云端后端 | **明确拒绝**并说明未实现，**不静默回退到本机** |
| 测试自身可失败 | 故意写错断言 → `20 passed, 1 failed`，退出码 1；复原 → 退出码 0 |

### 未能验证（必须由人在本机确认）

> **我无法看到 Electron 窗口。** 拖入、按钮、波形渲染、播放、导出对话框等**视觉与交互**
> 没有被自动验证过。本节不做「界面已工作」的声明——只声明：
> 静态合约通过 + 处理链路用真实音频跑通 + 导出产出真实文件。

本机确认方式：

```bash
cd moodify-desktop && npm start
# 拖入一首歌 → 选目标 → 让 AI 处理 → 听原版与 AI 版 → 用这个版本 → 导出
```

### 关于测试本身的一个缺陷（如实记录）

`test-studio.js` 的第一版用同步 `check()` 包裹 `async` 回调，助手不 await，
于是**四个检查（含覆盖守卫）在没有真正断言的情况下报了 ok**——是假通过。
已修复（`check` 现在 async，21 处调用全部 await），并补了「故意写错断言」的负对照确认它能失败。
测试工具的 bug 比测试失败更危险：它会制造信心。

---

## 7. 交付物

**新建**
```
moodify-desktop/src/backends/index.js   后端注册表 + 契约（§3）
moodify-desktop/src/backends/local.js   本机后端：protocol process + evidence
moodify-desktop/src/studio.js           版本层：attempt/versions/selection/meta（§6）
moodify-desktop/scripts/test-studio.js  无头行为测试（21 项，含真实 Core 链路）
.github/workflows/studio.yml            desktop 首次进入 CI
```

**修改**
```
moodify-desktop/src/main.js             +registerStudioV02Ipc()：7 个 IPC
moodify-desktop/src/preload.js          +7 个桥接方法
moodify-desktop/renderer/index.html     +view-studio（14 个 id）+ rail-studio
moodify-desktop/renderer/app.js         +Studio 段：目标/处理/版本/试听/导出
moodify-desktop/renderer/style.css      +Studio 样式
moodify-desktop/package.json            +check:contracts / test
```

**Core 未改一行。** 没有新增预设、没有改 DSP、没有改协议。

---

## 8. 第 1 期验收标准（§8）对照

| 标准 | 状态 |
|---|---|
| 不懂音频参数的人能在 10 分钟内：丢歌 → 处理 → 听原版与 AI 版 → 选一版并导出 | **待人类本机确认**（流程已接通，视觉未验证） |
| 全过程不必打开任何参数面板 | 已满足 — `view-studio` 无任何参数控件 |
| 原版始终可回听；导出前必须有一次明确确认 | 已满足 — 原版恒在版本列表首位；导出走 `dialog.showSaveDialog` 显式确认 |
| 每次 AI 处理都有可查 evidence（hash + 目标/预设） | 已满足 — `evidence.json` 每版一份；UI 显示 hash 前 12 位 |
| 本地模式可完全离线完成 | 已满足 — 全链路走本机 Core，无网络调用 |

---

## 9. 未做（§7 明确排除 / 后续分期）

完整可编辑 Mix Graph · 上链/MOOD 贡献值 · 移动端 · 参数墙 ·
云端真实接通（接口已留，后端明确拒绝）· 参数变体 A/B（第 2 期）·
历史 case 内的版本回顾 UI（第 2 期）· 自然语言目标（第 3 期）·
`streaming_ready` 真实预设（需人类确认参数）· 处理过程逐行进度流（当前为忙碌态）。

---

## 10. HUMAN_DECISION_REQUIRED

1. **`streaming_ready` 的 15 个参数值**——「什么叫更适合流媒体」是听觉判断，需人类确认后才加预设。
2. **第 1 期验收**——§8 第一条要求「一个不懂音频参数的人 10 分钟内完成」，
   只能由人在本机实跑确认，我不能代填。
