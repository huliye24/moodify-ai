#!/usr/bin/env node
/**
 * Headless test for the Studio production pipeline (V4).
 *
 * CONTRACT: docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md
 *
 *     检测 → 分轨 → 结构 → 修音 → 复合 → 复检 → 选定 → 导出
 *
 * What this proves, and why each one matters:
 *
 *  1 stage derivation        deleting artifacts moves the cursor backwards, by itself
 *  2 the reversibility gate  ④修音 stays LOCKED until 分解→复合 is proven to return the
 *                            original; this is the only measurable proxy for decomposition
 *                            quality (the original stems are unknowable), and it is the
 *                            reason adopting "multi-stem beats single-stem" is safe
 *  3 pair integrity          one side alone is a半成品: TUNED requires BOTH sides
 *  4 stage-by-stage gating   ⑤ needs 修音, ⑥ needs 复合, ⑦ needs 复检, ⑧ needs a choice
 *  5 the third exit          ORIGINAL is a first-class choice, not a fallback
 *  5b the choice gate        a choice needs a pair that exists, BOTH candidates and a real
 *                            recheck — at write time AND when deriving `chosen`, so an unbacked
 *                            ledger row cannot reach CHOSEN or unlock ⑧导出
 *  5c the blocked-deep switch  when the deep path cannot run (no roundtrip / failed roundtrip /
 *                            no per-stem Core ability) the explicit pure-stereo switch is OFFERED
 *                            again — the gate key is `!deepExecutable`, not `!deepAssetsReady`
 *                            (2026-10-04 human ruling; CANON_CHANGE = YES)
 *  6 the quick route         skips decomposition, still walks 修音→复合→复检→选定
 *  7 discovery + context     stems/MIDI found, honest grades carried, only existing paths cited
 *  8 capability honesty      the three presets are gone; unimplemented Core abilities are
 *                            LISTED AS UNAVAILABLE rather than mapped onto something similar
 *  9 retired code            diagnosis/plan no longer feed any stage
 *
 * Fixtures are SYNTHESISED, so the assertions are deterministic and do not depend on
 * whatever happens to be in ~/.moodify/cases.
 *
 * Run: node scripts/test-pipeline.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');

const pipeline = require(path.join(__dirname, '..', 'src', 'pipeline'));
const tuning = require(path.join(__dirname, '..', 'src', 'tuning'));

let passed = 0;
const failures = [];
async function check(label, fn) {
  try { await fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

// ── fixture ─────────────────────────────────────────────────────────────────────

const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-pipeline-test-'));
let caseSeq = 0;
let pairSeq = 0;

/** A real-shaped Core report. Notes the finding kinds Core can actually produce. */
function makeReport({ withFinding = false } = {}) {
  const findings = withFinding
    ? [{
      code: 'TRUE_PEAK_MARGIN_EXCEEDED',
      severity: 'WARNING',
      message: 'true peak margin below 0.5 dB',
      metric: 'true_peak_dbfs',
      observed_value: 0.28,
      unit: 'dBFS',
      calibration_status: 'DEFAULT_UNCALIBRATED',
      evidence_refs: ['metrics.json'],
      check: 'absolute_rule',
    }]
    : [];
  return {
    protocol: 'moodify.sound/0.2',
    report_schema_version: 'moodify.msp_report/0.2',
    generated_at: '2026-10-04T00:00:00+00:00',
    job: { type: 'analyze', source: 'song.wav' },
    case: { case_id: 'case_test' },
    source: { name: 'song.wav', sha256: 'sha256:' + 'a'.repeat(64), duration_s: 30, channels: 2, sample_rate: 48000 },
    representation: {},
    measurements: [],
    findings,
    plan: { status: 'DRAFT_PLAN_NOT_EXECUTED', nodes: [], next_actions: [], notes: [] },
    judgment_boundary: { layer1_measurement: 'EXECUTED', layer2_comparison: 'NOT_RUN' },
    technical_state: { overall: 'PARTIAL', workflow_decision: 'NO_TECHNICAL_BLOCKERS', reasons: [] },
    provenance: { core_version: '1.0.0-rc.1' },
  };
}

/**
 * Create one tuning pair on disk.
 *   tuned     both sides have tuned/*.wav
 *   composed  both sides additionally have mix.wav
 *   recheck   a recheck.json that a real ⑥ run would produce: correct schema, this pair's id,
 *             and three report paths that exist on disk, with alignable metrics.
 *             A recheck that satisfies none of that is NOT a recheck — see §5b.
 *   keep      record a decision with that exit
 *
 * `recheck` may also be the string 'BOGUS' to write a structurally invalid recheck.json, which
 * exists only so the test can prove such a thing does not unlock ⑦/⑧.
 */
function addPair(dir, { tuned = false, composed = false, recheck = false, keep = null, mode = 'DEEP' } = {}) {
  const id = tuning.newPairId();
  tuning.createPairDir(dir, id);
  fs.writeFileSync(path.join(tuning.pairDir(dir, id), 'pair.json'), JSON.stringify({
    schema: 'moodify.core.tuning-pair/0.1',
    pair_id: id,
    mode,
    created_at: new Date(Date.now() + (++pairSeq)).toISOString(),
    tiers: { A: 'conservative', B: 'aggressive' },
    calibration_status: 'UNCALIBRATED_ENGINEERING_DEFAULT',
  }));
  const reports = { original: path.join(dir, 'report.json') };
  for (const side of tuning.SIDE_DIRS) {
    const sdir = tuning.sideDir(dir, id, side);
    fs.mkdirSync(sdir, { recursive: true });
    if (tuned) {
      fs.mkdirSync(path.join(sdir, 'tuned'), { recursive: true });
      fs.writeFileSync(path.join(sdir, 'tuned', 'vocals.wav'), 'RIFF');
    }
    if (composed) fs.writeFileSync(path.join(sdir, 'mix.wav'), 'RIFF');
  }
  if (recheck) {
    const pairDirAbs = tuning.pairDir(dir, id);
    if (recheck === 'BOGUS') {
      fs.writeFileSync(path.join(pairDirAbs, 'recheck.json'),
        JSON.stringify({ schema: 'moodify.studio.recheck/0.1', pair_id: 'tune_someone_else' }));
    } else {
      for (const side of tuning.SIDE_DIRS) reports[side] = path.join(tuning.sideDir(dir, id, side), 'report.json');
      for (const [key, file] of Object.entries(reports)) {
        if (key === 'original') continue; // the case's own report.json already exists
        fs.writeFileSync(file, JSON.stringify(makeReport({ withFinding: false })));
      }
      fs.writeFileSync(path.join(pairDirAbs, 'recheck.json'), JSON.stringify({
        schema: 'moodify.studio.recheck/0.1',
        pair_id: id,
        original: { report: reports.original },
        A: { report: reports.A },
        B: { report: reports.B },
        alignable: ['integrated_lufs'],
        summary: { alignable_count: 1, not_alignable_count: 0, A_changed_metrics: 0, B_changed_metrics: 0 },
      }));
    }
  }
  if (keep) tuning.appendDecision(dir, { pairId: id, kept: keep, role: 'creator', requestId: 'req_' + id });
  return id;
}

/** Build a case with exactly the artifacts requested. */
function makeCase(opts = {}) {
  const dir = path.join(tmpRoot, `case_${String(++caseSeq).padStart(4, '0')}`);
  fs.mkdirSync(path.join(dir, 'studio'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'case.json'), JSON.stringify({ case_id: 'case_test' }));

  if (opts.report !== false) {
    fs.writeFileSync(path.join(dir, 'report.json'), JSON.stringify(makeReport({ withFinding: opts.withFinding })));
    fs.writeFileSync(path.join(dir, 'measurements.json'), JSON.stringify([]));
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
  if (opts.roundtrip !== undefined) {
    fs.writeFileSync(path.join(dir, 'studio', 'roundtrip.json'), JSON.stringify({
      schema: 'moodify.studio.roundtrip/0.1',
      engine: 'dsp_center_hpss',
      grade: 'PREVIEW_NOT_MASTERING_GRADE',
      passed: opts.roundtrip,
      measured: { max_sample_error_dbfs: opts.roundtrip ? -72.4 : -18.1, correlation: opts.roundtrip ? 0.9999 : 0.61 },
    }));
  }
  if (opts.pair) addPair(dir, opts.pair);
  if (opts.export) {
    fs.mkdirSync(path.join(dir, 'studio', 'export'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'studio', 'export', 'export_record.json'), '{}');
  }
  return dir;
}

/** full deep prerequisites, optionally with a passing reversibility check */
const deepOpts = (extra = {}) => ({ stems: true, midi: true, roundtrip: true, ...extra });

(async () => {
  console.log('Studio pipeline test (V4)\n');

  // ── 1. stage derivation ───────────────────────────────────────────────────────
  console.log('1. stages are derived from disk, never hand-advanced');
  await check('an analysed case reports ANALYZED', () => {
    assert.strictEqual(pipeline.snapshot(makeCase({})).stage, 'ANALYZED');
  });
  await check('a bare directory reports IMPORTED', () => {
    const dir = path.join(tmpRoot, 'bare');
    fs.mkdirSync(dir, { recursive: true });
    assert.strictEqual(pipeline.snapshot(dir).stage, 'IMPORTED');
  });
  await check('deep prerequisites alone reach STRUCTURED, and no further', () => {
    assert.strictEqual(pipeline.snapshot(makeCase(deepOpts())).stage, 'STRUCTURED');
  });
  await check('the stage cursor contains no retired V3 names', () => {
    for (const gone of ['DIAGNOSED', 'PLANNED', 'RENDERED', 'VERIFIED']) {
      assert.ok(!pipeline.STAGES.includes(gone), `V3 stage ${gone} must be gone`);
    }
    assert.deepStrictEqual([...pipeline.STAGES], [
      'IMPORTED', 'ANALYZED', 'SEPARATED', 'STRUCTURED',
      'TUNED', 'COMPOSED', 'RECHECKED', 'CHOSEN', 'EXPORTED',
    ]);
  });
  await check('deleting artifacts moves the cursor backwards by itself', () => {
    const dir = makeCase({
      stems: true, midi: true, roundtrip: true, export: true,
      pair: { tuned: true, composed: true, recheck: true, keep: 'B' },
    });
    assert.strictEqual(pipeline.snapshot(dir).stage, 'EXPORTED');
    fs.rmSync(path.join(dir, 'studio', 'tuning'), { recursive: true, force: true });
    assert.strictEqual(pipeline.snapshot(dir).stage, 'STRUCTURED');
  });

  // ── 2. the reversibility gate ─────────────────────────────────────────────────
  console.log('\n2. the reversibility gate — ④修音 stays locked until 分解→复合 is proven');
  await check('without roundtrip.json, ④ is locked and says why', () => {
    const dir = makeCase({ stems: true, midi: true });   // no roundtrip
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.deepReady, true, 'decomposition itself is complete');
    assert.strictEqual(g.reversible, false);
    assert.strictEqual(g.canTune, false, 'the gate must not unlock on an unproven decomposition');
    assert.ok(g.tuneBlockers.some((b) => /可逆性未验证/.test(b)), 'must name the real reason');
  });
  await check('a FAILED roundtrip keeps ④ locked and says the composite drifted', () => {
    const dir = makeCase({ stems: true, midi: true, roundtrip: false });
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canTune, false);
    assert.ok(g.tuneBlockers.some((b) => /未能回到原版/.test(b)));
  });
  await check('a PASSED roundtrip satisfies the reversible half — but ④ also needs the Core ability', () => {
    const dir = makeCase(deepOpts());
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.reversible, true, 'the reversibility half is satisfied');
    // 2026-10-04 裁定：④（深度）需要 deepAssetsReady ∧ reversible ∧ **深度 Core 能力可用**。
    // 第三项今天不成立（逐轨能力未实现），所以 canTune 仍是 false —— 这是如实反映现状，
    // 不是把门禁放松或收紧：能力到位的那一天，同一段逻辑就会放行。
    assert.strictEqual(g.canTune, false);
    assert.strictEqual(g.deepExecutable, false);
    assert.ok(g.deepBlockers.includes('DEEP_CORE_UNAVAILABLE'), 'the real missing piece must be named');
    assert.ok(!g.deepBlockers.includes('NO_ROUNDTRIP'), 'reversibility is NOT the missing piece here');
    const withCapability = pipeline.modeDecision(g.facts, { deepCoreAvailable: true });
    assert.strictEqual(withCapability.deepExecutable, true, 'the gate is otherwise satisfied');
    assert.strictEqual(withCapability.mode, 'DEEP');
    assert.strictEqual(withCapability.canRequestQuick, false,
      'once the deep path really runs, the shortcut is not offered by default');
  });
  await check('the gate never invents a pass: only passed===true counts', () => {
    for (const v of [undefined, null, false, 0, 'true', 1]) {
      const dir = makeCase({ stems: true, midi: true, roundtrip: v });
      assert.strictEqual(pipeline.gates(pipeline.inspect(dir)).reversible, false,
        `passed=${JSON.stringify(v)} must not count as reversible`);
    }
  });

  // ── 3. pair integrity ─────────────────────────────────────────────────────────
  console.log('\n3. a pair is only a pair when both sides exist');
  await check('A alone does not reach TUNED', () => {
    const dir = makeCase(deepOpts());
    const id = tuning.newPairId();
    tuning.createPairDir(dir, id);
    const a = tuning.sideDir(dir, id, 'A');
    fs.mkdirSync(path.join(a, 'tuned'), { recursive: true });
    fs.writeFileSync(path.join(a, 'tuned', 'vocals.wav'), 'RIFF');
    assert.strictEqual(pipeline.inspect(dir).currentPair.tuned, false, 'one side is a半成品');
    assert.strictEqual(pipeline.snapshot(dir).stage, 'STRUCTURED');
  });
  await check('both sides reach TUNED; mixes then reach COMPOSED', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true } }));
    assert.strictEqual(pipeline.snapshot(dir).stage, 'TUNED');
    addPair(dir, { tuned: true, composed: true });
    assert.strictEqual(pipeline.snapshot(dir).stage, 'COMPOSED');
  });
  await check('the newest pair is found by time, not by id — same-second creates cannot swap', () => {
    const dir = makeCase(deepOpts());
    const first = addPair(dir, { tuned: true });
    const second = addPair(dir, { tuned: true, composed: true });
    assert.notStrictEqual(first, second);
    assert.strictEqual(tuning.currentPair(dir).pair_id, second, 'the later pair must win');
    // opening a fresh, empty pair must NOT roll the achieved stage backwards
    const third = addPair(dir, {});
    assert.strictEqual(tuning.currentPair(dir).pair_id, third, 'current follows the newest');
    assert.strictEqual(pipeline.snapshot(dir).stage, 'COMPOSED',
      'achievement is aggregated across pairs, not read off the newest one');
  });
  await check('a pair with mixes but no recheck stops at COMPOSED', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true, composed: true } }));
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canRecheck, true, '⑥ is available');
    assert.strictEqual(g.canChoose, false, '⑦ must wait for 复检');
    assert.strictEqual(g.canExport, false);
    assert.ok(g.chooseBlockers.some((b) => /复检/.test(b)));
  });

  // ── 4. gating chain ───────────────────────────────────────────────────────────
  console.log('\n4. each stage gates the next');
  await check('analysis only: nothing past ① is available', () => {
    const g = pipeline.gates(pipeline.inspect(makeCase({})));
    assert.strictEqual(g.canSeparate, true, '① done → ② offered');
    assert.strictEqual(g.canTune, false);
    assert.strictEqual(g.canCompose, false);
    assert.strictEqual(g.canRecheck, false);
    assert.strictEqual(g.canChoose, false);
    assert.strictEqual(g.canExport, false);
    assert.strictEqual(g.mode, null);
  });
  await check('stems without MIDI still cannot tune (MIDI is the reference)', () => {
    const g = pipeline.gates(pipeline.inspect(makeCase({ stems: true, roundtrip: true })));
    assert.strictEqual(g.canTune, false);
    assert.ok(g.tuneBlockers.some((b) => /缺 MIDI/.test(b)));
  });
  await check('score alone is not structure — MusicXML never substitutes for MIDI', () => {
    const dir = makeCase({ stems: true, score: true, roundtrip: true });
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.facts.structured, false);
    assert.strictEqual(g.canTune, false);
    const ctx = pipeline.buildContext(dir);
    assert.strictEqual(ctx.score.length, 1, 'the score is still discovered and cited');
    assert.ok(ctx.notes.some((n) => /缺少 MIDI/.test(n)), 'the gap must be stated, not silent');
  });
  await check('every locked stage explains itself', () => {
    const g = pipeline.gates(pipeline.inspect(makeCase({})));
    for (const key of ['tuneBlockers', 'composeBlockers', 'recheckBlockers', 'chooseBlockers', 'exportBlockers']) {
      assert.ok(Array.isArray(g[key]) && g[key].length > 0, `${key} must not be empty while locked`);
    }
  });

  // ── 5. the third exit ─────────────────────────────────────────────────────────
  console.log('\n5. the third exit — 保留原版 is a real choice');
  await check('EXITS offers A, B and ORIGINAL', () => {
    assert.deepStrictEqual([...tuning.EXITS], ['A', 'B', 'ORIGINAL']);
    assert.deepStrictEqual(pipeline.gates(pipeline.inspect(makeCase({}))).exits, ['A', 'B', 'ORIGINAL']);
  });
  await check('ORIGINAL counts as a choice, exactly like A or B, and unlocks ⑧', () => {
    for (const keep of ['A', 'B', 'ORIGINAL']) {
      const dir = makeCase(deepOpts({ pair: { tuned: true, composed: true, recheck: true, keep } }));
      const g = pipeline.gates(pipeline.inspect(dir));
      assert.strictEqual(g.canExport, true, `${keep}: ⑧ must unlock`);
      assert.strictEqual(pipeline.snapshot(dir).stage, 'CHOSEN');
      assert.strictEqual(pipeline.inspect(dir).decision.kept, keep);
    }
  });
  await check('⑦ stays available after a choice — a person may change their mind', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true, composed: true, recheck: true, keep: 'A' } }));
    assert.strictEqual(pipeline.gates(pipeline.inspect(dir)).canChoose, true);
    const id = pipeline.inspect(dir).currentPair.pair_id;
    tuning.appendDecision(dir, { pairId: id, kept: 'ORIGINAL', requestId: 'later' });
    assert.strictEqual(tuning.decisionFor(dir, id).kept, 'ORIGINAL', 'the latest row is effective');
  });
  await check('a decision that is neither A, B nor ORIGINAL is rejected', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true } }));
    const id = pipeline.inspect(dir).currentPair.pair_id;
    for (const bad of ['C', 'both', 'original', '', null]) {
      assert.strictEqual(tuning.appendDecision(dir, { pairId: id, kept: bad }).ok, false,
        `${JSON.stringify(bad)} must be rejected`);
    }
    assert.strictEqual(pipeline.inspect(dir).decision, null, 'nothing may have been written');
  });
  await check('the ledger is append-only and idempotent per request_id', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true, composed: true, recheck: true } }));
    const id = pipeline.inspect(dir).currentPair.pair_id;
    const first = tuning.appendDecision(dir, { pairId: id, kept: 'A', role: 'creator', requestId: 'r1' });
    assert.strictEqual(first.recorded, true);
    const retry = tuning.appendDecision(dir, { pairId: id, kept: 'A', role: 'creator', requestId: 'r1' });
    assert.strictEqual(retry.recorded, false, 'a retry must not write a second row');
    assert.strictEqual(retry.duplicate, true);
    assert.strictEqual(tuning.readDecisions(dir).length, 1);
    // a genuinely new choice with a new request id IS a new row
    tuning.appendDecision(dir, { pairId: id, kept: 'ORIGINAL', requestId: 'r2' });
    assert.strictEqual(tuning.readDecisions(dir).length, 2);
    // and the latest row is the effective decision
    assert.strictEqual(tuning.decisionFor(dir, id).kept, 'ORIGINAL');
  });

  // ── 5b. ⑦ is only reachable through a complete, rechecked pair ────────────────
  //
  // A choice is the point of no return: it is what unlocks ⑧导出. So the ledger must not accept
  // a choice for a pair that does not exist, for a half-built pair, or before ⑥复检 has actually
  // happened — and ORIGINAL is inside the same gate, because "keep the original" is the exit for
  // "both tiers are worse", not a way to deliver the source before A/B ever existed.
  console.log('\n5b. ⑦ 选定 requires a pair with two complete candidates and a real recheck');
  await check('a choice for a pair that does not exist is refused, and writes nothing', () => {
    const dir = makeCase(deepOpts());
    const r = tuning.appendDecision(dir, { pairId: 'tune_does_not_exist', kept: 'A' });
    assert.strictEqual(r.ok, false);
    assert.strictEqual(r.reason, 'PAIR_NOT_COMPLETE');
    assert.match(r.blockers[0], /修音对不存在/);
    assert.deepStrictEqual(tuning.readDecisions(dir), [], 'nothing may be appended');
  });
  await check('a half-built pair cannot be chosen (tuned only / composed but not rechecked)', () => {
    for (const pair of [{ tuned: true }, { tuned: true, composed: true }]) {
      const dir = makeCase(deepOpts({ pair }));
      const id = pipeline.inspect(dir).currentPair.pair_id;
      const r = tuning.appendDecision(dir, { pairId: id, kept: 'A' });
      assert.strictEqual(r.ok, false, `${JSON.stringify(pair)} must not be choosable`);
      assert.strictEqual(r.reason, 'PAIR_NOT_COMPLETE');
      assert.deepStrictEqual(tuning.readDecisions(dir), []);
    }
  });
  await check('a recheck belonging to another pair is not a recheck', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true, composed: true, recheck: 'BOGUS' } }));
    const id = pipeline.inspect(dir).currentPair.pair_id;
    const r = tuning.appendDecision(dir, { pairId: id, kept: 'B' });
    assert.strictEqual(r.ok, false);
    assert.ok(r.blockers.some((b) => /属于另一对/.test(b)), 'the mismatch must be named');
  });
  await check('a recheck whose referenced reports were deleted is not a recheck', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true, composed: true, recheck: true } }));
    const id = pipeline.inspect(dir).currentPair.pair_id;
    fs.rmSync(path.join(tuning.sideDir(dir, id, 'A'), 'report.json'), { force: true });
    const r = tuning.appendDecision(dir, { pairId: id, kept: 'A' });
    assert.strictEqual(r.ok, false);
    assert.ok(r.blockers.some((b) => /A 报告已不在磁盘上/.test(b)));
  });
  await check('ORIGINAL cannot bypass A/B: it is refused while the pair is incomplete', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true } }));
    const id = pipeline.inspect(dir).currentPair.pair_id;
    const r = tuning.appendDecision(dir, { pairId: id, kept: 'ORIGINAL' });
    assert.strictEqual(r.ok, false, 'the third exit must not be a shortcut around 审听');
    assert.strictEqual(r.reason, 'PAIR_NOT_COMPLETE');
    assert.strictEqual(pipeline.snapshot(dir).stage, 'TUNED', 'the cursor must not reach CHOSEN');
    assert.strictEqual(pipeline.gates(pipeline.inspect(dir)).canExport, false);
  });
  await check('the same rule answers canDecide and gates.chooseBlockers', () => {
    const incomplete = makeCase(deepOpts({ pair: { tuned: true, composed: true } }));
    assert.strictEqual(tuning.canDecide(incomplete, pipeline.inspect(incomplete).currentPair.pair_id), false);
    assert.ok(pipeline.gates(pipeline.inspect(incomplete)).chooseBlockers.some((b) => /复检/.test(b)),
      '⑦ must say what is missing');
    const complete = makeCase(deepOpts({ pair: { tuned: true, composed: true, recheck: true } }));
    assert.strictEqual(tuning.canDecide(complete, pipeline.inspect(complete).currentPair.pair_id), true);
    assert.deepStrictEqual(pipeline.gates(pipeline.inspect(complete)).chooseBlockers, []);
  });
  await check('a complete, rechecked pair is choosable — the gate is not just a wall', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true, composed: true, recheck: true, keep: 'A' } }));
    const id = pipeline.inspect(dir).currentPair.pair_id;
    assert.strictEqual(tuning.decisionFor(dir, id).kept, 'A');
    assert.strictEqual(pipeline.snapshot(dir).stage, 'CHOSEN');
    assert.strictEqual(pipeline.gates(pipeline.inspect(dir)).canExport, true);
  });
  await check('a hand-written decision without a backing pair cannot reach CHOSEN', () => {
    // The writer is guarded, but a ledger row from an older build / a hand edit is still on disk.
    // The reader must not treat it as fact: `chosen` is derived from what is on disk RIGHT NOW.
    const dir = makeCase(deepOpts());
    fs.mkdirSync(path.join(dir, 'studio', 'tuning'), { recursive: true });
    fs.appendFileSync(path.join(dir, 'studio', 'tuning', 'decisions.jsonl'),
      JSON.stringify({ schema: tuning.SCHEMA_DECISION, pair_id: 'tune_ghost', kept: 'ORIGINAL' }) + '\n');
    const info = pipeline.inspect(dir);
    assert.strictEqual(info.decisionValid, false, 'the record must not count as a backing fact');
    assert.strictEqual(info.decision.pair_id, 'tune_ghost', 'the raw record is still readable');
    assert.strictEqual(pipeline.snapshot(dir).stage, 'STRUCTURED', 'no CHOSEN without candidates');
    assert.strictEqual(pipeline.gates(info).canExport, false);
  });
  await check('deleting the candidates after a choice takes the CHOSEN stage back', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true, composed: true, recheck: true, keep: 'B' } }));
    assert.strictEqual(pipeline.snapshot(dir).stage, 'CHOSEN');
    const id = pipeline.inspect(dir).currentPair.pair_id;
    fs.rmSync(path.join(tuning.sideDir(dir, id, 'B'), 'mix.wav'), { force: true });
    // The stage walk stops at the first *required* fact that is missing, so losing one side's
    // mix takes the cursor back past COMPOSED (and therefore past RECHECKED/CHOSEN/EXPORTED)
    // all the way to TUNED. The recheck file is still there as a fact; the cursor is honest.
    assert.strictEqual(pipeline.snapshot(dir).stage, 'TUNED',
      'an artifact-derived cursor must fall back when the artifact is gone');
    assert.strictEqual(pipeline.gates(pipeline.inspect(dir)).canExport, false);
  });
  await check('reusing a request_id for a different exit is a conflict, not a silent keep', () => {
    const dir = makeCase(deepOpts({ pair: { tuned: true, composed: true, recheck: true } }));
    const id = pipeline.inspect(dir).currentPair.pair_id;
    tuning.appendDecision(dir, { pairId: id, kept: 'A', requestId: 'same' });
    const r = tuning.appendDecision(dir, { pairId: id, kept: 'B', requestId: 'same' });
    assert.strictEqual(r.ok, false);
    assert.strictEqual(r.reason, 'REQUEST_ID_CONFLICT');
    assert.strictEqual(tuning.readDecisions(dir).length, 1, 'no second row may appear');
  });

  // ── 5c. 深度受阻 → 显式快速完成入口（2026-10-04 人类裁定，CANON_CHANGE = YES）──────
  //
  // 死路：分轨 + MIDI 已存在（deepAssetsReady）但可逆性未通过、逐轨能力又未实现时，
  // 旧门禁 `canRequestQuick = baseReady ∧ ¬deepReady ∧ ¬optIn` 为 false，用户拿不到任何候选。
  // 新规则按 `!deepExecutable` 提供入口，并且**必须由人显式确认**。
  console.log('\n5c. 深度受阻时提供显式快速入口（不再是死路）');
  await check('1. 只有检测：可以请求快速完成（深度资产还没有，深度也跑不了）', () => {
    const dir = makeCase({});
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.deepAssetsReady, false);
    assert.strictEqual(g.deepExecutable, false);
    assert.strictEqual(g.fastAvailable, true);
    assert.strictEqual(g.canRequestQuick, true);
    assert.strictEqual(g.canTuneQuick, false, '未选择就不生成候选');
  });
  await check('2. 分轨 + MIDI 齐备、缺 roundtrip：**仍然**可以请求快速完成', () => {
    const dir = makeCase({ stems: true, midi: true });
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.deepAssetsReady, true, '深度资产确实齐备');
    assert.strictEqual(g.canRequestQuick, true, '这正是旧规则制造死路的那一格');
    assert.ok(g.deepBlockers.includes('NO_ROUNDTRIP'));
    assert.ok(g.deepBlockers.includes('DEEP_CORE_UNAVAILABLE'));
  });
  await check('3. roundtrip passed:false：可以请求快速完成，且不伪造通过', () => {
    const dir = makeCase({ stems: true, midi: true, roundtrip: false });
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.reversible, false, 'a failed roundtrip is still a failure');
    assert.ok(g.deepBlockers.includes('ROUNDTRIP_FAILED'));
    assert.strictEqual(g.canRequestQuick, true);
  });
  await check('4. roundtrip 通过但深度能力未就绪：可以请求快速完成', () => {
    const dir = makeCase(deepOpts()); // stems + midi + passing roundtrip
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.reversible, true);
    assert.strictEqual(g.canTune, false, '逐轨能力仍未实现 → 深度不可执行');
    assert.ok(!g.deepBlockers.includes('NO_ROUNDTRIP') && !g.deepBlockers.includes('ROUNDTRIP_FAILED'));
    assert.deepStrictEqual(g.deepBlockers, ['DEEP_CORE_UNAVAILABLE']);
    assert.strictEqual(g.canRequestQuick, true);
  });
  await check('5. 用户未选择：canTuneQuick=false，且磁盘上不会冒出 pair', () => {
    const dir = makeCase(deepOpts());
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.quickOptIn, false);
    assert.strictEqual(g.canTuneQuick, false);
    assert.strictEqual(g.mode, 'DEEP', '默认仍是深度模式（只是当前跑不了）');
    assert.strictEqual(g.modeExecutable, false);
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'tuning')), false);
  });
  await check('6. 上述任一受阻状态下显式选择 → FAST 生效，且深度资产一个不丢', () => {
    for (const opts of [{}, { stems: true, midi: true }, { stems: true, midi: true, roundtrip: false }, deepOpts()]) {
      const dir = makeCase(opts);
      const before = pipeline.inspect(dir);
      pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY', '测试：模拟人类确认');
      const g = pipeline.gates(pipeline.inspect(dir));
      assert.strictEqual(g.mode, 'FAST_STEREO_ONLY', JSON.stringify(opts));
      assert.strictEqual(g.canTuneQuick, true, JSON.stringify(opts));
      assert.strictEqual(g.canRequestQuick, false, 'already taken, not offered again');
      // 深度资产、失败证据一个都没被模式选择动过
      const after = pipeline.inspect(dir);
      assert.strictEqual(after.hasStems, before.hasStems);
      assert.strictEqual(after.hasMidi, before.hasMidi);
      assert.strictEqual(after.reversible, before.reversible, '模式选择绝不改动可逆性事实');
      assert.strictEqual(after.roundtrip && after.roundtrip.passed, before.roundtrip && before.roundtrip.passed);
      assert.deepStrictEqual(after.stemsManifest, before.stemsManifest);
    }
  });
  await check('7. 快速模式不改变 reversible，也不删除任何深度资产', () => {
    const dir = makeCase({ stems: true, midi: true, roundtrip: false });
    const snapshotBefore = JSON.stringify(pipeline.inspect(dir).roundtrip);
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    const info = pipeline.inspect(dir);
    assert.strictEqual(info.reversible, false, 'a failed roundtrip stays failed');
    assert.strictEqual(JSON.stringify(info.roundtrip), snapshotBefore);
    assert.strictEqual(info.hasStems, true);
    assert.strictEqual(info.hasMidi, true);
    assert.strictEqual(fs.existsSync(path.join(dir, 'stems', 'song__vocals.wav')), true);
    assert.strictEqual(fs.existsSync(pipeline.finishModePath(dir)), true, 'only the mode record changed');
  });
  await check('8. 深度路径真实可执行时仍默认 DEEP，不自动显示为 FAST', () => {
    const deepFacts = { analyzed: true, separated: true, structured: true, reversible: true,
      baseReady: true, deepReady: true };
    const future = pipeline.modeDecision(deepFacts, { optIn: false, deepCoreAvailable: true, fastAvailable: true });
    assert.strictEqual(future.deepExecutable, true);
    assert.strictEqual(future.mode, 'DEEP', 'deep wins when it actually works');
    assert.strictEqual(future.canRequestQuick, false, 'no shortcut offered by default');
    assert.strictEqual(future.modeExecutable, true);
    // 但人的显式选择依然优先，不会因为深度可用就被撤销
    const chosen = pipeline.modeDecision(deepFacts, { optIn: true, deepCoreAvailable: true, fastAvailable: true });
    assert.strictEqual(chosen.mode, 'FAST_STEREO_ONLY');
    assert.strictEqual(chosen.quick, true, 'the explicit choice stays active');
    assert.strictEqual(chosen.canRequestQuick, false);
  });
  await check('9. 已有 pair / recheck / 选定不会被模式选择倒退或破坏', () => {
    const dir = makeCase(deepOpts({
      pair: { tuned: true, composed: true, recheck: true, keep: 'B' },
    }));
    const before = pipeline.snapshot(dir);
    assert.strictEqual(before.stage, 'CHOSEN');
    const picksBefore = fs.readFileSync(path.join(dir, 'studio', 'tuning', 'decisions.jsonl'), 'utf8');
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    const after = pipeline.snapshot(dir);
    assert.strictEqual(after.stage, 'CHOSEN', 'the cursor must not move');
    assert.strictEqual(after.gates.canExport, true, 'nor may ⑧ be closed');
    assert.strictEqual(after.info.decisionValid, true);
    assert.strictEqual(fs.readFileSync(path.join(dir, 'studio', 'tuning', 'decisions.jsonl'), 'utf8'), picksBefore);
    assert.strictEqual(after.gates.mode, 'FAST_STEREO_ONLY', 'the mode is what the human chose');
  });
  await check('受阻时的阻断原因分行说明：缺什么 + 可以怎么补救', () => {
    const dir = makeCase({ stems: true, midi: true });
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.tuneBlockers.length > 0, true, '当前模式（DEEP）的阻断说明');
    assert.ok(g.deepTuneBlockers.some((b) => /可逆性未验证/.test(b)));
    assert.ok(g.deepTuneBlockers.some((b) => /逐轨修音/.test(b)), '深度能力未就绪必须单独说出来');
    assert.deepStrictEqual(g.tuneBlockers, g.deepTuneBlockers, 'DEEP 模式下两者一致');
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    const fast = pipeline.gates(pipeline.inspect(dir));
    assert.deepStrictEqual(fast.tuneBlockers, [], 'FAST 模式下深度阻断不再是当前阻断');
    assert.ok(fast.deepTuneBlockers.length > 0, '但深度为什么锁着仍然照实保留');
  });

  // ── 6. the quick route ────────────────────────────────────────────────────────
  console.log('\n6. the quick route skips decomposition, not verification');
  await check('quick is offered but never auto-unlocked', () => {
    const dir = makeCase({});
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canRequestQuick, true);
    assert.strictEqual(g.canTuneQuick, false, 'stereo-only must not open by default');
    assert.strictEqual(g.quickOptIn, false);
  });
  await check('an explicit opt-in opens it and the badge is honest', () => {
    const dir = makeCase({});
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canTuneQuick, true);
    assert.strictEqual(g.mode, 'FAST_STEREO_ONLY');
    assert.match(g.modeLabel, /仅立体声/);
    assert.strictEqual(g.canRequestQuick, false, 'not offered again once taken');
    assert.strictEqual(g.canTune, false, 'the quick route is NOT the deep ④');
  });
  await check('the quick route still must walk 修音→复合→复检→选定', () => {
    const dir = makeCase({ pair: { tuned: true, composed: true, recheck: true, keep: 'A', mode: 'FAST_STEREO_ONLY' } });
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canExport, true, 'it must not be "AI processed → auto delivered"');
    assert.strictEqual(pipeline.snapshot(dir).stage, 'CHOSEN');
  });
  await check('an explicit opt-in is not overridden by deep assets (2026-10-04 裁定)', () => {
    // 旧 Canon 说「深度优先」：分轨 + MIDI 一旦齐备，模式就翻回 DEEP。
    // 人类裁定改为：**人的显式选择优先**。否则用户在深度跑不通时切到快速，
    // 只要资产在，模式又会被翻回去 —— 等于把刚给出的补救路径收回。
    const dir = makeCase(deepOpts());
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.deepAssetsReady, true, 'the deep assets really are there');
    assert.strictEqual(g.mode, 'FAST_STEREO_ONLY', 'the human choice wins over deepAssetsReady');
    assert.strictEqual(g.modeLabel, '快速（仅立体声）');
    assert.strictEqual(g.canTuneQuick, true, 'and the pure-stereo route stays open');
    assert.strictEqual(g.canTune, false, 'the deep ④ is still not open (Core ability missing)');
    assert.strictEqual(g.quickOptIn, true);
  });
  await check('the opt-in is an attributable artifact', () => {
    const dir = makeCase({});
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    const rec = JSON.parse(fs.readFileSync(pipeline.finishModePath(dir), 'utf8'));
    assert.strictEqual(rec.mode, 'QUICK_STEREO_ONLY');
    assert.strictEqual(rec.schema, 'moodify.studio.finish-mode/0.1');
    assert.ok(rec.chosen_at, 'a human choice must carry a timestamp');
  });
  await check('a fresh case has no finish-mode artifact', () => {
    assert.strictEqual(fs.existsSync(pipeline.finishModePath(makeCase({}))), false);
  });

  // ── 7. discovery + context ────────────────────────────────────────────────────
  console.log('\n7. discovery and context');
  await check('the honest separation grade is carried, not softened', () => {
    const ctx = pipeline.buildContext(makeCase({ stems: true }));
    assert.strictEqual(ctx.stems.engine, 'dsp_center_hpss');
    assert.match(ctx.stems.engine_note, /不构成母带级分轨/);
    assert.strictEqual(ctx.stems.grade, 'PREVIEW_NOT_MASTERING_GRADE');
    assert.ok(ctx.notes.some((n) => /预览级|快速\/预览级/.test(n)));
  });
  await check('missing structure is stated, not silently omitted', () => {
    const ctx = pipeline.buildContext(makeCase({}));
    assert.ok(ctx.notes.some((n) => /结构信息缺失/.test(n)));
  });
  await check('every path context.json cites exists on disk', () => {
    const dir = makeCase(deepOpts({ score: true }));
    const ctx = pipeline.buildContext(dir);
    const studioDir = path.join(dir, 'studio');
    const rels = [];
    if (ctx.analysis.report) rels.push(ctx.analysis.report);
    if (ctx.analysis.measurements) rels.push(ctx.analysis.measurements);
    if (ctx.stems) { if (ctx.stems.manifest) rels.push(ctx.stems.manifest); rels.push(...ctx.stems.files); }
    rels.push(...ctx.midi, ...ctx.score);
    assert.ok(rels.length > 0);
    for (const r of rels) {
      assert.ok(fs.existsSync(path.resolve(studioDir, r)), `cited path missing on disk: ${r}`);
    }
  });
  await check('preserve lives on ④ now, and defaults to empty (it is a human judgement)', () => {
    const ctx = pipeline.buildContext(makeCase(deepOpts()));
    assert.deepStrictEqual(ctx.preserve, [], 'must not be pre-filled by the machine');
  });
  await check('context reports the reversibility state explicitly', () => {
    const ok = pipeline.buildContext(makeCase(deepOpts()));
    assert.strictEqual(ok.readiness.reversibility.passed, true);
    const no = pipeline.buildContext(makeCase({ stems: true, midi: true }));
    assert.strictEqual(no.readiness.reversibility.passed, false);
    assert.strictEqual(no.readiness.reversibility.path, null);
  });

  // ── 8. capability honesty ─────────────────────────────────────────────────────
  console.log('\n8. capabilities: what exists is listed, what does not is marked unavailable');
  await check('the three presets are gone from the capability list', () => {
    const ids = pipeline.CAPABILITIES.map((c) => c.id);
    assert.ok(!ids.includes('existing-presets'), 'presets retired 2026-10-04');
    assert.ok(!ids.includes('clean_master'));
    for (const c of pipeline.CAPABILITIES) {
      assert.ok(c.core_command, `${c.id} must name the real command behind it`);
    }
  });
  await check('unimplemented Core abilities are listed as PLANNED with a reason, never mapped', () => {
    const ids = pipeline.PLANNED_CAPABILITIES.map((c) => c.id);
    for (const need of ['reversibility-check', 'stem-tuning', 'multi-stem-compose']) {
      assert.ok(ids.includes(need), `${need} must be declared as not-yet-available`);
    }
    for (const c of pipeline.PLANNED_CAPABILITIES) {
      assert.ok(c.reason && c.reason.length > 10, `${c.id} must state why it is unavailable`);
      assert.ok(!pipeline.CAPABILITIES.some((a) => a.id === c.id), `${c.id} must not also be claimed as available`);
    }
  });
  await check('available capabilities name a real stage and the real command behind them', () => {
    const stages = new Set(['ANALYZE', 'SEPARATE', 'STRUCTURE', 'TUNE', 'EXPORT']);
    for (const c of pipeline.CAPABILITIES) {
      assert.ok(stages.has(c.stage), `${c.id} claims an unexpected stage ${c.stage}`);
      assert.ok(c.core_command && c.core_command.length > 10, `${c.id} must name the real command`);
    }
  });
  await check('the pair capability is the whole-track one; the per-stem path stays unavailable', () => {
    // 2026-10-04 Phase 2：Core 有了 FAST_STEREO_ONLY 的整轨两档渲染（MIP-0002 附录 A），
    // 于是 ④ 多了一项**真的能调**的能力。深度路径的逐轨能力仍然不可用——
    // 快速可用绝不能被读成深度可用（V4 §4.2）。
    const fast = pipeline.CAPABILITIES.find((c) => c.id === 'fast-stereo-pair');
    assert.ok(fast, 'Studio can really invoke the whole-track pair render');
    assert.match(fast.core_command, /tuning render-pair --mode fast-stereo-only/);
    const planned = pipeline.PLANNED_CAPABILITIES.map((c) => c.id);
    for (const deep of ['stem-tuning', 'multi-stem-compose', 'reversibility-check']) {
      assert.ok(planned.includes(deep), `${deep} must stay declared as not-yet-available`);
    }
  });

  // ── 9. ②问题 / ⑤方案 已删除 ───────────────────────────────────────────────────
  // 2026-10-04 裁定把它们退场。这里断言的是**真的删掉了**，而不是留一个还会被误用的壳。
  console.log('\n9. ②问题 / ⑤方案 are gone, not merely unused');
  await check('the retired API is absent from the module surface', () => {
    for (const gone of ['buildDiagnosis', 'writeDiagnosis', 'readDiagnosis', 'addHumanNote',
      'resolvePointer', 'writeContextPlan', 'preparePlan']) {
      assert.strictEqual(pipeline[gone], undefined, `${gone} must be deleted, not kept as a stub`);
    }
  });
  await check('no stage fact mentions diagnosis / plan / render / verify any more', () => {
    const f = pipeline.snapshot(makeCase(deepOpts())).facts;
    for (const gone of ['diagnosed', 'planned', 'rendered', 'verified']) {
      assert.strictEqual(f[gone], undefined, `fact ${gone} must be gone`);
    }
  });

  // ── 10. the record is never the authority ─────────────────────────────────────
  console.log('\n10. pipeline.json is a record, not an authority');
  await check('a stored stage never overrides the re-derived truth', () => {
    const dir = makeCase(deepOpts());
    pipeline.recordStage(dir);
    const recPath = pipeline.pipelinePath(dir);
    assert.strictEqual(JSON.parse(fs.readFileSync(recPath, 'utf8')).stage, 'STRUCTURED');
    fs.rmSync(path.join(dir, 'midi'), { recursive: true, force: true });
    assert.strictEqual(pipeline.snapshot(dir).stage, 'SEPARATED', 'truth was re-derived');
    assert.strictEqual(JSON.parse(fs.readFileSync(recPath, 'utf8')).stage, 'STRUCTURED', 'the stale record stays stale');
  });
  await check('the record carries the V4 schema version', () => {
    const dir = makeCase({});
    assert.strictEqual(pipeline.recordStage(dir).schema, 'moodify.studio.pipeline/0.2');
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
