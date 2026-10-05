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
  updateStatus: () => ipcRenderer.invoke('update:status'),
  updateCheck: () => ipcRenderer.invoke('update:check'),
  updateAction: (action) => ipcRenderer.invoke('update:action', action),
  onUpdateStatus: (cb) => ipcRenderer.on('update:status', (_e, payload) => cb(payload)),
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

  // 逆向分解 / 结构 / 可逆性：显式动作，产物落世界目录
  listCaseFiles: (caseDir, subdir, exts) => ipcRenderer.invoke('casefiles:list', caseDir, subdir, exts),
  // mode: 'auto'（默认，模型优先）| 'model'（Demucs 母带级）| 'dsp'（快速，秒级预览级）
  stemsRun: (caseDir, mode) => ipcRenderer.invoke('stems:run', caseDir, mode),
  // 可逆性验证：分轨相加回原版 → studio/roundtrip.json（④ 修音 的门禁）
  stemsRoundtrip: (caseDir) => ipcRenderer.invoke('stems:roundtrip', caseDir),
  // 分离引擎偏好；缺模型运行时时不会被替用户改选，只如实报缺
  stemsEngineGet: () => ipcRenderer.invoke('stems:engine:get'),
  stemsEngineSet: (engine) => ipcRenderer.invoke('stems:engine:set', engine),
  // 结构事实：速度 / 拍点 / 段落边界 → studio/structure.json
  structureAnalyze: (caseDir) => ipcRenderer.invoke('structure:analyze', caseDir),
  // 能力体检：哪些外部运行时可用、缺哪个、怎么装。UI 据此说明「为什么这一步走不通」。
  capabilitiesProbe: () => ipcRenderer.invoke('capabilities:probe'),
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
  // 修音渲染（研究仪器，**非产品面**）：产「源(A) vs 修音产物(B)」中的 B，成功后自动落带 delta 的
  // 研究证据。三预设作为产品面已于 2026-10-04 退场；此入口只服务研究侧 A/B 证据采集，
  // 待 Core 的 tuning render 就绪后删除（见 MIP-0002）。
  finishingRun: (caseDir, preset) => ipcRenderer.invoke('finishing:run', caseDir, preset),
  // 研究侧账本（T2 证据回流）：检测自动落账；渲染(W5)显式调用复用同一入口
  evidenceRecord: (caseDir, stage, sourceStatus) => ipcRenderer.invoke('evidence:record', caseDir, stage, sourceStatus),
  evidenceCount: () => ipcRenderer.invoke('evidence:count'),

  // ④ 修音 / ⑤ 复合 / ⑦ 选定（V4）。
  // 两档完整方案由系统产出；选定有**三个**出口 A / B / 保留原版。
  // Core 能力未就绪时 tuningRender 显式拒绝（TUNABLE_CORE_NOT_AVAILABLE），绝不留假产物。
  tuningPairs: (caseDir) => ipcRenderer.invoke('tuning:pairs', caseDir),
  tuningRender: (caseDir) => ipcRenderer.invoke('tuning:render', caseDir),
  tuningDecision: (caseDir, pairId, kept, role, requestId) =>
    ipcRenderer.invoke('tuning:decision', caseDir, pairId, kept, role, requestId),
  tuningAudio: (caseDir, pairId, side) => ipcRenderer.invoke('tuning:audio', caseDir, pairId, side),
  tuningRecheck: (caseDir, pairId) => ipcRenderer.invoke('tuning:recheck', caseDir, pairId),
  tuningRecheckRun: (caseDir, pairId) => ipcRenderer.invoke('tuning:recheckRun', caseDir, pairId),
  tuningExport: (caseDir, pairId, kept) => ipcRenderer.invoke('tuning:export', caseDir, pairId, kept),
  // A/B 审听工作台（Phase 2.2）：只读证据包 + 按侧生成的检测图表。
  // 路径全部由 main 侧从 recheck / pair 产物推导并守卫；渲染层递不了任意绝对路径。
  tuningEvidence: (caseDir, pairId) => ipcRenderer.invoke('tuning:evidence', caseDir, pairId),
  tuningCharts: (caseDir, pairId, side) => ipcRenderer.invoke('tuning:charts', caseDir, pairId, side),

  // 完成时刻的留存（Phase 2.3）。keepsake 是**表现层留存记录**，不是完成状态权威：
  // 完成与否由 pipeline 产物 + ⑦ 准入推导；这里只读写「选了哪一版、一句话、波形印记」。
  keepsakeState: (caseDir) => ipcRenderer.invoke('keepsake:state', caseDir),
  keepsakeSync: (caseDir) => ipcRenderer.invoke('keepsake:sync', caseDir),
  keepsakeInscription: (caseDir, text) => ipcRenderer.invoke('keepsake:inscription', caseDir, text),
  keepsakeImprint: (caseDir, values) => ipcRenderer.invoke('keepsake:imprint', caseDir, values),
  // 唯一把作品卡写出 case 之外的地方，且必须是显式动作（用户在保存对话框里确认）
  keepsakeSaveCard: (caseDir, bytes) => ipcRenderer.invoke('keepsake:saveCard', caseDir, bytes),

  // 完成会话（「一键完成机」）：放入一首歌 → 一次启动 → 内部自动执行 → 原版/A/B → 选定 → 导出。
  // 「一键」只简化操作，不省略内部步骤；缺能力时停在真实阻断态，不生成假产物。
  sessionView: (caseDir) => ipcRenderer.invoke('session:view', caseDir),
  sessionStart: (caseDir) => ipcRenderer.invoke('session:start', caseDir),
  onSessionProgress: (cb) => ipcRenderer.on('session:progress', (_e, payload) => cb(payload)),

  // 生产流程（V4）：检测 → 逆向分解 → 结构 → 修音 → 复合 → 复检 → 选定 → 导出。
  // 阶段由产物推导；context 只引用已存在的产物；preserve 由人填。
  pipelineSnapshot: (caseDir) => ipcRenderer.invoke('pipeline:snapshot', caseDir),
  pipelineContext: (caseDir) => ipcRenderer.invoke('pipeline:context', caseDir),
  pipelineReadContext: (caseDir) => ipcRenderer.invoke('pipeline:readContext', caseDir),
  // 显式选择快速完成（仅立体声）。深度路径需要 分轨 + MIDI + 可逆性通过，跳过必须由人主动选。
  pipelineSetFinishMode: (caseDir, mode) => ipcRenderer.invoke('pipeline:setFinishMode', caseDir, mode),
});
