# Moodify Desktop — 一键完成机 Phase 2：第一条真实 A/B 闭环（实现报告）

**Date:** 2026-10-04
**Status:** IMPLEMENTED（Core 侧 EXPERIMENTAL）— 待主控独立验收
**Owner / final acceptance:** Codex（主控）
**CANON_CHANGE:** NO
**MIP:** `protocol/mips/MIP-0002-stem-tuning-loop.md` **Addendum A**（`DRAFT`，本阶段先更新再实现）
**任务包:** [`docs/plan/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_REAL_AB.md`](../plan/2026-10-04_DESKTOP_ONE_CLICK_PHASE2_REAL_AB.md)
**前置:** [`docs/plan/2026-10-04_DESKTOP_ONE_CLICK_PHASE1.md`](../plan/2026-10-04_DESKTOP_ONE_CLICK_PHASE1.md)（Phase 1 已验收）
**契约:** [`docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`](../canon/STUDIO_PRODUCTION_PIPELINE_V4.md)

---

## 1. 本阶段的产品结果

> **一首真实歌曲第一次从 Desktop 走到两个真实可听候选：原版 / A（保守） / B（充分），
> 复检完成后由人选择并导出。**

打通的路径是 Canon 已允许的 **快速完成（仅立体声）**：

```text
导入歌曲（Core 真实检测）
  → 用户显式选择「使用快速完成（仅立体声）」        ← 一次人类动作，绝不自动
  → 一次「开始完成」：Core render-pair 产出 A / B 两个完整整轨候选
  → Core 对 A、B 各重跑一次完整检测 → recheck.json 三方对齐
  → REVIEW：同位置试听 原版 / A / B
  → 人选定 A / B / 保留原版（同一道准入）
  → 导出
```

深度路径（逐轨音准·节奏修正、多轨复合）**仍未实现**，继续显式拒绝
`TUNABLE_CORE_NOT_AVAILABLE`；快速路径可用**没有**解锁它。

## 2. Gate 0 — MIP-0002 增补（先于实现）

`MIP-0002` 仍是 `DRAFT`（未标 `ACCEPTED`、未标 `IMPLEMENTED`）。新增 **Addendum A**：

| 增补内容 | 位置 |
|---|---|
| tier 词汇：A=`conservative`、B=`full`（`aggressive` 为旧措辞，同义） | §A.1 |
| 新 CLI 面 `moodify tuning render-pair --mode fast-stereo-only` | §A.2 |
| tier descriptor 的规范字段（含 `calibration_status`、`preserve`、全部节点参数） | §A.3 |
| 参考实现的工程默认参数（明确标注未校准，B 不代表更好） | §A.4 |
| 允许的处理（仅既有 `mix_graph` primitives）与**禁止声称**的事 | §A.5 |
| 原子产物与发布规则（临时 attempt → 全部成功才重命名） | §A.6 |
| evidence 规范字段（逐侧，内嵌 Core mix-graph evidence 原文） | §A.7 |
| 硬门禁（可解码/时长/SR/声道/NaN/峰值/双侧完成） | §A.8 |
| 失败契约、兼容与回滚 | §A.9–A.10 |
| **明确不在本阶段**：逐轨修音、多轨复合、`tuning roundtrip` | §A.11 |

同时更新：Unresolved #5（快速路径如何与逐轨 MIP 共存）已由附录 A 回答；
Reference implementation 段落说明附录 A 有 EXPERIMENTAL 参考实现、但不满足主规范。

## 3. Core 命令与契约

```bash
moodify tuning render-pair \
  --mode fast-stereo-only \
  --source <case>/song.wav \
  --output-dir <case>/studio/tuning/<pair_id> \
  --pair-id <pair_id>
```

- stdout 一个 JSON 对象；失败时 stderr 一个 JSON 对象且退出码 2。
- 一次调用产出**一对**：`pair.json` + `A/`、`B/`，每侧 `plan.json` / `evidence.json` /
  `mix.wav` / `tuned/source.wav`。
- 复用既有 `moodify.mix_graph` 会话（`run_session`）渲染 → **一个 DSP 权威**，无新引擎、无第二套参数体系。
- 拒绝：未知 mode/tier、源缺失或不可解码、目标目录已存在、任一侧渲染或门禁失败、两档输出逐字节相同。

## 4. A/B 两档的实际参数与校准状态

`calibration_status = UNCALIBRATED_ENGINEERING_DEFAULT`（工程默认，人类尚未校准；B 只代表变化更充分）。

```text
A / conservative                        B / full
  eq  highshelf 10 kHz  +0.5 dB           eq  highshelf 10 kHz  +1.5 dB
                                          eq  peak 250 Hz  -1.0 dB  q 0.7
  comp  thr -14 dB  ratio 1.2             comp  thr -18 dB  ratio 1.5
        attack 35 ms  release 250 ms            attack 25 ms  release 220 ms
  limiter  ceiling -1.0 dB                stereo  width 1.08
           input_gain 0.0 dB              limiter  ceiling -1.0 dB
                                                  input_gain +0.5 dB
```

## 5. 真实音频运行记录

`moodify-desktop/scripts/test-main-ipc.js` §7 用**真实 Core** 跑完整闭环（合成 1.5 s 立体声，
22050 Hz，不提交任何 WAV）。每次运行的产物落在临时 cases-root；观察到的产物形状：

```text
<case>/studio/tuning/tune_<utcstamp17>_<rand4>/
  pair.json     mode=FAST_STEREO_ONLY, tiers={A:conservative,B:full}, source_sha256=…
  A/ plan.json  evidence.json  mix.wav  tuned/source.wav
  B/ plan.json  evidence.json  mix.wav  tuned/source.wav
  recheck.json  三方逐指标对齐（original/A/B 的 measurement_count 均 > 0）
```

断言：A、B 的 `mix_sha256` 不同；两侧 evidence 的 `output.mix_sha256` 可对文件重算；
`graph_digest_sha256` 可由 `plan.json` 的节点参数重算；每条硬门禁 `passed=true`；
发布后目录里**没有** `.attempt` 残留；`tuned/source.wav` 与 `mix.wav` 同源同哈希。

### 5.1 一次留档运行（合成 3.0 s 立体声 22050 Hz）

```bash
moodify tuning render-pair --mode fast-stereo-only \
  --source <run>/song.wav --output-dir <run>/studio/tuning/tune_record_0001 \
  --pair-id tune_record_0001        # 退出码 0
```

| | A / conservative | B / full |
|---|---|---|
| `mix.wav` sha256[:16] | `a0a266e103b760c9` | `609742dcf3a0b29e` |
| graph digest[:16] | `a4943f0de047bf33` | `549a16e5f9a063c4` |
| 节点 | eq, compressor, limiter | eq, compressor, stereo, limiter |
| LUFS before → after | −11.16 → −11.50（Δ −0.34） | −11.16 → −12.99（Δ −1.83） |
| crest Δ | +0.08 | +0.62 |
| sample peak before → after | −9.63 → −9.64 | −9.63 → −9.60 |
| peak gate（limit −1.0 dBFS） | passed（−9.64） | passed（−9.60） |
| invariants | channels/finite/length 全 True | 同左 |
| 硬门禁 6 条 | 全 passed | 全 passed |

源 `song.wav` sha256[:16] = `312254414a81e9b3`；`pair.json`：`mode=FAST_STEREO_ONLY`、
`tiers={A:conservative,B:full}`、`calibration_status=UNCALIBRATED_ENGINEERING_DEFAULT`、
`engine_version=1.0.0-rc.1`。产物：`pair.json` + `A|B/{plan.json,evidence.json,mix.wav,tuned/source.wav}`。

**如实观察：** 两档都没有把素材变响（A −0.34 LU、B −1.83 LU，B 压缩更明显）。
这不是缺陷，而是这两组工程默认值的真实结果；也正因如此，「保留原版」是必要时正确的第三出口——
机器只报「变了什么」，不报「更好」。

## 6. Desktop 完整操作路径

```text
1. 拖入/选择一首歌                     → Core 真实检测，建立 world（report.json）
2. 主界面出现「使用快速完成（仅立体声）」  ← 深度完成当前不可用；这是**人的显式决定**
3. 模式徽章变为「快速（仅立体声）」，相位条显示 ②③ 与可逆性为 skipped（划掉）
4. 点「开始完成」                       → 一次 Core render-pair → 自动复检 → REVIEW
5. 同位置试听 原版 / A / B              → 选择 A / B / 保留原版（统一准入）
6. 导出                                 → Core delivery 编码 + 保存对话框
```

- **未显式选择时**：一键启动走深度链条，绝不生成候选、绝不出现 skipped 相位（测试钉住）。
- **失败时**：进入 `STEP_FAILED` 可见态，显示阶段、Core 返回的真实原因、是否可重试、
  是否留下临时产物、以及「本次没有生成任何候选版本」；重试会真的再调一次 Core。
- **不覆盖**：再次生成会开出新的一对，旧候选与账本都不被动过。

## 7. 测试与结果

```text
cd moodify-core-package && python -m pytest -q
  → 1207 passed, 5 skipped（含新增 tests/test_tuning_pairs.py 22 条）

cd moodify-desktop && npm test
  → check-contracts ✓
    test-pipeline      51/51
    test-recheck        9/9
    test-session       31/31（含快速路径的相位投影）
    test-orchestrator  16/16（含「一对只生成一次」「失败→BLOCKED」「未选择不走快速路径」）
    test-main-ipc      24/24（其中 9 条跑真实 Core 的纵向闭环）
    test-studio        21/21

python scripts/check_repo_structure.py → OK
```

失败注入（§8.3）：

| 注入 | 期望 | 结果 |
|---|---|---|
| 未显式选择快速完成 | 不生成候选、不出现 skipped 相位 | ✓ |
| Core 侧 B 分支失败（Core 单测 monkeypatch `run_session`） | 不发布 pair、不留 attempt | ✓ |
| 源不是音频（真实 Core 失败） | `BLOCKED` + Core 真实原因、无 pair、无 attempt | ✓ |
| 只有 A 侧成品的半成品 | 不进 `REVIEW`，如实 `NO_PROGRESS` | ✓ |
| 两档输出相同 | 拒绝发布（两个相同候选不是两个候选） | ✓ |
| 目标目录已存在 | 拒绝且不改动既有产物 | ✓ |
| 人工选定前的导出 | `NOT_CHOSEN`，且不打开保存对话框 | ✓ |
| 已有完整一对后再启动 | 从现有产物继续、不重跑 Core、不改动旧 pair | ✓ |
| 重试（失败之后） | 真的再调一次 Core，成功后进入 `REVIEW` | ✓ |
| 原版 / A / B 试听数据面 | 三路都返回真实 WAV 字节，且 A≠B、原版≠A | ✓ |

## 8. 尚未实现（不得写成已实现）

- 逐轨音准修正 / 节奏修正（以 MIDI 为参考）：Core 无此能力。
- 多轨复合（逐轨处理 + 整曲合成）：Core 无此能力。
- `moodify tuning roundtrip`：本阶段**故意不实现**——没有来源化的 `passed` 判据，
  写 `passed: true` 就是伪造门禁；深度 ④ 因此继续锁定（V4 §4.1）。
- 精细分离引擎、云端/网络/账户：未实现。

## 9. HUMAN_DECISION_REQUIRED

1. **两档参数由谁签字？**（MIP-0002 Unresolved #1）现有值是工程默认，必须经人类校准后
   才能改变 `calibration_status`。本阶段未自行宣称任何听感结论。
2. **「深度就绪但不可逆」的 case 是否应仍提供快速完成？** 按 V4 §4.2「深度优先」，此时
   `canTune` / `canTuneQuick` / `canRequestQuick` 全为假，用户拿不到任何候选。
   本轮**未**修改 Canon，只如实记录（V4 §9）。
   → **2026-10-04 已裁定并实施（Phase 2.1）**：入口依据改为 `!deepExecutable`，人的显式选择优先，
   切换必须由人确认。见 [`CANON_CHANGELOG.md`](../canon/CANON_CHANGELOG.md) 2026-10-04 条目与
   [`2026-10-04_DESKTOP_ONE_CLICK_PHASE2_1_MODE_SWITCH.md`](2026-10-04_DESKTOP_ONE_CLICK_PHASE2_1_MODE_SWITCH.md)。
3. **快速完成是否需要一个「一键重跑检测」的入口？** 当源音频不可解码/被移动时，
   目前只能重新导入（检测会建立新的世界）。
