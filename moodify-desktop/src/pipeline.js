/**
 * Studio production pipeline — stages, gating, diagnosis and context.
 *
 * PRODUCT PRINCIPLE (TASK 002A):
 *     Understand first. Decompose second. Process last.
 *
 * Why this file exists
 *   The first Studio flow let the user pick a preset and process immediately after
 *   analysis, which processes a stereo master far too early. The canonical creator flow is
 *   now sequential:
 *
 *     检测 → 问题 → 分轨 → 结构 → 方案 → 成品
 *     ANALYZE → DIAGNOSE → SEPARATE → STRUCTURE → PLAN → FINISH
 *
 *   The three presets still exist and still work — they moved to the LAST stage. They are
 *   tools, not the workflow.
 *
 * STAGE IS DERIVED, NOT HAND-ADVANCED
 *   Nothing here records "the user clicked next". Every stage is derived from the artifacts
 *   actually present on disk. If stems are deleted, the case falls back out of SEPARATED by
 *   itself. A stored stage that says SEPARATED while the files are gone is exactly the kind
 *   of lie this repository keeps having to remove.
 *
 *   `pipeline.json` therefore records the derived result and its history. It is a record,
 *   not an authority. Section 12 also says not to build a distributed workflow engine —
 *   this is a few filesystem checks in one module.
 *
 * NO INVENTED MEASUREMENT FACTS
 *   `diagnosis.json` is assembled strictly from Core's own `report.json`. Every issue
 *   carries an `evidence` pointer back to the finding it came from, and `resolvePointer()`
 *   exists so a test can prove those pointers actually resolve. Nothing here interprets,
 *   scores or paraphrases a measurement.
 *
 *   Being honest about thinness matters: Core currently emits only two finding kinds, and
 *   most real cases produce none. A diagnosis with no issues says "当前规则未发现技术问题",
 *   never "this song is fine".
 */

'use strict';

const fs = require('fs');
const path = require('path');

// ── stages ──────────────────────────────────────────────────────────────────────

/**
 * Ordered stages. READY_FOR_PLAN is a derivable state (analysis + diagnosis done), not a
 * separate artifact; it exists so the UI can say "ready to plan" without inventing a file.
 */
const STAGES = Object.freeze([
  'IMPORTED',
  'ANALYZED',
  'DIAGNOSED',
  'SEPARATED',
  'STRUCTURED',
  'READY_FOR_PLAN',
  'PLANNED',
  'RENDERED',
  'VERIFIED',
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

function listDirs(dir) {
  let entries = [];
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return []; }
  return entries.filter((e) => e.isDirectory()).map((e) => e.name).sort();
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
  const diagnosisPath = path.join(studioDir, 'diagnosis.json');
  const plansDir = path.join(studioDir, 'plans');
  const versionsDir = path.join(studioDir, 'versions');
  const verificationDir = path.join(studioDir, 'verification');
  const exportDir = path.join(studioDir, 'export');
  const selectionPath = path.join(studioDir, 'selection.json');

  const attemptDirs = listDirs(versionsDir).filter((n) => n.startsWith('ai_'));

  return {
    caseDir,
    reportPath,
    report,
    hasReport: Boolean(report),
    caseId: (report && report.case && report.case.case_id) || null,

    diagnosisPath,
    hasDiagnosis: fs.existsSync(diagnosisPath),

    stemsDir,
    stemWavs,
    stemsManifestPath,
    stemsManifest,
    hasStems: stemWavs.length > 0,

    midiFiles,
    scoreFiles,
    hasStructure: midiFiles.length > 0 || scoreFiles.length > 0,

    plansDir,
    plans: listFiles(plansDir, ['.json']),
    hasPlan: listFiles(plansDir, ['.json']).length > 0,

    versionsDir,
    attemptDirs,
    hasRender: attemptDirs.length > 0,

    verificationDir,
    verifications: listFiles(verificationDir, ['.json']),
    hasVerification: listFiles(verificationDir, ['.json']).length > 0,

    selectionPath,
    hasSelection: fs.existsSync(selectionPath),
    exportDir,
    exports: listFiles(exportDir, ['.json']),
    hasExport: listFiles(exportDir, ['.json']).length > 0,
  };
}

/** Boolean checklist behind the stages — the thing the UI gates on. */
function factsOf(info) {
  const analyzed = info.hasReport;
  const diagnosed = info.hasDiagnosis;
  return {
    imported: Boolean(info.caseDir) && fs.existsSync(info.caseDir),
    analyzed,
    diagnosed,
    separated: info.hasStems,
    structured: info.hasStructure,
    // ready to plan = the hard gate for reaching the AI planning/finishing stages
    readyForPlan: analyzed && diagnosed,
    planned: info.hasPlan,
    rendered: info.hasRender,
    verified: info.hasVerification,
    chosen: info.hasSelection,
    exported: info.hasExport,
  };
}

/**
 * Stage order with the fact each one requires.
 *
 * `optional: true` means a legitimate path may skip it — a FAST stereo-only finish never
 * separates or structures, and a plan may be rendered without a separate verification
 * record. Skipping an optional does NOT stop the walk; missing a required one does.
 *
 * READY_FOR_PLAN is deliberately NOT in this table, even though it is a valid state name.
 * It is derived from `analyzed && diagnosed`, i.e. it is a *readiness* fact rather than
 * something the user did. Including it made every case that had analysed and diagnosed
 * report itself as READY_FOR_PLAN, jumping past 分轨 and 结构 — so the indicator claimed
 * progress the user had not made. Readiness is reported through `gates().canPlan` instead.
 */
const STAGE_TABLE = Object.freeze([
  { stage: 'IMPORTED', fact: 'imported' },
  { stage: 'ANALYZED', fact: 'analyzed' },
  { stage: 'DIAGNOSED', fact: 'diagnosed' },
  { stage: 'SEPARATED', fact: 'separated', optional: true },
  { stage: 'STRUCTURED', fact: 'structured', optional: true },
  { stage: 'PLANNED', fact: 'planned' },
  { stage: 'RENDERED', fact: 'rendered' },
  { stage: 'VERIFIED', fact: 'verified', optional: true },
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

/**
 * What the UI may enter.
 *
 * THE FINISH STAGE IS NOT AUTOMATICALLY AVAILABLE.
 *
 * Deep Finish is the canonical path and REQUIRES the full preparation:
 *
 *     ANALYZED + DIAGNOSED + SEPARATED + STRUCTURED
 *
 * A stereo-only finish is a legitimate fallback for a song that should not be forced
 * through an expensive decomposition — but it is a *concession*, not a default. It must be
 * a Quick Finish the user **explicitly opts into**, recorded as a human decision:
 *
 *     canRequestQuick  the affordance is offered (deep prereqs missing, no opt-in yet)
 *     canFinishQuick   the user opted in, so the finish stage opens in FAST mode
 *
 * What this replaced, and why it mattered: the first version unlocked the finish stage as
 * soon as analysis + diagnosis were done, and merely *labelled* the result FAST. That made
 * stereo-only the path of least resistance — the user would reach 成品 by default, never
 * separating or extracting structure, and the canonical deep path would quietly become the
 * exception. A labelled shortcut is still a shortcut. Now the shortcut requires a decision.
 *
 * Deep always wins: if the user opts into Quick and later separates and structures the song,
 * `deepReady` takes precedence and the mode returns to DEEP without needing to undo anything.
 */
function gates(info) {
  const f = factsOf(info);
  const deepReady = f.readyForPlan && f.separated && f.structured;
  const optIn = readFinishMode(info.caseDir).mode === 'QUICK_STEREO_ONLY';
  const quickFinish = f.readyForPlan && !deepReady && optIn;
  return {
    canDiagnose: f.analyzed,
    canSeparate: f.analyzed,
    canStructure: f.analyzed,
    canPlan: f.readyForPlan,
    // canonical finish: separation + structure are required, not optional
    canFinish: deepReady,
    canFinishQuick: quickFinish,
    canRequestQuick: f.readyForPlan && !deepReady && !optIn,
    quickOptIn: optIn,
    mode: deepReady ? 'DEEP' : (quickFinish ? 'FAST_STEREO_ONLY' : null),
    modeLabel: deepReady ? '深度完成' : (quickFinish ? '快速（仅立体声）' : null),
    facts: f,
  };
}

// ── explicit Quick Finish opt-in ────────────────────────────────────────────────

function finishModePath(caseDir) {
  return path.join(caseDir, 'studio', 'finish_mode.json');
}

/**
 * The recorded human choice to skip separation and structure for this case.
 *
 * This is deliberately a persisted artifact rather than a checkbox in the UI: "the user
 * chose the shortcut" is a decision worth being able to point at later, the same way
 * selection.json records which version was kept.
 */
function readFinishMode(caseDir) {
  return readJsonSafe(finishModePath(caseDir)) || {};
}

/**
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
    reason: '用户显式选择跳过分轨与结构；深度完成需 SEPARATED + STRUCTURED。',
  };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(payload, null, 2), 'utf8');
  return payload;
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
  // report.json nests the id under `case`; case.json keeps it flat.
  const report = readJsonSafe(path.join(caseDir, 'report.json')) || {};
  const caseJson = readJsonSafe(path.join(caseDir, 'case.json')) || {};
  const payload = {
    schema: 'moodify.studio.pipeline/0.1',
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

// ── diagnosis.json ──────────────────────────────────────────────────────────────

/**
 * Build the Studio diagnosis from Core's report.
 *
 * Strictly a projection: every issue is one `findings[]` entry, and its `evidence` points
 * back at the exact JSON location it came from. No threshold is re-evaluated, no metric is
 * re-derived, and nothing is invented. Core is the authority on what was found; this file
 * only says where to look and what the user should decide.
 *
 * Core currently emits only CLIPPING_PRESENT and TRUE_PEAK_MARGIN_EXCEEDED, and most real
 * songs produce no findings at all — so `issues` is frequently empty, and the UI must say
 * "当前规则未发现技术问题" rather than implying the audio is fine.
 */
function buildDiagnosis(caseDir) {
  const info = inspect(caseDir);
  if (!info.hasReport) return null;
  const report = info.report;
  const previous = readDiagnosis(caseDir);

  // Refreshing Core's projection must never erase human judgement.  Only carry these
  // fields from a diagnosis written for the same case/schema; every measured field below
  // is rebuilt from report.json so stale machine facts cannot leak through.
  const sameDiagnosis = previous
    && previous.schema === 'moodify.studio.diagnosis/0.1'
    && previous.case_id === info.caseId;
  const preserve = sameDiagnosis && Array.isArray(previous.preserve)
    ? previous.preserve
    : [];
  const humanNotes = sameDiagnosis && Array.isArray(previous.human_notes)
    ? previous.human_notes
    : [];

  const findings = Array.isArray(report.findings) ? report.findings : [];
  const issues = findings.map((f, i) => ({
    id: `issue-${String(i + 1).padStart(3, '0')}`,
    type: f.code || null,
    description: f.message || '',
    severity: f.severity || null,
    // a JSON pointer into report.json — resolvable by resolvePointer(), and asserted by test
    evidence: [`report.json#/findings/${i}`],
    confidence: 'measured',
    metric: f.metric ?? null,
    observed_value: f.observed_value ?? null,
    unit: f.unit ?? null,
    // carried through verbatim so a consumer cannot mistake an uncalibrated engineering
    // default for a perceptually validated limit
    calibration_status: f.calibration_status ?? null,
    threshold_source_class: f.threshold_source_class ?? null,
    evidence_refs: Array.isArray(f.evidence_refs) ? f.evidence_refs : [],
    check: f.check ?? null,
  }));

  const plan = report.plan || {};
  return {
    schema: 'moodify.studio.diagnosis/0.1',
    case_id: info.caseId,
    generated_at: new Date().toISOString(),
    source_report: 'report.json',
    // verbatim from Core — not our summary
    technical_state: report.technical_state || null,
    judgment_boundary: report.judgment_boundary || null,
    issues,
    // Core's own draft nodes (plan.status is always DRAFT_PLAN_NOT_EXECUTED)
    draft_plan: {
      status: plan.status || null,
      nodes: Array.isArray(plan.nodes) ? plan.nodes : [],
      notes: Array.isArray(plan.notes) ? plan.notes : [],
      next_actions: Array.isArray(plan.next_actions) ? plan.next_actions : [],
    },
    // Empty on first generation. On refresh these human-authored fields survive while all
    // machine-authored fields above are projected again from the latest Core report.
    preserve,
    human_notes: humanNotes,
    finding_rule_coverage: {
      // stated plainly so nobody reads an empty issue list as "the audio is fine"
      note: 'Core 当前只能产出 CLIPPING_PRESENT / TRUE_PEAK_MARGIN_EXCEEDED 两类 finding；'
        + '无 finding 只表示当前规则未发现问题，不代表音频已被判定为无问题。',
      producible_codes: ['CLIPPING_PRESENT', 'TRUE_PEAK_MARGIN_EXCEEDED'],
    },
  };
}

function writeDiagnosis(caseDir, diagnosis) {
  const file = path.join(caseDir, 'studio', 'diagnosis.json');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(diagnosis, null, 2), 'utf8');
  return file;
}

function readDiagnosis(caseDir) {
  return readJsonSafe(path.join(caseDir, 'studio', 'diagnosis.json'));
}

/** Add a human note (and optional preserve entries). The only writer of these fields. */
function addHumanNote(caseDir, { note, preserve }) {
  const current = readDiagnosis(caseDir);
  if (!current) return null;
  const next = { ...current };
  if (note) next.human_notes = [...(next.human_notes || []), { text: note, at: new Date().toISOString() }];
  if (preserve) next.preserve = [...(next.preserve || []), preserve];
  fs.writeFileSync(path.join(caseDir, 'studio', 'diagnosis.json'), JSON.stringify(next, null, 2), 'utf8');
  return next;
}

/**
 * Resolve a `report.json#/a/b/0` pointer against a case directory.
 *
 * Exists so the "diagnosis must reference real evidence" rule is testable rather than
 * asserted. Returns undefined when the pointer does not resolve — callers treat that as a
 * defect, not as empty data.
 */
function resolvePointer(caseDir, pointer) {
  const [file, frag] = String(pointer).split('#');
  const doc = readJsonSafe(path.join(caseDir, file));
  if (doc === null || !frag) return undefined;
  const parts = frag.split('/').filter(Boolean).map((p) => p.replace(/~1/g, '/').replace(/~0/g, '~'));
  let cur = doc;
  for (const p of parts) {
    if (cur === null || typeof cur !== 'object') return undefined;
    cur = Array.isArray(cur) ? cur[Number(p)] : cur[p];
  }
  return cur;
}

// ── context.json ────────────────────────────────────────────────────────────────

/**
 * What Studio can actually invoke, each with the real Core command behind it.
 *
 * Listed rather than guessed: an entry here means the desktop genuinely calls it today.
 * A capability we cannot invoke is not listed, because a planner that believes it can do
 * something it cannot produces plans that cannot run.
 */
const CAPABILITIES = Object.freeze([
  { id: 'existing-presets', kind: 'processing', detail: 'clean_master / warm_vocal / wide_space',
    core_command: 'moodify protocol process <job.json>', stage: 'FINISH' },
  { id: 'delivery-export', kind: 'export', detail: '峰值处理后的交付编码',
    core_command: 'moodify finishing export --audio <wav> --output-dir <dir>', stage: 'FINISH' },
  { id: 'analysis-report', kind: 'analysis', detail: '测量 + 报告三件套',
    core_command: 'moodify analyze <audio> | moodify report <case>', stage: 'ANALYZE' },
  { id: 'fast-separation', kind: 'separation', detail: 'DSP 中置估计 + HPSS（快速/预览，非母带级）',
    core_command: 'moodify-desktop/scripts/dsp_separate.py', stage: 'SEPARATE' },
  { id: 'audio-to-midi', kind: 'structure', detail: 'Basic Pitch 音频转 MIDI',
    core_command: 'basic-pitch --save-midi <dir> <audio>', stage: 'STRUCTURE' },
  { id: 'midi-to-score', kind: 'structure', detail: 'music21 转 MusicXML',
    core_command: 'moodify-desktop/scripts/midi_to_musicxml.py', stage: 'STRUCTURE' },
]);

/** True only when the path exists — context must never cite a file that is not there. */
function existingRelative(caseDir, target, relFromStudio) {
  if (!target) return null;
  const abs = path.isAbsolute(target) ? target : path.join(caseDir, target);
  if (!fs.existsSync(abs)) return null;
  return relFromStudio ?? path.relative(path.join(caseDir, 'studio'), abs).split(path.sep).join('/');
}

/**
 * Assemble the machine-readable context pack for the future AI planner (section 9).
 *
 * It REFERENCES artifacts and never copies them, and it only ever lists paths that exist —
 * a context pack citing a missing file would make the planner reason about something that
 * is not there. Section 15 also requires that raw audio never goes into a prompt: only
 * paths and structured summaries appear here.
 */
function buildContext(caseDir) {
  const info = inspect(caseDir);
  // Paths are relative to <case>/studio because that is where context.json lives — so
  // '../report.json' already means '<case>/report.json'. Adding another '../' would point
  // one level above the case, at a file that does not exist. Asserted by test-pipeline.js.
  const fromCase = (p) => path.relative(path.join(caseDir, 'studio'), p).split(path.sep).join('/');

  const ctx = {
    schema: 'moodify.studio.context/0.1',
    case_id: info.caseId,
    generated_at: new Date().toISOString(),
    source: null,
    analysis: {},
    diagnosis: null,
    stems: null,
    midi: [],
    score: [],
    available_capabilities: CAPABILITIES.map((c) => ({ ...c })),
    notes: [],
  };

  try {
    const sp = readJsonSafe(path.join(caseDir, 'source_path.json'));
    if (sp && sp.path && fs.existsSync(sp.path)) ctx.source = sp.path;
  } catch { /* none */ }

  if (info.hasReport) ctx.analysis.report = fromCase(info.reportPath);
  const measurements = path.join(caseDir, 'measurements.json');
  if (fs.existsSync(measurements)) ctx.analysis.measurements = fromCase(measurements);
  const evidence = path.join(caseDir, 'evidence.json');
  if (fs.existsSync(evidence)) ctx.analysis.evidence = fromCase(evidence);

  if (info.hasDiagnosis) ctx.diagnosis = 'diagnosis.json';

  if (info.hasStems || info.stemsManifest) {
    const m = info.stemsManifest || {};
    ctx.stems = {
      // only cite the manifest when it is actually present
      manifest: info.stemsManifest ? fromCase(info.stemsManifestPath) : null,
      files: info.stemWavs.map((p) => fromCase(p)),
      engine: m.engine || null,
      // carried verbatim: the separator's own statement of its limits travels with the data
      engine_note: m.engine_note || null,
      // explicit grade so no downstream consumer can mistake preview stems for master-grade
      grade: 'PREVIEW_NOT_MASTERING_GRADE',
    };
    ctx.notes.push('分轨为快速/预览级（DSP 中置估计 + HPSS），不可作为母带级分轨使用。');
  }

  ctx.midi = info.midiFiles.map((p) => fromCase(p));
  ctx.score = info.scoreFiles.map((p) => fromCase(p));

  if (!info.hasStructure) {
    ctx.notes.push('尚无 MIDI/曲谱产物；结构信息缺失。');
  }

  const { gates } = snapshot(caseDir);
  ctx.readiness = {
    stage: snapshot(caseDir).stage,
    finish_mode: gates.mode,
    finish_mode_label: gates.modeLabel,
    facts: gates.facts,
  };

  return ctx;
}

function writeContext(caseDir, ctx) {
  const file = path.join(caseDir, 'studio', 'context.json');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(ctx, null, 2), 'utf8');
  return file;
}

/**
 * Persist the concrete draft which makes the PLAN stage real.
 *
 * The context pack is the planner's input; this artifact records the Core draft that the
 * current Studio can actually execute.  It remains explicitly DRAFT_PLAN_NOT_EXECUTED and
 * references its evidence rather than copying analysis data.
 */
function writeContextPlan(caseDir, ctx) {
  const diagnosis = readDiagnosis(caseDir);
  if (!diagnosis) return null;
  const file = path.join(caseDir, 'studio', 'plans', 'context_plan.json');
  const payload = {
    schema: 'moodify.studio.plan/0.1',
    case_id: ctx.case_id,
    generated_at: new Date().toISOString(),
    status: (diagnosis.draft_plan && diagnosis.draft_plan.status)
      || 'DRAFT_PLAN_NOT_EXECUTED',
    context: '../context.json',
    diagnosis: '../diagnosis.json',
    finish_mode: ctx.readiness ? ctx.readiness.finish_mode : null,
    finish_mode_label: ctx.readiness ? ctx.readiness.finish_mode_label : null,
    draft_plan: diagnosis.draft_plan || {
      status: 'DRAFT_PLAN_NOT_EXECUTED', nodes: [], notes: [], next_actions: [],
    },
    note: '方案未执行；处理、校验与 A/B 选择仍需后续显式动作。',
  };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(payload, null, 2), 'utf8');
  return { file, plan: payload };
}

/** The real PLAN action used by the UI: context and plan are committed together. */
function preparePlan(caseDir) {
  const snap = snapshot(caseDir);
  if (!snap.gates.canPlan) return null;
  const context = buildContext(caseDir);
  const contextFile = writeContext(caseDir, context);
  const written = writeContextPlan(caseDir, context);
  if (!written) return null;
  return { context, contextFile, plan: written.plan, planFile: written.file };
}

module.exports = {
  STAGES,
  STAGE_INDEX,
  CAPABILITIES,
  inspect,
  factsOf,
  stageOf,
  gates,
  snapshot,
  pipelinePath,
  recordStage,
  finishModePath,
  readFinishMode,
  recordFinishMode,
  buildDiagnosis,
  writeDiagnosis,
  readDiagnosis,
  addHumanNote,
  resolvePointer,
  buildContext,
  writeContext,
  writeContextPlan,
  preparePlan,
  readJsonSafe,
  listFiles,
};
