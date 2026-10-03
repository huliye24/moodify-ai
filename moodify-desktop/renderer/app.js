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

const VIEWS = ['empty', 'data', 'spectrum', 'charts', 'bench', 'stems', 'score'];
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
  $('tabs').hidden = name === 'empty' || name === 'bench' || name === 'stems' || name === 'score';
  for (const [view, tabId] of Object.entries(VIEW_TAB)) {
    $(tabId).classList.toggle('active', view === name);
  }
  $('rail-fix').classList.toggle('active', name === 'bench');
  $('rail-stems').classList.toggle('active', name === 'stems');
  $('rail-score').classList.toggle('active', name === 'score');
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
  resetStudioTools(); // 换世界：分离/曲谱工作台复位（产物留在旧世界目录）

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
  setCompilerBusy(compiler.busy); // 同步禁用态（输入行从不因无世界而锁）
  toggleHistoryPanel(false);
  renderMeasurements(report.measurements || []);
  renderPlan(report);
  selectView('data'); // 落在第一个标签页：数据
  if (!$('research-panel').hidden) loadResearchCase(); // 研究面板开着则随世界刷新 A/B
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
    $('source-track').hidden = false;
    mountSourceWave(audio);
  } catch {
    // 轨道波形是增益，解码失败静默降级（数据/频谱/图表不受影响）
  }
}

function fmtTime(t) {
  const m = Math.floor(t / 60);
  const s = t - m * 60;
  return `${m}:${s < 10 ? '0' : ''}${s.toFixed(1)}`;
}

function mountSourceWave(audioBuffer) {
  if (sourceWS) { try { sourceWS.destroy(); } catch { /* already gone */ } }
  sourceWS = WaveSurfer.create({
    container: $('wave-source'),
    backend: 'WebAudio',
    height: 96,
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
  $('bench-time').textContent = `0:00.0 / ${fmtTime(audioBuffer.duration)}`;
  sourceWS.on('timeupdate', (t) => {
    if (sourceWS) $('bench-time').textContent = `${fmtTime(t)} / ${fmtTime(sourceWS.getDuration() || 0)}`;
  });
  sourceWS.on('play', () => { $('bench-play').textContent = '⏸'; });
  sourceWS.on('pause', () => { $('bench-play').textContent = '▶'; });
  sourceWS.on('finish', () => { $('bench-play').textContent = '▶'; });
  sourceWS.loadDecodedBuffer(audioBuffer);
}

function destroyBench() {
  if (sourceWS) { try { sourceWS.destroy(); } catch { /* already gone */ } }
  sourceWS = null;
  $('source-track').hidden = true;
  $('bench-time').textContent = '0:00.0';
  $('bench-play').textContent = '▶';
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

// ——— 分离工作台（图标栏第 4 位）：引擎 A=DSP 快速分离；模型精分离后续接入 ———

const STEM_LABELS = {
  vocals: '人声（中置估计）',
  instrumental: '伴奏（源 − 中置）',
  harmonic: '谐波（持续音）',
  percussive: '打击（瞬态）',
};
const stemWS = []; // 分离轨 WaveSurfer 实例（与 #stems-tracks 子行同序）

function destroyStemWaves() {
  for (const ws of stemWS) { try { ws.destroy(); } catch { /* already gone */ } }
  stemWS.length = 0;
}

async function openStems() {
  if (!state.caseDir) return;
  selectView('stems');
  destroyStemWaves();
  const box = $('stems-tracks');
  box.textContent = '';
  let stems = [];
  try { stems = await window.moodify.listCaseFiles(state.caseDir, 'stems', ['.wav']); } catch { /* empty */ }
  if (!stems.length) return;

  const caseDir = state.caseDir; // 异步解码期间换世界的守卫
  for (const stem of stems) {
    const row = document.createElement('div');
    row.className = 'track stem-row';
    const strip = document.createElement('div');
    strip.className = 'track-strip';
    const head = document.createElement('div');
    head.className = 'stem-head';
    const label = STEM_LABELS[stemBase(stem.name)] || stem.name;
    head.innerHTML = `<span class="stem-name"></span>`
      + `<button class="ghost stem-play" title="试听">▶</button>`;
    head.querySelector('.stem-name').textContent = label;
    const wave = document.createElement('div');
    wave.className = 'ws-wave stem-wave';
    strip.appendChild(head);
    strip.appendChild(wave);
    row.appendChild(strip);
    box.appendChild(row);

    // 惰性解码：点试听才载入波形（省内存，换轨互斥）
    const btn = head.querySelector('.stem-play');
    btn.addEventListener('click', async () => {
      if (btn.dataset.playing === '1') { stopStemWaves(); return; }
      stopStemWaves();
      if (state.caseDir !== caseDir) return;
      try {
        const bytes = await window.moodify.readAudio(stem.path);
        const ab = bytes instanceof ArrayBuffer ? bytes
          : bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
        const ctx = new AudioContext();
        const audio = await ctx.decodeAudioData(ab);
        await ctx.close();
        if (state.caseDir !== caseDir) return;
        const ws = WaveSurfer.create({
          container: wave,
          backend: 'WebAudio',
          height: 56,
          waveColor: 'rgba(79, 70, 229, 0.38)',
          progressColor: 'rgba(79, 70, 229, 0.82)',
          cursorColor: '#16181d',
          cursorWidth: 1,
        });
        ws.on('finish', () => { btn.textContent = '▶'; btn.dataset.playing = '0'; });
        ws.loadDecodedBuffer(audio);
        ws.play();
        btn.textContent = '⏸';
        btn.dataset.playing = '1';
        stemWS.push(ws);
      } catch { btn.textContent = '▶'; btn.dataset.playing = '0'; }
    });
  }
}

function stemBase(name) {
  const m = name.match(/__(vocals|instrumental|harmonic|percussive)\.wav$/i);
  return m ? m[1].toLowerCase() : name;
}

function stopStemWaves() {
  for (const ws of stemWS) { try { ws.pause(); } catch { /* already gone */ } }
  document.querySelectorAll('#stems-tracks .stem-play').forEach((b) => {
    b.textContent = '▶';
    b.dataset.playing = '0';
  });
}

async function runStems() {
  if (!state.caseDir) return;
  const btn = $('stems-run');
  btn.disabled = true;
  showToolProgress('stems', '分离中…');
  try {
    const res = await window.moodify.stemsRun(state.caseDir);
    if (!res.ok) showToolProgress('stems', `分离失败（code ${res.code ?? '?'} ${res.reason || ''}）`);
    else showToolProgress('stems', '完成。');
    await openStems(); // 重扫产物入列
  } catch (err) {
    showToolProgress('stems', `分离失败：${err.message || err}`);
  } finally {
    btn.disabled = false;
  }
}

// ——— 曲谱工作台（图标栏第 5 位）：音频 → MIDI → MusicXML → 壳内渲染 ———
// 世界里已有的产物（case/midi + case/score）进入即直接打开，无需重转；
// 转换一键成链：音频 → MIDI（basic-pitch）→ MusicXML（music21）→ 双栏渲染。

let scoreProducts = [];   // [{mid, xml, mtime}]，mid/xml = {name, path, size, mtime}|null
let scoreCurrent = null;
let scoreOsmd = null;
let scoreZoom = 0.85;
let scoreConverting = false;

const stripExt = (name) => name.replace(/\.(mid|midi|musicxml|xml)$/i, '');

function setSelectOptions(sel, items, emptyLabel) {
  sel.textContent = '';
  if (!items.length) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = emptyLabel;
    sel.appendChild(opt);
    return;
  }
  for (const it of items) {
    const opt = document.createElement('option');
    opt.value = it.path;
    opt.textContent = it.label;
    sel.appendChild(opt);
  }
}

async function refreshScoreSelects() {
  if (!state.caseDir) return;
  const stems = await window.moodify
    .listCaseFiles(state.caseDir, 'stems', ['.wav']).catch(() => []);
  const src = await window.moodify.resolveSource(state.caseDir);
  const audioItems = [];
  if (src) audioItems.push({ path: src, label: `源：${src.split(/[\\/]/).pop()}` });
  for (const s of stems) audioItems.push({ path: s.path, label: s.name });
  setSelectOptions($('score-audio'), audioItems, '（先分离或打开世界）');
}

async function openScore() {
  if (!state.caseDir) return;
  selectView('score');
  await refreshScoreSelects();
  await loadScoreProducts();
  requestAnimationFrame(requestRollDraw);
}

/** 扫描世界产物：MIDI × MusicXML 同名配对，新者优先；已有产物直接打开。 */
async function loadScoreProducts(focusPath) {
  const caseDir = state.caseDir;
  if (!caseDir) return;
  const [mids, xmls] = await Promise.all([
    window.moodify.listCaseFiles(caseDir, 'midi', ['.mid', '.midi']).catch(() => []),
    window.moodify.listCaseFiles(caseDir, 'score', ['.musicxml', '.xml']).catch(() => []),
  ]);
  if (state.caseDir !== caseDir) return; // 换世界守卫
  scoreProducts = mids.map((m) => ({
    mid: m,
    xml: xmls.find((x) => stripExt(x.name) === stripExt(m.name)) || null,
    mtime: m.mtime || 0,
  })).sort((a, b) => b.mtime - a.mtime);
  for (const x of xmls) {
    if (!scoreProducts.some((p) => p.xml && p.xml.path === x.path)) {
      scoreProducts.push({ mid: null, xml: x, mtime: x.mtime || 0 });
    }
  }
  const product = focusPath
    ? scoreProducts.find((p) => (p.mid && p.mid.path === focusPath)
      || (p.xml && p.xml.path === focusPath)) || scoreProducts[0]
    : scoreProducts[0];
  await loadScoreProduct(product || null);
}

/** 产物徽标 + 切换器 + 转换按钮语义（缺曲谱 = 补曲谱；齐了 = 全链重转）。 */
function renderScoreChrome() {
  const wrap = $('score-products');
  wrap.textContent = '';
  const chip = (ok, label) => {
    const span = document.createElement('span');
    span.className = `pill${ok ? ' ok' : ''}`;
    span.textContent = `${label} ${ok ? '✓' : '—'}`;
    wrap.appendChild(span);
  };
  chip(scoreProducts.some((p) => p.mid), 'MIDI');
  chip(scoreProducts.some((p) => p.xml), '曲谱');
  const sel = $('score-product');
  if (scoreProducts.length > 1) {
    sel.hidden = false;
    setSelectOptions(sel, scoreProducts.map((p, i) => ({
      path: String(i),
      label: p.mid ? p.mid.name : stripExt(p.xml.name),
    })), '');
    if (scoreCurrent) sel.value = String(scoreProducts.indexOf(scoreCurrent));
  } else {
    sel.hidden = true;
  }
  const incomplete = scoreProducts.find((p) => p.mid && !p.xml);
  const btn = $('score-convert');
  btn.textContent = incomplete ? '生成曲谱' : '音频转曲谱';
  btn.title = incomplete
    ? '为已有 MIDI 生成 MusicXML 曲谱'
    : '音频 → MIDI → 曲谱 一键完成（已有产物会被重新转换覆盖）';
}

async function loadScoreProduct(p) {
  stopRollPlayback();
  rollPlayState.t = 0;
  $('roll-time').textContent = '0:00.0';
  scoreCurrent = p || null;
  const split = $('score-split');
  const empty = $('score-empty');
  const sheet = $('score-sheet');
  if (!p) {
    split.hidden = true;
    empty.hidden = false;
    sheet.textContent = '';
    rollClear();
    rollMsg('');
    renderScoreChrome();
    return;
  }
  empty.hidden = true;
  split.hidden = false;
  if (p.xml) {
    await renderScoreSheet(p.xml.path);
  } else {
    sheet.textContent = '';
    sheetHint('MIDI 已有，曲谱尚未生成 — 点上方「生成曲谱」补齐。');
  }
  if (p.mid) await loadRoll(p.mid.path);
  else { rollClear(); rollMsg('该曲谱没有配对的 MIDI 文件，卷帘不可用。'); }
  // 转换源预选：MIDI 名去掉 _basic_pitch ↔ 源音频名
  if (p.mid) {
    const base = stripExt(p.mid.name).replace(/_basic_pitch$/i, '');
    const sel = $('score-audio');
    for (const opt of sel.options) {
      const name = opt.textContent.replace(/^源：/, '');
      if (name.replace(/\.[^.]+$/, '') === base) { sel.value = opt.value; break; }
    }
  }
  renderScoreChrome();
}

function sheetHint(text) {
  const p = document.createElement('p');
  p.className = 'muted pane-hint';
  p.textContent = text;
  $('score-sheet').appendChild(p);
}

async function renderScoreSheet(xmlPath) {
  const sheet = $('score-sheet');
  sheet.textContent = '';
  try {
    const xml = await window.moodify.readText(state.caseDir, xmlPath);
    if (!scoreOsmd) {
      scoreOsmd = new opensheetmusicdisplay.OpenSheetMusicDisplay(sheet, {
        drawTitle: false,
        drawComposer: false,
        drawCredits: false,
        drawSubtitle: false,
        autoResize: false,
      });
    }
    await scoreOsmd.load(xml);
    scoreOsmd.zoom = scoreZoom;
    scoreOsmd.render();
  } catch (err) {
    sheet.textContent = '';
    sheetHint(`曲谱打开失败：${err.message || err}`);
  }
}

function setScoreZoom(z) {
  scoreZoom = Math.min(1.8, Math.max(0.5, z));
  if (scoreOsmd && scoreCurrent && scoreCurrent.xml) {
    scoreOsmd.zoom = scoreZoom;
    scoreOsmd.render();
  }
}

/** 一键转换链。状态决定行为：缺曲谱 → 只补 MusicXML；否则全链（音频→MIDI→曲谱）。 */
async function convertChain() {
  if (!state.caseDir || scoreConverting) return;
  scoreConverting = true;
  const btn = $('score-convert');
  btn.disabled = true;
  const caseDir = state.caseDir;
  try {
    if (!scoreProducts.some((p) => p.mid && !p.xml)) {
      const audioPath = $('score-audio').value;
      if (!audioPath) { showToolProgress('score', '先在上方选择音频（源或分离轨）。'); return; }
      showToolProgress('midi', '转 MIDI 中（basic-pitch）…');
      const r1 = await window.moodify.midiRun(caseDir, audioPath);
      if (state.caseDir !== caseDir) return;
      if (!r1.ok) { showToolProgress('midi', `转 MIDI 失败（${r1.reason || `code ${r1.code}`}）`); return; }
      showToolProgress('midi', 'MIDI 完成，转曲谱中（music21）…');
      await loadScoreProducts(r1.midi);
    } else {
      showToolProgress('score', 'MusicXML 转换中（music21）…');
    }
    const target = (scoreCurrent && scoreCurrent.mid && !scoreCurrent.xml)
      ? scoreCurrent
      : scoreProducts.find((p) => p.mid && !p.xml);
    if (!target || !target.mid) {
      showToolProgress('score', '曲谱完成。');
      hideScoreProgressSoon();
      return;
    }
    const r2 = await window.moodify.scoreRun(caseDir, target.mid.path);
    if (state.caseDir !== caseDir) return;
    if (!r2.ok) { showToolProgress('score', `曲谱失败（${r2.reason || `code ${r2.code}`}）`); return; }
    showToolProgress('score', '曲谱完成。');
    hideScoreProgressSoon();
    await loadScoreProducts(r2.musicxml);
  } catch (err) {
    showToolProgress('score', `转换失败：${err.message || err}`);
  } finally {
    scoreConverting = false;
    btn.disabled = false;
  }
}

// ——— MIDI 钢琴卷帘：壳内解析（零依赖）+ canvas 渲染 + 预览合成器 ———
// 键盘列 / 小节线 / 播放头 / 悬停音符信息；拖动平移，Ctrl+滚轮缩放，空格播放。

const roll = {
  notes: [],   // {pitch, vel, ch, trk, start, dur}，按 start 升序
  bars: [],    // 小节线时刻（秒）
  duration: 0,
  minPitch: 48,
  maxPitch: 84,
  zoomPps: null, // 每秒像素；null = 适配全曲
  effPps: null,  // 实际生效值（fit 为下限）
  scrollX: 0,
  hover: null,
  hoverPos: null,
  rafPending: false,
};
const rollPlayState = {
  on: false, t: 0, ctx: null, master: null, sources: new Set(),
  raf: 0, nextIdx: 0, startT: 0, t0: 0,
};
const ROLL_KEY_W = 46;
const ROLL_RULER_H = 20;
const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const pitchName = (p) => `${NOTE_NAMES[p % 12]}${Math.floor(p / 12) - 1}`;
const pitchFreq = (p) => 440 * Math.pow(2, (p - 69) / 12);

function rollAudioCtx() {
  if (!rollPlayState.ctx) rollPlayState.ctx = new AudioContext();
  if (rollPlayState.ctx.state === 'suspended') rollPlayState.ctx.resume();
  return rollPlayState.ctx;
}

/** 标准 MIDI 文件解析：多轨 / running status / tempo 表 / 拍号，只取卷帘所需。 */
function parseMidi(data) {
  const u8 = data instanceof Uint8Array ? data : new Uint8Array(data);
  let p = 0;
  const byte = () => u8[p++];
  const u16 = () => (u8[p++] << 8) | u8[p++];
  const u32 = () => ((u8[p++] << 24) | (u8[p++] << 16) | (u8[p++] << 8) | u8[p++]) >>> 0;
  const vlq = () => { let v = 0, b; do { b = byte(); v = (v << 7) | (b & 0x7f); } while (b & 0x80); return v; };
  const tag = () => { const s = String.fromCharCode(u8[p], u8[p + 1], u8[p + 2], u8[p + 3]); p += 4; return s; };

  if (tag() !== 'MThd') throw new Error('不是标准 MIDI 文件');
  const hlen = u32();
  u16(); // format
  u16(); // 轨道数
  const division = u16(); // ticks per quarter（或 SMPTE 负数）
  p += hlen - 6;

  const smpte = Boolean(division & 0x8000);
  const tpq = smpte ? 480 : (division || 480);
  const notes = [];
  const tempos = []; // {tick, uspq}
  let timeSig = null;
  let maxTick = 0;
  let trackIndex = 0;

  while (p + 8 <= u8.length) {
    const id = tag();
    const len = u32();
    const end = p + len;
    if (id !== 'MTrk' || end > u8.length) break;
    let tick = 0;
    let running = 0;
    const active = new Map(); // ch:pitch → 起音
    while (p < end) {
      tick += vlq();
      let status = u8[p];
      if (status < 0x80) status = running; // running status
      else p++;
      if (status < 0x80) break; // 坏数据：止损本轨
      if (status < 0xf0) running = status;
      const type = status & 0xf0;
      if (type === 0x90 || type === 0x80) {
        const pitch = byte();
        const vel = byte();
        const key = `${status & 0x0f}:${pitch}`;
        if (type === 0x90 && vel > 0) {
          active.set(key, { pitch, vel, ch: status & 0x0f, trk: trackIndex, startTick: tick });
        } else {
          const n = active.get(key);
          if (n) {
            active.delete(key);
            notes.push({ ...n, durTick: Math.max(1, tick - n.startTick) });
          }
        }
      } else if (type === 0xa0 || type === 0xb0 || type === 0xe0) p += 2;
      else if (type === 0xc0 || type === 0xd0) p += 1;
      else if (status === 0xff) {
        const meta = byte();
        const mlen = vlq();
        const q = p;
        if (meta === 0x51 && mlen === 3) {
          tempos.push({ tick, uspq: (u8[q] << 16) | (u8[q + 1] << 8) | u8[q + 2] });
        } else if (meta === 0x58 && mlen >= 2) {
          timeSig = { num: u8[q], den: 1 << u8[q + 1] };
        }
        p = q + mlen;
      } else if (status === 0xf0 || status === 0xf7) {
        // 注意：p += vlq() 会先捕获旧 p（复合赋值求值顺序）再被 vlq 推进，导致少跳
        const sysexLen = vlq();
        p += sysexLen;
      }
      maxTick = Math.max(maxTick, tick);
    }
    for (const n of active.values()) { // 没等到 note-off 的音按轨尾闭合
      notes.push({ ...n, durTick: Math.max(1, maxTick - n.startTick) });
    }
    p = end;
    trackIndex++;
  }
  if (!notes.length) throw new Error('MIDI 里没有音符');

  // tick → 秒：SMPTE 直接除；tempo 表分段积分
  let tickToSec;
  if (smpte) {
    const spt = 1 / ((256 - (division >> 8)) * (division & 0xff));
    tickToSec = (t) => t * spt;
  } else {
    tempos.sort((a, b) => a.tick - b.tick);
    if (!tempos.length || tempos[0].tick > 0) tempos.unshift({ tick: 0, uspq: 500000 });
    const anchors = []; // {tick, sec, uspq}：uspq 为该锚点之后生效的速率
    let sec = 0;
    let lastTick = 0;
    let uspq = tempos[0].uspq;
    for (const t of tempos) {
      if (t.tick > 0) sec += ((t.tick - lastTick) * uspq) / (tpq * 1e6);
      lastTick = t.tick;
      uspq = t.uspq;
      anchors.push({ tick: t.tick, sec, uspq });
    }
    tickToSec = (tick) => {
      let a = anchors[0];
      for (const x of anchors) { if (x.tick <= tick) a = x; else break; }
      return a.sec + ((tick - a.tick) * a.uspq) / (tpq * 1e6);
    };
  }

  const bars = [];
  if (!smpte) {
    const num = timeSig ? timeSig.num : 4;
    const den = timeSig ? timeSig.den : 4;
    const barTicks = (num * 4 * tpq) / den;
    for (let t = 0; t <= maxTick + barTicks; t += barTicks) bars.push(tickToSec(t));
  }

  const out = notes.map((n) => {
    const start = tickToSec(n.startTick);
    return {
      pitch: n.pitch, vel: n.vel, ch: n.ch, trk: n.trk, start,
      dur: Math.max(0.03, tickToSec(n.startTick + n.durTick) - start),
    };
  }).sort((a, b) => a.start - b.start);
  const duration = out.reduce((m, n) => Math.max(m, n.start + n.dur), 0);
  return { notes: out, bars, duration };
}

async function loadRoll(midiPath) {
  const caseDir = state.caseDir;
  rollMsg('');
  try {
    const bytes = await window.moodify.readAudio(midiPath);
    if (state.caseDir !== caseDir) return;
    const ab = bytes instanceof ArrayBuffer ? bytes
      : bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    const parsed = parseMidi(new Uint8Array(ab));
    roll.notes = parsed.notes;
    roll.bars = parsed.bars;
    roll.duration = parsed.duration;
    let lo = roll.notes.reduce((m, n) => Math.min(m, n.pitch), 127);
    let hi = roll.notes.reduce((m, n) => Math.max(m, n.pitch), 0);
    lo = Math.max(21, lo - 2);
    hi = Math.min(108, hi + 2);
    while (hi - lo < 23) { lo = Math.max(21, lo - 1); hi = Math.min(108, hi + 1); }
    roll.minPitch = lo;
    roll.maxPitch = hi;
    roll.zoomPps = null;
    roll.scrollX = 0;
    roll.hover = null;
    requestRollDraw();
  } catch (err) {
    rollClear();
    rollMsg(`MIDI 解析失败：${err.message || err}`);
  }
}

function rollClear() {
  roll.notes = [];
  roll.bars = [];
  roll.duration = 0;
  roll.zoomPps = null;
  roll.effPps = null;
  roll.scrollX = 0;
  roll.hover = null;
  roll.hoverPos = null;
  requestRollDraw();
}

function rollMsg(text) {
  let hint = $('roll-hint');
  if (!text) { if (hint) hint.remove(); return; }
  if (!hint) {
    hint = document.createElement('p');
    hint.id = 'roll-hint';
    hint.className = 'muted pane-hint';
    $('roll-body').appendChild(hint);
  }
  hint.textContent = text;
}

function rollGeom() {
  const body = $('roll-body');
  const w = body.clientWidth;
  const h = body.clientHeight;
  const fitPps = (w - ROLL_KEY_W) / Math.max(roll.duration, 0.001);
  const pps = Math.max(roll.zoomPps || fitPps, fitPps);
  const rowH = Math.max(5, Math.floor((h - ROLL_RULER_H) / (roll.maxPitch - roll.minPitch + 1)));
  return { w, h, pps, rowH };
}

function requestRollDraw() {
  if (roll.rafPending) return;
  roll.rafPending = true;
  requestAnimationFrame(() => {
    roll.rafPending = false;
    drawRoll();
  });
}

function drawRoll() {
  const canvas = $('roll-canvas');
  const { w, h, pps, rowH } = rollGeom();
  if (!w || !h) return;
  roll.effPps = pps;
  const dpr = window.devicePixelRatio || 1;
  const bw = Math.round(w * dpr);
  const bh = Math.round(h * dpr);
  if (canvas.width !== bw || canvas.height !== bh) { canvas.width = bw; canvas.height = bh; }
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = '#fff';
  ctx.fillRect(0, 0, w, h);
  // 视窗滚动范围收口
  roll.scrollX = Math.min(roll.scrollX, Math.max(0, ROLL_KEY_W + roll.duration * pps - w));
  const yOf = (pitch) => ROLL_RULER_H + (roll.maxPitch - pitch) * rowH;

  // 标尺条（先画，小节序号落在其上）
  ctx.fillStyle = '#fff';
  ctx.fillRect(0, 0, w, ROLL_RULER_H);
  ctx.strokeStyle = '#e5e7eb';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(0, ROLL_RULER_H + 0.5);
  ctx.lineTo(w, ROLL_RULER_H + 0.5);
  ctx.stroke();

  // 横网格：每个八度（C 行上缘）一条淡线
  ctx.beginPath();
  ctx.strokeStyle = '#f1f3f5';
  for (let pitch = roll.maxPitch; pitch >= roll.minPitch; pitch--) {
    if (pitch % 12 === 0) {
      const y = Math.round(yOf(pitch)) + 0.5;
      ctx.moveTo(ROLL_KEY_W, y);
      ctx.lineTo(w, y);
    }
  }
  ctx.stroke();

  // 纵网格：小节线 + 序号（过密自动降频标注）
  if (roll.bars.length > 1) {
    const spacing = roll.bars[1] * pps;
    let step = 1;
    while (spacing * step < 64) step *= 2;
    ctx.font = '9px Consolas, monospace';
    ctx.fillStyle = '#9ca3af';
    ctx.beginPath();
    ctx.strokeStyle = '#eceef1';
    for (let i = 0; i < roll.bars.length; i += step) {
      const x = Math.round(ROLL_KEY_W + roll.bars[i] * pps - roll.scrollX) + 0.5;
      if (x < ROLL_KEY_W || x > w) continue;
      ctx.moveTo(x, ROLL_RULER_H);
      ctx.lineTo(x, h);
      if (i % 4 === 0) ctx.fillText(String(i + 1), x + 3, 12);
    }
    ctx.stroke();
  }

  // 音符（只画视窗内）
  const t0 = roll.scrollX / pps;
  const t1 = (roll.scrollX + w) / pps;
  const now = rollPlayState.on ? rollPlayState.t : -1;
  for (const n of roll.notes) {
    if (n.start > t1) break;
    if (n.start + n.dur < t0) continue;
    const x = ROLL_KEY_W + n.start * pps - roll.scrollX;
    const nw = Math.max(2.5, n.dur * pps - 1);
    const y = yOf(n.pitch) + 1;
    const nh = Math.max(2, rowH - 2);
    const live = now >= n.start && now <= n.start + n.dur;
    ctx.fillStyle = live
      ? '#312e81'
      : `rgba(79, 70, 229, ${(0.26 + 0.55 * (n.vel / 127)).toFixed(3)})`;
    ctx.beginPath();
    ctx.roundRect(x, y, nw, nh, 2);
    ctx.fill();
    if (n === roll.hover) {
      ctx.strokeStyle = '#312e81';
      ctx.lineWidth = 1.2;
      ctx.stroke();
    }
  }

  // 播放头（琥珀色 + 顶部小三角）
  if (rollPlayState.on || rollPlayState.t > 0) {
    const x = ROLL_KEY_W + rollPlayState.t * pps - roll.scrollX;
    if (x >= ROLL_KEY_W - 5 && x <= w + 1) {
      ctx.fillStyle = '#f59e0b';
      ctx.fillRect(x, ROLL_RULER_H, 1.5, h - ROLL_RULER_H);
      ctx.beginPath();
      ctx.moveTo(x - 4, ROLL_RULER_H);
      ctx.lineTo(x + 5, ROLL_RULER_H);
      ctx.lineTo(x + 0.5, ROLL_RULER_H + 6);
      ctx.closePath();
      ctx.fill();
    }
  }

  // 键盘列（最后画，盖住越界音符）
  ctx.fillStyle = '#fbfbfc';
  ctx.fillRect(0, ROLL_RULER_H, ROLL_KEY_W, h - ROLL_RULER_H);
  ctx.font = '9px Consolas, monospace';
  for (let pitch = roll.maxPitch; pitch >= roll.minPitch; pitch--) {
    const y = yOf(pitch);
    if ([1, 3, 6, 8, 10].includes(pitch % 12)) {
      ctx.fillStyle = '#4b5563';
      ctx.fillRect(ROLL_KEY_W - 24, y + 0.5, 22, Math.max(2, rowH - 1));
    } else if (pitch % 12 === 0) {
      ctx.fillStyle = '#9ca3af';
      ctx.fillText(`C${Math.floor(pitch / 12) - 1}`, 4, y + rowH - 2);
    }
  }

  // 悬停音符信息
  if (roll.hover && roll.hoverPos) {
    const n = roll.hover;
    const label = `${pitchName(n.pitch)}  ${fmtTime(n.start)} · ${n.dur.toFixed(2)}s · vel ${n.vel}`;
    ctx.font = '11px "Microsoft YaHei", sans-serif';
    const tw = ctx.measureText(label).width + 14;
    const tx = Math.min(roll.hoverPos.mx + 12, w - tw - 6);
    const ty = Math.min(roll.hoverPos.my + 14, h - 26);
    ctx.fillStyle = 'rgba(22, 24, 29, 0.88)';
    ctx.beginPath();
    ctx.roundRect(tx, ty, tw, 20, 5);
    ctx.fill();
    ctx.fillStyle = '#fff';
    ctx.fillText(label, tx + 7, ty + 14);
  }
}

function noteAt(mx, my) {
  const { w, pps, rowH } = rollGeom();
  if (!pps) return null;
  const yOf = (pitch) => ROLL_RULER_H + (roll.maxPitch - pitch) * rowH;
  const t0 = roll.scrollX / pps;
  const t1 = (roll.scrollX + w) / pps;
  for (const n of roll.notes) {
    if (n.start > t1) break;
    if (n.start + n.dur < t0) continue;
    const x = ROLL_KEY_W + n.start * pps - roll.scrollX;
    const nw = Math.max(2.5, n.dur * pps - 1);
    const y = yOf(n.pitch);
    if (mx >= x && mx <= x + nw && my >= y && my <= y + rowH) return n;
  }
  return null;
}

function setRollZoom(z, anchorSec) {
  const { pps } = rollGeom();
  const fitPps = roll.duration > 0
    ? ($('roll-body').clientWidth - ROLL_KEY_W) / roll.duration : 50;
  const next = Math.min(600, Math.max(fitPps, z || fitPps));
  if (anchorSec !== undefined && pps) {
    const ax = anchorSec * pps - roll.scrollX; // 锚点屏幕位置保持不动
    roll.scrollX = anchorSec * next - ax;
  }
  roll.zoomPps = next > fitPps + 0.01 ? next : null;
  requestRollDraw();
}

function centerSec() {
  const { w, pps } = rollGeom();
  return (roll.scrollX + (w - ROLL_KEY_W) / 2) / (pps || 1);
}

function initRollEvents() {
  const canvas = $('roll-canvas');
  const local = (e) => {
    const r = canvas.getBoundingClientRect();
    return { mx: e.clientX - r.left, my: e.clientY - r.top };
  };
  const timeAt = (mx) => (mx - ROLL_KEY_W + roll.scrollX) / (roll.effPps || 1);

  canvas.addEventListener('wheel', (e) => {
    if (!roll.notes.length) return;
    e.preventDefault();
    if (e.ctrlKey || e.metaKey) {
      const { mx } = local(e);
      setRollZoom((roll.zoomPps || roll.effPps || 100) * (e.deltaY < 0 ? 1.2 : 1 / 1.2), timeAt(mx));
    } else {
      roll.scrollX += Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
      requestRollDraw();
    }
  }, { passive: false });

  let drag = null;
  canvas.addEventListener('mousedown', (e) => {
    const { mx, my } = local(e);
    if (my <= ROLL_RULER_H && !rollPlayState.on) { // 标尺点击 = 定位播放头
      rollPlayState.t = Math.max(0, timeAt(mx));
      requestRollDraw();
      return;
    }
    drag = { x: e.clientX, scrollX: roll.scrollX, moved: false };
    canvas.classList.add('grabbing');
  });
  window.addEventListener('mousemove', (e) => {
    if (!drag) return;
    const dx = e.clientX - drag.x;
    if (Math.abs(dx) > 3) drag.moved = true;
    roll.scrollX = drag.scrollX - dx;
    requestRollDraw();
  });
  window.addEventListener('mouseup', (e) => {
    if (!drag) return;
    const d = drag;
    drag = null;
    canvas.classList.remove('grabbing');
    if (!d.moved && e.target === canvas) {
      const { mx, my } = local(e);
      const n = my > ROLL_RULER_H ? noteAt(mx, my) : null;
      if (n) previewNote(n); // 点音符 = 试听单音
    }
  });

  canvas.addEventListener('mousemove', (e) => {
    if (drag || !roll.notes.length) return;
    const { mx, my } = local(e);
    roll.hoverPos = { mx, my };
    roll.hover = my > ROLL_RULER_H ? noteAt(mx, my) : null;
    requestRollDraw();
  });
  canvas.addEventListener('mouseleave', () => {
    roll.hover = null;
    roll.hoverPos = null;
    requestRollDraw();
  });
}

function previewNote(n) {
  const ctx = rollAudioCtx();
  const osc = ctx.createOscillator();
  const g = ctx.createGain();
  osc.type = 'triangle';
  osc.frequency.value = pitchFreq(n.pitch);
  const t = ctx.currentTime;
  g.gain.setValueAtTime(0.0001, t);
  g.gain.linearRampToValueAtTime(0.1 + 0.3 * (n.vel / 127), t + 0.01);
  g.gain.exponentialRampToValueAtTime(0.0001, t + 0.3);
  osc.connect(g);
  g.connect(ctx.destination);
  osc.start(t);
  osc.stop(t + 0.32);
}

function rollToggle() {
  if (rollPlayState.on) stopRollPlayback();
  else startRollPlayback();
}

function startRollPlayback() {
  if (!roll.notes.length || !roll.duration) return;
  const ctx = rollAudioCtx();
  const st = rollPlayState;
  st.on = true;
  st.ctx = ctx;
  st.master = ctx.createGain();
  st.master.gain.value = 0.85;
  st.master.connect(ctx.destination);
  st.startT = Math.min(st.t, Math.max(0, roll.duration - 0.05));
  st.t0 = ctx.currentTime + 0.08;
  st.nextIdx = roll.notes.findIndex((n) => n.start + n.dur > st.startT);
  if (st.nextIdx < 0) st.nextIdx = roll.notes.length;
  $('roll-play').textContent = '⏸';
  const pump = () => {
    if (!st.on) return;
    const now = st.startT + (ctx.currentTime - st.t0);
    while (st.nextIdx < roll.notes.length && roll.notes[st.nextIdx].start < now + 0.35) {
      const n = roll.notes[st.nextIdx++];
      const at = st.t0 + (n.start - st.startT);
      if (at + n.dur <= ctx.currentTime) continue; // 恢复播放时已过去的音
      scheduleRollNote(n, Math.max(at, ctx.currentTime + 0.005));
    }
    st.t = Math.max(0, now);
    $('roll-time').textContent = `${fmtTime(Math.min(Math.max(now, 0), roll.duration))} / ${fmtTime(roll.duration)}`;
    requestRollDraw();
    if (now >= roll.duration + 0.15) {
      stopRollPlayback();
      st.t = 0;
      $('roll-time').textContent = `0:00.0 / ${fmtTime(roll.duration)}`;
      requestRollDraw();
      return;
    }
    st.raf = requestAnimationFrame(pump);
  };
  st.raf = requestAnimationFrame(pump);
}

function scheduleRollNote(n, at) {
  const ctx = rollPlayState.ctx;
  const osc = ctx.createOscillator();
  const g = ctx.createGain();
  osc.type = 'triangle';
  osc.frequency.value = pitchFreq(n.pitch);
  const v = 0.08 + 0.35 * (n.vel / 127);
  g.gain.setValueAtTime(0.0001, at);
  g.gain.linearRampToValueAtTime(v, at + 0.012);
  const end = at + Math.max(0.05, n.dur);
  g.gain.exponentialRampToValueAtTime(0.0001, end + 0.05);
  osc.connect(g);
  g.connect(rollPlayState.master);
  osc.start(at);
  osc.stop(end + 0.08);
  rollPlayState.sources.add(osc);
  osc.onended = () => rollPlayState.sources.delete(osc);
}

function stopRollPlayback() {
  const st = rollPlayState;
  st.on = false;
  if (st.raf) cancelAnimationFrame(st.raf);
  for (const s of st.sources) { try { s.stop(); } catch { /* already stopped */ } }
  st.sources.clear();
  if (st.master) { try { st.master.disconnect(); } catch { /* gone */ } }
  st.master = null;
  const btn = $('roll-play');
  if (btn) btn.textContent = '▶';
  requestRollDraw();
}

/** 上下分栏分隔条：拖动调整曲谱/卷帘比例。 */
function initScoreSplit() {
  const divider = $('score-divider');
  const pane = $('score-pane');
  const split = $('score-split');
  let dragging = false;
  let startY = 0;
  let startH = 0;
  divider.addEventListener('mousedown', (e) => {
    dragging = true;
    startY = e.clientY;
    startH = pane.getBoundingClientRect().height;
    e.preventDefault();
  });
  window.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const max = Math.max(120, split.clientHeight - 160);
    const h = Math.min(Math.max(startH + (e.clientY - startY), 120), max);
    pane.style.flex = `0 0 ${h}px`;
    requestRollDraw();
  });
  window.addEventListener('mouseup', () => { dragging = false; });
}

let scoreProgressTimer = null;

/** 完成提示 4 秒后自动收起，不留占位杂物。 */
function hideScoreProgressSoon() {
  clearTimeout(scoreProgressTimer);
  scoreProgressTimer = setTimeout(() => {
    const box = $('score-progress');
    box.hidden = true;
    box.textContent = '';
  }, 4000);
}

function showToolProgress(kind, text) {
  clearTimeout(scoreProgressTimer);
  const box = $(kind === 'stems' ? 'stems-progress' : 'score-progress');
  box.hidden = false;
  box.textContent = text;
  box.scrollTop = box.scrollHeight;
}

function appendToolProgress(kind, line) {
  clearTimeout(scoreProgressTimer);
  const box = $(kind === 'stems' ? 'stems-progress' : 'score-progress');
  box.hidden = false;
  box.textContent += (box.textContent ? '\n' : '') + line;
  box.scrollTop = box.scrollHeight;
}

function clearToolProgress() {
  clearTimeout(scoreProgressTimer);
  $('stems-progress').hidden = true;
  $('stems-progress').textContent = '';
  $('score-progress').hidden = true;
  $('score-progress').textContent = '';
}

function resetStudioTools() {
  // 换世界：清分离轨与曲谱工作台（产物留在旧世界目录里）
  destroyStemWaves();
  $('stems-tracks').textContent = '';
  destroyScore();
  clearToolProgress();
  // A/B 审听随世界复位：停播、清产物与未记录的选择
  // （已入账的选择留在旧世界的 compare/ab_choices.jsonl 与研究账本里）
  resetAbPanel();
}

/** 换世界：曲谱工作台复位（停播放、清卷帘与产物列表；产物留在旧世界目录）。 */
function destroyScore() {
  stopRollPlayback();
  rollPlayState.t = 0;
  rollClear();
  scoreProducts = [];
  scoreCurrent = null;
  scoreOsmd = null;
  scoreZoom = 0.85;
  $('roll-time').textContent = '0:00.0';
  $('score-sheet').textContent = '';
}

// ——— A/B 审听（图标栏第 6 位 · 薄 GUI）———
// 修音(后处理)之后得到 A(源, 修音前) 与 B(修音产物, 修音后)，二选一留哪个。
// 本面板不产生判断、不算响度、不写选择：事实来自 Core CLI 的比较产物
// （<case>/compare/ab_comparison.json, `moodify compare prepare`），
// 人的选择经同一条 CLI 记录（`moodify compare choose` → 世界内 append-only 账本）。
// 壳内只做两件事：把产物读成界面 + 同位置 A/B 试听。

const RESEARCH_PRESETS = [
  { id: 'clean_master', label: 'clean_master（干净母带）' },
  { id: 'warm_vocal', label: 'warm_vocal（暖人声）' },
  { id: 'wide_space', label: 'wide_space（宽空间）' },
];

const LOUD_LABEL = {
  NOT_MATCHED: '未匹配（v0.1 只测量，无匹配代理）',
  UNAVAILABLE: '不可测',
  MATCHED: '已匹配',
};

const ab = {
  caseDir: null,   // 产物所属世界（异步守卫用）
  artifact: null,  // Core 产出的比较产物
  freshness: null,
  choice: null,    // 'A' | 'B'（尚未记录的选择）
  requestId: null, // 本次待决选择的幂等键：重试同一条不会被记两次
  busy: false,     // 载入/准备/记录进行中
  // 播放（同位置切换：一个 AudioContext，两个已解码 buffer）
  ctx: null,
  buffers: { A: null, B: null },
  node: null,
  side: null,
  offset: 0,
  startedAt: 0,
  playing: false,
  raf: 0,
};

function toggleResearchPanel(force) {
  const panel = $('research-panel');
  const show = force !== undefined ? force : panel.hidden;
  panel.hidden = !show;
  $('rail-research').classList.toggle('active', show);
  if (show) loadResearchCase();
}

/** 世界变了：停播、清产物、清选择（账本里的既有记录不受影响）。 */
function resetAbPanel() {
  abStop();
  ab.caseDir = null;
  ab.artifact = null;
  ab.freshness = null;
  ab.choice = null;
  ab.requestId = null;
  ab.buffers = { A: null, B: null };
  ab.offset = 0;
  syncChoiceButtons();
  updateAbTime(0);
}

async function loadResearchCase() {
  const caseDir = state.caseDir;
  abStop();
  ab.buffers = { A: null, B: null };
  ab.offset = 0;
  ab.caseDir = caseDir;
  ab.artifact = null;
  ab.choice = null;
  ab.requestId = null;
  syncChoiceButtons();
  updateAbTime(0);
  $('rp-status').textContent = '';
  $('rp-ab-state').textContent = '同位置切换：播放中再点另一版即从当前位置切过去。';
  if (!caseDir) {
    $('rp-a-name').textContent = '—';
    $('rp-b-name').textContent = '—';
    $('rp-loud-status').textContent = '—';
    $('rp-render-note').textContent = '先打开一个世界。';
    setAbPlayEnabled(false);
    updateRecordBtn();
    return;
  }
  let read;
  try { read = await window.moodify.compareRead(caseDir); } catch (err) { read = null; }
  if (ab.caseDir !== caseDir) return; // 换世界守卫
  if (!read || !read.ok) {
    // 产物还没准备：用世界摘要给出提示（哪些产物已经存在），但不冒充权威事实
    let info = null;
    try { info = await window.moodify.researchCase(caseDir); } catch { info = null; }
    if (ab.caseDir !== caseDir) return;
    $('rp-a-name').textContent = (info && info.sourceName) || '—';
    $('rp-b-name').textContent = info && info.renderedB
      ? info.renderedB.split(/[\\/]/).pop() : '（未渲染）';
    $('rp-loud-status').textContent = '未准备';
    if (read && read.reason !== 'NO_COMPARISON') {
      $('rp-render-note').textContent = `无法读取比较产物：${read.reason || '未知'}`;
    } else if (info && info.renderedB) {
      $('rp-render-note').textContent = `B 已渲染（${info.preset || '修音产物'}）——点「准备比较」生成 A/B 产物。`;
    } else {
      $('rp-render-note').textContent = 'B 尚未渲染——先「渲染 B」产出修音产物，再「准备比较」。';
    }
    setAbPlayEnabled(false);
    updateRecordBtn();
    return;
  }
  ab.artifact = read.artifact;
  ab.freshness = read.freshness;
  renderAbArtifact();
  await syncResearchPrefs();
  updateRecordBtn();
}

function renderAbArtifact() {
  const art = ab.artifact || {};
  const a = art.a || null;
  const b = art.b || null;
  const loud = art.loudness || {};
  ab.duration = Math.max(
    (a && a.measurement && a.measurement.duration_s) || 0,
    (b && b.measurement && b.measurement.duration_s) || 0,
  );
  $('rp-a-name').textContent = a ? a.name : '（未定位）';
  $('rp-a-name').title = (a && a.path) || '';
  $('rp-b-name').textContent = b ? b.name : '（未渲染）';
  $('rp-b-name').title = (b && b.path) || '';
  const pill = $('rp-loud-status');
  pill.textContent = LOUD_LABEL[loud.matching_status] || loud.matching_status || '—';
  pill.classList.toggle('ok', loud.matching_status === 'MATCHED');
  pill.title = loud.delta_lu === null || loud.delta_lu === undefined
    ? (loud.note || '')
    : `Δ ${loud.delta_lu} LU（B − A）· ${loud.note || ''}`;
  $('rp-preset').value = ((b && b.mix_graph && b.mix_graph.preset) || $('rp-preset').value);
  const reasons = (art.reasons || []).map((r) => r.code).join(' · ');
  if (art.status !== 'READY') {
    $('rp-render-note').textContent = `比较状态 ${art.status}${reasons ? '（' + reasons + '）' : ''}`;
  } else {
    const stale = ab.freshness
      && (ab.freshness.a_matches_artifact === false || ab.freshness.b_matches_artifact === false);
    $('rp-render-note').textContent = stale
      ? '产物在界外被改动过：重新「准备比较」后再记录。'
      : `比较就绪${reasons ? '（提醒：' + reasons + '）' : ''} · 账本 ${(ab.freshness || {}).choice_count ?? 0} 条`;
  }
  setAbPlayEnabled(art.status === 'READY');
}

function setAbPlayEnabled(on) {
  $('rp-play-a').disabled = !on;
  $('rp-play-b').disabled = !on;
}

function buildChoiceButtons() {
  const box = $('rp-choice');
  box.textContent = '';
  for (const [value, label] of [['A', '留 A 源'], ['B', '留 B 修音']]) {
    const b = document.createElement('button');
    b.type = 'button';
    b.dataset.choice = value;
    b.textContent = label;
    b.title = value === 'A' ? '保留源音频' : '保留修音产物';
    b.addEventListener('click', () => {
      ab.choice = ab.choice === value ? null : value;
      ab.requestId = null; // 选择变了：这是另一次待决选择，换新幂等键
      syncChoiceButtons();
      updateRecordBtn();
    });
    box.appendChild(b);
  }
  syncChoiceButtons();
}

function syncChoiceButtons() {
  document.querySelectorAll('#rp-choice button').forEach((b) =>
    b.classList.toggle('sel', b.dataset.choice === ab.choice));
}

function updateRecordBtn() {
  const ready = Boolean(ab.artifact && ab.artifact.status === 'READY');
  $('rp-record').disabled = !(ready && ab.choice && $('rp-mode').checked && !ab.busy);
}

async function syncResearchPrefs() {
  const prefs = await window.moodify.researchPrefs();
  $('rp-mode').checked = prefs.researchMode;
  $('rp-role').value = prefs.role || 'listener';
}

/** 准备比较：调用 Core CLI（唯一权威）；壳不生成任何比较事实。 */
async function prepareComparison() {
  if (!state.caseDir || ab.busy) return;
  const caseDir = state.caseDir;
  ab.busy = true;
  const btn = $('rp-prepare');
  btn.disabled = true;
  $('rp-render-note').textContent = '准备比较中（moodify compare prepare）…';
  try {
    const res = await window.moodify.comparePrepare(caseDir);
    if (ab.caseDir !== caseDir) return;
    await loadResearchCase();
    const payload = (res && res.payload) || {};
    if (res && res.ok) {
      $('rp-render-note').textContent = '比较已就绪（compare prepare 完成）。';
    } else {
      const reasons = (payload.reasons || []).map((r) => r.code).join(' · ');
      $('rp-render-note').textContent = `准备未完成（${payload.status || (res && res.code) || '?'}）：`
        + `${payload.error || (res && res.reason) || '未知'}${reasons ? ' · ' + reasons : ''}`;
    }
  } catch (err) {
    $('rp-render-note').textContent = `准备失败：${err.message || err}`;
  } finally {
    ab.busy = false;
    btn.disabled = false;
    updateRecordBtn();
  }
}

/** 渲染 B（core finishing）→ 自动刷新比较产物（同一条 CLI 路径）。 */
async function runFinishing() {
  if (!state.caseDir || ab.busy) return;
  const preset = $('rp-preset').value;
  const caseDir = state.caseDir;
  const btn = $('rp-render');
  btn.disabled = true;
  $('rp-render-note').textContent = `修音渲染中（${preset}）…`;
  try {
    const res = await window.moodify.finishingRun(caseDir, preset);
    if (ab.caseDir !== caseDir) return;
    if (res && res.ok) {
      const ev = res.evidenceRec ? `，研究证据 #${res.evidenceRec.count}` : '';
      $('rp-render-note').textContent = `B 已渲染（${preset}）${ev}。`;
      await prepareComparison();
    } else {
      $('rp-render-note').textContent = `修音渲染失败：${(res && res.reason) || '未知'}`;
    }
  } catch (err) {
    $('rp-render-note').textContent = `修音渲染失败：${err.message || err}`;
  } finally {
    btn.disabled = false;
  }
}

/** 记录选择：先经 Core CLI 落权威账本，再补记研究账本（T1 感知通道）。 */
async function recordJudgment() {
  if (!ab.artifact || ab.artifact.status !== 'READY' || !ab.choice || ab.busy) return;
  if (!$('rp-mode').checked) {
    $('rp-status').textContent = '先开启研究模式（记录人类判断的显式开关）。';
    return;
  }
  const caseDir = ab.caseDir;
  const keep = ab.choice;
  const role = $('rp-role').value;
  // 同一次待决选择用同一个幂等键：网络/超时重试被 Core 拒绝，不会写两条。
  if (!ab.requestId) {
    ab.requestId = `gui-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  }
  ab.busy = true;
  updateRecordBtn();
  $('rp-status').textContent = '记录中（moodify compare choose）…';
  try {
    const res = await window.moodify.compareChoose(caseDir, keep, role, ab.requestId);
    if (ab.caseDir !== caseDir) return;
    const payload = (res && res.payload) || {};
    if (!res || !res.ok) {
      if (res && res.reason === 'DUPLICATE_REQUEST') {
        // 幂等键命中：上一次其实已经入账，这次没有追加。换键后才允许再记一次。
        ab.requestId = null;
        $('rp-status').textContent = '这条选择已经记录过（同一次请求重复发送），账本未追加。';
        return;
      }
      $('rp-status').textContent = `记录失败（${payload.status || (res && res.code) || '?'}）：`
        + `${payload.error || (res && res.reason) || '未知'}`;
      return;
    }
    // 旧研究账本继续入账：它是下游暂存区，A/B 的权威记录始终在 CLI 的 append-only 账本里。
    let ledger = '';
    try {
      const rec = await window.moodify.researchJudgment({
        caseId: caseDir,
        workName: ((ab.artifact.a) || {}).name || '',
        sourceSha256: ((ab.artifact.a) || {}).sha256 || null,
        versionA: 'source',
        versionB: ((ab.artifact.b) || {}).name || 'rendered',
        preset: (((ab.artifact.b) || {}).mix_graph || {}).preset || null,
        loudnessMatched: false, // 测出来的事实：v0.1 无匹配代理
        choice: keep,
        comparisonRef: (ab.freshness || {}).artifact_sha256 || null,
      });
      if (rec && rec.ok) ledger = ` · 研究账本 #${rec.count}`;
    } catch { /* 账本补记失败不影响已落地的 CLI 选择 */ }
    ab.choice = null;
    ab.requestId = null; // 已入账：下一次选择是新的待决请求
    syncChoiceButtons();
    $('rp-status').textContent = `已记录：保留 ${payload.keep}（${payload.kept}）`
      + `· 角色 ${payload.role} · 第 ${payload.count} 条${ledger}`;
    await loadResearchCase();
    $('rp-status').textContent = `已记录：保留 ${payload.keep}（${payload.kept}）`
      + `· 角色 ${payload.role} · 第 ${payload.count} 条${ledger}`;
  } finally {
    ab.busy = false;
    updateRecordBtn();
  }
}

// ——— 同位置 A/B 试听（A=源 / B=修音产物；一个 AudioContext 两 buffer）———

function abCtx() {
  if (!ab.ctx) ab.ctx = new AudioContext();
  if (ab.ctx.state === 'suspended') ab.ctx.resume();
  return ab.ctx;
}

function abDuration() {
  const bufs = ab.buffers;
  const aDur = bufs.A ? bufs.A.duration : 0;
  const bDur = bufs.B ? bufs.B.duration : 0;
  return Math.max(aDur, bDur, ab.duration || 0);
}

function abPosition() {
  if (!ab.playing || !ab.ctx) return ab.offset;
  return Math.min(ab.offset + (ab.ctx.currentTime - ab.startedAt), abDuration());
}

function updateAbTime(pos) {
  $('rp-time').textContent = `${fmtTime(pos || 0)} / ${fmtTime(abDuration())}`;
}

function updateAbButtons() {
  const onA = ab.playing && ab.side === 'A';
  const onB = ab.playing && ab.side === 'B';
  $('rp-play-a').textContent = onA ? '⏸ A' : '▶ A';
  $('rp-play-b').textContent = onB ? '⏸ B' : '▶ B';
  $('rp-play-a').classList.toggle('sel', onA);
  $('rp-play-b').classList.toggle('sel', onB);
}

function abHalt() {
  if (ab.raf) { cancelAnimationFrame(ab.raf); ab.raf = 0; }
  const node = ab.node;
  ab.node = null;
  ab.playing = false;
  if (node) {
    node.onended = null;
    try { node.stop(); } catch { /* already stopped */ }
    try { node.disconnect(); } catch { /* gone */ }
  }
  updateAbButtons();
}

function abStop() {
  if (ab.playing) ab.offset = 0;
  abHalt();
  updateAbTime(ab.offset);
}

function abTick() {
  if (!ab.playing) return;
  const pos = abPosition();
  updateAbTime(pos);
  if (pos >= abDuration() - 0.03) {
    ab.offset = 0;
    abHalt();
    updateAbTime(0);
    return;
  }
  ab.raf = requestAnimationFrame(abTick);
}

function abStart(side, offset) {
  const ctx = abCtx();
  const buf = ab.buffers[side];
  if (!buf) return;
  const dur = buf.duration;
  const start = Math.max(0, Math.min(offset, Math.max(0, dur - 0.02)));
  const node = ctx.createBufferSource();
  node.buffer = buf;
  node.connect(ctx.destination);
  node.start(0, start);
  ab.node = node;
  ab.side = side;
  ab.offset = start;
  ab.startedAt = ctx.currentTime;
  ab.playing = true;
  node.onended = () => { if (ab.node === node) { ab.playing = false; ab.node = null; updateAbButtons(); } };
  updateAbButtons();
  abTick();
}

function abDecode(ctx, bytes) {
  const ab_ = bytes instanceof ArrayBuffer ? bytes
    : bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  return ctx.decodeAudioData(ab_);
}

/** 点 A/B：未播放→从当前位置播；正在播另一版→同位置切过去；正在播自身→停。 */
async function abToggle(side) {
  if (ab.busy || !ab.artifact || ab.artifact.status !== 'READY') return;
  const caseDir = ab.caseDir;
  if (ab.playing && ab.side === side) { abStop(); return; }
  const switchFrom = ab.playing ? abPosition() : ab.offset;
  if (!ab.buffers.A || !ab.buffers.B) {
    ab.busy = true;
    updateRecordBtn();
    $('rp-ab-state').textContent = '载入 A/B 音频…';
    try {
      const [aBytes, bBytes] = await Promise.all([
        window.moodify.compareAudio(caseDir, 'A'),
        window.moodify.compareAudio(caseDir, 'B'),
      ]);
      const ctx = abCtx();
      const [bufA, bufB] = await Promise.all([abDecode(ctx, aBytes), abDecode(ctx, bBytes)]);
      if (ab.caseDir !== caseDir) return; // 换世界守卫
      ab.buffers = { A: bufA, B: bufB };
      ab.duration = Math.max(bufA.duration, bufB.duration);
      $('rp-ab-state').textContent = '已载入：同位置切换试听。';
      updateAbTime(ab.offset);
    } catch (err) {
      $('rp-ab-state').textContent = `载入失败：${err.message || err}`;
      return;
    } finally {
      ab.busy = false;
      updateRecordBtn();
    }
  }
  if (ab.caseDir !== caseDir) return;
  abHalt();
  abStart(side, switchFrom);
  $('rp-ab-state').textContent = ab.side === 'A'
    ? '正在听 A（源）——点「▶ B」从同一位置切到修音产物。'
    : '正在听 B（修音产物）——点「▶ A」从同一位置切回源。';
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

/** 意图命令条入口：惰性开线程，回答与操作都发生在 dock 里。首次发送弹出对话抽屉。
 *  无世界也可对话（纯聊）；打开世界后线程自动切到 case 目录。 */
async function intentSend(text) {
  if (!text.trim() || compiler.busy) return;
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
  if (!compiler.ready) return; // cwd 兜底：无世界时主进程落到 CASES_ROOT
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
    const cwdLabel = state.caseDir || '自由对话（未打开世界）';
    compilerLine('sys', `线程就绪（${cwdLabel}）· 生效沙箱：${effective}`);
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

/** 顶栏权限开关：standard（逐条审批）↔ full（无沙箱不审批，畅通无阻）。
 *  权限随线程生效：切换后丢弃当前线程，下一个新线程按新模式打开。 */
async function initPermToggle() {
  const btn = $('perm-toggle');
  const setLabel = (mode) => {
    btn.textContent = mode === 'full' ? '权限：全开' : '权限：标准';
    btn.title = mode === 'full'
      ? 'AI 畅通无阻（无沙箱、不再逐条审批）。点击切回标准保护。'
      : '标准保护（工作区写入 + 敏感操作逐条审批）。点击切为全开。';
  };
  try { setLabel(await window.moodify.permissionGet()); } catch { /* keep default */ }
  btn.addEventListener('click', async () => {
    const next = (await window.moodify.permissionGet()) === 'full' ? 'standard' : 'full';
    await window.moodify.permissionSet(next);
    setLabel(next);
    compiler.threadId = null; // 旧线程策略已冻结，丢弃；下个线程按新模式开
    compiler.threadCwd = null;
    compilerNote(next === 'full'
      ? '权限已切为全开：不再逐条审批，新对话线程起生效。'
      : '权限已切回标准：敏感操作将逐条审批，新对话线程起生效。');
  });
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
  // decision 值按协议代际映射（schema 权威）：
  //   v2 item/* → accept / acceptForSession / decline
  //   v1 旧名    → approved / approved_for_session / denied
  const v2 = req.method.startsWith('item/');
  const yes = v2 ? 'accept' : 'approved';
  const session = v2 ? 'acceptForSession' : 'approved_for_session';
  const no = v2 ? 'decline' : 'denied';
  const actions = document.createElement('div');
  actions.className = 'approval-actions';
  const mk = (text, decision, primary) => {
    const b = document.createElement('button');
    b.textContent = text;
    b.className = primary ? 'primary' : 'ghost';
    b.addEventListener('click', async () => {
      await window.moodify.codexRespond(req.id, { decision });
      card.remove();
    });
    return b;
  };
  actions.appendChild(mk('批准', yes, true));
  actions.appendChild(mk('本次会话全部允许', session, false));
  actions.appendChild(mk('拒绝', no, false));
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
  $('bench-play').addEventListener('click', (e) => {
    e.currentTarget.blur(); // 空格留给全局走带快捷键，不让按钮吃掉
    if (sourceWS) sourceWS.playPause();
  });
  // 空格 = 播放/暂停（修音台音频或曲谱台 MIDI，焦点不在输入区时）
  window.addEventListener('keydown', (e) => {
    if (e.code !== 'Space') return;
    const el = document.activeElement;
    if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable)) return;
    if (!$('view-bench').hidden && sourceWS) {
      e.preventDefault();
      sourceWS.playPause();
    } else if (!$('view-score').hidden && roll.notes.length) {
      e.preventDefault();
      rollToggle();
    }
  });
  $('rail-stems').addEventListener('click', openStems);
  $('rail-score').addEventListener('click', openScore);
  // A/B 审听（薄 GUI）：读 compare 产物 / 修音渲染 / 同位置试听 / 二选一交给 CLI
  $('rail-research').addEventListener('click', () => toggleResearchPanel());
  for (const preset of RESEARCH_PRESETS) {
    const opt = document.createElement('option');
    opt.value = preset.id;
    opt.textContent = preset.label;
    $('rp-preset').appendChild(opt);
  }
  buildChoiceButtons();
  syncResearchPrefs();
  $('rp-mode').addEventListener('change', () => {
    window.moodify.researchPrefs({ researchMode: $('rp-mode').checked });
    updateRecordBtn();
  });
  $('rp-role').addEventListener('change', () => {
    window.moodify.researchPrefs({ role: $('rp-role').value });
  });
  $('rp-play-a').addEventListener('click', () => abToggle('A'));
  $('rp-play-b').addEventListener('click', () => abToggle('B'));
  $('rp-render').addEventListener('click', runFinishing);
  $('rp-prepare').addEventListener('click', prepareComparison);
  $('rp-record').addEventListener('click', recordJudgment);
  $('stems-run').addEventListener('click', runStems);
  $('score-convert').addEventListener('click', convertChain);
  $('score-product').addEventListener('change', () => {
    const p = scoreProducts[Number($('score-product').value)];
    if (p) loadScoreProduct(p);
  });
  $('roll-play').addEventListener('click', rollToggle);
  $('score-zoom-in').addEventListener('click', () => setScoreZoom(scoreZoom + 0.15));
  $('score-zoom-out').addEventListener('click', () => setScoreZoom(scoreZoom - 0.15));
  $('score-zoom-fit').addEventListener('click', () => setScoreZoom(0.85));
  $('roll-zoom-in').addEventListener('click', () => setRollZoom((roll.zoomPps || roll.effPps || 100) * 1.5, centerSec()));
  $('roll-zoom-out').addEventListener('click', () => setRollZoom((roll.zoomPps || roll.effPps || 100) / 1.5, centerSec()));
  $('roll-zoom-fit').addEventListener('click', () => { roll.zoomPps = null; roll.scrollX = 0; requestRollDraw(); });
  initRollEvents();
  initScoreSplit();
  window.addEventListener('resize', requestRollDraw);
  window.moodify.onToolProgress((kind, line) => appendToolProgress(kind, line));
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
  initPermToggle();
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
