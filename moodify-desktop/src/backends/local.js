/**
 * ⚠️ RETIRED 2026-10-04 — 三预设作为产品面已退场（人类裁定），本文件不再被 main.js 引用。
 *
 * 本地后处理后端：把 `clean_master` / `warm_vocal` / `wide_space` 三个预设映射到 Core 的
 * `protocol process`。三预设已退场，这条预设路径不再是产品面。
 *
 * 未删除的原因：删除文件属不可逆动作，按仓库纪律留在磁盘上供审阅对比，
 * 待人类确认后整体删除。**不要为它新增调用方。**
 *
 * ──────────────────────────────────────────────────────────────────────────────
 */

/**
 * LocalBackend — runs the Moodify Sound Protocol `process` job on this machine.
 *
 * Studio v0.2 section 3 requires the "run analysis / run post-processing" step to be a
 * switchable backend behind one contract, so that a CloudBackend can be added later
 * without touching the UI. This file is the local implementation of that contract.
 *
 * CONTRACT (shared with every backend; see backends/index.js)
 *   process({ sourcePath, target, versionDir }, deps) ->
 *     { ok: true,  versionDir, output, evidencePath, evidence }
 *     { ok: false, reason, code? }
 *
 * deps = { runPython, lastJsonLine } — injected so this module never imports Electron.
 *
 * WHAT IT DOES NOT DO
 *   - It does not implement DSP. The actual post-processing is Core's
 *     `v01_pipeline.process_audio`, reached through the protocol `process` job.
 *     Studio only ever *asks*; Core decides what processing means.
 *   - It does not write the user's only copy. Output always lands in a fresh
 *     `versionDir`, never over the source.
 *
 * WHY versionDir IS UNIQUE PER ATTEMPT
 *   Core's `validate_job` refuses to overwrite an existing output
 *   ("refusing to overwrite existing output"). Giving every attempt its own directory
 *   satisfies that guard by construction, and it is also what Studio v0.2 section 1.3
 *   requires: a new attempt must never silently overwrite a version the user already
 *   confirmed. Verified against the real CLI before this file was written.
 */

'use strict';

const fs = require('fs');
const path = require('path');

const PROTOCOL = 'moodify.sound/0.2';
const JOB_TYPE = 'process';

/**
 * The targets Studio may offer.
 *
 * These map 1:1 onto presets that actually exist in Core
 * (moodify-core-package/src/moodify/v01_presets.py). If a target is listed here but has
 * no preset behind it, the UI is promising something it cannot do — so the list is
 * deliberately the three real ones. See docs/reports/ for why `streaming_ready`, which
 * the product spec lists, is NOT here yet.
 */
const TARGETS = Object.freeze(['clean_master', 'warm_vocal', 'wide_space']);

const DEFAULT_TARGET = 'clean_master';

function isSupportedTarget(target) {
  return TARGETS.includes(target);
}

/**
 * Run one processing attempt.
 *
 * @param {{sourcePath: string, target: string, versionDir: string, attemptId: string}} spec
 * @param {{runPython: Function, lastJsonLine: Function}} deps
 */
async function process(spec, deps) {
  const { sourcePath, target, versionDir, attemptId } = spec;
  const { runPython, lastJsonLine } = deps;

  if (!isSupportedTarget(target)) {
    return { ok: false, reason: `未知目标：${target}（可用：${TARGETS.join(', ')}）` };
  }
  if (!sourcePath || !fs.existsSync(sourcePath)) {
    return { ok: false, reason: '源音频不存在：' + String(sourcePath) };
  }

  // The output directory is the version directory itself, so the resulting file is
  // unique to this attempt and cannot collide with a previously confirmed version.
  const outDir = path.join(versionDir, 'out');
  fs.mkdirSync(outDir, { recursive: true });

  // Absolute paths on purpose. Job paths resolve against the job file's directory, and
  // an absolute path is unambiguous regardless of where the job file sits.
  const job = {
    protocol: PROTOCOL,
    type: JOB_TYPE,
    source: path.resolve(sourcePath),
    preset: target,
    output_dir: path.resolve(outDir),
  };
  const jobPath = path.join(versionDir, 'job.json');
  fs.writeFileSync(jobPath, JSON.stringify(job, null, 2), 'utf8');

  // 1) validate — pure check, no side effects. Fail here rather than half-way through.
  const v = await runPython(['-m', 'moodify.release_cli', 'protocol', 'validate', jobPath]);
  if (v.code !== 0) {
    return { ok: false, code: v.code, reason: (v.stderr || '').trim().slice(-300) || '作业校验失败' };
  }

  // 2) process — this is the actual "let AI process it" step.
  const p = await runPython(['-m', 'moodify.release_cli', 'protocol', 'process', jobPath]);
  const result = lastJsonLine(p.stdout || '');
  if (p.code !== 0 || !result) {
    // The CLI prints its error as JSON on stderr with exit 2; surface that text.
    const err = lastJsonLine(p.stderr || '');
    const reason = (err && err.error) || (p.stderr || '').trim().slice(-300) || '后处理失败';
    return { ok: false, code: p.code, reason };
  }

  const outputPath = result.output;
  if (!outputPath || !fs.existsSync(outputPath)) {
    return { ok: false, reason: '处理报告成功但未找到输出文件' };
  }

  // 3) evidence — Studio v0.2 section 6 requires input hash, output hash, target/preset,
  // key parameters, timestamp and backend kind. The Core's own result already carries the
  // hashes, the preset and the full parameter set; we add provenance around it and keep
  // the Core's JSON verbatim under `result` so nothing is paraphrased.
  const evidence = {
    schema: 'moodify.studio.version-evidence/0.1',
    backend: 'local',
    target,
    attempt_id: attemptId,
    created_at: new Date().toISOString(),
    source_path: job.source,
    source_sha256: result.source_sha256 || null,
    output_path: outputPath,
    output_sha256: result.output_sha256 || null,
    preset: result.preset || target,
    core_parameters: result.core_parameters || null,
    // `processed_review_required` = "what ran", NOT "this audio passed review".
    // Studio shows this verbatim as 已处理，待人确认. See section 1.3: 生成 ≠ 完成.
    status: result.status || null,
    review_required: result.review_required === true,
    result,
  };
  const evidencePath = path.join(versionDir, 'evidence.json');
  fs.writeFileSync(evidencePath, JSON.stringify(evidence, null, 2), 'utf8');

  return { ok: true, versionDir, output: outputPath, evidencePath, evidence };
}

module.exports = {
  kind: 'local',
  label: '本机',
  process,
  TARGETS,
  DEFAULT_TARGET,
  isSupportedTarget,
};
