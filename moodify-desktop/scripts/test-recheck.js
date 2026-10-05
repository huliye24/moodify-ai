#!/usr/bin/env node
/**
 * Headless test for ⑥ 复检 — the three-way metric alignment table.
 *
 * CONTRACT: docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md §6
 *
 * What this proves (and why each one matters):
 *   1  identical reports          → every metric alignable, every delta exactly 0
 *   2  a metric missing on one side → moves to not_alignable, never silently dropped
 *   3  unit mismatch              → not_alignable (0.5 "ratio" and 0.5 "dB" are not the same number)
 *   4  Core marked a measurement non-VALID → not_alignable (Core itself said it is unreliable)
 *   5  non-numeric value          → not_alignable, no NaN leaking into the artifact
 *   6  a missing report           → REFUSES; it must not emit an empty table that reads as
 *                                   "recheck already happened"
 *   7  conservation               → alignable ∪ not_alignable == every id seen, no invention
 *   8  write/read roundtrip       → artifact lands at <case>/studio/tuning/<pair>/recheck.json
 *
 * Fixtures are SYNTHESISED so the assertions are deterministic and do not depend on what is
 * currently in ~/.moodify/cases.
 *
 * Run: node scripts/test-recheck.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');

const recheck = require(path.join(__dirname, '..', 'src', 'recheck'));

let passed = 0;
const failures = [];
async function check(label, fn) {
  try { await fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

// ── fixture ─────────────────────────────────────────────────────────────────────

/** A real-shaped Core report: measurements are [{id, value, unit, status, group}]. */
function report(measurements, extra = {}) {
  return {
    protocol: 'moodify.sound/0.2',
    report_schema_version: 'moodify.msp_report/0.2',
    generated_at: '2026-10-04T00:00:00+00:00',
    case: { case_id: 'case_test' },
    source: { name: 'song.wav', sha256: 'sha256:' + 'a'.repeat(64), duration_s: 30, channels: 2, sample_rate: 48000 },
    measurements,
    findings: [],
    ...extra,
  };
}

const m = (id, value, unit = 'ratio', status = 'VALID', group = 'bands') => ({ id, value, unit, status, group });

const PATHS = {
  original: 'C:/cases/case_test/report.json',
  A: 'C:/cases/case_test/studio/tuning/tune_x/A/analysis/report.json',
  B: 'C:/cases/case_test/studio/tuning/tune_x/B/analysis/report.json',
};

/** Shorthand: original / A / B measurement arrays. */
function build(orig, a, b, mode) {
  return recheck.buildRecheck({
    pairId: 'tune_20261004T000000_abcd',
    paths: PATHS,
    reports: { original: report(orig), A: report(a), B: report(b) },
    mode,
    generatedAt: '2026-10-04T00:00:00.000Z',
  });
}

const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-recheck-test-'));

// ── tests ───────────────────────────────────────────────────────────────────────

(async () => {
  console.log('recheck');

  await check('1 identical reports → all alignable, all deltas 0', async () => {
    const px = [m('integrated_lufs', -14.0, 'dBFS'), m('sample_peak_dbfs', -1.2, 'dBFS'), m('spectral_centroid_hz', 2400, 'Hz')];
    const r = build(px, px, px);
    assert.strictEqual(r.ok, true, 'should build');
    assert.deepStrictEqual(r.payload.alignable, ['integrated_lufs', 'sample_peak_dbfs', 'spectral_centroid_hz']);
    assert.strictEqual(r.payload.not_alignable.length, 0);
    for (const id of r.payload.alignable) {
      assert.strictEqual(r.payload.A.delta_vs_original[id], 0, 'A delta ' + id);
      assert.strictEqual(r.payload.B.delta_vs_original[id], 0, 'B delta ' + id);
    }
  });

  await check('2 metric missing on one side → not_alignable, names the missing side', async () => {
    const r = build(
      [m('integrated_lufs', -14.0, 'dBFS'), m('crest_factor_db', 11.5, 'dB')],
      [m('integrated_lufs', -13.4, 'dBFS'), m('crest_factor_db', 10.9, 'dB')],
      [m('integrated_lufs', -13.8, 'dBFS')],                        // B lost crest_factor_db
    );
    assert.deepStrictEqual(r.payload.alignable, ['integrated_lufs']);
    assert.strictEqual(r.payload.not_alignable.length, 1);
    const na = r.payload.not_alignable[0];
    assert.strictEqual(na.name, 'crest_factor_db');
    assert.ok(/B/.test(na.reason), 'reason must name B: ' + na.reason);
    assert.ok(!(('crest_factor_db') in r.payload.B.metrics), 'missing metric must not appear in B.metrics');
  });

  await check('3 unit mismatch → not_alignable, not compared as if equal', async () => {
    const r = build(
      [m('stereo_width_proxy', 0.42, 'ratio')],
      [m('stereo_width_proxy', 0.42, 'ratio')],
      [m('stereo_width_proxy', 0.42, 'dB')],                        // same number, different unit
    );
    assert.deepStrictEqual(r.payload.alignable, []);
    assert.strictEqual(r.payload.not_alignable.length, 1);
    assert.ok(/单位不一致/.test(r.payload.not_alignable[0].reason));
    assert.strictEqual(r.payload.B.delta_vs_original.stereo_width_proxy, undefined);
  });

  await check('4 Core marked it non-VALID → not_alignable', async () => {
    const r = build(
      [m('estimated_noise_floor_dbfs', -72.0, 'dBFS')],
      [m('estimated_noise_floor_dbfs', -71.0, 'dBFS')],
      [m('estimated_noise_floor_dbfs', -71.4, 'dBFS', 'INVALID')],
    );
    assert.deepStrictEqual(r.payload.alignable, []);
    assert.strictEqual(r.payload.not_alignable.length, 1);
    assert.ok(/非 VALID/.test(r.payload.not_alignable[0].reason));
    assert.ok(/B=INVALID/.test(r.payload.not_alignable[0].reason));
  });

  await check('5 non-numeric value → not_alignable, no NaN in the artifact', async () => {
    const r = build(
      [m('phase_risk_ratio', 0.1, 'ratio')],
      [m('phase_risk_ratio', null, 'ratio')],                       // Core gave a null
      [m('phase_risk_ratio', 0.12, 'ratio')],
    );
    assert.deepStrictEqual(r.payload.alignable, []);
    assert.strictEqual(r.payload.not_alignable.length, 1);
    assert.ok(/非数值/.test(r.payload.not_alignable[0].reason));
    assert.ok(!('phase_risk_ratio' in r.payload.A.delta_vs_original), 'no delta for a non-numeric metric');
    assert.ok(!('phase_risk_ratio' in r.payload.A.metrics), 'no value for a non-numeric metric');
    assert.ok(!/NaN|Infinity/.test(JSON.stringify(r.payload)), 'no NaN / Infinity may leak into the artifact');
  });

  await check('6 a missing report → refuses, never an empty-looking table', async () => {
    const r = recheck.buildRecheck({
      pairId: 'tune_x', paths: PATHS,
      reports: { original: report([m('a', 1)]), A: report([m('a', 1)]), B: null },
    });
    assert.strictEqual(r.ok, false);
    assert.strictEqual(r.reason, 'MISSING_REPORT');
    assert.deepStrictEqual(r.missing, ['B']);
    assert.strictEqual(r.payload, undefined, 'must not emit a payload');
  });

  await check('7 conservation — every id lands in exactly one bucket, none invented', async () => {
    const r = build(
      [m('only_original', 1), m('shared', 2), m('orig_and_a', 3)],
      [m('shared', 2.5), m('orig_and_a', 3), m('only_a', 4)],
      [m('shared', 2.2), m('only_b', 5)],
    );
    const seen = new Set([...r.payload.alignable, ...r.payload.not_alignable.map((x) => x.name)]);
    for (const id of ['only_original', 'shared', 'orig_and_a', 'only_a', 'only_b']) {
      assert.ok(seen.has(id), 'id lost from both buckets: ' + id);
    }
    assert.deepStrictEqual(r.payload.alignable, ['shared']);
    assert.strictEqual(r.payload.alignable.length + r.payload.not_alignable.length, seen.size);
    assert.strictEqual(r.payload.summary.alignable_count, 1);
    assert.strictEqual(r.payload.summary.not_alignable_count, 4);
  });

  await check('8 roundtrip — artifact lands at <case>/studio/tuning/<pair>/recheck.json', async () => {
    const caseDir = path.join(tmpRoot, 'case_test');
    fs.mkdirSync(caseDir, { recursive: true });
    const r = build([m('shared', 1)], [m('shared', 1.1)], [m('shared', 0.9)], 'FAST_STEREO_ONLY');
    const file = recheck.writeRecheck(caseDir, r.payload.pair_id, r.payload);
    assert.strictEqual(file, path.join(caseDir, 'studio', 'tuning', r.payload.pair_id, 'recheck.json'));
    const back = recheck.readRecheck(caseDir, r.payload.pair_id);
    assert.strictEqual(back.schema, recheck.SCHEMA);
    assert.strictEqual(back.mode, 'FAST_STEREO_ONLY');
    assert.strictEqual(back.A.delta_vs_original.shared, 0.1);
    assert.strictEqual(back.B.delta_vs_original.shared, -0.1);
    assert.ok(/不补算/.test(back.note));
  });

  await check('9 empty measurement sets → empty-but-honest table, not a refusal', async () => {
    const r = build([], [], []);
    assert.strictEqual(r.ok, true, 'three readable reports is a valid (if empty) recheck');
    assert.deepStrictEqual(r.payload.alignable, []);
    assert.deepStrictEqual(r.payload.not_alignable, []);
    assert.strictEqual(r.payload.summary.alignable_count, 0);
  });

  // ── report ────────────────────────────────────────────────────────────────────
  console.log('');
  if (failures.length) {
    console.log('FAILED ' + failures.length + ' / ' + (passed + failures.length));
    for (const f of failures) console.log('  - ' + f);
    process.exitCode = 1;
  } else {
    console.log('recheck: ' + passed + ' passed');
  }
})();
