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
// Studio v0.2: the processing backend contract + the version layer. Both are plain
// Node modules with no Electron import, so they can be exercised headlessly.
const studioBackends = require('./backends');
const studio = require('./studio');
const pipeline = require('./pipeline');

const CASES_ROOT = process.env.MOODIFY_CASES_ROOT
  || path.join(os.homedir(), '.moodify', 'cases');
// 研究侧账本（T1）：暂存区，人类晋升动作才进文川院权威证据库
const RESEARCH_ROOT = path.join(os.homedir(), '.moodify', 'research');
const RESEARCH_PREFS = path.join(RESEARCH_ROOT, 'prefs.json');
const RESEARCH_JUDGMENTS = path.join(RESEARCH_ROOT, 'judgments.jsonl');
const RESEARCH_EVIDENCE = path.join(RESEARCH_ROOT, 'evidence.jsonl');
const RESEARCH_SCALES = ['明显更好', '略好', '听不出', '略差', '明显更差'];
const RESEARCH_ROLES = ['creator', 'listener', 'pro'];
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
  registerResearchIpc();
  registerCompareIpc();
  registerStudioV02Ipc();
  registerPipelineIpc();
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
      // T2 证据回流：检测完成自动落一条研究侧证据记录（不阻塞、不致命）
      try {
        if (reportPath) recordCaseEvidence(path.dirname(reportPath), 'detect', payload.status);
      } catch { /* evidence bookkeeping is best-effort; never blocks analysis */ }
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
      let mtime = 0;
      try { const st = fs.statSync(full); size = st.size; mtime = st.mtimeMs; } catch { /* raced deletion */ }
      return { name: e.name, path: full, size, mtime };
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
    const res = await runLong('midi', bpExe, [
      '--save-midi', '--model-serialization', 'onnx', outdir, audioPath,
    ]);
    if (res.ok) {
      // 回传刚生成的 MIDI，渲染层据此立即续跑曲谱转换（无需再扫目录猜）
      const base = path.basename(audioPath).replace(/\.[^.]+$/, '').toLowerCase();
      const mids = listCaseFiles(outdir, '', ['.mid', '.midi']);
      const mine = mids.find((m) => m.name.toLowerCase().startsWith(base)) || mids[0];
      return { ...res, midi: mine ? mine.path : null };
    }
    return res;
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

  // 修音渲染（后处理）：源 → finishing new(preset) 派生算子链 → finishing render 产 B(+evidence.json)。
  // 产物落 case/finishing/。这是研究账本「源(A) vs 修音产物(B)」中 B 的唯一来源；
  // 渲染成功后自动落一条带 delta 的研究侧证据（recordFinishingEvidence）。
  ipcMain.handle('finishing:run', async (_e, caseDir, preset) => {
    const src = resolveCaseSource(caseDir);
    if (!src) return { ok: false, reason: '未找到源音频（source_path.json 缺失或文件不存在）' };
    if (!['warm_vocal', 'clean_master', 'wide_space'].includes(preset)) {
      return { ok: false, reason: '未知修音预设：' + preset };
    }
    const fdir = path.join(caseDir, 'finishing');
    fs.mkdirSync(fdir, { recursive: true });
    const base = path.basename(src).replace(/\.[^.]+$/, '');
    const graph = path.join(fdir, `${base}__${preset}__graph.json`);
    // 1) 派生算子链（core，干净 .venv-core）
    const n1 = await runPython([
      '-m', 'moodify.release_cli', 'finishing', 'new',
      '--preset', preset, '--source', src, '--out', graph,
    ]);
    if (n1.code !== 0) return { ok: false, code: n1.code, reason: n1.stderr.trim().slice(-300) || 'finishing new failed' };
    // 2) 渲染 + 校验 + 导出（产 B wav + B.evidence.json）
    const n2 = await runPython([
      '-m', 'moodify.release_cli', 'finishing', 'render', graph, '--output-dir', fdir,
    ]);
    if (n2.code !== 0) return { ok: false, code: n2.code, reason: n2.stderr.trim().slice(-300) || 'finishing render failed' };
    // 3) 定位产物 B（*_mixgraph_*.wav）与其 evidence.json
    const files = listCaseFiles(caseDir, 'finishing', ['.wav', '.json']);
    const wav = files.find((f) => f.name.includes('_mixgraph_') && f.name.endsWith('.wav'));
    const ev = files.find((f) => f.name.includes('_mixgraph_') && f.name.endsWith('.evidence.json'));
    if (!wav) return { ok: false, reason: '渲染成功但未找到 B 产物 wav' };
    // 4) T2 证据回流：修音(后处理)证据带 delta，自动落研究账本（best-effort）
    let evidenceRec = null;
    try { evidenceRec = recordFinishingEvidence(caseDir, preset, ev ? ev.path : null); } catch { /* never blocks render */ }
    return { ok: true, preset, graph, output: wav.path, evidence: ev ? ev.path : null, evidenceRec };
  });
}

// ——— A/B 比较（Core CLI 权威 · 薄 GUI 支撑）———
//
// 比较产物与人类选择都由 `moodify compare`（Core CLI）生成与记录：壳不复制
// 比较逻辑、不算响度、不写选择。壳只做两件事——把 CLI 的 JSON 原样交给渲染层，
// 以及按产物里记录的 A/B 路径提供音频字节（同位置切换试听用）。
// 所有 caseDir 先经 resolveGuardedCase：必须落在 CASES_ROOT 内且确实是 case
// （case.json）——不新增任何可读写任意路径的 IPC 面。

function resolveGuardedCase(caseDir) {
  let resolved;
  try { resolved = path.resolve(String(caseDir || '')); } catch { return null; }
  if (!insideDir(path.resolve(CASES_ROOT), resolved)) return null;
  if (!fs.existsSync(path.join(resolved, 'case.json'))) return null;
  return resolved;
}

function runCompareCli(args) {
  return runPython(['-m', 'moodify.release_cli', 'compare', ...args]);
}

function readComparisonArtifact(caseDir) {
  try {
    return JSON.parse(fs.readFileSync(
      path.join(caseDir, 'compare', 'ab_comparison.json'), 'utf8'));
  } catch { return null; }
}

// A 的可信来源集合 = 本 case 自己记录的那些来源引用，规则与 Core CLI 的
// `compare prepare` 解析顺序一致（source_path.json → finishing 图的 source）。
// 试听接口只认这集合里的文件，渲染层递什么路径都读不到别的音频。
function caseSourceRefs(caseDir) {
  const refs = new Set();
  const add = (p, base) => {
    if (!p || typeof p !== 'string') return;
    const full = path.isAbsolute(p) ? p : path.join(base, p);
    try { if (fs.existsSync(full)) refs.add(fs.realpathSync(full)); } catch { /* raced */ }
  };
  try {
    add(JSON.parse(fs.readFileSync(path.join(caseDir, 'source_path.json'), 'utf8')).path);
  } catch { /* none */ }
  for (const g of listCaseFiles(caseDir, 'finishing', ['__graph.json'])) {
    const base = path.dirname(g.path);
    try { add(JSON.parse(fs.readFileSync(g.path, 'utf8')).source, base); } catch { /* skip */ }
  }
  return refs;
}

function registerCompareIpc() {
  // 读产物：`compare show` 是唯一读取实现（含 A/B 新鲜度），壳不自己算。
  ipcMain.handle('compare:read', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const res = await runCompareCli(['show', dir, '--cases-root', CASES_ROOT, '--json']);
    const payload = lastJsonLine(res.stdout);
    const failure = lastJsonLine(res.stderr);
    if (!payload || !payload.artifact) {
      return { ok: false, code: res.code,
               reason: (failure && failure.code) || 'COMPARISON_UNREADABLE', payload: failure };
    }
    return { ok: true, code: res.code, payload, artifact: payload.artifact,
             freshness: payload.freshness };
  });

  // 准备/刷新产物：A 只取该 case 自己记录的源（source_path.json），不接任意路径。
  ipcMain.handle('compare:prepare', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const args = ['prepare', dir, '--cases-root', CASES_ROOT, '--json'];
    const src = resolveCaseSource(dir);
    if (src) args.push('--a', src);
    const res = await runCompareCli(args);
    const payload = lastJsonLine(res.stdout);
    const failure = lastJsonLine(res.stderr);
    if (res.code === 0 && payload) return { ok: true, code: res.code, payload };
    return { ok: false, code: res.code,
             reason: (failure && failure.code) || 'PREPARE_FAILED',
             payload: payload || failure };
  });

  // 记录人的二选一：CLI 先校验产物未过期（A/B sha256），再 append 到世界账本。
  // requestId 由调用方对「同一次待决选择」保持不变：重试被 CLI 拒绝而不是写入两条。
  ipcMain.handle('compare:choose', async (_e, caseDir, keep, role, requestId) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    if (keep !== 'A' && keep !== 'B') return { ok: false, reason: 'BAD_KEEP' };
    if (!['creator', 'listener', 'pro'].includes(role)) return { ok: false, reason: 'BAD_ROLE' };
    const args = ['choose', dir, '--keep', keep, '--role', role,
                  '--cases-root', CASES_ROOT, '--json'];
    if (typeof requestId === 'string' && requestId) args.push('--request-id', requestId);
    const res = await runCompareCli(args);
    const payload = lastJsonLine(res.stdout);
    const failure = lastJsonLine(res.stderr);
    if (res.code === 0 && payload && payload.status === 'recorded') {
      return { ok: true, code: res.code, payload };
    }
    return { ok: false, code: res.code,
             reason: (failure && failure.code) || 'RECORD_FAILED',
             payload: failure || payload };
  });

  // 供试听的音频字节：只服务产物里记录的那两个文件（A 在世界外是设计如此）。
  // 产物路径必须落在世界内；A 只接受「本 case 自己记录的源」——渲染层递什么
  // 路径都读不到别的文件，不存在任意路径读取面。
  ipcMain.handle('compare:audio', async (_e, caseDir, side) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) throw new Error('INVALID_CASE_DIR');
    if (side !== 'A' && side !== 'B') throw new Error('BAD_SIDE');
    const artifact = readComparisonArtifact(dir);
    const block = artifact && artifact[side === 'A' ? 'a' : 'b'];
    const file = block && block.path;
    if (!file || !fs.existsSync(file)) throw new Error('AUDIO_NOT_AVAILABLE');
    const real = fs.realpathSync(file);
    if (side === 'B') {
      if (!insideDir(fs.realpathSync(dir), real)) throw new Error('AUDIO_OUTSIDE_CASE');
    } else if (!caseSourceRefs(dir).has(real)) {
      throw new Error('A_NOT_CASE_SOURCE');
    }
    return fs.promises.readFile(real);
  });
}

// ——— 研究侧账本（T1 感知通道）———
// 人类判断显式落账；不自动抓行为；暂存 ~/.moodify/research/，
// 晋升到文川院权威证据库是人类动作。量表与角色集合在 main 侧冻结。

function researchCaseSummary(caseDir) {
  try {
    const src = JSON.parse(fs.readFileSync(path.join(caseDir, 'source_path.json'), 'utf8'));
    return path.basename(src.path || '');
  } catch { return ''; }
}

// ——— T2 证据回流助手（模块级，供 registerResearchIpc 与 analysis:run 复用）———
// 只读 case 的核心产物（measurements.json / case.json / source_path.json），
// 从核心测量值抽五项净增益分项，落研究侧账本。不重算、不改核心产物（One Core）。

// 把 case 的 measurements.json 读成 name->value 映射
function loadMeasurementsMap(caseDir) {
  const map = {};
  try {
    const items = JSON.parse(fs.readFileSync(path.join(caseDir, 'measurements.json'), 'utf8'));
    for (const it of Array.isArray(items) ? items : []) {
      if (it && typeof it.name === 'string') map[it.name] = it.value;
    }
  } catch { /* measurements missing -> empty */ }
  return map;
}

function pick(map, keys) {
  const out = {};
  for (const k of keys) if (k in map) out[k] = map[k];
  return out;
}

// 读 case.json 的源 sha256 / 作品名 / 权威状态
function caseMeta(caseDir) {
  const meta = { workName: '', sourceSha256: null, authorityState: null, caseId: path.basename(caseDir) };
  try {
    const cj = JSON.parse(fs.readFileSync(path.join(caseDir, 'case.json'), 'utf8'));
    meta.caseId = cj.case_id || meta.caseId;
    meta.authorityState = cj.authority_state || null;
    if (typeof cj.source_id === 'string' && cj.source_id.startsWith('sha256:')) meta.sourceSha256 = cj.source_id.slice(7);
  } catch { /* none */ }
  try {
    const sp = JSON.parse(fs.readFileSync(path.join(caseDir, 'source_path.json'), 'utf8'));
    if (sp.path) meta.workName = path.basename(sp.path);
  } catch { /* none */ }
  return meta;
}

// 把一个 case 的测量快照落成研究侧证据记录（append ~/.moodify/research/evidence.jsonl）。
// 五项分项：单版本出绝对值/快照，delta 槽位留 null；不合并成任何分数。
// stage='detect'（默认，检测阶段）或 'render'（W5 渲染接入后填 delta）。
function recordCaseEvidence(caseDir, stage, sourceStatus) {
  fs.mkdirSync(RESEARCH_ROOT, { recursive: true });
  const m = loadMeasurementsMap(caseDir);
  const meta = caseMeta(caseDir);
  const entry = {
    evidence_id: `EV-${new Date().toISOString().replace(/[:.]/g, '').replace('T', '-')}`,
    created_at: new Date().toISOString(),
    stage,
    case_id: meta.caseId,
    work_name: meta.workName || null,
    source_sha256: meta.sourceSha256,
    technical_gate: meta.authorityState,
    source_status: sourceStatus || null,
    net_gain_components: {
      loudness_delta: {
        absolute: pick(m, ['integrated_lufs', 'loudness_range_lu', 'rms_dbfs']),
        delta: null,
      },
      identity_delta: {
        snapshot: pick(m, ['spectral_centroid_hz', 'spectral_flatness', 'spectral_rolloff_85_hz', 'stereo_width_proxy', 'mid_energy_ratio']),
        delta: null,
      },
      artifact_risk: {
        absolute: pick(m, ['clipping_sample_ratio', 'near_clipping_sample_count', 'dc_offset_left', 'dc_offset_right', 'estimated_noise_floor_dbfs', 'phase_risk_ratio', 'negative_correlation_ratio']),
        delta: null,
      },
      duration_check: {
        absolute: pick(m, ['duration', 'sample_rate', 'channels']),
        passed: null,
        delta: null,
      },
      complexity_cost: {
        operator_count: stage === 'render' ? null : 0,
        note: stage === 'render' ? 'pending W5 operator-chain wiring' : 'detection stage: no intervention',
      },
    },
    provenance: { method: 'auditory_scan', method_version: 'MFY-WSE-SCAN-PROFILE-001', source_case: caseDir },
    evidence_status: 'M1_measurement',
    research: { loudness_matched: null, blind_review: 'pending' },
  };
  fs.appendFileSync(RESEARCH_EVIDENCE, JSON.stringify(entry) + '\n');
  const count = fs.readFileSync(RESEARCH_EVIDENCE, 'utf8').trim().split('\n').filter(Boolean).length;
  return { ok: true, evidenceId: entry.evidence_id, stage, caseId: entry.case_id, count };
}

// 修音(后处理)证据回流：读 core finishing 产的 .evidence.json（verification.before/after/
// deltas/invariants/peak_gate + nodes 算子链），落一条 stage='render' 的研究记录，
// 把 T2 五项分项的 delta 槽位真正填上（PRINCIPLE-001 净增益：改了之后比之前好多少）。
function recordFinishingEvidence(caseDir, preset, evidenceJsonPath) {
  fs.mkdirSync(RESEARCH_ROOT, { recursive: true });
  const meta = caseMeta(caseDir);
  let ev = null;
  if (evidenceJsonPath) { try { ev = JSON.parse(fs.readFileSync(evidenceJsonPath, 'utf8')); } catch { /* none */ } }
  const v = (ev && ev.verification) || {};
  const before = v.before || {};
  const after = v.after || {};
  const deltas = v.deltas || {};
  const invariants = v.invariants || {};
  const peakGate = v.peak_gate || {};
  const nodes = (ev && Array.isArray(ev.nodes)) ? ev.nodes : [];
  const enabledNodes = nodes.filter((n) => n && n.enabled !== false);
  const entry = {
    evidence_id: `EV-${new Date().toISOString().replace(/[:.]/g, '').replace('T', '-')}`,
    created_at: new Date().toISOString(),
    stage: 'render',
    preset,
    case_id: meta.caseId,
    work_name: meta.workName || null,
    source_sha256: meta.sourceSha256,
    technical_gate: meta.authorityState,
    net_gain_components: {
      loudness_delta: {
        absolute: { integrated_lufs: after.integrated_loudness_lufs ?? null },
        before: before.integrated_loudness_lufs ?? null,
        delta: deltas.loudness_lu ?? null,
      },
      identity_delta: {
        snapshot: { crest_factor: after.crest_factor ?? null, stereo_correlation: after.stereo_correlation ?? null },
        delta: deltas.crest_factor ?? null,
      },
      artifact_risk: {
        absolute: { sample_peak_dbfs: after.sample_peak_dbfs ?? null, finite: after.finite ?? null },
        peak_gate: { limit: peakGate.limit ?? null, measured: peakGate.measured ?? null, passed: peakGate.passed ?? null },
        delta: deltas.sample_peak_db ?? null,
      },
      duration_check: {
        absolute: { duration_s: after.duration_s ?? null, sample_rate: after.sample_rate ?? null },
        passed: invariants.length_preserved ?? null,
      },
      complexity_cost: {
        operator_count: enabledNodes.length,
        operator_chain: enabledNodes.map((n) => n.type || n.node_type || null),
      },
    },
    provenance: {
      method: 'finishing_render',
      method_version: 'MFY-MIX-GRAPH/0.1',
      graph_digest: (ev && ev.graph_digest_sha256) || null,
      output_sha256: (ev && ev.output && ev.output.sha256) || null,
      source_case: caseDir,
      evidence_source: evidenceJsonPath || null,
    },
    evidence_status: 'M2_rendering',
    research: { loudness_matched: null, blind_review: 'pending' },
  };
  fs.appendFileSync(RESEARCH_EVIDENCE, JSON.stringify(entry) + '\n');
  const count = fs.readFileSync(RESEARCH_EVIDENCE, 'utf8').trim().split('\n').filter(Boolean).length;
  return { ok: true, evidenceId: entry.evidence_id, stage: 'render', preset, operator_count: enabledNodes.length, count };
}

// ——— Studio v0.2：选目标 → 一键让 AI 处理 → 试听选择 → 导出 ———
//
// 产品定义（人类 2026-10-03，APPROVED）：把歌丢进去，AI 自动试后处理，人只负责听和选。
// 本节只做「接线」，不复制任何能力：
//   后处理 = Core 的 `protocol process` 作业（内部是 v01_pipeline.process_audio）
//   导出   = Core 的 `finishing export`（内部是 export_delivery）
//   壳不实现 DSP、不算响度、不写音频字节，也不替用户做选择。
// 所有 caseDir 先经 resolveGuardedCase：必须落在 CASES_ROOT 内且确实是 case。

function registerStudioV02Ipc() {
  const localBackend = studioBackends.getBackend('local');

  // 目标清单由后端层提供，前端不硬编码 —— 新增预设时不会两边漂移。
  ipcMain.handle('studio:targets', async () => ({
    ok: true,
    defaultTarget: localBackend.DEFAULT_TARGET,
    defaultMode: studioBackends.DEFAULT_MODE,
    backends: studioBackends.describeBackends(),
    targets: localBackend.TARGETS.map((id) => ({
      id, label: studio.targetLabel(id), available: true,
    })),
    // 产品书写了、但 Core 做不到的目标：显式列出并标记不可用。
    // 不映射到别的预设 —— 按钮承诺什么就必须做什么。
    planned: studio.PLANNED_TARGETS.map((p) => ({
      id: p.id, label: studio.targetLabel(p.id), available: false, reason: p.reason,
    })),
  }));

  // 版本清单 = 原版（指向 case 源，不复制）+ 每次 AI 尝试。附上人类已做的选择。
  ipcMain.handle('studio:versions', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    return {
      ok: true,
      source: resolveCaseSource(dir),
      versions: studio.listVersions(dir, resolveCaseSource(dir)),
      selection: studio.readSelection(dir),
      meta: studio.readMeta(dir),
    };
  });

  // 「让 AI 处理」。每次调用落在**新的** attempt 目录：既满足 Core 的
  // 「拒绝覆盖已存在输出」守卫，也满足产品书 2.2「再试一次不得静默覆盖已确认版本」。
  ipcMain.handle('studio:process', async (_e, caseDir, target, mode) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const src = resolveCaseSource(dir);
    if (!src) return { ok: false, reason: '未找到源音频（source_path.json 缺失或文件不存在）' };

    let backend;
    try { backend = studioBackends.getBackend(mode || studioBackends.DEFAULT_MODE); }
    catch (err) { return { ok: false, reason: err.message }; }

    studio.ensureDirs(dir);
    const attemptId = studio.newAttemptId();
    const versionDir = studio.createAttemptDir(dir, attemptId);

    const result = await backend.process(
      { sourcePath: src, target, versionDir, attemptId },
      { runPython, lastJsonLine },
    );
    // 失败时清掉空壳目录，避免版本列表里冒出没有音频的条目
    if (!result.ok) {
      try { fs.rmSync(versionDir, { recursive: true, force: true }); } catch { /* best effort */ }
      return result;
    }
    studio.writeMeta(dir, { last_target: target, last_mode: backend.kind });
    return {
      ok: true,
      attemptId,
      output: result.output,
      // 产品书 1.3：导出前状态一律为「待人确认」。这里原样回传 Core 的状态，
      // 前端不得把它显示成「已验证」。
      status: result.evidence.status,
      reviewRequired: result.evidence.review_required === true,
      evidence: result.evidence,
      versions: studio.listVersions(dir, src),
    };
  });

  ipcMain.handle('studio:evidence', async (_e, caseDir, versionId) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const evidence = studio.readEvidence(dir, versionId);
    return evidence ? { ok: true, evidence } : { ok: false, reason: 'NO_EVIDENCE' };
  });

  // 人类的选择：只有显式动作才会写入，永不自动。
  ipcMain.handle('studio:select', async (_e, caseDir, versionId, note) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    if (!versionId) return { ok: false, reason: 'NO_VERSION' };
    return { ok: true, selection: studio.writeSelection(dir, { versionId, note }) };
  });

  // 试听某个版本。沿用 compare:audio 的守卫思路：音频必须落在本 case 内
  // （原版是例外——它是 case 自己记录的源文件）。
  ipcMain.handle('studio:audio', async (_e, caseDir, versionId) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) throw new Error('INVALID_CASE_DIR');
    let file;
    if (versionId === 'original') {
      file = resolveCaseSource(dir);
    } else {
      const v = studio.listVersions(dir, null).find((x) => x.id === versionId);
      file = v && v.audioPath;
    }
    if (!file || !fs.existsSync(file)) throw new Error('AUDIO_NOT_AVAILABLE');
    const real = fs.realpathSync(file);
    if (versionId !== 'original' && !insideDir(fs.realpathSync(dir), real)) {
      throw new Error('AUDIO_OUTSIDE_CASE');
    }
    return fs.promises.readFile(real);
  });

  // 导出：复用 Core 的 delivery 编码（export_delivery），再把结果复制到用户选定路径。
  // 导出是**显式动作**：这里是唯一把音频写出 case 之外的地方。
  ipcMain.handle('studio:export', async (event, caseDir, versionId) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };

    let audioPath;
    if (versionId === 'original') {
      audioPath = resolveCaseSource(dir);
    } else {
      const v = studio.listVersions(dir, null).find((x) => x.id === versionId);
      audioPath = v && v.audioPath;
    }
    if (!audioPath || !fs.existsSync(audioPath)) return { ok: false, reason: 'AUDIO_NOT_AVAILABLE' };

    const outDir = studio.exportDir(dir);
    fs.mkdirSync(outDir, { recursive: true });
    const res = await runPython([
      '-m', 'moodify.release_cli', 'finishing', 'export',
      '--audio', audioPath, '--output-dir', outDir,
    ]);
    if (res.code !== 0) {
      return { ok: false, code: res.code, reason: res.stderr.trim().slice(-300) || '导出失败' };
    }
    const exported = lastJsonLine(res.stdout);
    if (!exported || !exported.output || !fs.existsSync(exported.output)) {
      return { ok: false, reason: '导出命令成功但未找到产物' };
    }

    const suggested = path.basename(exported.output);
    const win = BrowserWindow.fromWebContents(event.sender);
    const picked = await dialog.showSaveDialog(win, {
      title: '导出音频',
      defaultPath: suggested,
      filters: [{ name: 'WAV 音频', extensions: ['wav'] }],
    });
    if (picked.canceled || !picked.filePath) {
      // 用户取消：case 内的导出产物保留（它是记录），但不写到用户路径
      return { ok: false, canceled: true, reason: '已取消导出' };
    }
    try {
      fs.copyFileSync(exported.output, picked.filePath);
    } catch (err) {
      return { ok: false, reason: '写入目标路径失败：' + err.message };
    }

    // 导出记录：写进 case，供日后回答「导出的是哪一版」
    const record = {
      schema: 'moodify.studio.export/0.1',
      version_id: versionId,
      source_audio: audioPath,
      case_output: exported.output,
      user_path: picked.filePath,
      output_sha256: exported.output_sha256 || null,
      applied_peak_trim_db: exported.applied_peak_trim_db,
      exported_at: new Date().toISOString(),
    };
    try {
      fs.writeFileSync(path.join(outDir, 'export_record.json'), JSON.stringify(record, null, 2), 'utf8');
    } catch { /* record is best-effort; the audio is already written */ }

    return { ok: true, path: picked.filePath, sha256: exported.output_sha256 || null, record };
  });
}

// ——— 生产流程（TASK 002A）：检测 → 问题 → 分轨 → 结构 → 方案 → 成品 ———
//
// 产品原则：**先理解，再分解，最后处理**。分析后立刻处理立体声母带是错的。
// 本节只暴露「流程状态 + 诊断产物 + context 包」，不含任何音频算法：
//   阶段由磁盘产物**推导**（见 src/pipeline.js），不是人手推进，也不会谎报。
//   诊断严格是 Core report.json 的投影，每条 issue 带 evidence 指针指回原 finding。

function registerPipelineIpc() {
  // 流程快照：当前阶段 + 各阶段事实 + 门禁。UI 靠它决定哪些阶段可进入。
  ipcMain.handle('pipeline:snapshot', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const snap = pipeline.snapshot(dir);
    // 顺手记一笔（记录用，不是权威；读的时候永远重新推导）
    let record = null;
    try { record = pipeline.recordStage(dir); } catch { /* best effort */ }
    return {
      ok: true,
      stage: snap.stage,
      gates: snap.gates,
      facts: snap.facts,
      record,
      stages: pipeline.STAGES,
    };
  });

  // 生成/刷新诊断产物。纯投影，不新增判断。
  ipcMain.handle('pipeline:diagnose', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const diagnosis = pipeline.buildDiagnosis(dir);
    if (!diagnosis) return { ok: false, reason: 'NO_REPORT' };
    pipeline.writeDiagnosis(dir, diagnosis);
    return {
      ok: true,
      diagnosis,
      stage: pipeline.snapshot(dir).stage,
    };
  });

  ipcMain.handle('pipeline:diagnosis', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const d = pipeline.readDiagnosis(dir);
    return d ? { ok: true, diagnosis: d } : { ok: false, reason: 'NO_DIAGNOSIS' };
  });

  // 人类批注 / 声明该保护什么。「该保护什么」是听觉判断，只能由人写。
  ipcMain.handle('pipeline:note', async (_e, caseDir, note, preserve) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const next = pipeline.addHumanNote(dir, { note, preserve });
    return next ? { ok: true, diagnosis: next } : { ok: false, reason: 'NO_DIAGNOSIS' };
  });

  // 构建 context 包（§9）：只引用不复制，且只写真实存在的路径。
  ipcMain.handle('pipeline:context', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const prepared = pipeline.preparePlan(dir);
    if (!prepared) return { ok: false, reason: 'NEED_ANALYZE_AND_DIAGNOSE' };
    return {
      ok: true,
      context: prepared.context,
      path: prepared.contextFile,
      plan: prepared.plan,
      planPath: prepared.planFile,
      stage: pipeline.snapshot(dir).stage,
    };
  });

  ipcMain.handle('pipeline:readContext', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const ctx = pipeline.readJsonSafe(path.join(dir, 'studio', 'context.json'));
    return ctx ? { ok: true, context: ctx } : { ok: false, reason: 'NO_CONTEXT' };
  });

  // 显式选择「快速完成（仅立体声）」。
  // 这是**人类决定**，不是一个 UI 开关：深度完成需要 SEPARATED + STRUCTURED；
  // 跳过它必须由人主动选择，并留下可追溯的记录（finish_mode.json）。
  // 绝不自动解锁——否则快捷路径会变成默认路径。
  ipcMain.handle('pipeline:setFinishMode', async (_e, caseDir, mode) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    if (mode !== null && mode !== 'QUICK_STEREO_ONLY') {
      return { ok: false, reason: 'BAD_MODE' };
    }
    const snap = pipeline.snapshot(dir);
    if (mode === 'QUICK_STEREO_ONLY' && !snap.gates.facts.readyForPlan) {
      // 连分析与诊断都没完成时，连「快速」都谈不上
      return { ok: false, reason: 'NEED_ANALYZE_AND_DIAGNOSE' };
    }
    const record = pipeline.recordFinishMode(dir, mode, '用户显式选择');
    return { ok: true, finishMode: record, gates: pipeline.snapshot(dir).gates };
  });
}

function registerResearchIpc() {
  // 世界侧 A/B 对照（修音语义）：A=源（修音前），B=修音产物（finishing 渲染出的 *_mixgraph_*.wav）。
  // 不再开放"随便选两个文件"——真 A/B 是固定的 [源 vs 修音产物]。
  // B 未渲染时 renderedB=null，UI 据此提示"先修音渲染"。
  ipcMain.handle('research:case', (_e, caseDir) => {
    let sourceName = '';
    let sourcePath = null;
    let sourceSha256 = null;
    let renderedB = null; // 修音产物 wav（A/B 的 B）
    let renderedBSha = null;
    let preset = null;
    try {
      const sp = JSON.parse(fs.readFileSync(path.join(caseDir, 'source_path.json'), 'utf8'));
      sourceName = path.basename(sp.path || '');
      sourcePath = sp.path || null;
    } catch { /* none */ }
    try {
      const cj = JSON.parse(fs.readFileSync(path.join(caseDir, 'case.json'), 'utf8'));
      if (typeof cj.source_id === 'string' && cj.source_id.startsWith('sha256:')) sourceSha256 = cj.source_id.slice(7);
    } catch { /* none */ }
    // 找 case/finishing/ 里最新的 *_mixgraph_*.wav + 其 .evidence.json（可判 preset）
    try {
      const fdir = path.join(caseDir, 'finishing');
      const files = listCaseFiles(caseDir, 'finishing', ['.wav', '.json']);
      const wavs = files.filter((f) => f.name.includes('_mixgraph_') && f.name.endsWith('.wav'))
        .sort((a, b) => b.mtime - a.mtime);
      if (wavs.length) {
        renderedB = wavs[0].path;
        const m = wavs[0].name.match(/_(clean_master|warm_vocal|wide_space)/);
        if (m) preset = m[1];
        const evs = files.filter((f) => f.name.includes('_mixgraph_') && f.name.endsWith('.evidence.json'))
          .sort((a, b) => b.mtime - a.mtime);
        if (evs.length) {
          try { renderedBSha = JSON.parse(fs.readFileSync(evs[0].path, 'utf8')).output && JSON.parse(fs.readFileSync(evs[0].path, 'utf8')).output.sha256; } catch { /* none */ }
        }
      }
    } catch { /* no finishing dir yet */ }
    return { sourceName, sourcePath, sourceSha256, renderedB, renderedBSha, preset };
  });

  ipcMain.handle('research:prefs', (_e, patch) => {
    fs.mkdirSync(RESEARCH_ROOT, { recursive: true });
    let prefs = {};
    try { prefs = JSON.parse(fs.readFileSync(RESEARCH_PREFS, 'utf8')); } catch { /* first write */ }
    if (patch && typeof patch === 'object') {
      if ('researchMode' in patch) prefs.researchMode = patch.researchMode === true;
      if ('role' in patch && RESEARCH_ROLES.includes(patch.role)) prefs.role = patch.role;
    }
    prefs.updatedAt = new Date().toISOString();
    fs.writeFileSync(RESEARCH_PREFS, JSON.stringify(prefs, null, 2));
    return {
      researchMode: prefs.researchMode === true,
      role: RESEARCH_ROLES.includes(prefs.role) ? prefs.role : 'listener',
      choices: ['A', 'B'], // 留源(A) / 留修音产物(B)
      roles: RESEARCH_ROLES,
      count: fs.existsSync(RESEARCH_JUDGMENTS)
        ? fs.readFileSync(RESEARCH_JUDGMENTS, 'utf8').trim().split('\n').filter(Boolean).length
        : 0,
    };
  });

  // 判断 = 二选一：留 A（源）还是留 B（修音产物）。记录含响度匹配状态 + 评判角色。
  ipcMain.handle('research:judgment', (_e, record) => {
    if (!record || typeof record !== 'object') return { ok: false, reason: '记录无效' };
    if (record.choice !== 'A' && record.choice !== 'B') return { ok: false, reason: '必须是二选一：A 或 B' };
    fs.mkdirSync(RESEARCH_ROOT, { recursive: true });
    const prefs = {};
    try { prefs = JSON.parse(fs.readFileSync(RESEARCH_PREFS, 'utf8')); } catch { /* absent */ }
    const entry = {
      judgment_id: `J-${new Date().toISOString().replace(/[:.]/g, '').replace('T', '-')}`,
      created_at: new Date().toISOString(),
      case_id: record.caseId || null,
      work_name: record.workName || null,
      source_sha256: record.sourceSha256 || null,
      pair: { a: 'source', b: 'rendered' },
      versions: { a: record.versionA || 'source', b: (record.versionB || 'rendered') + (record.preset ? `(${record.preset})` : '') },
      preset: record.preset || null,
      // 本次判断实际用的匹配状态（来自 Core 产物），不是界面勾选，也不是偏好值
      loudness_matched: record.loudnessMatched === true,
      choice: record.choice, // 'A' = 留源，'B' = 留修音产物
      kept: record.choice === 'A' ? 'source' : 'rendered',
      // 角色以本次判断携带的为准，偏好只作兜底：两份账本不会记成不同角色
      judge_role: RESEARCH_ROLES.includes(record.role) ? record.role
        : (RESEARCH_ROLES.includes(prefs.role) ? prefs.role : 'listener'),
      notes: typeof record.notes === 'string' ? record.notes.slice(0, 500) : '',
      evidence_status: 'M3_candidate',
      research_mode: prefs.researchMode === true,
    };
    fs.appendFileSync(RESEARCH_JUDGMENTS, JSON.stringify(entry) + '\n');
    return { ok: true, judgmentId: entry.judgment_id,
      count: fs.readFileSync(RESEARCH_JUDGMENTS, 'utf8').trim().split('\n').filter(Boolean).length };
  });

  // T2 证据回流：把世界（case）的测量快照落成研究侧证据记录。
  // 显式调用（shell 渲染完成后触发）或自动（analysis:run 成功钩子）。
  ipcMain.handle('evidence:record', (_e, caseDir, stage, sourceStatus) => {
    if (!caseDir || !fs.existsSync(path.join(caseDir, 'measurements.json'))) {
      return { ok: false, reason: '该世界没有 measurements.json' };
    }
    return recordCaseEvidence(caseDir, stage || 'detect', sourceStatus);
  });
  ipcMain.handle('evidence:count', () => {
    if (!fs.existsSync(RESEARCH_EVIDENCE)) return 0;
    return fs.readFileSync(RESEARCH_EVIDENCE, 'utf8').trim().split('\n').filter(Boolean).length;
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
