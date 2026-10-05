#!/usr/bin/env node
/**
 * 主进程集成测试 — 完成会话编排器（一键完成机 · Phase 1）
 *
 * 这里测的是 `src/orchestrator.js` 的调度循环 + `src/session.js` 的投影 + 真实的 `src/pipeline.js`
 * 阶段推导，跑在真实临时 case 目录上；步骤函数由测试注入，于是每一种失败都能被确定性地复现
 * （不需要 Electron、不需要 Python、不需要 Core）。
 *
 * 为什么必须有这个文件（三处 P1 的回归锚点）
 *
 *  1 没有 report.json 的世界，检测**不会**被反复执行
 *     Core 的检测总是新建 case（`analyze_to_case` → 新 case_id + mkdir(exist_ok=False)），
 *     所以对一个已经存在的 case 目录来说「再检测一次」永远不会让这一步完成。旧实现每轮重跑、
 *     每轮造一个新 case，最后只报一句 NO_PROGRESS。现在：同一步在一次启动里只尝试一次，
 *     「声称成功却没有产物」当场停止并如实记账。
 *
 *  2 真实步骤失败必须**可见**，而且不能只活在那一次返回值里
 *     `分轨失败 / 缺少 Basic Pitch` 这类原因如果只随返回值回一次，UI 随后重新拉投影时磁盘
 *     没变、状态又变回 READY，用户看到的就是「什么也没发生」。所以失败要落成记录，并在
 *     该相位仍未完成时把视图降级为 BLOCKED —— 它不推进任何阶段，只是不让失败消失。
 *
 *  3 一次失败的步骤必须**可以重试**（记录只影响显示，不影响控制流）
 *
 * 另外覆盖：续跑（已有产物跳过）、相位顺序、真实能力阻断（TUNABLE_CORE_NOT_AVAILABLE）、
 * 重复启动安全、不生成任何假产物。
 *
 * Run: node scripts/test-orchestrator.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');

const pipeline = require(path.join(__dirname, '..', 'src', 'pipeline'));
const session = require(path.join(__dirname, '..', 'src', 'session'));
const tuning = require(path.join(__dirname, '..', 'src', 'tuning'));
const { createOrchestrator } = require(path.join(__dirname, '..', 'src', 'orchestrator'));

let passed = 0;
const failures = [];
async function check(label, fn) {
  try { await fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-orchestrator-test-'));
let caseSeq = 0;

function makeReport() {
  return {
    protocol: 'moodify.sound/0.2',
    report_schema_version: 'moodify.msp_report/0.2',
    generated_at: '2026-10-04T00:00:00+00:00',
    job: { type: 'analyze', source: 'song.wav' },
    case: { case_id: 'case_test' },
    source: { name: 'song.wav', sha256: 'sha256:' + 'a'.repeat(64), duration_s: 30, channels: 2, sample_rate: 48000 },
    measurements: [],
    findings: [],
    plan: { status: 'DRAFT_PLAN_NOT_EXECUTED', nodes: [], next_actions: [], notes: [] },
    judgment_boundary: { layer1_measurement: 'EXECUTED', layer2_comparison: 'NOT_RUN' },
    technical_state: { overall: 'OK', workflow_decision: 'NO_TECHNICAL_BLOCKERS', reasons: [] },
    provenance: { core_version: '1.0.0-rc.1' },
  };
}

/** A case directory with exactly the artifacts requested. */
function makeCase(opts = {}) {
  const dir = path.join(tmpRoot, `case_${String(++caseSeq).padStart(4, '0')}`);
  fs.mkdirSync(path.join(dir, 'studio'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'case.json'), JSON.stringify({ case_id: 'case_test' }));
  fs.writeFileSync(path.join(dir, 'source_path.json'),
    JSON.stringify({ path: path.join(dir, 'song.wav') }));
  if (opts.report !== false) fs.writeFileSync(path.join(dir, 'report.json'), JSON.stringify(makeReport()));
  if (opts.stems) {
    fs.mkdirSync(path.join(dir, 'stems'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'stems', 'song__vocals.wav'), 'RIFF');
  }
  if (opts.midi) {
    fs.mkdirSync(path.join(dir, 'midi'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'midi', 'song.mid'), 'MThd');
  }
  if (opts.roundtrip) {
    fs.writeFileSync(path.join(dir, 'studio', 'roundtrip.json'), JSON.stringify({
      schema: 'moodify.studio.roundtrip/0.1', passed: true, engine: 'dsp_center_hpss',
    }));
  }
  return dir;
}

/**
 * Build an orchestrator over real pipeline/session with injected steps.
 * `impl` maps a phase run-key to a function; every call is recorded.
 */
function harness(impl = {}) {
  const calls = [];
  const steps = {};
  for (const key of ['analyze', 'separate', 'structure', 'tune', 'recheck']) {
    steps[key] = async (dir, ctx) => {
      calls.push(key);
      const fn = impl[key];
      if (!fn) return { ok: true, stubbed: true };
      return fn(dir, ctx);
    };
  }
  const events = [];
  const event = { sender: { send: (_ch, payload) => events.push(payload) } };
  const orch = createOrchestrator({
    snapshot: (dir) => pipeline.snapshot(dir),
    resolveCaseSource: (dir) => {
      try { return JSON.parse(fs.readFileSync(path.join(dir, 'source_path.json'), 'utf8')).path; }
      catch { return null; }
    },
    steps,
  });
  return { orch, calls, events, event };
}

/** The orchestrator may never leave audio or candidate artifacts behind. */
function assertNoFakeArtifacts(dir, { allow = [] } = {}) {
  for (const forbidden of ['tuning', 'versions', 'export', 'finishing']) {
    const p = path.join(dir, 'studio', forbidden);
    assert.strictEqual(fs.existsSync(p), false, `no ${forbidden}/ may be created by the orchestrator`);
  }
  assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'tuning', 'decisions.jsonl')), false,
    'no decision ledger may be written');
  const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => {
    const full = path.join(d, e.name);
    return e.isDirectory() ? walk(full) : [full];
  });
  const wavs = walk(dir).filter((f) => f.toLowerCase().endsWith('.wav') && !allow.some((a) => f.includes(a)));
  assert.deepStrictEqual(wavs, [], 'the orchestrator itself must never write audio');
}

(async () => {
  console.log('completion orchestrator (main process, Phase 1)\n');

  // ── 1. resume: finished steps are skipped ─────────────────────────────────────
  console.log('1. resume — artifacts already on disk are not produced again');
  await check('检测/分轨/结构 都已存在的世界直接停在真正缺的那一步', async () => {
    const dir = makeCase({ report: true, stems: true, midi: true });
    const h = harness();
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.deepStrictEqual(h.calls, [], 'no finished step may run again');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'BLOCKED');
    assert.strictEqual(res.blocker.kind, 'MISSING_CAPABILITY');
    assert.strictEqual(res.blocker.phase, 'reversible');
    const done = res.phases.filter((p) => p.status === 'done').map((p) => p.id);
    assert.deepStrictEqual(done, ['detect', 'decompose', 'structure']);
  });

  // ── 2. the P1: a report-less case must not be "re-analysed" round after round ──
  console.log('\n2. a world without report.json — one attempt, then an honest stop');
  await check('检测步骤拒绝就地补写，且只被调用一次（不会反复造新 case）', async () => {
    const dir = makeCase({ report: false });
    const before = fs.readdirSync(tmpRoot).sort();
    const h = harness({
      // 与 main.js 的 sessionAnalyze 同一语义：Core 的检测总是新建 case，无法就地补写
      analyze: async () => ({
        ok: false,
        reason: 'CASE_WITHOUT_REPORT',
        detail: 'Core 的检测总是新建一个世界，无法就地补写；请用「打开音频」重新导入。',
      }),
    });
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.deepStrictEqual(h.calls, ['analyze'], 'exactly one attempt');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'PHASE_FAILED');
    assert.strictEqual(res.phase, 'detect');
    assert.strictEqual(res.blocker.kind, 'STEP_FAILED');
    assert.match(res.blocker.detail, /重新导入/);
    assert.deepStrictEqual(fs.readdirSync(tmpRoot).sort(), before, 'no duplicate case may be created');
    assert.strictEqual(fs.existsSync(path.join(dir, 'report.json')), false, 'no fake report either');
  });
  await check('「声称成功但没有产物」当场停止为 NO_PROGRESS，而不是重复执行到上限', async () => {
    const dir = makeCase({ report: false });
    const before = fs.readdirSync(tmpRoot).sort();
    const h = harness({ analyze: async () => ({ ok: true }) }); // 谎报成功
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.deepStrictEqual(h.calls, ['analyze'], 'it must not be retried');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'NO_PROGRESS');
    assert.strictEqual(res.phase, 'detect');
    assert.strictEqual(res.state, 'BLOCKED');
    assert.strictEqual(session.readFailure(dir).reason, 'NO_PROGRESS');
    assert.deepStrictEqual(fs.readdirSync(tmpRoot).sort(), before);
  });

  // ── 3. the P1: a real step failure stays visible ──────────────────────────────
  console.log('\n3. a real step failure is visible, survives re-projection, and is retryable');
  const NO_BASIC_PITCH = '未找到 basic-pitch（.venv-basic-pitch）';
  await check('分轨失败 → BLOCKED + 原因保留；重新投影后仍然可见（不再是「什么也没发生」）', async () => {
    const dir = makeCase({ report: true });
    const h = harness({ separate: async () => ({ ok: false, reason: NO_BASIC_PITCH }) });
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'PHASE_FAILED');
    assert.strictEqual(res.phase, 'decompose');
    assert.strictEqual(res.detail, NO_BASIC_PITCH);

    // UI 随后会**重新拉一次投影**（换页、刷新都算）——失败不能被这一次投影洗掉
    const view = h.orch.sessionView(dir);
    assert.strictEqual(view.state, 'BLOCKED', 'a re-projection must not fall back to READY');
    assert.strictEqual(view.blocker.kind, 'STEP_FAILED');
    assert.strictEqual(view.blocker.phase, 'decompose');
    assert.strictEqual(view.blocker.detail, NO_BASIC_PITCH);
    assert.ok(view.message.includes(NO_BASIC_PITCH), 'the message must carry the real reason');
    assert.match(view.message, /没有生成任何候选版本/);
    assert.strictEqual(fs.existsSync(session.failurePath(dir)), true, 'the failure is a record, not a vibe');
    assertNoFakeArtifacts(dir);
  });
  await check('失败记录不拦控制流：再次启动会真的重试那一步，并继续往前走', async () => {
    const dir = makeCase({ report: true });
    let attempt = 0;
    const h = harness({
      separate: async (d) => {
        attempt += 1;
        if (attempt === 1) return { ok: false, reason: NO_BASIC_PITCH };
        fs.mkdirSync(path.join(d, 'stems'), { recursive: true });
        fs.writeFileSync(path.join(d, 'stems', 'song__vocals.wav'), 'RIFF');
        return { ok: true };
      },
      structure: async (d) => {
        fs.mkdirSync(path.join(d, 'midi'), { recursive: true });
        fs.writeFileSync(path.join(d, 'midi', 'song.mid'), 'MThd');
        return { ok: true };
      },
    });
    const first = await h.orch.runCompletionSession(h.event, dir);
    assert.strictEqual(first.blocker.detail, NO_BASIC_PITCH);
    const second = await h.orch.runCompletionSession(h.event, dir);
    assert.strictEqual(attempt, 2, 'the second start must really retry the failed step');
    assert.deepStrictEqual(h.calls, ['separate', 'separate', 'structure'],
      'and it must move on instead of stopping at the remembered failure');
    assert.strictEqual(second.blocker.phase, 'reversible', 'the next real blocker is reached');
    assert.strictEqual(fs.existsSync(session.failurePath(dir)), false, 'the stale record is cleared');
  });
  await check('产物补上之后，旧的失败记录自动过期（记录不是权威）', async () => {
    const dir = makeCase({ report: true });
    const h = harness({ separate: async () => ({ ok: false, reason: NO_BASIC_PITCH }) });
    await h.orch.runCompletionSession(h.event, dir);
    assert.strictEqual(h.orch.sessionView(dir).state, 'BLOCKED');
    // 人手动做了分轨（高级层），投影必须立刻反映真实产物
    fs.mkdirSync(path.join(dir, 'stems'), { recursive: true });
    fs.writeFileSync(path.join(dir, 'stems', 'song__vocals.wav'), 'RIFF');
    const view = h.orch.sessionView(dir);
    assert.notStrictEqual(view.state, 'BLOCKED');
    assert.strictEqual(view.nextPhase, 'structure');
    assert.strictEqual(fs.existsSync(session.failurePath(dir)), false, 'the expired record is removed');
  });

  // ── 4. phase order + the honest capability block ──────────────────────────────
  console.log('\n4. phase order and the honest capability block');
  const SEPARATE_OK = async (d) => {
    fs.mkdirSync(path.join(d, 'stems'), { recursive: true });
    fs.writeFileSync(path.join(d, 'stems', 'song__vocals.wav'), 'RIFF');
    return { ok: true };
  };
  const STRUCTURE_OK = async (d) => {
    fs.mkdirSync(path.join(d, 'midi'), { recursive: true });
    fs.writeFileSync(path.join(d, 'midi', 'song.mid'), 'MThd');
    return { ok: true };
  };
  await check('步骤按真实门禁顺序执行：分解 → 结构，然后停在 Core 不具备的 修音/复合', async () => {
    const dir = makeCase({ report: true, roundtrip: true });
    const h = harness({
      separate: SEPARATE_OK,
      structure: STRUCTURE_OK,
      tune: async () => ({ ok: false, reason: 'TUNABLE_CORE_NOT_AVAILABLE' }),
    });
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.deepStrictEqual(h.calls, ['separate', 'structure'], 'real execution order, no skipping');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'BLOCKED');
    assert.strictEqual(res.blocker.kind, 'MISSING_CAPABILITY');
    assert.strictEqual(res.blocker.phase, 'tune');
    assert.deepStrictEqual(res.blocker.capabilities, ['stem-tuning', 'multi-stem-compose']);
    assert.match(res.message, /没有生成任何候选版本/);
    assertNoFakeArtifacts(dir, { allow: ['stems' + path.sep, 'midi' + path.sep] });
    // 进度事件里能看到正在执行的相位（PROCESSING 面）
    const active = h.events.filter((e) => e.activePhase).map((e) => e.activePhase);
    assert.deepStrictEqual(active, ['decompose', 'structure']);
  });
  await check('修音/复合 的步骤自己也会拒绝（能力清单若变了，这一层仍然不产假产物）', async () => {
    const dir = makeCase({ report: true, roundtrip: true, stems: true, midi: true });
    const h = harness({ tune: async () => {
      // 与 main.js 的 sessionTune 同一语义
      return {
        ok: false,
        reason: 'TUNABLE_CORE_NOT_AVAILABLE',
        detail: 'Core 尚无逐轨修音 / 复合能力；本壳不生成任何修音产物。',
      };
    } });
    const step = await h.orch.runSessionPhase(dir, session.phaseById('tune'));
    assert.strictEqual(step.ok, false);
    assert.strictEqual(step.reason, 'TUNABLE_CORE_NOT_AVAILABLE');
    assert.match(step.detail, /不生成任何修音产物/);
    assertNoFakeArtifacts(dir, { allow: ['stems' + path.sep, 'midi' + path.sep] });
  });
  await check('复检之前不会去点复检（缺 pair 时不会假装复检过）', async () => {
    const dir = makeCase({ report: true, stems: true, midi: true, roundtrip: true });
    const h = harness();
    const res = await h.orch.runCompletionSession(h.event, dir);
    // roundtrip 已通过 → 下一相位是 修音/复合（能力缺失 → 在跑之前就被拦下，复检更不会被执行）
    assert.strictEqual(res.reason, 'BLOCKED');
    assert.strictEqual(res.blocker.phase, 'tune');
    assert.ok(res.blocker.capabilities.includes('stem-tuning'));
    assert.deepStrictEqual(h.calls, [], 'no step may run behind a capability block');
    assert.strictEqual(pipeline.snapshot(dir).facts.rechecked, false,
      'and nothing may claim 复检 happened');
  });

  // ── 5. re-runs are safe ───────────────────────────────────────────────────────
  console.log('\n5. re-running is safe (no duplicated work, no duplicated artifacts)');
  await check('重复启动得到同样的结论，且不会多做一次已完成的工作', async () => {
    const dir = makeCase({ report: true, stems: true, midi: true });
    const h = harness();
    const a = await h.orch.runCompletionSession(h.event, dir);
    const b = await h.orch.runCompletionSession(h.event, dir);
    assert.strictEqual(a.reason, b.reason);
    assert.strictEqual(b.blocker.phase, 'reversible');
    assert.deepStrictEqual(h.calls, []);
    assertNoFakeArtifacts(dir, { allow: ['stems' + path.sep] });
  });

  // ── 8. the blocked-deep case: explicit switch, never automatic (Phase 2.1) ────
  //
  // 真实歌曲复现的死路：分轨 + MIDI 已经存在（深度资产齐备），但可逆性未验证 / 逐轨能力
  // 未就绪。旧门禁在这里三处全为假，用户拿不到任何候选。2026-10-04 人类裁定：提供**显式**
  // 快速完成入口，切换必须由人确认，且任何情况下都不自动降级。
  console.log('\n6. 深度受阻：先如实停住，再由人显式切换（绝不自动降级）');
  const WRITE_PAIR = (d) => writePair(d);

  await check('截图状态：停在真实深度阻断，不自动生成候选、不自动切换', async () => {
    const dir = makeCase({ report: true, stems: true, midi: true }); // 有资产、无 roundtrip
    const h = harness({ tune: async (d) => { WRITE_PAIR(d); return { ok: true }; } });
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.deepStrictEqual(h.calls, [], 'the deep route must stop before ④, not silently switch');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.state, 'BLOCKED');
    assert.strictEqual(res.blocker.kind, 'MISSING_CAPABILITY');
    assert.strictEqual(res.blocker.phase, 'reversible');
    assert.strictEqual(res.blocker.canSwitchToFast, true, 'the remedy must be visible');
    assert.strictEqual(res.fastSwitch.available, true);
    assert.strictEqual(res.mode, 'DEEP');
    assert.strictEqual(res.modeExecutable, false);
    assert.match(res.fastSwitch.note, /不会使用分轨进行音准或节奏修正/);
    // 没有自动切换、没有候选、深度资产原封不动
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'finish_mode.json')), false);
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'tuning')), false);
    assert.strictEqual(fs.existsSync(path.join(dir, 'stems', 'song__vocals.wav')), true);
    assert.strictEqual(fs.existsSync(path.join(dir, 'midi', 'song.mid')), true);
    // 原因逐条说清：可逆性未验证 + 深度能力未就绪
    assert.ok(res.fastSwitch.deepBlockers.includes('NO_ROUNDTRIP'));
    assert.ok(res.fastSwitch.deepBlockers.includes('DEEP_CORE_UNAVAILABLE'));
  });

  await check('人确认切换后：一对候选 + 复检 → REVIEW，且深度资产一个不丢', async () => {
    const dir = makeCase({ report: true, stems: true, midi: true });
    // 人的显式动作（UI 的两级确认之后才会发生）
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY', '测试：模拟人类确认');
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'tuning')), false,
      '切换本身不生成音频');

    const h = harness({
      tune: async (d) => { WRITE_PAIR(d); return { ok: true }; },
      recheck: async (d) => {
        const pairDir = fs.readdirSync(path.join(d, 'studio', 'tuning'))[0];
        fs.writeFileSync(path.join(d, 'studio', 'tuning', pairDir, 'recheck.json'), '{}');
        return { ok: true };
      },
    });
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.deepStrictEqual(h.calls, ['tune', 'recheck'], 'one render + one recheck');
    assert.strictEqual(res.state, 'REVIEW');
    assert.strictEqual(res.mode, 'FAST_STEREO_ONLY');
    assert.strictEqual(res.fast, true);
    const status = Object.fromEntries(res.phases.map((p) => [p.id, p.status]));
    assert.strictEqual(status.decompose, 'done', '已有资产显示为 done，不伪装成不存在');
    assert.strictEqual(status.structure, 'done');
    assert.strictEqual(status.reversible, 'skipped', '这条路不经过可逆性验证');
    assert.strictEqual(status.tune, 'done');
    // 资产与证据都还在
    assert.strictEqual(fs.existsSync(path.join(dir, 'stems', 'song__vocals.wav')), true);
    assert.strictEqual(fs.existsSync(path.join(dir, 'midi', 'song.mid')), true);
  });

  await check('重启 Desktop：从 finish_mode.json 恢复快速模式（不依赖内存）', async () => {
    const dir = makeCase({ report: true, stems: true, midi: true });
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY', '测试：模拟人类确认');
    const fresh = harness(); // 全新编排器实例 = 重启后的进程
    const view = fresh.orch.sessionView(dir);
    assert.strictEqual(view.mode, 'FAST_STEREO_ONLY', 'read back from disk');
    assert.strictEqual(view.fast, true);
    assert.strictEqual(view.nextPhase, 'tune');
    assert.strictEqual(view.fastSwitch.available, false, 'already on the fast route');
    assert.strictEqual(fresh.calls.length, 0, 'reading the view runs nothing');
  });

  await check('切换之后快速 Core 真实失败：仍然 BLOCKED，且可以真的重试', async () => {
    const dir = makeCase({ report: true, stems: true, midi: true });
    pipeline.recordFinishMode(dir, 'QUICK_STEREO_ONLY', '测试：模拟人类确认');
    let attempt = 0;
    const h = harness({
      tune: async (d) => {
        attempt += 1;
        if (attempt === 1) return { ok: false, reason: 'RENDER_PAIR_FAILED', detail: '第一次失败' };
        WRITE_PAIR(d);
        return { ok: true };
      },
      recheck: async (d) => {
        const pairDir = fs.readdirSync(path.join(d, 'studio', 'tuning'))[0];
        fs.writeFileSync(path.join(d, 'studio', 'tuning', pairDir, 'recheck.json'), '{}');
        return { ok: true };
      },
    });
    const first = await h.orch.runCompletionSession(h.event, dir);
    assert.strictEqual(first.state, 'BLOCKED');
    assert.strictEqual(first.blocker.kind, 'STEP_FAILED');
    assert.notStrictEqual(first.state, 'REVIEW');
    const second = await h.orch.runCompletionSession(h.event, dir);
    assert.strictEqual(attempt, 2);
    assert.strictEqual(second.state, 'REVIEW');
    // 深度资产在整个过程中没有被删掉
    assert.strictEqual(fs.existsSync(path.join(dir, 'stems', 'song__vocals.wav')), true);
  });

  // ── 9. nothing is invented for a world that has no artifacts ──────────────────
  console.log('\n7. nothing is invented for a world that has no artifacts');
  await check('空世界的投影是 READY（下一步=检测），不写任何文件', async () => {
    const dir = makeCase({ report: false });
    const before = fs.readdirSync(path.join(dir, 'studio')).sort();
    const h = harness();
    const view = h.orch.sessionView(dir);
    assert.strictEqual(view.state, 'READY');
    assert.strictEqual(view.nextPhase, 'detect');
    assert.strictEqual(view.stage, 'IMPORTED');
    assert.deepStrictEqual(fs.readdirSync(path.join(dir, 'studio')).sort(), before, 'no file may appear');
    assert.deepStrictEqual(h.calls, []);
  });

  // ── 7. the pure-stereo route: one pair, then recheck, then REVIEW ─────────────
  console.log('\n8. 快速完成（仅立体声）：一对候选 → 复检 → REVIEW');
  const QUICK = () => ({ schema: 'moodify.studio.finish-mode/0.1', mode: 'QUICK_STEREO_ONLY' });

  /** Write a complete pair the way Core does (A/B mixes + tuned slots + per-side evidence). */
  function writePair(dir, { complete = true } = {}) {
    const pairId = `tune_test_${String(++caseSeq).padStart(8, '0')}`;
    const pairDir = path.join(dir, 'studio', 'tuning', pairId);
    fs.mkdirSync(pairDir, { recursive: true });
    fs.writeFileSync(path.join(pairDir, 'pair.json'), JSON.stringify({
      schema: 'moodify.studio.tuning-pair/0.1', pair_id: pairId, mode: 'FAST_STEREO_ONLY',
      tiers: { A: 'conservative', B: 'full' }, created_at: new Date().toISOString(),
    }));
    for (const side of ['A', 'B']) {
      const sdir = path.join(pairDir, side);
      fs.mkdirSync(path.join(sdir, 'tuned'), { recursive: true });
      fs.writeFileSync(path.join(sdir, 'evidence.json'), '{}');
      fs.writeFileSync(path.join(sdir, 'plan.json'), '{}');
      fs.writeFileSync(path.join(sdir, 'tuned', 'source.wav'), 'RIFF');
      if (complete || side === 'A') fs.writeFileSync(path.join(sdir, 'mix.wav'), 'RIFF');
    }
    return pairId;
  }

  await check('显式选择快速完成之后：只跑 修音/复合 → 复检，绝不跑分轨与结构', async () => {
    const dir = makeCase({ report: true });
    fs.writeFileSync(path.join(dir, 'studio', 'finish_mode.json'), JSON.stringify(QUICK()));
    const h = harness({
      tune: async (d) => {
        writePair(d); // Core 在一次调用里产出完整一对
        return { ok: true, pairId: 'x' };
      },
      recheck: async (d) => {
        const pairDir = fs.readdirSync(path.join(d, 'studio', 'tuning'))[0];
        fs.writeFileSync(path.join(d, 'studio', 'tuning', pairDir, 'recheck.json'),
          JSON.stringify({ schema: 'moodify.studio.recheck/0.1', pair_id: pairDir, alignable: [] }));
        return { ok: true };
      },
    });
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.deepStrictEqual(h.calls, ['tune', 'recheck'], 'the pure-stereo route in order');
    assert.strictEqual(res.ok, true);
    assert.strictEqual(res.state, 'REVIEW');
    assert.strictEqual(res.stage, 'RECHECKED');
    const status = Object.fromEntries(res.phases.map((p) => [p.id, p.status]));
    assert.strictEqual(status.decompose, 'skipped');
    assert.strictEqual(status.structure, 'skipped');
    assert.strictEqual(status.reversible, 'skipped');
    assert.strictEqual(status.tune, 'done');
    assert.strictEqual(status.recheck, 'done');
    // 进入审听之后：没有替人做任何选择
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'tuning', 'decisions.jsonl')), false);
  });
  await check('未显式选择快速完成时，绝不自动走快速路径（分轨/结构会先被尝试）', async () => {
    const dir = makeCase({ report: true }); // 没有 finish_mode.json
    const h = harness({
      separate: async (d) => {
        fs.mkdirSync(path.join(d, 'stems'), { recursive: true });
        fs.writeFileSync(path.join(d, 'stems', 'song__vocals.wav'), 'RIFF');
        return { ok: true };
      },
      structure: async (d) => {
        fs.mkdirSync(path.join(d, 'midi'), { recursive: true });
        fs.writeFileSync(path.join(d, 'midi', 'song.mid'), 'MThd');
        return { ok: true };
      },
    });
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.deepStrictEqual(h.calls, ['separate', 'structure'], 'the deep chain, not the shortcut');
    assert.strictEqual(res.state, 'BLOCKED');
    assert.strictEqual(res.blocker.phase, 'reversible');
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'tuning')), false,
      'no pair may appear without the explicit opt-in');
  });
  await check('一对只生成一次：Core 失败（单边/整体）→ BLOCKED，且不进 REVIEW', async () => {
    const dir = makeCase({ report: true });
    fs.writeFileSync(path.join(dir, 'studio', 'finish_mode.json'), JSON.stringify(QUICK()));
    const h = harness({
      tune: async () => ({
        ok: false,
        reason: 'RENDER_PAIR_FAILED',
        detail: 'Core 未能生成两档候选：hard gate failed for B/mix.wav',
      }),
      recheck: async () => { throw new Error('复检不该在这种情况下被调用'); },
    });
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.deepStrictEqual(h.calls, ['tune'], 'no second attempt in one start');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'PHASE_FAILED');
    assert.strictEqual(res.phase, 'tune');
    assert.notStrictEqual(res.state, 'REVIEW');
    assert.strictEqual(res.blocker.kind, 'STEP_FAILED');
    assert.match(res.blocker.detail, /hard gate failed/);
    assert.match(res.message, /没有生成任何候选版本/);
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'tuning')), false,
      'a failed pair must leave no published pair');
    // 失败原因在重新投影后仍然可见，而且可以重试
    assert.strictEqual(h.orch.sessionView(dir).state, 'BLOCKED');
    assert.strictEqual(session.readFailure(dir).reason, 'RENDER_PAIR_FAILED');
  });
  await check('失败之后重试：真的再调一次 Core，成功后进入 REVIEW', async () => {
    const dir = makeCase({ report: true });
    fs.writeFileSync(path.join(dir, 'studio', 'finish_mode.json'), JSON.stringify(QUICK()));
    let attempt = 0;
    const h = harness({
      tune: async (d) => {
        attempt += 1;
        if (attempt === 1) return { ok: false, reason: 'RENDER_PAIR_FAILED', detail: '第一次失败' };
        writePair(d);
        return { ok: true };
      },
      recheck: async (d) => {
        const pairDir = fs.readdirSync(path.join(d, 'studio', 'tuning'))[0];
        fs.writeFileSync(path.join(d, 'studio', 'tuning', pairDir, 'recheck.json'), '{}');
        return { ok: true };
      },
    });
    const first = await h.orch.runCompletionSession(h.event, dir);
    assert.strictEqual(first.blocker.detail, '第一次失败');
    const second = await h.orch.runCompletionSession(h.event, dir);
    assert.strictEqual(attempt, 2, 'the retry must really call the step again');
    assert.strictEqual(second.state, 'REVIEW');
    assert.strictEqual(fs.existsSync(session.failurePath(dir)), false, 'the stale failure is cleared');
  });
  await check('半成品一对（只有 A 侧）不会进入 REVIEW', async () => {
    const dir = makeCase({ report: true });
    fs.writeFileSync(path.join(dir, 'studio', 'finish_mode.json'), JSON.stringify(QUICK()));
    const h = harness({
      tune: async (d) => { writePair(d, { complete: false }); return { ok: true }; },
    });
    const res = await h.orch.runCompletionSession(h.event, dir);
    assert.notStrictEqual(res.state, 'REVIEW', 'one side is a半成品, not a candidate pair');
    assert.strictEqual(res.state, 'BLOCKED', 'the flow stops and says so');
    assert.strictEqual(res.reason, 'NO_PROGRESS');
    assert.match(res.blocker.detail, /仍没有它应留下的产物|没有前进|报告成功/);
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
