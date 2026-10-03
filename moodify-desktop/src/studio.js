/**
 * Studio version layer — Studio v0.2 section 6 (case model).
 *
 * WHERE THIS SITS, AND WHY (design decision D1)
 *
 * The product spec sketches a case as:
 *
 *     case_id/{ source.*, meta.json, versions/, selection.json, export/ }
 *
 * but Core's `analyze_to_case` already owns a case layout for the same directory:
 *
 *     <case>/{ case.json, scan/, measurements.json, evidence.json, report.json|md|html }
 *
 * Creating a second case root would mean two things in the repo both called "case",
 * with different shapes — the same failure mode as the two different things this repo
 * once called `protocol/`. So the version layer is mounted as a **subtree** of the
 * existing Core case:
 *
 *     <case>/                     <- Core's case, untouched
 *       case.json  scan/  report.json ...
 *       studio/                   <- Studio's version layer (this file)
 *         meta.json
 *         versions/
 *           original/             <- pointer to the case source; never a copy
 *           ai_<attempt_id>/
 *             job.json
 *             out/<stem>_<preset>.wav
 *             evidence.json
 *         selection.json
 *         export/
 *
 * Core stays the single authority for what a case *is* and what processing *does*;
 * Studio owns only which versions exist and which one the human picked.
 *
 * The `original` version is a pointer, not a copy: duplicating the source inside the
 * case would double disk use for no gain, and the case already records its source.
 */

'use strict';

const fs = require('fs');
const path = require('path');

const STUDIO_DIR = 'studio';
const VERSIONS_DIR = 'versions';
const ORIGINAL_DIR = 'original';

function studioDir(caseDir) {
  return path.join(caseDir, STUDIO_DIR);
}

function versionsDir(caseDir) {
  return path.join(studioDir(caseDir), VERSIONS_DIR);
}

function exportDir(caseDir) {
  return path.join(studioDir(caseDir), 'export');
}

function metaPath(caseDir) {
  return path.join(studioDir(caseDir), 'meta.json');
}

function selectionPath(caseDir) {
  return path.join(studioDir(caseDir), 'selection.json');
}

function ensureDirs(caseDir) {
  fs.mkdirSync(versionsDir(caseDir), { recursive: true });
  fs.mkdirSync(exportDir(caseDir), { recursive: true });
  return versionsDir(caseDir);
}

/**
 * A fresh attempt id per processing run.
 *
 * Uniqueness is load-bearing, not cosmetic: Core refuses to overwrite an existing
 * output, and Studio v0.2 section 2.2 requires "再试一次" to add a version rather than
 * silently replace one the user already confirmed. A unique directory per attempt gives
 * both properties for free.
 */
function newAttemptId(now = new Date()) {
  const stamp = now.toISOString().replace(/[-:T]/g, '').slice(0, 14);
  const rand = Math.random().toString(36).slice(2, 6);
  return `ai_${stamp}_${rand}`;
}

function createAttemptDir(caseDir, attemptId) {
  const dir = path.join(versionsDir(caseDir), attemptId);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function readJsonSafe(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return null; }
}

function writeMeta(caseDir, patch) {
  const current = readJsonSafe(metaPath(caseDir)) || {};
  const next = {
    schema: 'moodify.studio.meta/0.1',
    case_dir: caseDir,
    ...current,
    ...patch,
    updated_at: new Date().toISOString(),
  };
  fs.mkdirSync(studioDir(caseDir), { recursive: true });
  fs.writeFileSync(metaPath(caseDir), JSON.stringify(next, null, 2), 'utf8');
  return next;
}

function readMeta(caseDir) {
  return readJsonSafe(metaPath(caseDir));
}

/**
 * Every version for this case, original first, then AI attempts oldest → newest.
 *
 * @param {string} caseDir
 * @param {string|null} sourcePath  the case source, used for the `original` entry
 */
function listVersions(caseDir, sourcePath) {
  const out = [];

  if (sourcePath && fs.existsSync(sourcePath)) {
    out.push({
      id: 'original',
      kind: 'original',
      label: '原版',
      target: null,
      audioPath: sourcePath,
      evidencePath: null,
      status: null,
      createdAt: null,
    });
  }

  let entries = [];
  try {
    entries = fs.readdirSync(versionsDir(caseDir), { withFileTypes: true });
  } catch { return out; }

  const attempts = entries
    .filter((e) => e.isDirectory() && e.name.startsWith('ai_'))
    .map((e) => e.name)
    .sort(); // ids start with a UTC timestamp, so lexical order is chronological

  for (const id of attempts) {
    const dir = path.join(versionsDir(caseDir), id);
    const evidencePath = path.join(dir, 'evidence.json');
    const evidence = readJsonSafe(evidencePath);
    // The audio file lives in out/; find it rather than reconstructing the name, so a
    // future rename in Core's exporter cannot silently break the list.
    let audioPath = null;
    try {
      const files = fs.readdirSync(path.join(dir, 'out'), { withFileTypes: true });
      const wav = files.find((f) => f.isFile() && f.name.toLowerCase().endsWith('.wav'));
      if (wav) audioPath = path.join(dir, 'out', wav.name);
    } catch { /* attempt may have failed before producing audio */ }

    out.push({
      id,
      kind: 'ai',
      label: evidence && evidence.target ? targetLabel(evidence.target) : 'AI 版本',
      target: (evidence && evidence.target) || null,
      audioPath,
      evidencePath: fs.existsSync(evidencePath) ? evidencePath : null,
      status: (evidence && evidence.status) || null,
      reviewRequired: Boolean(evidence && evidence.review_required),
      createdAt: (evidence && evidence.created_at) || null,
    });
  }

  return out;
}

function readEvidence(caseDir, versionId) {
  const dir = path.join(versionsDir(caseDir), String(versionId || ''));
  return readJsonSafe(path.join(dir, 'evidence.json'));
}

function readSelection(caseDir) {
  return readJsonSafe(selectionPath(caseDir));
}

/**
 * Record the human's choice. This is the only place a version becomes "chosen", and it
 * is always the result of an explicit user action — never automatic.
 */
function writeSelection(caseDir, { versionId, note }) {
  const versions = listVersions(caseDir, null);
  const payload = {
    schema: 'moodify.studio.selection/0.1',
    version_id: versionId,
    note: note || null,
    chosen_at: new Date().toISOString(),
    // A copy of what was true at choice time, so the record stays readable even if the
    // version directory is later removed.
    version_count_at_choice: versions.length,
  };
  fs.mkdirSync(studioDir(caseDir), { recursive: true });
  fs.writeFileSync(selectionPath(caseDir), JSON.stringify(payload, null, 2), 'utf8');
  return payload;
}

/** Human-facing label for a target. Kept next to the ids so they cannot drift apart. */
const TARGET_LABELS = Object.freeze({
  clean_master: '更干净、更适合发布',
  warm_vocal: '人声更暖、更贴',
  wide_space: '更宽、更有空间感',
  // Labelled so the UI can name it, but see PLANNED_TARGETS: there is no preset behind it.
  streaming_ready: '更适合流媒体（Spotify 等）',
});

/**
 * Targets the product spec lists that Core cannot actually perform yet.
 *
 * WHY THIS EXISTS INSTEAD OF A MAPPING
 *   The product spec lists `streaming_ready`. Core has exactly three presets
 *   (clean_master / warm_vocal / wide_space). Mapping `streaming_ready` onto
 *   `clean_master` would make the UI say "更适合流媒体" while running generic
 *   clean-master processing — the button would promise something it does not do.
 *
 *   Inventing a real `streaming_ready` preset means choosing 15 parameter values, i.e.
 *   deciding what "more suitable for streaming" sounds like. That is a
 *   "what sounds better" judgement, which AGENTS.md reserves to humans. So it is shown
 *   as not-yet-available rather than faked.
 */
const PLANNED_TARGETS = Object.freeze([
  { id: 'streaming_ready', reason: 'Core 尚无对应预设；新增预设等于替人类决定"什么叫更适合流媒体"，需人类确认参数' },
]);

function targetLabel(target) {
  return TARGET_LABELS[target] || target;
}

module.exports = {
  STUDIO_DIR,
  TARGET_LABELS,
  PLANNED_TARGETS,
  targetLabel,
  studioDir,
  versionsDir,
  exportDir,
  ensureDirs,
  newAttemptId,
  createAttemptDir,
  listVersions,
  readEvidence,
  readMeta,
  writeMeta,
  readSelection,
  writeSelection,
};
