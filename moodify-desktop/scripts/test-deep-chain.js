#!/usr/bin/env node
/**
 * 深度处理链路的真实回归测试（DEEP-PROCESSING-GAP-SCAN-001）。
 *
 * WHY THIS EXISTS
 *   「深度处理」这条链（逆向分解 → 可逆性 → 结构）曾经在真实机器上**完全不可达**，
 *   而且没有任何测试发现它：
 *
 *     · `dsp_separate.py` import 了 librosa.decompose，导入链是
 *       librosa → sklearn → pandas → numpy C-ABI，在 numpy 2.x 上直接抛
 *       `ValueError: numpy.dtype size changed`；
 *     · `.venv-basic-pitch` / `.venv-score` 从未被安装过，`midi:run` 永远返回
 *       DEPENDENCY_MISSING；
 *     · 「可逆性」只是门禁上的一个字，没人验证过把分轨加起来能不能回到原版。
 *
 *   单元测试全绿，产品功能全废——因为**没有一个测试真的跑过那条链**。
 *   这个文件补的就是那一层：它拿一段合成音频真的跑脚本，然后断言产物内容。
 *
 * 它只依赖 `.venv-audio`（numpy+scipy+soundfile，几十 MB）。模型分离与 Basic Pitch
 * 需要重量级运行时，因此这里只验证**接线与诚实降级**，不跑推理（那属于验收而非 CI）。
 *
 * Run: node scripts/test-deep-chain.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const SCRIPTS = path.join(__dirname);
const rt = require(path.join(__dirname, '..', 'src', 'runtime'));
const pipeline = require(path.join(__dirname, '..', 'src', 'pipeline'));

let failures = 0;
const tmpDirs = [];

function check(name, fn) {
  try {
    fn();
    console.log(`  ok    ${name}`);
  } catch (err) {
    failures += 1;
    console.error(`  FAIL  ${name}`);
    console.error(`        ${err.message}`);
  }
}

function tmp(prefix) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  tmpDirs.push(dir);
  return dir;
}

/**
 * 找出一个能跑这些脚本的解释器。
 *
 * 顺序刻意如此：
 *   1. `runtime.js` 解析出的专用运行时（`.venv-audio`）——**这是产品的真实路径**，
 *      应用就是这么找解释器的，所以优先测它。
 *   2. 退回到系统 python，**仅当它真的装了 numpy+scipy+soundfile**。
 *
 * 为什么允许第 2 步：CI 里没有 `.venv-audio`（虚拟环境不进仓库），
 * 但流水线会显式安装 `requirements-audio.txt`。若只认 `.venv-audio`，
 * CI 里这条测试会**永远如实跳过**——而「永远跳过的测试」正是这条链当初
 * 全绿却完全不可达的原因。退回系统 python 不违反产品纪律：
 * 产品代码仍然只走 runtime.js，这里退的只是**测试的解释器**，
 * 而且必须先验证依赖真的存在（rc !== 0 就不退）。
 */
function findAudioPython() {
  const candidates = [];
  try {
    candidates.push({ exe: rt.resolveRuntime('audio').python, how: 'dedicated runtime (.venv-audio)' });
  } catch { /* 没装专用运行时，试系统 python */ }
  candidates.push({ exe: process.env.MOODIFY_PYTHON || 'python', how: 'system python (CI)' });

  for (const c of candidates) {
    const probe = spawnSync(c.exe, ['-c', 'import numpy, scipy, soundfile'],
      { encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1' } });
    if (!probe.error && probe.status === 0) return c;
  }
  return null;
}

console.log('moodify-desktop deep chain (separate → reversibility → structure)');

const audio = findAudioPython();
const PY = audio ? audio.exe : null;
if (PY) console.log(`  using: ${PY}  (${audio.how})\n`);

/**
 * 合成一段「居中人声 + 偏侧伴奏」的立体声测试音频。
 *
 * 为什么必须是合成的而不是拿一首真歌：测试要能在任何机器上确定性通过，
 * 且不能把私有音频带进仓库（AGENTS.md：不引入私有音频）。
 * 这个信号同时含中置成分（用于中置估计）与瞬态成分（用于 HPSS），
 * 因此两条 DSP 路径都会被真的执行到。
 */
function writeFixture(dir, python) {
  const wav = path.join(dir, 'fixture.wav');
  const gen = path.join(dir, 'gen.py');
  fs.writeFileSync(gen, [
    'import sys, numpy as np, soundfile as sf',
    'sr = 44100',
    'dur = 4.0',
    't = np.linspace(0, dur, int(sr*dur), endpoint=False)',
    '# 中置人声：左右完全相同',
    'voc = 0.30*np.sin(2*np.pi*440*t) + 0.10*np.sin(2*np.pi*660*t)',
    '# 偏侧伴奏：只在左声道有低频，右声道有噪声瞬态',
    'rng = np.random.default_rng(7)',
    'bass = 0.25*np.sin(2*np.pi*110*t)',
    'hits = np.zeros_like(t)',
    'for k in range(int(dur*2)):',
    '    i = int(k*sr/2)',
    '    hits[i:i+400] += rng.standard_normal(400)*0.5',
    'L = voc + bass + hits',
    'R = voc + hits*0.3',
    'y = np.stack([L, R], axis=1).astype("float32")',
    'y /= max(1e-9, np.abs(y).max())',
    'y *= 0.7',
    'sf.write(sys.argv[1], y, sr)',
    'print("fixture ok", y.shape, sr)',
  ].join('\n'), 'utf8');
  const res = spawnSync(python, [gen, wav], { encoding: 'utf8' });
  assert.strictEqual(res.status, 0, `fixture generation failed: ${res.stderr}`);
  return wav;
}

function run(python, args) {
  const env = { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' };
  return spawnSync(python, args, { encoding: 'utf8', env });
}

function lastJson(text) {
  const lines = String(text || '').trimEnd().split('\n');
  for (let i = lines.length - 1; i >= 0; i -= 1) {
    const s = lines[i].trim();
    if (!s) continue;
    try { return JSON.parse(s); } catch { /* keep scanning */ }
  }
  return null;
}

// ── 1. 运行时清单 ───────────────────────────────────────────────────────────────
console.log('\n1. 运行时清单：新引擎各有一个可解析的运行时');

check('audio / demucs / basic-pitch 都登记了环境变量覆盖与 python 入口', () => {
  for (const name of ['audio', 'demucs', 'basic-pitch', 'score']) {
    assert.ok(rt.RUNTIMES[name], `${name} must be declared`);
    assert.ok(rt.RUNTIMES[name].envVar, `${name} must declare an env override`);
    assert.ok(rt.RUNTIMES[name].python, `${name} must declare a python entry point`);
  }
});

check('probeRuntime 只报告事实，不抛异常也不回退', () => {
  const probe = rt.probeRuntime('demucs');
  assert.strictEqual(probe.name, 'demucs');
  assert.strictEqual(typeof probe.available, 'boolean');
  if (!probe.available) {
    assert.ok(probe.reason, 'missing runtime must carry a reason');
    assert.ok(/pip install/.test(probe.install), 'missing runtime must carry an install hint');
  }
});

check('未知运行时名仍然是编程错误，不是「缺依赖」', () => {
  assert.throws(() => rt.probeRuntime('nope'), /unknown Moodify runtime/);
});

if (!PY) {
  console.log('\n  SKIP  未安装 .venv-audio —— 深度链路未经真实产物验证');
  console.log('        (this is a skip, not a pass)');
  console.log('        install: python -m venv .venv-audio && '
    + '.venv-audio/Scripts/python -m pip install -r moodify-desktop/scripts/requirements-audio.txt');
} else {
  // ── 2. 快速分离真的跑起来 ─────────────────────────────────────────────────────
  console.log('\n2. 快速分离：脚本能在没有 sklearn/pandas 的解释器上跑完');

  const dir = tmp('moodify-deep-');
  const wav = writeFixture(dir, PY);
  const stemsDir = path.join(dir, 'stems');

  const sep = run(PY, [path.join(SCRIPTS, 'dsp_separate.py'), wav, '--outdir', stemsDir]);

  check('dsp_separate.py 退出码 0（曾经在 librosa→sklearn→pandas 导入链上必崩）', () => {
    assert.strictEqual(sep.status, 0,
      `exit ${sep.status}\nstdout: ${sep.stdout}\nstderr: ${sep.stderr}`);
  });

  const manifestPath = path.join(stemsDir, 'manifest.json');
  let manifest = null;
  check('写出 manifest.json 且声明引擎等级与划分', () => {
    assert.ok(fs.existsSync(manifestPath), 'manifest must exist');
    manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    assert.strictEqual(manifest.engine, 'dsp_center_hpss');
    assert.strictEqual(manifest.engine_grade, 'PREVIEW_NOT_MASTERING_GRADE',
      '预览级必须写进产物，不能只在文档里');
    assert.ok(manifest.partition && Array.isArray(manifest.partition.primary),
      '必须声明哪几轨相加等于原版，否则可逆性验证只能靠猜');
    assert.strictEqual(manifest.partition.primary.length, 2);
  });

  check('四轨都真的写出了 wav，且不全是静音', () => {
    const files = fs.readdirSync(stemsDir).filter((f) => f.endsWith('.wav'));
    assert.strictEqual(files.length, 4, `expected 4 stems, got ${files.join(', ')}`);
    for (const f of files) {
      const size = fs.statSync(path.join(stemsDir, f)).size;
      assert.ok(size > 1000, `${f} looks empty (${size} bytes)`);
    }
  });

  // ── 3. 可逆性验证 ─────────────────────────────────────────────────────────────
  console.log('\n3. 可逆性：分轨按划分相加必须回到原版');

  const rtOut = path.join(dir, 'studio', 'roundtrip.json');
  const rtRun = run(PY, [path.join(SCRIPTS, 'roundtrip.py'), '--stems', stemsDir,
    '--original', wav, '--out', rtOut]);
  const rtArtifact = fs.existsSync(rtOut) ? JSON.parse(fs.readFileSync(rtOut, 'utf8')) : null;

  check('roundtrip.py 对 DSP 划分给出 passed=true（中置划分是精确分解）', () => {
    assert.ok(rtArtifact, `no artifact; stderr: ${rtRun.stderr}`);
    assert.strictEqual(rtArtifact.passed, true,
      `null depth ${rtArtifact && rtArtifact.measurement && rtArtifact.measurement.null_depth_db} dB`);
    assert.ok(rtArtifact.measurement.null_depth_db <= -40,
      `null depth must be deep, got ${rtArtifact.measurement.null_depth_db}`);
  });

  check('可逆性产物自带「它不证明分轨质量」的说明与控制组', () => {
    assert.ok(rtArtifact.interpretation.passed_does_not_mean, 'must state what passed does NOT mean');
    assert.ok(/不表示|does_not_mean/.test(JSON.stringify(rtArtifact.interpretation)),
      'the honest boundary must travel with the artifact');
    assert.strictEqual(rtArtifact.control.kind, 'TRIVIAL_DECOMPOSITION',
      'the control proves any invertible split passes — so passed ≠ separated well');
    assert.strictEqual(rtArtifact.control.passed_if_measured, true);
  });

  check('未参与验证的轨被如实列出，不是静默丢弃', () => {
    assert.deepStrictEqual(rtArtifact.excluded_stems.slice().sort(), ['harmonic', 'percussive'],
      'the overlapping partition must be named as excluded with a reason');
    assert.ok(rtArtifact.interpretation.excluded_note, 'exclusion must be explained');
  });

  check('划分来源被记录：声明优先，搜索兜底', () => {
    assert.ok(['DECLARED_BY_ENGINE_MANIFEST', 'SEARCHED_BY_NULL_DEPTH']
      .includes(rtArtifact.partition_source));
  });

  check('原版缺失时如实失败，绝不返回一张空表', () => {
    const out2 = path.join(dir, 'rt-missing.json');
    const res = run(PY, [path.join(SCRIPTS, 'roundtrip.py'), '--stems', stemsDir,
      '--original', path.join(dir, 'nope.wav'), '--out', out2]);
    assert.notStrictEqual(res.status, 0, 'must exit non-zero');
    const art = JSON.parse(fs.readFileSync(out2, 'utf8'));
    assert.strictEqual(art.passed, false);
    assert.strictEqual(art.error, 'ORIGINAL_NOT_FOUND');
  });

  // ── 4. 结构分析 ───────────────────────────────────────────────────────────────
  console.log('\n4. 结构分析：测出速度/拍点/段落，并声明它不是曲式判断');

  const structOut = path.join(dir, 'studio', 'structure.json');
  const st = run(PY, [path.join(SCRIPTS, 'structure.py'), wav, '--out', structOut]);
  const struct = fs.existsSync(structOut) ? JSON.parse(fs.readFileSync(structOut, 'utf8')) : null;

  check('structure.py 退出码 0 并写出 structure.json', () => {
    assert.strictEqual(st.status, 0, `stderr: ${st.stderr}`);
    assert.ok(struct, 'artifact must exist');
    assert.strictEqual(struct.schema, 'moodify.studio.structure/0.1');
  });

  check('节奏字段存在，且缺失时是 null 而不是编造的数字', () => {
    assert.ok('bpm' in struct.tempo, 'bpm key must exist');
    if (struct.tempo.bpm !== null) {
      assert.ok(struct.tempo.bpm >= 40 && struct.tempo.bpm <= 200,
        `bpm out of musical range: ${struct.tempo.bpm}`);
    }
    assert.strictEqual(typeof struct.tempo.confidence, 'number');
  });

  check('能量用 dBFS 参考满幅 1.0（不是 STFT 幅度，那会低报十几 dB）', () => {
    const prof = struct.energy_profile.rms_db;
    assert.ok(Array.isArray(prof) && prof.length > 0, 'energy profile must exist');
    const peak = Math.max(...prof);
    const floor = Math.min(...prof);
    assert.ok(peak > -30, `a 0.7-peak fixture should sit well above -30 dBFS, got ${peak}`);
    assert.ok(peak <= 6, `dBFS cannot meaningfully exceed ~0 for a 0.7-peak signal, got ${peak}`);
    assert.ok(floor < peak, 'profile must vary');
  });

  check('段落只有位置编号，judgment_boundary 明说它不是主歌/副歌', () => {
    for (const s of struct.sections) {
      assert.strictEqual(typeof s.index, 'number');
      assert.ok(!('label' in s), 'sections must NOT carry verse/chorus labels');
    }
    assert.ok(struct.judgment_boundary.what_this_is_not, 'must state what it is not');
    assert.match(struct.judgment_boundary.what_this_is_not, /不是.*曲式|主歌|副歌/);
  });

  check('找不到边界时如实标记，不假装整首是一段', () => {
    assert.ok(struct.section_detection.status, 'detection status must be recorded');
    assert.ok(['ok', 'none_detected', 'flat_novelty', 'insufficient_frames']
      .includes(struct.section_detection.status));
    if (struct.section_detection.status === 'none_detected') {
      assert.match(struct.section_detection.note, /不表示这首歌没有段落结构/);
    }
  });

  // ── 5. context.json 携带真实等级与可逆性 ──────────────────────────────────────
  console.log('\n5. context.json：升级过的分轨不得被降级描述');

  check('stems.grade 来自 manifest，而不是写死的预览级', () => {
    const caseDir = path.join(dir, 'case');
    fs.mkdirSync(path.join(caseDir, 'studio'), { recursive: true });
    fs.mkdirSync(path.join(caseDir, 'stems'), { recursive: true });
    fs.writeFileSync(path.join(caseDir, 'stems', 'manifest.json'), JSON.stringify({
      engine: 'demucs',
      engine_grade: 'MODEL_SEPARATION_NOT_VERIFIED_AGAINST_ORIGINAL_STEMS',
      engine_note: 'test',
      partition: { primary: ['vocals', 'instrumental'] },
    }));
    fs.writeFileSync(path.join(caseDir, 'stems', 'a__vocals.wav'), '');
    fs.writeFileSync(path.join(caseDir, 'stems', 'a__instrumental.wav'), '');
    const ctx = pipeline.buildContext(caseDir);
    assert.strictEqual(ctx.stems.engine, 'demucs');
    assert.strictEqual(ctx.stems.grade,
      'MODEL_SEPARATION_NOT_VERIFIED_AGAINST_ORIGINAL_STEMS',
      'a model-grade split must not be described as preview-grade');
    assert.ok(ctx.stems.partition, 'the partition must travel into the context pack');
  });

  check('roundtrip.json 的内容进入 context 的可逆性块（含 null 深度与解释）', () => {
    const caseDir = path.join(dir, 'case');
    fs.writeFileSync(path.join(caseDir, 'studio', 'roundtrip.json'),
      JSON.stringify(rtArtifact));
    const ctx = pipeline.buildContext(caseDir);
    assert.strictEqual(ctx.readiness.reversibility.passed, true);
    assert.ok(typeof ctx.readiness.reversibility.null_depth_db === 'number');
    assert.ok(ctx.readiness.reversibility.partition.includes('vocals'));
    assert.ok(ctx.readiness.reversibility.interpretation,
      'the interpretation must not be dropped when entering the context pack');
  });
}

// ── cleanup ────────────────────────────────────────────────────────────────────
for (const d of tmpDirs) {
  try { fs.rmSync(d, { recursive: true, force: true }); } catch { /* best effort */ }
}

console.log(`\n${failures ? `${failures} FAILED` : 'all deep-chain checks passed'}`);
process.exit(failures ? 1 : 0);
