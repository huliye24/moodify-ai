/**
 * Moodify Studio — preload bridge.
 * Exposes exactly the product flow: pick a song, run detection, read the
 * report, render its charts, open a terminal in the case directory, and
 * talk to the Mood 编译器 (Codex app-server kernel). No node APIs reach
 * the renderer.
 */

const { contextBridge, ipcRenderer, webUtils } = require('electron');

contextBridge.exposeInMainWorld('moodify', {
  env: () => ipcRenderer.invoke('env'),
  pickAudio: () => ipcRenderer.invoke('pick-audio'),
  // drag-drop: Electron 32+ removed File.path — resolve via webUtils
  pathForFile: (file) => {
    try { return webUtils.getPathForFile(file); } catch { return file && file.path ? file.path : null; }
  },
  listArchive: () => ipcRenderer.invoke('archive:list'),
  runAnalysis: (audioPath) => ipcRenderer.invoke('analysis:run', audioPath),
  readReport: (reportPath) => ipcRenderer.invoke('report:read', reportPath),
  renderCharts: (reportPath) => ipcRenderer.invoke('charts:render', reportPath),
  // waveform: resolve the source audio of a case and read its bytes
  resolveSource: (caseDir) => ipcRenderer.invoke('source:resolve', caseDir),
  readAudio: (audioPath) => ipcRenderer.invoke('audio:read', audioPath),

  // embedded terminal (node-pty)
  createTerminal: (termId, cwd) => ipcRenderer.invoke('pty:create', termId, cwd),
  termWrite: (termId, data) => ipcRenderer.invoke('pty:write', termId, data),
  termResize: (termId, cols, rows) => ipcRenderer.invoke('pty:resize', termId, cols, rows),
  termKill: (termId) => ipcRenderer.invoke('pty:kill', termId),
  termRunCommand: (termId, command) => ipcRenderer.invoke('pty:run-command', termId, command),
  onPtyData: (cb) => ipcRenderer.on('pty:data', (_e, termId, data) => cb(termId, data)),
  onPtyExit: (cb) => ipcRenderer.on('pty:exit', (_e, termId, code) => cb(termId, code)),

  // Mood 编译器 (Codex app-server kernel)
  codexEnsure: () => ipcRenderer.invoke('codex:ensure'),
  codexProviderGet: () => ipcRenderer.invoke('codex:provider:get'),
  codexProviderSet: (provider) => ipcRenderer.invoke('codex:provider:set', provider),
  codexThreadOpen: (caseDir) => ipcRenderer.invoke('codex:thread-open', caseDir),
  codexSend: (threadId, text) => ipcRenderer.invoke('codex:send', threadId, text),
  codexInterrupt: (threadId) => ipcRenderer.invoke('codex:interrupt', threadId),
  codexRespond: (requestId, result) => ipcRenderer.invoke('codex:respond', requestId, result),
  codexSavePlan: (caseDir, text) => ipcRenderer.invoke('codex:save-plan', caseDir, text),
  onCodexEvent: (cb) => ipcRenderer.on('codex:event', (_e, notification) => cb(notification)),
  onCodexServerRequest: (cb) => ipcRenderer.on('codex:server-request', (_e, request) => cb(request)),
  // 权限模式：standard（审批）| full（全开，畅通无阻）
  permissionGet: () => ipcRenderer.invoke('codex:permission:get'),
  permissionSet: (value) => ipcRenderer.invoke('codex:permission:set', value),

  // 分离 / MIDI / 曲谱：显式动作，产物落世界目录
  listCaseFiles: (caseDir, subdir, exts) => ipcRenderer.invoke('casefiles:list', caseDir, subdir, exts),
  stemsRun: (caseDir) => ipcRenderer.invoke('stems:run', caseDir),
  midiRun: (caseDir, audioPath) => ipcRenderer.invoke('midi:run', caseDir, audioPath),
  scoreRun: (caseDir, midiPath) => ipcRenderer.invoke('score:run', caseDir, midiPath),
  readText: (caseDir, filePath) => ipcRenderer.invoke('text:read', caseDir, filePath),
  onToolProgress: (cb) => ipcRenderer.on('tool:progress', (_e, kind, line) => cb(kind, line)),
});
