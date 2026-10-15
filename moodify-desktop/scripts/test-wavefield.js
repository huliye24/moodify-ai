#!/usr/bin/env node
/**
 * Headless tests for the Wave Field local lane（实验通道 · Wave Field Local v0）.
 *
 * WHAT THIS PROVES, AND WHY EACH ONE MATTERS
 *
 *   1 flag off        when MOODIFY_WAVEFIELD_V0 is not '1' nothing is exposed: the
 *                     rail button stays hidden and every IPC handler is gated by the
 *                     same check. An unfinished experiment must not leak into the
 *                     released path — this is the test that pins that.
 *   2 flag on         with the flag on, disk-derived state is exposed: ORIGINAL + A/B/C
 *                     availability, the exact FieldSpec per candidate, the hearing
 *                     numbers and the recorded choice.
 *   3 runner failure  a failing runner must surface its own code/detail, never a silent
 *                     empty state. A crash-to-launch is reported as RUNNER_UNAVAILABLE.
 *   4 missing artifact a missing candidate is VISIBLE (blockers + exists:false + a
 *                     disabled choice), not quietly treated as unavailable-but-fine.
 *   5 valid choices   only ORIGINAL / A / B / C and the three known roles may be chosen;
 *                     invalid input is refused before a python process is spawned.
 *   6 export gating   export is refused while no decision exists — you cannot export
 *                     something that was never chosen.
 *   7 manifest        after a choice, an export manifest on disk is surfaced with the
 *                     field, both hashes and the decision.
 *   8 playback        ONE playback authority: switching candidate stops the previous
 *                     source. Two simultaneous sources must be impossible.
 *
 * Fixtures are SYNTHESISED into a temp dir — results never depend on what is in
 * ~/.moodify/cases, and no audio is committed.
 *
 * Run: node scripts/test-wavefield.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');

const wavefield = require(path.join(__dirname, '..', 'src', 'wavefield.js'));
const playerModule = require(path.join(__dirname, '..', 'renderer', 'wavefield-player.js'));

let passed = 0;
const failures = [];
async function check(label, fn) {
  try { await fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

// ——— fixtures ————————————————————————————————————————————————————————————

const roots = [];
function makeCase(label) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'wf-' + label + '-'));
  roots.push(dir);
  fs.writeFileSync(path.join(dir, 'case.json'), JSON.stringify({ case_id: path.basename(dir) }));
  fs.writeFileSync(path.join(dir, 'source.wav'), Buffer.from('RIFF-fake-source'));
  return dir;
}

function fieldRecord(candidateId, roomSize) {
  return {
    schema: 'moodify.wavefield/0.1',
    field_id: 'field_' + candidateId,
    engine: 'algorithmic_room_v0',
    parameters: { room_size: roomSize, damping: 0.5, wet: 0.16, width: 0.86 },
  };
}

function snapshot(candidateId, opts = {}) {
  const reference = opts.reference === true;
  return {
    schema: 'moodify.hear/0.1',
    candidate_id: candidateId,
    field_id: reference ? null : 'field_' + candidateId,
    is_reference: reference,
    metrics: {
      integrated_lufs: { value: opts.lufs === undefined ? -14.0 : opts.lufs, unit: 'LUFS' },
      true_peak_dbfs: { value: -1.2, unit: 'dBFS' },
      crest_factor_db: { value: 11.4, unit: 'dB' },
      stereo_correlation: { value: 0.42, unit: 'ratio' },
      stereo_width_proxy: { value: 0.58, unit: 'ratio' },
      side_to_mid_db: { value: -6.1, unit: 'dB' },
      negative_correlation_ratio: { value: 0.0, unit: 'ratio' },
      phase_risk_ratio: { value: 0.01, unit: 'ratio' },
      duration: { value: 6.0, unit: 's' },
      sample_rate: { value: 48000, unit: 'Hz' },
      channels: { value: 2, unit: 'ch' },
    },
    source_comparison: reference ? null : {
      reference: 'ORIGINAL',
      normalization_gain_db: 0.4,
      normalization_valid: true,
      normalization_method: 'gain-to-before-LUFS',
      audition_correction_db: opts.correction === undefined ? 0.4 : opts.correction,
      metric_delta: {},
    },
    judge: reference ? { technical_status: 'REFERENCE', blocking_flags: [], warnings: [] } : {
      technical_status: opts.blocked ? 'BLOCKED' : 'SAFE_TO_LISTEN',
      blocking_flags: opts.blocked ? ['STEREO_PHASE_RISK_INCREASED'] : [],
      warnings: opts.warned ? ['EXCESSIVE_LOUDNESS_INCREASE'] : [],
    },
  };
}

/** Build a full lane on disk. `omit` lists candidates whose artifacts are left out. */
function writeLane(caseDir, opts = {}) {
  const omit = opts.omit || [];
  const root = wavefield.wavefieldDir(caseDir);
  fs.mkdirSync(path.join(root, 'candidates'), { recursive: true });
  fs.mkdirSync(path.join(root, 'fields'), { recursive: true });
  fs.mkdirSync(path.join(root, 'renders'), { recursive: true });
  fs.mkdirSync(path.join(root, 'hearing'), { recursive: true });
  fs.mkdirSync(path.join(root, 'export'), { recursive: true });

  fs.writeFileSync(path.join(root, 'session.json'), JSON.stringify({
    schema: 'moodify.wavefield.session/0.1',
    case_id: path.basename(caseDir),
    source_path: path.join(caseDir, 'source.wav'),
    source_sha256: 'a'.repeat(64),
    policy_id: 'FIELD_SEARCH_POLICY_V0',
    calibration_status: 'UNCALIBRATED_ENGINEERING_DEFAULT',
  }));
  fs.writeFileSync(path.join(root, 'search.json'), JSON.stringify({
    schema: 'moodify.wavefield.search/0.1',
    policy_id: 'FIELD_SEARCH_POLICY_V0',
    calibration_status: 'UNCALIBRATED_ENGINEERING_DEFAULT',
    probes: ['A', 'B', 'C'].map((id) => ({
      candidate_id: id,
      field_id: 'field_' + id,
      intent: id === 'A' ? 'smaller / more direct field'
        : (id === 'B' ? 'medium field' : 'larger / more open field'),
      parameters: fieldRecord(id, id === 'A' ? 0.22 : (id === 'B' ? 0.5 : 0.8)).parameters,
    })),
  }));
  fs.writeFileSync(path.join(root, 'decisions.jsonl'), (opts.decisions || [])
    .map((row) => JSON.stringify(row)).join('\n') + (opts.decisions && opts.decisions.length ? '\n' : ''));

  for (const id of ['A', 'B', 'C']) {
    if (omit.includes(id)) continue;
    fs.writeFileSync(path.join(root, 'candidates', id + '.wav'), Buffer.from('RIFF-fake-' + id));
    fs.writeFileSync(path.join(root, 'fields', id + '.json'),
      JSON.stringify(fieldRecord(id, id === 'A' ? 0.22 : (id === 'B' ? 0.5 : 0.8))));
    fs.writeFileSync(path.join(root, 'renders', id + '.json'), JSON.stringify({
      output_path: path.join(root, 'candidates', id + '.wav'),
      output_sha256: 'b'.repeat(64),
    }));
    fs.writeFileSync(path.join(root, 'hearing', id + '.json'),
      JSON.stringify(snapshot(id, id === 'C' ? { warned: true } : {})));
  }
  if (!omit.includes('ORIGINAL')) {
    fs.writeFileSync(path.join(root, 'hearing', 'ORIGINAL.json'), JSON.stringify(snapshot('ORIGINAL', { reference: true })));
  }
  if (opts.manifest) {
    fs.writeFileSync(path.join(root, 'export', 'manifest.json'), JSON.stringify(opts.manifest));
  }
  return root;
}

function fakeRun(result, captured = []) {
  const run = async (args, input) => {
    captured.push({ args, input });
    if (typeof result === 'function') return result(args, input);
    return result;
  };
  run.captured = captured;
  return run;
}

const OK_RUN = { code: 0, stdout: JSON.stringify({ ok: true, action: 'choose', created: true }) + '\n', stderr: '' };

// ——— 1) feature flag ————————————————————————————————————————————————————

(async () => {
  console.log('wavefield — feature flag');

  await check('未设置时关闭', () => {
    assert.strictEqual(wavefield.enabled({}), false);
    assert.strictEqual(wavefield.enabled({ MOODIFY_WAVEFIELD_V0: '' }), false);
    assert.strictEqual(wavefield.enabled({ MOODIFY_WAVEFIELD_V0: 'true' }), false);
    assert.strictEqual(wavefield.enabled({ MOODIFY_WAVEFIELD_V0: '0' }), false);
  });

  await check('设为 1 时才开启', () => {
    assert.strictEqual(wavefield.enabled({ MOODIFY_WAVEFIELD_V0: '1' }), true);
    assert.strictEqual(wavefield.enabled({ MOODIFY_WAVEFIELD_V0: ' 1 ' }), true);
  });

  await check('关闭时入口默认隐藏（index.html 里 rail 按钮带 hidden）', () => {
    const html = fs.readFileSync(path.join(__dirname, '..', 'renderer', 'index.html'), 'utf8');
    const button = /<button id="rail-wavefield"[^>]*hidden/.exec(html);
    assert.ok(button, '波场 rail 按钮必须以 hidden 起始');
  });

  await check('每个波场 IPC 入口都被同一个开关挡住', () => {
    const main = fs.readFileSync(path.join(__dirname, '..', 'src', 'main.js'), 'utf8');
    const block = /function registerWaveFieldIpc\(\)([\s\S]*?)\n}\n/.exec(main);
    assert.ok(block, 'main.js 必须有 registerWaveFieldIpc');
    const gates = (block[1].match(/wavefield\.enabled\(\)/g) || []).length;
    const handles = (block[1].match(/ipcMain\.handle\('wavefield:/g) || []).length;
    assert.strictEqual(handles, 5, '应注册 5 个波场 channel，实到 ' + handles);
    assert.ok(gates >= handles, '每个 channel 都必须先过开关，实到 ' + gates + '/' + handles);
    assert.ok(block[1].includes('wavefieldDisabled()'), '未启用时要返回 DISABLED');
  });

  await check('关闭时状态不暴露（readState 只读盘，从不写盘）', () => {
    const dir = makeCase('flagoff');
    const before = fs.readdirSync(dir).sort();
    const state = wavefield.readState(dir);
    assert.strictEqual(state.present, false);
    assert.deepStrictEqual(state.blockers, ['NO_WAVEFIELD_SESSION']);
    assert.deepStrictEqual(fs.readdirSync(dir).sort(), before, 'readState 不得新建任何文件');
    assert.strictEqual(fs.existsSync(wavefield.wavefieldDir(dir)), false);
  });

  // ——— 2) flag on ——————————————————————————————————————————————————————

  console.log('wavefield — state exposure');

  await check('开启后暴露 ORIGINAL/A/B/C 的可用性、场与听测', () => {
    const dir = makeCase('on');
    writeLane(dir);
    const state = wavefield.readState(dir);
    assert.strictEqual(state.present, true);
    assert.deepStrictEqual(Object.keys(state.candidates), ['ORIGINAL', 'A', 'B', 'C']);
    assert.ok(state.candidates.A.exists);
    assert.deepStrictEqual(state.fields.B.parameters,
      { room_size: 0.5, damping: 0.5, wet: 0.16, width: 0.86 });
    assert.strictEqual(state.summary.A.integrated_lufs, -14.0);
    assert.strictEqual(state.summary.ORIGINAL.technical_status, 'REFERENCE');
    assert.strictEqual(state.summary.C.warnings.length, 1);
    assert.strictEqual(state.summary.A.audition_correction_db, 0.4);
    assert.strictEqual(state.blockers[0], 'NOT_CHOSEN');
    assert.deepStrictEqual(state.choices, ['ORIGINAL', 'A', 'B', 'C']);
  });

  await check('ORIGINAL 指向源音频，通道不复刻它', () => {
    const dir = makeCase('original');
    writeLane(dir);
    const state = wavefield.readState(dir);
    assert.strictEqual(state.candidates.ORIGINAL.path, path.join(dir, 'source.wav'));
    assert.strictEqual(wavefield.candidateAudioPath(dir, 'ORIGINAL'), null);
    const wavs = fs.readdirSync(path.join(wavefield.wavefieldDir(dir), 'candidates'));
    assert.deepStrictEqual(wavs.sort(), ['A.wav', 'B.wav', 'C.wav']);
  });

  await check('已记录的选择被读回（账本只追加）', () => {
    const dir = makeCase('decided');
    writeLane(dir, {
      decisions: [
        { schema: 'moodify.wavefield.decision/0.1', request_id: 'r1', kept: 'A', role: 'creator' },
        { schema: 'moodify.wavefield.decision/0.1', request_id: 'r2', kept: 'C', role: 'pro' },
      ],
      manifest: { kept: 'C', export_mode: 'RENDERED_FIELD', chosen_audio_sha256: 'c'.repeat(64) },
    });
    const state = wavefield.readState(dir);
    assert.strictEqual(state.decisions.length, 2);
    assert.strictEqual(state.chosen.kept, 'C');
    assert.strictEqual(state.export.kept, 'C');
    assert.deepStrictEqual(state.blockers, [], '已选定且产物齐备时不应有阻断，实到 ' + JSON.stringify(state.blockers));
  });

  await check('坏行不影响账本的其余记录', () => {
    const dir = makeCase('torn');
    writeLane(dir);
    fs.appendFileSync(wavefield.decisionsPath(dir),
      '{"torn": \n' + JSON.stringify({ request_id: 'r2', kept: 'B', role: 'listener' }) + '\n');
    const rows = wavefield.readDecisions(dir);
    assert.strictEqual(rows.length, 1);
    assert.strictEqual(rows[0].kept, 'B');
  });

  // ——— 3) runner failure ——————————————————————————————————————————————

  console.log('wavefield — runner boundary');

  await check('runner 失败时暴露它自己的 code/detail（不静默）', async () => {
    const client = wavefield.createClient({
      run: fakeRun({ code: 1, stdout: '', stderr: JSON.stringify({ ok: false, code: 'CANDIDATE_MISSING', detail: 'C 还没有渲染产物' }) + '\n' }),
    });
    const res = await client.inspect('/tmp/whatever');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'CANDIDATE_MISSING');
    assert.match(res.detail, /C 还没有渲染产物/);
  });

  await check('runner 起不来时报 RUNNER_UNAVAILABLE', async () => {
    const client = wavefield.createClient({ run: async () => { throw new Error('spawn python ENOENT'); } });
    const res = await client.inspect('/tmp/whatever');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'RUNNER_UNAVAILABLE');
    assert.match(res.detail, /ENOENT/);
  });

  await check('成功时转发 action 与 JSON stdin，并解析 stdout', async () => {
    const run = fakeRun(OK_RUN);
    const client = wavefield.createClient({ run, runnerPath: '/x/wavefield_runner.py' });
    const res = await client.choose('/case', 'A', 'creator', 'req-1');
    assert.strictEqual(res.ok, true);
    assert.strictEqual(run.captured.length, 1);
    assert.strictEqual(run.captured[0].args[0], '/x/wavefield_runner.py');
    assert.strictEqual(run.captured[0].args[1], 'choose');
    const sent = JSON.parse(run.captured[0].input);
    assert.strictEqual(sent.action, 'choose');
    assert.strictEqual(sent.case_dir, '/case');
    assert.strictEqual(sent.kept, 'A');
    assert.strictEqual(sent.request_id, 'req-1');
  });

  await check('未知 action 不会启动进程', async () => {
    const run = fakeRun(OK_RUN);
    const res = await wavefield.invoke(run, 'r', 'delete-everything', {});
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'UNKNOWN_ACTION');
    assert.strictEqual(run.captured.length, 0, '未知 action 不得启动进程');
  });

  await check('runner 退出码非零但 stdout 有 JSON 时，仍归因到它自己的 code', async () => {
    const run = fakeRun({ code: 2, stdout: JSON.stringify({ ok: false, code: 'BAD_KEPT', detail: '只能选择 ORIGINAL / A / B / C' }) + '\n', stderr: '' });
    const res = await wavefield.invoke(run, 'r', 'choose', {});
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'BAD_KEPT');
  });

  // ——— 4) missing artifacts ————————————————————————————————————————————

  console.log('wavefield — missing artifacts are visible');

  await check('缺一个候选：exists 为假、blocker 点名、试听按钮禁用', () => {
    const dir = makeCase('missing');
    writeLane(dir, { omit: ['C'] });
    const state = wavefield.readState(dir);
    assert.strictEqual(state.candidates.C.exists, false);
    assert.ok(state.blockers.includes('CANDIDATE_MISSING:C'), JSON.stringify(state.blockers));
    assert.ok(state.blockers.includes('HEARING_MISSING:C'));
    assert.ok(state.candidates.A.exists, '其余候选不受影响');
    assert.strictEqual(state.candidates.C.path, path.join(wavefield.wavefieldDir(dir), 'candidates', 'C.wav'));
  });

  await check('没有任何候选时给出 NO_CANDIDATES', () => {
    const dir = makeCase('nocand');
    writeLane(dir, { omit: ['A', 'B', 'C', 'ORIGINAL'] });
    const state = wavefield.readState(dir);
    assert.ok(state.blockers.includes('NO_CANDIDATES'));
    assert.strictEqual(state.candidates.ORIGINAL.exists, true, '原版始终可用');
  });

  await check('源音频不可读时给出警告', () => {
    const dir = makeCase('nosource');
    writeLane(dir);
    fs.unlinkSync(path.join(dir, 'source.wav'));
    const state = wavefield.readState(dir);
    assert.strictEqual(state.candidates.ORIGINAL.exists, false);
    assert.ok(state.warnings.includes('ORIGINAL_SOURCE_UNREADABLE'));
  });

  // ——— 5) choice validation ————————————————————————————————————————————

  console.log('wavefield — choice validation');

  await check('只认 ORIGINAL/A/B/C', async () => {
    for (const ok of ['ORIGINAL', 'A', 'B', 'C']) assert.strictEqual(wavefield.isValidChoice(ok), true);
    for (const bad of ['D', 'a', '', null, 'original', 'AB']) assert.strictEqual(wavefield.isValidChoice(bad), false);
  });

  await check('非法选择在本地就被拒（不启动 python）', async () => {
    const run = fakeRun(OK_RUN);
    const client = wavefield.createClient({ run, runnerPath: 'r' });
    const res = await client.choose('/case', 'D', 'creator');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'BAD_KEPT');
    assert.strictEqual(run.captured.length, 0, '非法输入不得启动进程');
  });

  await check('非法角色同样被拒', async () => {
    const run = fakeRun(OK_RUN);
    const res = await wavefield.createClient({ run, runnerPath: 'r' }).choose('/case', 'A', 'admin');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'BAD_ROLE');
    assert.strictEqual(run.captured.length, 0);
  });

  // ——— 6) export gating ————————————————————————————————————————————————

  console.log('wavefield — export gating');

  await check('没有记录过选择就不导出', async () => {
    const dir = makeCase('nochoice');
    writeLane(dir);
    const run = fakeRun(OK_RUN);
    const res = await wavefield.createClient({ run, runnerPath: 'r' }).exportChosen(dir);
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'NOT_CHOSEN');
    assert.strictEqual(run.captured.length, 0);
  });

  await check('导出「没选过的那一版」也被拒', async () => {
    const dir = makeCase('wrongkeep');
    writeLane(dir, { decisions: [{ request_id: 'r1', kept: 'A', role: 'creator' }] });
    const run = fakeRun(OK_RUN);
    const res = await wavefield.createClient({ run, runnerPath: 'r' }).exportChosen(dir, 'C');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'NOT_CHOSEN');
    assert.strictEqual(run.captured.length, 0);
  });

  await check('账本与请求一致时转发 export', async () => {
    const dir = makeCase('dokeep');
    writeLane(dir, { decisions: [{ request_id: 'r1', kept: 'B', role: 'creator' }] });
    const run = fakeRun({ code: 0, stdout: JSON.stringify({ ok: true, action: 'export', manifest: { kept: 'B' } }) + '\n', stderr: '' });
    const res = await wavefield.createClient({ run, runnerPath: 'r' }).exportChosen(dir, 'B');
    assert.strictEqual(res.ok, true);
    assert.strictEqual(res.payload.manifest.kept, 'B');
    assert.strictEqual(run.captured.length, 1);
  });

  // ——— 7) manifest —————————————————————————————————————————————————————

  console.log('wavefield — export manifest');

  await check('导出后的 manifest 可被读回（场 + 双哈希 + 决定）', () => {
    const dir = makeCase('manifest');
    const manifest = {
      schema: 'moodify.wavefield.export/0.1',
      kept: 'C',
      export_mode: 'RENDERED_FIELD',
      chosen_audio: path.join(wavefield.exportDir(dir), 'chosen.wav'),
      chosen_audio_sha256: 'd'.repeat(64),
      source_sha256: 'e'.repeat(64),
      chosen_field: fieldRecord('C', 0.8),
      engine_version: 'algorithmic-room-v0.1',
      decided_at: '2026-10-06T00:00:00+00:00',
      created_at: '2026-10-06T00:00:00+00:00',
    };
    writeLane(dir, { decisions: [{ request_id: 'r1', kept: 'C', role: 'creator', decided_at: '2026-10-06T00:00:00+00:00' }], manifest });
    const state = wavefield.readState(dir);
    assert.strictEqual(state.export.chosen_audio_sha256, 'd'.repeat(64));
    assert.strictEqual(state.export.source_sha256, 'e'.repeat(64));
    assert.strictEqual(state.export.chosen_field.parameters.room_size, 0.8);
    assert.strictEqual(state.export.engine_version, 'algorithmic-room-v0.1');
    assert.strictEqual(state.chosen.kept, 'C');
    assert.deepStrictEqual(state.blockers, []);
  });

  await check('保留原版时可以没有 chosen.wav（导出即源文件的引用）', () => {
    const dir = makeCase('keeporig');
    writeLane(dir, {
      decisions: [{ request_id: 'r1', kept: 'ORIGINAL', role: 'listener' }],
      manifest: {
        kept: 'ORIGINAL', export_mode: 'REFERENCE_TO_SOURCE',
        chosen_audio: null, source_sha256: 'a'.repeat(64),
      },
    });
    const state = wavefield.readState(dir);
    assert.strictEqual(state.export.chosen_audio, null);
    assert.strictEqual(state.export.export_mode, 'REFERENCE_TO_SOURCE');
    assert.deepStrictEqual(state.blockers, []);
  });

  // ——— 8) playback authority ————————————————————————————————————————————

  console.log('wavefield — playback authority');

  function fakeAudio() {
    const created = [];
    const running = new Set();
    return {
      created,
      running,
      async decode() { return { duration: 2.0 }; },
      createSource(buffer) {
        const node = {
          buffer,
          started: false,
          stopCount: 0,
          onended: null,
          start() { this.started = true; running.add(node); },
          stop() { this.stopCount += 1; running.delete(node); },
        };
        created.push(node);
        return node;
      },
      now: () => 0,
    };
  }

  await check('切换候选会先停掉上一个（永不重叠）', async () => {
    const audio = fakeAudio();
    const player = playerModule.createPlayer({ audio });
    await player.load('A', new ArrayBuffer(4));
    player.play('A');
    assert.strictEqual(audio.running.size, 1);
    assert.strictEqual(player.activeCount(), 1);

    await player.load('B', new ArrayBuffer(4));
    assert.strictEqual(audio.created.length, 2, '应当新建音源');
    assert.strictEqual(audio.created[0].stopCount >= 1, true, '上一个必须先被停掉');
    assert.strictEqual(audio.running.size, 1, '同一时刻只能有一条在响');
    assert.strictEqual(player.current(), 'B');
  });

  await check('播放中反复切换，活跃音源数恒为 0 或 1', async () => {
    const audio = fakeAudio();
    const player = playerModule.createPlayer({ audio });
    for (const id of ['ORIGINAL', 'A', 'B', 'C', 'A', 'ORIGINAL']) {
      await player.load(id, new ArrayBuffer(4));
      player.play(id);
      assert.ok(audio.running.size <= 1, '出现了 ' + audio.running.size + ' 条同时播放的音源');
    }
    assert.strictEqual(audio.running.size, 1);
    assert.strictEqual(player.current(), 'ORIGINAL');
  });

  await check('未载入的候选不能播放', () => {
    const audio = fakeAudio();
    const player = playerModule.createPlayer({ audio });
    const res = player.play('C');
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'NOT_LOADED');
    assert.strictEqual(audio.created.length, 0, '拒绝时不得创建音源');
  });

  await check('stop 之后没有任何音源在响', async () => {
    const audio = fakeAudio();
    const player = playerModule.createPlayer({ audio });
    await player.load('A', new ArrayBuffer(4));
    player.play('A');
    player.stop();
    assert.strictEqual(audio.running.size, 0);
    assert.strictEqual(player.activeCount(), 0);
    assert.strictEqual(player.isPlaying(), false);
  });

  await check('解码失败时保留上一版可播放，不谎称已切换', async () => {
    const audio = fakeAudio();
    audio.decode = async (bytes) => {
      if (bytes && bytes.fail) throw new Error('decode blew up');
      return { duration: 2.0 };
    };
    const player = playerModule.createPlayer({ audio });
    await player.load('A', new ArrayBuffer(4));
    player.play('A');
    const res = await player.load('B', { fail: true });
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'DECODE_FAILED');
    assert.strictEqual(player.current(), 'A', '当前仍是 A');
    assert.strictEqual(audio.running.size, 1, 'A 仍在响');
  });

  await check('没有音频后端时明确拒绝', async () => {
    const player = playerModule.createPlayer({});
    const res = await player.load('A', new ArrayBuffer(4));
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'NO_AUDIO_BACKEND');
  });

  await check('reset 清空缓冲与状态（换世界）', async () => {
    const audio = fakeAudio();
    const player = playerModule.createPlayer({ audio });
    await player.load('A', new ArrayBuffer(4));
    player.play('A');
    player.reset();
    assert.strictEqual(audio.running.size, 0);
    assert.strictEqual(player.current(), null);
    assert.strictEqual(player.status(), 'idle');
    assert.deepStrictEqual(player.loadedIds(), []);
  });

  await check('候选展示顺序固定为 ORIGINAL/A/B/C', () => {
    assert.deepStrictEqual(playerModule.CANDIDATE_ORDER, ['ORIGINAL', 'A', 'B', 'C']);
  });

  // ——— clean up ————————————————————————————————————————————————————————

  for (const dir of roots) {
    try { fs.rmSync(dir, { recursive: true, force: true }); } catch { /* best effort */ }
  }

  console.log('\n' + passed + ' passed, ' + failures.length + ' failed');
  if (failures.length) {
    console.log('\nFailures:');
    for (const f of failures) console.log('  - ' + f);
    process.exit(1);
  }
})().catch((err) => {
  console.error('TEST HARNESS ERROR:', err);
  process.exit(1);
});
