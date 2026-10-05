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

const VIEWS = ['empty', 'tuning', 'data', 'spectrum', 'charts', 'bench', 'stems', 'score'];
/** Which pipeline stage each view belongs to (① 检测 spans the three observation tabs). */
const VIEW_STAGE = {
  data: 'analyze', spectrum: 'analyze', charts: 'analyze',
  stems: 'separate',
  score: 'structure',
  tuning: 'tune',
};
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

// ——— application updates: prompt only; the user chooses update / later / skip. ———

let currentUpdateState = null;

/**
 * 更新对话框的状态投影。
 *
 * 三种人类选择（下载并安装 / 稍后提醒 / 跳过此版本）之外，还必须始终留一条
 * 「手动检查」的路径。早先的实现把 primary 按钮在 `later` / `skipped` 下**整个隐藏**，
 * 于是用户点了「稍后提醒」之后重新打开入口，卡片上只剩一个「关闭」——
 * 想改主意也没有按钮可点。那是把「本次不再提示」实现成了「再也查不了」。
 *
 * 现在的规则：
 *   - `available`  → primary = 下载更新；显示 稍后提醒 / 跳过此版本
 *   - `ready`      → primary = 重启并安装（唯一允许安装的状态）
 *   - `later` / `skipped` / `current` / `error` / `idle`
 *                  → primary = 检查更新（可再次检查，用户可改主意）
 *   - `downloading` / `installing` / `checking` → primary 隐藏，避免重复提交
 *   - `dev`（未打包）→ 不提供检查：没有 feed 可查，给按钮就是骗人
 */
function renderUpdateStatus(next, forceOpen = false) {
  if (!next) return;
  currentUpdateState = next;
  const dialog = $('update-dialog');
  const open = $('update-open');
  const primary = $('update-primary');
  const later = $('update-later');
  const skip = $('update-skip');
  const progress = $('update-progress');
  const status = next.status;

  $('update-version').textContent = `当前版本 ${next.currentVersion || '—'}${next.version ? ` · 新版本 ${next.version}` : ''}`;
  $('update-message').textContent = next.message || '检查是否有新版本。';

  // 顶栏入口：让人一眼看出有没有待处理的新版本
  open.classList.toggle('has-update', ['available', 'downloading', 'ready'].includes(status));
  open.textContent = status === 'ready' ? '更新已就绪' : status === 'available' ? '有新版本' : '更新';

  progress.hidden = status !== 'downloading';
  progress.value = next.percent || 0;

  // 「稍后」与「跳过」只对**当下这个可用版本**有意义
  later.hidden = status !== 'available';
  skip.hidden = status !== 'available';

  // primary 的动作由状态决定；只有 ready 才可能是「安装」
  let action = 'check';
  let label = '检查更新';
  if (status === 'available') { action = 'download'; label = '下载更新'; }
  else if (status === 'ready') { action = 'install'; label = '重启并安装'; }

  const busy = ['downloading', 'installing', 'checking'].includes(status);
  const unsupported = status === 'dev' || next.supported === false;
  primary.hidden = busy || unsupported;
  primary.disabled = busy || unsupported;
  primary.dataset.action = action;
  primary.textContent = label;

  // 自动弹窗只发生在**真的需要用户做决定**时（有可用版本 / 已下载完成）。
  // 手动打开入口（forceOpen）则一律展示卡片——即使当前无动作可做（例如 dev
  // 未打包模式，或正在下载），因为那时候用户需要的是**看到状态说明**，
  // 而不是面对一个点了没反应的入口。
  if (forceOpen || ['available', 'ready'].includes(status)) dialog.hidden = false;
}

async function initUpdater() {
  $('update-open').addEventListener('click', async () => {
    $('update-dialog').hidden = false;
    const status = await window.moodify.updateStatus();
    renderUpdateStatus(status, true);
  });
  $('update-close').addEventListener('click', () => { $('update-dialog').hidden = true; });
  $('update-later').addEventListener('click', async () => {
    renderUpdateStatus(await window.moodify.updateAction('later'));
    $('update-dialog').hidden = true;
  });
  $('update-skip').addEventListener('click', async () => {
    renderUpdateStatus(await window.moodify.updateAction('skip'));
    $('update-dialog').hidden = true;
  });
  $('update-primary').addEventListener('click', async () => {
    // 动作由 renderUpdateStatus 写在 dataset 上，这里不再二次推断：
    // 两处各自推断同一个动作，迟早会分叉（按钮写着「下载更新」却发 check 请求）。
    const action = $('update-primary').dataset.action || 'check';
    const result = action === 'check'
      ? await window.moodify.updateCheck()
      : await window.moodify.updateAction(action);
    renderUpdateStatus(result, true);
  });
  window.moodify.onUpdateStatus((status) => renderUpdateStatus(status));
  renderUpdateStatus(await window.moodify.updateStatus());
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

/** 当前视图名。用于「制作详情」展开时决定技术阶段条是否出现。 */
let currentView = 'empty';

function selectView(name) {
  currentView = name;
  for (const v of VIEWS) $(`view-${v}`).hidden = v !== name;
  $('tabs').hidden = name === 'empty' || name === 'bench' || name === 'stems' || name === 'score'
    || name === 'tuning';
  // 技术阶段条（pipeline.js 的内部 8 阶段）不再裸露在主界面上——它属于「制作详情」层。
  // 主界面的进度由完成会话的 6 相位条承担，而那一条是不可点的状态投影。
  $('pipeline-bar').hidden = name === 'empty' || name === 'tuning';
  for (const [view, tabId] of Object.entries(VIEW_TAB)) {
    $(tabId).classList.toggle('active', view === name);
  }
  $('rail-tuning').classList.toggle('active', name === 'tuning');
  $('rail-bench').classList.toggle('active', name === 'bench');
  $('rail-stems').classList.toggle('active', name === 'stems');
  $('rail-score').classList.toggle('active', name === 'score');
  // 波形在隐藏态宽度为 0：进入审听视图后重新应用缩放，别留一条画不出来的空轨。
  if (name === 'tuning') {
    requestAnimationFrame(() => { try { applyReviewZoom(); } catch { /* not mounted yet */ } });
  }

  // 流程条高亮当前阶段。同一阶段可以有多个视图（① 检测 = 数据/频谱/图表）。
  const stage = VIEW_STAGE[name];
  for (const btn of $('pipeline-stages').querySelectorAll('.pipe-stage')) {
    btn.classList.toggle('active', btn.dataset.stage === stage);
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
  destroyBench(); // 换世界：旧工作台实例销毁
  resetStudioTools(); // 换世界：分离/曲谱工作台复位（产物留在旧世界目录）
  resetTuningWorld(); // 换世界：修音/复合视图复位（修音对留在旧世界目录）
  resetSession();     // 换世界：完成会话复位（一次启动的状态不跨世界）
  resetPipeline();    // 换世界：流程状态复位（阶段由新 case 的产物重新推导）

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
  // 落地在「完成会话」而不是数据页：普通用户不需要先读指标表，
  // 数据 / 频谱 / 图表仍在，但归入「制作详情」层。
  await refreshPipeline(); // 流程条按本 case 的真实产物点亮/锁定
  await openTuning();
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

// ——— 逆向分解工作台（图标栏第 4 位）———
//
// 两档真实引擎，不是「快/慢」的措辞差异：
//   model = Demucs htdemucs（MIT）神经网络四轨 drums/bass/other/vocals，母带级
//   dsp   = scipy 中置估计 + HPSS，秒级，产物自带 PREVIEW_NOT_MASTERING_GRADE
// 没装模型运行时时默认走快速并**明确标注这是降级**——用户必须知道手上是哪一档。
// 可逆性验证是 ④ 修音 的门禁：分轨按划分相加必须回到原版（null 深度）。

const STEM_LABELS = {
  vocals: '人声（模型分离 / 中置估计）',
  instrumental: '伴奏（源 − 中置）',
  harmonic: '谐波（持续音）',
  percussive: '打击（瞬态）',
  drums: '鼓（模型分离）',
  bass: '贝斯（模型分离）',
  other: '其他乐器（模型分离）',
};

/** Demucs 的轨名也要认得出来，否则四轨会显示成文件名。 */
const STEM_BASE_RE = /__(vocals|instrumental|harmonic|percussive|drums|bass|other)\.wav$/i;
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
  const m = name.match(STEM_BASE_RE);
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
  const engineSel = $('stems-engine');
  const mode = (engineSel && engineSel.value) || 'auto';
  btn.disabled = true;
  showToolProgress('stems', mode === 'dsp' ? '快速分离中…' : '分离中…（模型分离按 2–4× 实时长，请耐心）');
  try {
    const res = await window.moodify.stemsRun(state.caseDir, mode);
    if (!res.ok) {
      // 缺运行时是**可操作**的失败：把怎么装一起说出来，不给一个光秃秃的错误码
      const hint = res.install ? `；安装：${res.install}` : '';
      showToolProgress('stems', `分离失败（${res.code || res.reason || '?'} ${res.detail || ''}）${hint}`);
    } else if (res.downgraded) {
      showToolProgress('stems',
        `已用快速分离（预览级）。${res.downgradeReason || ''}${res.installHint ? ` 安装模型引擎：${res.installHint}` : ''}`);
    } else {
      showToolProgress('stems', `完成（引擎：${res.engine === 'model' ? 'Demucs 模型' : 'DSP 快速'}）。`);
    }
    await openStems(); // 重扫产物入列
  } catch (err) {
    showToolProgress('stems', `分离失败：${err.message || err}`);
  } finally {
    btn.disabled = false;
  }
}

/**
 * 可逆性验证（④ 修音 的门禁）。
 *
 * UI 的两条纪律：
 *   · 通过时必须把 null 深度一起显示 —— 只显示「通过」会被读成「分轨已验证」；
 *   · 必须同时说明它**不**证明分轨质量（任何可逆分解都能通过，包括「轨1=原版、轨2=静音」）。
 */
async function runRoundtrip() {
  if (!state.caseDir) return;
  const btn = $('stems-roundtrip');
  const note = $('stems-roundtrip-note');
  btn.disabled = true;
  note.hidden = false;
  note.textContent = '正在把分轨相加与原版比较…';
  try {
    const res = await window.moodify.stemsRoundtrip(state.caseDir);
    if (!res.ok) {
      note.textContent = `可逆性验证未完成（${res.code || res.reason || '?'}）。`
        + '这不代表分轨有问题——只代表这一步没跑完。';
    } else {
      const db = res.nullDepthDb;
      note.textContent = res.passed
        ? `可逆性通过：null 深度 ${db} dB（分轨按划分相加能回到原版）。`
          + '注意：这**不**说明分轨分得好——任何可逆分解都能通过。'
        : `可逆性未通过：null 深度 ${db} dB。分解与复合之间存在真实漂移，`
          + '④ 修音保持锁定。';
    }
    await refreshPipeline();
  } catch (err) {
    note.textContent = `可逆性验证失败：${err.message || err}`;
  } finally {
    btn.disabled = false;
  }
}

/** 引擎下拉：缺模型运行时时如实标注，并保留用户的选择权（不替他改）。 */
async function initStemEngineSelect() {
  const sel = $('stems-engine');
  const note = $('stems-engine-note');
  if (!sel || !note) return;
  try {
    const res = await window.moodify.stemsEngineGet();
    if (res && res.ok) {
      sel.value = res.engine || 'auto';
      const model = res.model || {};
      if (model.available) {
        note.textContent = '模型引擎可用（Demucs）。';
      } else {
        sel.querySelector('option[value="model"]').disabled = true;
        note.textContent = '模型引擎未安装：自动模式会走快速分离（预览级）。'
          + (model.install ? ` 安装：${model.install}` : '');
      }
    }
  } catch { /* 探测失败不阻断工作台 */ }
  sel.addEventListener('change', async () => {
    try { await window.moodify.stemsEngineSet(sel.value); } catch { /* 记录失败不影响本次运行 */ }
    await refreshPipeline();
  });
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
  try { await syncResearchPrefs(); } catch { /* 偏好读不到不阻塞产物展示 */ }
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
        // 读产物的事实，不由界面声明：v0.1 没有匹配代理 → NOT_MATCHED → false
        loudnessMatched: (((ab.artifact || {}).loudness || {}).matching_status) === 'MATCHED',
        role,
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
  } catch (err) {
    // IPC 层失败也必须留下明确状态，不能停在「记录中…」冒充成功
    $('rp-status').textContent = `记录失败：${err.message || err}`;
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
  try {
    abStart(side, switchFrom);
    $('rp-ab-state').textContent = ab.side === 'A'
      ? '正在听 A（源）——点「▶ B」从同一位置切到修音产物。'
      : '正在听 B（修音产物）——点「▶ A」从同一位置切回源。';
  } catch (err) {
    $('rp-ab-state').textContent = `播放失败：${err.message || err}`;
  }
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
  await initUpdater();
  const env = await window.moodify.env();
  $('archive-path').textContent = env.casesRoot;
  if (!env.coreReady) {
    setStatus('核心不可用 — 请先安装 moodify 包（pip install -e moodify-core-package）');
  }

  $('rail-open').addEventListener('click', pickAndAnalyze);
  $('empty-pick').addEventListener('click', pickAndAnalyze);
  $('rail-history').addEventListener('click', () => toggleHistoryPanel());
  $('tab-data').addEventListener('click', () => { if (state.caseDir) selectView('data'); });
  $('tab-spectrum').addEventListener('click', () => { if (state.caseDir) selectView('spectrum'); });
  $('tab-charts').addEventListener('click', () => { if (state.caseDir) selectView('charts'); });
  $('rail-bench').addEventListener('click', openBench);
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
  $('stems-roundtrip').addEventListener('click', runRoundtrip);
  initStemEngineSelect();
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
  initTuning();
  initSession();
  initPipeline();
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

// ——— 完成会话（「一键完成机」· Phase 1）———
//
// 产品形态：放入一首歌 → 一次启动 → 内部自动执行 → 原版 / A / B → 人选择 → 导出。
//
// 这里的代码只做**投影与发起**：
//   · 相位与状态来自 main 侧的 session 投影，其权威仍是 pipeline.js 的产物推导；
//   · 渲染层不自己算进度，也不自己判断能不能继续；
//   · 阻断态照原样显示，绝不把「Core 还没实现」渲染成成功或进行中。

const STATUS_TITLE = {
  done: '已完成',
  next: '下一步',
  blocked: '做不了：产品能力尚未就绪',
  todo: '尚未开始',
  skipped: '快速完成（仅立体声）不经过这一步',
};

const sessionState = {
  caseDir: null,
  view: null,
  busy: false,
};

function initSession() {
  $('session-start').addEventListener('click', startCompletion);
  $('session-detail-toggle').addEventListener('click', toggleSessionDetail);
  // 显式切换到快速完成：两级动作。点「切换」只展开确认，**不写任何东西**；
  // 只有点「确认切换」才记录人类决定（与「制作详情」里的按钮共用同一个处理器）。
  $('session-remedy-switch').addEventListener('click', askQuickSwitch);
  $('session-remedy-yes').addEventListener('click', () => {
    hideQuickConfirm();
    chooseQuickFinish();
  });
  $('session-remedy-no').addEventListener('click', hideQuickConfirm);
  window.moodify.onSessionProgress((payload) => {
    // 只接受当前世界的进度——换世界后旧会话的事件必须被丢掉
    if (!payload || payload.caseDir !== sessionState.caseDir) return;
    renderSession(payload);
  });
}

/** 展开确认区（不写 finish_mode.json）。 */
function askQuickSwitch() {
  const view = sessionState.view || {};
  const note = (view.fastSwitch && view.fastSwitch.note)
    || '快速完成不会使用分轨进行音准或节奏修正；仍会生成 A/B、复检并由你选择。';
  $('session-remedy-note').textContent = note;
  $('session-remedy-ask').hidden = true;
  $('session-remedy-confirm').hidden = false;
}

function hideQuickConfirm() {
  $('session-remedy-confirm').hidden = true;
  $('session-remedy-ask').hidden = false;
}

function toggleSessionDetail(force) {
  const box = $('session-detail');
  box.hidden = typeof force === 'boolean' ? !force : !box.hidden;
  $('session-detail-toggle').textContent = box.hidden ? '制作详情' : '收起详情';
  // 技术阶段条只在「制作详情」展开时出现：主界面用它只会暴露内部步骤。
  if (currentView === 'tuning') $('pipeline-bar').hidden = box.hidden;
}

function resetSession() {
  sessionState.caseDir = null;
  sessionState.view = null;
  sessionState.busy = false;
  $('session-phases').textContent = '';
  $('session-state').textContent = '';
  $('session-stage').textContent = '';
  $('session-mode').hidden = true;
  $('session-remedy').hidden = true;
  $('session-remedy-reason').textContent = '';
  hideQuickConfirm();
  $('session-start').disabled = false;
  $('session-start').textContent = '开始完成';
  toggleSessionDetail(false);
}

async function refreshSession() {
  const caseDir = state.caseDir;
  if (!caseDir) return null;
  let res;
  try { res = await window.moodify.sessionView(caseDir); } catch { return null; }
  if (!res || !res.ok || state.caseDir !== caseDir) return null; // 换世界守卫
  sessionState.caseDir = caseDir;
  renderSession(res.view);
  return res.view;
}

function renderSession(view) {
  if (!view) return;
  sessionState.view = view;

  const blockerKind = view.blocker && view.blocker.kind;
  const stepFailed = blockerKind === 'STEP_FAILED';
  const fast = view.fast === true;

  const list = $('session-phases');
  list.textContent = '';
  for (const p of view.phases || []) {
    const li = document.createElement('li');
    li.className = 'session-phase ' + p.status;
    li.textContent = p.label;
    // 阻断有两种：产品缺能力（等 Core / 重试无用）与这一步真实失败（修好后可重试）。
    // 用同一句话概括它们，用户就无法判断该等还是该修。
    li.title = (p.status === 'blocked' && stepFailed)
      ? '这一步真实失败：修好原因后可重试'
      : (p.status === 'skipped' ? (p.reason || STATUS_TITLE.skipped) : (STATUS_TITLE[p.status] || ''));
    list.appendChild(li);
  }

  $('session-state').textContent = view.message || '';
  $('session-stage').textContent = view.running
    ? '正在执行…'
    : (view.state === 'BLOCKED'
      ? (stepFailed ? '已停止 · 这一步真实失败' : '已停止 · 能力未就绪')
      : '');

  // 完成模式徽章：持续可见。跳过分解与结构仍然要导出、要复检，但人必须知道自己在哪条路上。
  const mode = $('session-mode');
  if (view.modeLabel) {
    mode.textContent = view.modeLabel;
    mode.hidden = false;
    mode.classList.toggle('deep', view.mode === 'DEEP');
  } else {
    mode.hidden = true;
  }

  // 深度受阻 → 补救动作必须看得见（2026-10-04 裁定）。三点纪律：
  //   ① 只有人能按（两级确认），系统绝不自动切换；
  //   ② 文案说清这条路不做逐轨音准/节奏修正，也不删除已有分解结果；
  //   ③ 已经在快速模式、或已经有候选/选定（流程走过去了）时不再提示切换。
  const sw = view.fastSwitch || {};
  const canSwitch = Boolean(sw.available) && !view.running;
  const remedy = $('session-remedy');
  remedy.hidden = !canSwitch;
  if (canSwitch) {
    $('session-remedy-title').textContent = view.state === 'BLOCKED'
      ? '深度完成暂不可用' : '也可以改用快速完成（仅立体声）';
    // 产品面只显示投影算好的白话一句（原因 + 可怎么办）；
    // 工程细节（缺哪个文件、哪项能力）在「制作详情」层，不摆到主界面。
    $('session-remedy-reason').textContent = sw.summary
      || '可逆性验证或逐轨处理能力尚未就绪。你可以改用整轨两档完成（快速完成：仅立体声）。';
    $('session-remedy-switch').textContent = sw.label || '切换到快速完成（仅立体声）';
  } else {
    hideQuickConfirm();
  }

  // 「开始完成」只在真能继续时开放。缺能力时它不该看起来还能点——一个点了没反应的按钮，
  // 会让人以为是应用坏了。但**这一步真实失败**不同：原因可能是环境问题（依赖没装、
  // 磁盘满），人修好之后必须能重试，否则只能重开应用。
  const retryable = view.state === 'BLOCKED' && stepFailed && !view.running;
  const canStart = (view.state === 'READY' || retryable) && !view.running && !sessionState.busy;
  $('session-start').disabled = !canStart;
  $('session-start').textContent = retryable
    ? '重试（已完成的步骤会跳过）'
    : ((view.state === 'REVIEW' || view.state === 'DONE')
      ? '重新完成（已完成的步骤会跳过）' : '开始完成');

  // 阻断时展开详情，让「哪一步、缺什么能力 / 失败原因」直接可见，而不是藏在一个折叠面板里
  if (view.state === 'BLOCKED') toggleSessionDetail(true);
  if (fast && view.running) toggleSessionDetail(false);
}

async function startCompletion() {
  const caseDir = state.caseDir;
  if (!caseDir || sessionState.busy) return;
  if (sessionState.view && sessionState.view.running) return;
  sessionState.busy = true;
  $('session-start').disabled = true;
  $('session-state').textContent = '正在执行…';

  let res;
  try { res = await window.moodify.sessionStart(caseDir); }
  catch (err) { res = { ok: false, reason: (err && err.message) || String(err) }; }
  sessionState.busy = false;
  if (state.caseDir !== caseDir) return; // 换世界守卫

  if (res && res.phases) {
    renderSession(res);
  } else {
    // 连投影都没拿到：如实说，不编造进度
    $('session-state').textContent = '启动失败：' + ((res && res.reason) || '未知原因');
    $('session-start').disabled = false;
  }
  await refreshSession();
  await refreshPipeline();
  await refreshTuning();
}

// ——— ④修音 / ⑤复合 / ⑦选定（V4 主流程）———
//
// 产品方向（人类 2026-10-04 采纳）：**逆向工程 · 多轨复合**。
// 一次修音产出**两档完整方案**（A 保守 conservative / B 充分 full），由系统生成，人只负责听和选。
// 选定有**三个**出口：A / B / **保留原版**——两档都不如原版时，「回原版」是一条真路，
// 也是「最小变换」从口号变成规则的地方。
//
// 本段只做「发起」与「呈现」：
//   快速完成的两档整轨渲染 = Core `tuning render-pair`（**已实现**，MIP-0002 附录 A）
//   深度路径的逐轨修音 / 复合 = Core（**尚未实现** → main 侧显式拒绝 TUNABLE_CORE_NOT_AVAILABLE）
//   ⑥ 复检      = 对 A、B 各跑一次 Core 既有检测，再由 main 侧做三方对齐
//   ⑧ 导出      = Core 的 finishing export
// 渲染层不实现 DSP、不算响度、不替用户做选择，也绝不把「Core 未就绪」显示成「已处理」。

const tuningState = {
  caseDir: null,
  pairs: [],
  decisions: [],
  gates: null,
  // ⑦ 选定 的准入：按 pair_id 存「还差什么」。按钮的可点状态必须与 main 侧的
  // validateDecision 完全一致——否则会出现「按钮能点，点了被拒」这种看起来很坏的行为。
  decisionBlockers: {},
  activePairId: null,
  busy: false,
  // 决定 id 的单调计数：每次**显式点击**生成新的 requestId，于是「改选」会真的追加一条记录；
  // 同一个点击的重试仍然幂等（id 在这一次动作内不变）。
  decisionSeq: 0,
};

/**
 * A/B 审听工作台状态（Phase 2.2）。
 *
 * `tab` = 当前**页面**（在看哪个候选），`playing` = 当前**真正加载在播放器里的音源**。
 * 两者必须分开记录：浏览 B 但正在听原版时，界面要同时说清这两件事，禁止拿页签冒充播放源。
 */
const review = {
  pairId: null,
  evidence: null,      // tuning:evidence 的结果（报告 / 频谱 / 图表 / 卡片 / 处理链）
  alignment: null,     // tuning:recheck 的三方对齐表（完整表与卡片的数据源）
  tab: 'A',            // 当前页面：A | B
  playing: null,       // 当前播放源：ORIGINAL | A | B | null
  ws: null,            // 唯一的 transport（一个播放器，三个音源）
  loadToken: 0,        // 竞态守卫：只接受最后一次加载的结果
  bufferCache: new Map(), // 最多缓存 2 个已解码 buffer，长曲不至于把内存吃光
  zoomPx: null,
  tableOpen: false,
  tableFilter: 'changed',
  busy: false,
};

function initTuning() {
  // NOTE: rail-tuning 由 initPipeline() 接到 enterPipeline()，不直接进本视图——
  // 入口必须落在第一个未完成的阶段，而不是直接跳到处理。
  $('tuning-run').addEventListener('click', runTuningRender);
  $('tuning-recheck').addEventListener('click', runTuningRecheck);
  initReview();
  initCompletion();
}

function resetTuningWorld() {
  destroyReviewTransport();
  tuningState.caseDir = null;
  tuningState.pairs = [];
  tuningState.decisions = [];
  tuningState.gates = null;
  tuningState.decisionBlockers = {};
  tuningState.activePairId = null;
  tuningState.decisionSeq = 0;
  review.pairId = null;
  review.evidence = null;
  review.alignment = null;
  review.tab = 'A';
  review.playing = null;
  review.tableOpen = false;
  review.tableFilter = 'changed';
  completion.state = null;
  completion.quiet = false;
  completion.detailsOpen = false;
  completion.lastStatus = '';
  document.body.classList.remove('cp-quiet');
  $('completion').hidden = true;
  $('session-detail').hidden = true;
  $('tuning-pairs').textContent = '';
  $('tuning-status').textContent = '';
  $('tuning-note').textContent = '';
  $('tuning-mode').textContent = '';
  $('review').hidden = true;
}

function activePair() {
  return tuningState.pairs.find((p) => p.pair_id === tuningState.activePairId) || null;
}

function decisionForPair(pairId) {
  const rows = tuningState.decisions.filter((d) => d.pair_id === pairId);
  return rows.length ? rows[rows.length - 1] : null;
}

async function openTuning() {
  if (!state.caseDir) return;
  selectView('tuning');
  tuningState.caseDir = state.caseDir;
  sessionState.caseDir = state.caseDir;
  await refreshSession();
  // 完成层优先：已完成的作品默认落在作品上，技术细节在「查看制作详情」后面。
  completion.detailsOpen = false;
  await refreshCompletion();
  await refreshTuning();
}

async function refreshTuning() {
  const caseDir = tuningState.caseDir || state.caseDir;
  if (!caseDir) return null;
  let res;
  try { res = await window.moodify.tuningPairs(caseDir); } catch { return null; }
  if (!res || !res.ok || state.caseDir !== caseDir) return null; // 换世界守卫
  tuningState.pairs = res.pairs || [];
  tuningState.decisions = res.decisions || [];
  tuningState.gates = res.gates || null;
  tuningState.decisionBlockers = res.decisionBlockers || {};
  tuningState.activePairId = res.currentPairId || tuningState.activePairId;
  renderTuning();
  await refreshReview();
  return res;
}

function renderTuning() {
  const g = tuningState.gates || {};

  // 完成模式徽章：深度 / 快速（仅立体声）。不标注就是骗人。
  $('tuning-mode').textContent = g.modeLabel || '';

  renderTuningStatus(g);
  renderTuningPairs();
}

/** 差什么就说差什么——「需要先完成前面的阶段」等于没说。 */
function renderTuningStatus(g) {
  const paint = (text) => { $('tuning-status').textContent = text; };
  const first = (...arrs) => {
    for (const a of arrs) if (Array.isArray(a) && a.length) return a[0];
    return null;
  };

  if (!tuningState.pairs.length) {
    const why = first(g.tuneBlockers, g.composeBlockers);
    // 快速完成是另一条路：它不需要分轨与 MIDI，所以提示也不能拿「缺分轨」来解释。
    if (g.mode === 'FAST_STEREO_ONLY') {
      paint('快速完成（仅立体声）：尚无候选。点「开始完成」或上面的「只生成两档」，'
        + 'Core 会一次产出 A 保守 / B 充分两个完整整轨候选。');
    } else {
      paint(why
        ? `还不能生成修音：${why}`
        : '尚无修音对。点「生成两档修音」让系统产出保守 / 充分两档完整方案。');
    }
    return;
  }

  const p = activePair();
  if (!p) { paint(''); return; }
  const parts = [];
  parts.push(p.mode === 'FAST_STEREO_ONLY' ? '快速（仅立体声）' : '深度');
  parts.push(`A/B 修音：${p.tuned ? '两侧齐备' : '未完成'}`);
  parts.push(`合成：${p.composed ? '两侧齐备' : '未完成'}`);
  parts.push(`复检：${p.has_recheck ? '已完成' : '未做'}`);
  const d = decisionForPair(p.pair_id);
  parts.push(`选定：${d ? exitLabel(d.kept) : '未选'}`);
  // ⑦ 的准入附在后面：差什么就说差什么。「需要先完成前面的阶段」等于没说。
  const blockers = tuningState.decisionBlockers[p.pair_id] || [];
  paint(blockers.length
    ? `${parts.join(' · ')} —— 还不能选定：${blockers.join('；')}`
    : parts.join(' · '));
}

function exitLabel(kept) {
  if (kept === 'A') return 'A（保守）';
  if (kept === 'B') return 'B（充分）';
  if (kept === 'ORIGINAL') return '保留原版';
  return kept;
}

function renderTuningPairs() {
  const box = $('tuning-pairs');
  box.textContent = '';
  for (const p of tuningState.pairs) {
    const row = document.createElement('button');
    row.className = 'pair-row';
    if (p.pair_id === tuningState.activePairId) row.classList.add('active');
    const d = decisionForPair(p.pair_id);
    if (d) row.classList.add('chosen');

    const name = document.createElement('span');
    name.className = 'sv-name';
    name.textContent = p.pair_id + (p.mode === 'FAST_STEREO_ONLY' ? ' · 快速' : ' · 深度');
    row.appendChild(name);

    const badge = document.createElement('span');
    badge.className = 'sv-badge';
    if (p.composed) { badge.textContent = 'A/B 可听'; }
    else if (p.tuned) { badge.textContent = '已修音，待合成'; badge.classList.add('sv-review'); }
    else { badge.textContent = '未完成'; badge.classList.add('sv-review'); }
    row.appendChild(badge);

    if (d) {
      const tick = document.createElement('span');
      tick.className = 'sv-chosen';
      tick.textContent = `✓ ${exitLabel(d.kept)}`;
      row.appendChild(tick);
    }

    row.addEventListener('click', () => selectPair(p.pair_id));
    box.appendChild(row);
  }
}

async function selectPair(pairId) {
  tuningState.activePairId = pairId || null;
  renderTuningPairs();
  renderTuningStatus(tuningState.gates || {});
  await refreshReview();
}

// ——— 生成两档（Core 未就绪时显式拒绝）———

async function runTuningRender() {
  const caseDir = tuningState.caseDir || state.caseDir;
  if (!caseDir || tuningState.busy) return;
  tuningState.busy = true;
  $('tuning-run').disabled = true;
  const fast = tuningState.gates && tuningState.gates.mode === 'FAST_STEREO_ONLY';
  $('tuning-status').textContent = fast
    ? '正在让 Core 生成两档整轨候选（A 保守 / B 充分）…'
    : '正在请求 Core 生成两档修音…';
  let res;
  try { res = await window.moodify.tuningRender(caseDir); }
  catch (err) { res = { ok: false, reason: (err && err.message) || String(err) }; }
  tuningState.busy = false;
  $('tuning-run').disabled = false;
  if (tuningState.caseDir !== caseDir && state.caseDir !== caseDir) return;

  if (!res || !res.ok) {
    // 拒绝是预期行为，不是故障——把原因说清楚，别把机器码丢给用户
    const why = (res && res.reason) || '';
    if (why === 'TUNABLE_CORE_NOT_AVAILABLE') {
      $('tuning-status').textContent = '深度路径的逐轨修音与复合能力尚未就绪（见 MIP-0002）。'
        + '本壳不会生成任何逐轨修音产物；如果想先走通闭环，请显式选择「快速完成（仅立体声）」。';
    } else if (why === 'TUNE_LOCKED') {
      const b = (res.blockers && res.blockers[0]) || '前置条件未满足';
      $('tuning-status').textContent = `还不能生成：${b}`;
    } else if (why === 'RENDER_PAIR_FAILED') {
      const leftover = res.leftover ? `（磁盘上留下了 ${res.leftover}，本次未发布为正式 pair）` : '（没有留下任何产物）';
      $('tuning-status').textContent = `Core 未能生成两档候选：${(res.detail || '').trim()} ${leftover}`;
    } else if (why === 'PAIR_INCOMPLETE_ON_DISK') {
      $('tuning-status').textContent = `${res.detail} 这一对**不会**被当成完整候选。`;
    } else if (why === 'NO_SOURCE') {
      $('tuning-status').textContent = res.detail || '未找到源音频。';
    } else {
      $('tuning-status').textContent = '生成失败：' + why;
    }
    return;
  }

  $('tuning-status').textContent = fast
    ? `已生成两档整轨候选（A 保守 / B 充分）。请点「复检（重跑检测）」对 A、B 各跑一次完整检测，`
      + '然后同位置试听并选定。'
    : '已生成两档候选。';
  await refreshTuning();
  await refreshPipeline();
  await refreshSession();
}

// ——— ⑥ 复检 ———

async function runTuningRecheck() {
  const caseDir = tuningState.caseDir;
  const pairId = tuningState.activePairId;
  if (!caseDir || !pairId || tuningState.busy) return;
  tuningState.busy = true;
  $('tuning-recheck').disabled = true;
  $('tuning-status').textContent = '正在对 A、B 各重跑一次完整检测…（可能耗时数分钟）';
  let res;
  try { res = await window.moodify.tuningRecheckRun(caseDir, pairId); }
  catch (err) { res = { ok: false, reason: (err && err.message) || String(err) }; }
  tuningState.busy = false;
  $('tuning-recheck').disabled = false;
  if (tuningState.caseDir !== caseDir) return;

  if (!res || !res.ok) {
    const why = (res && res.reason) || '';
    $('tuning-status').textContent = why === 'NEED_BOTH_SIDES'
      ? '还不能复检：A、B 两侧都需先有合成结果。'
      : `复检失败：${why}`;
    return;
  }
  // 复检产物就是审听工作台的数据源：刷新它，让新对齐表/卡片立刻可见。
  await refreshTuning();
}

// ——— ⑦ 选定（三出口）与 ⑧ 导出 ———
//
// 选择永远只有一条权威通道：`tuning:decision`（main 侧的 validateDecision）。
// 渲染层不维护私有选择状态，也不在本地「先选中再同步」——选定成功以账本回读为准。
//
// requestId 每次**显式点击**生成一次：同一次动作的重试仍然幂等，而「改选」会真的追加一条
// 记录（否则 A→B→A 的第三次会被当成第一次的重复，账本留在 B 而界面显示 A）。

function nextDecisionRequestId(pairId, kept) {
  tuningState.decisionSeq += 1;
  return `keep:${pairId}:${kept}:${tuningState.decisionSeq}`;
}

async function keepExit(kept) {
  const caseDir = tuningState.caseDir;
  const pairId = tuningState.activePairId;
  if (!caseDir || !pairId || tuningState.busy) return;
  tuningState.busy = true;
  const requestId = nextDecisionRequestId(pairId, kept);
  let res;
  try { res = await window.moodify.tuningDecision(caseDir, pairId, kept, 'creator', requestId); }
  catch (err) { res = { ok: false, reason: (err && err.message) || String(err) }; }
  tuningState.busy = false;
  if (tuningState.caseDir !== caseDir) return;

  if (!res || !res.ok) {
    // 拒绝是预期行为：把原因说清楚，别把机器码丢给用户
    const why = (res && res.reason) || '';
    if (why === 'PAIR_NOT_COMPLETE') {
      const first = (res.blockers && res.blockers[0]) || '候选或复检还不完整';
      $('tuning-note').textContent = `还不能选定：${first}。`
        + '「保留原版」也是三个出口之一，同样要等 A / B 两个完整候选与复检齐备之后才可选。';
    } else if (why === 'REQUEST_ID_CONFLICT') {
      $('tuning-note').textContent = '记录失败：同一次选择被用于不同的出口或不同的修音对，已拒绝写入。';
    } else {
      $('tuning-note').textContent = '记录失败：' + why;
    }
    return;
  }
  $('tuning-note').textContent = `已记录：${exitLabel(kept)}。`
    + (kept === 'ORIGINAL' ? '两档都不如原版时，这是正确的选择。' : '');
  await refreshTuning();   // 账本回读 → 标签、按钮、导出目标一起更新
  // 选定之后自然收束到完成层（没有庆祝弹层、没有提示音）：先同步留存记录，再显示作品。
  await window.moodify.keepsakeSync(caseDir).catch(() => null);
  completion.detailsOpen = false;
  const entered = await refreshCompletion();
  if (entered) {
    completion.lastStatus = '';
    $('cp-status').textContent = '';
    // 焦点落到「从头听」，但不自动播放
    if (typeof $('cp-listen').focus === 'function') $('cp-listen').focus();
  }
}

async function exportChosen() {
  const caseDir = tuningState.caseDir;
  const pairId = tuningState.activePairId || (completion.state && completion.state.pairId);
  if (!caseDir || !pairId) return;
  const note = (text) => {
    // 导出反馈同时写到「制作详情」与完成层，谁在前面都不会看不到
    $('tuning-note').textContent = text;
    if (completion.state && completion.state.complete) $('cp-status').textContent = text;
  };
  const d = decisionForPair(pairId);
  if (!d) { note('请先选定一个出口再导出。'); return; }
  note('正在导出…');
  let res;
  try { res = await window.moodify.tuningExport(caseDir, pairId, d.kept); }
  catch (err) { note('导出失败：' + ((err && err.message) || err)); return; }
  if (!res || !res.ok) {
    if (res && res.canceled) { note('已取消导出。'); return; }
    const why = (res && res.reason) || '';
    if (why === 'CANDIDATES_INCOMPLETE') {
      const first = (res.blockers && res.blockers[0]) || '候选或复检产物已不完整';
      note(`导出被拒绝：${first}。选定必须仍然被两个完整候选与复检支撑——产物没了，这一步就退回未完成。`);
      return;
    }
    note('导出失败：' + why);
    return;
  }
  note(`已导出（${exitLabel(d.kept)}）：${res.path}`);
}
// ——— A/B 审听工作台（Phase 2.2）———
//
// 首屏先回答两件事：**我正在听谁**、**它相对原版变了什么**。每一条数据都来自真实产物：
//   音频      pair/<side>/mix.wav（原版 = case 源）——经 tuning:audio 读字节
//   对齐表    tuning:recheck（recheck.js 从三份 Core report 摊出来的对齐结果）
//   卡片/频谱/图表/处理链  tuning:evidence（main 侧从候选自己那份 report + plan/evidence 推导）
// 本层不做测量、不跑分析、不缩放波形去制造差异、不生成任何「谁更好」的结论。

const REV_SIDE_LABEL = { ORIGINAL: '原版', A: 'A（保守）', B: 'B（充分）' };
const REV_TAB_LABEL = { A: 'A · 保守', B: 'B · 充分' };

function revSideLabel(side) { return REV_SIDE_LABEL[side] || side; }

function initReview() {
  $('rv-play').addEventListener('click', () => reviewTogglePlay());
  $('rv-src-original').addEventListener('click', () => reviewLoadSide('ORIGINAL'));
  $('rv-src-a').addEventListener('click', () => reviewLoadSide('A'));
  $('rv-src-b').addEventListener('click', () => reviewLoadSide('B'));
  $('rv-tab-a').addEventListener('click', () => reviewSelectTab('A'));
  $('rv-tab-b').addEventListener('click', () => reviewSelectTab('B'));
  $('rv-zoom-out').addEventListener('click', () => reviewSetZoom(1 / 1.6));
  $('rv-zoom-in').addEventListener('click', () => reviewSetZoom(1.6));
  $('rv-zoom-fit').addEventListener('click', () => { review.zoomPx = null; applyReviewZoom(); });
  $('rv-table-toggle').addEventListener('click', () => {
    review.tableOpen = !review.tableOpen;
    renderReviewTable();
  });
  for (const input of document.querySelectorAll('input[name="rv-filter"]')) {
    input.addEventListener('change', () => {
      review.tableFilter = input.value;
      renderReviewTable();
    });
  }
  $('rv-choose').addEventListener('click', () => keepExit(review.tab));
  $('rv-keep-original').addEventListener('click', () => keepExit('ORIGINAL'));
  $('rv-export-run').addEventListener('click', exportChosen);
}

/** 工作台刷新：当前 pair 的证据包 + 三方对齐表。数据不全就整体隐藏，绝不用别的图占位。 */
async function refreshReview() {
  const caseDir = tuningState.caseDir || state.caseDir;
  const pairId = tuningState.activePairId;
  if (!caseDir || !pairId) { $('review').hidden = true; return; }
  let evidence;
  let alignment;
  try { evidence = await window.moodify.tuningEvidence(caseDir, pairId); } catch { evidence = null; }
  try { alignment = await window.moodify.tuningRecheck(caseDir, pairId); } catch { alignment = null; }
  if (state.caseDir !== caseDir || tuningState.activePairId !== pairId) return; // 换世界/换 pair 守卫

  if (!evidence || !evidence.ok || !alignment || !alignment.ok) {
    // 没有复检就没有可审听的对齐证据：工作台不出现（选择本来也被门禁锁着）。
    review.evidence = null;
    review.alignment = null;
    review.pairId = pairId;
    applyWorkspaceMode();
    return;
  }
  review.pairId = pairId;
  review.evidence = evidence;
  review.alignment = alignment.recheck;
  // 播放器：如果当前播放源在这个 pair 里不可用（缺 mix.wav），退回原版，不留一个假状态。
  const wanted = review.playing || review.tab;
  const usable = (side) => Boolean(evidence.sides[side] && evidence.sides[side].audio);
  if (!usable(wanted)) review.playing = null;

  renderReviewChrome();
  renderReviewPage();
  applyWorkspaceMode();
  if (review.playing === null) await reviewLoadSide(usable('A') ? 'A' : 'ORIGINAL');
}

/**
 * 谁在前面：完成层是第一视图，A/B 审听是它的第二层（同一份数据、同一个播放器）。
 * 两者永远只显示一个，避免出现「两套完成态」。
 */
function applyWorkspaceMode() {
  const s = completion.state;
  const complete = Boolean(s && s.complete);
  const showDetails = completion.detailsOpen || !complete;
  $('view-tuning').classList.toggle('cp-complete', complete && !showDetails);
  $('completion').hidden = !(complete && !showDetails);
  $('review').hidden = !(showDetails && review.evidence);
}

function renderReviewChrome() {
  const ev = review.evidence;
  // 当前页面（在看哪个候选）——与「正在试听」是两件事，永远同时显示。
  $('rv-page').textContent = REV_TAB_LABEL[review.tab] || '—';
  for (const [id, side] of [['rv-tab-a', 'A'], ['rv-tab-b', 'B']]) {
    const btn = $(id);
    const bundle = ev.sides[side];
    btn.classList.toggle('active', review.tab === side);
    btn.classList.toggle('playing', review.playing === side);
    btn.classList.toggle('chosen', Boolean(decisionForPair(review.pairId)
      && decisionForPair(review.pairId).kept === side));
    btn.classList.toggle('unavailable', !(bundle && bundle.audio));
    const badges = [];
    if (!(bundle && bundle.audio)) badges.push('不可用');
    if (review.playing === side) badges.push('当前试听');
    if (decisionForPair(review.pairId) && decisionForPair(review.pairId).kept === side) badges.push('已选择');
    btn.textContent = `${REV_TAB_LABEL[side]}${badges.length ? ` · ${badges.join(' · ')}` : ''}`;
    btn.disabled = !(bundle && bundle.audio);
  }
  // 三个真实音源：填充色 + 文字 + 圆点三重表达，不靠颜色单独承载信息。
  for (const [id, side] of [['rv-src-original', 'ORIGINAL'], ['rv-src-a', 'A'], ['rv-src-b', 'B']]) {
    const btn = $(id);
    const bundle = ev.sides[side];
    const usable = Boolean(bundle && bundle.audio);
    btn.classList.toggle('active', review.playing === side);
    btn.disabled = !usable;
    btn.title = usable ? `试听${revSideLabel(side)}` : `${revSideLabel(side)}暂不可试听`;
    if (review.playing === side) btn.setAttribute('aria-current', 'true');
    else btn.removeAttribute('aria-current');
  }
  const playing = $('rv-playing');
  playing.textContent = review.playing ? revSideLabel(review.playing) : '—';
  playing.className = 'rv-playing' + (review.playing ? ` rv-${review.playing.toLowerCase()}` : ' rv-none');
  const d = decisionForPair(review.pairId);
  $('rv-choice-state').textContent = d
    ? `当前选择：${exitLabel(d.kept)}（已记入账本，可改选）`
    : '当前选择：未选定 —— 选定之后才能导出。';
}

/** 一个候选页：身份 → 波形 → 频谱 → 指标 → 图表 → 处理链 → 完整表 → 动作。 */
function renderReviewPage() {
  const ev = review.evidence;
  const side = review.tab;
  const bundle = ev.sides[side];
  const other = ev.sides[side === 'A' ? 'B' : 'A'];
  $('rv-wave-title').textContent = `${REV_TAB_LABEL[side]} 候选波形`;

  // ——— 身份卡（诚实说明永远在这里）———
  const identity = $('rv-identity');
  identity.textContent = '';
  const h = document.createElement('h3');
  h.className = 'rv-h';
  h.textContent = revSideLabel(side);
  identity.appendChild(h);
  const facts = document.createElement('p');
  facts.className = 'muted caption';
  const mode = (ev.mode === 'FAST_STEREO_ONLY') ? '快速完成（仅立体声）' : (ev.mode || '—');
  facts.textContent = `${mode} · ${bundle.calibrationStatus || '未标注校准状态'}`
    + ' · 机器已处理并测量；是否更好由你试听决定。';
  identity.appendChild(facts);
  if (!bundle.audio) {
    const warn = document.createElement('p');
    warn.className = 'rv-missing';
    warn.textContent = '这一侧的候选音频不可用（缺 mix.wav）：不可试听、也不可选定。';
    identity.appendChild(warn);
  }

  renderReviewSpectra();
  renderReviewMetrics();
  renderReviewCharts();
  renderReviewChain();
  renderReviewTable();
  renderReviewActions();
  // 导出目标（与当前 pair 的账本一致）
  const d = decisionForPair(review.pairId);
  $('rv-export-target').textContent = d
    ? `导出对象：${exitLabel(d.kept)}（pair ${review.pairId}）`
    : '导出对象：尚未选定';
  $('rv-export-run').disabled = !d;
  void other;
}

function renderReviewMissing(box, text) {
  box.textContent = '';
  const p = document.createElement('p');
  p.className = 'rv-missing';
  p.textContent = text;
  box.appendChild(p);
}

/** 频谱：原版 vs 当前候选，并排、同显示尺寸、图例常驻。图来自各自复检报告，缺就写缺。 */
function renderReviewSpectra() {
  const box = $('rv-spectra');
  const ev = review.evidence;
  const side = review.tab;
  box.textContent = '';
  const head = document.createElement('h3');
  head.className = 'rv-h';
  head.textContent = `频谱：原版 vs ${REV_TAB_LABEL[side]}`;
  box.appendChild(head);
  const note = document.createElement('p');
  note.className = 'muted caption';
  note.textContent = '两张图由 Core 的同一导出器分别从各自 report 生成（log 频谱）；本层不重绘、不缩放、不解释差异好坏。';
  box.appendChild(note);

  const columns = [
    { key: 'original', label: '原版', bundle: ev.sides.ORIGINAL },
    { key: 'candidate', label: REV_TAB_LABEL[side], bundle: ev.sides[side] },
  ];
  const grid = document.createElement('div');
  grid.className = 'rv-grid-2';
  for (const col of columns) {
    const cell = document.createElement('div');
    cell.className = 'rv-cell';
    const cap = document.createElement('p');
    cap.className = 'rv-cap';
    const found = (col.bundle.spectra || []).find((s) => s.key === 'spectrum_log');
    cap.textContent = found ? `${col.label} · 频谱（log）` : `${col.label} · 缺频谱`;
    cell.appendChild(cap);
    if (found) {
      const img = document.createElement('img');
      img.src = fileUrl(found.path);
      img.alt = `${col.label} 频谱`;
      cell.appendChild(img);
    } else {
      const miss = document.createElement('p');
      miss.className = 'rv-missing';
      miss.textContent = '该复检报告未提供频谱';
      cell.appendChild(miss);
    }
    grid.appendChild(cell);
  }
  box.appendChild(grid);
}

/** 关键指标卡：值全部来自 recheck；缺就写「不可对齐」，不给颜色暗示、不给综合分。 */
function renderReviewMetrics() {
  const box = $('rv-metrics');
  const cards = (review.evidence.sides[review.tab].cards) || [];
  box.textContent = '';
  const head = document.createElement('h3');
  head.className = 'rv-h';
  head.textContent = `关键指标：原版 → ${REV_TAB_LABEL[review.tab]}`;
  box.appendChild(head);
  if (!cards.length) { renderReviewMissing(box, '这份复检没有提供可用于审听的指标。'); return; }
  const grid = document.createElement('div');
  grid.className = 'rv-cards';
  for (const c of cards) {
    const card = document.createElement('div');
    card.className = 'rv-card';
    const name = document.createElement('div');
    name.className = 'rv-card-name';
    name.textContent = c.label;
    card.appendChild(name);
    if (c.status === 'alignable') {
      const val = document.createElement('div');
      val.className = 'rv-card-value';
      val.textContent = `${revNum(c.original, c.digits)} → ${revNum(c.value, c.digits)}`;
      card.appendChild(val);
      const delta = document.createElement('div');
      delta.className = 'rv-card-delta';
      delta.textContent = `Δ ${c.delta > 0 ? '+' : ''}${revNum(c.delta, c.digits)} ${c.unit}`;
      card.appendChild(delta);
      const unit = document.createElement('div');
      unit.className = 'muted caption';
      unit.textContent = `单位：${c.unit} · 指标 id：${c.id}`;
      card.appendChild(unit);
    } else {
      const na = document.createElement('div');
      na.className = 'rv-card-na';
      na.textContent = '不可对齐';
      card.appendChild(na);
      const why = document.createElement('div');
      why.className = 'muted caption';
      why.textContent = c.reason || '复检未说明原因';
      card.appendChild(why);
    }
    grid.appendChild(card);
  }
  box.appendChild(grid);
  const note = document.createElement('p');
  note.className = 'muted caption';
  note.textContent = 'Δ 只表示数学方向，不表示审美好坏；本表不出评分、不做推荐。';
  box.appendChild(note);
}

function revNum(value, digits) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '—';
  return value.toFixed(digits === undefined ? 3 : digits);
}

/** 图表：原版 | 当前候选。候选图按需由 Core 导出器生成（同一份 report），缺就写缺。 */
async function renderReviewCharts() {
  const box = $('rv-charts');
  const ev = review.evidence;
  const side = review.tab;
  const caseDir = tuningState.caseDir;
  const pairId = review.pairId;
  box.textContent = '';
  const head = document.createElement('h3');
  head.className = 'rv-h';
  head.textContent = `检测图表：原版 | ${REV_TAB_LABEL[side]}`;
  box.appendChild(head);

  const candidate = ev.sides[side];
  let charts = candidate.charts || [];
  if (!charts.length && candidate.audio !== undefined) {
    const note = document.createElement('p');
    note.className = 'muted caption';
    note.textContent = '正在生成这一侧的检测图表…';
    box.appendChild(note);
    let res;
    try { res = await window.moodify.tuningCharts(caseDir, pairId, side); } catch { res = null; }
    if (state.caseDir !== caseDir || review.pairId !== pairId || review.tab !== side) return;
    if (res && res.ok) {
      charts = res.charts || [];
      // 只刷新这一侧的图表数据，不重跑整页
      candidate.charts = charts;
    } else {
      renderReviewMissing(box, `这一侧的检测图表不可用：${(res && res.reason) || '生成失败'}（不会用原版图占位）`);
      return;
    }
  }
  box.textContent = '';
  box.appendChild(head);

  if (!charts.length) {
    renderReviewMissing(box, '该复检报告未提供检测图表（不会用原版图占位）。');
    return;
  }
  for (const chart of charts) {
    const row = document.createElement('div');
    row.className = 'rv-chart-row';
    const cap = document.createElement('p');
    cap.className = 'rv-cap';
    cap.textContent = chart.label;
    row.appendChild(cap);
    const grid = document.createElement('div');
    grid.className = 'rv-grid-2';
    const originalChart = (ev.sides.ORIGINAL.charts || []).find((c) => c.key === chart.key);
    for (const [label, found] of [['原版', originalChart], [REV_TAB_LABEL[side], chart]]) {
      const cell = document.createElement('div');
      cell.className = 'rv-cell';
      const sub = document.createElement('p');
      sub.className = 'rv-cap';
      sub.textContent = found ? label : `${label} · 缺图`;
      cell.appendChild(sub);
      if (found) {
        const img = document.createElement('img');
        img.src = fileUrl(found.path);
        img.alt = `${label} ${chart.label}`;
        cell.appendChild(img);
      } else {
        const miss = document.createElement('p');
        miss.className = 'rv-missing';
        miss.textContent = '该报告未提供此图';
        cell.appendChild(miss);
      }
      grid.appendChild(cell);
    }
    row.appendChild(grid);
    box.appendChild(row);
  }
  // 原版图表同样按需生成（只用于对照，不替代候选图）
  if (!(ev.sides.ORIGINAL.charts || []).length) {
    try {
      const res = await window.moodify.tuningCharts(caseDir, pairId, 'ORIGINAL');
      if (res && res.ok) ev.sides.ORIGINAL.charts = res.charts || [];
    } catch { /* 对照图缺失就保持缺失，绝不用候选图顶替 */ }
  }
}

/** 处理链：只读展示 Core 写的算子与参数 + Mix Graph digest（解释「为什么不同」）。 */
function renderReviewChain() {
  const box = $('rv-chain');
  const bundle = review.evidence.sides[review.tab];
  box.textContent = '';
  const head = document.createElement('h3');
  head.className = 'rv-h';
  head.textContent = '实际处理链（只读）';
  box.appendChild(head);
  if (!bundle.chain || !bundle.chain.nodes.length) {
    renderReviewMissing(box, '这一侧没有可读的处理链产物（缺 plan/evidence）。');
    return;
  }
  const chain = document.createElement('p');
  chain.className = 'rv-chain';
  chain.textContent = bundle.chain.nodes.map((n) => n.type).join(' → ');
  box.appendChild(chain);
  const meta = document.createElement('p');
  meta.className = 'muted caption';
  meta.textContent = `Mix Graph digest：${(bundle.chain.graphDigest || '—').slice(0, 16)}…`
    + ` · 引擎：${bundle.chain.engineVersion || '—'}`
    + ` · 复合：${bundle.chain.composite === 'identity_single_track' ? '单轨恒等（整轨两档）' : (bundle.chain.composite || '—')}`
    + ` · 待人确认：${bundle.chain.reviewRequired ? '是' : '否'}`;
  box.appendChild(meta);
  const details = document.createElement('details');
  const summary = document.createElement('summary');
  summary.textContent = '展开实际参数';
  details.appendChild(summary);
  const pre = document.createElement('pre');
  pre.className = 'rv-pre';
  pre.textContent = JSON.stringify(bundle.chain.nodes, null, 2);
  details.appendChild(pre);
  box.appendChild(details);
  const gates = document.createElement('p');
  gates.className = 'muted caption';
  const passed = (bundle.chain.checks || []).filter((g) => g.passed).length;
  gates.textContent = `Core 硬门禁：${passed}/${(bundle.chain.checks || []).length} 通过`
    + (bundle.chain.checks || []).map((g) => ` · ${g.gate}`).join('');
  box.appendChild(gates);
}

/** 完整复检表（审计层）：默认折叠，只按当前候选过滤；不可对齐项保留真实原因。 */
function renderReviewTable() {
  const box = $('rv-table');
  const filters = $('rv-table-filters');
  const toggle = $('rv-table-toggle');
  const r = review.alignment;
  const side = review.tab;
  if (!r) { box.textContent = ''; box.hidden = true; filters.hidden = true; return; }
  const total = r.summary.alignable_count + r.summary.not_alignable_count;
  toggle.textContent = review.tableOpen
    ? `收起完整复检表（${total} 项）`
    : `查看全部 ${total} 项复检指标`;
  box.hidden = !review.tableOpen;
  filters.hidden = !review.tableOpen;
  if (!review.tableOpen) { box.textContent = ''; return; }

  const head = document.createElement('p');
  head.className = 'muted caption';
  head.textContent = `可比 ${r.summary.alignable_count} 项 · 不可比 ${r.summary.not_alignable_count} 项`
    + ` · 本页只列「原版 / ${REV_TAB_LABEL[side]}」两列（本表只报变了什么，不报更好）`;

  const table = document.createElement('table');
  table.className = 'data rv-data';
  const thead = document.createElement('thead');
  thead.innerHTML = `<tr><th>指标</th><th>原版</th><th>${side === 'A' ? 'A' : 'B'}</th><th>Δ</th><th>单位</th></tr>`;
  table.appendChild(thead);
  const tbody = document.createElement('tbody');
  const column = r[side] || {};
  let rows = 0;
  for (const id of r.alignable) {
    const delta = (column.delta_vs_original || {})[id];
    if (review.tableFilter === 'changed' && (delta === 0 || delta === null || delta === undefined)) continue;
    if (review.tableFilter === 'not_alignable') continue;
    const original = (r.original.metrics || {})[id] || {};
    const candidate = (column.metrics || {})[id] || {};
    const tr = document.createElement('tr');
    for (const cell of [id, original.value, candidate.value, delta, original.unit || '']) {
      const td = document.createElement('td');
      td.textContent = cell === null || cell === undefined ? '—' : String(cell);
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
    rows += 1;
  }
  if (review.tableFilter !== 'changed') {
    for (const na of r.not_alignable) {
      const tr = document.createElement('tr');
      tr.className = 'rv-na-row';
      const td = document.createElement('td');
      td.textContent = na.name;
      const td2 = document.createElement('td');
      td2.colSpan = 3;
      td2.textContent = `不可对齐：${na.reason}`;
      const td3 = document.createElement('td');
      td3.textContent = '—';
      tr.append(td, td2, td3);
      tbody.appendChild(tr);
      rows += 1;
    }
  }
  table.appendChild(tbody);
  box.textContent = '';
  box.appendChild(head);
  if (!rows) {
    const none = document.createElement('p');
    none.className = 'muted caption';
    none.textContent = review.tableFilter === 'changed'
      ? '这一侧没有与「仅看有变化」匹配的指标。'
      : '没有匹配的指标。';
    box.appendChild(none);
  } else {
    box.appendChild(table);
  }
}

/** 动作区：每页的主动作与本页对象一致；「保留原版」是三出口里共同的第三选项。 */
function renderReviewActions() {
  const side = review.tab;
  const bundle = review.evidence.sides[side];
  const blockers = tuningState.decisionBlockers[review.pairId] || [];
  const ready = blockers.length === 0 && Boolean(bundle.audio);
  $('rv-choose').textContent = `选择 ${REV_TAB_LABEL[side]}`;
  $('rv-choose').disabled = !ready;
  $('rv-keep-original').disabled = !ready;
  const note = $('tuning-note');
  if (!ready && blockers.length) note.textContent = `还不能选定：${blockers.join('；')}`;
}

//
// 产品方向（2026-10-04 采纳）：**逆向工程 · 多轨复合**。
// 先把立体声逆向分解成多轨，逐轨修音，再复合——多轨复合才是 AI 后处理的核心操作。
// 该方向的前提是**假设**，所以由两道机制关住风险：可逆性门禁（不过则 ④修音 不开）
// 与第三出口「保留原版」。
//
// 阶段状态由 main 侧从磁盘产物**推导**（src/pipeline.js），渲染层不自己记进度，
// 也不允许把「未满足前置」的阶段显示成可用。

// ——— 传输控制：一个播放器、三个真实音源、同一时间位置 ———
//
// 同一时刻只加载一个源（没有三个 AudioContext、没有三个播放头）。切换源时记住当前时间与
// 缩放，加载完成后回到同一位置；加载失败就**保持上一个可播放源**，绝不出现「按钮显示 B、
// 实际在放 A」。位置绝不在切换时被偷偷归零。

function reviewSelectTab(side) {
  if (review.tab === side) return;
  review.tab = side;
  renderReviewChrome();
  renderReviewPage();
}

function destroyReviewTransport() {
  if (review.ws) { try { review.ws.destroy(); } catch { /* already gone */ } }
  review.ws = null;
  review.bufferCache.clear();
  review.zoomPx = null;
  review.loadToken += 1;
}

function reviewSetLoadNote(text) { $('rv-load').textContent = text || ''; }

function reviewCurrentPosition() {
  if (!review.ws) return 0;
  try { return review.ws.getCurrentTime() || 0; } catch { return 0; }
}

function reviewIsPlaying() {
  if (!review.ws) return false;
  try { return review.ws.isPlaying(); } catch { return false; }
}

/** 把已解码的 buffer 放进一个最多两条的缓存（长曲不至于把内存吃光）。 */
function reviewCacheBuffer(side, buffer) {
  review.bufferCache.delete(side);
  review.bufferCache.set(side, buffer);
  while (review.bufferCache.size > 2) {
    const oldest = review.bufferCache.keys().next().value;
    review.bufferCache.delete(oldest);
  }
}

async function reviewDecodeSide(side) {
  const cached = review.bufferCache.get(side);
  if (cached) return cached;
  const bytes = await window.moodify.tuningAudio(tuningState.caseDir, review.pairId, side);
  const ab = bytes instanceof ArrayBuffer ? bytes
    : bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  const ctx = new AudioContext();
  try {
    const audio = await ctx.decodeAudioData(ab);
    reviewCacheBuffer(side, audio);
    return audio;
  } finally {
    await ctx.close();
  }
}

function reviewMountTransport(buffer) {
  if (!review.ws) {
    review.ws = WaveSurfer.create({
      container: $('rv-wave'),
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
        container: $('rv-ruler'),
        fontSize: 10,
        primaryColor: '#d1d5db',
        secondaryColor: '#f3f4f6',
        primaryFontColor: '#9ca3af',
        secondaryFontColor: '#c7cbd1',
      })],
    });
    review.ws.on('timeupdate', (t) => {
      if (!review.ws) return;
      const text = `${fmtTime(t)} / ${fmtTime(review.ws.getDuration() || 0)}`;
      $('rv-time').textContent = text;
      $('cp-time').textContent = text;
    });
    review.ws.on('play', () => { $('rv-play').textContent = '⏸'; $('cp-play').textContent = '⏸'; });
    review.ws.on('pause', () => { $('rv-play').textContent = '▶'; $('cp-play').textContent = '▶'; });
    review.ws.on('finish', () => {
      // 曲终保持安静：停在这里，不自动跳下一首、不弹任何推荐
      $('rv-play').textContent = '▶';
      $('cp-play').textContent = '▶';
    });
  }
  review.ws.loadDecodedBuffer(buffer);
  $('rv-time').textContent = `0:00.0 / ${fmtTime(buffer.duration)}`;
}

/**
 * 载入某个音源。切换时保留时间位置与缩放；失败时保持上一个可播放源。
 *
 * @param {'ORIGINAL'|'A'|'B'} side
 * @param {{autoplay?:boolean}} [opts]
 */
async function reviewLoadSide(side, opts = {}) {
  const caseDir = tuningState.caseDir;
  const pairId = review.pairId;
  if (!caseDir || !pairId) return;
  const bundle = review.evidence && review.evidence.sides[side];
  if (!bundle || !bundle.audio) {
    reviewSetLoadNote(`${revSideLabel(side)}没有可用音频`);
    return;
  }
  const token = ++review.loadToken;
  const position = reviewCurrentPosition();
  const wasPlaying = reviewIsPlaying();
  const previous = review.playing;
  reviewSetLoadNote(`正在加载${revSideLabel(side)}…`);
  let buffer;
  try {
    buffer = await reviewDecodeSide(side);
  } catch (err) {
    if (token !== review.loadToken) return;
    // 真实原因照说；播放器保持在原来那一侧（绝不把按钮状态切成 B 却仍在放 A）。
    reviewSetLoadNote(`加载${revSideLabel(side)}失败：${(err && err.message) || err}`);
    return;
  }
  if (token !== review.loadToken) return;             // 只接受最后一次切换
  if (state.caseDir !== caseDir || review.pairId !== pairId) return; // 换世界/换 pair

  if (!review.ws) reviewMountTransport(buffer);
  else review.ws.loadDecodedBuffer(buffer);
  if (position > 0) {
    try { review.ws.seekTo(Math.min(position, buffer.duration)); } catch { /* keep 0 */ }
  }
  review.playing = side;
  reviewSetLoadNote('');
  renderReviewChrome();
  requestAnimationFrame(applyReviewZoom); // 换 buffer 后重新应用同一缩放
  const keepPlaying = opts.autoplay === undefined ? wasPlaying : opts.autoplay;
  if (keepPlaying) { try { review.ws.play(); } catch { /* user gesture rules */ } }
  void previous;
}

function reviewTogglePlay() {
  if (!review.ws) return;
  review.ws.playPause();
}

/**
 * 波形缩放：默认适配全曲（长曲不会把页面横向撑破），缩小/放大只在显式点击时发生。
 * 切换音源后重新应用同一缩放，于是「保留当前缩放范围」是真的。
 */
function applyReviewZoom() {
  const el = $('rv-wave');
  if (!review.ws || !el || el.clientWidth < 10) return; // 隐藏态宽度为 0
  const duration = review.ws.getDuration() || 1;
  const fitPx = el.clientWidth / duration;
  review.ws.zoom(Math.max(review.zoomPx || fitPx, fitPx));
}

function reviewSetZoom(factor) {
  const el = $('rv-wave');
  if (!review.ws || !el || el.clientWidth < 10) return;
  const duration = review.ws.getDuration() || 1;
  const fitPx = el.clientWidth / duration;
  review.zoomPx = Math.min(800, Math.max(fitPx, (review.zoomPx || fitPx) * factor));
  applyReviewZoom();
}

// ——— 完成层（Phase 2.3）：作品留存 ———
//
// 「完成」不是这里判断的：能不能进入由 keepsake:state 投影（= pipeline 产物 + ⑦ 准入）决定。
// 本层只做三件事：把作品安静地摆出来、把最终选择听一遍、把一句话与作品卡留下来。
// 它复用 Phase 2.2 的同一个 transport（`review.ws`），不新建播放器、不复用第二份数据。

const CP_COLORS = {
  ORIGINAL: { line: '#64748b', soft: 'rgba(100, 116, 139, 0.18)' },
  A: { line: '#4f46e5', soft: 'rgba(79, 70, 229, 0.18)' },
  B: { line: '#c2410c', soft: 'rgba(194, 65, 12, 0.18)' },
};

const completion = {
  state: null,
  quiet: false,
  detailsOpen: false,   // 「查看制作详情」= 把 A/B 审听这第二层打开
  includeInscription: true,
  lastStatus: '',
  imprintDrawToken: 0,
};

function prefersReducedMotion() {
  try { return window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch { return false; }
}

function initCompletion() {
  $('cp-listen').addEventListener('click', completionListenFromStart);
  $('cp-play').addEventListener('click', () => reviewTogglePlay());
  $('cp-exit-listen').addEventListener('click', () => completionExitQuiet());
  $('cp-details').addEventListener('click', () => completionShowDetails());
  $('cp-export').addEventListener('click', exportChosen);
  $('cp-card').addEventListener('click', completionSaveCard);
  $('cp-inscribe-toggle').addEventListener('click', () => {
    $('cp-inscribe-box').hidden = !$('cp-inscribe-box').hidden;
    if (!$('cp-inscribe-box').hidden) $('cp-inscription').focus();
  });
  $('cp-inscription-save').addEventListener('click', completionSaveInscription);
  $('cp-inscription-clear').addEventListener('click', () => {
    // 清空是普通编辑行为：不发确认弹窗、不报警，写完就安静地更新
    $('cp-inscription').value = '';
    completionSaveInscription();
  });
  $('cp-card-include').addEventListener('change', () => {
    completion.includeInscription = $('cp-card-include').checked;
  });
  $('cp-volume').addEventListener('input', () => {
    const value = Number($('cp-volume').value) / 100;
    if (review.ws && typeof review.ws.setVolume === 'function') review.ws.setVolume(value);
  });
  window.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (completion.quiet) { completionExitQuiet(); return; }
    if ($('completion').hidden) return;
    if (!$('cp-inscribe-box').hidden) { $('cp-inscribe-box').hidden = true; return; }
  });
}

/** 刷新完成状态；返回 true 表示当前 case 有完成层可进。 */
async function refreshCompletion() {
  const caseDir = tuningState.caseDir || state.caseDir;
  if (!caseDir) { $('completion').hidden = true; return false; }
  let res;
  try { res = await window.moodify.keepsakeState(caseDir); } catch { res = null; }
  if (state.caseDir !== caseDir) return false;
  completion.state = res && res.ok ? res : null;
  return renderCompletion();
}

/**
 * 渲染完成层。返回是否显示。
 *
 * 只有真完成才显示：伪造的 decision、被删掉的候选、消失的复检，都会让 complete 为假，
 * 于是这里**什么都不显示**（回到真实的 A/B/阻断状态），而不是摆一个假完成。
 */
function renderCompletion() {
  const s = completion.state;
  const complete = Boolean(s && s.complete);
  const layer = $('completion');
  if (!complete) {
    layer.hidden = true;
    completion.quiet = false;
    completion.detailsOpen = false;
    document.body.classList.remove('cp-quiet');
    applyWorkspaceMode();
    return false;
  }
  layer.hidden = false;
  $('cp-title').textContent = s.title || '未命名作品';
  $('cp-title').title = s.title || '';
  // 「快速完成」只是小型事实标签；保留原版时就说保留原版，不伪装成处理版本。
  const version = s.selected === 'ORIGINAL'
    ? '保留原版'
    : [s.selectedLabel, s.tierLabel].filter(Boolean).join(' · ');
  $('cp-version').textContent = version;
  const completed = s.completedAt ? new Date(s.completedAt) : null;
  $('cp-date').textContent = completed && !Number.isNaN(completed.getTime())
    ? `${completed.getFullYear()}.${String(completed.getMonth() + 1).padStart(2, '0')}.${String(completed.getDate()).padStart(2, '0')}`
    : '';

  // 文字：完成层显示的永远是本地留存里那一句（可编辑、可清空）
  const text = typeof s.inscription === 'string' ? s.inscription : '';
  $('cp-inscription-shown').textContent = text;
  $('cp-inscription-shown').hidden = !text;
  if ($('cp-inscription').value !== text) $('cp-inscription').value = text;

  // 警告（音频不可用 / 留存文件读不出来）就地显示，不弹 toast
  const warn = $('cp-warning');
  if (!s.audioAvailable) {
    warn.hidden = false;
    warn.textContent = s.selected === 'ORIGINAL'
      ? '原版音频不可用（文件可能被移动或删除）。'
      : `${s.selectedLabel} 的音频不可用（文件可能被移动或删除）。`;
  } else if (s.keepsakeError) {
    warn.hidden = false;
    warn.textContent = '留存记录读取失败，本次显示为空白状态（不影响声音与导出）。';
  } else {
    warn.hidden = true;
    warn.textContent = '';
  }

  drawCompletionImprint();
  $('cp-listen').disabled = !s.audioAvailable;
  $('cp-export').disabled = !s.audioAvailable;
  $('cp-card').disabled = false;
  $('cp-status').textContent = completion.lastStatus;
  applyWorkspaceMode();
  return true;
}

/** 把留存里的波形印记画出来；没有印记时从已解码的最终音频算一次并存下来。 */
function drawCompletionImprint() {
  const canvas = $('cp-imprint');
  const s = completion.state;
  if (!canvas || !s) return;
  if (Array.isArray(s.imprint) && s.imprint.length) {
    paintImprint(canvas, s.imprint, s.selected);
    return;
  }
  paintImprint(canvas, [], s.selected);
  // 还没有印记：用最终选择的真实音频算一次（同一段音频永远得到同一个形状）
  ensureSelectedAudioDecoded().then((buffer) => {
    if (!buffer || !completion.state || completion.state.selected !== s.selected) return;
    const peaks = imprintPeaksFromBuffer(buffer, completion.state.imprintBuckets || 600);
    if (!peaks.length) return;
    paintImprint(canvas, peaks, s.selected);
    window.moodify.keepsakeImprint(tuningState.caseDir, peaks).then((res) => {
      if (res && res.ok && completion.state) completion.state.imprint = res.imprint;
    }).catch(() => { /* 印记存不下来不影响任何东西 */ });
  }).catch(() => { /* 音频不可用时只是没有印记 */ });
}

/** 从**已解码的最终音频**取峰值包络（纯计算：无随机、无时钟、桶数固定）。 */
function imprintPeaksFromBuffer(buffer, buckets) {
  const count = Math.max(1, Number(buckets) || 600);
  const channels = Math.max(1, buffer.numberOfChannels || 1);
  const length = buffer.length || 0;
  if (!length) return [];
  const data = [];
  for (let c = 0; c < channels; c += 1) data.push(buffer.getChannelData(c));
  const peaks = new Array(count).fill(0);
  for (let i = 0; i < count; i += 1) {
    const start = Math.floor((i * length) / count);
    const end = Math.max(start + 1, Math.floor(((i + 1) * length) / count));
    let peak = 0;
    for (let j = start; j < end && j < length; j += 1) {
      let value = 0;
      for (let c = 0; c < channels; c += 1) {
        const sample = Math.abs(data[c][j]);
        if (sample > value) value = sample;
      }
      if (value > peak) peak = value;
    }
    peaks[i] = Math.min(1, peak);
  }
  return peaks;
}

/**
 * 画波形印记：只画形状，不画时间刻度、网格或工程游标。
 * 它是作品的指纹，不是 DAW 截图，也不是分析证据。
 */
function paintImprint(canvas, imprint, selected) {
  const ctx = canvas.getContext('2d');
  const colors = CP_COLORS[selected] || CP_COLORS.ORIGINAL;
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = colors.soft;
  ctx.fillRect(0, 0, width, height);

  const mid = height / 2;
  const top = 18;
  const bottom = height - 18;
  const usable = (bottom - top) / 2;
  ctx.fillStyle = colors.line;
  if (!imprint.length) {
    // 还没有可画的形状：留一条极细的中线，不假装有波形
    ctx.globalAlpha = 0.35;
    ctx.fillRect(0, mid - 0.5, width, 1);
    ctx.globalAlpha = 1;
    return;
  }
  const step = width / imprint.length;
  for (let i = 0; i < imprint.length; i += 1) {
    const value = Math.max(0, Math.min(1, imprint[i] || 0));
    const barHeight = Math.max(1, value * usable);
    const x = i * step;
    ctx.globalAlpha = 0.9;
    ctx.fillRect(x, mid - barHeight, Math.max(0.8, step * 0.72), barHeight * 2);
  }
  ctx.globalAlpha = 1;
  ctx.fillStyle = 'rgba(22, 24, 29, 0.16)';
  ctx.fillRect(0, mid, width, 1);
}

/** 取「最终选择」的已解码音频（复用 Phase 2.2 的同一解码路径与缓存）。 */
async function ensureSelectedAudioDecoded() {
  const s = completion.state;
  if (!s || !s.complete || !s.audioAvailable) return null;
  try {
    return await reviewDecodeSide(s.selected);
  } catch {
    return null;
  }
}

/** ▶ 从头听：载入最终选择、位置归零、进入安静聆听；绝不自动播放之外的任何东西。 */
async function completionListenFromStart() {
  const s = completion.state;
  if (!s || !s.complete || !s.audioAvailable) return;
  review.pairId = s.pairId;
  review.tab = s.selected === 'A' ? 'A' : (s.selected === 'B' ? 'B' : review.tab);
  await reviewLoadSide(s.selected, { autoplay: false });
  if (review.ws) {
    try { review.ws.seekTo(0); } catch { /* fresh buffer starts at 0 anyway */ }
    try { review.ws.play(); } catch { /* user gesture rules may block; the button shows ▶ */ }
  }
  completionEnterQuiet();
}

function completionEnterQuiet() {
  completion.quiet = true;
  document.body.classList.add('cp-quiet');
  $('cp-listen-bar').hidden = false;
  $('cp-listen').hidden = true;
  $('cp-listen').focus();
  paintCompletionListening();
}

function completionExitQuiet() {
  completion.quiet = false;
  document.body.classList.remove('cp-quiet');
  $('cp-listen-bar').hidden = true;
  $('cp-listen').hidden = false;
}

/** 播放身份与时间：安静聆听时也要明确「现在放的是哪一版」。 */
function paintCompletionListening() {
  const s = completion.state;
  if (!s) return;
  const playing = review.playing || s.selected;
  $('cp-listening').textContent = `正在播放：${playing === 'ORIGINAL' ? '保留原版' : revSideLabel(playing)}`;
}

/** 「查看制作详情」：回到 Phase 2.2 的 A/B 审听（证据都在那里，完成不删除证据）。 */
async function completionShowDetails() {
  completionExitQuiet();
  completion.detailsOpen = true;
  await refreshReview();
  applyWorkspaceMode();
  const target = $('session-head');
  if (target && typeof target.scrollIntoView === 'function') {
    // 减少动画时直接跳过去，不做平滑滚动
    target.scrollIntoView({ block: 'start', behavior: prefersReducedMotion() ? 'auto' : 'smooth' });
  }
}

async function completionSaveInscription() {
  const caseDir = tuningState.caseDir || state.caseDir;
  if (!caseDir) return;
  const text = $('cp-inscription').value;
  let res;
  try { res = await window.moodify.keepsakeInscription(caseDir, text); }
  catch (err) { res = { ok: false, reason: (err && err.message) || String(err) }; }
  if (!res || !res.ok) {
    const why = res && res.reason === 'INSCRIPTION_TOO_LONG' ? '最多 280 个字'
      : (res && res.reason === 'INSCRIPTION_TOO_MANY_LINES' ? '最多 4 行'
        : '暂时存不下来');
    $('cp-status').textContent = `文字${why}。`;
    return;
  }
  if (completion.state) completion.state.inscription = res.inscription;
  $('cp-inscription-shown').textContent = res.inscription;
  $('cp-inscription-shown').hidden = !res.inscription;
  $('cp-status').textContent = '已留下';
  $('cp-inscribe-box').hidden = true;
}

/**
 * 保存作品卡：本地画一张 PNG（1600×1000，确定性），再过系统保存对话框落盘。
 * 卡片上只有：Moodify 标识、标题、最终选择、波形印记、完成日期、可选的一句话。
 */
async function completionSaveCard() {
  const caseDir = tuningState.caseDir || state.caseDir;
  const s = completion.state;
  if (!caseDir || !s || !s.complete) return;
  $('cp-status').textContent = '正在生成作品卡…';
  let bytes;
  try {
    bytes = await drawKeepsakeCard(s, completion.includeInscription);
  } catch (err) {
    $('cp-status').textContent = '作品卡生成失败。';
    return;
  }
  if (!bytes) { $('cp-status').textContent = '作品卡生成失败。'; return; }
  let res;
  try { res = await window.moodify.keepsakeSaveCard(caseDir, bytes); }
  catch (err) { res = { ok: false, reason: (err && err.message) || String(err) }; }
  if (!res) { $('cp-status').textContent = '作品卡保存失败。'; return; }
  if (res.canceled) { $('cp-status').textContent = ''; return; }   // 用户取消不算失败
  $('cp-status').textContent = res.ok ? '作品卡已保存' : '作品卡保存失败。';
}

function loadImage(src) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => resolve(null);
    img.src = src;
  });
}

/** 文本换行（按像素宽度贪心断行），确定性、可预测。 */
function wrapCanvasText(ctx, text, maxWidth, maxLines) {
  const lines = [];
  for (const paragraph of String(text).split('\n')) {
    let current = '';
    for (const char of paragraph) {
      const next = current + char;
      if (ctx.measureText(next).width > maxWidth && current) {
        lines.push(current);
        current = char;
        if (lines.length >= maxLines) break;
      } else {
        current = next;
      }
    }
    if (lines.length >= maxLines) break;
    lines.push(current);
  }
  return lines.slice(0, maxLines);
}

async function drawKeepsakeCard(state, includeInscription) {
  const width = 1600;
  const height = 1000;
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  const colors = CP_COLORS[state.selected] || CP_COLORS.ORIGINAL;

  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = colors.soft;
  ctx.fillRect(0, 0, width, height);

  // Moodify 小型标识（现有品牌资产；加载不出来就不画，绝不拿别的东西顶替）
  const logo = await loadImage('assets/moodify_logo.png');
  if (logo && logo.width) {
    const markWidth = 180;
    const markHeight = Math.round((logo.height / logo.width) * markWidth);
    ctx.globalAlpha = 0.9;
    ctx.drawImage(logo, 96, 84, markWidth, Math.min(markHeight, 64));
    ctx.globalAlpha = 1;
  }

  // 标题（最多两行，超出用省略号；不换行也不能溢出）
  ctx.fillStyle = '#16181d';
  ctx.font = '600 58px "Microsoft YaHei", "Segoe UI", sans-serif';
  const titleLines = wrapCanvasText(ctx, state.title || '未命名作品', width - 192, 2);
  let y = 300;
  for (const [index, line] of titleLines.entries()) {
    const isLast = index === titleLines.length - 1;
    const text = isLast && line.length < String(state.title || '').length ? `${line}…` : line;
    ctx.fillText(text, 96, y);
    y += 72;
  }

  // 版本
  ctx.fillStyle = colors.line;
  ctx.font = '500 30px "Microsoft YaHei", "Segoe UI", sans-serif';
  const version = state.selected === 'ORIGINAL'
    ? '保留原版'
    : [state.card.selectionLabel, state.card.versionLabel].filter(Boolean).join(' · ');
  ctx.fillText(version, 96, y + 6);

  // 波形印记：同一份数据、同一算法（与完成层一致）
  const imprintTop = 470;
  const imprintHeight = 240;
  const imprintWidth = width - 192;
  const imprint = Array.isArray(state.imprint) ? state.imprint : [];
  ctx.fillStyle = colors.line;
  if (!imprint.length) {
    ctx.globalAlpha = 0.35;
    ctx.fillRect(96, imprintTop + imprintHeight / 2, imprintWidth, 2);
    ctx.globalAlpha = 1;
  } else {
    const mid = imprintTop + imprintHeight / 2;
    const usable = imprintHeight / 2;
    const step = imprintWidth / imprint.length;
    for (let i = 0; i < imprint.length; i += 1) {
      const value = Math.max(0, Math.min(1, imprint[i] || 0));
      const barHeight = Math.max(1, value * usable);
      ctx.fillRect(96 + i * step, mid - barHeight, Math.max(1, step * 0.72), barHeight * 2);
    }
  }

  // 完成日期
  ctx.fillStyle = '#6b7280';
  ctx.font = '400 28px "Microsoft YaHei", "Segoe UI", sans-serif';
  if (state.card.dateLabel) ctx.fillText(state.card.dateLabel, 96, imprintTop + imprintHeight + 72);

  // 一句私人文字（可选包含）
  if (includeInscription && state.card.inscription) {
    ctx.fillStyle = '#16181d';
    ctx.font = '400 30px "Microsoft YaHei", "Segoe UI", sans-serif';
    const lines = wrapCanvasText(ctx, state.card.inscription, width - 192, 4);
    let ty = imprintTop + imprintHeight + 150;
    for (const line of lines) {
      ctx.fillText(line, 96, ty);
      ty += 42;
    }
  }

  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
  if (!blob) return null;
  return new Uint8Array(await blob.arrayBuffer());
}

// ——— 生产流程（V4）：检测 → 逆向分解 → 结构 → 修音 → 复合 → 复检 → 选定 → 导出 ———
//
// 产品方向（人类 2026-10-04 采纳）：**逆向工程 · 多轨复合**。
// 先把立体声逆向分解成多轨，逐轨修音，再复合——多轨复合才是 AI 后处理的核心操作。
// 该方向的前提是**假设**，所以由两道机制关住风险：可逆性门禁（不过则 ④修音 不开）
// 与第三出口「保留原版」。

const PIPELINE_STAGES = [
  { id: 'analyze', label: '① 检测', view: 'data' },
  { id: 'separate', label: '② 逆向分解', view: 'stems' },
  { id: 'structure', label: '③ 结构', view: 'score' },
  { id: 'tune', label: '④ 修音', view: 'tuning' },
  { id: 'compose', label: '⑤ 复合', view: 'tuning' },
  { id: 'recheck', label: '⑥ 复检', view: 'tuning' },
  { id: 'choose', label: '⑦ 选定', view: 'tuning' },
  { id: 'export', label: '⑧ 导出', view: 'tuning' },
];

const pipe = { caseDir: null, snap: null };

function initPipeline() {
  // rail-tuning 接到 enterPipeline：入口落在第一个未完成的阶段，不直接跳到处理。
  $('rail-tuning').addEventListener('click', enterPipeline);
  $('pipeline-quick').addEventListener('click', chooseQuickFinish);
}

function resetPipeline() {
  pipe.caseDir = null;
  pipe.snap = null;
  $('pipeline-stages').textContent = '';
  $('pipeline-mode').hidden = true;
  $('pipeline-quick').hidden = true;
}

async function refreshPipeline() {
  const caseDir = state.caseDir;
  if (!caseDir) return null;
  let res;
  try { res = await window.moodify.pipelineSnapshot(caseDir); } catch { return null; }
  if (!res || !res.ok || state.caseDir !== caseDir) return null; // world-switch guard
  pipe.caseDir = caseDir;
  pipe.snap = res;
  renderPipelineBar();
  return res;
}

/**
 * Which stages the current case may enter. Mirrors src/pipeline.js gates().
 *
 * ④ 修音 requires 分轨 + MIDI **and 可逆性通过**：分解是信息有损的，原分轨不可知，
 * 所以唯一可测的质量代理是「分解 → 复合（不处理）是否回到原版」。门禁不过，④ 不开。
 * ⑤ 复合 opens on the paired tuned artifacts; ⑥ on the paired mixes; ⑦ on the recheck;
 * ⑧ on a recorded choice (A / B / 保留原版 皆可).
 * Quick Finish skips decomposition, not verification — it still walks ④→⑤→⑥→⑦.
 */
function stageUnlocked(id, gates) {
  if (!gates) return false;
  switch (id) {
    case 'analyze': return true;
    case 'separate': return gates.canSeparate;
    case 'structure': return gates.canStructure;
    case 'tune': return gates.canTune || gates.canTuneQuick;
    case 'compose': return gates.canCompose;
    case 'recheck': return gates.canRecheck;
    case 'choose': return gates.canChoose;
    case 'export': return gates.canExport;
    default: return false;
  }
}

/**
 * 差什么就说差什么——「需要先完成前面的阶段」等于没说。
 *
 * 每个被锁的阶段都从 gates 的 `*Blockers` 里取第一条真实原因：
 * 「缺分轨」「缺 MIDI」「可逆性未通过」是三个不同的问题、三种不同的补救，
 * 压成一句含糊的话会让门禁显得任意。
 */
function stageLockReason(id, gates) {
  const g = gates || {};
  const first = (arr) => (Array.isArray(arr) && arr.length ? arr[0] : null);
  switch (id) {
    case 'separate':
    case 'structure':
      return '需要先完成 ① 检测。';
    case 'tune':
      return first(g.tuneBlockers) || '尚未满足 ④ 修音的前置条件。';
    case 'compose':
      return first(g.composeBlockers) || '需要先完成 ④ 修音。';
    case 'recheck':
      return first(g.recheckBlockers) || '需要先完成 ⑤ 复合。';
    case 'choose':
      return first(g.chooseBlockers) || '需要先完成 ⑥ 复检。';
    case 'export':
      return first(g.exportBlockers) || '需要先在 ⑦ 选定一个出口（A / B / 保留原版）。';
    default:
      return '尚未满足前置条件。';
  }
}

function renderPipelineBar() {
  const box = $('pipeline-stages');
  box.textContent = '';
  if (!pipe.snap) return;
  const { gates } = pipe.snap;

  for (const s of PIPELINE_STAGES) {
    const unlocked = stageUnlocked(s.id, gates);
    const btn = document.createElement('button');
    btn.className = 'pipe-stage';
    btn.dataset.stage = s.id;
    btn.textContent = s.label;
    btn.disabled = !unlocked;
    if (!unlocked) {
      btn.classList.add('locked');
      btn.title = stageLockReason(s.id, gates);
    }
    btn.addEventListener('click', () => {
      if (btn.disabled) return;
      openPipelineStage(s.id);
    });
    box.appendChild(btn);
  }

  // 显式选择「快速完成」的入口。只在前置不足且尚未选择时出现。
  // 它不是一个开关：点它 = 记录一次人类决定（finish_mode.json）。
  const quick = $('pipeline-quick');
  quick.hidden = !gates.canRequestQuick;

  // 完成模式徽章：深度 or 快速（仅立体声）。
  // 不标注就是骗人——跳过分离与结构仍然是合法路径，但必须让人知道自己在哪条路上。
  const badge = $('pipeline-mode');
  if (gates.modeLabel) {
    badge.textContent = gates.modeLabel;
    badge.hidden = false;
    badge.classList.toggle('deep', gates.mode === 'DEEP');
  } else {
    badge.hidden = true;
  }
}

/**
 * 人类显式选择快速完成（仅立体声）。
 * 记录后 ④ 才以 FAST 模式解锁；但快速路径仍然要走 ⑤复合 → ⑥复检 → ⑦选定 才能导出——
 * 它跳过的是分解，不是验证。
 */
async function chooseQuickFinish() {
  const caseDir = state.caseDir;
  if (!caseDir) return;
  let res;
  try { res = await window.moodify.pipelineSetFinishMode(caseDir, 'QUICK_STEREO_ONLY'); }
  catch (err) { res = { ok: false, reason: err.message }; }
  if (!res || !res.ok) return;
  await refreshPipeline();
  openPipelineStage('tune');
}

function openPipelineStage(id) {
  const s = PIPELINE_STAGES.find((x) => x.id === id);
  if (!s) return;
  switch (id) {
    case 'analyze': selectView('data'); break;
    case 'separate': openStems(); break;
    case 'structure': openScore(); break;
    case 'tune':
    case 'compose':
    case 'recheck':
    case 'choose':
    case 'export': openTuning(); break;
    default: selectView(s.view);
  }
}

/** 进入流程：落在第一个「已解锁但还没做」的阶段，而不是直接跳到处理。 */
async function enterPipeline() {
  if (!state.caseDir) return;
  const snap = await refreshPipeline();
  if (!snap) return;
  const f = snap.facts || {};
  const done = {
    analyze: f.analyzed,
    separate: f.separated,
    structure: f.structured,
    tune: f.tuned,
    compose: f.composed,
    recheck: f.rechecked,
    choose: f.chosen,
    export: f.exported,
  };
  const next = PIPELINE_STAGES.find((s) => stageUnlocked(s.id, snap.gates) && !done[s.id])
    || PIPELINE_STAGES[PIPELINE_STAGES.length - 1];
  openPipelineStage(next.id);
}
