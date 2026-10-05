/**
 * Studio production pipeline — stages, gating, context.
 *
 * CONTRACT: docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md
 *
 * PRODUCT PRINCIPLE (V4, 2026-10-04):
 *     Understand first. Decompose second. Tune third. Compose fourth. Verify fifth.
 *     先理解，再分解，再修音，再复合，最后复检。
 *
 * Why this file exists, and what it replaced
 *   V3 let a case be processed as a stereo master with one of three presets. 2026-10-04 the
 *   human direction changed the shape of the back half:
 *
 *     检测 → 分轨 → 结构 → 修音 → 复合 → 复检 → 选定 → 导出
 *     ANALYZE → SEPARATE → STRUCTURE → TUNE → COMPOSE → RECHECK → CHOOSE → EXPORT
 *
 *   1. Processing targets the **stems**, not the stereo master. A single out-of-tune part
 *      cannot be corrected by a whole-mix chain.
 *   2. 修音 and 复合 are **separate stages**. 修音 changes each part (pitch / timing / per-stem
 *      processing); 复合 decides how they stack (balance / space / loudness). Merging them
 *      makes "this step got worse" unattributable, and attribution is a hard requirement here.
 *   3. The three presets (clean_master / warm_vocal / wide_space) **retired**. They were the
 *      V3 "finish" tool; there is no finish stage any more.
 *   4. ②「问题」is no longer its own stage. Core's `findings` stay visible in ①检测.
 *
 * STAGE IS DERIVED, NOT HAND-ADVANCED
 *   Nothing here records "the user clicked next". Every stage is derived from the artifacts
 *   actually on disk. Delete the tuning pair and the case falls back out of TUNED by itself.
 *   A stored stage that says COMPOSED while the mixes are gone is exactly the kind of lie
 *   this repository keeps having to remove.
 *
 *   `pipeline.json` therefore records the derived result and its history. It is a record,
 *   not an authority.
 *
 * THE REVERSIBILITY GATE (new in V4)
 *   Decomposition is information-losing: the original stems of a generated mix are not
 *   knowable. So "did we recover the right stems" is unanswerable, while
 *   "does decompose → compose (with no processing) return the original" is measurable.
 *
 *   `canTune` therefore requires `reversible`, which is read from
 *   `<case>/studio/roundtrip.json` (written by Core; `passed: true`). Until the engine can
 *   produce it, ④修音 stays locked — it does not silently unlock on a bad decomposition, and
 *   it does not pretend the gate passed. This is the whole reason the premise "multi-stem
 *   beats single-stem" can be adopted safely: the system cannot emit a re-composite that
 *   drifts from the original without the gate noticing.
 *
 * THE THIRD EXIT
 *   `canChoose` leads to A / B / **ORIGINAL** (see src/tuning.js). If both tiers are worse
 *   than the untouched original, "keep the original" must be a real, recordable choice —
 *   otherwise minimal-transformation is a slogan rather than a rule.
 *
 *   All three exits pass the same gate: a decision only exists when it is backed **right now**
 *   by a pair with two complete candidates (A and B mixes) and a real recheck
 *   (`tuning.validateDecision`). `chosen` is derived from that, not from "a line exists in the
 *   ledger": otherwise an unbacked record — written by an older build, by hand, or left behind
 *   after the candidates were deleted — would push the case to CHOSEN and unlock ⑧导出.
 *   ORIGINAL is inside the same gate on purpose: it is the exit for "both tiers are worse",
 *   not a way to deliver the untouched source before A/B ever existed.
 *
 * ② 问题 / ⑤ 方案 已删除（2026-10-04）
 *   `buildDiagnosis` / `preparePlan` 及其同伴在壳接线搬走后已从本文件移除。Core 的 findings
 *   仍在 ①检测 的 report 里可见，但不再有独立阶段或产物。诚实要求不变：
 *   「无 finding」只能说「当前规则未发现技术问题」，绝不说「这首歌没问题」——
 *   这句话现在由 ①检测 页承接。
 */

'use strict';

const fs = require('fs');
const path = require('path');

const tuning = require('./tuning');

// ── stages ──────────────────────────────────────────────────────────────────────

/**
 * Ordered stages (V4).
 *
 * READY_FOR_TUNE is deliberately absent even though it is a valid state name: it is a
 * *readiness* fact (`deepReady ∧ reversible`), not something the user did. V3 learned this
 * the hard way — including a readiness state in the cursor made every analysed case claim
 * progress the user had not made. Readiness is reported through `gates()` instead.
 */
const STAGES = Object.freeze([
  'IMPORTED',
  'ANALYZED',
  'SEPARATED',
  'STRUCTURED',
  'TUNED',
  'COMPOSED',
  'RECHECKED',
  'CHOSEN',
  'EXPORTED',
]);

const STAGE_INDEX = Object.freeze(
  Object.fromEntries(STAGES.map((s, i) => [s, i])),
);

function readJsonSafe(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return null; }
}

function listFiles(dir, exts) {
  let entries = [];
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return []; }
  return entries
    .filter((e) => e.isFile() && exts.some((x) => e.name.toLowerCase().endsWith(x)))
    .map((e) => path.join(dir, e.name))
    .sort();
}

// ── artifacts on disk ───────────────────────────────────────────────────────────

/** Everything the pipeline can see about a case. Pure read; never writes. */
function inspect(caseDir) {
  const reportPath = path.join(caseDir, 'report.json');
  const report = readJsonSafe(reportPath);

  const stemsDir = path.join(caseDir, 'stems');
  const stemWavs = listFiles(stemsDir, ['.wav']);
  const stemsManifestPath = path.join(stemsDir, 'manifest.json');
  const stemsManifest = readJsonSafe(stemsManifestPath);

  const midiFiles = listFiles(path.join(caseDir, 'midi'), ['.mid', '.midi']);
  const scoreFiles = listFiles(path.join(caseDir, 'score'), ['.musicxml', '.xml']);

  const studioDir = path.join(caseDir, 'studio');
  const roundtripPath = path.join(studioDir, 'roundtrip.json');
  const roundtrip = readJsonSafe(roundtripPath);

  // 达成度用聚合（任一成对的 pair 达到即可），因为做完一对再开新的一对是往前走、不是倒退。
  // `currentPair` 仍是最新一对，供 UI 决定"现在在操作哪一对"。
  const agg = tuning.aggregate(caseDir);
  // ⑦ 的选定不光要「有一条记录」，还要**此刻仍被一对完整候选 + 复检支撑**
  // （tuning.validateDecision 是唯一那条规则，写与读共用）。理由见 factsOf.chosen。
  const decisionBacked = tuning.decisionBacked(caseDir);
  const decision = decisionBacked.decision;
  // 当前这一对能不能被选定；闭着的时候把原因一并给出，好让 UI 说清「还差什么」
  const currentPairId = agg.current ? agg.current.pair_id : null;
  const decisionBlockers = currentPairId ? tuning.decisionBlockers(caseDir, currentPairId) : [];

  const exportDir = path.join(studioDir, 'export');
  const exports = listFiles(exportDir, ['.json']);

  return {
    caseDir,
    reportPath,
    report,
    hasReport: Boolean(report),
    caseId: (report && report.case && report.case.case_id) || null,

    stemsDir,
    stemWavs,
    stemsManifestPath,
    stemsManifest,
    hasStems: stemWavs.length > 0,

    midiFiles,
    scoreFiles,
    // MIDI is the required machine-readable structure for Deep Tune. Score/MusicXML is an
    // optional derived interpretation: worth discovering and citing, but it never substitutes
    // for MIDI when deciding whether the song has been decomposed.
    hasMidi: midiFiles.length > 0,
    hasStructure: midiFiles.length > 0 || scoreFiles.length > 0,

    roundtripPath,
    roundtrip,
    hasRoundtrip: Boolean(roundtrip),
    // Only an explicit `passed: true` counts. A missing or failed roundtrip keeps ④修音 locked.
    reversible: Boolean(roundtrip && roundtrip.passed === true),

    tuningDir: tuning.tuningDir(caseDir),
    pairs: agg.pairs,
    currentPair: agg.current,
    // 达成度聚合 —— 与 currentPair 分开，见 factsOf
    anyTuned: agg.any_tuned,
    anyComposed: agg.any_composed,
    anyRechecked: agg.any_rechecked,
    chosenPair: agg.chosen_pair,
    decisions: agg.decisions,
    decision,
    decisionValid: decisionBacked.valid,
    decisionReason: decisionBacked.reason,
    decisionBlockers,

    exportDir,
    exports,
    hasExport: exports.length > 0,
  };
}

/** Boolean checklist behind the stages — the thing the UI gates on. */
function factsOf(info) {
  const analyzed = info.hasReport;
  const separated = info.hasStems;
  const structured = info.hasMidi; // MIDI specifically — score alone is not decomposition
  return {
    imported: Boolean(info.caseDir) && fs.existsSync(info.caseDir),
    analyzed,
    separated,
    structured,
    // 分解→复合可逆：唯一的分解质量代理（原分轨不可知）
    reversible: info.reversible,
    // 成对即成立；单边是半成品，不成阶段。
    // 用聚合而非最新一对：开一对新实验不应让阶段倒退。
    tuned: info.anyTuned,
    composed: info.anyComposed,
    rechecked: info.anyRechecked,
    // 三出口里的任何一个都算已选，包括 ORIGINAL —— 但只有在**此刻**仍被一对完整候选
    // 与一次真实复检支撑时才算。一条没有候选支撑的记录（旧版本写的、手写的、或候选后来
    // 被删掉的）不能把阶段推到 CHOSEN、更不能解锁 ⑧导出：那正是「未完成被显示成完成」。
    // 与「产物没了就退回」同一条纪律：账本可以留着，事实由磁盘重新推导。
    chosen: Boolean(info.decisionValid),
    exported: info.hasExport,
    // Readiness facts, not stages.
    baseReady: analyzed,
    deepReady: analyzed && separated && structured,
  };
}

/**
 * Stage order with the fact each one requires.
 *
 * `optional: true` means a legitimate path may skip it — the FAST stereo-only route never
 * separates or structures. Skipping an optional does NOT stop the walk; missing a required
 * one does.
 */
const STAGE_TABLE = Object.freeze([
  { stage: 'IMPORTED', fact: 'imported' },
  { stage: 'ANALYZED', fact: 'analyzed' },
  { stage: 'SEPARATED', fact: 'separated', optional: true },
  { stage: 'STRUCTURED', fact: 'structured', optional: true },
  { stage: 'TUNED', fact: 'tuned' },
  { stage: 'COMPOSED', fact: 'composed' },
  { stage: 'RECHECKED', fact: 'rechecked' },
  { stage: 'CHOSEN', fact: 'chosen' },
  { stage: 'EXPORTED', fact: 'exported' },
]);

/** The furthest stage whose condition currently holds. */
function stageOf(facts) {
  let reached = 'IMPORTED';
  for (const { stage, fact, optional } of STAGE_TABLE) {
    if (facts[fact]) { reached = stage; continue; }
    if (!optional) break; // a required prerequisite is missing: nothing beyond is reached
  }
  return reached;
}

function finishModePath(caseDir) {
  return path.join(caseDir, 'studio', 'finish_mode.json');
}

function readFinishMode(caseDir) {
  return readJsonSafe(finishModePath(caseDir)) || {};
}

/**
 * The recorded human choice to skip decomposition for this case.
 *
 * Deliberately a persisted artifact rather than a checkbox: "the user chose the shortcut"
 * is a decision worth being able to point at later. The FAST route still has to walk
 * ④修音 → ⑤复合 → ⑥复检 → ⑦选定 — it skips *decomposition*, not verification.
 *
 * @param {'QUICK_STEREO_ONLY'|null} mode  null clears the opt-in (file removed)
 */
function recordFinishMode(caseDir, mode, note) {
  const file = finishModePath(caseDir);
  if (!mode) {
    try { fs.rmSync(file, { force: true }); } catch { /* already gone */ }
    return {};
  }
  const payload = {
    schema: 'moodify.studio.finish-mode/0.1',
    mode,
    note: note || null,
    chosen_at: new Date().toISOString(),
    reason: '用户显式选择跳过逆向分解；深度路径需 分轨 + MIDI + 可逆性通过 三者齐备。',
  };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(payload, null, 2), 'utf8');
  return payload;
}

/**
 * 深度路径真正需要的能力。它们目前仍在 PLANNED_CAPABILITIES 里（Core 未实现），
 * 所以 `deepExecutable` 恒为 false —— **这是如实反映现状**，并且会随能力清单自动翻转：
 * 一旦逐轨能力真的可用（从 PLANNED 移到 CAPABILITIES），深度路径就会成为默认可执行路径，
 * 快速入口也随之不再主动提供。不需要另一处硬编码开关。
 *
 * 具体的可得性常量在 CAPABILITIES / PLANNED_CAPABILITIES 定义之后计算（见下方
 * `AVAILABLE_CAPABILITY_IDS`），因为 const 有暂时性死区，不能提前引用。
 */
const DEEP_CORE_CAPABILITY_IDS = Object.freeze(['stem-tuning', 'multi-stem-compose']);
const FAST_PAIR_CAPABILITY_ID = 'fast-stereo-pair';

/** 阻断原因码 → 给人看的一句话。分开列，UI 才能说清「差什么、怎么补」。 */
const DEEP_BLOCKER_LABELS = Object.freeze({
  NOT_ANALYZED: '尚未检测（缺 report.json）',
  NO_STEMS: '尚未逆向分解（缺 stems/*.wav）',
  NO_MIDI: '尚缺 MIDI（曲谱不能替代）',
  NO_ROUNDTRIP: '可逆性未验证（缺 studio/roundtrip.json；Core 尚未产出）',
  ROUNDTRIP_FAILED: '可逆性未通过：分解 → 复合 未能回到原版',
  DEEP_CORE_UNAVAILABLE: '深度路径的逐轨修音 / 复合能力尚未就绪（Core 未实现，见 MIP-0002）',
});

/**
 * 模式决策 —— 唯一的实现（纯函数，便于钉住「未来深度可执行时仍默认 DEEP」）。
 *
 * ```text
 * deepAssetsReady = analyzed ∧ separated ∧ structured
 * deepExecutable  = deepAssetsReady ∧ reversible ∧ 深度 Core 能力可用
 * fastAvailable   = analyzed ∧ 整轨两档能力可用
 *
 * deepExecutable → 默认 DEEP，不提供快速入口
 * !deepExecutable → canRequestQuick（提供显式入口，人不选就不生成候选）
 * optIn          → mode = FAST_STEREO_ONLY（人的选择优先，不被 deepAssetsReady 覆盖）
 * ```
 *
 * @param {object} facts  pipeline.inspect 推导出的事实
 * @param {{optIn?:boolean, deepCoreAvailable?:boolean, fastAvailable?:boolean}} [options]
 *        能力可得性只在测试里显式传入，用来验证「深度能力到位的未来」这一分支。
 */
function modeDecision(facts, options = {}) {
  const optIn = options.optIn === true;
  const deepCoreAvailable = options.deepCoreAvailable === undefined
    ? DEEP_CORE_AVAILABLE : options.deepCoreAvailable === true;
  const fastCapability = options.fastAvailable === undefined
    ? FAST_PAIR_AVAILABLE : options.fastAvailable === true;

  const deepAssetsReady = Boolean(facts.deepReady);
  const reversible = Boolean(facts.reversible);
  const deepExecutable = deepAssetsReady && reversible && deepCoreAvailable;
  const fastAvailable = Boolean(facts.baseReady) && fastCapability;
  const quick = fastAvailable && optIn;
  // 人的显式选择优先：optIn 之后不再看 deepAssetsReady。
  const mode = quick ? 'FAST_STEREO_ONLY' : (deepAssetsReady ? 'DEEP' : null);
  const modeLabel = mode === 'DEEP' ? '深度完成'
    : (mode === 'FAST_STEREO_ONLY' ? '快速（仅立体声）' : null);

  return {
    deepAssetsReady,
    deepExecutable,
    deepCoreAvailable,
    fastAvailable,
    reversible,
    quickOptIn: optIn,
    quick,
    // 入口依据是「深度现在跑不了」，不是「深度资产还没凑齐」（2026-10-04 裁定）。
    canRequestQuick: fastAvailable && !deepExecutable && !optIn,
    mode,
    modeLabel,
    // 当前模式这条路此刻是否真的能走完（UI 用它决定要不要说「暂不可用」）。
    modeExecutable: mode === 'FAST_STEREO_ONLY' ? quick : deepExecutable,
  };
}

/**
 * What the UI may enter.
 *
 *     ④ 修音（深度）  deepAssetsReady ∧ 可逆性通过 ∧ 深度 Core 能力可用 = deepExecutable
 *     ④ 修音（快速）  analyzed ∧ 整轨两档能力可用 ∧ 人已显式选择 QUICK_STEREO_ONLY
 *     ⑤ 复合          ④ 已产出成对的 tuned 产物
 *     ⑥ 复检          ⑤ 已产出成对的 mix.wav
 *     ⑦ 选定          ⑥ 已完成（recheck.json 存在）
 *     ⑧ 导出          ⑦ 已有决策记录（A / B / ORIGINAL 皆可）
 *
 * `tuneBlockers` exists so the UI can say *why* ④ is locked instead of showing a dead
 * button. The reasons are genuinely different problems with genuinely different remedies, and
 * collapsing them into one greyed button is the kind of vagueness that makes a gate feel
 * arbitrary.
 *
 * 2026-10-04 人类裁定（Phase 2.1，CANON_CHANGE = YES）
 *   「有 stems + MIDI」只证明深度**资产**存在，不等于深度路径**当前可执行**。旧规则用
 *   `!deepReady` 决定是否提供快速入口，于是「资产已存在 + 逐轨能力未实现」的 case 三处门禁
 *   全为假（`canTune` / `canTuneQuick` / `canRequestQuick`），用户拿不到任何候选——一条死路。
 *   现在入口依据 `!deepExecutable`，且**人的显式选择优先**：写下 QUICK_STEREO_ONLY 之后，
 *   `mode` 就是 FAST_STEREO_ONLY，不再被 `deepAssetsReady` 覆盖回 DEEP。详见 V4 §4.2.0。
 */
function gates(info) {
  const f = factsOf(info);
  const optIn = readFinishMode(info.caseDir).mode === 'QUICK_STEREO_ONLY';
  const decision = modeDecision(f, { optIn });
  const { deepAssetsReady, deepExecutable, quick } = decision;

  // 深度路径的阻断原因（代码 + 人话）。分开列出是为了让 UI 能区分
  // 「还没做分轨 / 缺 MIDI」「可逆性未验证或未通过」「逐轨能力未就绪」这三种补救。
  const deepBlockers = [];
  if (!f.analyzed) deepBlockers.push('NOT_ANALYZED');
  if (f.analyzed && !f.separated) deepBlockers.push('NO_STEMS');
  if (f.analyzed && !f.structured) deepBlockers.push('NO_MIDI');
  if (deepAssetsReady && !f.reversible) {
    deepBlockers.push(info.roundtrip ? 'ROUNDTRIP_FAILED' : 'NO_ROUNDTRIP');
  }
  if (deepAssetsReady && !decision.deepCoreAvailable) deepBlockers.push('DEEP_CORE_UNAVAILABLE');
  const deepTuneBlockers = deepBlockers.map((code) => DEEP_BLOCKER_LABELS[code]);

  // 快速完成是**另一条合法路径**，不是「缺前置的深度路径」。
  // 人已经显式选择它之后，还拿「尚未逆向分解」去解释 ④ 为什么锁着，就是在说假话：
  // 这条路本来就不需要分轨。所以此时阻断清空，模式徽章承担说明责任（V4 §4.2）。
  const effectiveTuneBlockers = quick ? [] : deepTuneBlockers;

  return {
    canSeparate: f.analyzed,
    canStructure: f.analyzed,
    baseReady: f.baseReady,
    // 资产存在 ≠ 可执行。两个名字都保留，是为了让调用方无法再把它们混为一谈（V4 §3.4）。
    deepAssetsReady,
    deepReady: deepAssetsReady, // 兼容旧调用方：它一直只表示「资产齐备」
    deepExecutable,
    deepCoreAvailable: decision.deepCoreAvailable,
    fastAvailable: decision.fastAvailable,
    reversible: f.reversible,
    // ④ 修音（深度）— the reversibility + capability gate lives here
    canTune: deepExecutable,
    tuneBlockers: effectiveTuneBlockers,
    // 同一份深度阻断原样保留：说明「深度路径为什么还锁着」，即使快速路径此刻是开的。
    // 快速完成可用不等于深度可用（V4 §4.2 明令深度不得被自动解锁）。
    deepTuneBlockers,
    deepBlockers,
    // FAST route: 整轨两档，需要人显式选择；仍要走 修音/复合 → 复检 → 选定。
    // 入口依据是 `!deepExecutable`（2026-10-04 裁定），不再是 `!deepAssetsReady`。
    canRequestQuick: decision.canRequestQuick,
    canTuneQuick: quick,
    quickOptIn: optIn,
    canCompose: f.tuned,
    composeBlockers: f.tuned ? [] : ['④ 修音尚未产出成对的 A / B 修音结果'],
    canRecheck: f.composed,
    recheckBlockers: f.composed ? [] : ['⑤ 复合尚未产出成对的 A / B mix'],
    canChoose: f.rechecked,
    // ⑦ 进入之后还有一道独立的事：这一对**此刻**能否被选定（两侧候选 + 复检都真实存在）。
    // 分开报是因为补救不同：前者是「还没做复检」，后者是「复检有了，但候选/复检产物不完整」。
    chooseBlockers: f.rechecked
      ? info.decisionBlockers.slice()
      : ['⑥ 复检尚未完成（缺 recheck.json）'],
    canExport: f.chosen,
    exportBlockers: f.chosen ? [] : [
      info.decision && !info.decisionValid
        ? `⑦ 的选定没有被完整候选支撑（${info.decisionBlockers[0] || info.decisionReason}），⑧ 不开放`
        : '⑦ 尚未选定（A / B / 保留原版）',
    ],
    exits: [...tuning.EXITS],
    // 模式来自 modeDecision()：人的显式 FAST 选择优先，不再被 deepAssetsReady 覆盖（V4 §4.2.0）。
    mode: decision.mode,
    modeLabel: decision.modeLabel,
    modeExecutable: decision.modeExecutable,
    // 两条路各自要什么能力：深度要逐轨修音/复合（未实现），快速要整轨两档（已实现）。
    // 分开列出，UI 才能诚实地说明「快速可用、深度仍不可用」。
    tuneCapability: decision.mode === 'FAST_STEREO_ONLY'
      ? FAST_PAIR_CAPABILITY_ID
      : (decision.mode === 'DEEP' ? DEEP_CORE_CAPABILITY_IDS.join('+') : null),
    facts: f,
  };
}

function snapshot(caseDir) {
  const info = inspect(caseDir);
  const facts = factsOf(info);
  return { info, facts, stage: stageOf(facts), gates: gates(info) };
}

// ── pipeline.json (a record, not an authority) ──────────────────────────────────

function pipelinePath(caseDir) {
  return path.join(caseDir, 'studio', 'pipeline.json');
}

/**
 * Persist the derived stage. Never used as a source of truth on read — `snapshot()`
 * re-derives every time. This exists so the case carries a readable history of what the
 * user actually did, which raw directory listings cannot express.
 */
function recordStage(caseDir) {
  const { stage, facts } = snapshot(caseDir);
  const file = pipelinePath(caseDir);
  const prior = readJsonSafe(file) || {};
  const history = Array.isArray(prior.history) ? prior.history.slice(-49) : [];
  const last = history[history.length - 1];
  if (!last || last.stage !== stage) {
    history.push({ stage, at: new Date().toISOString() });
  }
  const report = readJsonSafe(path.join(caseDir, 'report.json')) || {};
  const caseJson = readJsonSafe(path.join(caseDir, 'case.json')) || {};
  const payload = {
    schema: 'moodify.studio.pipeline/0.2',
    case_id: (report.case && report.case.case_id) || caseJson.case_id || null,
    stage,
    facts,
    history,
    updated_at: new Date().toISOString(),
    note: '记录用，不是权威来源；阶段每次由磁盘产物重新推导。',
  };
  try {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, JSON.stringify(payload, null, 2), 'utf8');
  } catch { /* best effort — the record is never load-bearing */ }
  return payload;
}

// ── capabilities ────────────────────────────────────────────────────────────────

/**
 * What Studio can actually invoke today, each with the real Core command behind it.
 *
 * Listed rather than guessed: an entry here means the desktop genuinely calls it. A
 * capability we cannot invoke is not listed here — it goes in PLANNED_CAPABILITIES, because
 * a planner that believes it can do something it cannot produces plans that cannot run.
 */
const CAPABILITIES = Object.freeze([
  { id: 'analysis-report', kind: 'analysis', detail: '测量 + 报告三件套',
    core_command: 'moodify analyze <audio> | moodify report <case>', stage: 'ANALYZE' },
  { id: 'fast-separation', kind: 'separation',
    detail: 'DSP 中置估计 + HPSS（scipy 中值滤波；快速/预览，非母带级）',
    core_command: 'moodify-desktop/scripts/dsp_separate.py', stage: 'SEPARATE' },
  // 模型分离：Demucs htdemucs（MIT）。母带级四轨（drums/bass/other/vocals）。
  // 与快速分离是**两档**，不是替代关系：快速用于秒级观察，模型用于真正要复合的场合。
  { id: 'model-separation', kind: 'separation',
    detail: 'Demucs htdemucs 神经网络四轨分离（母带级；CPU RTF ≈ 2–4×）',
    core_command: 'moodify-desktop/scripts/model_separate.py', stage: 'SEPARATE' },
  // 可逆性验证（**壳侧**实现）。放在这里而不是 PLANNED 里，是因为它真的能跑；
  // 同时 PLANNED 里保留了**Core 侧**的同名能力，两者不冲突也更不能混为一谈：
  //   - 壳侧（本项）：分轨相加与原版比较，写 studio/roundtrip.json，给门禁一个真实依据
  //   - Core 侧（PLANNED）：Core 自己产出可逆性证据
  // 名称带 `shell-` 前缀就是为了让这两件事在代码里无法被认错。
  { id: 'shell-reversibility-check', kind: 'verification',
    detail: '可逆性验证：按划分把分轨相加与原版比较（null 深度），写 studio/roundtrip.json',
    core_command: 'moodify-desktop/scripts/roundtrip.py --stems <dir> --original <wav>',
    stage: 'SEPARATE' },
  { id: 'structure-analysis', kind: 'structure',
    detail: '速度 / 拍点 / 段落边界 / 能量曲线（numpy+scipy；段落是位置编号，不是主歌副歌判断）',
    core_command: 'moodify-desktop/scripts/structure.py', stage: 'STRUCTURE' },
  { id: 'audio-to-midi', kind: 'structure', detail: 'Basic Pitch 音频转 MIDI',
    core_command: 'basic-pitch --save-midi <dir> <audio>', stage: 'STRUCTURE' },
  { id: 'midi-to-score', kind: 'structure', detail: 'music21 转 MusicXML',
    core_command: 'moodify-desktop/scripts/midi_to_musicxml.py', stage: 'STRUCTURE' },
  // 快速完成（仅立体声）的两档整轨候选：Core 已实现（MIP-0002 附录 A）。
  // 一次调用产出**一对**（A 保守 / B 充分），每侧带 plan / mix / tuned / evidence。
  // 它不做逐轨处理，也不修正音准与节奏 —— 深度路径要的 `stem-tuning` 仍在下面标为未就绪。
  { id: 'fast-stereo-pair', kind: 'processing',
    detail: '整轨两档候选（A 保守 / B 充分，逐侧 evidence；无逐轨处理、无音准/节奏修正）',
    core_command: 'moodify tuning render-pair --mode fast-stereo-only --source <wav> --output-dir <pair_dir>',
    stage: 'TUNE' },
  { id: 'delivery-export', kind: 'export', detail: '交付编码',
    core_command: 'moodify finishing export --audio <wav> --output-dir <dir>', stage: 'EXPORT' },
]);

/**
 * Capabilities the V4 flow needs but **Core** does not have yet.
 *
 * Listed, marked unavailable, with a reason — never mapped onto something similar. The V3
 * `streaming_ready` target was handled the same way: the button must not promise what the
 * engine cannot do. The three presets that used to live here retired on 2026-10-04.
 *
 * `reversibility-check` stays here on purpose even though the shell can now perform a
 * reversibility check (`shell-reversibility-check`, above). The two are different claims:
 * the shell compares a stem sum against the original; Core owning the evidence is what
 * this entry is about. Collapsing them would let a shell-side null test be read as Core
 * verification — exactly the kind of upgrade-by-renaming this repository keeps removing.
 */
const PLANNED_CAPABILITIES = Object.freeze([
  { id: 'reversibility-check', stage: 'SEPARATE',
    reason: '由 Core 自己产出可逆性证据（studio/roundtrip.json）；壳侧实现见 '
      + 'shell-reversibility-check，两者不得互相顶替' },
  { id: 'stem-tuning', stage: 'TUNE',
    reason: '逐轨音准·节奏修正以 MIDI 为参考，Core 无此能力；见 MIP-0002' },
  { id: 'multi-stem-compose', stage: 'COMPOSE',
    reason: '逐轨混音处理 + 整曲合成的两档渲染，Core 无此能力；见 MIP-0002' },
]);

// 能力可得性（供 modeDecision / gates 使用）。这两行**必须**在 CAPABILITIES 与
// PLANNED_CAPABILITIES 之后：它们决定「深度现在能不能跑」，也就是快速入口的依据。
const AVAILABLE_CAPABILITY_IDS = new Set(CAPABILITIES.map((c) => c.id));
const DEEP_CORE_AVAILABLE = DEEP_CORE_CAPABILITY_IDS.every((id) => AVAILABLE_CAPABILITY_IDS.has(id));
const FAST_PAIR_AVAILABLE = AVAILABLE_CAPABILITY_IDS.has(FAST_PAIR_CAPABILITY_ID);

// ── context.json ────────────────────────────────────────────────────────────────

/**
 * Assemble the machine-readable context pack for the tuner.
 *
 * It REFERENCES artifacts and never copies them, and it only ever lists paths that exist —
 * a context pack citing a missing file would make the tuner reason about something that is
 * not there. Raw audio never goes into a prompt: only paths and structured summaries.
 */
function buildContext(caseDir) {
  const info = inspect(caseDir);
  const studioDir = path.join(caseDir, 'studio');
  const fromCase = (p) => path.relative(studioDir, p).split(path.sep).join('/');

  const ctx = {
    schema: 'moodify.studio.context/0.2',
    case_id: info.caseId,
    generated_at: new Date().toISOString(),
    source: null,
    analysis: {},
    stems: null,
    // 结构事实（速度/拍点/段落边界）由 scripts/structure.py 产出；缺失时为 null。
    // 段落只有位置编号，没有主歌/副歌标签——语义不是测量结果。
    structure: null,
    midi: [],
    score: [],
    // 该保护什么 —— ④ 修音 的输入侧，由人填写（2026-10-04 裁定：从 ②问题 迁来）
    preserve: [],
    available_capabilities: CAPABILITIES.map((c) => ({ ...c })),
    planned_capabilities: PLANNED_CAPABILITIES.map((c) => ({ ...c })),
    notes: [],
  };

  if (info.hasReport) ctx.analysis.report = fromCase(info.reportPath);
  const measurements = path.join(caseDir, 'measurements.json');
  if (fs.existsSync(measurements)) ctx.analysis.measurements = fromCase(measurements);
  const evidence = path.join(caseDir, 'evidence.json');
  if (fs.existsSync(evidence)) ctx.analysis.evidence = fromCase(evidence);

  // preserve 现在挂在 ④ 修音：从修音对里读已记录的保护项（人写的），没有就空数组。
  if (info.currentPair && info.currentPair.pair && Array.isArray(info.currentPair.pair.preserve)) {
    ctx.preserve = info.currentPair.pair.preserve;
  }

  if (info.hasStems || info.stemsManifest) {
    const m = info.stemsManifest || {};
    // grade 必须**来自 manifest**，不能在这里写死。写死的话，接入模型分离之后
    // （engine_grade = MODEL_SEPARATION_NOT_VERIFIED_AGAINST_ORIGINAL_STEMS）
    // 每个下游仍会读到「预览级」，等于把升级过的产物降级描述——比没写更糟。
    const grade = m.engine_grade
      || (m.engine === 'demucs' ? 'MODEL_SEPARATION_NOT_VERIFIED_AGAINST_ORIGINAL_STEMS'
        : 'PREVIEW_NOT_MASTERING_GRADE');
    ctx.stems = {
      manifest: info.stemsManifest ? fromCase(info.stemsManifestPath) : null,
      files: info.stemWavs.map((p) => fromCase(p)),
      engine: m.engine || null,
      engine_model: m.engine_model || null,
      engine_note: m.engine_note || null,
      grade,
      // 划分：一套分轨里哪些轨**相加等于原版**。缺了它，可逆性验证只能靠搜索猜。
      partition: m.partition || null,
    };
    if (grade === 'PREVIEW_NOT_MASTERING_GRADE') {
      ctx.notes.push('分轨为快速/预览级（DSP 中置估计 + HPSS），不可作为母带级分轨使用。');
    } else {
      ctx.notes.push('分轨来自模型引擎（Demucs）；原分轨不可知，'
        + '因此『分离得对不对』无法回答，只能以可逆性作为代理。');
    }
  }

  const structurePath = path.join(studioDir, 'structure.json');
  const structure = readJsonSafe(structurePath);
  if (structure) {
    ctx.structure = {
      path: 'structure.json',
      bpm: structure.tempo ? structure.tempo.bpm : null,
      tempo_confidence: structure.tempo ? structure.tempo.confidence : null,
      beats: structure.beat_count ?? null,
      sections: Array.isArray(structure.sections) ? structure.sections.length : 0,
      section_labels: null, // 段落语义不是测量结果——**没有**标签，只有位置编号
      judgment_boundary: structure.judgment_boundary || null,
    };
  }

  ctx.midi = info.midiFiles.map((p) => fromCase(p));
  ctx.score = info.scoreFiles.map((p) => fromCase(p));

  if (!info.hasMidi) {
    ctx.notes.push(info.hasStructure
      ? '仅有曲谱（MusicXML），缺少 MIDI；④ 修音需要 MIDI 作为音准·节奏的参考。'
      : '尚无 MIDI/曲谱产物；结构信息缺失。④ 修音需要 MIDI 作为参考。');
  }

  const snap = snapshot(caseDir);
  ctx.readiness = {
    stage: snap.stage,
    finish_mode: snap.gates.mode,
    finish_mode_label: snap.gates.modeLabel,
    reversibility: info.roundtrip
      ? {
        passed: info.roundtrip.passed === true,
        path: 'roundtrip.json',
        // 把「这个数说明什么 / 不说明什么」一起带上：只有 passed 一个布尔值，
        // 下游一定会把它读成「分轨已验证」。null 深度与控制组读数必须同行。
        null_depth_db: info.roundtrip.measurement
          ? info.roundtrip.measurement.null_depth_db : null,
        partition: info.roundtrip.stems ? Object.keys(info.roundtrip.stems) : null,
        interpretation: info.roundtrip.interpretation || null,
      }
      : { passed: false, path: null, null_depth_db: null, partition: null, interpretation: null },
    facts: snap.gates.facts,
  };

  return ctx;
}

function writeContext(caseDir, ctx) {
  const file = path.join(caseDir, 'studio', 'context.json');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(ctx, null, 2), 'utf8');
  return file;
}

module.exports = {
  STAGES,
  STAGE_INDEX,
  CAPABILITIES,
  PLANNED_CAPABILITIES,
  DEEP_CORE_CAPABILITY_IDS,
  DEEP_BLOCKER_LABELS,
  inspect,
  factsOf,
  stageOf,
  modeDecision,
  gates,
  snapshot,
  pipelinePath,
  recordStage,
  finishModePath,
  readFinishMode,
  recordFinishMode,
  buildContext,
  writeContext,
  readJsonSafe,
  listFiles,
};
