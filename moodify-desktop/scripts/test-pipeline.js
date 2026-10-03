#!/usr/bin/env node
/**
 * Headless test for the Studio production pipeline (TASK 002A).
 *
 * Covers the seven things section 20 requires:
 *   1 analysis artifacts can be located        5 context.json contains only existing paths
 *   2 diagnosis references real evidence       6 pipeline cannot jump to deep finishing early
 *   3 stems manifest can be discovered         7 preset processing still works (see test-studio.js)
 *   4 MIDI / score artifacts can be discovered
 *
 * Fixtures are SYNTHESISED, not taken from a real case, so the assertions are deterministic
 * and do not depend on whatever happens to be in ~/.moodify/cases. The one test that needs
 * the real Core (7) lives in test-studio.js.
 *
 * Run: node scripts/test-pipeline.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');

const pipeline = require(path.join(__dirname, '..', 'src', 'pipeline'));

let passed = 0;
const failures = [];
// Must stay async and every call site must await it. A synchronous helper wrapping async
// callbacks reported false passes once already in test-studio.js; not repeating that here.
async function check(label, fn) {
  try { await fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

// ── fixture ─────────────────────────────────────────────────────────────────────

const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-pipeline-test-'));
let caseSeq = 0;

/** A real-shaped Core report. Only two finding codes exist in Core; use one of them. */
function makeReport({ withFinding = false } = {}) {
  const findings = withFinding
    ? [{
      code: 'TRUE_PEAK_MARGIN_EXCEEDED',
      severity: 'WARNING',
      message: 'true peak margin below 0.5 dB',
      metric: 'true_peak_dbfs',
      observed_value: 0.28,
      unit: 'dBFS',
      classification: 'TECHNICAL_RISK',
      confidence: 0.9,
      reference_basis: 'true_peak_margin_reduced',
      calibration_status: 'DEFAULT_UNCALIBRATED',
      threshold_source_class: 'DEFAULT',
      evidence_refs: ['metrics.json'],
      check: 'absolute_rule',
    }]
    : [];
  return {
    protocol: 'moodify.sound/0.2',
    report_schema_version: 'moodify.msp_report/0.2',
    generated_at: '2026-10-03T00:00:00+00:00',
    job: { type: 'analyze', source: 'song.wav' },
    case: { case_id: 'case_test' },
    source: { name: 'song.wav', sha256: 'sha256:' + 'a'.repeat(64), duration_s: 30, channels: 2, sample_rate: 48000 },
    representation: {},
    measurements: [],
    findings,
    plan: {
      status: 'DRAFT_PLAN_NOT_EXECUTED',
      nodes: withFinding
        ? [{ op: 'limiter', params: { ceiling_dbfs: -1.0 }, reason: 'restore headroom',
          evidence_refs: ['TRUE_PEAK_MARGIN_EXCEEDED'], reversible: true }]
        : [],
      next_actions: [], notes: [],
    },
    judgment_boundary: { layer1_measurement: 'EXECUTED', layer2_comparison: 'NOT_RUN' },
    technical_state: {
      overall: 'PARTIAL',
      workflow_decision: withFinding ? 'REVIEW_RECOMMENDED' : 'NO_TECHNICAL_BLOCKERS',
      reasons: withFinding ? ['warning: TRUE_PEAK_MARGIN_EXCEEDED'] : [],
    },
    provenance: { core_version: '1.0.0-rc.1' },
  };
}

/**
 * Build a case directory with exactly the artifacts requested.
 *   report / diagnosis / stems / midi / score / plan / render / selection / export
 */
function makeCase(opts = {}) {
  const dir = path.join(tmpRoot, `case_${String(++caseSeq).padStart(4, '0')}`);
  fs.mkdirSync(path.join(dir, 'studio'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'case.json'), JSON.stringify({ case_id: 'case_test' }));

  if (opts.report !== false) {
    fs.writeFileSync(path.join(dir, 'report.json'),
      JSON.stringify(makeReport({ withFinding: opts.withFinding })));
    fs.writeFileSync(path.join(dir, 'measurements.json'), JSON.stringify([]));
    fs.writeFileSync(path.join(dir, 'evidence.json'), JSON.stringify([]));
  }
  if (opts.diagnosis) {
    const d = pipeline.buildDiagnosis(dir);
    pipeline.writeDiagnosis(dir, d);
  }
  if (opts.stems) {
    fs.mkdirSync(path.join(dir, 'stems'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'stems', 'song__vocals.wav'), 'RIFF');
    fs.writeFileSync(path.join(dir, 'stems', 'manifest.json'), JSON.stringify({
      engine: 'dsp_center_hpss',
      engine_note: '非模型快速分离：中置声道估计 + HPSS 谱分解；有人声残留与伪影，不构成母带级分轨。',
      stems: { vocals: '/abs/vocals.wav' },
    }));
  }
  if (opts.midi) {
    fs.mkdirSync(path.join(dir, 'midi'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'midi', 'song_basic_pitch.mid'), 'MThd');
  }
  if (opts.score) {
    fs.mkdirSync(path.join(dir, 'score'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'score', 'song_basic_pitch.musicxml'), '<score/>');
  }
  if (opts.plan) {
    fs.mkdirSync(path.join(dir, 'studio', 'plans'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'studio', 'plans', 'plan_001.json'), '{}');
  }
  if (opts.render) {
    fs.mkdirSync(path.join(dir, 'studio', 'versions', 'ai_x'), { recursive: true });
  }
  if (opts.selection) {
    fs.writeFileSync(path.join(dir, 'studio', 'selection.json'), JSON.stringify({ version_id: 'ai_x' }));
  }
  if (opts.export) {
    fs.mkdirSync(path.join(dir, 'studio', 'export'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'studio', 'export', 'export_record.json'), '{}');
  }
  return dir;
}

(async () => {
  console.log('Studio pipeline test (TASK 002A)\n');

  // ── 1. artifacts can be located ───────────────────────────────────────────────
  console.log('1. analysis artifacts can be located');
  await check('an analyzed case reports ANALYZED', () => {
    const dir = makeCase({});
    assert.strictEqual(pipeline.snapshot(dir).stage, 'ANALYZED');
  });
  await check('a bare directory reports IMPORTED, not ANALYZED', () => {
    const dir = path.join(tmpRoot, 'bare');
    fs.mkdirSync(dir, { recursive: true });
    assert.strictEqual(pipeline.snapshot(dir).stage, 'IMPORTED');
  });
  await check('stage is derived, so deleting artifacts moves it backwards', () => {
    const dir = makeCase({ diagnosis: true, stems: true });
    assert.strictEqual(pipeline.snapshot(dir).stage, 'SEPARATED');
    fs.rmSync(path.join(dir, 'stems'), { recursive: true, force: true });
    // no stored state to go stale: the fallback is automatic
    assert.notStrictEqual(pipeline.snapshot(dir).stage, 'SEPARATED');
  });

  // ── 2. diagnosis references real evidence ─────────────────────────────────────
  console.log('\n2. diagnosis references real evidence');
  await check('every issue evidence pointer resolves against report.json', () => {
    const dir = makeCase({ withFinding: true });
    const d = pipeline.buildDiagnosis(dir);
    assert.strictEqual(d.issues.length, 1);
    for (const issue of d.issues) {
      for (const ptr of issue.evidence) {
        const resolved = pipeline.resolvePointer(dir, ptr);
        assert.ok(resolved !== undefined, `pointer did not resolve: ${ptr}`);
        assert.strictEqual(resolved.code, issue.type, 'pointer must land on the finding it came from');
      }
    }
  });
  await check('a case with no findings produces no issues (not invented ones)', () => {
    const dir = makeCase({ withFinding: false });
    const d = pipeline.buildDiagnosis(dir);
    assert.deepStrictEqual(d.issues, []);
    assert.ok(d.finding_rule_coverage.note, 'must carry the "no finding != audio is fine" note');
  });
  await check('resolvePointer returns undefined for a pointer that does not exist', () => {
    const dir = makeCase({});
    assert.strictEqual(pipeline.resolvePointer(dir, 'report.json#/findings/99'), undefined);
  });
  await check('diagnosis copies Core values verbatim, never re-derives them', () => {
    const dir = makeCase({ withFinding: true });
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'report.json'), 'utf8'));
    const d = pipeline.buildDiagnosis(dir);
    assert.strictEqual(d.issues[0].observed_value, report.findings[0].observed_value);
    assert.strictEqual(d.issues[0].calibration_status, report.findings[0].calibration_status);
    assert.deepStrictEqual(d.technical_state, report.technical_state);
  });
  await check('preserve starts empty — it is a human judgement, not a default', () => {
    const dir = makeCase({ diagnosis: true });
    assert.deepStrictEqual(pipeline.readDiagnosis(dir).preserve, []);
  });

  // ── 3 / 4. stems and structure discovery ──────────────────────────────────────
  console.log('\n3-4. stems and structure artifacts can be discovered');
  await check('stems manifest and its honest engine note are found', () => {
    const dir = makeCase({ diagnosis: true, stems: true });
    const ctx = pipeline.buildContext(dir);
    assert.ok(ctx.stems, 'stems block must be present');
    assert.strictEqual(ctx.stems.engine, 'dsp_center_hpss');
    assert.match(ctx.stems.engine_note, /不构成母带级分轨/);
    assert.strictEqual(ctx.stems.grade, 'PREVIEW_NOT_MASTERING_GRADE');
  });
  await check('MIDI and score files are discovered', () => {
    const dir = makeCase({ diagnosis: true, midi: true, score: true });
    const ctx = pipeline.buildContext(dir);
    assert.strictEqual(ctx.midi.length, 1);
    assert.strictEqual(ctx.score.length, 1);
  });
  await check('missing structure is stated, not silently omitted', () => {
    const dir = makeCase({ diagnosis: true });
    const ctx = pipeline.buildContext(dir);
    assert.ok(ctx.notes.some((n) => /结构信息缺失/.test(n)));
  });

  // ── 5. context.json only cites paths that exist ───────────────────────────────
  console.log('\n5. context.json contains only existing paths');
  await check('every referenced path resolves on disk', () => {
    const dir = makeCase({ diagnosis: true, stems: true, midi: true, score: true });
    const ctx = pipeline.buildContext(dir);
    const studioDir = path.join(dir, 'studio');
    const rels = [];
    if (ctx.analysis.report) rels.push(ctx.analysis.report);
    if (ctx.analysis.measurements) rels.push(ctx.analysis.measurements);
    if (ctx.diagnosis) rels.push(ctx.diagnosis);
    if (ctx.stems) { if (ctx.stems.manifest) rels.push(ctx.stems.manifest); rels.push(...ctx.stems.files); }
    rels.push(...ctx.midi, ...ctx.score);
    for (const r of rels) {
      assert.ok(fs.existsSync(path.resolve(studioDir, r)), `cited path missing on disk: ${r}`);
    }
  });
  await check('a case with no stems does not cite a stems manifest', () => {
    const dir = makeCase({ diagnosis: true });
    const ctx = pipeline.buildContext(dir);
    assert.strictEqual(ctx.stems, null);
  });
  await check('capabilities list only things Studio can actually invoke', () => {
    const dir = makeCase({ diagnosis: true });
    const ctx = pipeline.buildContext(dir);
    assert.ok(ctx.available_capabilities.length > 0);
    for (const c of ctx.available_capabilities) {
      assert.ok(c.core_command, `${c.id} must name the real command behind it`);
    }
  });

  // ── 6. gating ─────────────────────────────────────────────────────────────────
  console.log('\n6. the pipeline cannot jump to deep finishing early');
  await check('analysis alone cannot reach planning or finishing', () => {
    const dir = makeCase({});
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canPlan, false, 'planning needs diagnosis');
    assert.strictEqual(g.canFinish, false, 'finishing needs diagnosis');
    assert.strictEqual(g.mode, null);
  });

  // DEEP FINISH REQUIRES THE FULL PREPARATION
  await check('analysis + diagnosis does NOT unlock the finish stage', () => {
    const dir = makeCase({ diagnosis: true });
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canFinish, false,
      'stereo-only must not be auto-unlocked as the main flow');
    assert.strictEqual(g.mode, null, 'no mode before the user has chosen one');
  });
  await check('a stereo-only fallback is OFFERED, not granted', () => {
    const dir = makeCase({ diagnosis: true });
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canRequestQuick, true, 'the affordance must be reachable');
    assert.strictEqual(g.canFinishQuick, false, 'but not applied until chosen');
    assert.strictEqual(g.quickOptIn, false);
  });
  await check('the finish stage opens as FAST only after an explicit opt-in', () => {
    const dir = makeCase({ diagnosis: true });
    assert.strictEqual(pipeline.gates(pipeline.inspect(dir)).canFinish, false);
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canFinishQuick, true, 'explicit choice unlocks quick finish');
    assert.strictEqual(g.mode, 'FAST_STEREO_ONLY');
    assert.match(g.modeLabel, /仅立体声/);
    assert.strictEqual(g.canRequestQuick, false, 'no longer offered once taken');
  });
  await check('the opt-in is recorded as an attributable artifact', () => {
    const dir = makeCase({ diagnosis: true });
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    const rec = JSON.parse(fs.readFileSync(pipeline.finishModePath(dir), 'utf8'));
    assert.strictEqual(rec.mode, 'QUICK_STEREO_ONLY');
    assert.ok(rec.chosen_at, 'a human choice must carry a timestamp');
    assert.strictEqual(rec.schema, 'moodify.studio.finish-mode/0.1');
  });
  await check('separated + structured unlocks DEEP with no opt-in needed', () => {
    const dir = makeCase({ diagnosis: true, stems: true, midi: true });
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canFinish, true);
    assert.strictEqual(g.mode, 'DEEP');
    assert.strictEqual(g.canRequestQuick, false, 'no shortcut offered on the canonical path');
  });
  await check('separated WITHOUT structure still does not reach DEEP', () => {
    const dir = makeCase({ diagnosis: true, stems: true });
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canFinish, false, 'DEEP needs both separation and structure');
    assert.strictEqual(g.canRequestQuick, true);
  });
  await check('structure without separation still does not reach DEEP', () => {
    const dir = makeCase({ diagnosis: true, midi: true });
    assert.strictEqual(pipeline.gates(pipeline.inspect(dir)).canFinish, false);
  });
  await check('DEEP wins over an earlier quick opt-in once prereqs are met', () => {
    const dir = makeCase({ diagnosis: true });
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    assert.strictEqual(pipeline.gates(pipeline.inspect(dir)).mode, 'FAST_STEREO_ONLY');
    // user then does the real work — no need to undo the earlier choice
    fs.mkdirSync(path.join(dir, 'stems'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'stems', 'song__vocals.wav'), 'RIFF');
    fs.mkdirSync(path.join(dir, 'midi'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'midi', 'song_basic_pitch.mid'), 'MThd');
    assert.strictEqual(pipeline.gates(pipeline.inspect(dir)).mode, 'DEEP');
  });
  await check('a fresh case has no finish-mode artifact at all', () => {
    const dir = makeCase({ diagnosis: true });
    assert.strictEqual(fs.existsSync(pipeline.finishModePath(dir)), false);
  });
  await check('a full case walks all the way to EXPORTED', () => {
    const dir = makeCase({
      diagnosis: true, stems: true, midi: true, score: true,
      plan: true, render: true, selection: true, export: true,
    });
    assert.strictEqual(pipeline.snapshot(dir).stage, 'EXPORTED');
  });
  await check('recording a stage does not become an authority', () => {
    const dir = makeCase({ diagnosis: true });
    pipeline.recordStage(dir);
    const rec = JSON.parse(fs.readFileSync(pipeline.pipelinePath(dir), 'utf8'));
    assert.strictEqual(rec.stage, 'DIAGNOSED');
    // delete a prerequisite; the record on disk must NOT override the re-derived truth
    fs.rmSync(path.join(dir, 'studio', 'diagnosis.json'), { force: true });
    assert.strictEqual(pipeline.snapshot(dir).stage, 'ANALYZED');
    assert.strictEqual(JSON.parse(fs.readFileSync(pipeline.pipelinePath(dir), 'utf8')).stage, 'DIAGNOSED');
  });

  // ── 7. preset processing still reachable at the finishing stage ───────────────
  console.log('\n7. presets remain available at the finishing stage');
  await check('preset targets are still offered and unchanged', () => {
    const { getBackend } = require(path.join(__dirname, '..', 'src', 'backends'));
    const local = getBackend('local');
    assert.deepStrictEqual(local.TARGETS, ['clean_master', 'warm_vocal', 'wide_space']);
  });
  await check('the preset backend is untouched by the reordering', () => {
    const { getBackend } = require(path.join(__dirname, '..', 'src', 'backends'));
    assert.strictEqual(typeof getBackend('local').process, 'function');
  });

  try { fs.rmSync(tmpRoot, { recursive: true, force: true }); } catch { /* best effort */ }

  console.log(`\n${passed} passed, ${failures.length} failed`);
  if (failures.length) {
    console.log('\nFailures:');
    for (const f of failures) console.log('  - ' + f);
    process.exit(1);
  }
})().catch((err) => {
  console.error('TEST HARNESS ERROR:', err);
  process.exit(1);
});
