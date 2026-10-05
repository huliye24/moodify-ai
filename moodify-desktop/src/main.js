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
// V4 流程层：阶段推导与门禁（pipeline）、修音对与三出口账本（tuning）、三方对齐表（recheck）。
// 三者都是纯 Node 模块，无 Electron 依赖，可 headless 测试。
//
// RETIRED 2026-10-04：`./backends` 与 `./studio`（Studio v0.2 的预设版本层）不再被本文件引用。
// 三预设作为产品面已退场；两个文件仍留在磁盘上供审阅，待人类确认后删除。
const tuning = require('./tuning');
const recheck = require('./recheck');
const pipeline = require('./pipeline');
// 完成会话编排器（纯投影 + 重入保护）。阶段权威仍在 pipeline.js，它只是把进度折叠给用户看。
const session = require('./session');
// 调度循环本体（与 Electron 无关，步骤函数由本文件注入）—— 这样它能被 headless 测到。
const { createOrchestrator } = require('./orchestrator');

const CASES_ROOT = process.env.MOODIFY_CASES_ROOT
  || path.join(os.homedir(), '.moodify', 'cases');
// 研究侧账本（T1）：暂存区，人类晋升动作才进文川院权威证据库
const RESEARCH_ROOT = path.join(os.homedir(), '.moodify', 'research');
const RESEARCH_PREFS = path.join(RESEARCH_ROOT, 'prefs.json');
const RESEARCH_JUDGMENTS = path.join(RESEARCH_ROOT, 'judgments.jsonl');
const RESEARCH_EVIDENCE = path.join(RESEARCH_ROOT, 'evidence.jsonl');
const RESEARCH_SCALES = ['明显更好', '略好', '听不出', '略差', '明显更差'];
const RESEARCH_ROLES = ['creator', 'listener', 'pro'];
const BUNDLED_RUNTIME = app.isPackaged ? path.join(process.resourcesPath, 'runtime') : null;
const PYTHON = process.env.MOODIFY_PYTHON
  || (BUNDLED_RUNTIME ? path.join(BUNDLED_RUNTIME, 'python', 'python.exe') : 'python');
const AUDIO_FILTERS = [
  { name: '音频', extensions: ['flac', 'wav', 'mp3', 'm4a', 'aac', 'ogg', 'aiff', 'aif'] },
  { name: '所有文件', extensions: ['*'] },
];

// ——— Application updates: user chooses; Studio never replaces itself silently. ———

let desktopUpdater = null;
let updaterStarted = false;
function currentAppVersion() {
  try { return typeof app.getVersion === 'function' ? app.getVersion() : '1.0.1-rc.1'; } catch { return '1.0.1-rc.1'; }
}
let updateState = {
  supported: false,
  status: 'idle',
  currentVersion: currentAppVersion(),
  version: null,
  percent: 0,
  message: '',
  // 生效的更新源。让「当前连的是哪个 feed」成为界面可读的事实——
  // 差分升级测试时会指向本机 server，正常情况指向 https://rongjingmusic.com/...
  feed: null,
  feedOverridden: false,
};

function updatePreferencesPath() {
  return path.join(app.getPath('userData'), 'update-preferences.json');
}

function readUpdatePreferences() {
  try { return JSON.parse(fs.readFileSync(updatePreferencesPath(), 'utf8')); } catch { return {}; }
}

function writeUpdatePreferences(patch) {
  const next = { ...readUpdatePreferences(), ...patch, updatedAt: new Date().toISOString() };
  fs.mkdirSync(path.dirname(updatePreferencesPath()), { recursive: true });
  fs.writeFileSync(updatePreferencesPath(), JSON.stringify(next, null, 2), 'utf8');
  return next;
}

function publishUpdateState(patch = {}) {
  updateState = { ...updateState, ...patch, currentVersion: currentAppVersion() };
  for (const win of BrowserWindow.getAllWindows()) {
    if (!win.isDestroyed()) win.webContents.send('update:status', updateState);
  }
  return updateState;
}

function setupAutoUpdater() {
  if (updaterStarted) return desktopUpdater;
  updaterStarted = true;
  if (!app.isPackaged || process.platform !== 'win32') {
    publishUpdateState({ supported: false, status: 'dev', message: '开发模式不检查更新。' });
    return null;
  }
  try {
    desktopUpdater = require('electron-updater').autoUpdater;
    desktopUpdater.autoDownload = false;
    desktopUpdater.autoInstallOnAppQuit = false;
    desktopUpdater.allowPrerelease = true;

    // 仅供本地差分升级测试使用的 feed 覆盖。
    //
    // 为什么需要它：验证「发现更新 → 下载 → 重启安装 → 版本真的变了」这条闭环，
    // 必须在真实安装的旧版上跑。若为此把假版本推到生产 feed，等于让所有已安装客户端
    // 都看到一个不存在的版本——不可接受。所以走环境变量，**默认严格使用生产 URL**。
    //
    // 边界：环境变量由本机启动者提供，远端 feed 无法改写它，因此不构成
    // 「被投递的 feed 自称来自别处」这一类风险。仍然把生效的 URL 写进状态里，
    // 让「我现在不是连生产」这件事在界面上可见，而不是只在日志里。
    const feedOverride = (process.env.MOODIFY_UPDATE_URL || '').trim();
    if (feedOverride) {
      desktopUpdater.setFeedURL({ provider: 'generic', url: feedOverride, channel: 'latest' });
    }
    const effectiveFeed = feedOverride || 'https://rongjingmusic.com/downloads/studio/windows/';
    updateState.feed = effectiveFeed;
    updateState.feedOverridden = Boolean(feedOverride);

    desktopUpdater.on('checking-for-update', () => publishUpdateState({ supported: true, status: 'checking', message: '正在检查更新…' }));
    desktopUpdater.on('update-available', (info) => {
      const skipped = readUpdatePreferences().skippedVersion;
      publishUpdateState({
        supported: true,
        status: skipped === info.version ? 'skipped' : 'available',
        version: info.version,
        percent: 0,
        message: skipped === info.version ? `已跳过 ${info.version}` : `发现新版本 ${info.version}`,
      });
    });
    desktopUpdater.on('update-not-available', () => publishUpdateState({ supported: true, status: 'current', version: null, percent: 0, message: '已是最新版本。' }));
    desktopUpdater.on('download-progress', (progress) => publishUpdateState({ supported: true, status: 'downloading', percent: Math.round(progress.percent || 0), message: `正在下载更新 ${Math.round(progress.percent || 0)}%` }));
    desktopUpdater.on('update-downloaded', (info) => publishUpdateState({ supported: true, status: 'ready', version: info.version, percent: 100, message: `版本 ${info.version} 已准备好。` }));
    desktopUpdater.on('error', (error) => publishUpdateState({ supported: true, status: 'error', message: `更新失败：${error && error.message ? error.message : String(error)}` }));
    publishUpdateState({ supported: true, status: 'idle', message: '' });
  } catch (error) {
    publishUpdateState({ supported: false, status: 'error', message: `更新组件不可用：${error.message}` });
  }
  return desktopUpdater;
}

async function checkForDesktopUpdate(manual = false) {
  const updater = setupAutoUpdater();
  if (!updater) return publishUpdateState(manual ? { message: '当前环境不支持自动更新。' } : {});
  try {
    await updater.checkForUpdates();
  } catch (error) {
    publishUpdateState({ status: 'error', message: `检查更新失败：${error.message}` });
  }
  return updateState;
}

function registerUpdateIpc() {
  ipcMain.handle('update:status', () => ({ ...updateState }));
  ipcMain.handle('update:check', async () => checkForDesktopUpdate(true));
  ipcMain.handle('update:action', async (_event, action) => {
    const updater = setupAutoUpdater();
    if (action === 'later') return publishUpdateState({ status: 'later', message: '已保留当前版本，稍后可再次更新。' });
    if (action === 'skip') {
      if (updateState.version) writeUpdatePreferences({ skippedVersion: updateState.version });
      return publishUpdateState({ status: 'skipped', message: `已跳过 ${updateState.version || '此版本'}。` });
    }
    if (!updater) return publishUpdateState({ status: 'error', message: '当前环境不支持自动更新。' });
    if (action === 'download') {
      writeUpdatePreferences({ skippedVersion: null });
      publishUpdateState({ status: 'downloading', percent: 0, message: '正在下载更新…' });
      try { await updater.downloadUpdate(); } catch (error) { publishUpdateState({ status: 'error', message: `下载更新失败：${error.message}` }); }
      return updateState;
    }
    if (action === 'install' && updateState.status === 'ready') {
      setImmediate(() => updater.quitAndInstall(false, true));
      return publishUpdateState({ status: 'installing', message: '正在重启并安装更新…' });
    }
    return publishUpdateState({ status: 'error', message: '无法执行这个更新操作。' });
  });
}

function pythonEnv() {
  const env = { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' };
  if (BUNDLED_RUNTIME) {
    env.PATH = `${path.join(BUNDLED_RUNTIME, 'ffmpeg')};${env.PATH || ''}`;
    env.MPLCONFIGDIR = path.join(os.homedir(), '.moodify', 'matplotlib');
  }
  return env;
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

/**
 * 子进程最后一行非空输出 —— 长任务失败时的原因。
 *
 * 工具脚本（dsp_separate.py / basic-pitch / midi_to_musicxml.py）失败时，唯一有用的话
 * 就在输出的最后一行（`ModuleNotFoundError: No module named 'librosa'` 之类）。
 * 没有它，失败只会剩下一个退出码，而「缺少 Basic Pitch」这种真实原因正是用户需要看到的。
 */
function lastOutputLine(text, max = 300) {
  const lines = String(text || '').trimEnd().split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  if (!lines.length) return null;
  const line = lines[lines.length - 1];
  return line.length > max ? line.slice(-max) : line;
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
  registerUpdateIpc();
  registerTerminalIpc();
  registerCodexIpc();
  registerResearchIpc();
  registerCompareIpc();
  registerTuningIpc();
  registerReviewIpc();
  registerKeepsakeIpc();
  registerSessionIpc();
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
  // 真正的实现在 analyzeAudio()（完成会话编排器复用同一条路径，不复制第二份）
  ipcMain.handle('analysis:run', async (_event, audioPath) => analyzeAudio(audioPath));
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
    let output = ''; // 尾部输出留一份：失败时要能说清**为什么**失败，而不是只给一个退出码
    const feed = (d) => {
      const text = d.toString('utf8');
      output = (output + text).slice(-4000);
      tail += text;
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
      if (code === 0) { resolve({ ok: true, code }); return; }
      // 非零退出必须带原因：调用方（完成会话编排器）要把它当成真实阻断显示给用户。
      // 只回一个 code 的话，「缺少 Basic Pitch / 依赖没装 / 脚本报错」全都会变成
      // 一句没有信息的「失败」——那和编造成功一样没用。
      const reason = lastOutputLine(output)
        || `子进程退出码 ${code}（无输出；工具：${kind}）`;
      resolve({ ok: false, code, reason });
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

  // 快速分离（引擎 A）→ 实现在 separateStems()（完成会话编排器复用同一条路径）
  ipcMain.handle('stems:run', async (_e, caseDir) => separateStems(caseDir));

  // 音频 → MIDI → 实现在 transcribeMidi()（完成会话编排器复用同一条路径）
  ipcMain.handle('midi:run', async (_e, caseDir, audioPath) => transcribeMidi(caseDir, audioPath));

  // MIDI → MusicXML；渲染由壳内 OSMD 完成 → 实现在 convertScore()
  ipcMain.handle('score:run', async (_e, caseDir, midiPath) => convertScore(caseDir, midiPath));

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

// ——— 可复用的真实步骤（IPC 与完成会话编排器共用，绝不写第二条实现）———
//
// 每个函数就是界面上某个按钮背后真正做的事。编排器调用**同一批函数**，
// 所以「一键完成」不会走一条只有它自己知道的路径——用户手动做的与自动做的是同一件事。

/** 检测：源音频 → 新 case（report.json / measurements.json）+ source_path.json + 研究证据。失败抛错。 */
async function analyzeAudio(audioPath) {
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
}

/** 逆向分解：源音频 → case/stems/ 四轨 + manifest.json（预览级，见 V4 §5.2） */
async function separateStems(caseDir) {
  const src = resolveCaseSource(caseDir);
  if (!src) return { ok: false, reason: '未找到源音频（source_path.json 缺失或文件不存在）' };
  const outdir = path.join(caseDir, 'stems');
  fs.mkdirSync(outdir, { recursive: true });
  return runLong('stems', pyExe('basic-pitch'), [
    path.join(TOOLS_ROOT, 'dsp_separate.py'), src, '--outdir', outdir,
  ]);
}

/**
 * 结构 1/2：音频 → MIDI。
 *
 * 当前 Core 的能力是「一个音频文件 → 一份 MIDI」，所以编排器用**源音频**作为输入
 * （midi:run 明确允许源或 case 内分离轨）。逐轨 MIDI 要等 Core 具备逐轨能力，
 * 这一限制记在 V4 §5.4，不在这里假装已经做到。
 */
async function transcribeMidi(caseDir, audioPath) {
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
    // 回传刚生成的 MIDI，供紧接着的曲谱转换使用（不必再扫目录猜）
    const base = path.basename(audioPath).replace(/\.[^.]+$/, '').toLowerCase();
    const mids = listCaseFiles(outdir, '', ['.mid', '.midi']);
    const mine = mids.find((m) => m.name.toLowerCase().startsWith(base)) || mids[0];
    return { ...res, midi: mine ? mine.path : null };
  }
  return res;
}

/** 结构 2/2：MIDI → MusicXML（music21）→ case/score/ */
async function convertScore(caseDir, midiPath) {
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
}

/**
 * ⑥ 复检：对 A、B 各重跑一次**完整**检测，再交 recheck.js 做三方对齐。
 *
 * 复用 Core 既有分析（与 analyzeAudio 同一条 `demo` 路径），不新增第二套测量权威。
 * 缺任一侧就拒绝——不留一张看起来"已复检"的空表。
 */
async function recheckPair(caseDir, pairId) {
  const p = tuning.pairState(caseDir, pairId);
  if (!p.composed) {
    return { ok: false, reason: 'NEED_BOTH_SIDES',
             detail: 'A、B 两侧都需先有 mix.wav 才能复检。' };
  }

  const origPath = path.join(caseDir, 'report.json');
  const paths = { original: origPath, A: p.A.report, B: p.B.report };
  const reports = { original: recheck.readReport(origPath), A: null, B: null };

  for (const side of ['A', 'B']) {
    const mix = pairSideAudio(p, side);
    if (!mix) return { ok: false, reason: 'NEED_BOTH_SIDES', side };
    // 每次复检用独立的 cases-root，避免覆盖上一次的分析 case
    const outRoot = path.join(tuning.sideDir(caseDir, pairId, side), 'recheck-cases');
    fs.mkdirSync(outRoot, { recursive: true });
    const res = await runPython([
      '-m', 'moodify.release_cli', 'demo', mix,
      '--cases-root', outRoot, '--no-open',
    ]);
    if (res.code !== 0) {
      return { ok: false, code: res.code, side,
               reason: res.stderr.trim().slice(-300) || '复检检测失败' };
    }
    const payload = lastJsonLine(res.stdout);
    const reportPath = payload && payload.reports && payload.reports.json;
    if (!reportPath || !fs.existsSync(reportPath)) {
      return { ok: false, reason: 'RECHECK_REPORT_MISSING', side };
    }
    reports[side] = recheck.readReport(reportPath);
    paths[side] = reportPath;
  }

  const built = recheck.buildRecheck({
    pairId, paths, reports, mode: (p.pair && p.pair.mode) || null,
  });
  if (!built.ok) return built;
  recheck.writeRecheck(caseDir, pairId, built.payload);
  return { ok: true, recheck: built.payload, gates: pipeline.snapshot(caseDir).gates };
}

// ——— ④修音 / ⑤复合 / ⑦选定（V4）———
//
// 产品方向（人类 2026-10-04 采纳）：**逆向工程 · 多轨复合**。
// 一次修音产出**两档完整方案**（保守 / 充分），由系统生成，人只负责听和选。
// 选定有**三个**出口：A / B / **保留原版**。第三出口是「最小变换」的落地——
// 若两档都不如原版，人必须有路可退，系统也应主动推荐回原版。
//
// 本段只做「接线」与「记账」，不复制任何声音能力：
//   快速完成的两档整轨渲染 = Core `tuning render-pair`（已实现，MIP-0002 附录 A）
//   深度路径的逐轨修音 / 复合 = Core **尚未实现** → 显式拒绝 TUNABLE_CORE_NOT_AVAILABLE
//   ⑥ 复检        = 对 A、B 各跑一次 Core 既有分析，再交 src/recheck.js 做三方对齐
//   ⑧ 导出        = Core 的 `finishing export`
//   壳不算响度、不写音频字节、不替用户做选择，**绝不留看起来像修音产物的假文件**。
//
// 所有 caseDir 先经 resolveGuardedCase：必须落在 CASES_ROOT 内且确实是 case。

/**
 * 快速完成（仅立体声）：一次 Core 调用生成一对完整候选（A 保守 / B 充分）。
 *
 * 「一键编排」与「只生成两档」按钮**共用这一个实现**——不写第二份接线，也不新建第二个编排器。
 * 壳只做三件事：调 Core、核对磁盘上真的是完整一对、把 **Core 自己写的**理由原样带回。
 * 它不算响度、不写音频、不猜参数。
 */
async function renderFastPair(dir) {
  const src = resolveCaseSource(dir);
  if (!src) {
    return { ok: false, reason: 'NO_SOURCE',
             detail: '未找到源音频（source_path.json 缺失或文件不存在）' };
  }
  const pairId = tuning.newPairId();
  const pairDir = path.join(tuning.tuningDir(dir), pairId);
  fs.mkdirSync(tuning.tuningDir(dir), { recursive: true });

  const res = await runPython([
    '-m', 'moodify.release_cli', 'tuning', 'render-pair',
    '--mode', 'fast-stereo-only',
    '--source', src,
    '--output-dir', pairDir,
    '--pair-id', pairId,
  ]);
  const payload = lastJsonLine(res.stdout);
  if (res.code !== 0 || !payload || payload.status !== 'rendered') {
    const err = lastJsonLine(res.stderr);
    const reason = (err && err.error) || res.stderr.trim().slice(-300) || 'Core 未能生成两档候选';
    // 失败时 Core 不发布任何 pair；这里如实报告磁盘上还剩什么，而不是「已清理」了事。
    return {
      ok: false, code: res.code, reason: 'RENDER_PAIR_FAILED', detail: reason,
      leftover: fs.existsSync(pairDir) ? pairDir : null,
    };
  }

  // Core 说成功 ≠ 磁盘上真的是完整一对。阶段由产物推导，所以这里必须自己核对一遍。
  const missing = [];
  if (!fs.existsSync(path.join(pairDir, 'pair.json'))) missing.push('pair.json');
  for (const side of ['A', 'B']) {
    for (const rel of ['plan.json', 'evidence.json', 'mix.wav', path.join('tuned', 'source.wav')]) {
      if (!fs.existsSync(path.join(pairDir, side, rel))) missing.push(`${side}/${rel}`);
    }
  }
  if (missing.length) {
    return {
      ok: false, reason: 'PAIR_INCOMPLETE_ON_DISK',
      detail: 'Core 报告成功，但磁盘上这一对不完整：' + missing.join('、'),
      leftover: pairDir,
    };
  }
  return { ok: true, pairId, pairDir, tiers: payload.tiers, checks: payload.checks, sides: payload.sides };
}

/** 一侧的整曲合成产物；没有就是 null（单边不成阶段）。 */
function pairSideAudio(pair, side) {
  const s = pair && pair[side];
  return (s && s.mix) || null;
}

// ——— A/B 审听工作台的数据面（Phase 2.2，只读）———
//
// 工作台要展示的每一张频谱、每一个指标都必须是**真实产物**里的东西：候选自己那次复检的
// report / scan 图，以及 pair 里 Core 写的 plan / evidence。所以路径全部由 main 侧从
// recheck 产物**推导并守卫**，渲染层只拿到「可以读的东西」，拿不到「任意路径」。
//
// 这一层不算测量、不跑分析、不改证据：它只做三件事——把 recheck 引用的报告读出来、
// 把 Core 已经生成的图找出来、把 Core 的指标按固定顺序摊成卡片数据。

/** 审听卡片偏好顺序。值一律取自 recheck，缺失就写「不可对齐」，绝不补算。 */
const REVIEW_CARD_METRICS = Object.freeze([
  { id: 'integrated_lufs', label: '整体响度', unit: 'LUFS', digits: 2 },
  { id: 'true_peak_dbfs', label: '真峰值', unit: 'dBFS', digits: 2 },
  { id: 'sample_peak_dbfs', label: '采样峰值', unit: 'dBFS', digits: 2 },
  { id: 'rms_dbfs', label: 'RMS 电平', unit: 'dBFS', digits: 2 },
  { id: 'crest_factor_db', label: '波峰因数', unit: 'dB', digits: 2 },
  { id: 'plr_db', label: '峰均比 PLR', unit: 'dB', digits: 2 },
  { id: 'core_mid_500_2000_hz', label: '核心中频占比', unit: 'ratio', digits: 3 },
  { id: 'low_mid_120_250_hz', label: '低中频占比', unit: 'ratio', digits: 3 },
  { id: 'stereo_width_proxy', label: '立体声宽度', unit: 'ratio', digits: 3 },
  { id: 'stereo_correlation', label: '声道相关性', unit: 'ratio', digits: 3 },
  { id: 'spectral_centroid_hz', label: '频谱质心', unit: 'Hz', digits: 1 },
  { id: 'clipping_sample_ratio', label: '削波比例', unit: 'ratio', digits: 4 },
]);

/**
 * 把三方对齐表摊成该侧的审听卡片。
 *
 * 只在 alignable / not_alignable 里出现过的指标才会成为卡片——没被复检覆盖的指标不出现，
 * 也绝不替 Core 补算一个值。`digits` 写死在这里，A/B 两页因此天然同精度（§3.3）。
 */
function buildReviewCards(alignment, side) {
  if (!alignment) return [];
  const alignable = new Set(Array.isArray(alignment.alignable) ? alignment.alignable : []);
  const notAlignable = new Map(
    (Array.isArray(alignment.not_alignable) ? alignment.not_alignable : [])
      .map((x) => [x.name, x.reason]));
  const cards = [];
  for (const metric of REVIEW_CARD_METRICS) {
    const { id } = metric;
    if (alignable.has(id)) {
      const column = alignment[side] || {};
      const original = (alignment.original && alignment.original.metrics
        && alignment.original.metrics[id]) || null;
      const candidate = (column.metrics && column.metrics[id]) || null;
      if (!original || !candidate) continue;
      cards.push({
        ...metric,
        status: 'alignable',
        original: original.value,
        value: candidate.value,
        // 原版对原版的变化是 0，不是「未定义」——这样任何消费者都不会打印出 Δ null。
        delta: side === 'original' ? 0 : ((column.delta_vs_original || {})[id] ?? null),
      });
    } else if (notAlignable.has(id)) {
      cards.push({ ...metric, status: 'not_alignable', reason: notAlignable.get(id) });
    }
  }
  return cards;
}

/** 报告目录下 Core 已经生成的频谱图；不存在的直接不列（缺图由 UI 说缺图）。 */
function sideSpectra(reportPath) {
  const dir = path.join(path.dirname(reportPath), 'scan');
  return [
    { key: 'spectrum_log', label: '频谱（log）', file: path.join(dir, 'spectrum_log.png') },
    { key: 'spectrum_linear', label: '频谱（linear）', file: path.join(dir, 'spectrum_linear.png') },
  ].filter((s) => fs.existsSync(s.file)).map((s) => ({ key: s.key, label: s.label, path: s.file }));
}

/** 已经导出过的图表（由 tuning:charts 生成，同样落在该报告的 charts/ 下）。
    文件名由 Core 的导出器决定（`chart_<name>.png`），这里只按它的命名去找，不猜。 */
function sideCharts(reportPath) {
  const dir = path.join(path.dirname(reportPath), 'charts');
  const keys = ['bands', 'levels_db', 'stereo_ratios'];
  const labels = { bands: '频段能量', levels_db: '电平 / 响度', stereo_ratios: '立体声分布' };
  return keys
    .map((key) => ({ key, label: labels[key], file: path.join(dir, `chart_${key}.png`) }))
    .filter((c) => fs.existsSync(c.file))
    .map((c) => ({ key: c.key, label: c.label, path: c.file }));
}

/**
 * 一侧的证据包：报告 + 频谱 + 图表 + 卡片 + Core 写的 plan / evidence。
 *
 * 守卫：报告路径必须落在**本 case 内**且确实由这份 recheck 引用；候选侧的 plan / evidence
 * 必须落在本 case 内。任一条不成立就拒绝，不给渲染层任何越界读取面。
 */
function sideEvidence(dir, pairId, side, alignment) {
  const rc = recheck.readRecheck(dir, pairId);
  if (!rc) return { ok: false, reason: 'NO_RECHECK' };
  const key = side === 'ORIGINAL' ? 'original' : side;
  const reportPath = rc[key] && rc[key].report;
  if (!reportPath || !fs.existsSync(reportPath)) return { ok: false, reason: 'NO_REPORT', side };
  let real;
  let realCase;
  try {
    real = fs.realpathSync(reportPath);
    realCase = fs.realpathSync(dir);
  } catch { return { ok: false, reason: 'NO_REPORT', side }; }
  if (!insideDir(realCase, real)) return { ok: false, reason: 'EVIDENCE_OUTSIDE_CASE', side };

  const bundle = {
    side,
    reportPath: real,
    spectra: sideSpectra(real),
    charts: sideCharts(real),
    cards: buildReviewCards(alignment, key),
    isCandidate: side !== 'ORIGINAL',
  };
  if (side === 'ORIGINAL') {
    bundle.source = resolveCaseSource(dir);
    bundle.audio = Boolean(bundle.source);
    return { ok: true, bundle };
  }

  const sideDir = tuning.sideDir(dir, pairId, side);
  const planPath = path.join(sideDir, 'plan.json');
  const evidencePath = path.join(sideDir, 'evidence.json');
  const mixPath = path.join(sideDir, 'mix.wav');
  const plan = fs.existsSync(planPath) ? JSON.parse(fs.readFileSync(planPath, 'utf8')) : null;
  const evidence = fs.existsSync(evidencePath)
    ? JSON.parse(fs.readFileSync(evidencePath, 'utf8')) : null;
  bundle.audio = fs.existsSync(mixPath);
  bundle.mixPath = bundle.audio ? mixPath : null;
  bundle.planPath = fs.existsSync(planPath) ? planPath : null;
  bundle.evidencePath = fs.existsSync(evidencePath) ? evidencePath : null;
  bundle.tier = plan && plan.tier ? plan.tier : null;
  bundle.calibrationStatus = (plan && plan.calibration_status)
    || (evidence && evidence.calibration_status) || null;
  // 处理链与门禁：直接取 Core 写的那份，不转述、不重算（只读展示，不可编辑）。
  bundle.chain = evidence ? {
    nodes: (evidence.tier && evidence.tier.parameters && evidence.tier.parameters.nodes) || [],
    graphDigest: evidence.graph_digest_sha256 || null,
    checks: Array.isArray(evidence.checks) ? evidence.checks : [],
    reviewRequired: evidence.review_required === true,
    composite: (plan && plan.composite) || null,
    engineVersion: evidence.engine_version || null,
  } : null;
  return { ok: true, bundle };
}

function registerReviewIpc() {
  // 工作台的一次性数据面。所有路径都由这里推导并守卫，渲染层不参与路径拼接。
  ipcMain.handle('tuning:evidence', async (_e, caseDir, pairId) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    if (!pairId || !fs.existsSync(tuning.pairDir(dir, pairId))) {
      return { ok: false, reason: 'NO_SUCH_PAIR' };
    }
    const rc = recheck.readRecheck(dir, pairId);
    if (!rc) return { ok: false, reason: 'NO_RECHECK' };
    const sides = {};
    for (const side of ['ORIGINAL', 'A', 'B']) {
      const one = sideEvidence(dir, pairId, side, rc);
      if (!one.ok) return { ...one, pair_id: pairId };
      sides[side] = one.bundle;
    }
    return {
      ok: true,
      pair_id: rc.pair_id || pairId,
      mode: rc.mode || null,
      sides,
      // 对齐表的三方报告路径：数据守恒测试与 UI 都据此核对「A 页只绑 A」。
      reports: {
        original: (rc.original && rc.original.report) || null,
        A: (rc.A && rc.A.report) || null,
        B: (rc.B && rc.B.report) || null,
      },
    };
  });

  // 单个侧的检测图表：Core 的导出器按**该侧自己那份 report** 生成，落在该报告目录下。
  // 这不是新测量，也不是第二套绘图权威——就是把 Core 已有的图渲染出来。
  ipcMain.handle('tuning:charts', async (_e, caseDir, pairId, side) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    if (!['ORIGINAL', 'A', 'B'].includes(side)) return { ok: false, reason: 'BAD_SIDE' };
    const rc = recheck.readRecheck(dir, pairId);
    if (!rc) return { ok: false, reason: 'NO_RECHECK' };
    const key = side === 'ORIGINAL' ? 'original' : side;
    const reportPath = rc[key] && rc[key].report;
    if (!reportPath || !fs.existsSync(reportPath)) return { ok: false, reason: 'NO_REPORT', side };
    let real;
    try { real = fs.realpathSync(reportPath); } catch { return { ok: false, reason: 'NO_REPORT', side }; }
    if (!insideDir(fs.realpathSync(dir), real)) {
      return { ok: false, reason: 'EVIDENCE_OUTSIDE_CASE', side };
    }
    const res = await runPython([
      '-m', 'moodify.ui.chart_export', real, '--out', path.join(path.dirname(real), 'charts'),
    ]);
    if (res.code !== 0) {
      return { ok: false, reason: res.stderr.trim().slice(-300) || 'chart export failed', side };
    }
    return { ok: true, side, charts: sideCharts(real), payload: lastJsonLine(res.stdout) };
  });
}

function registerTuningIpc() {
  // 修音对清单 + 门禁 + 可逆性状态 + 已做的选择。UI 靠它决定哪些动作可点。
  ipcMain.handle('tuning:pairs', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const snap = pipeline.snapshot(dir);
    const currentPairId = snap.info.currentPair ? snap.info.currentPair.pair_id : null;
    return {
      ok: true,
      source: resolveCaseSource(dir),
      pairs: snap.info.pairs,
      currentPairId,
      decisions: snap.info.decisions,
      roundtrip: snap.info.roundtrip,
      // ⑦ 选定 每一对到底能不能选；不能就给出原因（与 appendDecision 同一条规则）。
      // UI 靠它决定三个出口按钮是否可点——按钮必须与真实准入一致，否则点了只会被拒。
      decidable: currentPairId ? tuning.canDecide(dir, currentPairId) : false,
      decisionBlockers: Object.fromEntries(
        snap.info.pairs.map((p) => [p.pair_id, tuning.decisionBlockers(dir, p.pair_id)]),
      ),
      decisionBacked: snap.info.decisionValid,
      stage: snap.stage,
      gates: snap.gates,
      exits: [...tuning.EXITS],
    };
  });

  // 生成两档完整方案。
  //
  // 分支顺序 = 用户的真实处境，逐条说实话：
  //   ① 人已显式选择快速完成 → **真的调 Core** 生成一对整轨候选；
  //   ② 深度路径被声明为可执行（能力清单里已有逐轨能力）→ 本壳尚未接这条线，如实拒绝；
  //   ③ 连检测都没有 → 说清缺什么；
  //   ④ 其余（深度资产可能齐备，但深度跑不了）→ 说清深度为什么跑不了，并告诉人可以**显式切换**。
  // 快速路径可用**不会**解锁深度路径：这里的分支就是那条纪律的落点。
  ipcMain.handle('tuning:render', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const snap = pipeline.snapshot(dir);
    if (snap.gates.canTuneQuick) {
      const r = await renderFastPair(dir);
      if (!r.ok) return r;
      return { ...r, gates: pipeline.snapshot(dir).gates };
    }
    if (snap.gates.canTune) {
      return {
        ok: false,
        reason: 'TUNABLE_CORE_NOT_AVAILABLE',
        detail: '深度路径的逐轨修音 / 复合尚未接入本壳，本壳不会生成任何逐轨修音产物。',
        planned: pipeline.PLANNED_CAPABILITIES.map((c) => ({ ...c })),
      };
    }
    if (!snap.gates.baseReady) {
      return { ok: false, reason: 'TUNE_LOCKED', blockers: snap.gates.tuneBlockers,
               detail: snap.gates.tuneBlockers[0] || '前置条件未满足' };
    }
    // 深度路径现在不可执行（可逆性未验证/未通过，或逐轨能力未就绪）。
    // 这不是「缺前置」而是「产品能力尚未就绪」，所以不能只说 TUNE_LOCKED：
    // 必须把真实原因与**由人确认**的补救一起给出。
    return {
      ok: false,
      reason: 'DEEP_NOT_EXECUTABLE',
      blockers: snap.gates.deepTuneBlockers,
      deepBlockers: snap.gates.deepBlockers,
      canSwitchToFast: Boolean(snap.gates.canRequestQuick),
      detail: '深度路径现在不可执行：' + (snap.gates.deepTuneBlockers[0] || '前置条件未满足')
        + (snap.gates.canRequestQuick
          ? '。你可以显式切换到「快速完成（仅立体声）」（需要你确认，系统不会自动切换）。'
          : '。'),
    };
  });

  // ⑦ 选定：A / B / 保留原版。只追加、不可修改；同一 requestId 重试幂等。
  ipcMain.handle('tuning:decision', async (_e, caseDir, pairId, kept, role, requestId) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const r = tuning.appendDecision(dir, { pairId, kept, role, requestId });
    if (!r.ok) return r;
    return { ...r, decision: tuning.decisionFor(dir, pairId), gates: pipeline.snapshot(dir).gates };
  });

  // 试听 A / B / 原版。A、B 必须落在本 case 内；ORIGINAL 是本 case 自己记录的源。
  // 渲染层递什么路径都读不到别的音频。
  ipcMain.handle('tuning:audio', async (_e, caseDir, pairId, side) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) throw new Error('INVALID_CASE_DIR');
    if (!tuning.EXITS.includes(side)) throw new Error('BAD_SIDE');
    let file;
    if (side === 'ORIGINAL') {
      file = resolveCaseSource(dir);
    } else {
      file = pairSideAudio(tuning.pairState(dir, pairId), side);
    }
    if (!file || !fs.existsSync(file)) throw new Error('AUDIO_NOT_AVAILABLE');
    const real = fs.realpathSync(file);
    if (side !== 'ORIGINAL' && !insideDir(fs.realpathSync(dir), real)) {
      throw new Error('AUDIO_OUTSIDE_CASE');
    }
    return fs.promises.readFile(real);
  });

  // 读已产出的对齐表（⑥ 的产物）。
  ipcMain.handle('tuning:recheck', async (_e, caseDir, pairId) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const r = recheck.readRecheck(dir, pairId);
    return r ? { ok: true, recheck: r } : { ok: false, reason: 'NO_RECHECK' };
  });

  // ⑥ 复检：对 A、B 各重跑一次**完整**检测，再与原版逐指标对齐。
  //
  // 实现在 recheckPair()（完成会话编排器复用同一条路径）。
  // 注意：本处理器在 Core 能产出 mix.wav 之前**不会被走到**（composed 为 false）。
  // 它是 ⑥ 的接口契约，属 P2/P3 的对接面。
  ipcMain.handle('tuning:recheckRun', async (_e, caseDir, pairId) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    return recheckPair(dir, pairId);
  });

  // ⑧ 导出：把选定的一侧（或原版）交给 Core 的 delivery 编码，再复制到用户选定路径。
  // 这是唯一把音频写出 case 之外的地方，且是**显式动作**。
  ipcMain.handle('tuning:export', async (event, caseDir, pairId, kept) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    if (!tuning.EXITS.includes(kept)) return { ok: false, reason: 'BAD_KEPT' };

    // 出口必须与账本一致：不允许导出「没选过的东西」。
    const decided = tuning.decisionFor(dir, pairId);
    if (!decided || decided.kept !== kept) {
      return { ok: false, reason: 'NOT_CHOSEN', detail: '请先在 ⑦ 选定这一出口。' };
    }
    // 而且**此刻**仍要有一对完整候选撑着它：候选被删掉之后，「保留原版」不该还能把原版交出去。
    // 与 appendDecision 同一条规则（validateDecision），不另立标准。
    const stillValid = tuning.validateDecision(dir, { pairId, kept });
    if (!stillValid.ok) {
      return {
        ok: false,
        reason: 'CANDIDATES_INCOMPLETE',
        blockers: stillValid.blockers || [],
        detail: stillValid.detail || 'A / B 候选或复检产物已不完整，导出被拒绝。',
      };
    }

    const audioPath = kept === 'ORIGINAL'
      ? resolveCaseSource(dir)
      : pairSideAudio(tuning.pairState(dir, pairId), kept);
    if (!audioPath || !fs.existsSync(audioPath)) return { ok: false, reason: 'AUDIO_NOT_AVAILABLE' };

    const outDir = path.join(dir, 'studio', 'export');
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

    const win = BrowserWindow.fromWebContents(event.sender);
    const picked = await dialog.showSaveDialog(win, {
      title: '导出音频',
      defaultPath: path.basename(exported.output),
      filters: [{ name: 'WAV 音频', extensions: ['wav'] }],
    });
    if (picked.canceled || !picked.filePath) {
      // 用户取消：case 内的导出产物保留（它是记录），但不写到用户路径
      return { ok: false, canceled: true, reason: '已取消导出' };
    }
    try { fs.copyFileSync(exported.output, picked.filePath); }
    catch (err) { return { ok: false, reason: '写入目标路径失败：' + err.message }; }

    // 导出记录写明「导出的是哪一对、哪一个出口」——选了 ORIGINAL 也要能日后指出来
    const record = {
      schema: 'moodify.studio.export/0.2',
      pair_id: pairId,
      kept,
      chosen_at: decided.at || null,
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

// ——— 完成会话（「一键完成机」· Phase 1）———
//
// 产品形态：放入一首歌 → 一次启动 → 内部自动执行 → 原版 / A / B → 人选择 → 导出。
//
// 「一键」只简化**用户操作**：
//   · 不省略内部步骤 —— 检测 → 逆向分解 → 结构 → 可逆性 → 修音/复合 → 复检，一步不少；
//   · 不把未实现能力伪装成成功 —— 缺能力时停在真实阻断态，并说清「本次没有生成任何候选」；
//   · 不维护第二套状态机 —— 每一轮都从磁盘重新推导（pipeline.snapshot），
//     编排队列只是对唯一权威的投影（调度循环本身在 src/orchestrator.js）。
//
// 这里只提供两样东西：**真实步骤函数**（与手动按钮共用同一批，绝不写第二条实现），
// 以及 IPC 接线。

/**
 * ① 检测 这一步在会话里的真实行为。
 *
 * 为什么不是「直接再检测一次」：Core 的检测（`moodify demo` → `analyze_to_case`）
 * **总是新建一个 case 目录**（case_id 新生成，`mkdir(exist_ok=False)`），它无法把
 * report.json 补写进一个已经存在的 case。所以对一个没有 report.json 的世界来说，
 * 「再检测一次」并不会让这一步完成，只会造出一个同名的孤儿 case —— 反复重试就是反复造垃圾。
 *
 * 因此这里如实拒绝，并给出唯一真正可行的补救（重新导入，检测会建立新的世界）。
 * 会话自己不修 case：把别人的产物搬进这个目录才是真正不许发生的事。
 */
async function sessionAnalyze(dir) {
  if (pipeline.snapshot(dir).info.hasReport) return { ok: true, skipped: true };
  const src = resolveCaseSource(dir);
  return {
    ok: false,
    reason: 'CASE_WITHOUT_REPORT',
    detail: '这个还没有检测产物（缺 report.json），而 Core 的检测总是新建一个世界，'
      + '无法就地补写。请用「打开音频」重新导入'
      + (src ? `这首歌（${path.basename(src)}）` : '这首歌')
      + '，检测会建立一个新的世界。本壳不会把检测结果搬进别的目录，也不会重复新建世界。',
  };
}

/** ③ 结构：音频 → MIDI（必需）→ 曲谱（派生解读，失败不阻断）。 */
async function sessionStructure(dir) {
  const src = resolveCaseSource(dir);
  if (!src) return { ok: false, reason: '未找到源音频（source_path.json 缺失或文件不存在）' };
  const midi = await transcribeMidi(dir, src);
  if (!midi.ok) return midi;
  if (!midi.midi) return { ok: false, reason: '未生成 MIDI 文件' };
  // 曲谱是派生解读，转不出来不阻断主流程（MIDI 才是机器可读结构）
  const score = await convertScore(dir, midi.midi);
  return {
    ok: true,
    midi: midi.midi,
    score: score.ok ? score.musicxml : null,
    scoreSkipped: score.ok ? null : (score.reason || '曲谱转换失败'),
  };
}

/**
 * ④修音 / ⑤复合 这一步在会话里的真实行为。
 *
 * 快速完成（仅立体声）已经由 Core 实现：一次调用产出 A 保守 / B 充分两个完整整轨候选。
 * 深度路径（逐轨音准与节奏修正）仍然是 Core 不具备的能力，继续如实拒绝——
 * 快速路径可用**不是**深度路径的解锁理由。
 */
async function sessionTune(dir) {
  const snap = pipeline.snapshot(dir);
  if (snap.gates.canTuneQuick) {
    const r = await renderFastPair(dir);
    return r.ok ? { ok: true, ...r } : r;
  }
  if (snap.gates.canTune) {
    return {
      ok: false,
      reason: 'TUNABLE_CORE_NOT_AVAILABLE',
      detail: '深度路径的逐轨修音 / 复合尚未接入本壳；本壳不生成任何逐轨修音产物。',
    };
  }
  return {
    ok: false,
    reason: 'DEEP_NOT_EXECUTABLE',
    detail: '深度路径现在不可执行：' + (snap.gates.deepTuneBlockers[0] || '前置条件未满足')
      + (snap.gates.canRequestQuick
        ? '。可以显式切换到「快速完成（仅立体声）」（需要你确认）。'
        : '。'),
  };
}

/** ⑥ 复检：对当前修音对的两侧各重跑一次完整检测，再做三方对齐。 */
async function sessionRecheck(dir) {
  const pair = pipeline.snapshot(dir).info.currentPair;
  if (!pair) return { ok: false, reason: 'NO_PAIR', detail: '还没有修音对，无从复检。' };
  return recheckPair(dir, pair.pair_id);
}

// 相位 → 真实步骤。键与 session.PHASES[].run 一一对应（测试会钉住这一点）。
const SESSION_STEPS = Object.freeze({
  analyze: sessionAnalyze,
  separate: separateStems,
  structure: sessionStructure,
  tune: sessionTune,
  recheck: sessionRecheck,
});

const orchestrator = createOrchestrator({
  snapshot: (dir) => pipeline.snapshot(dir),
  resolveCaseSource,
  steps: SESSION_STEPS,
});

const sessionView = orchestrator.sessionView;
const runCompletionSession = orchestrator.runCompletionSession;

// ——— 完成时刻的留存（Phase 2.3）———
//
// 「完成」不是一个新的状态权威：它由既有事实推导——有效 decision（tuning 的 ⑦ 准入：
// pair 存在 + A/B 两侧候选 + 真实复检）+ 该 decision 指向的那一侧音频还在。
// `keepsake.json` 只是**表现层留存记录**：它记录选的是哪一版、什么时候、人写的一句话和
// 波形印记。它读不出完成状态，也不能让阶段前进或解锁导出（keepsake 永远在下游）。

const keepsake = require('./keepsake');

/** 源曲名（不含扩展名）。只用于标题与作品卡文件名。 */
function caseTitle(dir) {
  try {
    const report = JSON.parse(fs.readFileSync(path.join(dir, 'report.json'), 'utf8'));
    const name = report && report.source && report.source.name;
    if (name) return path.basename(String(name), path.extname(String(name)));
  } catch { /* fall through to the recorded source path */ }
  const src = resolveCaseSource(dir);
  if (src) return path.basename(src, path.extname(src));
  return path.basename(dir);
}

/**
 * 完成状态投影（只读）。
 *
 * complete 只可能来自 `tuning.decisionBacked()` —— 手写的假记录、被删掉候选之后的记录、
 * 或者没有记录的 case 都得不到完成层。
 */
function completionState(dir) {
  const snap = pipeline.snapshot(dir);
  const backed = tuning.decisionBacked(dir);
  const decision = backed.decision || null;
  const complete = Boolean(backed.valid && decision);
  const pairId = complete ? decision.pair_id : null;
  const pair = complete
    ? (snap.info.pairs.find((p) => p.pair_id === pairId) || null)
    : null;
  const selected = complete ? decision.kept : null;
  const selectedAudio = !complete ? null
    : (selected === 'ORIGINAL' ? resolveCaseSource(dir) : pairSideAudio(pair, selected));
  const audioAvailable = Boolean(selectedAudio && fs.existsSync(selectedAudio));

  const record = keepsake.readKeepsake(dir);
  const stored = record.keepsake || {};
  const tierLabel = pair && pair.mode === 'FAST_STEREO_ONLY'
    ? '快速完成（仅立体声）'
    : (pair && pair.mode === 'DEEP' ? '深度完成' : null);
  const completedAt = complete ? (decision.at || null) : null;

  return {
    ok: true,
    complete,
    // 为什么还没有完成层：直接引用 ⑦ 的真实原因，不另编一套
    reason: complete ? null : (backed.reason || 'NOT_COMPLETE'),
    blockers: complete ? [] : (backed.blockers || []),
    selected,
    selectedLabel: selected ? session.exitLabel(selected) : null,
    pairId,
    title: caseTitle(dir),
    tierLabel,
    completedAt,
    audioAvailable,
    audioPath: audioAvailable ? selectedAudio : null,
    decisionRequestId: complete ? (decision.request_id || null) : null,
    // 留存内容（非权威）：读不出来就是空的，声音流程不受影响
    inscription: typeof stored.inscription === 'string' ? stored.inscription : '',
    imprint: Array.isArray(stored.imprint) ? stored.imprint : null,
    imprintBuckets: keepsake.IMPRINT_BUCKETS,
    inscriptionMax: keepsake.INSCRIPTION_MAX_CHARS,
    inscriptionMaxLines: keepsake.INSCRIPTION_MAX_LINES,
    storedSelection: stored.selected || null,
    keepsakeError: record.error,
    keepsakeAge: stored.updated_at || null,
    // 作品卡能画的东西只有这些字段（不含 id / 路径 / hash）
    card: keepsake.cardModel({
      title: caseTitle(dir), selected, completedAt, inscription: stored.inscription, tierLabel,
    }),
  };
}

function registerKeepsakeIpc() {
  const guard = (caseDir) => resolveGuardedCase(caseDir);

  // 只读投影。渲染层据它决定「进完成层还是进 A/B 审听」。
  ipcMain.handle('keepsake:state', async (_e, caseDir) => {
    const dir = guard(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    return completionState(dir);
  });

  // 把当前有效 decision 投影进留存记录（selected / completed_at / request_id）。
  // 文字与波形印记不动；没有有效 decision 时拒绝写入（完成层消失，但旧文字留着）。
  ipcMain.handle('keepsake:sync', async (_e, caseDir) => {
    const dir = guard(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const state = completionState(dir);
    if (!state.complete) return { ok: false, reason: state.reason || 'NOT_COMPLETE' };
    const res = keepsake.writeKeepsake(dir, {
      case_id: path.basename(dir),
      decision_request_id: state.decisionRequestId,
      selected: state.selected,
      completed_at: state.completedAt,
    });
    return res.ok ? { ok: true, keepsake: res.keepsake, state: completionState(dir) } : res;
  });

  // 一句私人文字：可选、本地、可编辑可清空。清空就是普通编辑（写空串），没有确认弹窗。
  ipcMain.handle('keepsake:inscription', async (_e, caseDir, text) => {
    const dir = guard(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const valid = keepsake.validateInscription(text);
    if (!valid.ok) return valid;
    const existing = keepsake.readKeepsake(dir).keepsake;
    const state = completionState(dir);
    if (!existing && !state.complete) {
      // 还没有任何留存记录、也还没完成：没有东西可以附着，拒绝写入而不是凭空造一条
      return { ok: false, reason: 'NOT_COMPLETED' };
    }
    const res = keepsake.writeKeepsake(dir, { inscription: valid.text });
    return res.ok ? { ok: true, inscription: res.keepsake.inscription } : res;
  });

  // 波形印记：渲染层从**已解码的最终音频**算出峰值，这里只做定长/限幅/舍入后落盘。
  ipcMain.handle('keepsake:imprint', async (_e, caseDir, values) => {
    const dir = guard(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const state = completionState(dir);
    if (!state.complete) return { ok: false, reason: state.reason || 'NOT_COMPLETE' };
    const imprint = keepsake.normalizeImprint(values);
    if (!imprint.length) return { ok: false, reason: 'EMPTY_IMPRINT' };
    const res = keepsake.writeKeepsake(dir, { imprint });
    return res.ok ? { ok: true, imprint: res.keepsake.imprint } : res;
  });

  // 作品卡：渲染层画好 PNG 字节，这里只负责系统保存对话框与落盘（唯一写出 case 的地方）。
  ipcMain.handle('keepsake:saveCard', async (event, caseDir, bytes) => {
    const dir = guard(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const state = completionState(dir);
    if (!state.complete) return { ok: false, reason: state.reason || 'NOT_COMPLETE' };
    const buffer = Buffer.isBuffer(bytes) ? bytes
      : (bytes instanceof ArrayBuffer ? Buffer.from(new Uint8Array(bytes)) : Buffer.from(bytes || []));
    if (!buffer.length) return { ok: false, reason: 'EMPTY_PNG' };

    const win = BrowserWindow.fromWebContents(event.sender);
    let defaultPath = keepsake.defaultCardFileName(state.title);
    try { defaultPath = path.join(app.getPath('pictures'), defaultPath); } catch { /* 没有图片目录就退到纯文件名 */ }
    const picked = await dialog.showSaveDialog(win, {
      title: '保存作品卡',
      defaultPath,
      filters: [{ name: 'PNG 图片', extensions: ['png'] }],
    });
    if (picked.canceled || !picked.filePath) return { ok: false, canceled: true };
    try {
      fs.writeFileSync(picked.filePath, buffer);
    } catch (err) {
      return { ok: false, reason: 'CARD_WRITE_FAILED', detail: err && err.message };
    }
    return { ok: true, path: picked.filePath, bytes: buffer.length };
  });
}

function registerSessionIpc() {
  // 读会话状态（不执行任何步骤）。EMPTY 由渲染层处理：没有 case 就没有会话。
  ipcMain.handle('session:view', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    return { ok: true, view: sessionView(dir) };
  });

  // 一键启动。已完成的步骤跳过，所以重复启动是安全的（上一次真实失败也会在这次重新尝试，
  // 因为失败记录只影响显示、不影响控制流）；**并发**启动被显式拒绝——
  // 两次并发会在同一个 case 目录里交错写产物，那是最难排查的一类损坏。
  ipcMain.handle('session:start', async (event, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    if (!session.acquire(dir)) {
      return { ok: false, reason: 'ALREADY_RUNNING', view: sessionView(dir) };
    }
    try {
      return await runCompletionSession(event, dir);
    } finally {
      session.release(dir);
    }
  });
}

// ——— 生产流程（V4）：检测 → 逆向分解 → 结构 → 修音 → 复合 → 复检 → 选定 → 导出 ———
//
// 产品原则：**先理解，再分解，再修音，再复合，最后复检**。
// 本节只暴露「流程状态 + context 包」，不含任何音频算法：
//   阶段由磁盘产物**推导**（见 src/pipeline.js），不是人手推进，也不会谎报。
//   context 只引用已存在的产物；`preserve`（该保护什么）是听觉判断，由人填。
//
// ②问题 已退场（2026-10-04）：Core 的 findings 仍在 ①检测 的 report 里可见，
// 但不再单设阶段与 IPC。诚实要求不变——「无 finding」只能说「当前规则未发现技术问题」。

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
      // 计划中的能力随快照一起给 UI，好让「未就绪」有出处而不是一句含糊的提示
      plannedCapabilities: pipeline.PLANNED_CAPABILITIES.map((c) => ({ ...c })),
    };
  });

  // 构建 context 包：只引用不复制，且只写真实存在的路径。
  // 这是 ④修音 的输入（分轨 / MIDI / 可逆性状态 / 计划中能力），不再是「方案」产物——
  // ⑤方案 已并入 ④，两档参数由 Core 的 tuning 产出。
  ipcMain.handle('pipeline:context', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const context = pipeline.buildContext(dir);
    const file = pipeline.writeContext(dir, context);
    return {
      ok: true,
      context,
      path: file,
      stage: pipeline.snapshot(dir).stage,
      gates: pipeline.snapshot(dir).gates,
    };
  });

  ipcMain.handle('pipeline:readContext', async (_e, caseDir) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    const ctx = pipeline.readJsonSafe(path.join(dir, 'studio', 'context.json'));
    return ctx ? { ok: true, context: ctx } : { ok: false, reason: 'NO_CONTEXT' };
  });

  // 显式选择「快速完成（仅立体声）」。
  // 这是**人类决定**，不是一个 UI 开关：深度路径需要 分轨 + MIDI + 可逆性通过 + 逐轨能力；
  // 跳过它必须由人主动选择，并留下可追溯的记录（finish_mode.json）。
  // 绝不自动解锁——否则快捷路径会变成默认路径。
  // 注意：快速路径同样必须走 ⑤复合 → ⑥复检 → ⑦选定 才能导出（跳过的是分解，不是验证）。
  //
  // 2026-10-04 裁定（Phase 2.1）：**已经有分轨 / MIDI 的 case 也可以切换**。
  // 旧的「深度资产齐备就不给快速入口」在逐轨能力未实现时是一条死路。切换只写这一份记录：
  // 不生成音频、不删除/移动任何深度资产、不改动任何已有 pair 或账本。
  ipcMain.handle('pipeline:setFinishMode', async (_e, caseDir, mode) => {
    const dir = resolveGuardedCase(caseDir);
    if (!dir) return { ok: false, reason: 'INVALID_CASE_DIR' };
    if (mode !== null && mode !== 'QUICK_STEREO_ONLY') {
      return { ok: false, reason: 'BAD_MODE' };
    }
    const snap = pipeline.snapshot(dir);
    if (mode === 'QUICK_STEREO_ONLY') {
      // 连检测都没完成时，连「快速」都谈不上
      if (!snap.gates.baseReady) return { ok: false, reason: 'NEED_ANALYZE' };
      // 快速路径本身不可用时不能记录成「已选择」——那会写下一个跑不通的模式
      if (!snap.gates.fastAvailable) return { ok: false, reason: 'FAST_NOT_AVAILABLE' };
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
  if (win.webContents && typeof win.webContents.once === 'function') {
    win.webContents.once('did-finish-load', () => {
      setupAutoUpdater();
      if (app.isPackaged) setTimeout(() => checkForDesktopUpdate(false), 5000);
    });
  }
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
