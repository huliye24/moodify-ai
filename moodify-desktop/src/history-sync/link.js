/**
 * `account_link.json` — the per-case binding to an account, and nothing else.
 *
 * Contract: `protocol/mips/MIP-0003-personal-identity-history.md` §2, §8
 *
 * The file records *which* cloud work a local case corresponds to and how far its history has
 * been pushed. It must never hold an email, an access/refresh token, or any remote key —
 * credentials live (encrypted) in the application data directory, never beside the user's work.
 *
 * Like the keepsake record, this file is **not authoritative**: deleting it disables nothing
 * except history sync for that case, and it can never advance a local stage.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const SCHEMA = 'moodify.studio.account-link/0.1';
const FILE_NAME = 'account_link.json';

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

const FORBIDDEN_KEYS = Object.freeze([
  'email', 'access_token', 'refresh_token', 'token', 'api_key', 'anon_key',
  'service_role_key', 'session', 'jwt', 'password', 'otp', 'magic_link', 'local_path',
]);

function linkPath(caseDir) {
  return path.join(caseDir, 'studio', FILE_NAME);
}

/** 读取。永不抛：损坏/缺失都只是「这个 case 没有开启同步」。 */
function readLink(caseDir) {
  let raw;
  try {
    raw = fs.readFileSync(linkPath(caseDir), 'utf8');
  } catch (err) {
    if (err && err.code === 'ENOENT') return { ok: true, link: null, error: null };
    return { ok: true, link: null, error: 'LINK_UNREADABLE' };
  }
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return { ok: true, link: null, error: 'LINK_CORRUPT_JSON' };
  }
  if (!parsed || typeof parsed !== 'object' || parsed.schema !== SCHEMA) {
    return { ok: true, link: null, error: 'LINK_SCHEMA_MISMATCH' };
  }
  for (const key of Object.keys(parsed)) {
    if (FORBIDDEN_KEYS.includes(key.toLowerCase())) {
      // 有人（或某个旧版本）把凭据写进了作品旁边：不接受、不静默删除，只拒绝使用
      return { ok: true, link: null, error: 'LINK_CONTAINS_FORBIDDEN_FIELD' };
    }
  }
  if (parsed.work_id && !UUID_RE.test(String(parsed.work_id))) {
    return { ok: true, link: null, error: 'LINK_BAD_WORK_ID' };
  }
  return { ok: true, link: parsed, error: null };
}

/** 原子写入（临时文件 + rename）。只允许本 case 内的这一个路径。 */
function writeLink(caseDir, patch = {}) {
  const previous = readLink(caseDir).link || {};
  const next = {
    schema: SCHEMA,
    work_id: patch.work_id !== undefined ? patch.work_id : (previous.work_id || null),
    sync_enabled: patch.sync_enabled !== undefined
      ? Boolean(patch.sync_enabled) : (previous.sync_enabled || false),
    last_pushed_revision: patch.last_pushed_revision !== undefined
      ? Number(patch.last_pushed_revision) || 0 : (previous.last_pushed_revision || 0),
    last_pulled_cursor: patch.last_pulled_cursor !== undefined
      ? patch.last_pulled_cursor : (previous.last_pulled_cursor || null),
    updated_at: new Date().toISOString(),
  };
  if (!next.work_id || !UUID_RE.test(String(next.work_id))) {
    return { ok: false, reason: 'BAD_WORK_ID' };
  }
  const dir = path.join(caseDir, 'studio');
  const file = linkPath(caseDir);
  const tmp = path.join(dir, `.${FILE_NAME}.tmp-${process.pid}-${crypto.randomBytes(4).toString('hex')}`);
  try {
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(tmp, JSON.stringify(next, null, 2), 'utf8');
    fs.renameSync(tmp, file);
  } catch (err) {
    try { fs.rmSync(tmp, { force: true }); } catch { /* already gone */ }
    return { ok: false, reason: 'LINK_WRITE_FAILED', detail: err && err.message };
  }
  return { ok: true, link: next };
}

/**
 * 为一个 case 生成/取得 work_id。
 *
 * 首次生成时会写进 `account_link.json`（`sync_enabled: false`）——work_id 从生成那一刻起稳定，
 * 而「是否同步」仍由用户显式确认控制。这样本地身份不需要联网，也不会因为一次重启就换 id。
 */
function ensureWorkId(caseDir, existing = null) {
  if (existing && UUID_RE.test(String(existing))) return String(existing).toLowerCase();
  const read = readLink(caseDir).link;
  if (read && read.work_id) return read.work_id;
  const generated = crypto.randomUUID();
  writeLink(caseDir, { work_id: generated, sync_enabled: false });
  return generated;
}

module.exports = { SCHEMA, FILE_NAME, FORBIDDEN_KEYS, linkPath, readLink, writeLink, ensureWorkId };
