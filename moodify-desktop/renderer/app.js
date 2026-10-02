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
  wave: null,           // {lanes:[Float32Array(min,max)…], duration} peaks cache
};

const VIEWS = ['empty', 'wave', 'charts', 'data'];
const VIEW_TAB = { wave: 'tab-wave', charts: 'tab-charts', data: 'tab-data' };

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
    setStatus('检测完成');
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
  $('tabs').hidden = name === 'empty';
  for (const [view, tabId] of Object.entries(VIEW_TAB)) {
    $(tabId).classList.toggle('active', view === name);
  }
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
  state.wave = null;

  const source = report.source || {};
  const technical = report.technical_state || {};
  const caseInfo = report.case || {};
  $('source-name').textContent = source.name || '?';
  $('report-meta').textContent = [
    `case ${caseInfo.case_id || '?'}`,
    report.protocol || '?',
    `${fmt(source.duration_s)}s`,
    `${fmt(source.channels)}ch @ ${fmt(source.sample_rate)}Hz`,
    `生成于 ${report.generated_at || '?'}`,
  ].join(' · ');
  $('badge-overall').textContent = technical.overall || '?';
  $('badge-decision').textContent = technical.workflow_decision || '?';
  $('badge-overall').hidden = false;
  $('badge-decision').hidden = false;
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
  selectView('wave'); // 落在波谱：音乐本身先行
  fitTerminalSoon();
  const entryDir = state.caseDir;
  const wave = renderWaveform(entryDir);   // 波形先行：解码完即有内容可看
  await renderSpectrum(entryDir);
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

const CHART_TITLES = {
  bands: ['频段能量占比（实测）', 'ratio（log 轴）'],
  levels_db: ['电平与响度（实测）', 'dB 域（LUFS/dBFS/dB/LU）'],
  stereo_ratios: ['立体声分布（实测）', 'ratio'],
};

/** 波谱页：音乐本身的声谱（扫描频谱渲染；波形 canvas 另由 renderWaveform 负责）。 */
async function renderSpectrum(caseDir) {
  const box = $('spectrum-body');
  box.textContent = '';
  const spectrum = ['spectrum_log.png', 'spectrum_linear.png']
    .map((name) => `${caseDir}/scan/${name}`);
  for (const src of spectrum) {
    if (await imageExists(src)) {
      box.appendChild(figure(src, '实测频谱渲染；不构成审美或平台适配判断'));
      break;
    }
  }
}

/** 图表页：检测产物（指标实测图）。 */
async function renderCharts(reportPath) {
  const box = $('charts-body');
  box.textContent = '';
  try {
    const payload = await window.moodify.renderCharts(reportPath);
    for (const [name, title] of Object.entries(CHART_TITLES)) {
      const png = payload.charts[name];
      if (png) box.appendChild(figure(png, title.join(' · ')));
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

function figure(pngPath, caption) {
  const fig = document.createElement('figure');
  const img = document.createElement('img');
  img.src = fileUrl(pngPath);
  const cap = document.createElement('figcaption');
  cap.textContent = caption;
  fig.appendChild(img);
  fig.appendChild(cap);
  return fig;
}

// ——— 波形（Audacity 式）：Web Audio 解码源音频 → 峰值包络 → canvas ———

const WAVE_PEAK_COLS = 2000;

async function renderWaveform(entryDir) {
  const wrap = $('wave-wrap');
  const src = await window.moodify.resolveSource(entryDir);
  if (!src || state.caseDir !== entryDir) { wrap.hidden = true; return; }
  wrap.hidden = false;
  try {
    const bytes = await window.moodify.readAudio(src);
    const ab = bytes instanceof ArrayBuffer ? bytes
      : bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    const ctx = new AudioContext();
    const audio = await ctx.decodeAudioData(ab);
    await ctx.close();
    if (state.caseDir !== entryDir) return; // world switched mid-decode
    state.wave = buildWavePeaks(audio);
    $('wave-caption').textContent =
      `${src.split(/[\\/]/).pop()} · ${audio.numberOfChannels}ch @ ${audio.sampleRate}Hz`
      + ` · ${audio.duration.toFixed(1)}s`;
    drawWaveform();
  } catch { wrap.hidden = true; } // 波形是增益，不是依赖：失败静默降级为图表
}

function buildWavePeaks(audio) {
  const cols = WAVE_PEAK_COLS;
  const lanes = [];
  for (let ch = 0; ch < Math.min(audio.numberOfChannels, 2); ch++) {
    const data = audio.getChannelData(ch);
    const lane = new Float32Array(cols * 2);
    const step = data.length / cols;
    for (let c = 0; c < cols; c++) {
      const start = Math.floor(c * step);
      const end = Math.min(Math.floor((c + 1) * step), data.length);
      let min = 1.0, max = -1.0;
      for (let i = start; i < end; i++) {
        if (data[i] < min) min = data[i];
        if (data[i] > max) max = data[i];
      }
      lane[c * 2] = min > max ? 0 : min;
      lane[c * 2 + 1] = min > max ? 0 : max;
    }
    lanes.push(lane);
  }
  return { lanes, duration: audio.duration };
}

function drawWaveform() {
  const canvas = $('waveform');
  const wrap = $('wave-wrap');
  if (!state.wave || wrap.hidden) return;
  const { lanes, duration } = state.wave;
  const dpr = window.devicePixelRatio || 1;
  const cssW = Math.max(400, wrap.clientWidth);
  const laneH = 64, gap = 6, rulerH = 18;
  const cssH = laneH * lanes.length + gap * (lanes.length - 1) + rulerH;
  canvas.style.width = '100%';
  canvas.style.height = `${cssH}px`;
  canvas.width = Math.round(cssW * dpr);
  canvas.height = Math.round(cssH * dpr);
  const g = canvas.getContext('2d');
  g.scale(dpr, dpr);
  const cols = lanes[0].length / 2;
  const half = laneH / 2 - 2;
  lanes.forEach((lane, ch) => {
    const y0 = ch * (laneH + gap);
    const mid = y0 + laneH / 2;
    g.fillStyle = '#f6f7ff';
    g.fillRect(0, y0, cssW, laneH);
    g.strokeStyle = '#e5e7eb';
    g.strokeRect(0.5, y0 + 0.5, cssW - 1, laneH - 1);
    g.strokeStyle = '#d1d5db';
    g.beginPath(); g.moveTo(0, mid); g.lineTo(cssW, mid); g.stroke();
    g.fillStyle = 'rgba(79, 70, 229, 0.78)';
    for (let x = 0; x < cssW; x++) {
      const c = Math.min(cols - 1, Math.floor((x / cssW) * cols));
      const yMax = mid + lane[c * 2 + 1] * half;
      const yMin = mid + lane[c * 2] * half;
      g.fillRect(x, yMax, 1, Math.max(1, yMin - yMax));
    }
    g.fillStyle = '#9ca3af';
    g.font = '10px "Segoe UI", sans-serif';
    g.fillText(ch === 0 ? 'L' : 'R', 4, y0 + 11);
  });
  // time ruler（诚实时间轴）
  const steps = [1, 2, 5, 10, 15, 30, 60, 120, 300];
  const stepSize = steps.find((s) => duration / s <= 10) || 600;
  g.font = '10px "Segoe UI", sans-serif';
  for (let t = 0; t <= duration; t += stepSize) {
    const x = (t / duration) * cssW;
    g.strokeStyle = '#f3f4f6';
    g.beginPath(); g.moveTo(x, 0); g.lineTo(x, cssH - rulerH); g.stroke();
    g.fillStyle = '#9ca3af';
    const m = Math.floor(t / 60);
    const s = Math.round(t % 60);
    g.fillText(`${m}:${String(s).padStart(2, '0')}`, x + 2, cssH - 5);
  }
}

function renderPlan(report) {
  const plan = report.plan || {};
  const findings = report.findings || [];
  const body = $('plan-body');
  body.textContent = '';

  const status = document.createElement('h3');
  status.textContent = `状态：${plan.status || '?'}`;
  body.appendChild(status);

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
  if (!(plan.nodes || []).length) {
    const none = document.createElement('p');
    none.className = 'muted';
    none.textContent = '无自动算子建议（未发现可安全映射到标准算子的发现）。';
    body.appendChild(none);
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

const PLAN_PROMPT = [
  '请读取当前目录下的 report.json、measurements.json、judgment_rules.json，基于 L1 技术测量给出',
  '【修音与混音方案】：1) 目标（可测量）；2) 逐步算子建议（算子/参数/理由，映射到标准算子',
  ' gain/eq/limiter/compressor/stereo 等）；3) 验收指标（使用 report.json 中同 id 指标）；',
  '4) 风险与边界（阈值 0/16 calibrated，全部 DEFAULT_UNCALIBRATED）。只输出方案正文（Markdown）。',
].join('');

const compiler = {
  ready: false,
  threadId: null,
  threadCwd: null,
  busy: false,
  currentAssistantEl: null,
  lastAssistantText: '',
};

function showDockStream() {
  $('compiler-stream').hidden = false;
  $('dock-bar').hidden = false;
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
  const worldOpen = Boolean(state.caseDir);
  $('compiler-plan-btn').disabled = busy || !worldOpen;
  $('compiler-send').disabled = busy || !worldOpen;
  $('compiler-input').disabled = busy || !worldOpen;
}

/** 意图命令条入口：惰性开线程，回答与操作都发生在 dock 里。 */
async function intentSend(text) {
  if (!text.trim() || !state.caseDir || compiler.busy) return;
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
  if (!res.ok) {
    $('compiler-setup').hidden = false;
    status.textContent = `内核启动失败：${res.reason}`;
    return false;
  }
  if (!res.provider) {
    $('compiler-setup').hidden = false;
    status.textContent = '首次使用：选择模型提供方并粘贴 API Key（仅存本机 ~/.moodify/codex）。';
    return false;
  }
  $('compiler-setup').hidden = true;
  compiler.ready = true;
  const ws = res.windowsSandbox ? res.windowsSandbox.status : 'unknown';
  $('compiler-subtitle').textContent =
    `Codex 内核 · ${res.provider.model || res.provider.kind} · Windows 沙箱：${ws}`
    + (ws === 'ready' ? ' · 边界：workspace-write + 命令审批' : ' · 边界降级为 read-only（诚实显示）');
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

async function sendPlanRequest() {
  await intentSend(PLAN_PROMPT);
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
  $('tab-wave').addEventListener('click', () => {
    if (!state.caseDir) return;
    selectView('wave');
    drawWaveform(); // 隐藏期间 clientWidth 归零过，重画一次
  });
  $('tab-charts').addEventListener('click', () => { if (state.caseDir) selectView('charts'); });
  $('tab-data').addEventListener('click', () => { if (state.caseDir) selectView('data'); });
  window.addEventListener('resize', drawWaveform);
  $('refresh').addEventListener('click', refreshArchive);
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
  $('compiler-plan-btn').addEventListener('click', sendPlanRequest);
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
