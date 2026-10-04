#!/usr/bin/env node
/**
 * Parity between the shell's gate authority and its one mirror.
 *
 * WHY THIS EXISTS
 *   The gate rule lives in two places:
 *
 *     src/pipeline.js            gates()                    ← authority
 *     renderer/app.js  stageLockReason() / stageUnlocked()  ← "Mirrors src/pipeline.js gates()"
 *
 *   The mirror says so in its own docstring. test-pipeline.js pins the authority
 *   thoroughly (33 checks) but never looks at the mirror, so a rule change in
 *   pipeline.js would leave the renderer's copy silently wrong — and the renderer
 *   copy is the one a human actually reads when a stage refuses to open.
 *
 *   That matters now specifically: the realignment migrates the shell onto Core
 *   and deletes this mirror. Freezing the two together first is what makes the
 *   deletion safe rather than hopeful.
 *
 * HOW IT CHECKS
 *   Behaviourally, not by string match. The prerequisites pipeline.js actually
 *   enforces are found by building a fully deep-ready case and removing one fact
 *   at a time, recording which removals flip canPlan to false. That set is then
 *   compared against the fact names the renderer's lock reason names.
 *
 *   A string comparison would pass if both texts drifted together. This does not.
 *
 * Run: node scripts/test-pipeline-parity.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');

const ROOT = path.join(__dirname, '..');
const pipeline = require(path.join(ROOT, 'src', 'pipeline'));
const RENDERER = path.join(ROOT, 'renderer', 'app.js');

let passed = 0;
const failures = [];

function check(label, fn) {
  try { fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-parity-test-'));
let seq = 0;

/** A case that satisfies every deep prerequisite: analyzed + diagnosed + separated + structured. */
function deepCase() {
  const dir = path.join(tmpRoot, `case_${String(++seq).padStart(4, '0')}`);
  fs.mkdirSync(path.join(dir, 'studio'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'case.json'), JSON.stringify({ case_id: 'case_test' }));
  fs.writeFileSync(path.join(dir, 'report.json'), JSON.stringify({
    protocol: 'moodify.sound/0.2',
    findings: [],
    measurements: [],
    technical_state: { overall: 'PARTIAL', workflow_dec_noop: true },
  }));
  fs.writeFileSync(path.join(dir, 'measurements.json'), '[]');
  fs.writeFileSync(path.join(dir, 'evidence.json'), '[]');
  pipeline.writeDiagnosis(dir, pipeline.buildDiagnosis(dir));
  fs.mkdirSync(path.join(dir, 'stems'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'stems', 'song__vocals.wav'), 'RIFF');
  fs.mkdirSync(path.join(dir, 'midi'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'midi', 'song_basic_pitch.mid'), 'MThd');
  return dir;
}

/** The artifact whose removal makes each fact false. */
const FACT_ARTIFACT = {
  analyzed: 'report.json',
  diagnosed: path.join('studio', 'diagnosis.json'),
  separated: 'stems',
  structured: 'midi',
  planned: path.join('studio', 'plans'),
};

function planUnlocked(dir) {
  return pipeline.gates(pipeline.inspect(dir)).canPlan === true;
}

// ── the authority's actual prerequisites, measured ────────────────────────────

function authorityPlanPrerequisites() {
  const blocking = [];
  for (const [fact, rel] of Object.entries(FACT_ARTIFACT)) {
    const dir = deepCase();
    assert.strictEqual(planUnlocked(dir), true, 'fixture must start deep-ready');
    fs.rmSync(path.join(dir, rel), { recursive: true, force: true });
    if (!planUnlocked(dir)) blocking.push(fact);
  }
  return blocking.sort();
}

// ── the mirror's declared prerequisites, read from source ─────────────────────

function rendererSource() {
  assert.ok(fs.existsSync(RENDERER), `renderer not found at ${RENDERER}`);
  return fs.readFileSync(RENDERER, 'utf8');
}

function rendererFnBody(src, name) {
  const start = src.indexOf(`function ${name}(`);
  assert.notStrictEqual(start, -1,
    `renderer no longer defines ${name}() — this parity test must be updated, ` +
    'not deleted: the mirror may have moved, and silently skipping would hide that');
  const rest = src.slice(start);
  const end = rest.indexOf('\n}');
  assert.notStrictEqual(end, -1, `could not find the end of ${name}()`);
  return rest.slice(0, end);
}

function rendererPlanPrerequisites(src) {
  const body = rendererFnBody(src, 'stageLockReason');
  const planCase = body.slice(body.indexOf("case 'plan'"), body.indexOf("case 'finish'"));
  assert.ok(planCase.length > 0, "stageLockReason() no longer has a 'plan' branch");
  return [...planCase.matchAll(/if \(!f\.(\w+)\)/g)].map((m) => m[1]).sort();
}

// ── the checks ────────────────────────────────────────────────────────────────

console.log('Studio gate parity (authority vs renderer mirror)\n');

try {
  const src = rendererSource();

  check('the renderer still consumes gates rather than deriving them', () => {
    // A browser script cannot read files, so it cannot re-derive state by accident.
    // If it ever gains fs/require, this mirror stops being a mirror.
    assert.ok(!/require\(/.test(src), 'renderer must not require() anything');
    assert.ok(!/\bfs\./.test(src), 'renderer must not touch the filesystem');
    assert.ok(/pipe\.snap/.test(src), 'renderer should render from the snapshot the shell derived');
  });

  check('⑤ prerequisites: renderer list == what pipeline.js actually enforces', () => {
    const authority = authorityPlanPrerequisites();
    const mirror = rendererPlanPrerequisites(src);
    assert.deepStrictEqual(mirror, authority,
      `renderer says ⑤ needs [${mirror}] but pipeline.js enforces [${authority}]`);
  });

  check('the authority really does gate planning on all four facts', () => {
    // Guards the test itself: if pipeline.js stopped needing decomposition, the
    // parity above could pass vacuously with both sides empty.
    const authority = authorityPlanPrerequisites();
    assert.deepStrictEqual(authority, ['analyzed', 'diagnosed', 'separated', 'structured']);
  });

  check('⑥ is not among the ⑤ prerequisites', () => {
    const authority = authorityPlanPrerequisites();
    assert.ok(!authority.includes('planned'),
      'a plan artifact must open ⑥, not be a prerequisite for writing a plan');
  });

  check('a persisted plan is what opens ⑥, on top of deep readiness', () => {
    const dir = deepCase();
    assert.strictEqual(pipeline.gates(pipeline.inspect(dir)).canFinish, false);
    assert.ok(pipeline.preparePlan(dir), 'preparePlan should succeed once deep-ready');
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.planned, true);
    assert.strictEqual(g.canFinish, true);
  });

  check('stageUnlocked maps ⑤ and ⑥ onto the authority fields, not onto copies', () => {
    const body = rendererFnBody(src, 'stageUnlocked');
    assert.ok(/case 'plan':\s*return gates\.canPlan;/.test(body),
      "⑤ must map to gates.canPlan");
    assert.ok(/case 'finish':\s*return gates\.canFinish \|\| gates\.canFinishQuick;/.test(body),
      '⑥ must map to gates.canFinish || gates.canFinishQuick');
  });

  check('the quick route cannot reach ⑤ in either implementation', () => {
    const dir = deepCase();
    fs.rmSync(path.join(dir, 'stems'), { recursive: true, force: true });
    fs.rmSync(path.join(dir, 'midi'), { recursive: true, force: true });
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY');
    const g = pipeline.gates(pipeline.inspect(dir));
    assert.strictEqual(g.canFinishQuick, true, 'quick finish is open');
    assert.strictEqual(g.canPlan, false, 'but ⑤ stays shut — the mirror relies on this too');
  });

  check('mode labels are the two canonical strings', () => {
    const deep = deepCase();
    assert.strictEqual(pipeline.gates(pipeline.inspect(deep)).modeLabel, '深度完成');
    const quick = deepCase();
    fs.rmSync(path.join(quick, 'stems'), { recursive: true, force: true });
    fs.rmSync(path.join(quick, 'midi'), { recursive: true, force: true });
    pipeline.recordFinishMode(quick, 'QUICK_STEREO_ONLY');
    assert.strictEqual(pipeline.gates(pipeline.inspect(quick)).modeLabel, '快速（仅立体声）');
  });
} catch (err) {
  failures.push('harness: ' + err.message);
  console.log('  FAIL harness — ' + err.message);
}

try { fs.rmSync(tmpRoot, { recursive: true, force: true }); } catch { /* best effort */ }

console.log(`\n${passed} passed, ${failures.length} failed`);
if (failures.length) {
  console.log('\nFailures:');
  for (const f of failures) console.log('  - ' + f);
  process.exit(1);
}
