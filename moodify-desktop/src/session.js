/**
 * 完成会话编排器 — Desktop「一键完成机」的骨架（Phase 1）
 *
 * 目标形态：
 *     放入一首歌 → 一次启动 → 内部自动执行 → 原版 / A / B → 人选择 → 导出
 *
 * 「一键」只简化**用户操作**，不省略内部步骤，也**不把未实现能力伪装成成功**。
 *
 * 这个文件里没有第二套状态机
 *   阶段与门禁的唯一权威是 `src/pipeline.js`（由磁盘产物推导）。本模块**只做投影**：
 *   把 pipeline 的 8 个内部阶段折叠成用户能看懂的 6 个相位，并在相位缺能力时
 *   给出真实阻断原因。它自己不记进度、不写产物、不推进任何状态。
 *
 * 能力可得性只有一处来源
 *   `pipeline.CAPABILITIES`（真的能调）与 `pipeline.PLANNED_CAPABILITIES`（还没实现）。
 *   本模块**不硬编码第二份清单**——否则两处会漂移，而漂移的后果是引导用户走进死路。
 *
 * 为什么阻断要具体到相位
 *   「第 5 步做不了」和「第 4 步做不了」是两件不同的事、两种不同的补救。把 6 个相位压成
 *   一条含糊的错误信息，用户无法判断是自己缺素材还是产品缺能力。所以 blocker 里带
 *   `capability` 与 `reason`（后者直接引用 PLANNED_CAPABILITIES 自己写的理由）。
 *
 * 阻断有两种，而且必须分得清（blocker.kind）
 *   MISSING_CAPABILITY  产品还没有这个能力（Core 未实现）——重试无用，只能等。
 *   STEP_FAILED         这一步真实失败了（缺依赖、脚本报错、磁盘满）——修好之后可以重试。
 *   区分它们不是为了措辞好看：前者点「重试」是白点，后者不给重试就只剩重开应用。
 *
 * 「检测」这一步在这个会话里是**核对**，不是就地补做
 *   Core 的检测（`analyze_to_case`）总是新建一个 case（新 case_id + mkdir(exist_ok=False)），
 *   无法把 report.json 补写进一个已经存在的 case 目录。所以对一个没有 report.json 的世界，
 *   「再检测一次」永远不会让这一步完成，只会每轮造一个新的孤儿 case。会话因此如实拒绝并
 *   让用户重新导入（检测会建立新的世界），而不是反复制造 case。
 */

'use strict';

const fs = require('fs');
const path = require('path');

const pipeline = require('./pipeline');

/** 真的能调用的能力 id 集合 / 还没实现的能力（id → 声明）。 */
const AVAILABLE_CAPABILITIES = new Set(pipeline.CAPABILITIES.map((c) => c.id));
const PLANNED_CAPABILITIES = new Map(pipeline.PLANNED_CAPABILITIES.map((c) => [c.id, c]));

/**
 * 深度阻断原因码 → **普通用户能读的一句话**（2026-10-04 裁定）。
 *
 * 产品面和「制作详情」层要的是两种话：前者说「现在走不通、你可以怎么办」，后者说
 * 「缺哪个文件、哪项能力」（`deepReasons`，来自 pipeline 的技术说明）。
 * 把 `studio/roundtrip.json`、`MIP-0002` 这类工程细节摆到主界面，等于让用户替我们做集成判断。
 */
const PLAIN_DEEP_REASON = Object.freeze({
  NOT_ANALYZED: '这首歌还没有完成检测',
  NO_STEMS: '还没有完成逆向分解',
  NO_MIDI: '还缺少机器可读的结构（MIDI）',
  NO_ROUNDTRIP: '可逆性验证还没有做',
  ROUNDTRIP_FAILED: '可逆性验证没有通过',
  DEEP_CORE_UNAVAILABLE: '逐轨修音与复合能力还没有就绪',
});

/**
 * 补救面板的那一句话：先说清为什么走不通，再说清可以怎么办。
 * 只有**真的已经有分解产物**时才说「保留现有分解结果」——没有的东西不能让人以为有。
 */
function plainDeepSummary(codes, deepAssetsReady) {
  const phrases = (Array.isArray(codes) ? codes : [])
    .map((code) => PLAIN_DEEP_REASON[code])
    .filter(Boolean);
  const why = phrases.length ? `${phrases.join('、')}。` : '';
  const remedy = deepAssetsReady
    ? '你可以保留现有分解结果，改用整轨两档完成（快速完成：仅立体声）。'
    : '你可以改用整轨两档完成（快速完成：仅立体声）。';
  return `${why}${remedy}技术原因见「制作详情」。`;
}

/**
 * 用户可见的 6 个相位，顺序 = 真实执行顺序。
 *
 * `requires` 是这一步真正依赖的能力；`done(facts)` 直接读 pipeline 推导出的事实——
 * 所以「已经做过的步骤不会重复执行」，而不是靠一张会话自己的进度表来记。
 *
 * `requiresFast` / `skippedInFast` 是**快速完成（仅立体声）**这条合法旁路的形状：
 * 那条路没有分轨、没有 MIDI，也就不需要逆向分解与结构，更没有可逆性可言（V4 §4.2）。
 * 这些字段不是第二套阶段表——它们只回答「在已经由 pipeline 推导出的模式里，这一步是否属于
 * 本次流程」。模式本身来自 `pipeline.gates.mode`，由产物 + 人类显式选择推导，不是会话自己定的。
 */
const PHASES = Object.freeze([
  {
    // 检测在产品里由「导入」完成（renderer 拖入/选择 → analysis:run → 新 case）。
    // 会话这一步是**核对**它确实发生过：Core 的 analyze 总是新建 case，无法把 report.json
    // 补写进已有目录，所以缺 report.json 时如实阻断并让用户重新导入，而不是就地重跑
    // （那只会每轮造一个孤儿 case）。见 main.js 的 sessionAnalyze 与 V4 §11.2。
    id: 'detect',
    label: '检测',
    requires: ['analysis-report'],
    run: 'analyze',
    done: (f) => Boolean(f.analyzed),
  },
  {
    id: 'decompose',
    label: '逆向分解',
    requires: ['fast-separation'],
    run: 'separate',
    skippedInFast: true,
    done: (f) => Boolean(f.separated),
  },
  {
    id: 'structure',
    label: '结构（MIDI / 曲谱）',
    requires: ['audio-to-midi', 'midi-to-score'],
    run: 'structure',
    skippedInFast: true,
    done: (f) => Boolean(f.structured),
  },
  {
    // 分解是信息有损的：原分轨不可知，所以唯一可测的质量代理是「分解 → 复合是否回到原版」。
    id: 'reversible',
    label: '可逆性验证',
    requires: ['reversibility-check'],
    run: null,
    skippedInFast: true,
    done: (f) => Boolean(f.reversible),
  },
  {
    // 修音与复合由**同一次** Core 渲染产出（一个 pair 的两侧），所以在这里是一个相位。
    // 完成判据用 composed（更强）：只有修音、没有合成的是半成品，不算完成。
    // 深度路径要逐轨能力（未实现）；快速路径要的是整轨两档候选（已实现，见 MIP-0002 附录 A）。
    id: 'tune',
    label: '修音与复合',
    requires: ['stem-tuning', 'multi-stem-compose'],
    requiresFast: ['fast-stereo-pair'],
    run: 'tune',
    done: (f) => Boolean(f.tuned) && Boolean(f.composed),
  },
  {
    id: 'recheck',
    label: '复检',
    requires: ['analysis-report'],
    run: 'recheck',
    done: (f) => Boolean(f.rechecked),
  },
]);

const PHASE_BY_ID = new Map(PHASES.map((p) => [p.id, p]));

const EXIT_LABELS = Object.freeze({
  ORIGINAL: '保留原版',
  A: 'A（保守）',
  B: 'B（充分）',
});

function phaseById(id) { return PHASE_BY_ID.get(id) || null; }
function exitLabel(kept) { return EXIT_LABELS[kept] || kept; }

/** 快速完成（仅立体声）是否本次生效。权威是 pipeline 推导出的模式，不是会话自己的判断。 */
function isFastMode(snap) {
  const gates = (snap && snap.gates) || {};
  return gates.mode === 'FAST_STEREO_ONLY';
}

/** 缺哪些能力（空数组 = 这一步现在就能跑）。快速模式下按该模式声明的要求来判。 */
function missingCapabilities(phase, fast = false) {
  const requires = (fast && phase.requiresFast) ? phase.requiresFast : phase.requires;
  return requires.filter((id) => !AVAILABLE_CAPABILITIES.has(id));
}

/**
 * 把一次 pipeline 快照投影成用户可见的会话状态。
 *
 * @param {object} snap  pipeline.snapshot(caseDir) 的结果
 * @returns {{state:string, phases:Array, nextPhase:string|null, blocker:object|null, message:string}}
 */
function project(snap) {
  const facts = (snap && snap.facts) || {};

  const fast = isFastMode(snap);
  const gates = (snap && snap.gates) || {};
  // 2026-10-04 人类裁定：深度路径跑不了时，必须给出一条**由人确认**的补救路径。
  // 这里只把「可不可以切、切了会发生什么」如实投影出来；绝不自动切、绝不替人决定。
  const fastSwitch = {
    available: Boolean(gates.canRequestQuick),
    label: '切换到快速完成（仅立体声）',
    note: '快速完成不会使用分轨进行音准或节奏修正；仍会生成 A/B、复检并由你选择。',
    // 产品面：白话一句（原因 + 可怎么办）。技术原因码只用来生成它，不直接上屏。
    summary: plainDeepSummary(gates.deepBlockers, Boolean(gates.deepAssetsReady)),
    deepAssetsReady: Boolean(gates.deepAssetsReady),
    // 「制作详情」/高级层用：原因码 + pipeline 写的技术说明，逐条可读。
    deepBlockers: Array.isArray(gates.deepBlockers) ? gates.deepBlockers : [],
    deepReasons: Array.isArray(gates.deepTuneBlockers) ? gates.deepTuneBlockers : [],
    // 深度这条路此刻是否真的能走完：不能，且可切，才把补救动作摆到台面上。
    deepExecutable: Boolean(gates.deepExecutable),
  };
  let nextPhaseId = null;
  let blocker = null;
  const phases = [];

  for (const p of PHASES) {
    if (p.done(facts)) {
      // 事实优先：即使这一步在当前模式里「不需要」，产物确实在就说产物在（比如先做了分轨，
      // 之后才选择快速完成）。反过来把已有产物显示成「跳过」才是谎报。
      phases.push({ id: p.id, label: p.label, status: 'done' });
      continue;
    }
    if (fast && p.skippedInFast) {
      // 快速完成不使用这一步。它不是「待办」，也不是失败：这条路的定义就是没有分解与结构。
      phases.push({
        id: p.id,
        label: p.label,
        status: 'skipped',
        reason: '快速完成（仅立体声）不经过这一步',
      });
      continue;
    }
    if (nextPhaseId) {
      // 第一个未完成的相位之后，一切都还是「待办」——顺序不能跳。
      phases.push({ id: p.id, label: p.label, status: 'todo' });
      continue;
    }
    nextPhaseId = p.id;
    const missing = missingCapabilities(p, fast);
    if (missing.length) {
      blocker = {
        // 两种阻断在 UI 上是两件事：产品缺能力（重试无用）vs 这一步真实失败（修好后可重试）。
        // 把它们压成一种，用户就无法判断该等还是该修。
        kind: 'MISSING_CAPABILITY',
        phase: p.id,
        phaseLabel: p.label,
        capabilities: missing,
        // 「产品缺能力」与「人可以换一条路」必须同时说清：前者是原因，后者是补救。
        // 但绝不暗示系统已经替人换过去了。
        canSwitchToFast: fastSwitch.available,
        // 理由直接引用能力清单自己写的说明，不在这里另编一套
        reasons: missing.map((id) => {
          const c = PLANNED_CAPABILITIES.get(id);
          return { capability: id, reason: (c && c.reason) || '尚未实现' };
        }),
      };
      phases.push({ id: p.id, label: p.label, status: 'blocked' });
    } else {
      phases.push({ id: p.id, label: p.label, status: 'next' });
    }
  }

  const chosen = Boolean(facts.chosen);
  const reviewReady = Boolean(facts.tuned) && Boolean(facts.composed) && Boolean(facts.rechecked);

  let state;
  if (chosen) state = 'DONE';
  else if (reviewReady) state = 'REVIEW';
  else if (blocker) state = 'BLOCKED';
  else if (nextPhaseId) state = 'READY';
  else state = 'DONE';

  return {
    state,
    phases,
    nextPhase: nextPhaseId,
    blocker,
    exits: Object.keys(EXIT_LABELS),
    // 模式是权威（pipeline 推导）原样带出：UI 必须持续显示自己在哪条路上，
    // 以及「快速完成」此刻是否还等着人做一次显式选择。
    mode: gates.mode || null,
    modeLabel: gates.modeLabel || null,
    modeExecutable: gates.modeExecutable === undefined ? null : Boolean(gates.modeExecutable),
    fast,
    canRequestQuick: Boolean(gates.canRequestQuick),
    fastSwitch,
    message: messageFor(state, nextPhaseId, blocker, fast, fastSwitch),
  };
}

/**
 * 状态文案。
 *
 * BLOCKED 的措辞是有意为之：**说清是产品缺能力，不是用户做错了**。
 * 同时明确「没有生成任何候选」——否则用户会去找那两个不存在的 A / B。
 * READY 的措辞按**当前模式**列出真正会执行的步骤（快速完成不该被说成会做分轨与结构）。
 *
 * 2026-10-04 裁定：深度受阻且可切换时，文案要给出补救路径，并明确**必须由人确认**；
 * 绝不能写成「系统已切换/已降级」。
 */
function messageFor(state, nextPhaseId, blocker, fast = false, fastSwitch = null) {
  const phaseLabel = nextPhaseId && phaseById(nextPhaseId) ? phaseById(nextPhaseId).label : '';
  const planned = PHASES
    .filter((p) => !(fast && p.skippedInFast))
    .map((p) => p.label)
    .join(' → ');
  const canSwitch = Boolean(fastSwitch && fastSwitch.available);
  switch (state) {
    case 'READY':
      return `已导入${fast ? '（快速完成：仅立体声）' : ''}。点「开始完成」，内部会依次执行：${planned}。`
        + (nextPhaseId && nextPhaseId !== 'detect' ? `（将从「${phaseLabel}」继续，已完成的步骤会跳过。）` : '');
    case 'PROCESSING':
      return '正在执行…';
    case 'BLOCKED':
      return `流程停在「${blocker ? blocker.phaseLabel : phaseLabel}」：${blocker && blocker.reasons[0] ? blocker.reasons[0].reason : '前置条件未满足'}`
        + ' —— 这是产品能力尚未就绪，不是你的操作问题。'
        + '**本次没有生成任何候选版本**，因此没有 A / B 可选。'
        + (canSwitch
          ? '深度路径现在走不通；你可以保留已有分解结果，改用快速完成（仅立体声）——'
            + '需要你确认一次，系统不会自动切换。'
          : '');
    case 'REVIEW':
      return '两档候选与复检都已完成。请同位置试听 原版 / A / B，然后选定一个出口。';
    case 'DONE':
      return '已选定。可导出，或换一个出口重选。';
    default:
      return '';
  }
}

// ── 重入保护：同一首歌不允许被并发启动两次 ──────────────────────────────────
//
// 需要它是因为「一键」按钮可以被连点，而两次并发跑同一条链会在同一个 case 目录里
// 交错写产物——那正是最难排查的一类损坏。这里只是内存标记，进程重启即失效，
// 而「关掉再打开能接着跑」由产物推导保证（已完成的步骤会被跳过）。

const INFLIGHT = new Set();

function acquire(caseDir) {
  if (!caseDir || INFLIGHT.has(caseDir)) return false;
  INFLIGHT.add(caseDir);
  return true;
}
function release(caseDir) { INFLIGHT.delete(caseDir); }
function isRunning(caseDir) { return INFLIGHT.has(caseDir); }

// ── 上一次真实失败：让「哪一步失败了」在重新投影后仍然可见 ─────────────────────
//
// 为什么必须落盘
//   编排器返回失败原因是一回事，UI 随后**重新拉一次投影**是另一回事：那时磁盘上的产物没变，
//   纯由产物推导的状态自然又变回 READY，用户看到的就成了「什么也没发生」——失败原因消失，
//   人以为可以照常继续。这不是显示层的小毛病：它把一次真实失败伪装成了「还没开始」。
//   所以失败要作为**记录**留下，并在重新投影时叠加回去。
//
// 为什么它仍然不是第二套状态机
//   这条记录不推进任何阶段：阶段 / 门禁依旧每次由 pipeline 从磁盘产物推导（唯一权威）。
//   记录只有一个作用域——**同一个相位、且该相位此刻仍未完成**时，把视图降级为 BLOCKED
//   并给出原因。相位一旦完成（产物补上了 / 人手动做完了），记录立即过期，视图立刻回到
//   真实推导结果。它永远不能让任何东西变成 done / REVIEW / DONE。

const FAILURE_SCHEMA = 'moodify.studio.session-failure/0.1';
const FAILURE_FILE = 'session_failure.json';

function failurePath(caseDir) {
  return path.join(caseDir, 'studio', FAILURE_FILE);
}

function readFailure(caseDir) {
  try { return JSON.parse(fs.readFileSync(failurePath(caseDir), 'utf8')); } catch { return null; }
}

/** 记一次真实的步骤失败。覆盖前一条：只有最近一次失败与「现在卡在哪」有关。 */
function recordFailure(caseDir, { phase, phaseLabel, reason, detail, at } = {}) {
  const payload = {
    schema: FAILURE_SCHEMA,
    phase: phase || null,
    phaseLabel: phaseLabel || null,
    reason: reason || 'STEP_FAILED',
    detail: detail || null,
    at: at || new Date().toISOString(),
    note: '记录用，不是权威：阶段仍由磁盘产物推导。仅当该相位仍未完成时把视图降级为 BLOCKED。',
  };
  try {
    fs.mkdirSync(path.join(caseDir, 'studio'), { recursive: true });
    fs.writeFileSync(failurePath(caseDir), JSON.stringify(payload, null, 2), 'utf8');
  } catch { /* best effort — 记录不是承重件 */ }
  return payload;
}

function clearFailure(caseDir) {
  try { fs.rmSync(failurePath(caseDir), { force: true }); } catch { /* already gone */ }
}

/**
 * 把失败记录叠加到投影上。
 *
 * @returns {{view:object, applies:boolean, why:string|null}}
 *   applies=false 时 view 就是原始投影（记录已过期），why 说明原因。
 */
function applyFailure(proj, failure) {
  if (!failure || !failure.phase) return { view: proj, applies: false, why: 'NO_FAILURE' };
  // 已经走到审听 / 已选定：绝不用一条旧失败把成功挡回去
  if (proj.state === 'REVIEW' || proj.state === 'DONE') {
    return { view: proj, applies: false, why: 'FLOW_ADVANCED' };
  }
  // 失败的那一步已经不是「下一个未完成相位」→ 它被补上了（或流程走过去了）
  if (proj.nextPhase !== failure.phase) {
    return { view: proj, applies: false, why: 'PHASE_RESOLVED' };
  }
  // 产品缺能力是更根本的阻断：那种情况下重试无用，说「能力尚未就绪」比说「上一步失败」准确
  if (proj.blocker) return { view: proj, applies: false, why: 'STRONGER_BLOCKER' };

  const phase = phaseById(failure.phase);
  const phaseLabel = failure.phaseLabel || (phase && phase.label) || failure.phase;
  const detail = failure.detail || failure.reason || '未知原因';
  return {
    applies: true,
    why: null,
    view: {
      ...proj,
      state: 'BLOCKED',
      blocker: {
        kind: 'STEP_FAILED',
        phase: failure.phase,
        phaseLabel,
        capabilities: [],
        reason: failure.reason || null,
        detail,
        at: failure.at || null,
        reasons: [{ capability: null, reason: detail }],
      },
      message: `流程停在「${phaseLabel}」这一步：${detail}`
        + ' —— 这是这一步真实失败，不是你的操作问题。'
        + '**本次没有生成任何候选版本**，所以没有 A / B 可选。'
        + '处理完原因后可再次「开始完成」，已经完成的步骤会自动跳过。',
    },
  };
}

module.exports = {
  PHASES,
  EXIT_LABELS,
  AVAILABLE_CAPABILITIES,
  PLANNED_CAPABILITIES,
  FAILURE_SCHEMA,
  failurePath,
  readFailure,
  recordFailure,
  clearFailure,
  applyFailure,
  phaseById,
  exitLabel,
  missingCapabilities,
  isFastMode,
  project,
  acquire,
  release,
  isRunning,
};
