'use strict';
/**
 * 外部运行时解析器（HOTFIX 000 / F4）。
 *
 * 为什么存在
 *   「快速分离 / MIDI / 曲谱」依赖壳外专用 venv（.venv-basic-pitch / .venv-score），
 *   而不是随包发布的运行时。旧实现在 venv 缺失时**静默回退到系统 python**：
 *
 *       return fs.existsSync(exe) ? exe : PYTHON;   // ← 已移除
 *
 *   系统 python 通常跑不动这条链（librosa → sklearn → pandas 的 ABI 不匹配），
 *   于是用户看到的是深层 pandas/numpy traceback，而不是「缺依赖」。
 *
 * 现在的行为
 *   专用运行时缺失 → 抛 RuntimeMissingError（code = DEPENDENCY_MISSING）。
 *   绝不静默回退，绝不用一个已知跑不通的解释器去起子进程。
 *
 * 本模块不依赖 Electron，可被 node 直接 require 做无头测试。
 */

const fs = require('fs');
const path = require('path');

const CODE_DEPENDENCY_MISSING = 'DEPENDENCY_MISSING';

// 专用运行时清单。dir 是打包/开发布局下的默认位置；envVar 允许显式覆盖。
// 注意：envVar 指向的是**同一个专用 venv**，不是「随便一个 python」——
// 覆盖是显式的、要校验的，与「静默回退」是两件事。
const RUNTIMES = {
  'basic-pitch': {
    label: 'Basic Pitch（快速分离 / MIDI）',
    envVar: 'MOODIFY_VENV_BASIC_PITCH',
    dir: path.join(__dirname, '..', '..', '.venv-basic-pitch'),
    python: path.join('Scripts', 'python.exe'),
    tools: { 'basic-pitch': path.join('Scripts', 'basic-pitch.exe') },
  },
  score: {
    label: 'music21（MIDI → 曲谱）',
    envVar: 'MOODIFY_VENV_SCORE',
    dir: path.join(__dirname, '..', '..', '.venv-score'),
    python: path.join('Scripts', 'python.exe'),
    tools: {},
  },
};

class RuntimeMissingError extends Error {
  constructor(runtime, candidates) {
    super(`缺少必需的 Moodify 外部运行时：${runtime}（${RUNTIMES[runtime] ? RUNTIMES[runtime].label : '未知'}）`);
    this.name = 'RuntimeMissingError';
    this.code = CODE_DEPENDENCY_MISSING;
    this.runtime = runtime;
    this.candidates = candidates;
  }

  /** 转成壳内统一的 IPC 结果形状（与 { ok:false, code, reason } 约定一致）。 */
  toResult() {
    return {
      ok: false,
      code: this.code,
      runtime: this.runtime,
      reason: this.message,
      candidates: this.candidates,
    };
  }
}

/** 运行时名是否已登记（拼错名字是编程错误，不是缺依赖）。 */
function isKnownRuntime(name) {
  return Object.prototype.hasOwnProperty.call(RUNTIMES, name);
}

/** 该运行时在当前环境下会去哪些目录找（显式覆盖在前）。 */
function runtimeCandidates(name, options = {}) {
  if (!isKnownRuntime(name)) throw new Error(`unknown Moodify runtime: ${name}`);
  const spec = RUNTIMES[name];
  const out = [];
  const envValue = process.env[spec.envVar];
  if (envValue && envValue.trim()) out.push(path.resolve(envValue.trim()));
  out.push(spec.dir);
  if (Array.isArray(options.extraCandidates)) {
    for (const extra of options.extraCandidates) if (extra) out.push(path.resolve(extra));
  }
  return out;
}

/**
 * 解析专用运行时。
 * @returns {{ name: string, dir: string, python: string }}
 * @throws {RuntimeMissingError} 找不到时——不返回任何回退解释器。
 */
function resolveRuntime(name, options = {}) {
  if (!isKnownRuntime(name)) throw new Error(`unknown Moodify runtime: ${name}`);
  const spec = RUNTIMES[name];
  const candidates = options.candidates || runtimeCandidates(name, options);

  for (const dir of candidates) {
    const python = path.join(dir, spec.python);
    if (fs.existsSync(python)) return { name, dir, python };
  }
  throw new RuntimeMissingError(name, candidates);
}

/**
 * 解析运行时内的某个工具可执行文件（如 basic-pitch.exe）。
 * @throws {RuntimeMissingError} 运行时缺失，或运行时在但工具缺失。
 */
function resolveRuntimeTool(name, tool, options = {}) {
  const resolved = resolveRuntime(name, options);
  const spec = RUNTIMES[name];
  const relative = spec.tools[tool];
  if (!relative) throw new Error(`runtime ${name} declares no tool: ${tool}`);
  const exe = path.join(resolved.dir, relative);
  if (!fs.existsSync(exe)) {
    const err = new RuntimeMissingError(name, [resolved.dir]);
    err.message = `运行时 ${name} 存在，但缺少可执行工具：${tool}`;
    throw err;
  }
  return exe;
}

/** 便捷包装：把解析失败统一成 IPC 结果；成功时返回 { exe }。 */
function tryResolve(fn) {
  try {
    return { ok: true, exe: fn() };
  } catch (err) {
    if (err instanceof RuntimeMissingError) return err.toResult();
    throw err;
  }
}

module.exports = {
  CODE_DEPENDENCY_MISSING,
  RUNTIMES,
  RuntimeMissingError,
  isKnownRuntime,
  resolveRuntime,
  resolveRuntimeTool,
  runtimeCandidates,
  tryResolve,
};
