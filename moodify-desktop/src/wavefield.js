/**
 * Moodify Studio — Wave Field lane boundary (experimental, opt-in).
 *
 * 这一层只做四件事：**定位** case 内的波场目录、**调用** Python runner、
 * **校验**预期产物是否存在、把状态交给 main/preload/renderer。
 *
 * 它**不实现任何音频算法**——渲染在 Core（moodify.wavefield.renderer），
 * 听测在 Core（moodify.wavefield.hearing），账本在 Core（moodify.wavefield.record）。
 * 壳里再写一份渲染实现，就是 "One Core" 被破坏的那一刻。
 *
 * 本模块是纯 Node（无 Electron 依赖），可 headless 测试：所有外部调用都通过
 * 注入的 `run(args, input)` 发生。
 *
 * 默认关闭：只有 MOODIFY_WAVEFIELD_V0=1 时产品面才出现。
 * 未开启时，已发布 Studio 的行为必须完全不变。
 */

'use strict';

const fs = require('fs');
const path = require('path');

/** 开关。未设置或为非 '1' 值 = 关闭（不静默启用未完成的实验流程）。 */
const FLAG_ENV = 'MOODIFY_WAVEFIELD_V0';

/** runner 相对本模块的默认位置。 */
const DEFAULT_RUNNER = path.join(__dirname, '..', 'scripts', 'wavefield_runner.py');

/** 产品面只有四个出口：原版 + 三个探针。 */
const CANDIDATE_IDS = ['A', 'B', 'C'];
const CHOICES = ['ORIGINAL', 'A', 'B', 'C'];
const ROLES = ['creator', 'listener', 'pro'];

/** runner 支持的 action（与 scripts/wavefield_runner.py 的 HANDLERS 对齐）。 */
const ACTIONS = ['create-session', 'render-search', 'inspect', 'choose', 'export'];

const LAYOUT = {
  session: 'session.json',
  search: 'search.json',
  candidates: 'candidates',
  fields: 'fields',
  renders: 'renders',
  hearing: 'hearing',
  decisions: 'decisions.jsonl',
  export: 'export',
};

// ——— 开关 ————————————————————————————————————————————————————————————————

/**
 * 是否启用波场通道。
 * @param {NodeJS.ProcessEnv} [env]
 */
function enabled(env = process.env) {
  return String((env && env[FLAG_ENV]) || '').trim() === '1';
}

function isValidChoice(value) {
  return CHOICES.includes(value);
}

function isValidRole(value) {
  return ROLES.includes(value);
}

// ——— 路径 ————————————————————————————————————————————————————————————————

/** 波场通道挂在既有 Studio 子树里，绝不另建 case root。 */
function wavefieldDir(caseDir) {
  return path.join(String(caseDir), 'studio', 'wavefield');
}

function sessionPath(caseDir) { return path.join(wavefieldDir(caseDir), LAYOUT.session); }
function searchPath(caseDir) { return path.join(wavefieldDir(caseDir), LAYOUT.search); }
function candidatesDir(caseDir) { return path.join(wavefieldDir(caseDir), LAYOUT.candidates); }
function fieldsDir(caseDir) { return path.join(wavefieldDir(caseDir), LAYOUT.fields); }
function rendersDir(caseDir) { return path.join(wavefieldDir(caseDir), LAYOUT.renders); }
function hearingDir(caseDir) { return path.join(wavefieldDir(caseDir), LAYOUT.hearing); }
function decisionsPath(caseDir) { return path.join(wavefieldDir(caseDir), LAYOUT.decisions); }
function exportDir(caseDir) { return path.join(wavefieldDir(caseDir), LAYOUT.export); }

/** 候选音频路径。ORIGINAL 没有独立文件——它指向源音频。 */
function candidateAudioPath(caseDir, candidateId) {
  if (candidateId === 'ORIGINAL') return null;
  if (!CANDIDATE_IDS.includes(candidateId)) return null;
  return path.join(candidatesDir(caseDir), `${candidateId}.wav`);
}

// ——— 读取 ————————————————————————————————————————————————————————————————

function readJsonSafe(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return null; }
}

function fileRow(file) {
  let stat = null;
  try { stat = fs.statSync(file); } catch { /* absent is data, not an error */ }
  return {
    path: file,
    exists: Boolean(stat && stat.isFile()),
    size: stat ? stat.size : null,
    mtime: stat ? stat.mtimeMs : null,
  };
}

/** 只追加的人类选择账本。坏行跳过，不影响其余记录。 */
function readDecisions(caseDir) {
  let text = '';
  try { text = fs.readFileSync(decisionsPath(caseDir), 'utf8'); } catch { return []; }
  const rows = [];
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try { rows.push(JSON.parse(trimmed)); } catch { /* torn line from an interrupted append */ }
  }
  return rows;
}

function lastJsonLine(text) {
  for (const line of String(text || '').trimEnd().split('\n').reverse()) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try { return JSON.parse(trimmed); } catch { /* keep scanning */ }
  }
  return null;
}

function lastOutputLine(text, max = 300) {
  const lines = String(text || '').trimEnd().split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  if (!lines.length) return null;
  const line = lines[lines.length - 1];
  return line.length > max ? line.slice(-max) : line;
}

/**
 * 当前波场状态 —— **只从磁盘推导**，不缓存、不猜测。
 *
 * 缺失就是缺失：没有产物会写成 `exists:false` 并给出 blocker，
 * 而不是被补一个默认值糊过去。
 */
function readState(caseDir) {
  const root = wavefieldDir(caseDir);
  const present = fs.existsSync(root);
  if (!present) {
    return {
      enabled: true,
      present: false,
      caseDir: String(caseDir),
      wavefieldDir: root,
      session: null,
      policy: null,
      candidates: {},
      fields: {},
      hearing: {},
      summary: {},
      judgment: {},
      decisions: [],
      chosen: null,
      export: null,
      blockers: ['NO_WAVEFIELD_SESSION'],
      warnings: [],
    };
  }

  const session = readJsonSafe(sessionPath(caseDir));
  const policy = readJsonSafe(searchPath(caseDir));
  const sourcePath = session && session.source_path ? session.source_path : null;

  const candidates = {};
  const fields = {};
  const hearing = {};
  const summary = {};
  const judgment = {};
  const blockers = [];
  const warnings = [];

  // ORIGINAL 永远是可用出口：它指向源音频，本通道不复刻它。
  const sourceExists = Boolean(sourcePath && fs.existsSync(sourcePath));
  candidates.ORIGINAL = {
    id: 'ORIGINAL',
    label: '原版',
    path: sourcePath,
    exists: sourceExists,
    size: null,
    mtime: null,
  };
  if (!sourceExists) warnings.push('ORIGINAL_SOURCE_UNREADABLE');

  for (const candidateId of CANDIDATE_IDS) {
    const row = fileRow(path.join(candidatesDir(caseDir), `${candidateId}.wav`));
    candidates[candidateId] = { id: candidateId, label: candidateId, ...row };

    const field = readJsonSafe(path.join(fieldsDir(caseDir), `${candidateId}.json`));
    fields[candidateId] = field;
    const render = readJsonSafe(path.join(rendersDir(caseDir), `${candidateId}.json`));
    candidates[candidateId].render = render;
    candidates[candidateId].stale = Boolean(
      render && row.exists && render.output_sha256
      && path.basename(render.output_path || '') !== `${candidateId}.wav`
    );

    if (!row.exists) blockers.push(`CANDIDATE_MISSING:${candidateId}`);
    if (!field) blockers.push(`FIELD_MISSING:${candidateId}`);
  }

  for (const id of ['ORIGINAL', ...CANDIDATE_IDS]) {
    const snapshot = readJsonSafe(path.join(hearingDir(caseDir), `${id}.json`));
    hearing[id] = snapshot;
    if (!snapshot) blockers.push(`HEARING_MISSING:${id}`);
    summary[id] = snapshot ? humanSummary(snapshot) : null;
    judgment[id] = snapshot && snapshot.judge ? {
      technical_status: snapshot.judge.technical_status,
      blocking_flags: snapshot.judge.blocking_flags || [],
      warnings: snapshot.judge.warnings || [],
      informational_flags: snapshot.judge.informational_flags || [],
      reasons: snapshot.judge.reasons || [],
    } : null;
  }

  const decisions = readDecisions(caseDir);
  const chosen = decisions.length ? decisions[decisions.length - 1] : null;
  const exportManifest = readJsonSafe(path.join(exportDir(caseDir), 'manifest.json'));

  // 阻断顺序即「下一步该做什么」，不是一串错误码。
  const ordered = [];
  if (!session) ordered.push('SESSION_MISSING');
  if (!CANDIDATE_IDS.some((id) => candidates[id].exists)) ordered.push('NO_CANDIDATES');
  for (const id of CANDIDATE_IDS) {
    if (!candidates[id].exists && CANDIDATE_IDS.some((x) => candidates[x].exists)) {
      ordered.push(`CANDIDATE_MISSING:${id}`);
    }
  }
  if (!chosen) ordered.push('NOT_CHOSEN');
  else if (chosen.kept !== 'ORIGINAL' && !candidates[chosen.kept].exists) {
    ordered.push('CHOSEN_CANDIDATE_MISSING');
  }
  for (const id of ['ORIGINAL', ...CANDIDATE_IDS]) {
    if (!hearing[id]) ordered.push(`HEARING_MISSING:${id}`);
  }

  return {
    enabled: true,
    present: true,
    caseDir: String(caseDir),
    wavefieldDir: root,
    session,
    policy,
    candidates,
    fields,
    hearing,
    summary,
    judgment,
    decisions,
    chosen,
    export: exportManifest,
    blockers: ordered.length ? ordered : (blockers.length ? blockers : []),
    warnings,
    choices: CHOICES.slice(),
    policyCandidates: policy && Array.isArray(policy.probes)
      ? policy.probes.map((probe) => ({
        candidateId: probe.candidate_id,
        fieldId: probe.field_id,
        intent: probe.intent,
        parameters: probe.parameters,
      }))
      : [],
  };
}

/** 最小 UI 需要的几个数：全部照抄 HearSnapshot，不新增任何计算。 */
function humanSummary(snapshot) {
  const metrics = (snapshot && snapshot.metrics) || {};
  const value = (key) => {
    const entry = metrics[key];
    return entry && typeof entry === 'object' ? entry.value : null;
  };
  const comparison = snapshot.source_comparison || null;
  const judge = snapshot.judge || {};
  return {
    integrated_lufs: value('integrated_lufs'),
    true_peak_dbfs: value('true_peak_dbfs'),
    crest_factor_db: value('crest_factor_db'),
    stereo_correlation: value('stereo_correlation'),
    stereo_width_proxy: value('stereo_width_proxy'),
    side_to_mid_db: value('side_to_mid_db'),
    negative_correlation_ratio: value('negative_correlation_ratio'),
    phase_risk_ratio: value('phase_risk_ratio'),
    duration_seconds: value('duration'),
    sample_rate: value('sample_rate'),
    channels: value('channels'),
    technical_status: judge.technical_status || null,
    blocking_flags: judge.blocking_flags || [],
    warnings: judge.warnings || [],
    is_reference: Boolean(snapshot.is_reference),
    audition_correction_db: comparison ? comparison.audition_correction_db : null,
  };
}

// ——— 调用 runner ————————————————————————————————————————————————————————

/**
 * 与 runner 的一次往返。**不含任何算法**，只做协议与错误归因。
 *
 * @param {(args: string[], input: string) => Promise<{code:number, stdout:string, stderr:string}>} run
 * @param {string} runnerPath
 * @param {string} action
 * @param {object} payload
 */
async function invoke(run, runnerPath, action, payload = {}) {
  if (!ACTIONS.includes(action)) {
    return { ok: false, reason: 'UNKNOWN_ACTION', detail: `未知的 runner action：${action}` };
  }
  if (typeof run !== 'function') {
    return { ok: false, reason: 'RUNNER_UNAVAILABLE', detail: '没有可用的 runner 调用通道' };
  }

  let result;
  try {
    result = await run([runnerPath, action], JSON.stringify({ ...payload, action }));
  } catch (err) {
    // 起不来（python 缺失 / 路径错）也必须说清，而不是静默返回空状态。
    return { ok: false, reason: 'RUNNER_UNAVAILABLE', detail: (err && err.message) || String(err) };
  }

  const payloadOut = lastJsonLine(result.stdout);
  const failure = lastJsonLine(result.stderr);
  if (result.code === 0 && payloadOut && payloadOut.ok !== false) {
    return { ok: true, code: 0, payload: payloadOut };
  }
  return {
    ok: false,
    code: result.code,
    reason: (failure && failure.code) || (payloadOut && payloadOut.code) || 'RUNNER_FAILED',
    detail: (failure && failure.detail)
      || (payloadOut && payloadOut.detail)
      || lastOutputLine(result.stderr)
      || `runner 退出码 ${result.code}`,
  };
}

/**
 * runner 客户端：把五个动作包成方法，并在本地做**廉价**的输入校验。
 *
 * 权威校验仍在 Core（runner + moodify.wavefield.record）：这里只是让明显非法的
 * 请求不必要地启动一个 python 进程。
 */
function createClient({ run, runnerPath = DEFAULT_RUNNER } = {}) {
  const call = (action, payload) => invoke(run, runnerPath, action, payload);

  return {
    createSession: (caseDir, sourcePath) =>
      call('create-session', { case_dir: String(caseDir), source_path: sourcePath || undefined }),
    renderSearch: (caseDir) => call('render-search', { case_dir: String(caseDir) }),
    inspect: (caseDir) => call('inspect', { case_dir: String(caseDir) }),

    async choose(caseDir, kept, role = 'creator', requestId = null) {
      if (!isValidChoice(kept)) {
        return { ok: false, reason: 'BAD_KEPT', detail: `只能选择 ${CHOICES.join(' / ')}` };
      }
      if (!isValidRole(role)) {
        return { ok: false, reason: 'BAD_ROLE', detail: `角色必须是 ${ROLES.join(' / ')}` };
      }
      return call('choose', {
        case_dir: String(caseDir),
        kept,
        role,
        request_id: requestId || undefined,
      });
    },

    /**
     * 导出。**没有记录过选择就不导出**——出口必须与账本一致，
     * 不允许导出「没选过的东西」。
     */
    async exportChosen(caseDir, kept = null) {
      const state = readState(caseDir);
      if (!state.chosen) {
        return { ok: false, reason: 'NOT_CHOSEN', detail: '请先选定 A / B / C 或保留原版。' };
      }
      if (kept && state.chosen.kept !== kept) {
        return {
          ok: false,
          reason: 'NOT_CHOSEN',
          detail: `账本里选的是 ${state.chosen.kept}，不是 ${kept}。`,
        };
      }
      return call('export', { case_dir: String(caseDir) });
    },
  };
}

module.exports = {
  ACTIONS,
  CANDIDATE_IDS,
  CHOICES,
  DEFAULT_RUNNER,
  FLAG_ENV,
  LAYOUT,
  ROLES,
  candidateAudioPath,
  candidatesDir,
  createClient,
  decisionsPath,
  enabled,
  exportDir,
  fieldsDir,
  hearingDir,
  humanSummary,
  invoke,
  isValidChoice,
  isValidRole,
  lastJsonLine,
  readDecisions,
  readJsonSafe,
  readState,
  rendersDir,
  sessionPath,
  searchPath,
  wavefieldDir,
};
