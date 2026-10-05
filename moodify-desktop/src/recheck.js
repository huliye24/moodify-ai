/**
 * ⑥ 复检 — 三方逐指标对齐表
 *
 * CONTRACT: docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md §6
 *
 * 这段代码只做一件事：把三份 Core `report.json`（原版 / A 档 / B 档）的测量摊成一张对齐表。
 * 它不测量、不推理、不补算。
 *
 * 为什么必须这么严
 *   复检是本流程里唯一声称"改完之后比之前怎样"的地方。一旦它开始补算或推断缺失指标，
 *   它就变成了第二个测量权威（One Core 禁止），而且用户无法分辨哪个数字是 Core 说的、
 *   哪个是我们编的。所以：
 *
 *     alignable      ← 三份 report 里**都**有、单位一致、且 Core 自己标了 VALID 的指标
 *     not_alignable  ← 其余全部，逐条写明原因（缺失于哪一侧 / 单位不一致 / 非 VALID / 非数值）
 *
 *   缺项不许静默消失。这一点尤其重要，因为 Core 的指标集可能随版本变化——
 *   与其让一个指标悄悄从表里掉出去，不如让 `not_alignable` 把它挂出来。
 *
 * 指标来源
 *   `report.json` 顶层 `measurements: [{ id, value, unit, status, group, ... }]`。
 *   这是 Core 对**那一次运行**的权威测量集。不使用 `measurements.json`（case 级快照），
 *   因为复检要对齐的是"这次渲染后重新检测"的结果，不是初始快照。
 *
 * 与 ⑤修音 的关系
 *   本模块在 A、B 尚未渲染时完全不参与——它读不到 report 就返回 `MISSING_REPORT`，
 *   而不是给出一张空表让人误以为"已经复检过了"。
 */

'use strict';

const fs = require('fs');
const path = require('path');

const SCHEMA = 'moodify.studio.recheck/0.1';

/** report.json 的测量是 Core 的权威输出；读不出来就是 null，不是空对象。 */
function readReport(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return null; }
}

/** id -> { value, unit, status, group }。只接受有字符串 id 的条目。 */
function metricsOf(report) {
  const out = new Map();
  const list = report && Array.isArray(report.measurements) ? report.measurements : [];
  for (const m of list) {
    if (!m || typeof m.id !== 'string') continue;
    out.set(m.id, {
      value: m.value,
      unit: m.unit ?? null,
      status: m.status ?? null,
      group: m.group ?? null,
    });
  }
  return out;
}

function isNum(v) { return typeof v === 'number' && Number.isFinite(v); }

/** 固定小数位，避免 float 噪声进产物（0.30000000000000004 这类）。 */
function round(v, digits = 6) {
  if (!isNum(v)) return null;
  const f = 10 ** digits;
  return Math.round(v * f) / f;
}

function diff(after, before) {
  if (!isNum(after) || !isNum(before)) return null;
  return round(after - before);
}

/**
 * 造对齐表。
 *
 * @param {object} args
 * @param {string} args.pairId
 * @param {{original:string,A:string,B:string}} args.paths     三份 report.json 的路径（写进产物，便于回溯）
 * @param {{original:object|null,A:object|null,B:object|null}} args.reports  已解析的 report
 * @param {'DEEP'|'FAST_STEREO_ONLY'} [args.mode]
 * @param {string} [args.generatedAt]
 * @returns {{ok:boolean, reason?:string, payload?:object}}
 */
function buildRecheck({ pairId, paths, reports, mode, generatedAt }) {
  if (!pairId || !paths) return { ok: false, reason: 'BAD_ARGS' };

  // 缺任何一份 report 都不算复检过。宁可拒绝，不留空表。
  const missing = ['original', 'A', 'B'].filter((k) => !reports || !reports[k]);
  if (missing.length) {
    return { ok: false, reason: 'MISSING_REPORT', missing };
  }

  const orig = metricsOf(reports.original);
  const aMap = metricsOf(reports.A);
  const bMap = metricsOf(reports.B);

  const ids = [...new Set([...orig.keys(), ...aMap.keys(), ...bMap.keys()])].sort();

  const alignable = [];
  const notAlignable = [];
  const origMetrics = {};
  const aMetrics = {};
  const bMetrics = {};
  const aDelta = {};
  const bDelta = {};

  for (const id of ids) {
    const o = orig.get(id);
    const a = aMap.get(id);
    const b = bMap.get(id);

    const absent = [];
    if (!o) absent.push('原版');
    if (!a) absent.push('A');
    if (!b) absent.push('B');
    if (absent.length) {
      notAlignable.push({ name: id, reason: `指标缺失于 ${absent.join(' / ')}；不补算` });
      continue;
    }

    const units = new Set([o.unit ?? null, a.unit ?? null, b.unit ?? null]);
    if (units.size > 1) {
      notAlignable.push({
        name: id,
        reason: `单位不一致（原版=${o.unit} / A=${a.unit} / B=${b.unit}），不可比`,
      });
      continue;
    }

    const invalid = [];
    if (o.status !== 'VALID') invalid.push(`原版=${o.status}`);
    if (a.status !== 'VALID') invalid.push(`A=${a.status}`);
    if (b.status !== 'VALID') invalid.push(`B=${b.status}`);
    if (invalid.length) {
      notAlignable.push({
        name: id,
        reason: `Core 标记该次测量非 VALID（${invalid.join(', ')}），不作比较依据`,
      });
      continue;
    }

    if (!isNum(o.value) || !isNum(a.value) || !isNum(b.value)) {
      notAlignable.push({ name: id, reason: '存在非数值测量值，无法求差' });
      continue;
    }

    const unit = o.unit ?? null;
    alignable.push(id);
    origMetrics[id] = { value: round(o.value), unit, group: o.group ?? null };
    aMetrics[id] = { value: round(a.value), unit, group: o.group ?? null };
    bMetrics[id] = { value: round(b.value), unit, group: o.group ?? null };
    aDelta[id] = diff(a.value, o.value);
    bDelta[id] = diff(b.value, o.value);
  }

  const changed = (deltaMap) => alignable.filter((id) => deltaMap[id] !== 0).length;

  const payload = {
    schema: SCHEMA,
    pair_id: pairId,
    generated_at: generatedAt || new Date().toISOString(),
    mode: mode || null,
    original: {
      report: paths.original,
      measurement_count: orig.size,
      source: (reports.original && reports.original.source) || null,
      metrics: origMetrics,
    },
    A: {
      report: paths.A,
      measurement_count: aMap.size,
      delta_vs_original: aDelta,
      metrics: aMetrics,
    },
    B: {
      report: paths.B,
      measurement_count: bMap.size,
      delta_vs_original: bDelta,
      metrics: bMetrics,
    },
    alignable,
    not_alignable: notAlignable,
    // 计数只作导航用；判定不依赖它们（判定是人 + 报告本身的事）。
    summary: {
      alignable_count: alignable.length,
      not_alignable_count: notAlignable.length,
      A_changed_metrics: changed(aDelta),
      B_changed_metrics: changed(bDelta),
    },
    note: '本表只对齐 Core 实际产出的指标；缺项如实列出，不补算。'
      + '对齐数量不代表哪个方案更好——那是听觉判断。',
  };

  return { ok: true, payload };
}

function recheckPath(caseDir, pairId) {
  return path.join(caseDir, 'studio', 'tuning', String(pairId || ''), 'recheck.json');
}

function writeRecheck(caseDir, pairId, payload) {
  const file = recheckPath(caseDir, pairId);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(payload, null, 2), 'utf8');
  return file;
}

function readRecheck(caseDir, pairId) {
  return readReport(recheckPath(caseDir, pairId));
}

module.exports = {
  SCHEMA,
  readReport,
  metricsOf,
  buildRecheck,
  recheckPath,
  writeRecheck,
  readRecheck,
};
