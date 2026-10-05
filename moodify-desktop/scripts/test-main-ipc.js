#!/usr/bin/env node
/**
 * 主进程集成测试 — 真实的 main.js IPC 处理器（不是它的复制品）
 *
 * 这个文件用一个 stub 的 `electron` 把 `src/main.js` 原样加载进来，拿到它注册的
 * `ipcMain.handle` 处理器，然后用真实的临时 case 目录逐个调用。于是被测的是**真正的接线**：
 * 守卫（resolveGuardedCase）、真实步骤函数、编排器、账本校验、导出拒绝，一个都不少。
 *
 * 为什么不能用「再写一个等价的假 main」
 *   三处 P1 里有两处正是**接线层**的错误（调用旧 case、丢掉失败原因），另一处是账本校验。
 *   把它们在测试里重新实现一遍，就是测我自己写的副本，而不是产品里跑的那段代码。
 *
 * 覆盖
 *   1 会话 IPC 面存在，且加载的是 stub 的 electron（没有真窗口）
 *   2 没有 report.json 的世界：`session:start` 拒绝，**不会**在 cases-root 里造出第二个 case，
 *     并且失败原因在重新投影后仍然可见（P1：反复造 case + 最终只报 NO_PROGRESS）
 *   3 真实步骤失败（缺 source_path.json → 分轨无法开始）：原因是真实的那一句，
 *     `session:view` 之后仍然可见；人补上产物后记录自动过期（P1：失败原因消失、UI 回到 READY）
 *   4 并发启动被拒（ALREADY_RUNNING），不是静默交错写产物
 *   5 账本：不存在 / 不完整 / 复检缺失或不属于本对的 pair 全部写不进去；「保留原版」不能
 *     绕过 A/B；手写的一条假记录也**不能**让 ⑧导出 交出原版（P1：虚假 pair 写入选择 → DONE → 导出）
 *   6 Core 未就绪的修音渲染显式拒绝，且不产任何文件
 *   7 tuning:pairs 把 ⑦ 的真实准入告诉 UI（按钮不会比校验更宽松）
 *
 * Run: node scripts/test-main-ipc.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');
const Module = require('module');
const { spawnSync } = require('child_process');

const sha256file = (file) =>
  require('crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex');

// ── stub electron ───────────────────────────────────────────────────────────────

const handlers = new Map();
const dialogs = { open: [], save: [], lastOptions: null, nextSavePath: null };

const electronStub = {
  app: {
    // main.js: app.whenReady().then(() => { registerIpc(); createWindow(); ... })
    whenReady: () => ({ then: (fn) => { fn(); return { catch: () => {} }; } }),
    on: () => {},
    quit: () => {},
    getPath: (name) => path.join(os.tmpdir(), name),
  },
  ipcMain: {
    handle: (channel, fn) => handlers.set(channel, fn),
    on: (channel, fn) => handlers.set(channel, fn),
  },
  BrowserWindow: class BrowserWindow {
    constructor() {
      this.webContents = { send: () => {} };
      this.destroyed = false;
    }
    loadFile() {}
    on() {}
    isDestroyed() { return this.destroyed; }
    static getAllWindows() { return []; }
    static fromWebContents() { return null; }
  },
  dialog: {
    showOpenDialog: async () => { dialogs.open.push(1); return { canceled: true, filePaths: [] }; },
    showSaveDialog: async (_win, options) => {
      dialogs.save.push(1);
      dialogs.lastOptions = options || {};
      // 测试可以指定下一次保存路径；没指定就当作「用户取消」
      if (dialogs.nextSavePath) return { canceled: false, filePath: dialogs.nextSavePath };
      return { canceled: true, filePath: null };
    },
  },
};

const CASES_ROOT = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-main-ipc-'));
process.env.MOODIFY_CASES_ROOT = CASES_ROOT;
process.env.MOODIFY_CODEX_HOME = path.join(CASES_ROOT, 'codex-home');

const originalLoad = Module._load;
Module._load = function load(request, parent, isMain) {
  if (request === 'electron') return electronStub;
  return originalLoad.call(this, request, parent, isMain);
};

const MAIN = path.join(__dirname, '..', 'src', 'main.js');
require(MAIN);

// ── test harness ────────────────────────────────────────────────────────────────

let passed = 0;
const failures = [];
async function check(label, fn) {
  try { await fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

const call = (channel, ...args) => {
  const fn = handlers.get(channel);
  if (!fn) throw new Error(`no handler registered for ${channel}`);
  return fn({ sender: {} }, ...args);
};

let caseSeq = 0;
function newCaseDir(opts = {}) {
  const dir = path.join(CASES_ROOT, `case_${String(++caseSeq).padStart(4, '0')}`);
  fs.mkdirSync(path.join(dir, 'studio'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'case.json'), JSON.stringify({ case_id: 'case_test', source_id: 'sha256:' + 'a'.repeat(64) }));
  if (opts.report !== false) {
    fs.writeFileSync(path.join(dir, 'report.json'), JSON.stringify({
      report_schema_version: 'moodify.msp_report/0.2',
      case: { case_id: 'case_test' },
      source: { name: 'song.wav' },
      measurements: [],
      findings: [],
      technical_state: { overall: 'OK', workflow_decision: 'NO_TECHNICAL_BLOCKERS', reasons: [] },
    }));
    fs.writeFileSync(path.join(dir, 'measurements.json'), '[]');
  }
  if (opts.source) {
    const wav = path.join(dir, 'song.wav');
    fs.writeFileSync(wav, 'RIFF');
    fs.writeFileSync(path.join(dir, 'source_path.json'), JSON.stringify({ path: wav }));
  }
  if (opts.stems) {
    fs.mkdirSync(path.join(dir, 'stems'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'stems', 'song__vocals.wav'), 'RIFF');
  }
  if (opts.midi) {
    fs.mkdirSync(path.join(dir, 'midi'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'midi', 'song.mid'), 'MThd');
  }
  if (opts.roundtrip) {
    fs.writeFileSync(path.join(dir, 'studio', 'roundtrip.json'),
      JSON.stringify({ schema: 'moodify.studio.roundtrip/0.1', passed: true }));
  }
  return dir;
}

const listCases = () => fs.readdirSync(CASES_ROOT).filter((n) => n.startsWith('case_')).sort();

/**
 * A pair that ⑦ would accept: both mixes + a recheck.json that names THIS pair and three
 * report.json files that really exist. Anything less is not a complete pair (see §5).
 */
function addCompletePair(dir, { tuned = true, composed = true, recheck = true } = {}) {
  const id = `tune_20261004120000_${String(++caseSeq).padStart(3, '0')}`;
  const pairDir = path.join(dir, 'studio', 'tuning', id);
  fs.mkdirSync(pairDir, { recursive: true });
  fs.writeFileSync(path.join(pairDir, 'pair.json'),
    JSON.stringify({ schema: 'moodify.core.tuning-pair/0.1', pair_id: id, mode: 'DEEP' }));
  const reports = { original: path.join(dir, 'report.json') };
  for (const side of ['A', 'B']) {
    const sdir = path.join(pairDir, side);
    fs.mkdirSync(sdir, { recursive: true });
    if (tuned) {
      fs.mkdirSync(path.join(sdir, 'tuned'), { recursive: true });
      fs.writeFileSync(path.join(sdir, 'tuned', 'vocals.wav'), 'RIFF');
    }
    if (composed) fs.writeFileSync(path.join(sdir, 'mix.wav'), 'RIFF');
    reports[side] = path.join(sdir, 'report.json');
    fs.writeFileSync(reports[side], JSON.stringify({ measurements: [], case: { case_id: 'case_test' } }));
  }
  if (recheck) {
    fs.writeFileSync(path.join(pairDir, 'recheck.json'), JSON.stringify({
      schema: 'moodify.studio.recheck/0.1',
      pair_id: id,
      original: { report: reports.original },
      A: { report: reports.A },
      B: { report: reports.B },
      alignable: ['integrated_lufs'],
      summary: { alignable_count: 1, not_alignable_count: 0, A_changed_metrics: 0, B_changed_metrics: 0 },
    }));
  }
  return id;
}

(async () => {
  console.log('main-process IPC integration (Phase 1)\n');

  // ── 1. the wiring itself ──────────────────────────────────────────────────────
  console.log('1. the real main.js is loaded and its handlers are reachable');
  await check('会话 / 修音 / 流程 的 IPC 面都注册了', () => {
    for (const ch of ['session:start', 'session:view', 'tuning:pairs', 'tuning:render',
      'tuning:decision', 'tuning:export', 'tuning:recheckRun', 'pipeline:snapshot']) {
      assert.ok(handlers.has(ch), `${ch} must be handled by main.js`);
    }
  });
  await check('守卫仍然生效：不在 CASES_ROOT 内的目录、或不是 case 的目录都被拒绝', async () => {
    const outside = await call('session:start', os.tmpdir());
    assert.strictEqual(outside.ok, false);
    assert.strictEqual(outside.reason, 'INVALID_CASE_DIR');
    const notACase = path.join(CASES_ROOT, 'not_a_case');
    fs.mkdirSync(notACase, { recursive: true });
    const res = await call('session:start', notACase);
    assert.strictEqual(res.reason, 'INVALID_CASE_DIR');
  });

  // ── 2. P1: a world without report.json ────────────────────────────────────────
  console.log('\n2. P1 — a case without report.json: refuse, do not build duplicate cases');
  await check('session:start 如实拒绝「就地补检测」，并且不新建任何 case', async () => {
    const dir = newCaseDir({ report: false, source: true });
    const before = listCases();
    const view = (await call('session:view', dir)).view;
    assert.strictEqual(view.state, 'READY');
    assert.strictEqual(view.nextPhase, 'detect');

    // 连按三次：一次显式启动 + 两次重复启动，都不许造出第二个 case
    const first = await call('session:start', dir);
    assert.strictEqual(first.ok, false);
    assert.strictEqual(first.reason, 'PHASE_FAILED');
    assert.strictEqual(first.phase, 'detect');
    assert.strictEqual(first.blocker.kind, 'STEP_FAILED');
    assert.strictEqual(first.blocker.reason, 'CASE_WITHOUT_REPORT');
    assert.match(first.blocker.detail, /重新导入/);
    await call('session:start', dir);
    await call('session:start', dir);
    assert.deepStrictEqual(listCases(), before, 'no duplicate case may be created');
    assert.strictEqual(fs.existsSync(path.join(dir, 'report.json')), false, 'and no fake report');
  });
  await check('失败原因在**重新投影**后仍然可见（UI 不会退回「什么也没发生」）', async () => {
    const dir = newCaseDir({ report: false, source: true });
    await call('session:start', dir);
    const view = (await call('session:view', dir)).view;
    assert.strictEqual(view.state, 'BLOCKED');
    assert.strictEqual(view.blocker.kind, 'STEP_FAILED');
    assert.strictEqual(view.blocker.reason, 'CASE_WITHOUT_REPORT');
    assert.match(view.message, /没有生成任何候选版本/);
    // 而且这条记录不推进任何阶段：产物推导仍然是 IMPORTED
    assert.strictEqual(view.stage, 'IMPORTED');
    const snap = await call('pipeline:snapshot', dir);
    assert.strictEqual(snap.stage, 'IMPORTED');
  });

  // ── 3. P1: a real step failure stays visible ──────────────────────────────────
  console.log('\n3. P1 — a real step failure is visible and survives re-projection');
  await check('缺 source_path.json → 分轨真实失败，原因原样进入 BLOCKED', async () => {
    const dir = newCaseDir({ report: true }); // analysed, but the case does not know its source
    const res = await call('session:start', dir);
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'PHASE_FAILED');
    assert.strictEqual(res.phase, 'decompose');
    assert.match(res.detail, /未找到源音频/);

    const view = (await call('session:view', dir)).view;
    assert.strictEqual(view.state, 'BLOCKED');
    assert.strictEqual(view.blocker.phase, 'decompose');
    assert.match(view.blocker.detail, /未找到源音频/);
    assert.ok(fs.existsSync(path.join(dir, 'studio', 'session_failure.json')));
    // 没有候选、没有音频被编排器写出来
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'tuning')), false);
  });
  await check('产物补上之后，投影立刻回到真实状态（记录不是权威）', async () => {
    const dir = newCaseDir({ report: true });
    await call('session:start', dir);
    assert.strictEqual((await call('session:view', dir)).view.state, 'BLOCKED');
    // 人手动做了逆向分解（高级层）
    fs.mkdirSync(path.join(dir, 'stems'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'stems', 'song__vocals.wav'), 'RIFF');
    const view = (await call('session:view', dir)).view;
    assert.notStrictEqual(view.state, 'BLOCKED');
    assert.strictEqual(view.nextPhase, 'structure');
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'session_failure.json')), false);
  });

  // ── 4. concurrency ────────────────────────────────────────────────────────────
  console.log('\n4. two concurrent starts for the same song');
  await check('第二次并发启动被拒绝（ALREADY_RUNNING），而不是交错写同一个目录', async () => {
    const dir = newCaseDir({ report: false, source: true });
    const first = call('session:start', dir);
    const second = await call('session:start', dir); // 同步进入 → 锁已被第一次持有
    assert.strictEqual(second.ok, false);
    assert.strictEqual(second.reason, 'ALREADY_RUNNING');
    assert.strictEqual(second.view.running, true);
    await first; // 第一次正常结束（本项目里是如实拒绝检测）
    const after = (await call('session:view', dir)).view;
    assert.strictEqual(after.running, false, 'the lock must be released');
  });

  // ── 5. P1: the ⑦ ledger cannot be written for a pair that is not complete ─────
  console.log('\n5. P1 — ⑦ 选定 only accepts a pair with two candidates and a real recheck');
  await check('不存在的 pair 写不进去，账本文件也不会出现', async () => {
    const dir = newCaseDir({ report: true });
    const res = await call('tuning:decision', dir, 'tune_ghost', 'A', 'creator', 'req1');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'PAIR_NOT_COMPLETE');
    assert.match(res.blockers[0], /修音对不存在/);
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'tuning', 'decisions.jsonl')), false);
    assert.strictEqual((await call('pipeline:snapshot', dir)).stage, 'ANALYZED');
  });
  await check('不完整的一对（只有修音 / 只有合成）都写不进去', async () => {
    const tunedOnly = newCaseDir({ report: true });
    const idA = addCompletePair(tunedOnly, { composed: false, recheck: false });
    const rA = await call('tuning:decision', tunedOnly, idA, 'A', 'creator', 'r1');
    assert.strictEqual(rA.ok, false);
    assert.strictEqual(rA.reason, 'PAIR_NOT_COMPLETE');

    const composedNoRecheck = newCaseDir({ report: true });
    const idB = addCompletePair(composedNoRecheck, { recheck: false });
    const rB = await call('tuning:decision', composedNoRecheck, idB, 'B', 'creator', 'r2');
    assert.strictEqual(rB.ok, false);
    assert.ok(rB.blockers.some((b) => /尚未复检/.test(b)));
    assert.strictEqual((await call('pipeline:snapshot', composedNoRecheck)).stage, 'COMPOSED');
  });
  await check('「保留原版」同样过这道门：不能绕过 A/B 直接交原版', async () => {
    const dir = newCaseDir({ report: true });
    const id = addCompletePair(dir, { composed: false, recheck: false });
    const res = await call('tuning:decision', dir, id, 'ORIGINAL', 'creator', 'r3');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'PAIR_NOT_COMPLETE');
    assert.strictEqual((await call('pipeline:snapshot', dir)).gates.canExport, false);
  });
  await check('手写的一条假记录也不能让 ⑧导出 交出原版（读侧同样按规则推导）', async () => {
    const dir = newCaseDir({ report: true, source: true });
    fs.mkdirSync(path.join(dir, 'studio', 'tuning'), { recursive: true });
    fs.appendFileSync(path.join(dir, 'studio', 'tuning', 'decisions.jsonl'),
      JSON.stringify({ schema: 'moodify.studio.tuning-decision/0.1', pair_id: 'tune_ghost', kept: 'ORIGINAL' }) + '\n');
    const snap = await call('pipeline:snapshot', dir);
    assert.strictEqual(snap.stage, 'ANALYZED', 'a ledger row is not a fact');
    assert.strictEqual(snap.gates.canExport, false);
    const savesBefore = dialogs.save.length;
    const res = await call('tuning:export', dir, 'tune_ghost', 'ORIGINAL');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'CANDIDATES_INCOMPLETE');
    assert.strictEqual(dialogs.save.length, savesBefore, 'no save dialog may even open');
  });
  await check('完整的一对（两档 + 真复检）可以选定，并把 ⑧ 打开', async () => {
    const dir = newCaseDir({ report: true });
    const id = addCompletePair(dir);
    const res = await call('tuning:decision', dir, id, 'A', 'creator', 'r4');
    assert.strictEqual(res.ok, true);
    assert.strictEqual(res.recorded, true);
    assert.strictEqual((await call('pipeline:snapshot', dir)).stage, 'CHOSEN');
    const pairs = await call('tuning:pairs', dir);
    assert.strictEqual(pairs.decidable, true, 'and the UI is told it is decidable');
    // 完整的一对过了 ⑦ 的门：从这里开始是 Core 的事——本机装没装 Core 不由这个测试决定。
    // 所以只断言「拒绝的理由不再是账本那两条」；Core 不可调用（连进程都起不来）也算通过这一关。
    let res2;
    try { res2 = await call('tuning:export', dir, id, 'A'); }
    catch (err) { res2 = { ok: false, reason: 'CORE_UNAVAILABLE', detail: String(err && err.message) }; }
    assert.notStrictEqual(res2.reason, 'NOT_CHOSEN');
    assert.notStrictEqual(res2.reason, 'CANDIDATES_INCOMPLETE');
  });
  await check('tuning:pairs 把 ⑦ 的真实准入告诉 UI（按钮不会比校验更宽松）', async () => {
    const dir = newCaseDir({ report: true });
    const id = addCompletePair(dir, { recheck: false });
    const pairs = await call('tuning:pairs', dir);
    assert.strictEqual(pairs.decidable, false);
    assert.ok(pairs.decisionBlockers[id].some((b) => /尚未复检/.test(b)));
    assert.deepStrictEqual(pairs.exits, ['A', 'B', 'ORIGINAL']);
  });

  // ── 6. the unimplemented Core ability is refused, not faked ───────────────────
  console.log('\n6. the unimplemented 修音/复合 is refused, and leaves nothing behind');
  await check('深度被声明可执行但未接线时：显式拒绝，且不产任何文件', async () => {
    // 2026-10-04 裁定后，canTune 还需要「逐轨能力可用」；今天它恒为 false。
    // 这里直接钉住那一层的语义：canTune 为真意味着深度路径应当能跑，
    // 而本壳尚未接那条线，所以必须拒绝而不是假装跑过。
    const dir = newCaseDir({ report: true, source: true, stems: true, midi: true, roundtrip: true });
    const gates = (await call('pipeline:snapshot', dir)).gates;
    assert.strictEqual(gates.reversible, true, '可逆性这一半是满足的');
    assert.strictEqual(gates.deepExecutable, false, '但逐轨能力仍未实现 → 深度不可执行');
    assert.strictEqual(gates.canTune, false, '所以深度 ④ 没有被解锁');
    const res = await call('tuning:render', dir);
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'DEEP_NOT_EXECUTABLE', '说的是真实处境，不是含糊的「未就绪」');
    assert.strictEqual(res.canSwitchToFast, true, '并给出由人确认的补救');
    assert.ok(res.deepBlockers.includes('DEEP_CORE_UNAVAILABLE'));
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'tuning')), false);
  });
  await check('闸门未开时 tuning:render 说的是真实缺什么（而不是能力未就绪）', async () => {
    const dir = newCaseDir({ report: true, source: true, stems: true }); // 缺 MIDI
    const res = await call('tuning:render', dir);
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'DEEP_NOT_EXECUTABLE');
    assert.ok(res.blockers.some((b) => /MIDI/.test(b)), '缺什么就说缺什么');
    assert.ok(res.canSwitchToFast, '并且给出由人确认的补救路径');
  });

  // ── 7. the first real vertical loop: Core pair → recheck → REVIEW → choice → export ──
  //
  // This is the Phase 2 claim, so it runs the **real Core** on real synthesised audio. If Core is
  // not importable, it SKIPS (like test-studio.js) rather than pretending the loop was verified.
  console.log('\n7. real Core: 一对真实候选 → 自动复检 → REVIEW → 人选定 → 导出');
  const coreReady = spawnSync(process.env.MOODIFY_PYTHON || 'python',
    ['-c', 'import moodify, soundfile, pedalboard'], { encoding: 'utf8' }).status === 0;

  const SONG_PY = [
    'import sys, numpy as np, soundfile as sf',
    'sr = 22050',
    't = np.arange(int(sr * 1.5)) / sr',
    'l = (0.30 * np.sin(2 * np.pi * 220.0 * t)).astype(np.float32)',
    'r = (0.25 * np.sin(2 * np.pi * 330.0 * t) + 0.05 * np.sin(2 * np.pi * 1200.0 * t)).astype(np.float32)',
    'sf.write(sys.argv[1], np.column_stack([l, r]), sr, subtype="PCM_16")',
  ].join('\n');
  const PY = process.env.MOODIFY_PYTHON || 'python';
  const pyEnv = { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' };

  /**
   * A case created the way the product creates one: synthesise audio, then let Core analyse it
   * (`analysis:run` runs exactly this command) so the case's own report.json is a real one.
   * The original side of the three-way recheck then has real measurements, as it must.
   */
  function songCase() {
    const staging = path.join(CASES_ROOT, `staging_${String(++caseSeq).padStart(4, '0')}`);
    fs.mkdirSync(staging, { recursive: true });
    const wav = path.join(staging, 'song.wav');
    const made = spawnSync(PY, ['-c', SONG_PY, wav], { encoding: 'utf8', env: pyEnv });
    assert.strictEqual(made.status, 0, `could not synthesise the fixture: ${made.stderr}`);

    const run = spawnSync(PY, ['-m', 'moodify.release_cli', 'demo', wav,
      '--cases-root', CASES_ROOT, '--no-open'], { encoding: 'utf8', env: pyEnv });
    assert.strictEqual(run.status, 0, `could not analyse the fixture: ${run.stderr}`);
    const payload = JSON.parse(run.stdout.trim().split('\n').pop());
    const dir = path.dirname(payload.reports.json);
    fs.writeFileSync(path.join(dir, 'source_path.json'), JSON.stringify({ path: wav }));
    return dir;
  }

  const pairsIn = (dir) => {
    const tuningDir = path.join(dir, 'studio', 'tuning');
    if (!fs.existsSync(tuningDir)) return [];
    return fs.readdirSync(tuningDir).filter((n) => n.startsWith('tune_')).sort();
  };
  const attemptsIn = (dir) => {
    const tuningDir = path.join(dir, 'studio', 'tuning');
    if (!fs.existsSync(tuningDir)) return [];
    return fs.readdirSync(tuningDir).filter((n) => n.includes('.attempt')).sort();
  };

  if (!coreReady) {
    console.log('  SKIP  Core / soundfile / pedalboard 不可用 —— 纵向闭环未经真实音频验证');
    console.log('        (this is a skip, not a pass)');
  } else {

    await check('未显式选择快速完成时，一键启动**不会**走快速路径、也不会生成候选', async () => {
      const dir = songCase();
      const offered = await call('pipeline:snapshot', dir);
      assert.strictEqual(offered.gates.mode, null, 'not a mode at all before the choice');
      assert.strictEqual(offered.gates.canRequestQuick, true, 'the choice is offered');
      assert.strictEqual(offered.gates.canTuneQuick, false, 'and it is not active by default');

      const res = await call('session:start', dir);
      assert.deepStrictEqual(pairsIn(dir), [], 'no pair may appear without the human choice');
      const view = (await call('session:view', dir)).view;
      assert.strictEqual(view.fast, false, 'the deep chain is what ran');
      assert.strictEqual(view.phases.some((p) => p.status === 'skipped'), false,
        'nothing may be skipped as if the fast route had been chosen');
      assert.strictEqual(res.ok, false, 'and it stops on the deep path’s real blocker');
    });

    await check('显式选择快速完成后：一次「开始完成」真的调 Core，产出一对完整候选', async () => {
      const dir = songCase();
      const chosen = await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      assert.strictEqual(chosen.ok, true);
      assert.strictEqual(chosen.gates.mode, 'FAST_STEREO_ONLY');
      assert.strictEqual(chosen.gates.modeLabel, '快速（仅立体声）');

      const view = (await call('session:view', dir)).view;
      assert.strictEqual(view.nextPhase, 'tune', 'the pure-stereo route goes straight to the pair');

      const res = await call('session:start', dir);
      assert.strictEqual(res.ok, true, `session must complete: ${JSON.stringify(res.blocker || res.detail)}`);
      assert.strictEqual(res.state, 'REVIEW');

      const ids = pairsIn(dir);
      assert.strictEqual(ids.length, 1, 'exactly one render-pair call');
      const pairDir = path.join(dir, 'studio', 'tuning', ids[0]);
      for (const rel of ['pair.json', 'A/mix.wav', 'B/mix.wav', 'A/tuned/source.wav',
        'B/tuned/source.wav', 'A/plan.json', 'B/plan.json', 'A/evidence.json',
        'B/evidence.json', 'recheck.json']) {
        assert.ok(fs.existsSync(path.join(pairDir, rel)), `${rel} must exist`);
      }
      assert.deepStrictEqual(attemptsIn(dir), [], 'no temporary attempt may survive');
      assert.deepStrictEqual(
        fs.readdirSync(pairDir).sort(), ['A', 'B', 'pair.json', 'recheck.json'],
        'exactly the documented pair layout');
    });

    await check('A / B 是两个不同的可听候选，各自带参数、图摘要与证据', async () => {
      const dir = songCase();
      await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      await call('session:start', dir);
      const pairDir = path.join(dir, 'studio', 'tuning', pairsIn(dir)[0]);

      const a = JSON.parse(fs.readFileSync(path.join(pairDir, 'A', 'evidence.json'), 'utf8'));
      const b = JSON.parse(fs.readFileSync(path.join(pairDir, 'B', 'evidence.json'), 'utf8'));
      assert.notStrictEqual(a.output.mix_sha256, b.output.mix_sha256, 'A and B must not be one sound');
      for (const [doc, tier] of [[a, 'conservative'], [b, 'full']]) {
        assert.strictEqual(doc.tier.tier, tier);
        assert.strictEqual(doc.tier.calibration_status, 'UNCALIBRATED_ENGINEERING_DEFAULT');
        assert.strictEqual(doc.review_required, true);
        assert.ok(doc.graph_digest_sha256 && doc.tier.parameters.nodes.length >= 3);
        assert.strictEqual(doc.mix_graph_evidence.schema, 'moodify.mix_graph.evidence/0.1');
        for (const gate of doc.checks) assert.strictEqual(gate.passed, true, JSON.stringify(gate));
        // 发布的路径必须是最终路径，不是临时 attempt
        assert.ok(!doc.output.mix_wav.includes('.attempt'));
        assert.strictEqual(doc.output.mix_sha256,
          sha256file(path.join(pairDir, doc.tier.side, 'mix.wav')), 'hash is recomputable');
      }
      const pair = JSON.parse(fs.readFileSync(path.join(pairDir, 'pair.json'), 'utf8'));
      assert.deepStrictEqual(pair.tiers, { A: 'conservative', B: 'full' });
      assert.strictEqual(pair.mode, 'FAST_STEREO_ONLY');
    });

    await check('复检真的跑了：recheck.json 三方守恒，且绑定本对', async () => {
      const dir = songCase();
      await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      await call('session:start', dir);
      const pairId = pairsIn(dir)[0];
      const rc = JSON.parse(fs.readFileSync(
        path.join(dir, 'studio', 'tuning', pairId, 'recheck.json'), 'utf8'));
      assert.strictEqual(rc.schema, 'moodify.studio.recheck/0.1');
      assert.strictEqual(rc.pair_id, pairId);
      assert.strictEqual(rc.original.measurement_count > 0, true, '原版有测量');
      assert.strictEqual(rc.A.measurement_count > 0, true, 'A 有测量');
      assert.strictEqual(rc.B.measurement_count > 0, true, 'B 有测量');
      // 守恒：一个 id 要么可比、要么在 not_alignable 里被解释，绝不消失
      const explained = new Set([...rc.alignable, ...rc.not_alignable.map((x) => x.name)]);
      const seen = new Set([
        ...Object.keys(rc.original.metrics), ...Object.keys(rc.A.metrics),
        ...Object.keys(rc.B.metrics),
      ]);
      for (const id of seen) {
        assert.ok(explained.has(id) || rc.not_alignable.some((x) => x.name === id),
          `${id} must be either alignable or explained`);
      }
      assert.strictEqual(rc.summary.alignable_count, rc.alignable.length);
      assert.strictEqual(rc.summary.not_alignable_count, rc.not_alignable.length);
      assert.strictEqual(
        rc.summary.alignable_count + rc.summary.not_alignable_count > 0, true,
        'a recheck that aligns nothing at all would mean the analysis never ran');
    });

    await check('没有人选定之前，导出被拒绝；三个出口用同一道门', async () => {
      const dir = songCase();
      await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      await call('session:start', dir);
      const pairId = pairsIn(dir)[0];

      const savesBefore = dialogs.save.length;
      const refused = await call('tuning:export', dir, pairId, 'A');
      assert.strictEqual(refused.ok, false);
      assert.strictEqual(refused.reason, 'NOT_CHOSEN');
      assert.strictEqual(dialogs.save.length, savesBefore, 'no dialog may open before a choice');

      // A / B / 保留原版 都过同一条准入规则（两侧候选 + 真复检）
      for (const [i, kept] of ['A', 'B', 'ORIGINAL'].entries()) {
        const res = await call('tuning:decision', dir, pairId, kept, 'creator', `e2e-${i}`);
        assert.strictEqual(res.ok, true, `${kept} must be recordable: ${res.reason}`);
      }
      const ledger = fs.readFileSync(path.join(dir, 'studio', 'tuning', 'decisions.jsonl'), 'utf8')
        .trim().split('\n').map((l) => JSON.parse(l));
      assert.deepStrictEqual(ledger.map((r) => r.kept), ['A', 'B', 'ORIGINAL']);
      assert.strictEqual((await call('pipeline:snapshot', dir)).stage, 'CHOSEN');

      // 选定之后导出会走到「选路径」这一步；stub 里用户取消，不写任何文件
      const exported = await call('tuning:export', dir, pairId, 'ORIGINAL');
      assert.notStrictEqual(exported.reason, 'NOT_CHOSEN');
      assert.notStrictEqual(exported.reason, 'CANDIDATES_INCOMPLETE');
    });

    await check('再次生成会开出新的一对，旧的候选与账本都不被动过', async () => {
      const dir = songCase();
      await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      const first = await call('tuning:render', dir);
      assert.strictEqual(first.ok, true, first.reason);
      const idA = pairsIn(dir)[0];
      const before = sha256file(path.join(dir, 'studio', 'tuning', idA, 'A', 'mix.wav'));

      const second = await call('tuning:render', dir);
      assert.strictEqual(second.ok, true, second.reason);
      const ids = pairsIn(dir);
      assert.strictEqual(ids.length, 2, 'a second attempt is a second pair');
      assert.notStrictEqual(ids[0], ids[1]);
      assert.strictEqual(before, sha256file(path.join(dir, 'studio', 'tuning', idA, 'A', 'mix.wav')),
        'the first pair must be untouched');
    });

    await check('已经有完整一对之后再启动：从当前产物继续，不会重跑 Core', async () => {
      const dir = songCase();
      await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      const first = await call('session:start', dir);
      assert.strictEqual(first.state, 'REVIEW');
      const ids = pairsIn(dir);
      assert.strictEqual(ids.length, 1);
      const mixHash = sha256file(path.join(dir, 'studio', 'tuning', ids[0], 'A', 'mix.wav'));

      const again = await call('session:start', dir);
      assert.strictEqual(again.ok, true, 're-running a finished session is not a failure');
      assert.strictEqual(again.state, 'REVIEW');
      assert.deepStrictEqual(pairsIn(dir), ids, 'no second pair may be produced');
      assert.strictEqual(sha256file(path.join(dir, 'studio', 'tuning', ids[0], 'A', 'mix.wav')),
        mixHash, 'and the existing pair must be untouched');
    });

    await check('原版 / A / B 三路都能拿到真实音频字节（同位置试听的数据面）', async () => {
      const dir = songCase();
      await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      await call('session:start', dir);
      const pairId = pairsIn(dir)[0];

      const bytes = {};
      const hashes = {};
      const sourcePath = JSON.parse(
        fs.readFileSync(path.join(dir, 'source_path.json'), 'utf8')).path;
      for (const side of ['ORIGINAL', 'A', 'B']) {
        const buf = await call('tuning:audio', dir, pairId, side);
        assert.ok(Buffer.isBuffer(buf) || buf instanceof Uint8Array, `${side} must return bytes`);
        assert.ok(buf.length > 44, `${side} must be a real audio file`);
        assert.strictEqual(buf.slice(0, 4).toString('latin1'), 'RIFF', `${side} must be a WAV`);
        bytes[side] = buf;
        hashes[side] = sha256file(side === 'ORIGINAL'
          ? sourcePath
          : path.join(dir, 'studio', 'tuning', pairId, side, 'mix.wav'));
      }
      assert.notStrictEqual(hashes.A, hashes.B, 'the two candidates are different audio');
      assert.notStrictEqual(hashes.ORIGINAL, hashes.A, 'and neither is the untouched original');
      assert.notStrictEqual(bytes.ORIGINAL.length, 0);
    });

    await check('Core 真实失败 → BLOCKED + 真实原因，且不留下任何 pair 或 attempt', async () => {
      const dir = newCaseDir({ report: true });
      // 源音频不是音频：Core 会在读源时失败（真实失败路径，不是注入的假错误）
      const notAudio = path.join(dir, 'song.txt');
      fs.writeFileSync(notAudio, 'this is not audio');
      fs.writeFileSync(path.join(dir, 'source_path.json'), JSON.stringify({ path: notAudio }));
      await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');

      const res = await call('session:start', dir);
      assert.strictEqual(res.ok, false);
      assert.strictEqual(res.reason, 'PHASE_FAILED');
      assert.strictEqual(res.phase, 'tune');
      assert.strictEqual(res.blocker.kind, 'STEP_FAILED');
      assert.match(res.blocker.detail, /unsupported audio extension|source is not a file|error/i);
      assert.deepStrictEqual(pairsIn(dir), [], 'a failed render must not publish a pair');
      assert.deepStrictEqual(attemptsIn(dir), [], 'and must not leave an attempt behind');
      // 失败在重新投影后仍然可见，并给出可重试的信号
      const view = (await call('session:view', dir)).view;
      assert.strictEqual(view.state, 'BLOCKED');
      assert.strictEqual(view.blocker.kind, 'STEP_FAILED');
    });
  }

  // ── 8. Phase 2.1: the blocked deep case offers an explicit switch ─────────────
  //
  // 真实复现的死路：分轨 + MIDI 已存在，深度路径因可逆性 / 逐轨能力走不通。
  // 2026-10-04 人类裁定：提供**显式**快速完成入口，切换必须由人确认，且绝不自动降级。
  console.log('\n8. 深度受阻 → 显式切换到快速完成（Phase 2.1）');
  if (!coreReady) {
    console.log('  SKIP  Core 不可用 —— 图标状态下的真实闭环未经真实音频验证');
    console.log('        (this is a skip, not a pass)');
  } else {
    /** A case with deep assets already on disk (stems + MIDI) but no roundtrip. */
    function deepCase() {
      const dir = songCase();
      fs.mkdirSync(path.join(dir, 'stems'), { recursive: true });
      fs.writeFileSync(path.join(dir, 'stems', 'song__vocals.wav'), 'RIFF');
      fs.writeFileSync(path.join(dir, 'stems', 'manifest.json'),
        JSON.stringify({ engine: 'dsp_center_hpss', engine_note: 'preview' }));
      fs.mkdirSync(path.join(dir, 'midi'), { recursive: true });
      fs.writeFileSync(path.join(dir, 'midi', 'song.mid'), 'MThd');
      return dir;
    }
    const deepAssets = (dir) => ({
      stems: fs.existsSync(path.join(dir, 'stems', 'song__vocals.wav')),
      midi: fs.existsSync(path.join(dir, 'midi', 'song.mid')),
      manifest: sha256file(path.join(dir, 'stems', 'manifest.json')),
    });

    await check('截图状态：模式仍是 DEEP、深度不可执行、切换入口可见', async () => {
      const dir = deepCase();
      const snap = await call('pipeline:snapshot', dir);
      assert.strictEqual(snap.gates.deepAssetsReady, true, '深度资产确实齐备');
      assert.strictEqual(snap.gates.deepExecutable, false, '但深度路径跑不了');
      assert.strictEqual(snap.gates.canTune, false, '深度 ④ 没有被虚假解锁');
      assert.strictEqual(snap.gates.mode, 'DEEP', '没选之前仍是 DEEP');
      assert.strictEqual(snap.gates.modeExecutable, false);
      assert.strictEqual(snap.gates.canRequestQuick, true, '入口必须给出（旧规则这里是死的）');
      assert.ok(snap.gates.deepBlockers.includes('NO_ROUNDTRIP'));
      assert.ok(snap.gates.deepBlockers.includes('DEEP_CORE_UNAVAILABLE'));
      assert.ok(snap.gates.deepTuneBlockers.some((b) => /逐轨修音/.test(b)));

      const view = (await call('session:view', dir)).view;
      assert.strictEqual(view.state, 'BLOCKED');
      assert.strictEqual(view.fastSwitch.available, true);
      assert.strictEqual(view.blocker.canSwitchToFast, true);
      assert.match(view.fastSwitch.note, /不会使用分轨进行音准或节奏修正/);
      assert.match(view.message, /需要你确认一次/);
    });

    await check('确认之前：一键启动不会自动切换，也不写 finish_mode.json、不生成 pair', async () => {
      const dir = deepCase();
      const before = deepAssets(dir);
      const res = await call('session:start', dir);
      assert.strictEqual(res.ok, false, 'it must stop, not silently downgrade');
      assert.strictEqual(res.state, 'BLOCKED');
      assert.strictEqual(res.blocker.kind, 'MISSING_CAPABILITY');
      assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'finish_mode.json')), false,
        'nothing may be recorded on the human’s behalf');
      assert.deepStrictEqual(pairsIn(dir), [], 'and no candidate may be generated');
      assert.deepStrictEqual(deepAssets(dir), before, 'deep assets untouched');
    });

    await check('显式确认切换：只写模式，不生成音频，深度资产与阶段都不倒退', async () => {
      const dir = deepCase();
      const before = deepAssets(dir);
      const stageBefore = (await call('pipeline:snapshot', dir)).stage;
      const res = await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      assert.strictEqual(res.ok, true);
      assert.strictEqual(res.gates.mode, 'FAST_STEREO_ONLY', 'the human choice wins over deep assets');
      assert.strictEqual(res.gates.canTuneQuick, true);
      assert.strictEqual(res.gates.canRequestQuick, false);
      assert.strictEqual(res.gates.canTune, false, 'deep ④ stays closed');
      const record = JSON.parse(fs.readFileSync(path.join(dir, 'studio', 'finish_mode.json'), 'utf8'));
      assert.strictEqual(record.mode, 'QUICK_STEREO_ONLY');
      assert.strictEqual(record.schema, 'moodify.studio.finish-mode/0.1');
      assert.ok(record.chosen_at, 'a human action carries a timestamp');
      assert.deepStrictEqual(pairsIn(dir), [], 'switching generates no audio');
      assert.deepStrictEqual(deepAssets(dir), before, 'and deletes nothing');
      assert.strictEqual((await call('pipeline:snapshot', dir)).stage, stageBefore, 'no stage regression');

      const view = (await call('session:view', dir)).view;
      assert.strictEqual(view.mode, 'FAST_STEREO_ONLY');
      assert.strictEqual(view.fastSwitch.available, false, 'no longer asking');
      const status = Object.fromEntries(view.phases.map((p) => [p.id, p.status]));
      assert.strictEqual(status.decompose, 'done', 'existing assets stay visible');
      assert.strictEqual(status.structure, 'done');
      assert.strictEqual(status.reversible, 'skipped', 'this route does not use it');
      assert.strictEqual(view.nextPhase, 'tune');
    });

    await check('切换后同一个「开始完成」走完真实闭环：一对候选 → 复检 → REVIEW', async () => {
      const dir = deepCase();
      const before = deepAssets(dir);
      await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      const res = await call('session:start', dir);
      assert.strictEqual(res.ok, true, `must complete: ${JSON.stringify(res.blocker || res.detail)}`);
      assert.strictEqual(res.state, 'REVIEW');
      const ids = pairsIn(dir);
      assert.strictEqual(ids.length, 1, 'exactly one render-pair call');
      const pairDir = path.join(dir, 'studio', 'tuning', ids[0]);
      for (const rel of ['pair.json', 'A/mix.wav', 'B/mix.wav', 'A/evidence.json',
        'B/evidence.json', 'recheck.json']) {
        assert.ok(fs.existsSync(path.join(pairDir, rel)), `${rel} must exist`);
      }
      assert.deepStrictEqual(attemptsIn(dir), []);
      assert.deepStrictEqual(deepAssets(dir), before,
        'the whole fast run must leave the deep assets exactly as they were');
    });

    await check('未检测的 case 不能记录快速模式（避免写下一个跑不通的模式）', async () => {
      const dir = newCaseDir({ report: false });
      const res = await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      assert.strictEqual(res.ok, false);
      assert.strictEqual(res.reason, 'NEED_ANALYZE');
      assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'finish_mode.json')), false);
    });
  }

  // ── 9. renderer contract for the switch (copy, not behaviour) ─────────────────
  console.log('\n9. renderer contract: 切换入口的文案与两级确认');
  const html = fs.readFileSync(path.join(__dirname, '..', 'renderer', 'index.html'), 'utf8');
  const appSrc = fs.readFileSync(path.join(__dirname, '..', 'renderer', 'app.js'), 'utf8');
  await check('切换入口与确认按钮是**两个**元素（两级动作，不是一键）', () => {
    assert.ok(html.includes('id="session-remedy-switch"'));
    assert.ok(html.includes('id="session-remedy-yes"'));
    assert.ok(html.includes('id="session-remedy-no"'));
    assert.ok(/id="session-remedy-switch"[\s\S]{0,400}id="session-remedy-yes"/.test(html),
      'the switch and the confirm must be separate controls');
  });
  await check('按钮文案是「切换到快速完成（仅立体声）」，不暗示逐轨/音准/节奏修正', () => {
    const label = /id="session-remedy-switch"[^>]*>([^<]+)</.exec(html);
    assert.ok(label, 'the switch must carry a label');
    assert.match(label[1], /切换到快速完成（仅立体声）/);
    assert.ok(!/逐轨|音准|节奏/.test(label[1]), 'the button must not promise per-track work');
    // 说明里必须**明确否认**这些能力（否认不是承诺）
    assert.match(appSrc, /不会使用分轨进行音准或节奏修正/);
  });
  await check('点「切换」不写任何东西：只有确认那一步才调用 IPC', () => {
    const ask = /function askQuickSwitch\(\)\s*\{([\s\S]*?)\n\}/.exec(appSrc);
    assert.ok(ask, 'askQuickSwitch must exist');
    assert.ok(!/window\.moodify/.test(ask[1]), 'expanding the confirmation must not call the bridge');
    const confirm = /\$\('session-remedy-yes'\)\.addEventListener\('click',[\s\S]{0,200}?chooseQuickFinish\(\)/.exec(appSrc);
    assert.ok(confirm, 'the confirmed action is what records the human decision');
  });
  await check('面板正文来自投影的白话总结，不把工程细节拼到产品面', () => {
    const paints = [...appSrc.matchAll(/\$\('session-remedy-reason'\)\.textContent\s*=\s*([^;]+);/g)]
      .map((m) => m[1]);
    assert.ok(paints.length > 0, 'the remedy panel must set its reason line');
    assert.ok(paints.some((p) => /sw\.summary/.test(p)),
      'the plain summary from the projection is the source');
    assert.ok(!paints.some((p) => /deepReasons/.test(p)),
      'technical reasons must not be concatenated onto the panel');
    // 白话总结在 session.js 里由原因码映射而来，映射表本身不含文件路径
    const sessionSrc = fs.readFileSync(path.join(__dirname, '..', 'src', 'session.js'), 'utf8');
    const map = /PLAIN_DEEP_REASON = Object\.freeze\(\{([\s\S]*?)\}\)/.exec(sessionSrc);
    assert.ok(map, 'the plain-language map must exist');
    assert.ok(!/\.json|MIP-|stems\//.test(map[1]), 'the user-facing wording carries no engineering detail');
  });

  // ── 10. Phase 2.2: the A/B audition workbench data plane ─────────────────────
  //
  // 工作台的每一条数据都必须指向真实产物：候选自己那次复检的 report 与图、pair 里 Core 写的
  // plan/evidence、以及该侧自己的 mix.wav。这一节验证**守恒**与**守卫**，不验证像素。
  console.log('\n10. A/B 审听工作台（Phase 2.2）：数据守恒与路径守卫');
  if (!coreReady) {
    console.log('  SKIP  Core 不可用 —— 工作台数据面未经真实产物验证');
    console.log('        (this is a skip, not a pass)');
  } else {
    async function reviewPair() {
      const dir = songCase();
      await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      const res = await call('session:start', dir);
      assert.strictEqual(res.state, 'REVIEW', `pair must exist: ${JSON.stringify(res.blocker || res.detail)}`);
      return { dir, pairId: pairsIn(dir)[0] };
    }

    await check('证据包：A 页只绑 A 的报告与音频，B 页只绑 B（守恒）', async () => {
      const { dir, pairId } = await reviewPair();
      const ev = await call('tuning:evidence', dir, pairId);
      assert.strictEqual(ev.ok, true, ev.reason);
      const rc = JSON.parse(fs.readFileSync(
        path.join(dir, 'studio', 'tuning', pairId, 'recheck.json'), 'utf8'));

      // A/B/原版三侧都存在，且报告路径与会话侧 recheck 的引用一致
      assert.strictEqual(ev.reports.A, rc.A.report);
      assert.strictEqual(ev.reports.B, rc.B.report);
      assert.strictEqual(ev.reports.original, rc.original.report);
      for (const side of ['ORIGINAL', 'A', 'B']) {
        assert.ok(ev.sides[side], `${side} must be present`);
        assert.ok(fs.existsSync(ev.sides[side].reportPath), `${side} report must exist`);
      }
      // 候选侧必须有音频 + plan + evidence；原版侧指向 case 源
      for (const side of ['A', 'B']) {
        const b = ev.sides[side];
        assert.strictEqual(b.isCandidate, true);
        assert.strictEqual(b.audio, true, `${side} mix.wav must be usable`);
        assert.strictEqual(b.mixPath, path.join(dir, 'studio', 'tuning', pairId, side, 'mix.wav'));
        assert.ok(b.planPath && fs.existsSync(b.planPath));
        assert.ok(b.evidencePath && fs.existsSync(b.evidencePath));
        assert.strictEqual(b.calibrationStatus, 'UNCALIBRATED_ENGINEERING_DEFAULT');
        assert.ok(b.chain && b.chain.nodes.length >= 3, `${side} chain must list its nodes`);
        assert.ok(b.chain.graphDigest && b.chain.graphDigest.length === 64);
        assert.strictEqual(b.chain.reviewRequired, true);
        assert.ok(b.chain.checks.length >= 6, 'the Core hard gates travel with the evidence');
        assert.ok(b.spectra.length >= 1, `${side} must expose its own spectra`);
      }
      // 频谱/图表路径必须落在该侧复检报告目录下（不是原版的、也不是别处的）
      for (const side of ['A', 'B']) {
        for (const spec of ev.sides[side].spectra) {
          assert.ok(spec.path.startsWith(path.dirname(ev.sides[side].reportPath)),
            `${side} spectra must come from its own report dir`);
        }
      }
      // A 与 B 的报告必须是两份不同的文件
      assert.notStrictEqual(ev.reports.A, ev.reports.B);
    });

    await check('音频守恒：三路字节的 sha256 与磁盘上的真实文件一一对应', async () => {
      const { dir, pairId } = await reviewPair();
      const sourcePath = JSON.parse(
        fs.readFileSync(path.join(dir, 'source_path.json'), 'utf8')).path;
      const expect = {
        ORIGINAL: sourcePath,
        A: path.join(dir, 'studio', 'tuning', pairId, 'A', 'mix.wav'),
        B: path.join(dir, 'studio', 'tuning', pairId, 'B', 'mix.wav'),
      };
      for (const [side, file] of Object.entries(expect)) {
        const bytes = await call('tuning:audio', dir, pairId, side);
        const hash = require('crypto').createHash('sha256').update(Buffer.from(bytes)).digest('hex');
        assert.strictEqual(hash, sha256file(file), `${side} audio must be exactly that file`);
      }
      assert.notStrictEqual(sha256file(expect.A), sha256file(expect.B));
    });

    await check('指标卡守恒：每张卡都来自对齐表，缺项写「不可对齐」且带真实原因', async () => {
      const { dir, pairId } = await reviewPair();
      const ev = await call('tuning:evidence', dir, pairId);
      const rc = await call('tuning:recheck', dir, pairId);
      const alignable = new Set(rc.recheck.alignable);
      const notAlignable = new Map(rc.recheck.not_alignable.map((x) => [x.name, x.reason]));
      for (const side of ['A', 'B']) {
        const cards = ev.sides[side].cards;
        assert.ok(cards.length >= 6, `${side} must have a useful card set`);
        for (const card of cards) {
          if (card.status === 'alignable') {
            assert.ok(alignable.has(card.id), `${card.id} must be an alignable metric`);
            const column = side === 'A' ? rc.recheck.A : rc.recheck.B;
            assert.strictEqual(card.original, rc.recheck.original.metrics[card.id].value);
            assert.strictEqual(card.value, column.metrics[card.id].value);
            assert.strictEqual(card.delta, column.delta_vs_original[card.id]);
            assert.ok(typeof card.digits === 'number', 'identical precision is fixed per metric');
          } else {
            assert.strictEqual(card.status, 'not_alignable');
            assert.ok(notAlignable.has(card.id), `${card.id} must be explained by the recheck`);
            assert.strictEqual(card.reason, notAlignable.get(card.id), 'the real reason travels');
          }
        }
      }
      // 卡片绝不引入对齐表之外的指标（守恒：卡片 ⊆ alignable ∪ not_alignable）
      for (const side of ['A', 'B']) {
        for (const card of ev.sides[side].cards) {
          assert.ok(alignable.has(card.id) || notAlignable.has(card.id),
            `${card.id} is not covered by this recheck`);
        }
      }
    });

    await check('图表按侧生成：候选图来自候选自己的报告，原版图另算', async () => {
      const { dir, pairId } = await reviewPair();
      const res = await call('tuning:charts', dir, pairId, 'A');
      assert.strictEqual(res.ok, true, res.reason);
      assert.ok(res.charts.length >= 1, 'Core exports at least one chart');
      const ev = await call('tuning:evidence', dir, pairId);
      const aReportDir = path.dirname(ev.sides.A.reportPath);
      for (const chart of res.charts) {
        assert.ok(chart.path.startsWith(aReportDir), 'A charts live beside A’s report');
        assert.ok(fs.existsSync(chart.path));
      }
      // 原版的图表也按需生成，且落在原版报告目录下（不是候选的）
      const orig = await call('tuning:charts', dir, pairId, 'ORIGINAL');
      assert.strictEqual(orig.ok, true, orig.reason);
      for (const chart of orig.charts) {
        assert.ok(chart.path.startsWith(path.dirname(ev.sides.ORIGINAL.reportPath)));
        assert.ok(!chart.path.startsWith(aReportDir), 'original charts must not come from A');
      }
    });

    await check('守卫：伪造 pair_id / 越界引用 / 非法侧 一律读不到东西', async () => {
      const { dir, pairId } = await reviewPair();
      const fake = await call('tuning:evidence', dir, 'tune_does_not_exist');
      assert.strictEqual(fake.ok, false);
      assert.strictEqual(fake.reason, 'NO_SUCH_PAIR');
      const badSide = await call('tuning:charts', dir, pairId, 'C');
      assert.strictEqual(badSide.ok, false);
      assert.strictEqual(badSide.reason, 'BAD_SIDE');

      // 把 recheck 里的 A 报告路径改成 case 之外的真实文件 → 必须拒绝，不能读出去
      const rcPath = path.join(dir, 'studio', 'tuning', pairId, 'recheck.json');
      const rc = JSON.parse(fs.readFileSync(rcPath, 'utf8'));
      const outside = path.join(CASES_ROOT, 'outside-report.json');
      fs.writeFileSync(outside, JSON.stringify({ measurements: [] }));
      rc.A.report = outside;
      fs.writeFileSync(rcPath, JSON.stringify(rc));
      const escaped = await call('tuning:evidence', dir, pairId);
      assert.strictEqual(escaped.ok, false);
      assert.strictEqual(escaped.reason, 'EVIDENCE_OUTSIDE_CASE');
      const escapedCharts = await call('tuning:charts', dir, pairId, 'A');
      assert.strictEqual(escapedCharts.ok, false);
      assert.strictEqual(escapedCharts.reason, 'EVIDENCE_OUTSIDE_CASE');
      // 伪造路径不予读取，也不得触发 Core 侧的任何分析/导出
      assert.deepStrictEqual(pairsIn(dir), [pairId], 'no new artifacts may appear');
    });

    await check('缺候选音频 / 缺复检时：相应侧不可用，选择与导出保持锁定', async () => {
      const { dir, pairId } = await reviewPair();
      const pairDir = path.join(dir, 'studio', 'tuning', pairId);
      // 移走 B 的 mix.wav：B 侧不可试听，且账本门禁拒绝对这一对做选择
      const bMix = path.join(pairDir, 'B', 'mix.wav');
      fs.renameSync(bMix, `${bMix}.moved`);
      const ev = await call('tuning:evidence', dir, pairId);
      assert.strictEqual(ev.ok, true);
      assert.strictEqual(ev.sides.B.audio, false, 'B must report itself unusable');
      assert.strictEqual(ev.sides.A.audio, true);
      const decision = await call('tuning:decision', dir, pairId, 'A', 'creator', 'missing-b');
      assert.strictEqual(decision.ok, false, 'a half pair is not choosable');
      assert.strictEqual(decision.reason, 'PAIR_NOT_COMPLETE');
      const snapshot = await call('pipeline:snapshot', dir);
      assert.strictEqual(snapshot.gates.canExport, false, 'export stays locked');
      fs.renameSync(`${bMix}.moved`, bMix);
    });

    await check('改选：A → B → A 每次都真的追加记录（request_id 不同即不同决定）', async () => {
      const { dir, pairId } = await reviewPair();
      for (const [i, kept] of ['A', 'B', 'A'].entries()) {
        const res = await call('tuning:decision', dir, pairId, kept, 'creator', `ui-${i}`);
        assert.strictEqual(res.ok, true, `${kept} must be recordable: ${res.reason}`);
      }
      const ledger = fs.readFileSync(path.join(dir, 'studio', 'tuning', 'decisions.jsonl'), 'utf8')
        .trim().split('\n').map((l) => JSON.parse(l));
      assert.deepStrictEqual(ledger.map((r) => r.kept), ['A', 'B', 'A']);
      // 有效决定 = 最后一行的 kept（改选生效）
      const pairs = await call('tuning:pairs', dir);
      const effective = pairs.decisions[pairs.decisions.length - 1];
      assert.strictEqual(effective.kept, 'A');
      assert.strictEqual((await call('pipeline:snapshot', dir)).stage, 'CHOSEN');
    });
  }

  // ── 11. renderer contract for the workbench ─────────────────────────────────
  console.log('\n11. renderer contract：工作台的结构、身份与纪律');
  const html2 = fs.readFileSync(path.join(__dirname, '..', 'renderer', 'index.html'), 'utf8');
  const app2 = fs.readFileSync(path.join(__dirname, '..', 'renderer', 'app.js'), 'utf8');
  await check('两个候选标签存在，且没有第三个「原版」详情页', () => {
    assert.ok(html2.includes('id="rv-tab-a"') && html2.includes('id="rv-tab-b"'));
    assert.ok(!html2.includes('id="rv-tab-original"'),
      '原版是共同基准，通过试听源与对照列进入，不设第三个详情页');
  });
  await check('「当前页面」与「正在试听」是两个独立状态', () => {
    assert.ok(html2.includes('id="rv-page"'), '当前页面必须可见');
    assert.ok(html2.includes('id="rv-playing"'), '正在试听必须可见');
    assert.match(app2, /review\.tab/, 'page state');
    assert.match(app2, /review\.playing/, 'playback state');
  });
  await check('切换音源走真实 tuning:audio，保留位置，失败不改播放身份', () => {
    const load = /async function reviewLoadSide\(side[\s\S]*?\n\}/.exec(app2);
    assert.ok(load, 'reviewLoadSide must exist');
    const decode = /async function reviewDecodeSide\(side[\s\S]*?\n\}/.exec(app2);
    assert.ok(decode, 'reviewDecodeSide must exist');
    assert.match(decode[0], /window\.moodify\.tuningAudio\(/, 'audio comes from the real IPC');
    assert.match(load[0], /reviewDecodeSide\(side\)/, 'and the switch goes through it');
    assert.match(load[0], /reviewCurrentPosition\(\)/, 'the position is captured before loading');
    assert.match(load[0], /seekTo\(/, 'and restored after loading');
    assert.match(load[0], /review\.playing = side/, 'the identity flips only after a successful load');
    // 身份只在**加载成功之后**翻转：失败分支必须先 return。
    const flip = load[0].indexOf('review.playing = side');
    assert.ok(flip > 0, 'the identity flip must exist');
    const beforeFlip = load[0].slice(0, flip);
    assert.match(beforeFlip, /catch \(err\)/, 'the failure path precedes the flip');
    assert.ok(/catch \(err\)[\s\S]*return;/.test(beforeFlip),
      'a load failure must return early and keep the previous source');
    assert.ok(!/loadSide\([^)]*\)\s*[\s\S]{0,120}reviewCurrentPosition\(\)\s*=\s*0/.test(app2),
      'the position must never be reset by a switch');
  });
  await check('A 页只绑定 A，B 页只绑定 B（按 review.tab 取数据）', () => {
    for (const fn of ['renderReviewMetrics', 'renderReviewChain', 'renderReviewActions']) {
      const src = new RegExp(`function ${fn}\\(\\)[\\s\\S]*?\\n\\}`).exec(app2);
      assert.ok(src, `${fn} must exist`);
      assert.ok(/review\.tab/.test(src[0]), `${fn} must read the active tab, not a fixed side`);
    }
    const table = /function renderReviewTable\(\)[\s\S]*?\n\}/.exec(app2);
    assert.ok(table && /r\[side\]/.test(table[0]), 'the audit table follows the active tab');
    assert.ok(table && !/r\.A\.metrics[\s\S]{0,40}r\.B\.metrics/.test(table[0]),
      'one page must never show both A and B columns');
  });
  await check('完整表默认折叠，且按当前候选过滤', () => {
    assert.ok(html2.includes('id="rv-table-toggle"'));
    assert.ok(/id="rv-table"[^>]*hidden/.test(html2), 'the audit table starts folded');
    assert.ok(html2.includes('name="rv-filter"'), 'filters exist');
    assert.match(app2, /review\.tableOpen = false/, 'default state is folded');
  });
  await check('文案不含「更好 / 最佳 / 推荐」，且未校准状态持续可见', () => {
    for (const word of ['更好，', '最佳', '推荐', '增强版']) {
      assert.ok(!new RegExp(`(试听|选择|保留)[^。；]{0,12}${word}`).test(html2 + app2),
        `候选文案不得出现「${word}」`);
    }
    assert.match(app2, /是否更好由你试听决定/, 'the honest disclaimer is present');
    assert.match(app2, /calibrationStatus/, 'the calibration status is shown per candidate');
  });
  await check('选择仍走同一 decision 门禁，改选用新的 requestId', () => {
    assert.match(app2, /\$\('rv-choose'\)\.addEventListener\('click', \(\) => keepExit\(review\.tab\)\)/);
    assert.match(app2, /\$\('rv-keep-original'\)\.addEventListener\('click', \(\) => keepExit\('ORIGINAL'\)\)/);
    assert.match(app2, /window\.moodify\.tuningDecision\(/, 'the single decision authority');
    assert.match(app2, /nextDecisionRequestId/, 'a fresh id per explicit action (改选)');
    assert.ok(!/tuningState\.decisions\.push/.test(app2),
      'no private selection state may be written locally');
  });

  // ── 12. Phase 2.3: the completion layer's gate, keepsake and card ─────────────
  //
  // 「完成」不是新的权威：它由既有 decision（⑦ 准入）+ 该侧音频还在推导。
  // keepsake 只是留存记录——这一节的重点就是证明它既不能被伪造成完成，也不能解锁导出。
  console.log('\n12. 完成层（Phase 2.3）：门禁、留存与作品卡');
  if (!coreReady) {
    console.log('  SKIP  Core 不可用 —— 完成层未经真实产物验证');
    console.log('        (this is a skip, not a pass)');
  } else {
    async function reviewPair2() {
      const dir = songCase();
      await call('pipeline:setFinishMode', dir, 'QUICK_STEREO_ONLY');
      const res = await call('session:start', dir);
      assert.strictEqual(res.state, 'REVIEW', `pair must exist: ${JSON.stringify(res.blocker || res.detail)}`);
      return { dir, pairId: pairsIn(dir)[0] };
    }

    await check('没有 decision 就没有完成层；keepsake 也造不出完成态', async () => {
      const { dir, pairId } = await reviewPair2();
      const state = await call('keepsake:state', dir);
      assert.strictEqual(state.complete, false);
      assert.strictEqual(state.reason, 'NO_DECISION');
      assert.strictEqual((await call('pipeline:snapshot', dir)).gates.canExport, false);

      // 先塞一条 keepsake（假装完成过）→ 阶段不得前进，完成层不得出现
      await call('keepsake:imprint', dir, null);
      fs.writeFileSync(path.join(dir, 'studio', 'keepsake.json'), JSON.stringify({
        schema: 'moodify.studio.keepsake/0.1', selected: 'A', inscription: '伪造',
      }));
      const after = await call('keepsake:state', dir);
      assert.strictEqual(after.complete, false, 'a keepsake file is not a completion fact');
      assert.strictEqual((await call('pipeline:snapshot', dir)).stage, 'RECHECKED');
      assert.strictEqual((await call('pipeline:snapshot', dir)).gates.canExport, false);
      assert.strictEqual(pairId, pairsIn(dir)[0]);
    });

    await check('手写假 decision 不显示完成层', async () => {
      const { dir } = await reviewPair2();
      fs.appendFileSync(path.join(dir, 'studio', 'tuning', 'decisions.jsonl'),
        `${JSON.stringify({ schema: 'moodify.studio.tuning-decision/0.1', pair_id: 'tune_ghost', kept: 'A' })}\n`);
      const state = await call('keepsake:state', dir);
      assert.strictEqual(state.complete, false);
      assert.strictEqual(state.reason, 'PAIR_NOT_COMPLETE');
    });

    await check('A / B / ORIGINAL 三个真实出口都能进入完成层', async () => {
      for (const kept of ['A', 'B', 'ORIGINAL']) {
        const { dir, pairId } = await reviewPair2();
        const decision = await call('tuning:decision', dir, pairId, kept, 'creator', `cp-${kept}`);
        assert.strictEqual(decision.ok, true, decision.reason);
        const sync = await call('keepsake:sync', dir);
        assert.strictEqual(sync.ok, true, sync.reason);
        const state = await call('keepsake:state', dir);
        assert.strictEqual(state.complete, true, `${kept} must complete`);
        assert.strictEqual(state.selected, kept);
        assert.strictEqual(state.pairId, pairId);
        assert.strictEqual(state.audioAvailable, true);
        assert.ok(state.completedAt, 'the completion carries the real decision time');
        assert.ok(state.title, 'and the work title');
        assert.strictEqual(state.selectedLabel,
          kept === 'ORIGINAL' ? '保留原版' : (kept === 'A' ? 'A（保守）' : 'B（充分）'));
        assert.strictEqual(sync.keepsake.selected, kept);
      }
    });

    await check('候选或复检被删掉后，完成层立即失效', async () => {
      const { dir, pairId } = await reviewPair2();
      await call('tuning:decision', dir, pairId, 'A', 'creator', 'cp-del');
      await call('keepsake:sync', dir);
      assert.strictEqual((await call('keepsake:state', dir)).complete, true);

      const recheckFile = path.join(dir, 'studio', 'tuning', pairId, 'recheck.json');
      const backup = fs.readFileSync(recheckFile);
      fs.rmSync(recheckFile);
      const gone = await call('keepsake:state', dir);
      assert.strictEqual(gone.complete, false, 'a lost recheck takes the completion away');
      assert.strictEqual(gone.reason, 'PAIR_NOT_COMPLETE');
      assert.strictEqual((await call('pipeline:snapshot', dir)).gates.canExport, false);
      fs.writeFileSync(recheckFile, backup);
      assert.strictEqual((await call('keepsake:state', dir)).complete, true, 'and it comes back');
    });

    await check('选 ORIGINAL 后源音频缺失：完成层保留文字但显示音频不可用（不换别的版本）', async () => {
      const { dir, pairId } = await reviewPair2();
      await call('tuning:decision', dir, pairId, 'ORIGINAL', 'creator', 'cp-orig');
      await call('keepsake:sync', dir);
      await call('keepsake:inscription', dir, '写给这首歌');
      const sourcePath = JSON.parse(
        fs.readFileSync(path.join(dir, 'source_path.json'), 'utf8')).path;
      fs.renameSync(sourcePath, `${sourcePath}.moved`);
      const state = await call('keepsake:state', dir);
      assert.strictEqual(state.complete, true, 'the decision is still backed by a complete pair');
      assert.strictEqual(state.selected, 'ORIGINAL');
      assert.strictEqual(state.audioAvailable, false, 'but the audio is gone');
      assert.strictEqual(state.audioPath, null, 'no other version may be substituted');
      assert.strictEqual(state.inscription, '写给这首歌', 'the words survive');
      fs.renameSync(`${sourcePath}.moved`, sourcePath);
    });

    await check('一句话：写入 / 读回 / 超限拒绝 / 改选后保留 / 失效后不删', async () => {
      const { dir, pairId } = await reviewPair2();
      await call('tuning:decision', dir, pairId, 'A', 'creator', 'cp-text');
      await call('keepsake:sync', dir);
      const saved = await call('keepsake:inscription', dir, 'é中文😀 一行\n第二行');
      assert.strictEqual(saved.ok, true);
      assert.strictEqual((await call('keepsake:state', dir)).inscription, 'é中文😀 一行\n第二行');

      const tooLong = await call('keepsake:inscription', dir, '花'.repeat(281));
      assert.strictEqual(tooLong.ok, false);
      assert.strictEqual(tooLong.reason, 'INSCRIPTION_TOO_LONG');
      const tooManyLines = await call('keepsake:inscription', dir, 'a\nb\nc\nd\ne');
      assert.strictEqual(tooManyLines.reason, 'INSCRIPTION_TOO_MANY_LINES');

      // 改选 → selected 更新，文字保留
      await call('tuning:decision', dir, pairId, 'B', 'creator', 'cp-text-2');
      await call('keepsake:sync', dir);
      const changed = await call('keepsake:state', dir);
      assert.strictEqual(changed.selected, 'B');
      assert.strictEqual(changed.inscription, 'é中文😀 一行\n第二行');

      // decision 失效 → 完成层消失，但文字不删
      const bMix = path.join(dir, 'studio', 'tuning', pairId, 'B', 'mix.wav');
      fs.renameSync(bMix, `${bMix}.moved`);
      const invalid = await call('keepsake:state', dir);
      assert.strictEqual(invalid.complete, false);
      assert.strictEqual(invalid.inscription, 'é中文😀 一行\n第二行', 'the text is not collateral');
      const refused = await call('keepsake:sync', dir);
      assert.strictEqual(refused.ok, false, 'nothing may be projected while incomplete');
      fs.renameSync(`${bMix}.moved`, bMix);
      assert.strictEqual((await call('keepsake:state', dir)).complete, true);
    });

    await check('损坏的留存文件不阻断任何东西，并留下可诊断原因', async () => {
      const { dir, pairId } = await reviewPair2();
      await call('tuning:decision', dir, pairId, 'A', 'creator', 'cp-broken');
      fs.writeFileSync(path.join(dir, 'studio', 'keepsake.json'), '{ not json at all');
      const state = await call('keepsake:state', dir);
      assert.strictEqual(state.ok, true, 'the state itself is still readable');
      assert.strictEqual(state.complete, true, 'completion does not depend on the keepsake file');
      assert.strictEqual(state.inscription, '');
      assert.strictEqual(state.keepsakeError, 'KEEPSAKE_CORRUPT_JSON');
      assert.strictEqual((await call('pipeline:snapshot', dir)).gates.canExport, true);
      // 而且可以就地修好
      await call('keepsake:inscription', dir, '重来一句');
      assert.strictEqual((await call('keepsake:state', dir)).inscription, '重来一句');
    });

    await check('波形印记：定长、限幅、可复算，且不会写入 case 之外', async () => {
      const { dir, pairId } = await reviewPair2();
      await call('tuning:decision', dir, pairId, 'A', 'creator', 'cp-imprint');
      const peaks = Array.from({ length: 4000 }, (_, i) => Math.abs(Math.sin(i / 50)));
      const res = await call('keepsake:imprint', dir, peaks);
      assert.strictEqual(res.ok, true);
      assert.strictEqual(res.imprint.length, 600);
      const again = await call('keepsake:imprint', dir, peaks);
      assert.deepStrictEqual(again.imprint, res.imprint, 'same audio → same imprint');
      const state = await call('keepsake:state', dir);
      assert.deepStrictEqual(state.imprint, res.imprint);
      assert.strictEqual(state.imprintBuckets, 600);
      // 只有 <case>/studio 下的那个文件被写
      const studioFiles = fs.readdirSync(path.join(dir, 'studio')).sort();
      assert.deepStrictEqual(studioFiles, ['finish_mode.json', 'keepsake.json', 'pipeline.json', 'tuning']
        .filter((n) => fs.existsSync(path.join(dir, 'studio', n))).sort());
    });

    await check('作品卡：取消不写文件；确认后写入的正是那些字节且可解码', async () => {
      const { dir, pairId } = await reviewPair2();
      await call('tuning:decision', dir, pairId, 'B', 'creator', 'cp-card');
      await call('keepsake:sync', dir);

      // 用 Pillow 造一张真实 PNG（不是空文件），过一遍保存通道
      const pngPath = path.join(CASES_ROOT, 'card-fixture.png');
      const made = spawnSync(PY, ['-c',
        'import sys; from PIL import Image; Image.new("RGB", (1600, 1000), "white").save(sys.argv[1])',
        pngPath], { encoding: 'utf8', env: pyEnv });
      assert.strictEqual(made.status, 0, `could not build the PNG fixture: ${made.stderr}`);
      const bytes = fs.readFileSync(pngPath);

      // ① 用户取消 → 不写文件、不算失败
      const saves = dialogs.save.length;
      const canceled = await call('keepsake:saveCard', dir, bytes);
      assert.strictEqual(canceled.ok, false);
      assert.strictEqual(canceled.canceled, true);
      assert.strictEqual(dialogs.save.length, saves + 1, 'the dialog opened once');
      assert.deepStrictEqual(dialogs.lastOptions.filters[0].extensions, ['png']);
      assert.match(dialogs.lastOptions.defaultPath, /B（充分）|— Moodify\.png/);

      // ② 确认 → 写入的字节与传入完全一致，且是一张可解码的 1600×1000
      const target = path.join(CASES_ROOT, '作品卡-out.png');
      dialogs.nextSavePath = target;
      const saved = await call('keepsake:saveCard', dir, bytes);
      dialogs.nextSavePath = null;
      assert.strictEqual(saved.ok, true, saved.reason);
      assert.strictEqual(saved.bytes, bytes.length);
      assert.deepStrictEqual(fs.readFileSync(target), bytes, 'the file is exactly what was drawn');
      const probe = spawnSync(PY, ['-c',
        'import sys; from PIL import Image; im = Image.open(sys.argv[1]); print(im.size[0], im.size[1], im.format)',
        target], { encoding: 'utf8', env: pyEnv });
      assert.strictEqual(probe.status, 0, probe.stderr);
      assert.strictEqual(probe.stdout.trim(), '1600 1000 PNG');
    });

    await check('卡片模型里没有 id / 路径 / hash（隐私由构造保证）', async () => {
      const { dir, pairId } = await reviewPair2();
      await call('tuning:decision', dir, pairId, 'A', 'creator', 'cp-privacy');
      await call('keepsake:sync', dir);
      const state = await call('keepsake:state', dir);
      const blob = JSON.stringify(state.card);
      assert.ok(!new RegExp(pairId).test(blob), 'no pair id');
      assert.ok(!/case_[0-9a-f]{32}/.test(blob), 'no case id');
      assert.ok(!/[A-Za-z]:\\/.test(blob), 'no absolute path');
      assert.ok(!/[0-9a-f]{64}/.test(blob), 'no hash');
      assert.deepStrictEqual(Object.keys(state.card).sort(),
        ['dateLabel', 'inscription', 'selectionLabel', 'title', 'versionLabel']);
    });
  }

  // ── 13. renderer contract for the completion layer ───────────────────────────
  console.log('\n13. renderer contract：完成层 / 安静聆听 / 作品卡');
  const html3 = fs.readFileSync(path.join(__dirname, '..', 'renderer', 'index.html'), 'utf8');
  const app3 = fs.readFileSync(path.join(__dirname, '..', 'renderer', 'app.js'), 'utf8');
  const css3 = fs.readFileSync(path.join(__dirname, '..', 'renderer', 'style.css'), 'utf8');
  await check('完成层元素齐备，且每个动作都有绑定', () => {
    for (const id of ['completion', 'cp-title', 'cp-version', 'cp-imprint', 'cp-date', 'cp-listen',
      'cp-export', 'cp-card', 'cp-details', 'cp-inscribe-toggle', 'cp-inscription',
      'cp-card-include', 'cp-inscription-save', 'cp-inscription-clear', 'cp-status',
      'cp-listen-bar', 'cp-play', 'cp-time', 'cp-volume', 'cp-listening', 'cp-exit-listen']) {
      assert.ok(html3.includes(`id="${id}"`), `${id} must exist`);
    }
    for (const id of ['cp-listen', 'cp-play', 'cp-details', 'cp-export', 'cp-card',
      'cp-inscription-save', 'cp-inscription-clear', 'cp-exit-listen']) {
      assert.ok(new RegExp(`\\$\\('${id}'\\)\\.addEventListener`).test(app3), `${id} must be wired`);
    }
  });
  await check('完成层与制作详情可双向进入（同一份数据，不复制第二套）', () => {
    assert.match(app3, /function applyWorkspaceMode\(\)/, 'a single place decides which layer shows');
    assert.match(app3, /\$\('cp-details'\)\.addEventListener\('click', \(\) => completionShowDetails\(\)\)/);
    assert.match(app3, /completion\.detailsOpen = true/, 'details opens the A/B workspace');
    assert.match(app3, /completion\.detailsOpen = false;[\s\S]{0,200}refreshCompletion\(\)/,
      'and choosing again settles back into the work');
    assert.ok(!/\$\('completion'\)\.hidden = false;\s*\$\(.review.\)\.hidden = false/.test(app3),
      'both layers must not be shown at once');
  });
  await check('播放器复用：审听/完成层共用 Phase 2.2 的那一个 transport', () => {
    // 整个 shell 里有别的工作台（波形/分轨），所以这里数的是**审听这条路**上的实例：
    // 只会建一次，且完成层自己绝不新建播放器。
    const mount = /function reviewMountTransport\(buffer\)[\s\S]*?\n\}/.exec(app3);
    assert.ok(mount, 'reviewMountTransport must exist');
    assert.strictEqual((mount[0].match(/WaveSurfer\.create\(/g) || []).length, 1);
    assert.match(mount[0], /if \(!review\.ws\)/, 'it is created once and reused');
    for (const fn of ['completionListenFromStart', 'ensureSelectedAudioDecoded', 'completionEnterQuiet',
      'completionExitQuiet', 'completionSaveCard']) {
      const body = new RegExp(`(async )?function ${fn}\\([\\s\\S]*?\\n\\}`).exec(app3);
      assert.ok(body, `${fn} must exist`);
      assert.ok(!/WaveSurfer\.create|new AudioContext/.test(body[0]),
        `${fn} must reuse the shared transport, not build another one`);
    }
    assert.match(app3, /async function ensureSelectedAudioDecoded[\s\S]*?reviewDecodeSide\(/,
      '从头听 reuses the Phase 2.2 decode path');
    assert.match(app3, /review\.ws\.on\('timeupdate'[\s\S]{0,260}\$\('cp-time'\)/,
      'the same transport also paints the completion layer time');
  });
  await check('从头听：位置归零、不自动播放、曲终保持安静', () => {
    const listen = /async function completionListenFromStart\(\)[\s\S]*?\n\}/.exec(app3);
    assert.ok(listen, 'completionListenFromStart must exist');
    assert.match(listen[0], /seekTo\(0\)/, 'it starts from the beginning');
    assert.match(listen[0], /autoplay: false/, 'loading a side never auto-plays by itself');
    assert.match(app3, /review\.ws\.on\('finish'[\s\S]{0,220}cp-play/,
      'the end of the song stays quiet (button back to ▶, nothing else)');
    assert.ok(!/nextTrack|playNext|autoplayNext/.test(app3), 'no autoplay-next exists anywhere');
    // 「推荐」只允许出现在「不做推荐」这种否定句里
    assert.ok(!/向你推荐|推荐你|为你推荐/.test(app3), 'the shell never recommends a version');
  });
  await check('波形印记确定性：无随机、无时钟，且与完成层/卡片同源', () => {
    const peaks = /function imprintPeaksFromBuffer[\s\S]*?\n\}/.exec(app3);
    assert.ok(peaks, 'imprintPeaksFromBuffer must exist');
    assert.ok(!/Math\.random|Date\.now|new Date/.test(peaks[0]), 'no randomness, no clock');
    assert.match(app3, /keepsakeImprint\(/, 'the imprint is stored via the keepsake IPC');
    assert.match(app3, /function paintImprint\(canvas, imprint, selected\)/, 'one painting routine');
    const card = /async function drawKeepsakeCard[\s\S]*?\n\}/.exec(app3);
    assert.ok(card, 'drawKeepsakeCard must exist');
    assert.ok(!/Math\.random/.test(card[0]), 'the card is drawn deterministically');
    assert.match(card[0], /state\.card\.title|state\.title/, 'the card uses the projected model');
  });
  await check('作品卡不外泄技术字段：只用投影里的字段绘制', () => {
    const card = /async function drawKeepsakeCard[\s\S]*?\n\}/.exec(app3);
    assert.ok(card, 'drawKeepsakeCard must exist');
    for (const leak of ['caseDir', 'pairId', 'pair_id', 'sha256', 'hash', 'reportPath', 'evidencePath']) {
      assert.ok(!new RegExp(`\\b${leak}\\b`).test(card[0]), `the card must not read ${leak}`);
    }
    assert.match(card[0], /state\.card\.inscription/, 'the optional inscription comes from the model');
  });
  await check('安静聆听：隐去流程与侧栏，Esc / 返回作品可退出', () => {
    assert.match(css3, /body\.cp-quiet\s+#rail[\s\S]{0,220}display:\s*none/);
    assert.match(app3, /function completionEnterQuiet\(\)/, 'quiet mode exists');
    assert.match(app3, /function completionExitQuiet\(\)/, 'and can be left');
    assert.match(app3, /event\.key !== 'Escape'[\s\S]{0,160}completionExitQuiet\(\)/,
      'Esc leaves quiet listening');
    assert.match(html3, /id="cp-exit-listen"[^>]*>返回作品</, 'and there is a visible way back');
  });
  await check('减少动画：CSS 媒体查询与 JS 分支都在', () => {
    assert.match(css3, /@media \(prefers-reduced-motion: reduce\)/);
    assert.match(css3, /\.cp-stage \{ animation: none; \}/);
    assert.match(app3, /function prefersReducedMotion\(\)/);
    assert.match(app3, /behavior: prefersReducedMotion\(\) \? 'auto' : 'smooth'/);
  });
  await check('完成层首屏只有作品：短文案，无指标/无 id/无理念句', () => {
    const section = /<section id="completion"[\s\S]*?<\/section>/.exec(html3);
    assert.ok(section, 'the completion section must exist');
    const text = section[0].replace(/<[^>]+>/g, ' ');
    for (const forbidden of ['LUFS', 'hash', 'pair_id', 'case_id', 'schema', 'MIP', 'dBFS', '频谱']) {
      assert.ok(!text.includes(forbidden), `首屏不得出现技术字样：${forbidden}`);
    }
    for (const allowed of ['从头听', '导出音频', '保存作品卡', '查看制作详情', '留一句话', '返回作品']) {
      assert.ok(text.includes(allowed), `缺少必要动作文案：${allowed}`);
    }
    assert.match(section[0], /placeholder="写给这首歌"/, 'the inscription placeholder is exactly this');
    assert.ok(!/更好|最佳|推荐|增强版|AI 增强/.test(text), 'no marketing or judgement words');
  });
  await check('键盘可达与无横向溢出：按钮为主、焦点可见、窄窗口留白', () => {
    assert.match(css3, /button:focus-visible, textarea:focus-visible, input:focus-visible/);
    assert.match(css3, /@media \(min-width: 800px\)[\s\S]{0,80}overflow-x: hidden/);
    assert.match(app3, /if \(entered\) \{[\s\S]{0,220}\$\('cp-listen'\)\.focus\(\)/,
      'focus lands on 从头听 after completion');
    assert.match(html3, /id="cp-title"[^>]*class="cp-title"/);
    assert.match(css3, /\.cp-title[\s\S]{0,200}text-overflow: ellipsis/,
      'long titles truncate visually');
  });

  Module._load = originalLoad;
  try { fs.rmSync(CASES_ROOT, { recursive: true, force: true }); } catch { /* best effort */ }

  console.log(`\n${passed} passed, ${failures.length} failed`);
  if (failures.length) {
    console.log('\nFailures:');
    for (const f of failures) console.log('  - ' + f);
    process.exit(1);
  }
  // 这个脚本 require 了真实的 main.js，而 main.js 会留下活着的句柄
  // （codex stdio 客户端、长任务单飞锁、可能还有 node-pty 的 shell）。
  // 断言全部跑完后必须显式退出：否则进程永远不退出，`npm test` 就变成一个
  // 「测试全过、但命令永不返回」的挂起——比失败更难诊断，而且会攒下孤儿进程。
  // 这是测试夹具的收尾，不是被测代码的行为。
  process.exit(0);
})().catch((err) => {
  console.error('TEST HARNESS ERROR:', err);
  process.exit(1);
});
