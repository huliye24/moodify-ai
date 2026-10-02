/**
 * Moodify desktop shell — Electron main process.
 *
 * Product definition (human, 2026-10-02): ONE shell, white, company logo,
 * fixed flow: pick a song → detect → data & charts → repair/mixing plan.
 * This shell orchestrates the pip-installed core; it never reimplements
 * measurement or judgment. Every python invocation sets PYTHONUTF8=1 —
 * the GBK console trap is a product-killing bug on Chinese Windows.
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

function registerIpc() {
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
  if (process.platform !== 'darwin') app.quit();
});
