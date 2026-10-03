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

  // 研究侧账本（T1 感知通道）：人类判断显式落账；默认关，不自动抓行为
  researchCase: (caseDir) => ipcRenderer.invoke('research:case', caseDir),
  researchPrefs: (patch) => ipcRenderer.invoke('research:prefs', patch),
  researchJudgment: (record) => ipcRenderer.invoke('research:judgment', record),

  // A/B 比较（Core CLI 权威）：读产物 / 准备 / 记录选择 / 取 A|B 试听音频。
  // prepare 与 choose 都走 `moodify compare`——GUI 与 AI 是同一条 CLI 路径。
  compareRead: (caseDir) => ipcRenderer.invoke('compare:read', caseDir),
  comparePrepare: (caseDir) => ipcRenderer.invoke('compare:prepare', caseDir),
  compareChoose: (caseDir, keep, role, requestId) =>
    ipcRenderer.invoke('compare:choose', caseDir, keep, role, requestId),
  compareAudio: (caseDir, side) => ipcRenderer.invoke('compare:audio', caseDir, side),
  // 修音渲染（后处理，接 core finishing）：产 B（源 vs 修音产物 中的 B），成功后自动落带 delta 的研究证据
  finishingRun: (caseDir, preset) => ipcRenderer.invoke('finishing:run', caseDir, preset),
  // 研究侧账本（T2 证据回流）：检测自动落账；渲染(W5)显式调用复用同一入口
  evidenceRecord: (caseDir, stage, sourceStatus) => ipcRenderer.invoke('evidence:record', caseDir, stage, sourceStatus),
  evidenceCount: () => ipcRenderer.invoke('evidence:count'),

  // Studio v0.2（产品书 2026-10-03）：选目标 → 一键让 AI 处理 → 试听选择 → 导出。
  // 后处理与导出都走 Core；渲染层只负责发起与呈现，不复制任何音频逻辑。
  studioTargets: () => ipcRenderer.invoke('studio:targets'),
  studioVersions: (caseDir) => ipcRenderer.invoke('studio:versions', caseDir),
  studioProcess: (caseDir, target, mode) => ipcRenderer.invoke('studio:process', caseDir, target, mode),
  studioEvidence: (caseDir, versionId) => ipcRenderer.invoke('studio:evidence', caseDir, versionId),
  studioSelect: (caseDir, versionId, note) => ipcRenderer.invoke('studio:select', caseDir, versionId, note),
  studioAudio: (caseDir, versionId) => ipcRenderer.invoke('studio:audio', caseDir, versionId),
  studioExport: (caseDir, versionId) => ipcRenderer.invoke('studio:export', caseDir, versionId),

  // 生产流程（TASK 002A）：检测 → 问题 → 分轨 → 结构 → 方案 → 成品。
  // 阶段由产物推导；诊断是 Core report.json 的投影；context 只引用已存在的产物。
  pipelineSnapshot: (caseDir) => ipcRenderer.invoke('pipeline:snapshot', caseDir),
  pipelineDiagnose: (caseDir) => ipcRenderer.invoke('pipeline:diagnose', caseDir),
  pipelineDiagnosis: (caseDir) => ipcRenderer.invoke('pipeline:diagnosis', caseDir),
  pipelineNote: (caseDir, note, preserve) => ipcRenderer.invoke('pipeline:note', caseDir, note, preserve),
  pipelineContext: (caseDir) => ipcRenderer.invoke('pipeline:context', caseDir),
  pipelineReadContext: (caseDir) => ipcRenderer.invoke('pipeline:readContext', caseDir),
  // 显式选择快速完成（仅立体声）。深度完成需要分轨 + 结构，跳过必须由人主动选。
  pipelineSetFinishMode: (caseDir, mode) => ipcRenderer.invoke('pipeline:setFinishMode', caseDir, mode),
});
