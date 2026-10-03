/**
 * Backend registry — Studio v0.2 section 3.
 *
 * "跑分析 / 跑后处理" must be abstracted behind a switchable interface, so the UI never
 * binds directly to a local-path assumption and a cloud backend can be added later
 * without touching the interface layer.
 *
 * CONTRACT — every backend implements exactly this:
 *
 *   kind    : 'local' | 'cloud'
 *   label   : short human label for the UI
 *   process({ sourcePath, target, versionDir, attemptId }, deps)
 *             -> { ok: true,  versionDir, output, evidencePath, evidence }
 *             -> { ok: false, reason, code? }
 *
 * The result shape is deliberately the same for both: Studio v0.2 section 3 says the UI
 * is driven by "结果清单 + 证据" from the backend, not by local paths it computed itself.
 *
 * THE CLOUD BACKEND IS NOT IMPLEMENTED, AND SAYS SO.
 * Phase 1 is local-only (section 7). The cloud entry exists so the interface is real and
 * the UI can show 云端即将推出 honestly — it returns a plain "not implemented" error
 * rather than silently falling back to local, because a backend that quietly does
 * something other than what the user selected is worse than one that refuses.
 */

'use strict';

const local = require('./local');

const NOT_IMPLEMENTED = {
  kind: 'cloud',
  label: '云端（即将推出）',
  implemented: false,
  async process() {
    return {
      ok: false,
      reason: '云端处理尚未实现（第 1 期仅支持本机）。接口已预留，未做静默回退。',
    };
  },
};

const BACKENDS = {
  local,
  cloud: NOT_IMPLEMENTED,
};

const DEFAULT_MODE = 'local';

function getBackend(mode) {
  const key = String(mode || DEFAULT_MODE);
  const backend = BACKENDS[key];
  if (!backend) {
    throw new Error(`未知后端：${key}（可用：${Object.keys(BACKENDS).join(', ')}）`);
  }
  return backend;
}

/** What the UI needs to render the backend choice without hardcoding either one. */
function describeBackends() {
  return Object.entries(BACKENDS).map(([mode, b]) => ({
    mode,
    kind: b.kind,
    label: b.label,
    implemented: b.implemented !== false,
  }));
}

module.exports = { getBackend, describeBackends, DEFAULT_MODE };
