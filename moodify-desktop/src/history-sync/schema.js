/**
 * History event schema — the **whitelist** boundary between the local case and the cloud.
 *
 * Contract: `protocol/mips/MIP-0003-personal-identity-history.md` §3, §4
 *
 * This module is the only place that decides what may leave the machine. Everything else in
 * the sync path is mechanical: if a payload is not validated here, it is never uploaded.
 *
 * Rules encoded below (all of them have tests in `scripts/test-sync.js`):
 *   • five event types, closed set — no free-form telemetry;
 *   • per-type payload whitelist — unknown or forbidden keys are rejected, not stripped;
 *   • a recursive scan for audio / paths / hashes / tokens as a second line of defence, so a
 *     future field cannot smuggle a local path in through a key nobody thought about;
 *   • `inscription` is user-provided text only: never inferred, never generated;
 *   • no listening duration, no play/pause counts, no search terms.
 */

'use strict';

const crypto = require('crypto');

const EVENT_SCHEMA = 'moodify.studio.history-event/0.1';

/** Phase 3A 闭集。新增类型必须走 MIP 变更，不得顺手加。 */
const EVENT_TYPES = Object.freeze([
  'WORK_COMPLETED',
  'DECISION_CHANGED',
  'INSCRIPTION_UPDATED',
  'AUDIO_EXPORTED',
  'WORK_REVISITED',
]);

const COMPLETION_MODES = Object.freeze(['DEEP', 'FAST_STEREO_ONLY']);
const SELECTIONS = Object.freeze(['A', 'B', 'ORIGINAL']);

/** 每个 event type 的 payload 白名单（键 → 校验器）。闭集：多余键即拒绝。 */
const PAYLOAD_SPEC = Object.freeze({
  WORK_COMPLETED: {
    title: { kind: 'title', required: true },
    duration_ms: { kind: 'duration' },
    completion_mode: { kind: 'enum', values: COMPLETION_MODES },
    selected: { kind: 'enum', values: SELECTIONS },
    completed_at: { kind: 'timestamp', required: true },
    inscription: { kind: 'inscription' },
  },
  DECISION_CHANGED: {
    selected: { kind: 'enum', values: SELECTIONS, required: true },
    title: { kind: 'title' },
  },
  INSCRIPTION_UPDATED: {
    inscription: { kind: 'inscription' },
    title: { kind: 'title' },
  },
  AUDIO_EXPORTED: {
    selected: { kind: 'enum', values: SELECTIONS, required: true },
    title: { kind: 'title' },
  },
  WORK_REVISITED: {
    title: { kind: 'title' },
  },
});

/** 无论出现在哪一层都绝不允许的键名（音频、路径、证据、凭据、行为遥测）。 */
const FORBIDDEN_KEYS = Object.freeze([
  'audio', 'audio_bytes', 'wav', 'mp3', 'flac', 'pcm', 'samples',
  'stems', 'stem', 'midi', 'musicxml', 'score', 'report', 'evidence', 'spectrum', 'spectra',
  'charts', 'mix_graph', 'plan', 'parameters', 'nodes', 'graph_digest_sha256',
  'path', 'paths', 'case_dir', 'casedir', 'case_path', 'source_path', 'mix_path', 'absolute_path',
  'source_sha256', 'sha256', 'hash', 'checksum', 'digest',
  'token', 'access_token', 'refresh_token', 'otp', 'magic_link', 'api_key', 'service_role_key',
  'email', 'user_id', 'session', 'jwt',
  'listening_ms', 'play_count', 'pause_count', 'search_terms', 'listening_duration',
  'terminal_log', 'logs', 'stderr', 'stdout',
]);

/** 值的形状级禁令：绝对路径、64 位十六进制、jwt/URL 里的凭据。 */
const FORBIDDEN_VALUE_PATTERNS = Object.freeze([
  { label: 'windows absolute path', re: /[A-Za-z]:\\[^\s]*/ },
  { label: 'posix absolute path', re: /\/(Users|home|var|tmp|mnt|Volumes)\/[^\s]*/ },
  { label: 'sha256 hex', re: /\b[0-9a-f]{64}\b/i },
  { label: 'jwt', re: /\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\./ },
  { label: 'magic link url', re: /https?:\/\/[^\s]*\/(auth|verify|magic)[^\s]*/i },
  { label: 'file uri', re: /file:\/\/[^\s]*/i },
]);

class HistorySchemaError extends Error {
  constructor(reason, detail) {
    super(`${reason}${detail ? `: ${detail}` : ''}`);
    this.name = 'HistorySchemaError';
    this.reason = reason;
    this.detail = detail || null;
  }
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

/**
 * 键名按「词段」比对：`spectrum_log`、`source_sha256`、`audio_bytes` 都要被抓住，
 * 而不是只抓完全等于 `spectrum` 的键。
 */
function keyIsForbidden(key) {
  const lower = String(key).toLowerCase();
  if (FORBIDDEN_KEYS.includes(lower)) return true;
  const segments = lower.split(/[^a-z0-9]+/).filter(Boolean);
  return segments.some((segment) => FORBIDDEN_KEYS.includes(segment));
}

/**
 * 深度扫描：任何层级出现禁止键或禁止值形状都抛错。
 *
 * 这是「数据最小化」的第二道防线（第一道是按 type 的白名单）。它不是字符串替换——
 * 发现可疑内容时**拒绝上传**，而不是悄悄改掉，因为静默改写会让用户以为素材已经同步。
 */
function assertNoForbiddenData(value, trail = '$') {
  if (value === null || value === undefined) return;
  if (Array.isArray(value)) {
    value.forEach((item, i) => assertNoForbiddenData(item, `${trail}[${i}]`));
    return;
  }
  if (isPlainObject(value)) {
    for (const [key, item] of Object.entries(value)) {
      if (keyIsForbidden(key)) {
        throw new HistorySchemaError('FORBIDDEN_FIELD', `${trail}.${key}`);
      }
      assertNoForbiddenData(item, `${trail}.${key}`);
    }
    return;
  }
  if (typeof value === 'string') {
    for (const { label, re } of FORBIDDEN_VALUE_PATTERNS) {
      if (re.test(value)) throw new HistorySchemaError('FORBIDDEN_VALUE', `${trail} (${label})`);
    }
  }
}

function checkTitle(value, key) {
  if (typeof value !== 'string') throw new HistorySchemaError('BAD_TITLE', key);
  const text = value.trim();
  if (!text) throw new HistorySchemaError('BAD_TITLE', key);
  if ([...text].length > 300) throw new HistorySchemaError('TITLE_TOO_LONG', key);
  return text;
}

/**
 * 一句话：完全可选、用户自己写的。空串是合法值（清空是普通编辑行为）。
 * 280 码位 / 4 行的边界与 `src/keepsake.js` 保持一致——同一条规则不在两处生效两种结果。
 */
function checkInscription(value, key) {
  if (value === null || value === undefined) return null;
  if (typeof value !== 'string') throw new HistorySchemaError('BAD_INSCRIPTION', key);
  const text = value.replace(/\r\n?/g, '\n');
  if ([...text].length > 280) throw new HistorySchemaError('INSCRIPTION_TOO_LONG', key);
  if (text.split('\n').length > 4) throw new HistorySchemaError('INSCRIPTION_TOO_MANY_LINES', key);
  return text;
}

function checkDuration(value, key) {
  if (value === null || value === undefined) return null;
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0) {
    throw new HistorySchemaError('BAD_DURATION', key);
  }
  if (value > 24 * 3600 * 1000) throw new HistorySchemaError('DURATION_OUT_OF_RANGE', key);
  return Math.round(value);
}

function checkTimestamp(value, key) {
  if (typeof value !== 'string') throw new HistorySchemaError('BAD_TIMESTAMP', key);
  const time = Date.parse(value);
  if (Number.isNaN(time)) throw new HistorySchemaError('BAD_TIMESTAMP', key);
  return new Date(time).toISOString();
}

function checkEnum(value, key, values) {
  if (!values.includes(value)) throw new HistorySchemaError('BAD_ENUM', `${key}=${value}`);
  return value;
}

const CHECKERS = {
  title: checkTitle,
  inscription: checkInscription,
  duration: checkDuration,
  timestamp: checkTimestamp,
  enum: checkEnum,
};

/** 按 event type 校验 payload：缺失必填项、未知键、类型错误一律拒绝。 */
function validatePayload(eventType, payload) {
  if (!EVENT_TYPES.includes(eventType)) {
    throw new HistorySchemaError('UNKNOWN_EVENT_TYPE', eventType);
  }
  if (!isPlainObject(payload)) throw new HistorySchemaError('PAYLOAD_NOT_AN_OBJECT', eventType);
  const spec = PAYLOAD_SPEC[eventType];
  const out = {};
  for (const key of Object.keys(payload)) {
    if (!Object.prototype.hasOwnProperty.call(spec, key)) {
      throw new HistorySchemaError('UNKNOWN_PAYLOAD_FIELD', `${eventType}.${key}`);
    }
  }
  for (const [key, rule] of Object.entries(spec)) {
    const raw = payload[key];
    if (raw === undefined || raw === null || raw === '') {
      if (rule.required) throw new HistorySchemaError('MISSING_REQUIRED_FIELD', `${eventType}.${key}`);
      continue;
    }
    const checker = CHECKERS[rule.kind];
    out[key] = rule.kind === 'enum' ? checker(raw, key, rule.values) : checker(raw, key);
  }
  assertNoForbiddenData(out, `payload(${eventType})`);
  return out;
}

/**
 * 构造一个可上传事件。
 *
 * `request_id` 由调用方提供时保持不变（重试幂等的前提）；未提供则生成一次。
 * `occurred_at` 是本地事实发生的时间，`client_id` 只用于同账户多设备诊断。
 */
function buildEvent({ eventType, workId, payload, requestId, occurredAt, clientId, revision }) {
  if (!EVENT_TYPES.includes(eventType)) {
    throw new HistorySchemaError('UNKNOWN_EVENT_TYPE', eventType);
  }
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(String(workId || ''))) {
    throw new HistorySchemaError('BAD_WORK_ID', String(workId || ''));
  }
  const event = {
    event_type: eventType,
    work_id: String(workId).toLowerCase(),
    request_id: (requestId || crypto.randomUUID()).toLowerCase(),
    occurred_at: occurredAt ? checkTimestamp(occurredAt, 'occurred_at') : new Date().toISOString(),
    schema_version: EVENT_SCHEMA,
    payload: validatePayload(eventType, payload),
  };
  if (clientId) event.client_id = String(clientId).toLowerCase();
  if (Number.isFinite(revision)) event.revision = Math.max(0, Math.trunc(revision));
  assertNoForbiddenData(event, 'event');
  return event;
}

/** 响应/日志里只允许出现这三样（MIP §8：不把 payload 打进日志）。 */
function logLine(event) {
  return JSON.stringify({
    event_type: event.event_type,
    request_id: event.request_id,
    status: event.status || 'pending',
  });
}

module.exports = {
  EVENT_SCHEMA,
  EVENT_TYPES,
  COMPLETION_MODES,
  SELECTIONS,
  PAYLOAD_SPEC,
  FORBIDDEN_KEYS,
  FORBIDDEN_VALUE_PATTERNS,
  HistorySchemaError,
  keyIsForbidden,
  assertNoForbiddenData,
  validatePayload,
  buildEvent,
  logLine,
};
