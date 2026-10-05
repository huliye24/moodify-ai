/**
 * Offline queue — append-only, idempotent, account-scoped.
 *
 * Contract: `protocol/mips/MIP-0003-personal-identity-history.md` §5
 *
 * Why it lives in the application data directory and not in the case:
 *   a queue is per *device + account*, not per song. Copying a queue into every case would
 *   multiply un-sent events and make "which account does this belong to" ambiguous.
 *
 * Invariants (each has a test in `scripts/test-sync.js`):
 *   1. append-only: entries are added and later *compacted* once confirmed, never rewritten;
 *   2. idempotent: one `request_id` appears at most once in the queue;
 *   3. account-scoped: entries carry the account binding; signing into a *different* account
 *      never sends the previous account's entries — they are parked, not uploaded;
 *   4. offline-safe: nothing is dropped on sign-out; signing back into the same account
 *      continues exactly where it stopped;
 *   5. crash-safe: a truncated final line (a crash during append) is isolated and reported,
 *      never allowed to break the rest of the queue or the Desktop;
 *   6. bounded: exponential backoff with a cap, and a hard cap on stored entries.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const QUEUE_SCHEMA = 'moodify.history-queue/0.1';
const FILE_NAME = 'history-queue.jsonl';
const MAX_ENTRIES = 5000;
const BASE_BACKOFF_MS = 5_000;
const MAX_BACKOFF_MS = 5 * 60 * 1000;

function backoffMs(attempts) {
  const n = Math.max(0, Math.trunc(attempts || 0));
  return Math.min(MAX_BACKOFF_MS, BASE_BACKOFF_MS * 2 ** n);
}

function queuePath(appDataDir) {
  return path.join(appDataDir, 'account', FILE_NAME);
}

/** 解析一行；损坏/半截的行返回 null（由调用方计入 diagnostics，绝不抛）。 */
function parseLine(line) {
  const text = String(line || '').trim();
  if (!text) return null;
  try {
    const parsed = JSON.parse(text);
    if (!parsed || typeof parsed !== 'object' || parsed.schema !== QUEUE_SCHEMA) return null;
    // account_id 允许为 null：退出登录后事件保留但解绑（既不丢弃，也不发给别的账户）
    if (!parsed.request_id) return null;
    if (parsed.account_id !== null && parsed.account_id !== undefined
        && typeof parsed.account_id !== 'string') return null;
    return parsed;
  } catch {
    return null;
  }
}

/**
 * 读队列。`accountId` 为 null 表示「还没有账户绑定」——这时只统计不挑选，
 * 因为未绑定的事件既不属于任何账户，也不允许被发走。
 */
function readQueue(appDataDir, { accountId = null } = {}) {
  const file = queuePath(appDataDir);
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (err) {
    if (err && err.code === 'ENOENT') {
      return { ok: true, entries: [], foreign: 0, diagnostics: [], total: 0 };
    }
    return { ok: false, reason: 'QUEUE_UNREADABLE', entries: [], foreign: 0, diagnostics: [], total: 0 };
  }
  const entries = [];
  const diagnostics = [];
  let foreign = 0;
  const lines = raw.split('\n');
  lines.forEach((line, index) => {
    if (!line.trim()) return;
    const parsed = parseLine(line);
    if (!parsed) {
      // 隔离损坏行：只记录，不阻断其余队列，也不删除（用户的数据不做静默清理）
      diagnostics.push({ line: index + 1, reason: 'QUEUE_ENTRY_CORRUPT' });
      return;
    }
    if (accountId && parsed.account_id !== accountId) { foreign += 1; return; }
    entries.push(parsed);
  });
  return { ok: true, entries, foreign, diagnostics, total: entries.length + foreign };
}

/** 同账户、未确认、且已到重试时间的事件（稳定顺序：入队顺序）。 */
function pendingEntries(appDataDir, { accountId, now = Date.now() } = {}) {
  const read = readQueue(appDataDir, { accountId });
  if (!read.ok) return { ok: false, reason: read.reason, entries: [], diagnostics: read.diagnostics };
  const entries = read.entries.filter((entry) => {
    if (entry.confirmed_at) return false;
    const due = Date.parse(entry.next_attempt_at || 0) || 0;
    return due <= now;
  });
  return { ok: true, entries, diagnostics: read.diagnostics, foreign: read.foreign };
}

function writeAll(appDataDir, lines) {
  const file = queuePath(appDataDir);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp-${process.pid}-${crypto.randomBytes(4).toString('hex')}`;
  try {
    fs.writeFileSync(tmp, lines.join('\n') + (lines.length ? '\n' : ''), 'utf8');
    fs.renameSync(tmp, file);
    return { ok: true };
  } catch (err) {
    try { fs.rmSync(tmp, { force: true }); } catch { /* already gone */ }
    return { ok: false, reason: 'QUEUE_WRITE_FAILED', detail: err && err.message };
  }
}

/**
 * 入队一个事件。重复的 `request_id` 直接返回 `{duplicate:true}`，不改动已有记录
 * —— 这正是「同一 request_id 重试只形成一个 event」的本地一半。
 */
function enqueue(appDataDir, { accountId, event, now = Date.now() } = {}) {
  if (!accountId) return { ok: false, reason: 'NO_ACCOUNT_BINDING' };
  if (!event || !event.request_id) return { ok: false, reason: 'EVENT_WITHOUT_REQUEST_ID' };
  const read = readQueue(appDataDir);
  const raw = (() => {
    try { return fs.readFileSync(queuePath(appDataDir), 'utf8'); } catch { return ''; }
  })();
  const existing = read.entries.find((e) => e.request_id === event.request_id);
  if (existing) return { ok: true, duplicate: true, entry: existing };
  if (read.entries.length >= MAX_ENTRIES) {
    return { ok: false, reason: 'QUEUE_FULL', limit: MAX_ENTRIES };
  }
  const entry = {
    schema: QUEUE_SCHEMA,
    request_id: event.request_id,
    account_id: accountId,
    enqueued_at: new Date(now).toISOString(),
    attempts: 0,
    next_attempt_at: new Date(now).toISOString(),
    last_error: null,
    event: {
      event_type: event.event_type,
      work_id: event.work_id,
      request_id: event.request_id,
      occurred_at: event.occurred_at,
      schema_version: event.schema_version,
      payload: event.payload,
      ...(event.client_id ? { client_id: event.client_id } : {}),
      ...(Number.isFinite(event.revision) ? { revision: event.revision } : {}),
    },
  };
  const lines = raw.split('\n').filter((l) => l.trim());
  lines.push(JSON.stringify(entry));
  const written = writeAll(appDataDir, lines);
  return written.ok ? { ok: true, duplicate: false, entry } : written;
}

/**
 * 标记结果。成功 → 记 `confirmed_at`（随后可压缩）；失败 → 记 attempts 与退避时间。
 * 只重写同一条记录所在的行，其他行原样保留（append-only 的实际形态）。
 */
function settle(appDataDir, { requestId, ok, error = null, now = Date.now() } = {}) {
  const file = queuePath(appDataDir);
  let raw;
  try { raw = fs.readFileSync(file, 'utf8'); } catch { return { ok: false, reason: 'QUEUE_UNREADABLE' }; }
  const lines = raw.split('\n');
  let touched = 0;
  const out = lines.map((line) => {
    const parsed = parseLine(line);
    if (!parsed || parsed.request_id !== requestId) return line;
    const next = { ...parsed };
    if (ok) {
      next.confirmed_at = new Date(now).toISOString();
      next.last_error = null;
    } else {
      next.attempts = (parsed.attempts || 0) + 1;
      // 第 1 次失败等 BASE_BACKOFF_MS，之后每次翻倍，直到上限
      next.next_attempt_at = new Date(now + backoffMs(next.attempts - 1)).toISOString();
      next.last_error = String(error || 'SYNC_FAILED').slice(0, 200);
    }
    touched += 1;
    return JSON.stringify(next);
  }).filter((line) => line.trim());
  if (!touched) return { ok: true, touched: 0 };
  const written = writeAll(appDataDir, out);
  return written.ok ? { ok: true, touched } : written;
}

/** 压缩：丢掉已确认记录，保留未确认与外来账户的记录。 */
function compact(appDataDir, { keepConfirmed = 0 } = {}) {
  const read = readQueue(appDataDir);
  if (!read.ok) return { ok: false, reason: read.reason };
  const file = queuePath(appDataDir);
  let lines = [];
  try { lines = fs.readFileSync(file, 'utf8').split('\n').filter((l) => l.trim()); } catch { lines = []; }
  const confirmed = [];
  const kept = [];
  for (const line of lines) {
    const parsed = parseLine(line);
    if (parsed && parsed.confirmed_at) confirmed.push(line);
    else kept.push(line);
  }
  const tail = keepConfirmed > 0 ? confirmed.slice(-keepConfirmed) : [];
  const written = writeAll(appDataDir, [...kept, ...tail]);
  return written.ok
    ? { ok: true, removed: confirmed.length - tail.length, remaining: kept.length + tail.length }
    : written;
}

/**
 * 解绑账户：事件**保留**，只去掉账户绑定。
 *
 * 这样「退出登录 → 重新登录同一账户」可以续传，而「登录另一个账户」不会把上一个账户
 * 的事件发过去（未绑定事件不会被任何账户选中，直到用户明确重新绑定）。
 */
function unbindAccount(appDataDir, { accountId } = {}) {
  const file = queuePath(appDataDir);
  let lines = [];
  try { lines = fs.readFileSync(file, 'utf8').split('\n').filter((l) => l.trim()); } catch { lines = []; }
  let touched = 0;
  const out = lines.map((line) => {
    const parsed = parseLine(line);
    if (!parsed || parsed.account_id !== accountId || parsed.confirmed_at) return line;
    touched += 1;
    return JSON.stringify({ ...parsed, account_id: null, released_at: new Date().toISOString() });
  });
  if (!touched) return { ok: true, touched: 0 };
  const written = writeAll(appDataDir, out);
  return written.ok ? { ok: true, touched } : written;
}

/** 重新登录同一账户时，把之前解绑的事件重新绑定回去（只有该账户自己的事件）。 */
function rebindAccount(appDataDir, { accountId, workIds = null } = {}) {
  const file = queuePath(appDataDir);
  let lines = [];
  try { lines = fs.readFileSync(file, 'utf8').split('\n').filter((l) => l.trim()); } catch { lines = []; }
  let touched = 0;
  const out = lines.map((line) => {
    const parsed = parseLine(line);
    if (!parsed || parsed.account_id !== null || !parsed.released_at || parsed.confirmed_at) return line;
    if (workIds && !workIds.includes(parsed.event && parsed.event.work_id)) return line;
    touched += 1;
    const next = { ...parsed, account_id: accountId };
    delete next.released_at;
    return JSON.stringify(next);
  });
  const written = touched ? writeAll(appDataDir, out) : { ok: true };
  return written.ok ? { ok: true, touched } : written;
}

function stats(appDataDir, { accountId } = {}) {
  const read = readQueue(appDataDir, { accountId });
  if (!read.ok) return { ok: false, reason: read.reason };
  const pending = read.entries.filter((e) => !e.confirmed_at);
  const failed = pending.filter((e) => (e.attempts || 0) > 0);
  return {
    ok: true,
    pending: pending.length,
    failed: failed.length,
    confirmed: read.entries.length - pending.length,
    foreign: read.foreign,
    diagnostics: read.diagnostics.length,
    nextAttemptAt: pending
      .map((e) => e.next_attempt_at)
      .filter(Boolean)
      .sort()[0] || null,
  };
}

module.exports = {
  QUEUE_SCHEMA,
  FILE_NAME,
  MAX_ENTRIES,
  BASE_BACKOFF_MS,
  MAX_BACKOFF_MS,
  backoffMs,
  queuePath,
  readQueue,
  pendingEntries,
  enqueue,
  settle,
  compact,
  unbindAccount,
  rebindAccount,
  stats,
};
