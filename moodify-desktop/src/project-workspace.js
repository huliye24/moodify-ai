'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PROJECT_SCHEMA = 'moodify.commercial.project/0.1';
const CUE_SCHEMA = 'moodify.commercial.cue/0.1';
const CANDIDATE_SCHEMA = 'moodify.commercial.candidate-link/0.1';

function safeId(prefix) {
  return `${prefix}_${new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)}_${crypto.randomBytes(4).toString('hex')}`;
}

function nonEmpty(value, field) {
  const text = String(value || '').trim();
  if (!text) throw new Error(`${field} 不能为空`);
  return text;
}

function atomicJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const attempt = `${file}.tmp-${process.pid}-${crypto.randomBytes(3).toString('hex')}`;
  fs.writeFileSync(attempt, JSON.stringify(value, null, 2), 'utf8');
  fs.renameSync(attempt, file);
}

function readJson(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return null; }
}

function projectDir(root, projectId) { return path.join(root, projectId); }
function cueDir(root, projectId, cueId) { return path.join(projectDir(root, projectId), 'cues', cueId); }

function createProject(root, input) {
  const projectId = safeId('project');
  const record = {
    schema: PROJECT_SCHEMA,
    project_id: projectId,
    title: nonEmpty(input.title, '项目名称'),
    client_name: String(input.client_name || 'INTERNAL').trim() || 'INTERNAL',
    production_type: String(input.production_type || 'WEB_SERIES').trim() || 'WEB_SERIES',
    delivery_spec_ref: String(input.delivery_spec_ref || '待项目确认').trim() || '待项目确认',
    created_at: new Date().toISOString(),
  };
  const dir = projectDir(root, projectId);
  if (fs.existsSync(dir)) throw new Error('PROJECT_ALREADY_EXISTS');
  atomicJson(path.join(dir, 'project.json'), record);
  return record;
}

function createCue(root, projectId, input) {
  const project = readJson(path.join(projectDir(root, projectId), 'project.json'));
  if (!project) throw new Error('PROJECT_NOT_FOUND');
  const cueId = safeId('cue');
  const duration = Number(input.target_duration_s || 0);
  if (!Number.isFinite(duration) || duration <= 0) throw new Error('目标时长必须大于 0');
  const record = {
    schema: CUE_SCHEMA,
    cue_id: cueId,
    project_id: projectId,
    title: nonEmpty(input.title, 'Cue 名称'),
    kind: String(input.kind || 'SCORE'),
    scene: nonEmpty(input.scene, '场景'),
    creative_intent: nonEmpty(input.creative_intent, '创作意图'),
    target_duration_s: duration,
    dialogue_present: Boolean(input.dialogue_present),
    vocal_preference: String(input.vocal_preference || 'EITHER'),
    created_at: new Date().toISOString(),
  };
  atomicJson(path.join(cueDir(root, projectId, cueId), 'cue.json'), record);
  return record;
}

function linkCandidate(root, casesRoot, projectId, cueId, caseDir) {
  const cue = readJson(path.join(cueDir(root, projectId, cueId), 'cue.json'));
  if (!cue) throw new Error('CUE_NOT_FOUND');
  const resolvedCases = path.resolve(casesRoot);
  const resolvedCase = path.resolve(caseDir);
  const rel = path.relative(resolvedCases, resolvedCase);
  if (!rel || rel.startsWith('..') || path.isAbsolute(rel)) throw new Error('INVALID_CASE_DIR');
  const report = readJson(path.join(resolvedCase, 'report.json'));
  if (!report) throw new Error('REPORT_NOT_FOUND');
  const caseId = path.basename(resolvedCase);
  const file = path.join(cueDir(root, projectId, cueId), 'candidates.jsonl');
  const existing = readJsonLines(file);
  const same = existing.find((row) => row.case_id === caseId);
  if (same) return same;
  const record = {
    schema: CANDIDATE_SCHEMA,
    candidate_id: safeId('candidate'),
    cue_id: cueId,
    case_id: caseId,
    source_name: report.source && report.source.name || caseId,
    source_sha256: report.source && report.source.sha256 || null,
    linked_at: new Date().toISOString(),
  };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.appendFileSync(file, JSON.stringify(record) + '\n', 'utf8');
  return record;
}

function readJsonLines(file) {
  try {
    return fs.readFileSync(file, 'utf8').split(/\r?\n/).filter(Boolean).map((line) => JSON.parse(line));
  } catch { return []; }
}

function candidateProjection(casesRoot, link) {
  const reportPath = path.join(casesRoot, link.case_id, 'report.json');
  const report = readJson(reportPath);
  const technical = report && report.technical_state || {};
  return {
    ...link,
    case_dir: path.dirname(reportPath),
    report_path: reportPath,
    hear_status: report ? 'HEARD' : 'MISSING',
    judge_status: technical.workflow_decision || 'HUMAN_REQUIRED',
    judge_reasons: technical.reasons || [],
    finding_count: report && Array.isArray(report.findings) ? report.findings.length : 0,
  };
}

function snapshot(root, casesRoot) {
  let dirs = [];
  try { dirs = fs.readdirSync(root, { withFileTypes: true }); } catch { return { projects: [] }; }
  const projects = [];
  for (const entry of dirs.filter((item) => item.isDirectory())) {
    const project = readJson(path.join(root, entry.name, 'project.json'));
    if (!project || project.schema !== PROJECT_SCHEMA) continue;
    let cueEntries = [];
    try { cueEntries = fs.readdirSync(path.join(root, entry.name, 'cues'), { withFileTypes: true }); } catch { /* empty */ }
    const cues = [];
    for (const cueEntry of cueEntries.filter((item) => item.isDirectory())) {
      const dir = cueDir(root, project.project_id, cueEntry.name);
      const cue = readJson(path.join(dir, 'cue.json'));
      if (!cue || cue.schema !== CUE_SCHEMA) continue;
      const candidates = readJsonLines(path.join(dir, 'candidates.jsonl'))
        .map((row) => candidateProjection(casesRoot, row));
      cues.push({ ...cue, candidates });
    }
    cues.sort((a, b) => a.created_at.localeCompare(b.created_at));
    projects.push({ ...project, cues });
  }
  projects.sort((a, b) => b.created_at.localeCompare(a.created_at));
  return { projects };
}

module.exports = { createProject, createCue, linkCandidate, snapshot };
