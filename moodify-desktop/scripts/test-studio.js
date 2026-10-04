#!/usr/bin/env node
/**
 * Headless test for the Studio v0.2 post-processing path.
 *
 * WHY THIS EXISTS
 *   The Electron window cannot be asserted on from CI, so the shell's *logic* is tested
 *   here without Electron: the backend contract, the version layer, and the real
 *   Core processing path, driven exactly the way main.js drives them.
 *
 *   The static counterpart is scripts/check-contracts.js, which proves the renderer only
 *   touches DOM ids and bridges that exist. Together they cover "the wiring is sound and
 *   the chain actually runs"; neither can prove the window looks right — that stays a
 *   human check.
 *
 * WHAT IT ACTUALLY RUNS
 *   Real audio through the real CLI:
 *     validate -> process -> output.wav + evidence.json -> version list -> selection
 *   Nothing is mocked. If Core is not importable, the test SKIPS (exit 0) rather than
 *   failing, so a checkout without the Python environment is not reported as broken.
 *
 * Run: node scripts/test-studio.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn } = require('child_process');

const ROOT = path.join(__dirname, '..');
const REPO_ROOT = path.join(ROOT, '..');
const studio = require(path.join(ROOT, 'src', 'studio'));
const { getBackend, describeBackends } = require(path.join(ROOT, 'src', 'backends'));

// On POSIX the interpreter is normally `python3`; Windows ships `python`.
// MOODIFY_PYTHON still wins on every platform. Defaulting to `python` meant the
// harness died with ENOENT on a stock Linux box before any test could run.
const PYTHON = process.env.MOODIFY_PYTHON
  || (process.platform === 'win32' ? 'python' : 'python3');
const pythonEnv = () => ({ ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' });

const runPython = (args, timeoutMs = 10 * 60 * 1000) => new Promise((resolve, reject) => {
  const child = spawn(PYTHON, args, { env: pythonEnv() });
  let stdout = '';
  let stderr = '';
  const timer = setTimeout(() => child.kill(), timeoutMs);
  child.stdout.on('data', (d) => { stdout += d.toString('utf8'); });
  child.stderr.on('data', (d) => { stderr += d.toString('utf8'); });
  child.on('error', (err) => { clearTimeout(timer); reject(err); });
  child.on('close', (code) => { clearTimeout(timer); resolve({ code, stdout, stderr }); });
});

const lastJsonLine = (text) => {
  for (const line of String(text).trimEnd().split('\n').reverse()) {
    const s = line.trim();
    if (!s) continue;
    try { return JSON.parse(s); } catch { /* keep scanning */ }
  }
  return null;
};

const deps = { runPython, lastJsonLine };

let passed = 0;
const failures = [];
/**
 * NOTE: this MUST stay async and every call site MUST await it.
 *
 * An earlier version of this file used a synchronous helper while several checks were
 * `async` callbacks. The helper did not await them, so it printed "ok" and counted a pass
 * before the assertion had run — and the rejection surfaced later as an unhandled crash.
 * Four checks, including the overwrite guard, were silently reporting false passes.
 * Harness bugs like this are worse than a failing test: they manufacture confidence.
 */
async function check(label, fn) {
  try { await fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

function findSourceAudio() {
  const candidates = [
    path.join(REPO_ROOT, 'moodify-core-package', 'tests', 'baseline', 'test_audio', 'piano.wav'),
    path.join(REPO_ROOT, 'moodify-core-package', 'tests', 'baseline', 'test_audio', 'electronic.wav'),
  ];
  return candidates.find((p) => fs.existsSync(p)) || null;
}

(async () => {
  console.log('Studio v0.2 headless test\n');

  // ——— checks that need no Python ———

  console.log('backend contract');
  const described = describeBackends();
  await check('registry advertises local and cloud', () => {
    const modes = described.map((d) => d.mode).sort();
    assert.deepStrictEqual(modes, ['cloud', 'local']);
  });
  await check('cloud is marked not implemented', () => {
    const cloud = described.find((d) => d.mode === 'cloud');
    assert.strictEqual(cloud.implemented, false);
  });
  await check('unknown backend mode throws', () => {
    assert.throws(() => getBackend('nope'));
  });
  await check('cloud refuses instead of silently falling back to local', async () => {
    const cloud = getBackend('cloud');
    const r = await cloud.process({}, deps);
    assert.strictEqual(r.ok, false);
    assert.ok(/未实现/.test(r.reason), 'reason should say not implemented');
  });

  console.log('\nversion layer');
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-studio-test-'));
  const caseDir = path.join(tmp, 'case_0001');
  fs.mkdirSync(caseDir, { recursive: true });
  await check('attempt ids are unique', () => {
    const a = studio.newAttemptId();
    const b = studio.newAttemptId();
    assert.notStrictEqual(a, b);
    assert.ok(a.startsWith('ai_'));
  });
  await check('attempt ids sort chronologically', () => {
    const early = studio.newAttemptId(new Date('2026-01-01T00:00:00Z'));
    const late = studio.newAttemptId(new Date('2026-06-01T00:00:00Z'));
    assert.ok(early < late, `${early} should sort before ${late}`);
  });
  await check('empty case lists no versions', () => {
    assert.deepStrictEqual(studio.listVersions(caseDir, null), []);
  });
  await check('no target is offered that has no preset behind it', () => {
    const local = getBackend('local');
    // The product spec lists streaming_ready; Core has no such preset. It must be
    // surfaced as planned/disabled, never mapped onto an unrelated preset.
    assert.ok(!local.TARGETS.includes('streaming_ready'));
    assert.ok(studio.PLANNED_TARGETS.some((p) => p.id === 'streaming_ready'));
  });

  // ——— checks that need the real Core ———

  console.log('\nreal Core chain (validate -> process -> evidence)');
  const source = findSourceAudio();
  let ready = Boolean(source);
  if (ready) {
    const probe = await runPython(['-c', 'import moodify']);
    if (probe.code !== 0) ready = false;
  }
  if (!ready) {
    console.log('  SKIP  Core or test audio unavailable — headless chain not run');
    console.log('        (this is a skip, not a pass: the chain is unverified here)');
  } else {
    fs.writeFileSync(path.join(caseDir, 'case.json'), JSON.stringify({ case_id: 'case_0001' }));
    fs.writeFileSync(path.join(caseDir, 'source_path.json'), JSON.stringify({ path: source }));

    studio.ensureDirs(caseDir);
    const attemptId = studio.newAttemptId();
    const versionDir = studio.createAttemptDir(caseDir, attemptId);

    const local = getBackend('local');
    const r = await local.process(
      { sourcePath: source, target: 'clean_master', versionDir, attemptId }, deps);

    await check('process succeeds on real audio', () => assert.strictEqual(r.ok, true, r.reason));
    if (r.ok) {
      await check('output audio exists', () => assert.ok(fs.existsSync(r.output)));
      await check('evidence file written', () => assert.ok(fs.existsSync(r.evidencePath)));
      await check('status is processed_review_required', () =>
        assert.strictEqual(r.evidence.status, 'processed_review_required'));
      await check('review_required is true (generation != completion)', () =>
        assert.strictEqual(r.evidence.review_required, true));
      await check('evidence carries both hashes', () => {
        assert.match(r.evidence.source_sha256, /^[0-9a-f]{64}$/);
        assert.match(r.evidence.output_sha256, /^[0-9a-f]{64}$/);
      });
      await check('evidence carries the parameters actually applied', () =>
        assert.strictEqual(Object.keys(r.evidence.core_parameters).length, 15));
      await check('evidence records backend kind and target', () => {
        assert.strictEqual(r.evidence.backend, 'local');
        assert.strictEqual(r.evidence.target, 'clean_master');
      });

      await check('a re-run with the same attempt dir cannot overwrite', async () => {
        const again = await local.process(
          { sourcePath: source, target: 'clean_master', versionDir, attemptId }, deps);
        assert.strictEqual(again.ok, false);
        assert.ok(/overwrite/.test(again.reason), 'expected the overwrite guard');
      });

      await check('version list shows original + the AI attempt', () => {
        const versions = studio.listVersions(caseDir, source);
        assert.strictEqual(versions.length, 2);
        assert.strictEqual(versions[0].kind, 'original');
        assert.strictEqual(versions[1].id, attemptId);
        assert.strictEqual(versions[1].target, 'clean_master');
        assert.ok(versions[1].audioPath, 'AI version must be playable');
      });

      await check('selection round-trips', () => {
        studio.writeSelection(caseDir, { versionId: attemptId, note: 'test' });
        const sel = studio.readSelection(caseDir);
        assert.strictEqual(sel.version_id, attemptId);
      });

      await check('a second attempt does not disturb the first', async () => {
        const id2 = studio.newAttemptId();
        const dir2 = studio.createAttemptDir(caseDir, id2);
        const r2 = await local.process(
          { sourcePath: source, target: 'warm_vocal', versionDir: dir2, attemptId: id2 }, deps);
        assert.strictEqual(r2.ok, true, r2.reason);
        const versions = studio.listVersions(caseDir, source);
        // original + two attempts: "try again" adds a version, never replaces one
        assert.strictEqual(versions.length, 3);
      });

      await check('unknown target is rejected before any work', async () => {
        const bad = await local.process(
          { sourcePath: source, target: 'streaming_ready', versionDir: path.join(tmp, 'x'), attemptId: 'x' },
          deps);
        assert.strictEqual(bad.ok, false);
        assert.ok(/未知目标/.test(bad.reason));
      });
    }
  }

  try { fs.rmSync(tmp, { recursive: true, force: true }); } catch { /* best effort */ }

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
