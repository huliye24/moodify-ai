/**
 * 完成会话编排器 — 主进程侧的调度循环（Phase 1）
 *
 * 目标形态：
 *     放入一首歌 → 一次启动 → 内部自动执行 → 原版 / A / B → 人选择 → 导出
 *
 * 「一键」只简化**用户操作**，不省略内部步骤，也**不把未实现能力伪装成成功**。
 *
 * 这个文件里没有第二套状态机
 *   阶段与门禁的唯一权威是 `src/pipeline.js`（由磁盘产物推导），相位折叠在 `src/session.js`。
 *   本模块是**调度**：每一轮都重新 `snapshot()` 推导，然后调用那一步真实存在的函数。
 *   它自己不记进度、不写任何音频或产物，也不替任何东西宣布完成。
 *
 * 为什么它从 main.js 里搬出来
 *   调度循环里有两条必须被测到的纪律（见 scripts/test-orchestrator.js）：
 *     · 同一步在一次启动里只能尝试一次 —— 声称成功却没留下产物时立即停止，
 *       绝不重跑（Core 的检测每次都新建 case，重跑就是在 cases-root 里造垃圾）；
 *     · 真实失败要留下原因，并让「重新投影」后仍然可见（session.recordFailure）。
 *   这两条都要能在没有 Electron、没有 Python 的情况下被确定性地复现，所以步骤函数由
 *   main.js 注入，本模块只依赖注入进来的 `snapshot` / `resolveCaseSource` / `steps`。
 */

'use strict';

const session = require('./session');

/**
 * @param {object} deps
 * @param {(caseDir:string) => object} deps.snapshot   pipeline.snapshot —— 唯一权威
 * @param {(caseDir:string) => (string|null)} deps.resolveCaseSource
 * @param {Record<string, (caseDir:string, ctx:object) => Promise<object>>} deps.steps
 *        以 phase.run 为键的真实步骤函数（analyze / separate / structure / tune / recheck）。
 *        每个返回 `{ ok: true, ... }` 或 `{ ok: false, reason, detail? }`。
 */
function createOrchestrator(deps) {
  const { snapshot, resolveCaseSource, steps } = deps || {};
  if (typeof snapshot !== 'function') throw new Error('orchestrator: snapshot(caseDir) is required');
  if (!steps || typeof steps !== 'object') throw new Error('orchestrator: steps is required');
  const source = typeof resolveCaseSource === 'function' ? resolveCaseSource : () => null;

  /**
   * 会话视图：给 UI 的只读投影。不推进任何状态。
   *
   * 投影 = pipeline 推导 + session 相位折叠 + 「上一次真实失败」叠加。
   * 失败记录只在它描述的那一步**此刻仍未完成**时生效（见 session.applyFailure）；
   * 一旦过期就顺手清掉，免得它留着误导下一次。
   */
  function sessionView(caseDir) {
    const snap = snapshot(caseDir);
    const proj = session.project(snap);
    const failure = session.readFailure(caseDir);
    const merged = session.applyFailure(proj, failure);
    if (failure && !merged.applies) session.clearFailure(caseDir);
    return {
      ...merged.view,
      caseDir,
      source: source(caseDir),
      stage: snap.stage,
      facts: snap.facts,
      running: session.isRunning(caseDir),
    };
  }

  /** 一个相位 → main 侧真实步骤函数。找不到步骤就如实报错，不假装跑过。 */
  async function runSessionPhase(caseDir, phase) {
    const step = phase && phase.run ? steps[phase.run] : null;
    if (typeof step !== 'function') {
      return {
        ok: false,
        reason: 'PHASE_HAS_NO_ACTION',
        detail: `相位「${(phase && phase.label) || '?'}」没有可执行的步骤函数`,
      };
    }
    return step(caseDir, { phase });
  }

  /**
   * 编排循环。
   *
   * 每一轮都**重新从磁盘推导**状态，而不是自己维护进度表。于是：
   *   · 已完成的步骤自动跳过（关掉再打开能接着跑）；
   *   · 外部删了某个产物，下次启动会重新做那一步；
   *   · 「卡住」永远是能力缺失或步骤失败造成的真实结果，不是编排器自己的判断。
   */
  async function runCompletionSession(event, caseDir) {
    const emit = (payload) => {
      try { event.sender.send('session:progress', payload); } catch { /* window gone */ }
    };

    // 新的一次启动 = 新的一次尝试：上一次失败的原因不再代表这次的结果。
    // （若这次又失败，会立刻重新记录一条带新细节的。）
    session.clearFailure(caseDir);

    const attempted = new Set();
    const MAX_ROUNDS = session.PHASES.length + 2;

    for (let round = 0; round < MAX_ROUNDS; round += 1) {
      const snap = snapshot(caseDir);
      const proj = session.project(snap);
      emit({ caseDir, ...proj, running: true });

      // 控制流只看 pipeline 推导出来的投影：失败记录是显示层的事，绝不能拦住重试
      if (proj.state === 'BLOCKED') {
        return { ok: false, reason: 'BLOCKED', stage: snap.stage, ...sessionView(caseDir) };
      }
      if (proj.state === 'REVIEW' || proj.state === 'DONE') {
        return { ok: true, stage: snap.stage, ...sessionView(caseDir) };
      }

      const phase = session.phaseById(proj.nextPhase);
      if (!phase) {
        return { ok: false, reason: 'UNKNOWN_PHASE', ...sessionView(caseDir) };
      }

      // 同一步在一次启动里只尝试一次。
      // 走到这里说明它刚刚「成功」过，磁盘上却仍没有它应留下的产物 —— 再跑一遍只会
      // 重复同样的动作（检测还会在 cases-root 里再造一个 case）。所以立即停，如实记账。
      if (attempted.has(phase.id)) {
        const detail = `「${phase.label}」报告成功，但磁盘上仍没有它应留下的产物。`
          + '为避免重复执行与重复产物，本次启动就此停止。';
        session.recordFailure(caseDir, {
          phase: phase.id, phaseLabel: phase.label, reason: 'NO_PROGRESS', detail,
        });
        return { ok: false, reason: 'NO_PROGRESS', phase: phase.id, detail, ...sessionView(caseDir) };
      }
      attempted.add(phase.id);

      emit({ caseDir, ...proj, running: true, activePhase: phase.id });

      let res;
      try {
        res = await runSessionPhase(caseDir, phase);
      } catch (err) {
        // 步骤抛异常也是一次真实失败：原因照原样带走，不吞掉
        res = { ok: false, reason: (err && err.message) || String(err) };
      }

      if (!res || !res.ok) {
        const reason = (res && res.reason) || 'STEP_FAILED';
        const detail = (res && (res.detail || res.reason)) || null;
        session.recordFailure(caseDir, {
          phase: phase.id, phaseLabel: phase.label, reason, detail,
        });
        return { ok: false, reason: 'PHASE_FAILED', phase: phase.id, detail, ...sessionView(caseDir) };
      }

      // 这一步真的成功了：上一次的失败记录不再有效
      session.clearFailure(caseDir);
    }

    // 正常不可能走到这里（每个相位只尝试一次，尝试完必然停）。留着是为了万一循环条件
    // 被改坏时，也只会停住并如实报「没有前进」，绝不静默返回成功。
    const detail = '编排循环结束仍未前进；已停止，没有重复执行任何步骤。';
    session.recordFailure(caseDir, { phase: null, phaseLabel: null, reason: 'NO_PROGRESS', detail });
    return { ok: false, reason: 'NO_PROGRESS', detail, ...sessionView(caseDir) };
  }

  return { sessionView, runSessionPhase, runCompletionSession };
}

module.exports = { createOrchestrator };
