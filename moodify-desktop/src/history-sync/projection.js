/**
 * Projection — turning append-only history events into what the user sees.
 *
 * Contract: `protocol/mips/MIP-0003-personal-identity-history.md` §5 (conflict rules)
 *
 * The projection is **derived, never authoritative**:
 *   • it never writes to a local case and never advances a local stage;
 *   • `inscription` follows the last *explicit* edit event (no character-level merging);
 *   • decision history is preserved in full, and the *current* selection is the last valid
 *     decision event — the local `decisions.jsonl` still wins whenever the two disagree;
 *   • ordering is `(server_received_at, event_id)` when the server supplied them, otherwise
 *     `(occurred_at, request_id)` locally. Both are total and stable, so two devices that
 *     received the same events in a different order project the same list.
 */

'use strict';

const { EVENT_TYPES } = require('./schema');

function eventSortKey(event) {
  const received = event.server_received_at || event.occurred_at;
  const tie = event.event_id || event.request_id || '';
  return `${received}|${tie}`;
}

/** 稳定排序：同一批事件无论到达顺序如何，投影结果一致。 */
function sortEvents(events) {
  return [...events].sort((a, b) => {
    const ka = eventSortKey(a);
    const kb = eventSortKey(b);
    if (ka < kb) return -1;
    if (ka > kb) return 1;
    return 0;
  });
}

/** 去掉重复事件（同一 request_id，或同一 event_id），保留第一条。 */
function dedupeEvents(events) {
  const seen = new Set();
  const out = [];
  for (const event of sortEvents(events)) {
    const key = event.event_id || event.request_id;
    if (!key || seen.has(key)) continue;
    seen.add(key);
    out.push(event);
  }
  return out;
}

/**
 * 把一个 work 的事件投影成一条历史记录。
 *
 * 返回 `null` 表示这些事件不足以形成一条记录（没有 WORK_COMPLETED 时不算「完成过的作品」）。
 */
function projectWork(events) {
  const ordered = dedupeEvents(events).filter((e) => EVENT_TYPES.includes(e.event_type));
  if (!ordered.length) return null;
  const completed = ordered.find((e) => e.event_type === 'WORK_COMPLETED');
  const workId = (ordered[0].work_id || '').toLowerCase();
  if (!workId) return null;

  let selected = null;
  let selectedAt = null;
  let inscription = null;
  let inscriptionAt = null;
  const decisionHistory = [];
  let completedEvt = completed || null;
  let lastEvent = ordered[ordered.length - 1];

  for (const event of ordered) {
    const payload = event.payload || {};
    const at = event.occurred_at || event.server_received_at || null;
    if (event.event_type === 'DECISION_CHANGED' && payload.selected) {
      selected = payload.selected;
      selectedAt = at;
      decisionHistory.push({ selected: payload.selected, at, request_id: event.request_id });
    }
    if (event.event_type === 'INSCRIPTION_UPDATED' && typeof payload.inscription === 'string') {
      inscription = payload.inscription;
      inscriptionAt = at;
    }
    if (event.event_type === 'WORK_COMPLETED') {
      if (!completedEvt) completedEvt = event;
      if (payload.selected && !decisionHistory.length) {
        // WORK_COMPLETED 自带的初始选择也是历史的一部分
        selected = payload.selected;
        selectedAt = at;
        decisionHistory.push({ selected: payload.selected, at, request_id: event.request_id });
      }
      if (typeof payload.inscription === 'string' && inscription === null) {
        inscription = payload.inscription;
        inscriptionAt = at;
      }
    }
    if (!lastEvent || eventSortKey(event) >= eventSortKey(lastEvent)) lastEvent = event;
  }

  const title = (completedEvt && completedEvt.payload && completedEvt.payload.title)
    || ordered.map((e) => (e.payload || {}).title).find(Boolean)
    || '未命名作品';

  return {
    workId,
    title,
    durationMs: (completedEvt && completedEvt.payload && completedEvt.payload.duration_ms) || null,
    completionMode: (completedEvt && completedEvt.payload && completedEvt.payload.completion_mode) || null,
    selected,
    selectedAt,
    completedAt: (completedEvt && (completedEvt.payload || {}).completed_at)
      || (completedEvt && completedEvt.occurred_at) || null,
    inscription,
    inscriptionAt,
    revision: ordered.reduce((max, e) => Math.max(max, Number(e.revision) || 0), 0),
    lastEventAt: lastEvent ? (lastEvent.server_received_at || lastEvent.occurred_at || null) : null,
    decisionHistory,
    eventCount: ordered.length,
  };
}

/** 一批事件 → 按 work 分组的投影列表（按最近活动排序）。 */
function projectHistory(events) {
  const byWork = new Map();
  for (const event of dedupeEvents(events)) {
    const key = String(event.work_id || '').toLowerCase();
    if (!key) continue;
    if (!byWork.has(key)) byWork.set(key, []);
    byWork.get(key).push(event);
  }
  const works = [];
  for (const group of byWork.values()) {
    const projected = projectWork(group);
    if (projected) works.push(projected);
  }
  return works.sort((a, b) => {
    const ka = a.lastEventAt || '';
    const kb = b.lastEventAt || '';
    if (ka === kb) return a.workId < b.workId ? 1 : -1;
    return ka < kb ? 1 : -1;
  });
}

/**
 * 本地 case 与云端投影合并成个人历史列表。
 *
 * `audioAvailability` 是**本地事实**：只有本机确实存在该 case 的完成音频时才是
 * `LOCAL_AVAILABLE`，否则 `LOCAL_ONLY`（另一台设备）。远端记录永远不会让列表出现可播放状态。
 */
function mergeHistory({ local = [], remote = [] } = {}) {
  const byWork = new Map();
  for (const item of local) {
    byWork.set(item.workId, {
      ...item,
      sources: ['local'],
      syncState: item.syncEnabled ? (item.syncState || 'waiting') : 'local_only',
    });
  }
  for (const item of remote) {
    const existing = byWork.get(item.workId);
    if (existing) {
      existing.sources = [...existing.sources, 'remote'];
      // 本地是权威：本地存在的记录保留本地标题/选择，只在有差异时留下痕迹
      existing.remoteDirty = Boolean(
        item.selected && existing.selected && item.selected !== existing.selected,
      );
      existing.remoteSelected = item.selected || null;
      existing.remoteInscription = item.inscription ?? null;
      if (existing.inscription === null || existing.inscription === undefined) {
        existing.inscription = item.inscription;
      }
      continue;
    }
    byWork.set(item.workId, {
      ...item,
      sources: ['remote'],
      audioAvailability: 'LOCAL_ONLY',
      syncState: 'synced',
    });
  }
  return [...byWork.values()].sort((a, b) => {
    const ka = a.completedAt || a.lastEventAt || '';
    const kb = b.completedAt || b.lastEventAt || '';
    if (ka === kb) return a.workId < b.workId ? 1 : -1;
    return ka < kb ? 1 : -1;
  });
}

module.exports = {
  sortEvents,
  dedupeEvents,
  projectWork,
  projectHistory,
  mergeHistory,
};
