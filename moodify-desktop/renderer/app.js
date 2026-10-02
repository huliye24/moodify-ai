/**
 * Moodify Studio — renderer. Vanilla DOM, no frameworks: an IDE-style shell
 * (icon rail + central workspace + terminal drawer) around the fixed product
 * flow: pick a song → detect → data & charts → plan. All measurement truth
 * comes from the core's report.json; the plan is authored by Claude Code.
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
  planRunning: false,
  drawerCollapsed: false,
};

const VIEWS = ['empty', 'data', 'charts', 'plan'];

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
  $('rail-compiler').classList.toggle('active', name === 'plan');
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

  $('plan-output').hidden = true;
  $('plan-output').textContent = '';
  $('plan-saved').hidden = true;

  $('rail-compiler').disabled = false;
  toggleHistoryPanel(false);
  renderMeasurements(report.measurements || []);
  renderPlan(report);
  selectView('data');
  fitTerminalSoon();
  await renderCharts(reportPath, report);
  await ensureTerminal();
}

function closeCase() {
  state.reportPath = null;
  state.caseDir = null;
  $('case-title').hidden = true;
  $('badge-overall').hidden = true;
  $('badge-decision').hidden = true;
  $('rail-compiler').disabled = true;
  $('rail-compiler').classList.remove('active');
  selectView('empty');
  setStatus('');
  // fresh terminal for whatever comes next (cwd follows the case)
  if (state.term) {
    window.moodify.termKill(state.termId);
    state.term.dispose();
    state.term = null;
    state.fit = null;
    state.termId = null;
    state.termCwd = undefined;
  }
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

async function renderCharts(reportPath, report) {
  const box = $('charts-body');
  box.textContent = '';
  const caseDir = reportPath.replace(/[\\/]report\.json$/, '');
  const spectrum = ['spectrum_log.png', 'spectrum_linear.png']
    .map((name) => `${caseDir}/scan/${name}`);
  for (const src of spectrum) {
    if (await imageExists(src)) {
      box.appendChild(figure(src, '实测频谱渲染；不构成审美或平台适配判断'));
      break;
    }
  }
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
  if (state.drawerCollapsed) return;
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

function setDrawerCollapsed(collapsed) {
  state.drawerCollapsed = collapsed;
  $('drawer').classList.toggle('collapsed', collapsed);
  $('drawer-toggle').textContent = collapsed ? '▴' : '▾';
  if (!collapsed) ensureTerminal();
}

function initDrawer() {
  $('drawer-toggle').addEventListener('click', () => setDrawerCollapsed(!state.drawerCollapsed));
  const bar = $('drawer-bar');
  bar.addEventListener('dblclick', (e) => {
    if (e.target.closest('button')) return;
    setDrawerCollapsed(!state.drawerCollapsed);
  });
  // drag the bar up/down to resize; buttons keep their click behavior
  let startY = 0, startH = 0, dragging = false;
  bar.addEventListener('mousedown', (e) => {
    if (e.target.closest('button') || state.drawerCollapsed) return;
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

function launchClaudeInTerminal() {
  setDrawerCollapsed(false);
  // give a freshly spawned shell a moment before typing into it
  setTimeout(() => {
    if (state.termId) window.moodify.termRunCommand(state.termId, 'claude');
  }, 600);
}

window.moodify.onPtyData((termId, data) => {
  if (state.term && termId === state.termId) state.term.write(data);
});
window.moodify.onPtyExit((termId) => {
  if (state.term && termId === state.termId) {
    state.term.write('\r\n\x1b[90m[进程已退出]\x1b[0m\r\n');
  }
});

// ——— Mood 编译器（plan generation; claude CLI kernel, direct API later）———

async function generatePlan() {
  if (state.planRunning || !state.caseDir) return;
  state.planRunning = true;
  const output = $('plan-output');
  output.hidden = false;
  output.textContent = '';
  $('plan-saved').hidden = true;
  $('generate-plan').disabled = true;
  $('stop-plan').hidden = false;
  try {
    const started = await window.moodify.generatePlan(state.caseDir);
    if (started && started.started === false) {
      state.planRunning = false;
      $('generate-plan').disabled = false;
      $('stop-plan').hidden = true;
      setStatus(started.reason || '未能启动生成');
    }
  } catch (err) {
    state.planRunning = false;
    $('generate-plan').disabled = false;
    $('stop-plan').hidden = true;
    output.textContent += `\n[启动失败] ${err.message || err}\n`;
  }
}

window.moodify.onPlanChunk((text) => {
  const output = $('plan-output');
  output.textContent += text;
  output.scrollTop = output.scrollHeight;
});

window.moodify.onPlanDone((code, savedPath) => {
  state.planRunning = false;
  $('generate-plan').disabled = false;
  $('stop-plan').hidden = true;
  const saved = $('plan-saved');
  if (code === 0 && savedPath) {
    saved.textContent = `已保存：${savedPath}`;
    saved.hidden = false;
  } else if (code !== 0) {
    saved.textContent = `生成未完成（退出码 ${code}）——可在终端手动运行 claude 继续。`;
    saved.hidden = false;
  }
});

// ——— boot ———

window.addEventListener('DOMContentLoaded', async () => {
  const env = await window.moodify.env();
  $('archive-path').textContent = env.casesRoot;
  if (!env.coreReady) {
    setStatus('核心不可用 — 请先安装 moodify 包（pip install -e moodify-core-package）');
  }

  $('rail-open').addEventListener('click', pickAndAnalyze);
  $('rail-history').addEventListener('click', () => toggleHistoryPanel());
  $('rail-compiler').addEventListener('click', () => {
    if (state.caseDir) selectView('plan');
  });
  $('close-case').addEventListener('click', closeCase);
  $('refresh').addEventListener('click', refreshArchive);
  $('generate-plan').addEventListener('click', generatePlan);
  $('stop-plan').addEventListener('click', () => window.moodify.stopPlan());
  $('launch-claude').addEventListener('click', launchClaudeInTerminal);
  initDrawer();
  initDrop();
  if (!state.drawerCollapsed) ensureTerminal();
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
