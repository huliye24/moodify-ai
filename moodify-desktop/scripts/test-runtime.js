#!/usr/bin/env node
/**
 * Headless test for external-runtime resolution (HOTFIX 000 / F4).
 *
 * WHY THIS EXISTS
 *   The shell's separation / MIDI / score capabilities need a dedicated
 *   external venv. The old resolver silently fell back to system `python`
 *   when that venv was missing:
 *
 *       return fs.existsSync(exe) ? exe : PYTHON;   // removed
 *
 *   System python cannot run that chain (librosa -> sklearn -> pandas ABI),
 *   so the user got a deep numpy/pandas traceback instead of "dependency
 *   missing". These tests pin the corrected contract: a dedicated runtime
 *   resolves, a missing one fails explicitly, and nothing ever quietly
 *   substitutes an arbitrary interpreter.
 *
 * Run: node scripts/test-runtime.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const rt = require(path.join(__dirname, '..', 'src', 'runtime'));

let failures = 0;
const created = [];

function check(name, fn) {
  try {
    fn();
    console.log(`  ok    ${name}`);
  } catch (err) {
    failures += 1;
    console.error(`  FAIL  ${name}`);
    console.error(`        ${err.message}`);
  }
}

function tempVenv({ python = false, tool = false } = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-runtime-'));
  created.push(dir);
  if (python || tool) fs.mkdirSync(path.join(dir, 'Scripts'), { recursive: true });
  if (python) fs.writeFileSync(path.join(dir, 'Scripts', 'python.exe'), '');
  if (tool) fs.writeFileSync(path.join(dir, 'Scripts', 'basic-pitch.exe'), '');
  return dir;
}

console.log('moodify-desktop runtime resolver (HOTFIX 000 / F4)');

// --- A. dedicated runtime present -----------------------------------------
check('A. dedicated runtime present resolves to that interpreter', () => {
  const dir = tempVenv({ python: true });
  const resolved = rt.resolveRuntime('basic-pitch', { candidates: [dir] });
  assert.strictEqual(resolved.python, path.join(dir, 'Scripts', 'python.exe'));
  assert.strictEqual(resolved.dir, dir);
});

check('A. dedicated runtime present resolves a declared tool', () => {
  const dir = tempVenv({ python: true, tool: true });
  const exe = rt.resolveRuntimeTool('basic-pitch', 'basic-pitch', { candidates: [dir] });
  assert.strictEqual(exe, path.join(dir, 'Scripts', 'basic-pitch.exe'));
});

// --- B. dedicated runtime absent ------------------------------------------
check('B. missing runtime fails instead of falling back', () => {
  const empty = tempVenv();
  assert.throws(() => rt.resolveRuntime('basic-pitch', { candidates: [empty] }),
    (err) => err instanceof rt.RuntimeMissingError);
});

check('B. missing runtime never returns a system interpreter', () => {
  const empty = tempVenv();
  let returned = null;
  try {
    returned = rt.resolveRuntime('basic-pitch', { candidates: [empty] });
  } catch {
    returned = null;
  }
  assert.strictEqual(returned, null, 'resolver returned a path for a missing runtime');
  // the failure result must not hand back any interpreter to spawn
  const result = rt.tryResolve(() => rt.resolveRuntime('basic-pitch', { candidates: [empty] }));
  assert.strictEqual(result.ok, false);
  assert.ok(!('exe' in result), 'failure result must not carry an executable');
  // candidates are search *directories*; none of them is a runnable interpreter
  for (const candidate of result.candidates || []) {
    assert.ok(!/python(\.exe)?$/i.test(candidate), `failure names an interpreter: ${candidate}`);
  }
});

// --- C. error identity ----------------------------------------------------
check('C. failure carries DEPENDENCY_MISSING', () => {
  const empty = tempVenv();
  try {
    rt.resolveRuntime('score', { candidates: [empty] });
    assert.fail('expected RuntimeMissingError');
  } catch (err) {
    assert.strictEqual(err.code, rt.CODE_DEPENDENCY_MISSING);
    assert.strictEqual(err.code, 'DEPENDENCY_MISSING');
    assert.strictEqual(err.runtime, 'score');
  }
});

check('C. IPC result shape is machine-readable', () => {
  const empty = tempVenv();
  const result = rt.tryResolve(() => rt.resolveRuntime('score', { candidates: [empty] }));
  assert.deepStrictEqual(
    { ok: result.ok, code: result.code, runtime: result.runtime },
    { ok: false, code: 'DEPENDENCY_MISSING', runtime: 'score' }
  );
  assert.ok(typeof result.reason === 'string' && result.reason.length > 0);
});

check('C. a present runtime but missing tool still identifies the runtime', () => {
  const dir = tempVenv({ python: true });  // python present, basic-pitch.exe absent
  try {
    rt.resolveRuntimeTool('basic-pitch', 'basic-pitch', { candidates: [dir] });
    assert.fail('expected RuntimeMissingError');
  } catch (err) {
    assert.strictEqual(err.code, 'DEPENDENCY_MISSING');
    assert.strictEqual(err.runtime, 'basic-pitch');
  }
});

// --- D. no accidental spawn ------------------------------------------------
check('D. resolution failure produces no executable to spawn', () => {
  const empty = tempVenv();
  const result = rt.tryResolve(() => rt.resolveRuntime('basic-pitch', { candidates: [empty] }));
  // main.js returns early on !result.ok, so runLong() is never reached.
  assert.strictEqual(result.ok, false);
  assert.strictEqual(result.exe, undefined);
});

check('D. resolution failure does not throw past the guard', () => {
  const empty = tempVenv();
  assert.doesNotThrow(() => rt.tryResolve(() => rt.resolveRuntime('basic-pitch', { candidates: [empty] })));
});

// --- contract details ------------------------------------------------------
check('unknown runtime name is a programming error, not a missing dependency', () => {
  assert.throws(() => rt.resolveRuntime('not-a-runtime'), (err) =>
    !(err instanceof rt.RuntimeMissingError) && /unknown Moodify runtime/.test(err.message));
  assert.strictEqual(rt.isKnownRuntime('basic-pitch'), true);
  assert.strictEqual(rt.isKnownRuntime('nope'), false);
});

check('candidates honour an explicit env override before the packaged path', () => {
  const dir = tempVenv({ python: true });
  const key = rt.RUNTIMES['basic-pitch'].envVar;
  const previous = process.env[key];
  process.env[key] = dir;
  try {
    const candidates = rt.runtimeCandidates('basic-pitch');
    assert.strictEqual(candidates[0], path.resolve(dir));
    assert.strictEqual(rt.resolveRuntime('basic-pitch').dir, dir);
  } finally {
    if (previous === undefined) delete process.env[key];
    else process.env[key] = previous;
  }
});

check('every declared runtime names an env override and a python entry point', () => {
  for (const [name, spec] of Object.entries(rt.RUNTIMES)) {
    assert.ok(spec.envVar, `${name} missing envVar`);
    assert.ok(spec.python, `${name} missing python entry`);
    assert.ok(spec.dir, `${name} missing default dir`);
    assert.ok(spec.label, `${name} missing label`);
  }
});

for (const dir of created) {
  try { fs.rmSync(dir, { recursive: true, force: true }); } catch { /* best effort */ }
}

if (failures > 0) {
  console.error(`\n${failures} runtime check(s) failed`);
  process.exit(1);
}
console.log('\nall runtime checks passed');
