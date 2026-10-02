/**
 * Moodify desktop shell — Electron main process.
 *
 * Product definition (human, 2026-10-02): ONE shell, white, company logo,
 * fixed flow: pick a song → detect → data & charts → repair/mixing plan.
 * The plan is authored by Claude Code (human directive, same day): the
 * shell embeds a real terminal (node-pty + xterm.js) opened in the case
 * directory and can invoke the claude CLI directly. This shell orchestrates
 * the pip-installed core; it never reimplements measurement or judgment.
 * Every python invocation sets PYTHONUTF8=1 — the GBK console trap is a
 * product-killing bug on Chinese Windows.
 */

const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn } = require('child_process');

const CASES_ROOT = process.env.MOODIFY_CASES_ROOT
  || path.join(os.homedir(), '.moodify', 'cases');
const PYTHON = process.env.MOODIFY_PYTHON || 'python';
const AUDIO_FILTERS = [
  { name: '音频', extensions: ['flac', 'wav', 'mp3', 'm4a', 'aac', 'ogg', 'aiff', 'aif'] },
  { name: '所有文件', extensions: ['*'] },
];

function pythonEnv() {
  return { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' };
}

function runPython(args, timeoutMs = 30 * 60 * 1000) {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON, args, { env: pythonEnv() });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => child.kill(), timeoutMs);
    child.stdout.on('data', (d) => { stdout += d.toString('utf8'); });
    child.stderr.on('data', (d) => { stderr += d.toString('utf8'); });
    child.on('error', (err) => { clearTimeout(timer); reject(err); });
    child.on('close', (code) => { clearTimeout(timer); resolve({ code, stdout, stderr }); });
  });
}

/** The CLI prints exactly one JSON object on stdout; take the last parseable line. */
function lastJsonLine(text) {
  for (const line of text.trimEnd().split('\n').reverse()) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try { return JSON.parse(trimmed); } catch { /* keep scanning */ }
  }
  return null;
}

function scanArchive() {
  const rows = [];
  let entries = [];
  try { entries = fs.readdirSync(CASES_ROOT, { withFileTypes: true }); } catch { return rows; }
  for (const entry of entries) {
    if (!entry.isDirectory() || !entry.name.startsWith('case_')) continue;
    const reportPath = path.join(CASES_ROOT, entry.name, 'report.json');
    try {
      const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
      rows.push({
        caseId: (report.case && report.case.case_id) || entry.name,
        reportPath,
        sourceName: (report.source && report.source.name) || '?',
        generatedAt: report.generated_at || '?',
        overall: (report.technical_state && report.technical_state.overall) || '?',
        workflowDecision:
          (report.technical_state && report.technical_state.workflow_decision) || '?',
      });
    } catch { /* interrupted or corrupt case — skip, never fatal */ }
  }
  rows.sort((a, b) => (a.generatedAt < b.generatedAt ? 1 : -1));
  return rows;
}

// ——— embedded terminal (node-pty): one PTY per report view, in the case dir ———

const terms = new Map(); // termId -> { pty, win }

function registerTerminalIpc() {
  ipcMain.handle('pty:create', async (event, termId, cwd) => {
    if (terms.has(termId)) return true;
    const pty = require('node-pty');
    // cwd must exist or node-pty fails with 267 (invalid directory); the
    // archive root may not exist yet on first run — create it, never crash
    let dir = cwd;
    if (!dir || !fs.existsSync(dir)) {
      try { fs.mkdirSync(CASES_ROOT, { recursive: true }); } catch { /* read-only home */ }
      dir = fs.existsSync(CASES_ROOT) ? CASES_ROOT : os.homedir();
    }
    const term = pty.spawn(process.env.ComSpec || 'powershell.exe', [], {
      name: 'xterm-256color',
      cwd: dir,
      env: { ...codexEnv(), PYTHONUTF8: '1' },
    });
    const win = BrowserWindow.fromWebContents(event.sender);
    terms.set(termId, { pty, win });
    term.onData((data) => {
      const entry = terms.get(termId);
      if (entry && !entry.win.isDestroyed()) {
        entry.win.webContents.send('pty:data', termId, data);
      }
    });
    term.onExit(({ exitCode }) => {
      const entry = terms.get(termId);
      if (entry && !entry.win.isDestroyed()) {
        entry.win.webContents.send('pty:exit', termId, exitCode);
      }
      terms.delete(termId);
    });
    return true;
  });
  ipcMain.handle('pty:write', (_event, termId, data) => {
    const entry = terms.get(termId);
    if (entry) entry.pty.write(data);
  });
  ipcMain.handle('pty:resize', (_event, termId, cols, rows) => {
    const entry = terms.get(termId);
    if (entry) {
      try { entry.pty.resize(cols, rows); } catch { /* window may be shrinking */ }
    }
  });
  ipcMain.handle('pty:kill', (_event, termId) => {
    const entry = terms.get(termId);
    if (entry) {
      try { entry.pty.kill(); } catch { /* already gone */ }
      terms.delete(termId);
    }
  });
  ipcMain.handle('pty:run-command', (_event, termId, command) => {
    const entry = terms.get(termId);
    if (entry) entry.pty.write(`${command}\r`);
  });
}

function killAllTerminals() {
  for (const [, entry] of terms) {
    try { entry.pty.kill(); } catch { /* already gone */ }
  }
  terms.clear();
}

// ——— Mood 编译器 kernel: Codex app-server (JSON-RPC over stdio) ———
//
// Human adjudication 2026-10-02: embed openai/codex (Apache-2.0) as the
// compiler kernel via its app-server protocol; provider selectable at setup
// (DeepSeek / OpenAI / custom); the claude CLI channel is fully replaced.
// Config lives in an isolated CODEX_HOME so the user's own codex is untouched.

const CODEX_HOME = process.env.MOODIFY_CODEX_HOME
  || path.join(os.homedir(), '.moodify', 'codex');

const COMPILER_INSTRUCTIONS = [
  '你是 Moodify Studio 的 Mood 编译器：后处理方案工程师。你工作在一个音频检测 case 目录里，',
  '只读 case 导出物（report.json / measurements.json / judgment_rules.json / scan 图表），',
  '给出【修音与混音方案】：目标（可测量）、逐步算子建议（gain/eq/limiter/compressor/stereo 等，',
  '含参数与理由）、验收指标（使用 report.json 中同 id 指标）、风险与边界（阈值 0/16 calibrated，',
  '全部 DEFAULT_UNCALIBRATED；L3/L4/L5 判断不承诺）。方案不等于执行：你不修改 Moodify 核心、',
  '不改动阈值、不执行任何音频处理。用中文回复。',
].join('');

function resolveCodexExe() {
  const nm = path.join(__dirname, '..', 'node_modules', '@openai');
  let dirs = [];
  try { dirs = fs.readdirSync(nm).filter((d) => d.startsWith('codex-') && d !== 'codex'); } catch { return null; }
  const binName = process.platform === 'win32' ? 'codex.exe' : 'codex';
  for (const dir of dirs) {
    const vendor = path.join(nm, dir, 'vendor');
    let triples = [];
    try { triples = fs.readdirSync(vendor); } catch { continue; }
    for (const triple of triples) {
      const bin = path.join(vendor, triple, 'bin', binName);
      if (fs.existsSync(bin)) return bin;
    }
  }
  return null;
}

function codexEnv() {
  // the active provider's key lives in CODEX_HOME/providers.json; inject at
  // spawn time so config.toml's env_key resolves
  const env = { ...process.env, CODEX_HOME };
  try {
    const providers = JSON.parse(fs.readFileSync(path.join(CODEX_HOME, 'providers.json'), 'utf8'));
    if (providers.active && providers.active.apiKeyEnv && providers.active.apiKey) {
      env[providers.active.apiKeyEnv] = providers.active.apiKey;
    }
  } catch { /* first run: no provider configured yet */ }
  return env;
}

class CodexClient {
  constructor() {
    this.proc = null;
    this.nextId = 1;
    this.pending = new Map(); // request id -> {resolve, reject}
    this.ready = false;
    this.buffer = '';
    this.onEvent = null;      // (notification) => void
    this.onServerRequest = null; // (request) => void
  }

  start() {
    if (this.proc) return true;
    const exe = resolveCodexExe();
    if (!exe) return false;
    fs.mkdirSync(CODEX_HOME, { recursive: true });
    this.proc = spawn(exe, ['app-server'], { env: codexEnv() });
    this.proc.stdout.on('data', (d) => this.#consume(d.toString('utf8')));
    this.proc.stderr.on('data', () => { /* diagnostics only; protocol is on stdout */ });
    this.proc.on('exit', () => { this.proc = null; this.ready = false; this.pending.clear(); });
    return true;
  }

  #consume(chunk) {
    this.buffer += chunk;
    let idx;
    while ((idx = this.buffer.indexOf('\n')) >= 0) {
      const line = this.buffer.slice(0, idx).trim();
      this.buffer = this.buffer.slice(idx + 1);
      if (!line) continue;
      let msg;
      try { msg = JSON.parse(line); } catch { continue; }
      if (msg.id !== undefined && msg.method === undefined) {
        const entry = this.pending.get(msg.id);
        if (entry) {
          this.pending.delete(msg.id);
          if (msg.error) entry.reject(new Error(msg.error.message || JSON.stringify(msg.error)));
          else entry.resolve(msg.result);
        }
      } else if (msg.id !== undefined && msg.method) {
        if (this.onServerRequest) this.onServerRequest(msg);
      } else if (msg.method) {
        if (this.onEvent) this.onEvent(msg);
      }
    }
  }

  request(method, params) {
    return new Promise((resolve, reject) => {
      if (!this.proc && !this.start()) { reject(new Error('Codex 内核不可用（未找到 codex 二进制）')); return; }
      const id = this.nextId++;
      this.pending.set(id, { resolve, reject });
      this.proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`Codex 请求超时：${method}`));
        }
      }, 120 * 1000);
    });
  }

  respond(requestId, result) {
    if (this.proc) {
      this.proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: requestId, result }) + '\n');
    }
  }

  stop() {
    if (this.proc) {
      try { this.proc.kill(); } catch { /* already gone */ }
      this.proc = null;
      this.ready = false;
    }
  }
}

const codex = new CodexClient();

function readProviderState() {
  try {
    return JSON.parse(fs.readFileSync(path.join(CODEX_HOME, 'providers.json'), 'utf8'));
  } catch {
    return { active: null };
  }
}

function writeProviderConfig(state) {
  fs.mkdirSync(CODEX_HOME, { recursive: true });
  const p = state.active;
  const lines = [];
  // codex >=0.160 (Feb 2026) hard-removed the chat wire API: every provider
  // must speak the Responses API. DeepSeek serves /responses natively.
  if (p.kind === 'openai') {
    lines.push(`model = ${JSON.stringify(p.model || 'gpt-5.1-codex')}`);
    lines.push('preferred_auth_method = "apikey"');
  } else {
    const providerId = p.kind === 'deepseek' ? 'deepseek' : 'custom';
    lines.push(`model = ${JSON.stringify(p.model)}`);
    lines.push(`model_provider = ${JSON.stringify(providerId)}`);
    lines.push('');
    const baseUrl = p.kind === 'deepseek'
      ? 'https://api.deepseek.com/'
      : p.baseUrl.replace(/\/?$/, '/');
    lines.push(`[model_providers.${providerId}]`);
    lines.push(`name = ${JSON.stringify(p.kind === 'deepseek' ? 'DeepSeek' : 'Custom (Moodify)')}`);
    lines.push(`base_url = ${JSON.stringify(baseUrl)}`);
    lines.push('wire_api = "responses"');
    lines.push(`env_key = ${JSON.stringify(p.apiKeyEnv)}`);
  }
  fs.writeFileSync(path.join(CODEX_HOME, 'config.toml'), lines.join('\n') + '\n', 'utf8');
  // providers.json keeps the key locally per machine; config.toml only references it
  fs.writeFileSync(path.join(CODEX_HOME, 'providers.json'), JSON.stringify(state, null, 2), 'utf8');
}

function registerCodexIpc() {
  ipcMain.handle('codex:ensure', async () => {
    if (!codex.ready) {
      if (!codex.start()) return { ok: false, reason: '未找到 codex 内核（npm install 后重试）' };
      try {
        const info = await codex.request('initialize', {
          clientInfo: { name: 'moodify-studio', title: 'Moodify Studio', version: '1.0.0' },
        });
        codex.ready = true;
        let windowsSandbox = null;
        try { windowsSandbox = await codex.request('windowsSandbox/readiness', {}); } catch { /* optional */ }
        return { ok: true, info, windowsSandbox, provider: (readProviderState().active || null) };
      } catch (err) {
        codex.stop();
        return { ok: false, reason: err.message };
      }
    }
    return { ok: true, provider: (readProviderState().active || null) };
  });

  ipcMain.handle('codex:provider:get', async () => {
    const state = readProviderState();
    return { active: state.active ? { ...state.active, apiKey: undefined } : null };
  });

  ipcMain.handle('codex:provider:set', async (_e, provider) => {
    const kind = provider.kind;
    const apiKeyEnv = kind === 'openai' ? 'OPENAI_API_KEY'
      : kind === 'deepseek' ? 'DEEPSEEK_API_KEY' : 'MOODIFY_CUSTOM_API_KEY';
    const active = { kind, model: provider.model, apiKeyEnv, apiKey: provider.apiKey };
    if (kind === 'custom') active.baseUrl = provider.baseUrl;
    writeProviderConfig({ active });
    // restart the server so it picks up the new CODEX_HOME config; the
    // renderer re-invokes codex:ensure afterwards
    codex.stop();
    return { ok: true };
  });

  ipcMain.handle('codex:thread-open', async (_e, caseDir) => {
    if (!codex.ready) return { ok: false, reason: '内核未初始化' };
    // 权限模式（人类裁决 2026-10-02：提供全开档，执行畅通无阻）：
    //   standard = 工作区写入 + 敏感操作逐条审批
    //   full     = 无沙箱 + 不审批（danger-full-access / never，schema 枚举已核）
    // 注：本机 windowsSandbox notConfigured，workspace-write 实际降级 read-only；
    // full 档不做沙箱尝试，反而能让内核真正执行写入。
    const full = readProviderState().permission === 'full';
    const result = await codex.request('thread/start', {
      cwd: fs.existsSync(caseDir) ? caseDir : CASES_ROOT,
      baseInstructions: COMPILER_INSTRUCTIONS,
      sandbox: full ? 'danger-full-access' : 'workspace-write',
      approvalPolicy: full ? 'never' : 'untrusted',
    });
    return { ok: true, thread: result };
  });

  ipcMain.handle('codex:permission:get', async () => readProviderState().permission || 'standard');

  ipcMain.handle('codex:permission:set', async (_e, value) => {
    const state = readProviderState();
    state.permission = value === 'full' ? 'full' : 'standard';
    fs.writeFileSync(path.join(CODEX_HOME, 'providers.json'), JSON.stringify(state, null, 2), 'utf8');
    return state.permission;
  });

  ipcMain.handle('codex:send', async (_e, threadId, text) => {
    if (!codex.ready) return { ok: false, reason: '内核未初始化' };
    const result = await codex.request('turn/start', {
      threadId,
      input: [{ type: 'text', text }],
    });
    return { ok: true, result };
  });

  ipcMain.handle('codex:interrupt', async (_e, threadId) => {
    try { await codex.request('turn/interrupt', { threadId }); return { ok: true }; }
    catch (err) { return { ok: false, reason: err.message }; }
  });

  ipcMain.handle('codex:respond', async (_e, requestId, result) => {
    codex.respond(requestId, result);
    return true;
  });

  ipcMain.handle('codex:save-plan', async (_e, caseDir, text) => {
    const target = path.join(caseDir, 'plan.md');
    fs.writeFileSync(target, text, 'utf8');
    return target;
  });
}

codex.onEvent = (notification) => {
  for (const win of BrowserWindow.getAllWindows()) {
    if (!win.isDestroyed()) win.webContents.send('codex:event', notification);
  }
};
codex.onServerRequest = (request) => {
  for (const win of BrowserWindow.getAllWindows()) {
    if (!win.isDestroyed()) win.webContents.send('codex:server-request', request);
  }
};

function registerIpc() {
  registerTerminalIpc();
  registerCodexIpc();
  ipcMain.handle('env', async () => {
    const probe = await runPython(['-c', 'import moodify'], 60 * 1000).catch(() => null);
    return {
      casesRoot: CASES_ROOT,
      python: PYTHON,
      coreReady: Boolean(probe && probe.code === 0),
    };
  });
  ipcMain.handle('pick-audio', async (event) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    const picked = await dialog.showOpenDialog(win, {
      title: '选择音频文件', properties: ['openFile'], filters: AUDIO_FILTERS,
    });
    return picked.canceled ? null : picked.filePaths[0];
  });
  ipcMain.handle('archive:list', async () => scanArchive());
  ipcMain.handle('report:read', async (_event, reportPath) =>
    JSON.parse(fs.readFileSync(reportPath, 'utf8')));
  ipcMain.handle('analysis:run', async (_event, audioPath) => {
    const result = await runPython([
      '-m', 'moodify.release_cli', 'demo', audioPath,
      '--cases-root', CASES_ROOT, '--no-open',
    ]);
    if (result.code !== 0) {
      const payload = lastJsonLine(result.stderr);
      throw new Error((payload && payload.error) || result.stderr.trim().slice(-500)
        || `python exited with code ${result.code}`);
    }
    const payload = lastJsonLine(result.stdout);
    // remember where the audio lives so the shell can draw its waveform
    // (report.json carries only name/sha256); optional, never fatal
    try {
      const reportPath = payload && payload.reports && payload.reports.json;
      if (reportPath) {
        fs.writeFileSync(path.join(path.dirname(reportPath), 'source_path.json'),
          JSON.stringify({ path: audioPath }, null, 2), 'utf8');
      }
    } catch { /* waveform is optional */ }
    return payload;
  });
  ipcMain.handle('source:resolve', (_event, caseDir) => {
    try {
      const p = JSON.parse(fs.readFileSync(path.join(caseDir, 'source_path.json'), 'utf8'));
      return p.path && fs.existsSync(p.path) ? p.path : null;
    } catch { return null; }
  });
  ipcMain.handle('audio:read', (_event, audioPath) => fs.promises.readFile(audioPath));
  ipcMain.handle('charts:render', async (_event, reportPath) => {
    const result = await runPython([
      '-m', 'moodify.ui.chart_export', reportPath, '--out', path.join(path.dirname(reportPath), 'charts'),
    ]);
    if (result.code !== 0) {
      throw new Error(result.stderr.trim().slice(-500) || 'chart export failed');
    }
    return lastJsonLine(result.stdout);
  });

  registerStudioToolIpc();
}

// ——— 分离 / MIDI / 曲谱：显式动作，产物落 case 目录（世界产物）———
//
// 引擎 A「快速分离」= DSP 中置估计 + HPSS（本壳自带脚本，.venv-basic-pitch
// 里的 librosa 即可跑，秒级，非模型）；MIDI = basic-pitch（onnx 序列化，
// Apache-2.0）；曲谱 = music21（MIT）转 MusicXML，壳内 OSMD（BSD-3）渲染。
// 模型引擎（Demucs / BS-RoFormer）为后续「精分离」档，接入时同走 runLong。
// 所有 python 子进程强制 PYTHONUTF8=1；长任务单飞锁，进度行实时转发渲染层。

const TOOLS_ROOT = path.join(__dirname, '..', 'scripts');
const VENVS = {
  'basic-pitch': path.join(__dirname, '..', '..', '.venv-basic-pitch'),
  score: path.join(__dirname, '..', '..', '.venv-score'),
};

function pyExe(venvName) {
  const exe = path.join(VENVS[venvName], 'Scripts', 'python.exe');
  return fs.existsSync(exe) ? exe : PYTHON;
}

function insideDir(dir, p) {
  const rel = path.relative(dir, p);
  return Boolean(rel) && !rel.startsWith('..') && !path.isAbsolute(rel);
}

const longRuns = new Map(); // kind -> child process（单飞锁）

function runLong(kind, exe, args) {
  return new Promise((resolve) => {
    if (longRuns.has(kind)) {
      resolve({ ok: false, reason: '上一个同类任务还在进行中' });
      return;
    }
    const send = (line) => {
      for (const win of BrowserWindow.getAllWindows()) {
        if (!win.isDestroyed()) win.webContents.send('tool:progress', kind, line);
      }
    };
    let child;
    try {
      child = spawn(exe, args, { env: pythonEnv() });
    } catch (err) {
      resolve({ ok: false, reason: err.message });
      return;
    }
    longRuns.set(kind, child);
    let tail = '';
    const feed = (d) => {
      tail += d.toString('utf8');
      const lines = tail.split(/\r?\n/);
      tail = lines.pop();
      for (const line of lines) {
        if (line.trim()) send(line.trim());
      }
    };
    child.stdout.on('data', feed);
    child.stderr.on('data', feed);
    child.on('error', (err) => {
      longRuns.delete(kind);
      resolve({ ok: false, reason: err.message });
    });
    child.on('close', (code) => {
      longRuns.delete(kind);
      if (tail.trim()) send(tail.trim());
      resolve({ ok: code === 0, code });
    });
  });
}

function resolveCaseSource(caseDir) {
  try {
    const p = JSON.parse(fs.readFileSync(path.join(caseDir, 'source_path.json'), 'utf8')).path;
    return p && fs.existsSync(p) ? p : null;
  } catch { return null; }
}

function listCaseFiles(caseDir, subdir, exts) {
  const dir = path.join(caseDir, subdir);
  let entries = [];
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return []; }
  return entries
    .filter((e) => e.isFile() && exts.some((x) => e.name.toLowerCase().endsWith(x)))
    .map((e) => {
      const full = path.join(dir, e.name);
      let size = 0;
      try { size = fs.statSync(full).size; } catch { /* raced deletion */ }
      return { name: e.name, path: full, size };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}

function registerStudioToolIpc() {
  ipcMain.handle('casefiles:list', (_e, caseDir, subdir, exts) =>
    listCaseFiles(caseDir, subdir, exts));

  // 快速分离（引擎 A）：源音频 → case/stems/ 四轨 + manifest.json
  ipcMain.handle('stems:run', async (_e, caseDir) => {
    const src = resolveCaseSource(caseDir);
    if (!src) return { ok: false, reason: '未找到源音频（source_path.json 缺失或文件不存在）' };
    const outdir = path.join(caseDir, 'stems');
    fs.mkdirSync(outdir, { recursive: true });
    return runLong('stems', pyExe('basic-pitch'), [
      path.join(TOOLS_ROOT, 'dsp_separate.py'), src, '--outdir', outdir,
    ]);
  });

  // 音频 → MIDI（basic-pitch onnx）：输入限源音频或 case 内分离轨 → case/midi/
  ipcMain.handle('midi:run', async (_e, caseDir, audioPath) => {
    const src = resolveCaseSource(caseDir);
    const allowed = (src && path.resolve(audioPath) === path.resolve(src))
      || insideDir(caseDir, path.resolve(audioPath));
    if (!allowed) return { ok: false, reason: '输入音频必须是世界源或 case 内分离轨' };
    if (!fs.existsSync(audioPath)) return { ok: false, reason: '输入音频不存在' };
    const bpExe = path.join(VENVS['basic-pitch'], 'Scripts', 'basic-pitch.exe');
    if (!fs.existsSync(bpExe)) return { ok: false, reason: '未找到 basic-pitch（.venv-basic-pitch）' };
    const outdir = path.join(caseDir, 'midi');
    fs.mkdirSync(outdir, { recursive: true });
    return runLong('midi', bpExe, [
      '--save-midi', '--model-serialization', 'onnx', outdir, audioPath,
    ]);
  });

  // MIDI → MusicXML（music21）→ case/score/；渲染由壳内 OSMD 完成
  ipcMain.handle('score:run', async (_e, caseDir, midiPath) => {
    if (!insideDir(caseDir, path.resolve(midiPath))) {
      return { ok: false, reason: 'MIDI 必须在世界目录内（case/midi/）' };
    }
    if (!fs.existsSync(midiPath)) return { ok: false, reason: 'MIDI 文件不存在' };
    const outdir = path.join(caseDir, 'score');
    fs.mkdirSync(outdir, { recursive: true });
    const base = path.basename(midiPath).replace(/\.(mid|midi)$/i, '');
    const out = path.join(outdir, `${base}.musicxml`);
    const res = await runLong('score', pyExe('score'), [
      path.join(TOOLS_ROOT, 'midi_to_musicxml.py'), midiPath, out,
    ]);
    return res.ok ? { ...res, musicxml: out } : res;
  });

  // 壳内曲谱渲染需要读 MusicXML 文本；只放行世界目录内文件
  ipcMain.handle('text:read', (_e, caseDir, filePath) => {
    if (!insideDir(caseDir, path.resolve(filePath))) throw new Error('路径越出世界目录');
    return fs.promises.readFile(filePath, 'utf8');
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1080,
    height: 700,
    minWidth: 900,
    minHeight: 560,
    backgroundColor: '#ffffff',
    autoHideMenuBar: true,
    icon: path.join(__dirname, '..', 'renderer', 'assets', 'moodify_icon_64.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  win.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
  win.on('closed', killAllTerminals);
  return win;
}

app.whenReady().then(() => {
  registerIpc();
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  killAllTerminals();
  if (process.platform !== 'darwin') app.quit();
});
