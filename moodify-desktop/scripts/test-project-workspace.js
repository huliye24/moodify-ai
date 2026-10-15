#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const projects = require('../src/project-workspace');

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-projects-'));
const cases = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-cases-'));

try {
  const project = projects.createProject(root, { title: '网剧 A', client_name: '制作公司' });
  const cue = projects.createCue(root, project.project_id, {
    title: 'EP01 情感转折', scene: '人物第一次承认感情', creative_intent: '克制，不煽情',
    target_duration_s: 92, dialogue_present: true,
  });
  const caseDir = path.join(cases, 'case_001');
  fs.mkdirSync(caseDir);
  fs.writeFileSync(path.join(caseDir, 'report.json'), JSON.stringify({
    source: { name: 'candidate.wav', sha256: 'sha256:' + 'a'.repeat(64) }, findings: [{}],
    technical_state: { workflow_decision: 'HUMAN_REQUIRED', reasons: ['UNCALIBRATED'] },
  }));
  const first = projects.linkCandidate(root, cases, project.project_id, cue.cue_id, caseDir);
  const duplicate = projects.linkCandidate(root, cases, project.project_id, cue.cue_id, caseDir);
  assert.strictEqual(duplicate.candidate_id, first.candidate_id, 'same case link must be idempotent');
  const view = projects.snapshot(root, cases);
  assert.strictEqual(view.projects.length, 1);
  assert.strictEqual(view.projects[0].cues.length, 1);
  assert.strictEqual(view.projects[0].cues[0].candidates.length, 1);
  assert.strictEqual(view.projects[0].cues[0].candidates[0].hear_status, 'HEARD');
  assert.strictEqual(view.projects[0].cues[0].candidates[0].judge_status, 'HUMAN_REQUIRED');
  assert.throws(() => projects.linkCandidate(root, cases, project.project_id, cue.cue_id, root), /INVALID_CASE_DIR/);
  console.log('project workspace: 8 assertions passed');
} finally {
  fs.rmSync(root, { recursive: true, force: true });
  fs.rmSync(cases, { recursive: true, force: true });
}
