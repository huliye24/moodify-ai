/**
 * ④ 修音 / ⑤ 复合 的产物层 + ⑦ 选定 的三出口决策账本
 *
 * CONTRACT: docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md
 *
 * 目录形状
 *   <case>/studio/tuning/
 *     <pair_id>/
 *       pair.json            两档参数 + mode(DEEP|FAST_STEREO_ONLY) + calibration_status
 *       A/  plan.json  tuned/*.wav  mix.wav  evidence.json  recheck 见 recheck.js
 *       B/  plan.json  tuned/*.wav  mix.wav  evidence.json
 *       recheck.json         ⑤ 复检三方对齐表（由 src/recheck.js 写）
 *     decisions.jsonl        ⑦ 选定，只追加
 *
 * 为什么「修音」与「复合」是两个目录层级而不是一个
 *   修音改的是**每根轨**（音准 / 节奏 / 逐轨处理），复合决定的是**它们如何叠在一起**
 *   （平衡 / 空间 / 响度）。前者可以逐轨回退，后者是整曲判断。混在一起写，
 *   就无法回答「这一步变差是哪一层造成的」——而「可归因」是本流程的硬要求。
 *   所以 `tuned/` 与 `mix.wav` 是两个独立产物，`pipeline.js` 也据此分成两个阶段。
 *
 * 为什么 A / B 必须成对
 *   单边产物是半成品。`tuned` / `composed` 只在两侧都齐时才成立——
 *   与 V3「拒绝半成品方案」同一条纪律，也与 MIP-0002 的 pair 契约一致。
 *
 * 三出口（2026-10-04 裁定）
 *   `kept` ∈ A / B / **ORIGINAL**。第三个出口是「保留原版」：
 *   若两档都不如原版，用户必须有路可退，否则最小变换原则就成了空话。
 *   账本只追加、不可修改；带 `request_id` 时幂等（重试不会写两条）。
 */

'use strict';

const fs = require('fs');
const path = require('path');
// recheck.js 只依赖 fs/path，不反向依赖本文件 —— 方向是 tuning → recheck，无环。
const recheck = require('./recheck');

const TUNING_DIR = 'tuning';
const DECISIONS_FILE = 'decisions.jsonl';
const SIDE_DIRS = Object.freeze(['A', 'B']);
/** A / B 是两档候选，ORIGINAL 是「都不选，保留原版」。 */
const EXITS = Object.freeze(['A', 'B', 'ORIGINAL']);
const ROLES = Object.freeze(['creator', 'listener', 'pro']);
const SCHEMA_DECISION = 'moodify.studio.tuning-decision/0.1';

function tuningDir(caseDir) { return path.join(caseDir, 'studio', TUNING_DIR); }
function pairDir(caseDir, pairId) { return path.join(tuningDir(caseDir), String(pairId || '')); }
function sideDir(caseDir, pairId, side) { return path.join(pairDir(caseDir, pairId), side); }
function decisionsPath(caseDir) { return path.join(tuningDir(caseDir), DECISIONS_FILE); }

function readJsonSafe(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return null; }
}

function listFiles(dir, exts) {
  let entries = [];
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return []; }
  return entries
    .filter((e) => e.isFile() && exts.some((x) => e.name.toLowerCase().endsWith(x)))
    .map((e) => path.join(dir, e.name))
    .sort();
}

/**
 * 新 pair 的唯一 id。
 *
 * 时间戳带**毫秒**（`tune_YYYYMMDDHHMMSSmmm_rand`）：唯一性仍然是 load-bearing
 * （Core 拒绝覆盖已存在输出，也保证「再试一次」不静默覆盖已确认的版本），
 * 但排序不再依赖它 —— 同秒内建两个 pair 时，只到秒的时间戳 + 随机后缀会让顺序随机，
 * 而 V4 的 `currentPair` 是阶段推导依据。排序以 `pair.json.created_at` / 目录 mtime 为准。
 */
function newPairId(now = new Date()) {
  const stamp = now.toISOString().replace(/[-:TZ.]/g, '').slice(0, 17);
  const rand = Math.random().toString(36).slice(2, 6);
  return `tune_${stamp}_${rand}`;
}

function createPairDir(caseDir, pairId) {
  const dir = pairDir(caseDir, pairId);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

/** 一侧的产物状态。`tuned/` 在深度路径是逐轨 wav，在快速路径是单个整轨 wav —— 判据相同。 */
function sideState(caseDir, pairId, side) {
  const dir = sideDir(caseDir, pairId, side);
  const tuned = listFiles(path.join(dir, 'tuned'), ['.wav']);
  const mix = path.join(dir, 'mix.wav');
  const plan = path.join(dir, 'plan.json');
  const evidence = path.join(dir, 'evidence.json');
  const report = path.join(dir, 'analysis', 'report.json');
  return {
    dir,
    tuned,
    tuned_count: tuned.length,
    has_tuned: tuned.length > 0,
    mix: fs.existsSync(mix) ? mix : null,
    has_mix: fs.existsSync(mix),
    plan: fs.existsSync(plan) ? plan : null,
    evidence: fs.existsSync(evidence) ? evidence : null,
    report: fs.existsSync(report) ? report : null,
  };
}

/**
 * 一个修音对的完整状态。
 * `tuned` / `composed` **只在两侧都齐时**为 true —— 单边不成阶段。
 */
function pairState(caseDir, pairId) {
  const dir = pairDir(caseDir, pairId);
  const pair = readJsonSafe(path.join(dir, 'pair.json'));
  const A = sideState(caseDir, pairId, 'A');
  const B = sideState(caseDir, pairId, 'B');
  const recheck = path.join(dir, 'recheck.json');
  const hasRecheck = fs.existsSync(recheck);
  return {
    pair_id: pairId,
    dir,
    pair,
    mode: (pair && pair.mode) || null,
    A,
    B,
    tuned: A.has_tuned && B.has_tuned,
    composed: A.has_mix && B.has_mix,
    recheck: hasRecheck ? recheck : null,
    has_recheck: hasRecheck,
    complete: A.has_mix && B.has_mix && hasRecheck,
  };
}

/** 全部修音对，旧 → 新。 */
function listPairs(caseDir) {
  let entries = [];
  try { entries = fs.readdirSync(tuningDir(caseDir), { withFileTypes: true }); } catch { return []; }
  return entries
    .filter((e) => e.isDirectory() && e.name.startsWith('tune_'))
    .map((e) => e.name)
    .sort((a, b) => {
      const ta = createdAtMs(caseDir, a);
      const tb = createdAtMs(caseDir, b);
      return ta === tb ? (a < b ? -1 : a > b ? 1 : 0) : ta - tb;
    })
    .map((id) => pairState(caseDir, id));
}

/**
 * 建对时间（毫秒）。
 *
 * 为什么不能按 id 排序：`newPairId()` 的时间戳只到**秒**，后面的随机后缀在同秒内是任意的。
 * V3 用 `ai_<stamp>_<rand>` 时也这样，但那时只有「列表顺序」受影响；V4 里「最新的一对」
 * 是阶段推导的依据（`currentPair`），排序错了会让阶段随机跳。所以这里优先用 `pair.json`
 * 的 `created_at`，退而用目录 mtime —— **id 不再是排序权威**。
 */
function createdAtMs(caseDir, pairId) {
  const pair = readJsonSafe(path.join(pairDir(caseDir, pairId), 'pair.json'));
  if (pair && pair.created_at) {
    const t = Date.parse(pair.created_at);
    if (Number.isFinite(t)) return t;
  }
  try { return fs.statSync(pairDir(caseDir, pairId)).mtimeMs; } catch { return 0; }
}

/** 最新的一对（阶段游标依据它推导）。 */
function currentPair(caseDir) {
  const all = listPairs(caseDir);
  return all.length ? all[all.length - 1] : null;
}

/**
 * 整个 case 的达成度聚合。
 *
 * 用 `some` 而不是只看最新一对：做完一对再去开新的一对，是往前走，不是往回退。
 * 若只看最新一对，开一个新的实验就会让阶段倒退 —— 那会谎报"进度丢了"。
 * （`currentPair` 仍是最新一对，供 UI 决定"现在在操作哪一对"。）
 */
function aggregate(caseDir) {
  const pairs = listPairs(caseDir);
  const decisions = readDecisions(caseDir);
  return {
    pairs,
    current: pairs.length ? pairs[pairs.length - 1] : null,
    count: pairs.length,
    any_tuned: pairs.some((p) => p.tuned),
    any_composed: pairs.some((p) => p.composed),
    any_rechecked: pairs.some((p) => p.has_recheck),
    decisions,
    any_chosen: decisions.length > 0,
    // 已选定且仍完整的一对（产物都还在），否则 null
    chosen_pair: (() => {
      const last = decisions.length ? decisions[decisions.length - 1] : null;
      if (!last) return null;
      return pairs.find((p) => p.pair_id === last.pair_id) || null;
    })(),
  };
}

// ── ⑦ 选定：三出口账本 ──────────────────────────────────────────────────────────

function readDecisions(caseDir) {
  let raw = '';
  try { raw = fs.readFileSync(decisionsPath(caseDir), 'utf8'); } catch { return []; }
  return raw.split('\n').filter(Boolean)
    .map((line) => { try { return JSON.parse(line); } catch { return null; } })
    .filter(Boolean);
}

function decisionFor(caseDir, pairId) {
  const rows = readDecisions(caseDir).filter((r) => r && r.pair_id === pairId);
  return rows.length ? rows[rows.length - 1] : null;
}

/**
 * ⑦ 选定 的准入校验 —— **唯一一条规则**。
 *
 * 写（appendDecision）与读（pipeline 的 `chosen` 事实，经 decisionBacked）共用这份实现，
 * 所以不会出现「能写进去、推导却不认」或反过来的两套标准。
 *
 * 三个条件必须同时成立：
 *   1. 修音对真实存在（`<pair>/pair.json` 可解析）
 *   2. 两侧候选都完整（A、B 各有 `mix.wav`）—— 「A/B 的语义始终是两个完整候选」，
 *      单边是半成品，不能拿来做二选一
 *   3. 复检已完成：`recheck.json` 存在、schema 与 pair_id 对得上、且它对齐的三份 report
 *      仍都在磁盘上（一份指向别处或已被删掉的复检，不构成「已复检」）
 *
 * 为什么 ORIGINAL 也要过这三关
 *   「保留原版」是**两档都不如原版**时的第三出口，不是「还没做过 A/B 就能直接交原版」的捷径。
 *   若候选不完整时也允许写 ORIGINAL，⑧导出 就能绕开整个审听把原版交出去，而流程会被推成
 *   CHOSEN/DONE —— 那正是「未完成被显示成完成」。所以三个出口用同一道门。
 */
function decisionBlockers(caseDir, pairId) {
  if (!pairId) return ['没有指定修音对（pair）'];
  const dir = pairDir(caseDir, pairId);
  if (!readJsonSafe(path.join(dir, 'pair.json'))) {
    return [`修音对不存在：${pairId}`]; // 没有 pair 就谈不上两侧与复检
  }

  const blockers = [];
  const state = pairState(caseDir, pairId);
  if (!state.A.has_mix) blockers.push('A（保守）还没有合成产物 mix.wav');
  if (!state.B.has_mix) blockers.push('B（充分）还没有合成产物 mix.wav');

  const rc = readJsonSafe(path.join(dir, 'recheck.json'));
  if (!rc) {
    blockers.push('尚未复检（缺 recheck.json）');
  } else if (rc.schema !== recheck.SCHEMA) {
    blockers.push(`复检产物 schema 不符：${rc.schema || '缺失'}`);
  } else if (rc.pair_id !== pairId) {
    blockers.push(`复检产物属于另一对：${rc.pair_id || '缺失'}`);
  } else {
    for (const key of ['original', 'A', 'B']) {
      const report = rc[key] && rc[key].report;
      if (!report || !fs.existsSync(report)) {
        blockers.push(`复检引用的 ${key} 报告已不在磁盘上`);
      }
    }
  }
  return blockers;
}

/** 空数组 = 这一对现在真的可以被选定。 */
function canDecide(caseDir, pairId) {
  return decisionBlockers(caseDir, pairId).length === 0;
}

/**
 * 校验一次候选选择。返回 `{ok:true, pair}` 或 `{ok:false, reason, blockers?, detail?}`。
 * `kept` 的合法性先于 pair 完整性判断：`kept` 本身不是三个出口之一是调用错误，
 * 与「这一对还没准备好」是两件不同的事，报错也该不同。
 */
function validateDecision(caseDir, { pairId, kept } = {}) {
  if (!pairId) return { ok: false, reason: 'NO_PAIR' };
  if (!EXITS.includes(kept)) return { ok: false, reason: 'BAD_KEPT', allowed: [...EXITS] };
  const blockers = decisionBlockers(caseDir, pairId);
  if (blockers.length) {
    return {
      ok: false,
      reason: 'PAIR_NOT_COMPLETE',
      blockers,
      detail: '只有「两个完整候选 + 已完成复检」的修音对才能被选定：' + blockers.join('；'),
    };
  }
  return { ok: true, pair: pairState(caseDir, pairId) };
}

/**
 * 账本最后一条记录是否**此刻仍然**被一对完整候选支撑。
 *
 * pipeline 的 `chosen` 事实用它，所以一条没有被完整候选支撑的记录（旧版本写的、手写的、
 * 或者候选后来被删掉的）既写不进去，也不会在重新推导时把阶段推到 CHOSEN、把 ⑧导出 解锁。
 * 这与「阶段由磁盘产物推导」是同一条纪律：产物没了，进度就退回去。
 */
function decisionBacked(caseDir) {
  const rows = readDecisions(caseDir);
  const last = rows.length ? rows[rows.length - 1] : null;
  if (!last) return { decision: null, pair: null, valid: false, reason: 'NO_DECISION', blockers: [] };
  const v = validateDecision(caseDir, { pairId: last.pair_id, kept: last.kept });
  return {
    decision: last,
    pair: v.ok ? v.pair : null,
    valid: v.ok,
    reason: v.ok ? null : v.reason,
    blockers: v.blockers || [],
  };
}

/**
 * 记一次人的选择。只追加，永不改写历史。
 *
 * @param {object} args
 * @param {string} args.pairId
 * @param {'A'|'B'|'ORIGINAL'} args.kept   第三个出口 ORIGINAL = 保留原版
 * @param {'creator'|'listener'|'pro'} [args.role]
 * @param {string} [args.requestId]  同一次待决选择保持不变 → 重试被识别为重复而非写入两条
 */
function appendDecision(caseDir, { pairId, kept, role, note, requestId, at }) {
  if (!pairId) return { ok: false, reason: 'NO_PAIR' };
  if (!EXITS.includes(kept)) return { ok: false, reason: 'BAD_KEPT', allowed: [...EXITS] };
  if (role && !ROLES.includes(role)) return { ok: false, reason: 'BAD_ROLE', allowed: [...ROLES] };

  const existing = readDecisions(caseDir);
  if (requestId) {
    const dup = existing.find((r) => r.request_id === requestId);
    if (dup) {
      // 幂等只对**同一次待决选择**成立。同一个 request_id 换了 pair 或换了出口是调用方出错，
      // 不能静默返回旧结果——否则界面上会显示「已选 A」，而人点的是 B。
      if (dup.pair_id !== pairId || dup.kept !== kept) {
        return {
          ok: false,
          reason: 'REQUEST_ID_CONFLICT',
          detail: `request_id「${requestId}」已经用在 ${dup.pair_id} / ${dup.kept}`,
        };
      }
      return { ok: true, recorded: false, duplicate: true, entry: dup };
    }
  }

  // 写之前校验：虚假或未完成的 pair 一律写不进去（三个条件见 decisionBlockers）
  const valid = validateDecision(caseDir, { pairId, kept });
  if (!valid.ok) return valid;

  const entry = {
    schema: SCHEMA_DECISION,
    pair_id: pairId,
    kept,
    role: role || null,
    note: note || null,
    at: at || new Date().toISOString(),
    request_id: requestId || null,
  };
  fs.mkdirSync(tuningDir(caseDir), { recursive: true });
  fs.appendFileSync(decisionsPath(caseDir), JSON.stringify(entry) + '\n');
  return { ok: true, recorded: true, entry, count: existing.length + 1 };
}

module.exports = {
  TUNING_DIR,
  DECISIONS_FILE,
  SIDE_DIRS,
  EXITS,
  ROLES,
  SCHEMA_DECISION,
  tuningDir,
  pairDir,
  sideDir,
  decisionsPath,
  newPairId,
  createPairDir,
  sideState,
  pairState,
  listPairs,
  currentPair,
  aggregate,
  createdAtMs,
  readDecisions,
  decisionFor,
  decisionBlockers,
  canDecide,
  validateDecision,
  decisionBacked,
  appendDecision,
  readJsonSafe,
  listFiles,
};
