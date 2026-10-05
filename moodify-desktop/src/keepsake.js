/**
 * 完成时刻的留存记录（keepsake） — **非权威**的表现层产物
 *
 * 契约：`docs/plan/2026-10-04_DESKTOP_PHASE2_3_FINISHING_POLISH.md`（Phase 2.3 任务书）
 *
 * 它是什么
 *   `<case>/studio/keepsake.json`：一首歌被选定之后留下的东西——选的是哪一版、什么时候、
 *   以及人自己写的一句话和那个版本的波形印记。用户下次打开这首歌时，界面据此恢复完成状态。
 *
 * 它不是什么（这条纪律比文件本身重要）
 *   它**不是完成状态的权威**。完成与否由 `pipeline`（产物推导）与 `tuning`（⑦ 准入）决定：
 *   有 keepsake 而 decision 失效时，完成层必须消失；有 keepsake 也不能让阶段前进到 CHOSEN，
 *   更不能解锁导出。`selected` 只是当前有效 decision 的**投影**，永远是写进去的下游，不是上游。
 *
 * 为什么可以存波形印记
 *   印记是「这首歌被选定时的形状」，不重新解码也能重画（音频被移走时完成层仍然完整）。
 *   它只有固定桶数的一串小数（≤ 4 KB），不是音频字节、不是图片 base64、不是 report/hash 大表。
 */

'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const SCHEMA = 'moodify.studio.keepsake/0.1';
const FILE_NAME = 'keepsake.json';

/** 一句话的边界：280 个 Unicode 字符（按码位计）以内，最多 4 行。 */
const INSCRIPTION_MAX_CHARS = 280;
const INSCRIPTION_MAX_LINES = 4;

/** 波形印记的固定桶数。固定 = 同一段音频永远得到同一个形状。 */
const IMPRINT_BUCKETS = 600;
const IMPRINT_DECIMALS = 3;

const SELECTIONS = Object.freeze(['A', 'B', 'ORIGINAL']);

const SELECTION_LABELS = Object.freeze({
  A: 'A（保守）',
  B: 'B（充分）',
  ORIGINAL: '保留原版',
});

function keepsakePath(caseDir) {
  return path.join(caseDir, 'studio', FILE_NAME);
}

function selectionLabel(selected) {
  return SELECTION_LABELS[selected] || selected || '';
}

/** 一句话的长度按**码位**计（中文、法文重音、emoji 都算一个字符）。 */
function countChars(text) {
  return [...String(text == null ? '' : text)].length;
}

function countLines(text) {
  const normalized = String(text == null ? '' : text).replace(/\r\n?/g, '\n');
  return normalized.split('\n').length;
}

/**
 * 校验一句话。超限**拒绝**而不是静默截断：界面上有 maxlength 与行数限制，
 * 走到这里还超限说明调用方绕过了界面——那时悄悄改掉用户写的东西比报错更糟。
 */
function validateInscription(text) {
  if (text == null) return { ok: true, text: '' };
  if (typeof text !== 'string') return { ok: false, reason: 'INSCRIPTION_NOT_A_STRING' };
  const normalized = text.replace(/\r\n?/g, '\n');
  if (countChars(normalized) > INSCRIPTION_MAX_CHARS) {
    return { ok: false, reason: 'INSCRIPTION_TOO_LONG', limit: INSCRIPTION_MAX_CHARS };
  }
  if (countLines(normalized) > INSCRIPTION_MAX_LINES) {
    return { ok: false, reason: 'INSCRIPTION_TOO_MANY_LINES', limit: INSCRIPTION_MAX_LINES };
  }
  return { ok: true, text: normalized };
}

/**
 * 波形印记：把一串峰值摊成固定桶数的一维形状。
 *
 * 纯函数、无随机、无时间输入 —— 同一段音频（同一串峰值）永远得到同一串数字，
 * 于是作品卡与完成层上的形状是**同一个**，换窗口宽度也只是重画同一串数字。
 */
function normalizeImprint(values, buckets = IMPRINT_BUCKETS) {
  const source = Array.isArray(values) || ArrayBuffer.isView(values) ? Array.from(values) : [];
  if (!source.length || buckets <= 0) return [];
  const out = [];
  for (let i = 0; i < buckets; i += 1) {
    const start = Math.floor((i * source.length) / buckets);
    const end = Math.max(start + 1, Math.floor(((i + 1) * source.length) / buckets));
    let peak = 0;
    for (let j = start; j < end && j < source.length; j += 1) {
      const value = Number(source[j]);
      if (!Number.isFinite(value)) continue;
      const magnitude = Math.abs(value);
      if (magnitude > peak) peak = magnitude;
    }
    out.push(Math.min(1, Math.max(0, Number(peak.toFixed(IMPRINT_DECIMALS)))));
  }
  return out;
}

/** 卡片与文件名里出现的标题：只保留可打印字符，压掉路径与空白噪音。 */
function sanitizeFileName(name, fallback = 'Moodify') {
  const raw = String(name == null ? '' : name)
    .replace(/[\\/:*?"<>|\u0000-\u001f]/g, '')  // Windows/POSIX 非法字符与控制字符
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/[. ]+$/, '');                      // Windows 不允许结尾的点或空格
  const base = raw || fallback;
  return base.length > 80 ? base.slice(0, 80).trim() : base;
}

/**
 * 作品卡上允许出现的内容 —— **只有这些**。
 *
 * 卡片绘制在渲染层，但它能拿到的字段全部来自这里；case_id / pair_id / hash / 绝对路径
 * 从不进入这个模型，所以它们也没有机会被画上去（§8.1 的隐私要求由构造保证，而不是靠自觉）。
 */
function cardModel({ title, selected, completedAt, inscription, tierLabel }) {
  const date = completedAt ? new Date(completedAt) : null;
  const valid = date && !Number.isNaN(date.getTime());
  const iso = valid ? date.toISOString() : null;
  return {
    title: String(title == null ? '' : title).trim() || '未命名作品',
    selectionLabel: selectionLabel(selected),
    versionLabel: selected === 'ORIGINAL' ? '保留原版' : (tierLabel || '完成'),
    dateLabel: iso ? `${iso.slice(0, 4)}.${iso.slice(5, 7)}.${iso.slice(8, 10)}` : '',
    inscription: typeof inscription === 'string' && inscription.trim() ? inscription : '',
  };
}

function defaultCardFileName(title, extension = 'png') {
  return `${sanitizeFileName(title)} — Moodify.${extension}`;
}

/**
 * 读留存记录。**永不抛**：文件损坏、权限不足都只是「这次没有留存内容」，
 * 声音流程与完成状态都不受影响，原因通过 `error` 返回以便诊断。
 */
function readKeepsake(caseDir) {
  const file = keepsakePath(caseDir);
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (err) {
    if (err && err.code === 'ENOENT') return { ok: true, keepsake: null, error: null };
    return { ok: true, keepsake: null, error: 'KEEPSAKE_UNREADABLE' };
  }
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return { ok: true, keepsake: null, error: 'KEEPSAKE_CORRUPT_JSON' };
  }
  if (!parsed || typeof parsed !== 'object' || parsed.schema !== SCHEMA) {
    return { ok: true, keepsake: null, error: 'KEEPSAKE_SCHEMA_MISMATCH' };
  }
  return { ok: true, keepsake: parsed, error: null };
}

/**
 * 原子写入：先写同目录临时文件，再 rename 覆盖。
 * 断电或崩溃时要么是旧文件、要么是新文件，不会留半截 JSON。
 */
function writeKeepsake(caseDir, patch = {}) {
  const dir = path.join(caseDir, 'studio');
  const file = keepsakePath(caseDir);
  const previous = readKeepsake(caseDir).keepsake || {};

  const next = {
    schema: SCHEMA,
    case_id: patch.case_id !== undefined ? patch.case_id : (previous.case_id || null),
    decision_request_id: patch.decision_request_id !== undefined
      ? patch.decision_request_id : (previous.decision_request_id || null),
    selected: patch.selected !== undefined ? patch.selected : (previous.selected || null),
    completed_at: patch.completed_at !== undefined
      ? patch.completed_at : (previous.completed_at || null),
    inscription: patch.inscription !== undefined
      ? patch.inscription : (previous.inscription || ''),
    imprint: patch.imprint !== undefined ? patch.imprint : (previous.imprint || null),
    updated_at: new Date().toISOString(),
  };
  if (next.selected !== null && !SELECTIONS.includes(next.selected)) {
    return { ok: false, reason: 'BAD_SELECTION' };
  }
  if (next.imprint !== null && !Array.isArray(next.imprint)) {
    return { ok: false, reason: 'BAD_IMPRINT' };
  }

  const tmp = path.join(dir, `.${FILE_NAME}.tmp-${process.pid}-${crypto.randomBytes(4).toString('hex')}`);
  try {
    // mkdir 也在 try 里：留存记录不是承重件，任何文件系统问题都只报告、不抛。
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(tmp, JSON.stringify(next, null, 2), 'utf8');
    fs.renameSync(tmp, file);
  } catch (err) {
    try { fs.rmSync(tmp, { force: true }); } catch { /* already gone */ }
    return { ok: false, reason: 'KEEPSAKE_WRITE_FAILED', detail: err && err.message };
  }
  return { ok: true, keepsake: next };
}

module.exports = {
  SCHEMA,
  FILE_NAME,
  INSCRIPTION_MAX_CHARS,
  INSCRIPTION_MAX_LINES,
  IMPRINT_BUCKETS,
  IMPRINT_DECIMALS,
  SELECTIONS,
  SELECTION_LABELS,
  keepsakePath,
  selectionLabel,
  countChars,
  countLines,
  validateInscription,
  normalizeImprint,
  sanitizeFileName,
  cardModel,
  defaultCardFileName,
  readKeepsake,
  writeKeepsake,
};
