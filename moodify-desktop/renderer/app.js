/**
 * Moodify Studio — renderer (v0.2 World Loop). Vanilla DOM, no frameworks:
 * an IDE-style shell (icon rail + central workspace + intent dock) around a
 * creative loop: enter a world (song) once → observe charts → speak an
 * aesthetic intent → compile → (render, W5) → compare. Worlds never close —
 * they switch. The compiler is the only AI door; the terminal is engineering-
 * only. Measurement truth always comes from the core's report.json.
 */

const $ = (id) => document.getElementById(id);
const state = {
  reportPath: null,
  caseDir: null,
  elapsedTimer: null,
  term: null,        // xterm.Terminal
  fit: null,         // FitAddon
  termId: null,
  termCwd: undefined, // undefined = terminal never created
  drawerVisible: false, // engineering terminal stays hidden until asked for
  streamH: 200,         // 编译器对话抽屉高度（可拖动）
  streamOpen: false,    // 对话区是否展开
  streamUnread: false,  // 抽屉收起时有新内容待读
  convStarted: false,   // 本会话是否已开始 AI 对话（决定抽屉把手是否出现）
};

const VIEWS = ['empty', 'data', 'spectrum', 'charts', 'bench'];
const VIEW_TAB = {
  data: 'tab-data',
  spectrum: 'tab-spectrum',
  charts: 'tab-charts',
}; // bench 无顶层标签：观察（三页）与创造（工作台）按模式分开

function fileUrl(p) {
  return 'file:///' + encodeURI(String(p).replace(/\\/g, '/'));
}

function fmt(value) {
  if (typeof value === 'number') return String(parseFloat(value.toPrecision(5)));
  return value === null || value === undefined ? '—' : String(value);
}

function setStatus(text) {
  const el = $('status-line');
  el.textContent = text;
  el.hidden = !text;
}

// ——— history archive (left slide-out panel) ———

async function refreshArchive() {
  const rows = await window.moodify.listArchive();
  const body = $('archive-body');
  body.textContent = '';
  if (!rows.length) {
    const tr = document.createElement('tr');
    tr.className = 'static';
    const td = document.createElement('td');
    td.colSpan = 4;
    td.className = 'muted';
    td.textContent = '档案为空';
    tr.appendChild(td);
    body.appendChild(tr);
    return;
  }
  for (const row of rows) {
    const tr = document.createElement('tr');
    for (const key of ['sourceName', 'generatedAt', 'overall', 'workflowDecision']) {
      const td = document.createElement('td');
      td.textContent = row[key];
      tr.appendChild(td);
    }
    tr.addEventListener('dblclick', () => openReport(row.reportPath));
    body.appendChild(tr);
  }
}

function toggleHistoryPanel(force) {
  const panel = $('history-panel');
  const show = force !== undefined ? force : panel.hidden;
  panel.hidden = !show;
  $('rail-history').classList.toggle('active', show);
}

// ——— detection (fixed flow step 1→2) ———

async function pickAndAnalyze() {
  const audioPath = await window.moodify.pickAudio();
  if (audioPath) await runAnalysisPath(audioPath);
}

async function runAnalysisPath(audioPath) {
  const button = $('rail-open');
  button.disabled = true;
  const name = audioPath.split(/[\\/]/).pop();
  const startedAt = Date.now();
  clearInterval(state.elapsedTimer);
  state.elapsedTimer = setInterval(() => {
    setStatus(`检测中：${name} …（${Math.round((Date.now() - startedAt) / 1000)}s，完整测量链路）`);
  }, 500);
  setStatus(`检测中：${name} …（完整测量链路，约几十秒到几分钟）`);
  try {
    const result = await window.moodify.runAnalysis(audioPath);
    clearInterval(state.elapsedTimer);
    setStatus(''); // 检测完成直接出结果，不留状态文字
    await refreshArchive();
    await openReport(result.reports.json);
  } catch (err) {
    clearInterval(state.elapsedTimer);
    setStatus('检测失败');
    showError(err.message || String(err));
  } finally {
    button.disabled = false;
  }
}

function showError(message) {
  const ws = $('workspace');
  let box = $('error-box');
  if (!box) {
    box = document.createElement('div');
    box.id = 'error-box';
    box.className = 'error';
    ws.prepend(box);
  }
  box.textContent = message;
  setTimeout(() => box.remove(), 12000);
}

// ——— workspace views ———

function selectView(name) {
  for (const v of VIEWS) $(`view-${v}`).hidden = v !== name;
  $('tabs').hidden = name === 'empty' || name === 'bench';
  for (const [view, tabId] of Object.entries(VIEW_TAB)) {
    $(tabId).classList.toggle('active', view === name);
  }
  $('rail-fix').classList.toggle('active', name === 'bench');
}

async function openReport(reportPath) {
  let report;
  try {
    report = await window.moodify.readReport(reportPath);
  } catch (err) {
    showError(`无法打开档案：${err.message || err}`);
    return;
  }
  state.reportPath = reportPath;
  state.caseDir = reportPath.replace(/[\\/]report\.json$/, '');
  destroyBench(); // 换世界：旧工作台实例销毁

  $('source-name').textContent = (report.source || {}).name || '?';
  $('case-title').hidden = false;

  // stale compiler thread from another case is dropped; a fresh one opens on demand
  if (compiler.threadCwd !== state.caseDir) {
    compiler.threadId = null;
    compiler.threadCwd = null;
    $('compiler-stream').textContent = '';
    compiler.currentAssistantEl = null;
    compiler.lastAssistantText = '';
    $('compiler-save').hidden = true;
  }

  $('tabs').hidden = false;
  setCompilerBusy(compiler.busy); // intent bar unlocks with the world
  toggleHistoryPanel(false);
  renderMeasurements(report.measurements || []);
  renderPlan(report);
  selectView('data'); // 落在第一个标签页：数据
  fitTerminalSoon();
  const entryDir = state.caseDir;
  await renderSpectrum(entryDir);        // 本地 PNG 即刻顶格可见
  const wave = renderWaveform(entryDir); // 波形解码好后就地现身
  await wave;
  await renderCharts(reportPath); // 检测图表后台补齐（图表页）
  await ensureTerminal();
}

function renderMeasurements(measurements) {
  const body = $('measure-body');
  body.textContent = '';
  for (const m of measurements) {
    const tr = document.createElement('tr');
    for (const key of ['id', 'value', 'unit', 'status', 'group']) {
      const td = document.createElement('td');
      td.textContent = fmt(m[key]);
      tr.appendChild(td);
    }
    body.appendChild(tr);
  }
}

const CHART_KEYS = ['bands', 'levels_db', 'stereo_ratios'];

/** 频谱页：只放各种频谱图（log + linear）。 */
async function renderSpectrum(caseDir) {
  const box = $('spectrum-body');
  box.textContent = '';
  for (const name of ['spectrum_log.png', 'spectrum_linear.png']) {
    const src = `${caseDir}/scan/${name}`;
    if (await imageExists(src)) {
      const img = document.createElement('img');
      img.src = fileUrl(src);
      box.appendChild(img);
    }
  }
}

/** 图表页：检测产物图。 */
async function renderCharts(reportPath) {
  const box = $('charts-body');
  box.textContent = '';
  try {
    const payload = await window.moodify.renderCharts(reportPath);
    for (const key of CHART_KEYS) {
      const png = payload.charts[key];
      if (!png) continue;
      const img = document.createElement('img');
      img.src = fileUrl(png);
      box.appendChild(img);
    }
  } catch (err) {
    const p = document.createElement('p');
    p.className = 'muted';
    p.textContent = `图表生成跳过：${err.message || err}`;
    box.appendChild(p);
  }
}

function imageExists(src) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = src;
  });
}

// ——— 修音工作台波形：wavesurfer.js v6（BSD-3，vendor 内嵌）———
// 缩放 / 滚动 / 播放头 / 点击定位 / 精细时间标尺；L/R 分声道渲染。
// 统一轨道区：源轨 + W5 起叠加的版本轨，不再按修音/混音预分家。

let sourceWS = null;  // 源轨 WaveSurfer 实例
let zoomPx = null;    // 每秒像素；null = 适配全曲

async function renderWaveform(entryDir) {
  const src = await window.moodify.resolveSource(entryDir);
  if (!src || state.caseDir !== entryDir) return;
  try {
    const bytes = await window.moodify.readAudio(src);
    const ab = bytes instanceof ArrayBuffer ? bytes
      : bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    const ctx = new AudioContext();
    const audio = await ctx.decodeAudioData(ab);
    await ctx.close();
    if (state.caseDir !== entryDir) return; // world switched mid-decode
    $('source-meta').textContent =
      `${src.split(/[\\/]/).pop()} · ${audio.numberOfChannels}ch @ ${audio.sampleRate}Hz`
      + ` · ${audio.duration.toFixed(1)}s`;
    $('source-track').hidden = false;
    mountSourceWave(audio);
  } catch {
    // 轨道波形是增益，解码失败静默降级（数据/频谱/图表不受影响）
  }
}

function mountSourceWave(audioBuffer) {
  if (sourceWS) { try { sourceWS.destroy(); } catch { /* already gone */ } }
  sourceWS = WaveSurfer.create({
    container: $('wave-source'),
    backend: 'WebAudio',
    height: 60,
    splitChannels: true,
    responsive: true,
    scroll: true,
    waveColor: 'rgba(79, 70, 229, 0.38)',
    progressColor: 'rgba(79, 70, 229, 0.82)',
    cursorColor: '#16181d',
    cursorWidth: 1,
    plugins: [WaveSurfer.timeline.create({
      container: $('ruler-source'),
      fontSize: 10,
      primaryColor: '#d1d5db',
      secondaryColor: '#f3f4f6',
      primaryFontColor: '#9ca3af',
      secondaryFontColor: '#c7cbd1',
    })],
  });
  sourceWS.loadDecodedBuffer(audioBuffer);
}

function destroyBench() {
  if (sourceWS) { try { sourceWS.destroy(); } catch { /* already gone */ } }
  sourceWS = null;
  $('source-track').hidden = true;
  zoomPx = null;
}

function applyZoom() {
  const el = $('wave-source');
  if (!sourceWS || !el || el.clientWidth < 10) return; // 隐藏态宽度为 0
  const fitPx = el.clientWidth / (sourceWS.getDuration() || 1);
  sourceWS.zoom(Math.max(zoomPx || fitPx, fitPx));
}

function setZoom(factor) {
  const el = $('wave-source');
  if (!sourceWS || !el || el.clientWidth < 10) return;
  const fitPx = el.clientWidth / (sourceWS.getDuration() || 1);
  zoomPx = Math.min(800, Math.max(fitPx, (zoomPx || fitPx) * factor));
  applyZoom();
}

/** 修音工作台（图标栏第 2 位）：观察三页之外的创造模式。 */
function openBench() {
  if (!state.caseDir) return;
  selectView('bench');
  requestAnimationFrame(applyZoom); // 从隐藏态回来，宽度恢复后重画
}

function renderPlan(report) {
  const plan = report.plan || {};
  const findings = report.findings || [];
  const body = $('plan-body');
  body.textContent = '';

  if (findings.length) {
    const head = document.createElement('h3');
    head.textContent = '发现';
    body.appendChild(head);
    const ul = document.createElement('ul');
    for (const f of findings) {
      const li = document.createElement('li');
      li.textContent = `[${f.severity}] ${f.code}`
        + (f.calibration_status ? ` · 阈值 ${f.calibration_status}` : '')
        + ` — ${f.message || ''}`;
      ul.appendChild(li);
    }
    body.appendChild(ul);
  }

  for (const node of plan.nodes || []) {
    const div = document.createElement('div');
    div.className = 'node';
    const op = document.createElement('div');
    op.className = 'op';
    op.textContent = `◆ ${node.operator || '?'}`;
    const reason = document.createElement('p');
    reason.className = 'reason';
    reason.textContent = node.reason || '';
    div.appendChild(op);
    div.appendChild(reason);
    body.appendChild(div);
  }

  const notes = plan.notes || [];
  if (notes.length) {
    const head = document.createElement('h3');
    head.textContent = '注记';
    body.appendChild(head);
    const ul = document.createElement('ul');
    for (const n of notes) {
      const li = document.createElement('li');
      li.textContent = n;
      ul.appendChild(li);
    }
    body.appendChild(ul);
  }
}

// ——— terminal drawer (xterm.js + node-pty, cwd = case dir) ———

function ensureTerminal() {
  if (!state.drawerVisible) return;
  if (state.term && state.termCwd === state.caseDir) { fitTerminalSoon(); return; }
  if (state.term) {
    window.moodify.termKill(state.termId);
    state.term.dispose();
  }
  $('terminal').textContent = '';
  const term = new window.Terminal({
    fontSize: 13,
    fontFamily: 'Consolas, "Courier New", monospace',
    cursorBlink: true,
    theme: { background: '#ffffff', foreground: '#16181d', cursor: '#4f46e5' },
  });
  const fit = new window.FitAddon.FitAddon();
  term.loadAddon(fit);
  term.open($('terminal'));
  state.term = term;
  state.fit = fit;
  state.termId = `term-${Date.now()}`;
  state.termCwd = state.caseDir;
  term.onData((data) => window.moodify.termWrite(state.termId, data));
  term.onResize(({ cols, rows }) => window.moodify.termResize(state.termId, cols, rows));
  window.moodify.createTerminal(state.termId, state.caseDir);
  $('term-cwd').textContent = state.caseDir ? `目录：${state.caseDir}` : '目录：档案根';
  fitTerminalSoon();
}

function fitTerminalSoon() {
  requestAnimationFrame(() => {
    if (state.fit) { try { state.fit.fit(); } catch { /* not visible yet */ } }
  });
}

function setDrawerVisible(visible) {
  state.drawerVisible = visible;
  $('drawer').hidden = !visible;
  if (visible) ensureTerminal();
}

function initDrawer() {
  $('drawer-toggle').addEventListener('click', () => setDrawerVisible(false));
  $('drawer-toggle2').addEventListener('click', () => setDrawerVisible(!state.drawerVisible));
  const bar = $('drawer-bar');
  bar.addEventListener('dblclick', (e) => {
    if (e.target.closest('button')) return;
    setDrawerVisible(false);
  });
  // drag the bar up/down to resize; buttons keep their click behavior
  let startY = 0, startH = 0, dragging = false;
  bar.addEventListener('mousedown', (e) => {
    if (e.target.closest('button') || !state.drawerVisible) return;
    dragging = true;
    startY = e.clientY;
    startH = $('drawer').getBoundingClientRect().height;
    e.preventDefault();
  });
  window.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const h = Math.min(600, Math.max(90, startH + (startY - e.clientY)));
    $('drawer').style.height = `${h}px`;
    fitTerminalSoon();
  });
  window.addEventListener('mouseup', () => { dragging = false; });
  window.addEventListener('resize', fitTerminalSoon);
}

window.moodify.onPtyData((termId, data) => {
  if (state.term && termId === state.termId) state.term.write(data);
});
window.moodify.onPtyExit((termId) => {
  if (state.term && termId === state.termId) {
    state.term.write('\r\n\x1b[90m[进程已退出]\x1b[0m\r\n');
  }
});

// ——— Mood 编译器（Codex app-server kernel; claude channel fully replaced）———

const compiler = {
  ready: false,
  threadId: null,
  threadCwd: null,
  busy: false,
  currentAssistantEl: null,
  lastAssistantText: '',
};

/** 对话抽屉：平时只有输入框+发送；开始对话后抽屉出现（可拖动/可收起，收起后细条是把手）。 */
function openStream(height) {
  if (height) state.streamH = height;
  state.streamOpen = true;
  $('compiler-stream').hidden = false;
  $('compiler-stream').style.height = `${state.streamH}px`;
  $('stream-bar').hidden = false;
  state.streamUnread = false;
  updateStreamDot();
  $('compiler-stream').scrollTop = $('compiler-stream').scrollHeight;
}

function closeStream() {
  state.streamOpen = false;
  $('compiler-stream').hidden = true;
  // 细条保留为把手（对话已开始才有）；输入行常驻
  $('stream-bar').hidden = !state.convStarted;
  updateStreamDot();
}

function updateStreamDot() {
  // 抽屉收起时：有内容在产生或待读 → 把手上亮点提示
  $('stream-dot').hidden = state.streamOpen || !(compiler.busy || state.streamUnread);
}

function showDockStream() {
  if (!state.streamOpen) {
    state.streamUnread = true; // 有新内容但抽屉收着
  }
  updateStreamDot();
  const stream = $('compiler-stream');
  stream.scrollTop = stream.scrollHeight;
}

function initStreamBar() {
  const bar = $('stream-bar');
  let y0 = 0, h0 = 0, dragging = false;
  bar.addEventListener('mousedown', (e) => {
    if (e.target.closest('button')) return;
    dragging = true;
    y0 = e.clientY;
    h0 = state.streamOpen ? state.streamH : 0;
    e.preventDefault();
  });
  window.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const h = Math.min(Math.round(window.innerHeight * 0.6), Math.max(0, h0 + (y0 - e.clientY)));
    if (h < 60) {
      closeStream(); // 拖到底 = 收起对话区（输入行保留）
    } else {
      openStream(h);
    }
  });
  window.addEventListener('mouseup', () => { dragging = false; });
  bar.addEventListener('dblclick', (e) => {
    if (e.target.closest('button')) return;
    if (state.streamOpen) closeStream();
    else openStream();
  });
}

function compilerBubble(role, text) {
  showDockStream();
  const stream = $('compiler-stream');
  const div = document.createElement('div');
  div.className = `cmsg ${role}`;
  const body = document.createElement('div');
  body.className = 'cmsg-text';
  body.textContent = text;
  div.appendChild(body);
  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
  return body;
}

function compilerLine(kind, text) {
  showDockStream();
  const stream = $('compiler-stream');
  const div = document.createElement('div');
  div.className = `cline ${kind}`;
  div.textContent = text;
  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
  return div;
}

function compilerNote(text) {
  const note = $('compiler-note');
  note.textContent = text;
  note.hidden = !text;
}

function setCompilerBusy(busy) {
  compiler.busy = busy;
  $('compiler-stop').hidden = !busy;
  updateStreamDot();
  $('compiler-send').disabled = busy;
  $('compiler-input').disabled = busy;
}

/** 意图命令条入口：惰性开线程，回答与操作都发生在 dock 里。首次发送弹出对话抽屉。 */
async function intentSend(text) {
  if (!text.trim() || compiler.busy) return;
  if (!state.caseDir) {
    compilerNote('先打开一个音频文件（左上角打开或拖入），创建世界后再对话。');
    return;
  }
  if (!state.convStarted) {
    state.convStarted = true;
    openStream(); // 开始 AI 对话：抽屉对话区从此出现
  }
  if (!compiler.ready) {
    const ok = await ensureCompiler();
    if (!ok) return;
  }
  if (!compiler.threadId || compiler.threadCwd !== state.caseDir) {
    compiler.busy = true; // gate re-entry while the thread opens (async)
    try { await openCompilerThread(); } finally { compiler.busy = false; }
    setCompilerBusy(false);
  }
  await compilerSend(text);
}

async function ensureCompiler() {
  const status = $('setup-status');
  const res = await window.moodify.codexEnsure();
  if (!res.ok || !res.provider) {
    // 设置卡在输入行上方原位显示（输入行常驻，不依赖抽屉开合）
    $('compiler-setup').hidden = false;
    status.textContent = !res.ok
      ? `内核启动失败：${res.reason}`
      : '首次使用：选择模型提供方并粘贴 API Key（仅存本机 ~/.moodify/codex）。';
    return false;
  }
  $('compiler-setup').hidden = true;
  compiler.ready = true;
  return true;
}

async function openCompilerThread() {
  if (!compiler.ready || !state.caseDir) return;
  const res = await window.moodify.codexThreadOpen(state.caseDir);
  if (res.ok) {
    compiler.threadId = res.thread.thread.id;
    compiler.threadCwd = state.caseDir;
    $('compiler-stream').textContent = '';
    compiler.currentAssistantEl = null;
    compiler.lastAssistantText = '';
    $('compiler-save').hidden = true;
    compilerNote('');
    setCompilerBusy(false);
    const effective = res.thread.sandbox && res.thread.sandbox.type ? res.thread.sandbox.type : 'unknown';
    compilerLine('sys', `线程就绪（cwd = ${state.caseDir}）· 生效沙箱：${effective}`);
  } else {
    compilerNote(`线程打开失败：${res.reason}`);
  }
}

async function compilerSend(text) {
  if (!compiler.threadId || compiler.busy || !text.trim()) return;
  compilerBubble('user', text);
  setCompilerBusy(true);
  compiler.currentAssistantEl = null;
  const res = await window.moodify.codexSend(compiler.threadId, text);
  if (!res.ok) {
    compilerNote(`发送失败：${res.reason}`);
    setCompilerBusy(false);
  }
}

async function savePlan() {
  if (!compiler.lastAssistantText || !state.caseDir) return;
  const saved = await window.moodify.codexSavePlan(state.caseDir, compiler.lastAssistantText);
  compilerNote(`已保存：${saved}`);
}

function handleCodexEvent(n) {
  switch (n.method) {
    case 'item/agentMessage/delta': {
      if (!compiler.currentAssistantEl) {
        compiler.currentAssistantEl = compilerBubble('assistant', '');
      }
      compiler.currentAssistantEl.textContent += n.params.delta;
      const stream = $('compiler-stream');
      stream.scrollTop = stream.scrollHeight;
      compiler.lastAssistantText = compiler.currentAssistantEl.textContent;
      $('compiler-save').hidden = false;
      break;
    }
    case 'item/started': {
      const item = n.params.item || {};
      if (item.type === 'commandExecution') {
        compilerLine('cmd', `◆ 命令（待运行）：${item.command}`);
      } else if (item.type === 'fileChange') {
        compilerLine('cmd', '◆ 文件修改（待批准）');
      }
      break;
    }
    case 'item/completed': {
      const item = n.params.item || {};
      if (item.type === 'agentMessage') {
        compiler.currentAssistantEl = null;
        compiler.lastAssistantText = item.text || '';
        if (compiler.lastAssistantText) $('compiler-save').hidden = false;
      } else if (item.type === 'commandExecution') {
        compilerLine('cmd', `◆ 命令完成（exit ${item.exitCode ?? '?'}）：${item.command}`);
      } else if (item.type === 'fileChange') {
        compilerLine('cmd', `◆ 文件修改完成：${Object.keys(item.changes || {}).join(', ')}`);
      }
      break;
    }
    case 'turn/completed': {
      setCompilerBusy(false);
      compiler.currentAssistantEl = null;
      break;
    }
    case 'error':
      compilerNote(`错误：${(n.params && n.params.message) || ''}`);
      setCompilerBusy(false);
      break;
    case 'warning':
      compilerNote(`警告：${(n.params && n.params.message) || ''}`);
      break;
    default:
      break;
  }
}

function handleCodexServerRequest(req) {
  const p = req.params || {};
  if ($('compiler-stream').hidden) openStream(); // 审批卡必须可见可操作
  const stream = $('compiler-stream');
  const card = document.createElement('div');
  card.className = 'approval';
  const label = document.createElement('div');
  label.className = 'approval-title';
  if (req.method === 'item/commandExecution/requestApproval' || req.method === 'execCommandApproval') {
    label.textContent = `命令审批：${p.command || '?'}`;
  } else if (req.method === 'item/fileChange/requestApproval' || req.method === 'applyPatchApproval') {
    label.textContent = `文件修改审批：${p.reason || p.grantRoot || ''}`;
  } else {
    label.textContent = `审批请求：${req.method}`;
  }
  card.appendChild(label);
  const actions = document.createElement('div');
  actions.className = 'approval-actions';
  const mk = (text, decision) => {
    const b = document.createElement('button');
    b.textContent = text;
    b.className = decision === 'decline' ? 'ghost' : 'primary';
    b.addEventListener('click', async () => {
      await window.moodify.codexRespond(req.id, { decision });
      card.remove();
    });
    return b;
  };
  actions.appendChild(mk('批准', 'accept'));
  actions.appendChild(mk('本次会话批准', 'acceptForSession'));
  actions.appendChild(mk('拒绝', 'decline'));
  card.appendChild(actions);
  stream.appendChild(card);
  stream.scrollTop = stream.scrollHeight;
}

function initCompilerSetup() {
  const kindSel = $('setup-kind');
  kindSel.addEventListener('change', () => {
    $('setup-baseurl').hidden = kindSel.value !== 'custom';
    $('setup-model').placeholder = kindSel.value === 'deepseek' ? 'deepseek-v4-pro'
      : kindSel.value === 'openai' ? 'gpt-5.1-codex' : 'model-name';
  });
  $('setup-save').addEventListener('click', async () => {
    const status = $('setup-status');
    const kind = kindSel.value;
    const model = $('setup-model').value.trim()
      || (kind === 'deepseek' ? 'deepseek-v4-pro' : kind === 'openai' ? 'gpt-5.1-codex' : '');
    const apiKey = $('setup-key').value.trim();
    if (!apiKey && kind !== 'openai') { status.textContent = '请粘贴 API Key。'; return; }
    status.textContent = '保存中…';
    await window.moodify.codexProviderSet({
      kind, model, apiKey, baseUrl: $('setup-baseurl').value.trim(),
    });
    const ok = await ensureCompiler();
    if (ok) await openCompilerThread();
  });
}

// ——— boot ———

window.addEventListener('DOMContentLoaded', async () => {
  const env = await window.moodify.env();
  $('archive-path').textContent = env.casesRoot;
  if (!env.coreReady) {
    setStatus('核心不可用 — 请先安装 moodify 包（pip install -e moodify-core-package）');
  }

  $('rail-open').addEventListener('click', pickAndAnalyze);
  $('rail-history').addEventListener('click', () => toggleHistoryPanel());
  $('tab-data').addEventListener('click', () => { if (state.caseDir) selectView('data'); });
  $('tab-spectrum').addEventListener('click', () => { if (state.caseDir) selectView('spectrum'); });
  $('tab-charts').addEventListener('click', () => { if (state.caseDir) selectView('charts'); });
  $('rail-fix').addEventListener('click', openBench);
  $('zoom-in').addEventListener('click', () => setZoom(1.5));
  $('zoom-out').addEventListener('click', () => setZoom(1 / 1.5));
  $('zoom-fit').addEventListener('click', () => { zoomPx = null; applyZoom(); });
  initStreamBar();
  const sendIntent = () => {
    const text = $('compiler-input').value;
    $('compiler-input').value = '';
    $('compiler-input').style.height = '';
    intentSend(text);
  };
  $('compiler-send').addEventListener('click', sendIntent);
  $('compiler-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendIntent();
    }
  });
  $('compiler-input').addEventListener('input', (e) => {
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = `${Math.min(96, el.scrollHeight)}px`;
  });
  $('compiler-stop').addEventListener('click', () => window.moodify.codexInterrupt(compiler.threadId));
  $('compiler-save').addEventListener('click', savePlan);
  window.moodify.onCodexEvent(handleCodexEvent);
  window.moodify.onCodexServerRequest(handleCodexServerRequest);
  initCompilerSetup();
  initDrawer();
  initDrop();
  await ensureCompiler();
  await refreshArchive();
});

// ——— drag & drop audio onto the workspace ———

function initDrop() {
  const ws = $('workspace');
  ws.addEventListener('dragover', (e) => {
    e.preventDefault();
    ws.classList.add('drop-target');
  });
  ws.addEventListener('dragleave', () => ws.classList.remove('drop-target'));
  ws.addEventListener('drop', async (e) => {
    e.preventDefault();
    ws.classList.remove('drop-target');
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (!file) return;
    const p = await window.moodify.pathForFile(file);
    if (p) await runAnalysisPath(p);
  });
}
