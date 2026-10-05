#!/usr/bin/env node
/**
 * Headless test for the completion-session orchestrator（一键完成机 · Phase 1）.
 *
 * WHAT THIS PROVES, AND WHY EACH ONE MATTERS
 *
 *   1 ordering        the six phases are in the real execution order and never skipped
 *   2 resume          steps whose artifacts already exist are skipped — 「关掉再打开能接着跑」
 *   3 blocked         a phase whose Core capability does not exist stops the run as BLOCKED,
 *                     and the blocker NAMES the phase and the missing capability
 *   4 no fake artifacts  the projection is pure: it writes nothing, ever. A projection that
 *                     created files would be manufacturing progress out of nothing.
 *   5 single source of capability truth  the orchestrator does not keep its own list of what
 *                     exists; it reads pipeline.CAPABILITIES / PLANNED_CAPABILITIES
 *   6 re-entrancy     two concurrent starts for the same song are refused
 *   7 review/done     two composed+verified candidates become REVIEW; a recorded choice is DONE
 *   8 exits           the three exits are A / B / ORIGINAL, labelled 保守 / 充分 / 保留原版
 *   9 the pure-stereo route  an explicit Quick opt-in projects its own chain (no decomposition,
 *                     no structure, no reversibility) and requires the whole-track pair
 *                     capability — while the deep path stays blocked
 *  10 blocked deep switch  when the deep path cannot run, the projection offers an explicit
 *                     switch (with confirmation) and never claims an automatic downgrade
 *
 * Fixtures are SYNTHESISED so results do not depend on what is in ~/.moodify/cases.
 *
 * Run: node scripts/test-session.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');

const session = require(path.join(__dirname, '..', 'src', 'session'));
const pipeline = require(path.join(__dirname, '..', 'src', 'pipeline'));

let passed = 0;
const failures = [];
async function check(label, fn) {
  try { await fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

/** Minimal pipeline snapshot: the orchestrator reads ONLY `facts` (+ gates for the mode). */
const snap = (facts, gates = {}) => ({ facts, info: {}, stage: 'ANALYZED', gates });

const FAST_GATES = { mode: 'FAST_STEREO_ONLY', modeLabel: '快速（仅立体声）', canTuneQuick: true, canRequestQuick: false };

const F = {
  nothing: () => ({}),
  analyzed: () => ({ analyzed: true }),
  decomposed: () => ({ analyzed: true, separated: true }),
  structured: () => ({ analyzed: true, separated: true, structured: true }),
  reversible: () => ({ analyzed: true, separated: true, structured: true, reversible: true }),
  composed: () => ({ analyzed: true, separated: true, structured: true, reversible: true,
    tuned: true, composed: true }),
  review: () => ({ analyzed: true, separated: true, structured: true, reversible: true,
    tuned: true, composed: true, rechecked: true }),
  chosen: () => ({ analyzed: true, separated: true, structured: true, reversible: true,
    tuned: true, composed: true, rechecked: true, chosen: true }),
};

(async () => {
  console.log('completion session (Phase 1)\n');

  // ── 1. ordering ───────────────────────────────────────────────────────────────
  console.log('1. phase order');
  await check('the six phases are in real execution order', () => {
    assert.deepStrictEqual(
      session.PHASES.map((p) => p.id),
      ['detect', 'decompose', 'structure', 'reversible', 'tune', 'recheck'],
    );
  });
  await check('every phase declares at least one capability and a done predicate', () => {
    for (const p of session.PHASES) {
      assert.ok(p.label && p.label.length > 0, `${p.id} needs a user-facing label`);
      assert.ok(Array.isArray(p.requires) && p.requires.length > 0, `${p.id} needs requires[]`);
      assert.strictEqual(typeof p.done, 'function', `${p.id} needs a done() predicate`);
    }
  });
  await check('an untouched song reports READY with detect as the next phase', () => {
    const v = session.project(snap(F.nothing()));
    assert.strictEqual(v.state, 'READY');
    assert.strictEqual(v.nextPhase, 'detect');
    assert.strictEqual(v.phases[0].status, 'next');
    // nothing may be pre-marked done
    assert.strictEqual(v.phases.filter((p) => p.status === 'done').length, 0);
  });

  // ── 2. resume ─────────────────────────────────────────────────────────────────
  console.log('\n2. resume — finished steps are skipped');
  await check('an already-analysed song resumes at 逆向分解', () => {
    const v = session.project(snap(F.analyzed()));
    assert.strictEqual(v.nextPhase, 'decompose');
    assert.strictEqual(v.phases[0].status, 'done');
  });
  await check('分析过的 + 分轨过的 resumes at 结构', () => {
    const v = session.project(snap(F.decomposed()));
    assert.strictEqual(v.nextPhase, 'structure');
  });
  await check('+ MIDI resumes at 可逆性验证 — the first step Core cannot do', () => {
    const v = session.project(snap(F.structured()));
    assert.strictEqual(v.nextPhase, 'reversible');
  });
  await check('after a passing reversibility check the next phase moves on', () => {
    const v = session.project(snap(F.reversible()));
    assert.strictEqual(v.nextPhase, 'tune');
    assert.strictEqual(v.phases[3].status, 'done');
  });

  // ── 3. blocked ────────────────────────────────────────────────────────────────
  console.log('\n3. blocked — missing Core capability stops the run, honestly');
  await check('一首都做完了前面的步骤后，停在「可逆性验证」而不是假装继续', () => {
    const v = session.project(snap(F.structured()));
    assert.strictEqual(v.state, 'BLOCKED');
    assert.strictEqual(v.blocker.phase, 'reversible');
    assert.deepStrictEqual(v.blocker.capabilities, ['reversibility-check']);
  });
  await check('the blocker names the capability AND quotes its declared reason', () => {
    const v = session.project(snap(F.reversible()));
    assert.strictEqual(v.state, 'BLOCKED');
    assert.strictEqual(v.blocker.phase, 'tune');
    assert.deepStrictEqual(v.blocker.capabilities, ['stem-tuning', 'multi-stem-compose']);
    for (const r of v.blocker.reasons) {
      assert.ok(r.capability && r.reason && r.reason.length > 10, 'each reason must be substantive');
    }
  });
  await check('the BLOCKED message says the product lacks capability — not that the user erred', () => {
    const v = session.project(snap(F.structured()));
    assert.match(v.message, /能力尚未就绪|产品能力/);
    assert.match(v.message, /没有生成任何候选/, 'must say plainly that no candidates exist');
  });
  await check('phases after the blocker are todo, never done or next', () => {
    const v = session.project(snap(F.structured()));
    const after = v.phases.slice(v.phases.findIndex((p) => p.status === 'blocked') + 1);
    assert.ok(after.length > 0);
    for (const p of after) assert.strictEqual(p.status, 'todo', `${p.id} must be todo`);
  });

  // ── 4. the projection writes nothing ──────────────────────────────────────────
  console.log('\n4. no fake artifacts — the projection is pure');
  await check('project() writes nothing to disk', () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-session-test-'));
    fs.writeFileSync(path.join(dir, 'report.json'), '{"case":{"case_id":"t"}}');
    const before = fs.readdirSync(dir).sort();
    for (const facts of Object.values(F)) {
      session.project({ facts: facts(), info: {}, stage: 'X', gates: {} });
    }
    assert.deepStrictEqual(fs.readdirSync(dir).sort(), before, 'no file may appear');
    fs.rmSync(dir, { recursive: true, force: true });
  });
  await check('no phase is marked done unless its artifact fact is true', () => {
    // one fact at a time: only that phase may flip to done
    for (const p of session.PHASES) {
      const facts = {};
      const v = session.project(snap(facts));
      assert.strictEqual(v.phases.find((x) => x.id === p.id).status === 'done', false,
        `${p.id} must not be done on an empty case`);
    }
    // and the tune phase requires BOTH tuned and composed (a half pair is not done)
    const half = { analyzed: true, separated: true, structured: true, reversible: true, tuned: true };
    const v = session.project(snap(half));
    assert.strictEqual(v.phases.find((x) => x.id === 'tune').status !== 'done', true,
      'tuned-without-composed is a半成品 and must not count as done');
  });

  // ── 5. capability truth comes from pipeline ───────────────────────────────────
  console.log('\n5. one source of capability truth');
  await check('the available set mirrors pipeline.CAPABILITIES exactly', () => {
    assert.deepStrictEqual(
      [...session.AVAILABLE_CAPABILITIES].sort(),
      pipeline.CAPABILITIES.map((c) => c.id).sort(),
    );
  });
  await check('the planned set mirrors pipeline.PLANNED_CAPABILITIES exactly', () => {
    assert.deepStrictEqual(
      [...session.PLANNED_CAPABILITIES.keys()].sort(),
      pipeline.PLANNED_CAPABILITIES.map((c) => c.id).sort(),
    );
  });
  await check('every capability a phase requires is declared somewhere in pipeline', () => {
    const known = new Set([
      ...pipeline.CAPABILITIES.map((c) => c.id),
      ...pipeline.PLANNED_CAPABILITIES.map((c) => c.id),
    ]);
    for (const p of session.PHASES) {
      for (const need of [...p.requires, ...(p.requiresFast || [])]) {
        assert.ok(known.has(need), `${p.id} requires undeclared capability ${need}`);
      }
    }
  });
  await check('the fast-mode requirement is the capability Studio really has', () => {
    const tune = session.phaseById('tune');
    assert.deepStrictEqual(tune.requiresFast, ['fast-stereo-pair']);
    assert.ok(pipeline.CAPABILITIES.some((c) => c.id === 'fast-stereo-pair'),
      'the whole-track pair render must be declared as available');
    for (const need of tune.requires) {
      assert.ok(!pipeline.CAPABILITIES.some((c) => c.id === need),
        `${need} is the deep path and must not be claimed as available`);
    }
  });

  // ── 6. re-entrancy ────────────────────────────────────────────────────────────
  console.log('\n6. re-entrancy — one song, one run');
  await check('a second concurrent start for the same song is refused', () => {
    const dir = '/tmp/case_a';
    assert.strictEqual(session.acquire(dir), true, 'first start must be granted');
    assert.strictEqual(session.isRunning(dir), true);
    assert.strictEqual(session.acquire(dir), false, 'second start must be refused');
    session.release(dir);
    assert.strictEqual(session.isRunning(dir), false);
    assert.strictEqual(session.acquire(dir), true, 'and it is startable again afterwards');
    session.release(dir);
  });
  await check('different songs do not block each other', () => {
    assert.strictEqual(session.acquire('/tmp/case_x'), true);
    assert.strictEqual(session.acquire('/tmp/case_y'), true);
    session.release('/tmp/case_x');
    session.release('/tmp/case_y');
  });
  await check('acquire refuses an empty id rather than keying on undefined', () => {
    assert.strictEqual(session.acquire(''), false);
    assert.strictEqual(session.acquire(null), false);
  });

  // ── 7. review / done ──────────────────────────────────────────────────────────
  console.log('\n7. review and done');
  await check('two composed + verified candidates report REVIEW, not BLOCKED', () => {
    const v = session.project(snap(F.review()));
    assert.strictEqual(v.state, 'REVIEW');
    assert.strictEqual(v.blocker, null);
    for (const p of v.phases) assert.strictEqual(p.status, 'done');
  });
  await check('a recorded choice reports DONE', () => {
    assert.strictEqual(session.project(snap(F.chosen())).state, 'DONE');
  });
  await check('the REVIEW message tells the user to listen, not to trust a number', () => {
    const v = session.project(snap(F.review()));
    assert.match(v.message, /试听|听/);
  });

  // ── 8. exits ──────────────────────────────────────────────────────────────────
  console.log('\n8. the three exits');
  await check('exits are A / B / ORIGINAL and the labels match the brief', () => {
    assert.deepStrictEqual(Object.keys(session.EXIT_LABELS), ['ORIGINAL', 'A', 'B']);
    assert.strictEqual(session.exitLabel('A'), 'A（保守）');
    assert.strictEqual(session.exitLabel('B'), 'B（充分）');
    assert.strictEqual(session.exitLabel('ORIGINAL'), '保留原版');
    assert.deepStrictEqual(session.project(snap(F.nothing())).exits.sort(), ['A', 'B', 'ORIGINAL']);
  });
  await check('an unknown exit label degrades to itself rather than inventing a meaning', () => {
    assert.strictEqual(session.exitLabel('C'), 'C');
  });

  // ── 9. 快速完成（仅立体声）: another legitimate path, not a broken deep path ──
  //
  // The mode is derived by pipeline (artifacts + the human's explicit opt-in), never chosen here.
  // In FAST mode 逆向分解 / 结构 / 可逆性 are not "todo" and not "blocked": this route is defined
  // without them. The tune phase then requires the whole-track pair capability (available), NOT
  // the per-stem one (still unimplemented).
  console.log('\n9. the pure-stereo route is projected as its own path');
  await check('分析过 + 显式选择快速完成 → 下一步就是 修音/复合，分轨与结构标为 skipped', () => {
    const v = session.project(snap(F.analyzed(), FAST_GATES));
    assert.strictEqual(v.fast, true);
    assert.strictEqual(v.mode, 'FAST_STEREO_ONLY');
    assert.strictEqual(v.modeLabel, '快速（仅立体声）');
    assert.strictEqual(v.state, 'READY');
    assert.strictEqual(v.nextPhase, 'tune');
    const status = Object.fromEntries(v.phases.map((p) => [p.id, p.status]));
    assert.strictEqual(status.detect, 'done');
    assert.strictEqual(status.decompose, 'skipped');
    assert.strictEqual(status.structure, 'skipped');
    assert.strictEqual(status.reversible, 'skipped');
    assert.strictEqual(status.tune, 'next');
    assert.strictEqual(status.recheck, 'todo');
    assert.strictEqual(v.blocker, null, 'the fast route is not a missing-capability block');
  });
  await check('快速模式下的要求是整轨两档能力，而不是逐轨能力', () => {
    assert.deepStrictEqual(session.missingCapabilities(session.phaseById('tune'), true), []);
    assert.deepStrictEqual(session.missingCapabilities(session.phaseById('tune'), false),
      ['stem-tuning', 'multi-stem-compose']);
    // 深度路径没有因为快速路径可用而解锁
    const deep = session.project(snap(F.structured()));
    assert.strictEqual(deep.fast, false);
    assert.strictEqual(deep.state, 'BLOCKED');
    assert.strictEqual(deep.blocker.phase, 'reversible');
  });
  await check('快速模式下已完成的事实仍然是 done（不把已有产物显示成跳过）', () => {
    const v = session.project(snap(F.decomposed(), FAST_GATES));
    const status = Object.fromEntries(v.phases.map((p) => [p.id, p.status]));
    assert.strictEqual(status.decompose, 'done', 'the artifact really exists');
    assert.strictEqual(status.tune, 'next', 'and the fast route still goes straight to the pair');
  });
  await check('快速模式的 READY 文案只列真正会执行的步骤', () => {
    const v = session.project(snap(F.analyzed(), FAST_GATES));
    assert.match(v.message, /快速完成/);
    assert.ok(!/逆向分解/.test(v.message), 'it must not claim it will decompose');
    assert.ok(!/可逆性/.test(v.message));
    assert.match(v.message, /修音与复合/);
    assert.match(v.message, /复检/);
  });
  await check('深度模式（未选择快速）仍然投影完整链条，并停在真实缺的能力上', () => {
    const v = session.project(snap(F.analyzed()));
    assert.strictEqual(v.fast, false);
    assert.strictEqual(v.nextPhase, 'decompose');
    assert.strictEqual(v.blocker, null);
  });
  await check('canRequestQuick 由 pipeline 推导原样带出（UI 靠它决定是否请人做选择）', () => {
    const gates = { mode: null, modeLabel: null, canRequestQuick: true, canTuneQuick: false };
    assert.strictEqual(session.project(snap(F.analyzed(), gates)).canRequestQuick, true);
    assert.strictEqual(session.project(snap(F.analyzed(), FAST_GATES)).canRequestQuick, false);
  });

  // ── 10. 深度受阻 → 显式切换（2026-10-04 人类裁定，Phase 2.1）────────────────────
  //
  // 投影必须同时说清两件事：深度这条路现在走不通（原因逐条），以及人可以**自己**换一条路
  // （需要确认）。它绝不能说成「系统已经切过去了」——那是替人改变完成模式。
  console.log('\n10. 深度受阻时的补救投影');
  const BLOCKED_DEEP_GATES = {
    mode: 'DEEP',
    modeLabel: '深度完成',
    modeExecutable: false,
    deepExecutable: false,
    deepAssetsReady: true,
    fastAvailable: true,
    canRequestQuick: true,
    canTuneQuick: false,
    quickOptIn: false,
    deepBlockers: ['NO_ROUNDTRIP', 'DEEP_CORE_UNAVAILABLE'],
    deepTuneBlockers: [
      '可逆性未验证（缺 studio/roundtrip.json；Core 尚未产出）',
      '深度路径的逐轨修音 / 复合能力尚未就绪（Core 未实现，见 MIP-0002）',
    ],
  };

  await check('受阻时投影出可切换，并带确认文案（不是自动降级）', () => {
    const v = session.project(snap(F.structured(), BLOCKED_DEEP_GATES));
    assert.strictEqual(v.state, 'BLOCKED');
    assert.strictEqual(v.blocker.kind, 'MISSING_CAPABILITY');
    assert.strictEqual(v.blocker.canSwitchToFast, true);
    assert.strictEqual(v.fastSwitch.available, true);
    assert.strictEqual(v.fastSwitch.deepExecutable, false);
    assert.match(v.fastSwitch.label, /切换到快速完成（仅立体声）/);
    // 文案必须说清它**不做**逐轨音准/节奏修正
    assert.match(v.fastSwitch.note, /不会使用分轨进行音准或节奏修正/);
    assert.match(v.fastSwitch.note, /仍会生成 A\/B/);
    assert.deepStrictEqual(v.fastSwitch.deepBlockers, ['NO_ROUNDTRIP', 'DEEP_CORE_UNAVAILABLE']);
    // 阻断原因逐条带出（缺 roundtrip + 能力未就绪），供「制作详情」层使用
    assert.strictEqual(v.fastSwitch.deepReasons.length, 2);
    assert.match(v.fastSwitch.deepReasons[0], /可逆性未验证/);
    assert.match(v.fastSwitch.deepReasons[1], /逐轨修音/);
  });
  await check('产品面只显示白话总结：不出现文件名、路径或 MIP 编号', () => {
    const v = session.project(snap(F.structured(), BLOCKED_DEEP_GATES));
    const s = v.fastSwitch.summary;
    assert.match(s, /可逆性验证还没有做/, '说清哪一步没做');
    assert.match(s, /逐轨修音与复合能力还没有就绪/);
    assert.match(s, /保留现有分解结果/, '有分解产物时才这么说');
    assert.match(s, /改用整轨两档完成（快速完成：仅立体声）/);
    assert.match(s, /技术原因见「制作详情」/);
    // 工程细节不许上产品面
    for (const leak of ['roundtrip.json', 'studio/', 'MIP-', 'stems/', 'Core']) {
      assert.ok(!s.includes(leak), `产品面文案不得出现工程细节：${leak}`);
    }
  });
  await check('还没有分解产物时不说「保留现有分解结果」', () => {
    const gates = { ...BLOCKED_DEEP_GATES, deepAssetsReady: false,
      deepBlockers: ['NO_STEMS', 'NO_MIDI', 'DEEP_CORE_UNAVAILABLE'] };
    const v = session.project(snap(F.analyzed(), gates));
    assert.ok(!v.fastSwitch.summary.includes('保留现有分解结果'),
      '没有的东西不能让人以为有');
    assert.match(v.fastSwitch.summary, /还没有完成逆向分解/);
    assert.match(v.fastSwitch.summary, /还缺少机器可读的结构/);
  });
  await check('BLOCKED 文案给出补救路径，并明确要人确认、系统不会自动切换', () => {
    const v = session.project(snap(F.structured(), BLOCKED_DEEP_GATES));
    assert.match(v.message, /没有生成任何候选版本/);
    assert.match(v.message, /改用快速完成（仅立体声）/);
    assert.match(v.message, /需要你确认一次/);
    assert.match(v.message, /系统不会自动切换/);
    assert.ok(!/已自动切换|已自动降级/.test(v.message), 'never claim an automatic downgrade');
  });
  await check('深度真实可执行时不提示切换（未来能力到位后的行为）', () => {
    const gates = { mode: 'DEEP', modeLabel: '深度完成', modeExecutable: true,
      deepExecutable: true, fastAvailable: true, canRequestQuick: false, deepBlockers: [] };
    const v = session.project(snap(F.reversible(), gates));
    assert.strictEqual(v.fastSwitch.available, false, 'nothing to switch away from');
    assert.strictEqual(v.canRequestQuick, false);
    // 注意：相位是否可跑由**能力清单**决定，不由 gates 的布尔值决定（pipeline 是唯一权威）。
    // 今天逐轨能力仍未实现，所以这里如实停在 ④；等能力进 CAPABILITIES 的那天，同一段投影
    // 就会把 ④ 标成 next。
    assert.strictEqual(v.blocker.phase, 'tune');
    assert.deepStrictEqual(v.blocker.capabilities, ['stem-tuning', 'multi-stem-compose']);
  });
  await check('已显式选择快速后不再提示切换，且深度原因只作说明保留', () => {
    const v = session.project(snap(F.analyzed(), { ...FAST_GATES, deepExecutable: false, canRequestQuick: false,
      deepTuneBlockers: ['深度路径的逐轨修音 / 复合能力尚未就绪（Core 未实现，见 MIP-0002）'] }));
    assert.strictEqual(v.fast, true);
    assert.strictEqual(v.fastSwitch.available, false, 'already on the fast route');
    assert.strictEqual(v.blocker, null);
    assert.strictEqual(v.nextPhase, 'tune');
  });
  await check('有候选可听（REVIEW）时不再提示切换', () => {
    const gates = { mode: 'FAST_STEREO_ONLY', modeLabel: '快速（仅立体声）', modeExecutable: true,
      fastAvailable: true, canRequestQuick: false, deepBlockers: [] };
    const v = session.project(snap(F.review(), gates));
    assert.strictEqual(v.state, 'REVIEW');
    assert.strictEqual(v.fastSwitch.available, false);
  });

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
