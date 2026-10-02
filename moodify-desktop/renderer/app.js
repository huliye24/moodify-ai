/**
 * Moodify desktop shell — renderer. Vanilla DOM, no frameworks: the product
 * is one shell with a fixed flow (pick a song → detect → data & charts →
 * plan). All measurement truth comes from the core's report.json; nothing
 * is recomputed or re-judged here.
 */

const $ = (id) => document.getElementById(id);
const state = { reportPath: null, elapsedTimer: null };

function fileUrl(p) {
  return 'file:///' + encodeURI(String(p).replace(/\\/g, '/'));
}

function fmt(value) {
  if (typeof value === 'number') return String(parseFloat(value.toPrecision(5)));
  return value === null || value === undefined ? '—' : String(value);
}

// ——— hub ———

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
    td.textContent = '档案为空——打开一首歌开始检测';
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

function setStatus(text) {
  $('status-line').textContent = text;
}

async function pickAndAnalyze() {
  const audioPath = await window.moodify.pickAudio();
  if (!audioPath) return;
  const button = $('open-audio');
  button.disabled = true;
  const startedAt = Date.now();
  clearInterval(state.elapsedTimer);
  state.elapsedTimer = setInterval(() => {
    setStatus(`检测中：${audioPath.split(/[\\/]/).pop()} …（${Math.round((Date.now() - startedAt) / 1000)}s，完整测量链路）`);
  }, 500);
  setStatus(`检测中：${audioPath.split(/[\\/]/).pop()} …（完整测量链路，约几十秒到几分钟）`);
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
  const hub = $('hub-view');
  let box = $('error-box');
  if (!box) {
    box = document.createElement('div');
    box.id = 'error-box';
    box.className = 'error';
    hub.appendChild(box);
  }
  box.textContent = message;
  setTimeout(() => box.remove(), 12000);
}

// ——— report view ———

async function openReport(reportPath) {
  let report;
  try {
    report = await window.moodify.readReport(reportPath);
  } catch (err) {
    showError(`无法打开档案：${err.message || err}`);
    return;
  }
  state.reportPath = reportPath;
  $('hub-view').hidden = true;
  $('report-view').hidden = false;

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

  renderMeasurements(report.measurements || []);
  renderPlan(report);
  selectTab('data');
  await renderCharts(reportPath, report);
}

function renderMeasurements(measurements) {
  const body = $('measure-body');
  body.textContent = '';
  for (const m of measurements) {
    const tr = document.createElement('tr');
    for (const key of ['id', 'value', 'unit', 'status', 'group']) {
      const td = document.createElement('td');
      td.textContent = key === 'value' ? fmt(m[key]) : fmt(m[key]);
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

// ——— navigation ———

function selectTab(name) {
  for (const tab of document.querySelectorAll('.tab')) {
    tab.classList.toggle('active', tab.dataset.tab === name);
  }
  for (const panel of document.querySelectorAll('.tab-panel')) {
    panel.hidden = panel.id !== `tab-${name}`;
  }
}

function backToArchive() {
  $('report-view').hidden = true;
  $('hub-view').hidden = false;
  setStatus('空闲 — 选择一首歌开始检测');
}

// ——— boot ———

window.addEventListener('DOMContentLoaded', async () => {
  const env = await window.moodify.env();
  $('archive-path').textContent = `档案目录：${env.casesRoot}`;
  if (!env.coreReady) {
    setStatus('核心不可用 — 请先安装 moodify 包（pip install -e moodify-core-package）');
  }
  $('open-audio').addEventListener('click', pickAndAnalyze);
  $('refresh').addEventListener('click', refreshArchive);
  $('back-archive').addEventListener('click', backToArchive);
  for (const tab of document.querySelectorAll('.tab')) {
    tab.addEventListener('click', () => selectTab(tab.dataset.tab));
  }
  await refreshArchive();
});
