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

/** The plan-generation prompt: Claude Code reads the case, writes the plan. */
const PLAN_PROMPT = [
  '你是 Moodify 的后处理方案工程师。请读取当前目录下的 report.json、',
  'measurements.json、judgment_rules.json（如存在），基于 L1 技术测量给出',
  '【修音与混音方案】，包含：1) 目标（可测量）；2) 逐步算子建议（算子/参数/',
  '理由，映射到标准算子 gain/eq/limiter/compressor/stereo 等）；',
  '3) 验收指标（使用 report.json 中同 id 指标）；4) 风险与边界',
  '（阈值 0/16 calibrated，全部 DEFAULT_UNCALIBRATED；L3/L4/L5 判断不承诺）。',
  '只输出方案正文（Markdown），不要客套。',
].join('');

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
    const term = pty.spawn(process.env.ComSpec || 'powershell.exe', [], {
      name: 'xterm-256color',
      cwd: fs.existsSync(cwd) ? cwd : CASES_ROOT,
      env: { ...process.env, PYTHONUTF8: '1' },
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

// ——— Claude Code plan generation: one-shot, streamed, saved into the case ———

let claudeChild = null;

function registerClaudeIpc() {
  ipcMain.handle('claude:generate', async (event, caseDir) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    if (claudeChild) return { started: false, reason: '已有一次生成在进行' };
    const claudeCmd = process.env.MOODIFY_CLAUDE || 'claude';
    const child = spawn(claudeCmd, [
      '-p', PLAN_PROMPT, '--allowedTools', 'Read,Glob,Grep', '--output-format', 'text',
    ], { cwd: fs.existsSync(caseDir) ? caseDir : CASES_ROOT, env: process.env, shell: true });
    claudeChild = child;
    let planText = '';
    let errText = '';
    child.stdout.on('data', (d) => {
      const text = d.toString('utf8');
      planText += text;
      if (!win.isDestroyed()) win.webContents.send('claude:chunk', text);
    });
    // stderr is CLI noise (e.g. model warnings) — only surface it on failure
    child.stderr.on('data', (d) => { errText += d.toString('utf8'); });
    child.on('error', (err) => {
      if (!win.isDestroyed()) win.webContents.send('claude:chunk', `\r\n[claude 启动失败] ${err.message}\r\n`);
      claudeChild = null;
    });
    child.on('close', (code) => {
      if (code !== 0 && errText.trim() && !win.isDestroyed()) {
        win.webContents.send('claude:chunk', `\r\n[claude stderr]\r\n${errText.trim().slice(-800)}\r\n`);
      }
      let savedPath = null;
      if (code === 0 && planText.trim() && fs.existsSync(caseDir)) {
        try {
          savedPath = path.join(caseDir, 'plan_claude.md');
          fs.writeFileSync(savedPath, planText, 'utf8');
        } catch { /* archive dir may be read-only; the text is still in the pane */ }
      }
      if (!win.isDestroyed()) win.webContents.send('claude:done', code, savedPath);
      claudeChild = null;
    });
    return { started: true };
  });
  ipcMain.handle('claude:stop', async () => {
    if (claudeChild) {
      try { claudeChild.kill(); } catch { /* already gone */ }
      claudeChild = null;
      return true;
    }
    return false;
  });
}

function registerIpc() {
  registerTerminalIpc();
  registerClaudeIpc();
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
    return lastJsonLine(result.stdout);
  });
  ipcMain.handle('charts:render', async (_event, reportPath) => {
    const result = await runPython([
      '-m', 'moodify.ui.chart_export', reportPath, '--out', path.join(path.dirname(reportPath), 'charts'),
    ]);
    if (result.code !== 0) {
      throw new Error(result.stderr.trim().slice(-500) || 'chart export failed');
    }
    return lastJsonLine(result.stdout);
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
