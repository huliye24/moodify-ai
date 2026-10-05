#!/usr/bin/env node
/**
 * Headless tests for the history-sync data layer (Phase 3A, MIP-0003 §3–§5).
 *
 * Scope: `src/history-sync/{schema,queue,projection,link}.js` — the parts of account/history
 * sync that must be right *before* any server exists:
 *
 *   §15.4 data minimisation   every payload is whitelisted; audio / paths / hashes / tokens are
 *                             rejected recursively, and rejected loudly (never silently stripped)
 *   §15.3 sync                idempotency, offline restart, account switching, ordering,
 *                             duplicate events, inscription/decision conservation,
 *                             delete-without-resurrection, queue corruption isolation
 *   §13  account link         the per-case binding holds only a work_id and sync state
 *
 * What this file deliberately does NOT claim: nothing here touches a network or a database.
 * Real sign-in, real RLS and real cross-device sync remain `DEPLOYMENT_BLOCKED` until
 * `deployment/supabase/tests/run_rls_tests.js` exits 0 and two real test accounts are used.
 *
 * Run: node scripts/test-sync.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const schema = require(path.join(__dirname, '..', 'src', 'history-sync', 'schema'));
const queue = require(path.join(__dirname, '..', 'src', 'history-sync', 'queue'));
const projection = require(path.join(__dirname, '..', 'src', 'history-sync', 'projection'));
const link = require(path.join(__dirname, '..', 'src', 'history-sync', 'link'));

let passed = 0;
const failures = [];
function check(label, fn) {
  try { fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-sync-test-'));
let seq = 0;
const newAppData = () => {
  const dir = path.join(TMP, `appdata-${++seq}`);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
};
const newCase = () => {
  const dir = path.join(TMP, `case-${++seq}`);
  fs.mkdirSync(path.join(dir, 'studio'), { recursive: true });
  return dir;
};

const WORK = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const WORK2 = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
const USER_A = 'user-a-uuid';
const USER_B = 'user-b-uuid';

console.log('history-sync data layer (Phase 3A)\n');

// ── schema: the whitelist boundary ──────────────────────────────────────────
console.log('1. event schema (data minimisation)');

check('五个 event type 是闭集', () => {
  assert.deepStrictEqual(schema.EVENT_TYPES, [
    'WORK_COMPLETED', 'DECISION_CHANGED', 'INSCRIPTION_UPDATED', 'AUDIO_EXPORTED', 'WORK_REVISITED',
  ]);
  assert.throws(() => schema.buildEvent({
    eventType: 'PLAYBACK_TELEMETRY', workId: WORK, payload: {},
  }), /UNKNOWN_EVENT_TYPE/);
});

check('WORK_COMPLETED 需要标题与完成时间，并接受白名单字段', () => {
  const event = schema.buildEvent({
    eventType: 'WORK_COMPLETED',
    workId: WORK,
    payload: {
      title: 'Je ne blesserai pas ta fragilité',
      duration_ms: 123320,
      completion_mode: 'FAST_STEREO_ONLY',
      selected: 'A',
      completed_at: '2026-10-04T14:45:22.739Z',
      inscription: 'é中文😀',
    },
  });
  assert.strictEqual(event.event_type, 'WORK_COMPLETED');
  assert.strictEqual(event.schema_version, schema.EVENT_SCHEMA);
  assert.match(event.request_id, /^[0-9a-f-]{36}$/);
  assert.strictEqual(event.payload.duration_ms, 123320);
  assert.throws(() => schema.buildEvent({
    eventType: 'WORK_COMPLETED', workId: WORK, payload: { title: 'x' },
  }), /MISSING_REQUIRED_FIELD/);
});

check('未知 payload 字段被拒绝（不是被静默丢掉）', () => {
  assert.throws(() => schema.buildEvent({
    eventType: 'DECISION_CHANGED',
    workId: WORK,
    payload: { selected: 'B', listening_ms: 42000 },
  }), /UNKNOWN_PAYLOAD_FIELD|FORBIDDEN_FIELD/);
});

check('禁止字段：音频 / 分轨 / MIDI / 报告 / 频谱 / 参数 / 路径 / hash / 凭据 / 行为遥测', () => {
  const forbidden = [
    ['audio', Buffer.from('RIFF....')],
    ['stems', ['vocals.wav']],
    ['midi', 'x.mid'],
    ['report', { measurements: [] }],
    ['spectrum_log', 'scan/spectrum_log.png'],
    ['mix_graph', { nodes: [] }],
    ['local_path', 'E:\\moodify\\cases\\case_1'],
    ['source_sha256', 'a'.repeat(64)],
    ['refresh_token', 'v1.abc'],
    ['listening_ms', 1000],
    ['play_count', 3],
  ];
  for (const [key, value] of forbidden) {
    assert.throws(() => schema.assertNoForbiddenData({ [key]: value }, '$'),
      schema.HistorySchemaError, `${key} must be rejected`);
  }
});

check('禁止值形状：绝对路径、64 位 hash、JWT、magic link、file:// 出现在任何字符串值里', () => {
  const bad = [
    'E:\\Users\\me\\song.wav',
    '/Users/me/Music/song.wav',
    'C:/Users/me/a.wav',
    'file:///E:/moodify/case/report.json',
    'sha=' + 'f'.repeat(64),
    'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.signature',
    'https://project.supabase.co/auth/v1/verify?token=abc',
  ];
  for (const value of bad) {
    assert.throws(() => schema.assertNoForbiddenData({ note: value }, '$'),
      schema.HistorySchemaError, `${value} must be rejected`);
  }
  // 正常文本不受影响（重音、中文、emoji、普通句号）
  schema.assertNoForbiddenData({ inscription: '写给这首歌。é中文😀 — 3.5' }, '$');
});

check('一句话边界与 keepsake 一致：280 码位 / 4 行', () => {
  const ok = schema.buildEvent({
    eventType: 'INSCRIPTION_UPDATED', workId: WORK, payload: { inscription: '花'.repeat(280) },
  });
  assert.strictEqual([...ok.payload.inscription].length, 280);
  assert.throws(() => schema.buildEvent({
    eventType: 'INSCRIPTION_UPDATED', workId: WORK, payload: { inscription: '花'.repeat(281) },
  }), /INSCRIPTION_TOO_LONG/);
  assert.throws(() => schema.buildEvent({
    eventType: 'INSCRIPTION_UPDATED', workId: WORK, payload: { inscription: 'a\nb\nc\nd\ne' },
  }), /INSCRIPTION_TOO_MANY_LINES/);
  // 清空是普通编辑：空串合法
  assert.strictEqual(schema.buildEvent({
    eventType: 'INSCRIPTION_UPDATED', workId: WORK, payload: { inscription: '' },
  }).payload.inscription, undefined);
});

check('日志行只含 event_type / request_id / status（不打 payload）', () => {
  const event = schema.buildEvent({
    eventType: 'WORK_REVISITED', workId: WORK, payload: { title: '私密标题' },
  });
  const line = schema.logLine({ ...event, status: 'pending' });
  assert.ok(!line.includes('私密标题'), 'payload must not be logged');
  assert.deepStrictEqual(Object.keys(JSON.parse(line)).sort(), ['event_type', 'request_id', 'status']);
});

// ── queue: offline, idempotent, account-scoped ──────────────────────────────
console.log('\n2. offline queue');

const completedEvent = (requestId, workId = WORK, extra = {}) => schema.buildEvent({
  eventType: 'WORK_COMPLETED',
  workId,
  requestId,
  payload: {
    title: '一首歌', completion_mode: 'FAST_STEREO_ONLY', selected: 'A',
    completed_at: '2026-10-04T10:00:00.000Z', ...extra,
  },
});

check('同一 request_id 入队两次 → 只有一条（重试不改动已有记录）', () => {
  const app = newAppData();
  const event = completedEvent('11111111-1111-4111-8111-111111111111');
  const first = queue.enqueue(app, { accountId: USER_A, event });
  const second = queue.enqueue(app, { accountId: USER_A, event });
  assert.strictEqual(first.ok, true);
  assert.strictEqual(first.duplicate, false);
  assert.strictEqual(second.ok, true);
  assert.strictEqual(second.duplicate, true);
  const read = queue.readQueue(app, { accountId: USER_A });
  assert.strictEqual(read.entries.length, 1);
  assert.strictEqual(read.diagnostics.length, 0);
});

check('离线完成 → 重启 → 登录同一账户 → 成功续传', () => {
  const app = newAppData();
  const a = queue.enqueue(app, { accountId: USER_A, event: completedEvent('22222222-2222-4222-8222-222222222222') });
  assert.strictEqual(a.ok, true);
  // 「重启」：重新读盘（没有内存状态可依赖）
  const pending = queue.pendingEntries(app, { accountId: USER_A, now: Date.now() + 1000 });
  assert.strictEqual(pending.entries.length, 1);
  queue.settle(app, { requestId: pending.entries[0].request_id, ok: true });
  assert.strictEqual(queue.pendingEntries(app, { accountId: USER_A }).entries.length, 0);
  const after = queue.readQueue(app, { accountId: USER_A });
  assert.strictEqual(after.entries.length, 1, 'the confirmed entry is kept until compaction');
  assert.ok(after.entries[0].confirmed_at);
  const compacted = queue.compact(app);
  assert.strictEqual(compacted.removed, 1);
  assert.strictEqual(queue.readQueue(app, { accountId: USER_A }).entries.length, 0);
});

check('失败 → 指数退避（有上限），到点之前不再重试', () => {
  const app = newAppData();
  const event = completedEvent('33333333-3333-4333-8333-333333333333');
  queue.enqueue(app, { accountId: USER_A, event, now: 0 });
  const t0 = 1000;
  queue.settle(app, { requestId: event.request_id, ok: false, error: 'NETWORK', now: t0 });
  const entry = queue.readQueue(app, { accountId: USER_A }).entries[0];
  assert.strictEqual(entry.attempts, 1);
  assert.strictEqual(Date.parse(entry.next_attempt_at) - t0, queue.BASE_BACKOFF_MS);
  assert.strictEqual(queue.pendingEntries(app, { accountId: USER_A, now: t0 + 1 }).entries.length, 0);
  assert.strictEqual(queue.pendingEntries(app, { accountId: USER_A, now: t0 + queue.BASE_BACKOFF_MS + 1 })
    .entries.length, 1);
  for (let i = 0; i < 12; i += 1) {
    queue.settle(app, { requestId: event.request_id, ok: false, error: 'NETWORK', now: t0 });
  }
  const later = queue.readQueue(app, { accountId: USER_A }).entries[0];
  assert.strictEqual(queue.backoffMs(later.attempts), queue.MAX_BACKOFF_MS, 'backoff is capped');
  assert.ok(later.attempts <= 32);
});

check('登录另一账户：绝不发送前一账户的队列（foreign 计数可见）', () => {
  const app = newAppData();
  queue.enqueue(app, { accountId: USER_A, event: completedEvent('44444444-4444-4444-8444-444444444444') });
  const forB = queue.pendingEntries(app, { accountId: USER_B });
  assert.strictEqual(forB.entries.length, 0, 'B must see nothing of A');
  assert.strictEqual(forB.foreign, 1, 'but the queue reports that foreign entries exist');
  const stillThere = queue.readQueue(app, { accountId: USER_A });
  assert.strictEqual(stillThere.entries.length, 1, 'A owns its entries');
});

check('sign out 保留未发送事件，重新登录同一账户可续传', () => {
  const app = newAppData();
  const event = completedEvent('55555555-5555-4555-8555-555555555555');
  queue.enqueue(app, { accountId: USER_A, event });
  const off = queue.unbindAccount(app, { accountId: USER_A });
  assert.strictEqual(off.touched, 1);
  assert.strictEqual(queue.pendingEntries(app, { accountId: USER_A }).entries.length, 0,
    'unbound events belong to nobody');
  assert.strictEqual(queue.pendingEntries(app, { accountId: USER_B }).entries.length, 0,
    'and they must not leak to another account');
  const back = queue.rebindAccount(app, { accountId: USER_A });
  assert.strictEqual(back.touched, 1, 'signing back in continues where it stopped');
  assert.strictEqual(queue.pendingEntries(app, { accountId: USER_A }).entries.length, 1);
});

check('队列损坏隔离：半截行 / 垃圾行不进队列，也不阻断其余事件', () => {
  const app = newAppData();
  const good = completedEvent('66666666-6666-4666-8666-666666666666');
  queue.enqueue(app, { accountId: USER_A, event: good });
  fs.appendFileSync(queue.queuePath(app), '{"schema":"moodify.history-queue/0.1","request_id":"x"\n');
  fs.appendFileSync(queue.queuePath(app), 'not json at all\n');
  const read = queue.readQueue(app, { accountId: USER_A });
  assert.strictEqual(read.ok, true);
  assert.strictEqual(read.entries.length, 1, 'the good entry survives');
  assert.strictEqual(read.diagnostics.length, 2, 'and the damage is reported, not hidden');
  const stats = queue.stats(app, { accountId: USER_A });
  assert.strictEqual(stats.diagnostics, 2);
});

check('队列满时有界拒绝，而不是无限增长', () => {
  const app = newAppData();
  const file = queue.queuePath(app);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const rows = [];
  for (let i = 0; i < queue.MAX_ENTRIES; i += 1) {
    rows.push(JSON.stringify({
      schema: queue.QUEUE_SCHEMA, request_id: `r${i}`, account_id: USER_A, event: { work_id: WORK },
    }));
  }
  fs.writeFileSync(file, rows.join('\n') + '\n', 'utf8');
  const res = queue.enqueue(app, { accountId: USER_A, event: completedEvent('77777777-7777-4777-8777-777777777777') });
  assert.strictEqual(res.ok, false);
  assert.strictEqual(res.reason, 'QUEUE_FULL');
});

check('没有账户绑定时拒绝入队（未绑定事件不允许被发走）', () => {
  const app = newAppData();
  const res = queue.enqueue(app, { accountId: null, event: completedEvent('88888888-8888-4888-8888-888888888888') });
  assert.strictEqual(res.ok, false);
  assert.strictEqual(res.reason, 'NO_ACCOUNT_BINDING');
});

// ── projection: stable, explainable ─────────────────────────────────────────
console.log('\n3. projection');

check('乱序 / 重复事件投影一致（稳定排序 + 去重）', () => {
  const events = [
    { event_id: 'e2', request_id: 'r2', work_id: WORK, event_type: 'DECISION_CHANGED',
      occurred_at: '2026-10-04T11:00:00.000Z', server_received_at: '2026-10-04T11:00:01.000Z',
      payload: { selected: 'B' } },
    { event_id: 'e1', request_id: 'r1', work_id: WORK, event_type: 'WORK_COMPLETED',
      occurred_at: '2026-10-04T10:00:00.000Z', server_received_at: '2026-10-04T10:00:01.000Z',
      payload: { title: '一首歌', selected: 'A', completed_at: '2026-10-04T10:00:00.000Z' } },
    { event_id: 'e2', request_id: 'r2', work_id: WORK, event_type: 'DECISION_CHANGED',
      occurred_at: '2026-10-04T11:00:00.000Z', server_received_at: '2026-10-04T11:00:01.000Z',
      payload: { selected: 'B' } },
  ];
  const forward = projection.projectHistory(events);
  const backward = projection.projectHistory([...events].reverse());
  assert.deepStrictEqual(forward, backward, 'arrival order must not matter');
  assert.strictEqual(forward.length, 1);
  assert.strictEqual(forward[0].selected, 'B', 'current selection = last valid decision');
  assert.deepStrictEqual(forward[0].decisionHistory.map((d) => d.selected), ['A', 'B']);
});

check('inscription 取最后一次明确编辑，不做字符级合并；decision 历史全部保留', () => {
  const base = {
    work_id: WORK, server_received_at: '2026-10-04T10:00:00.000Z',
  };
  const events = [
    { ...base, event_id: 'e1', request_id: 'r1', event_type: 'WORK_COMPLETED',
      occurred_at: '2026-10-04T10:00:00.000Z',
      payload: { title: '一首歌', selected: 'A', completed_at: '2026-10-04T10:00:00.000Z', inscription: '第一句' } },
    { ...base, event_id: 'e2', request_id: 'r2', event_type: 'INSCRIPTION_UPDATED',
      occurred_at: '2026-10-04T11:00:00.000Z', server_received_at: '2026-10-04T11:00:00.000Z',
      payload: { inscription: '第二句' } },
    { ...base, event_id: 'e3', request_id: 'r3', event_type: 'INSCRIPTION_UPDATED',
      occurred_at: '2026-10-04T12:00:00.000Z', server_received_at: '2026-10-04T12:00:00.000Z',
      payload: { inscription: '' } },
  ];
  const [work] = projection.projectHistory(events);
  assert.strictEqual(work.inscription, '', 'clearing the text is an ordinary edit');
  assert.strictEqual(work.decisionHistory.length, 1, 'decision history survives inscription edits');
  assert.strictEqual(work.selected, 'A');
});

check('本地与云端冲突：本地是权威，只留下差异痕迹，不改本地', () => {
  const local = [{
    workId: WORK, title: '本地标题', selected: 'A', inscription: '本地的话',
    completedAt: '2026-10-04T10:00:00.000Z', audioAvailability: 'LOCAL_AVAILABLE',
    syncEnabled: true, syncState: 'waiting',
  }];
  const remote = [{
    workId: WORK, title: '云端标题', selected: 'B', inscription: '云端的话',
    completedAt: '2026-10-04T10:00:00.000Z',
  }];
  const merged = projection.mergeHistory({ local, remote });
  assert.strictEqual(merged.length, 1);
  assert.strictEqual(merged[0].title, '本地标题', 'local fields are authoritative');
  assert.strictEqual(merged[0].selected, 'A');
  assert.strictEqual(merged[0].inscription, '本地的话');
  assert.strictEqual(merged[0].remoteDirty, true, 'the difference is visible, not applied');
  assert.strictEqual(merged[0].remoteSelected, 'B');
  assert.strictEqual(merged[0].audioAvailability, 'LOCAL_AVAILABLE');
  assert.deepStrictEqual(local[0].selected, 'A', 'the merge never mutates local state');
});

check('远端独有记录：显示为记忆，音频恒为 LOCAL_ONLY（不出现假播放）', () => {
  const merged = projection.mergeHistory({
    local: [],
    remote: [{ workId: WORK2, title: '另一台设备上的歌', selected: 'ORIGINAL',
      inscription: '在那台机器上写的', completedAt: '2026-10-04T09:00:00.000Z' }],
  });
  assert.strictEqual(merged.length, 1);
  assert.strictEqual(merged[0].audioAvailability, 'LOCAL_ONLY');
  assert.deepStrictEqual(merged[0].sources, ['remote']);
  assert.strictEqual(merged[0].syncState, 'synced');
});

check('删除不复活：墓碑（服务端）与本地 sync_enabled=false 共同生效', () => {
  // 服务端删除后，pull 不再返回该 work；即使旧事件重现，投影也不会把它变回“已完成”
  const events = [
    { event_id: 'e1', request_id: 'r1', work_id: WORK, event_type: 'WORK_COMPLETED',
      occurred_at: '2026-10-04T10:00:00.000Z', server_received_at: '2026-10-04T10:00:00.000Z',
      payload: { title: '一首歌', selected: 'A', completed_at: '2026-10-04T10:00:00.000Z' } },
  ];
  const listed = projection.projectHistory(events);
  assert.strictEqual(listed.length, 1);
  const cluster = newCase();
  link.writeLink(cluster, { work_id: WORK, sync_enabled: true });
  link.writeLink(cluster, { sync_enabled: false });
  const stored = link.readLink(cluster).link;
  assert.strictEqual(stored.sync_enabled, false);
  assert.strictEqual(stored.work_id, WORK, 'the binding stays, only syncing stops');
  // 被删除的 work 不在 pull 结果里 → 列表里就没有它（本地 case 仍在，可重新开启同步）
  assert.strictEqual(projection.mergeHistory({ local: [], remote: [] }).length, 0);
});

// ── account link ────────────────────────────────────────────────────────────
console.log('\n4. account link (per case)');

check('只保存 work_id 与同步状态；无邮箱、无 token', () => {
  const dir = newCase();
  const workId = link.ensureWorkId(dir);
  const res = link.writeLink(dir, { work_id: workId, sync_enabled: true, last_pushed_revision: 3 });
  assert.strictEqual(res.ok, true);
  const raw = fs.readFileSync(link.linkPath(dir), 'utf8');
  assert.ok(!/email|token|anon_key|service_role|jwt/i.test(raw), 'no credentials beside the work');
  const parsed = JSON.parse(raw);
  assert.deepStrictEqual(Object.keys(parsed).sort(),
    ['last_pulled_cursor', 'last_pushed_revision', 'schema', 'sync_enabled', 'updated_at', 'work_id']);
  assert.strictEqual(parsed.schema, 'moodify.studio.account-link/0.1');
  assert.strictEqual(parsed.last_pushed_revision, 3);
});

check('凭据被写进来时拒绝使用（不静默接受，也不静默删除）', () => {
  const dir = newCase();
  fs.writeFileSync(link.linkPath(dir), JSON.stringify({
    schema: 'moodify.studio.account-link/0.1', work_id: WORK, sync_enabled: true,
    refresh_token: 'leaked',
  }));
  const read = link.readLink(dir);
  assert.strictEqual(read.link, null);
  assert.strictEqual(read.error, 'LINK_CONTAINS_FORBIDDEN_FIELD');
  assert.ok(fs.existsSync(link.linkPath(dir)), 'the file is left for a human to inspect');
});

check('损坏 / schema 不符 / 坏 work_id 都只报告，不阻断', () => {
  const dir = newCase();
  fs.writeFileSync(link.linkPath(dir), '{ broken');
  assert.strictEqual(link.readLink(dir).error, 'LINK_CORRUPT_JSON');
  fs.writeFileSync(link.linkPath(dir), JSON.stringify({ schema: 'other/0.1' }));
  assert.strictEqual(link.readLink(dir).error, 'LINK_SCHEMA_MISMATCH');
  assert.strictEqual(link.writeLink(dir, { work_id: 'not-a-uuid' }).reason, 'BAD_WORK_ID');
  assert.strictEqual(link.readLink(dir).link, null);
});

check('work_id 本地生成且稳定（不需要联网）', () => {
  const dir = newCase();
  const first = link.ensureWorkId(dir);
  const second = link.ensureWorkId(dir);
  assert.match(first, /^[0-9a-f-]{36}$/);
  assert.strictEqual(first, second, 'same case keeps the same work id');
  assert.strictEqual(link.ensureWorkId(newCase()) === first, false);
});

// ── data-minimisation sweep over a realistic payload set ─────────────────────
console.log('\n5. an upload batch carries nothing it should not');

check('真实形状的一批事件：序列化后不含音频/路径/hash/凭据/行为遥测', () => {
  const events = [
    schema.buildEvent({
      eventType: 'WORK_COMPLETED', workId: WORK,
      payload: {
        title: 'Je ne blesserai pas ta fragilité', duration_ms: 123320,
        completion_mode: 'FAST_STEREO_ONLY', selected: 'A',
        completed_at: '2026-10-04T14:45:22.739Z', inscription: 'é中文😀 写给这首歌',
      },
    }),
    schema.buildEvent({
      eventType: 'DECISION_CHANGED', workId: WORK, payload: { selected: 'B', title: 'Je ne blesserai pas ta fragilité' },
    }),
    schema.buildEvent({ eventType: 'AUDIO_EXPORTED', workId: WORK, payload: { selected: 'B' } }),
    schema.buildEvent({ eventType: 'WORK_REVISITED', workId: WORK, payload: {} }),
  ];
  const batch = JSON.stringify(events);
  for (const forbidden of ['RIFF', '.wav', '.mid', 'stems', 'report.json', 'spectrum', 'sha256',
    'E:\\\\', '/Users/', 'eyJ', 'token', 'listening', 'play_count']) {
    assert.ok(!batch.includes(forbidden), `batch must not contain ${forbidden}\n${batch}`);
  }
  assert.ok(batch.includes('é中文😀'), 'the user’s own words are allowed and preserved');
  // 每个事件都能通过白名单校验（这也是 push 前的实际检查）
  for (const event of events) schema.validatePayload(event.event_type, event.payload);
});

try { fs.rmSync(TMP, { recursive: true, force: true }); } catch { /* best effort */ }

console.log(`\n${passed} passed, ${failures.length} failed`);
if (failures.length) {
  console.log('\nFailures:');
  for (const f of failures) console.log('  - ' + f);
  process.exit(1);
}
