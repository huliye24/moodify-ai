const $ = selector => document.querySelector(selector);
const sidebar = $('#sidebar');
const conversation = $('#conversation');
const welcome = $('#welcome');
const composer = $('#composer');
const promptBox = $('#prompt');
const audioFile = $('#audioFile');
const attachment = $('#attachment');
let selectedAudio = null;
let activePoll = null;

$('#sidebarOpen')?.addEventListener('click', () => sidebar.classList.add('open'));
$('#sidebarClose')?.addEventListener('click', () => sidebar.classList.remove('open'));
$('#attachButton')?.addEventListener('click', () => audioFile.click());
$('#removeFile')?.addEventListener('click', clearFile);
$('#newSession')?.addEventListener('click', () => location.reload());

audioFile?.addEventListener('change', () => {
  selectedAudio = audioFile.files?.[0] || null;
  if (!selectedAudio) return;
  $('#fileName').textContent = selectedAudio.name;
  $('#fileMeta').textContent = `${(selectedAudio.size / 1024 / 1024).toFixed(2)} MB · 等待提交`;
  attachment.hidden = false;
});

document.querySelectorAll('[data-prompt]').forEach(button => {
  button.addEventListener('click', () => {
    promptBox.value = button.dataset.prompt;
    promptBox.focus();
    resizePrompt();
  });
});

promptBox?.addEventListener('input', resizePrompt);
promptBox?.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    composer.requestSubmit();
  }
});

composer?.addEventListener('submit', async event => {
  event.preventDefault();
  const text = promptBox.value.trim();
  if (!selectedAudio) {
    addMessage('assistant', '请先添加 WAV、MP3、FLAC、M4A、OGG 或 AAC 音频。');
    return;
  }
  const file = selectedAudio;
  welcome?.remove();
  addMessage('user', text || `请分析 ${file.name}`);
  promptBox.value = '';
  resizePrompt();
  const statusRow = addAssistant('正在安全上传并写入持久任务队列…');
  setBusy(true);
  try {
    const form = new FormData();
    form.append('audio', file);
    form.append('prompt', text);
    const response = await fetch('/api/v1/auditory/jobs', {method: 'POST', body: form});
    const body = await response.json();
    if (!response.ok) throw new Error(apiError(body, response.status));
    clearFile();
    statusRow.querySelector('.bubble').textContent = `任务 ${body.job.job_id.slice(-8)} 已进入队列，页面会自动更新。`;
    pollJob(body.job.job_id, statusRow);
  } catch (error) {
    statusRow.querySelector('.bubble').textContent = `提交失败：${error.message}`;
    setBusy(false);
  }
});

async function pollJob(jobId, row) {
  clearTimeout(activePoll);
  try {
    const response = await fetch(`/api/v1/auditory/jobs/${encodeURIComponent(jobId)}`, {cache: 'no-store'});
    const body = await response.json();
    if (!response.ok) throw new Error(apiError(body, response.status));
    const job = body.job;
    const labels = {
      QUEUED: '正在队列中等待可用计算资源',
      RUNNING: `正在执行 Listen → Represent → Judge → Intervene → Verify（第 ${job.attempts} 次）`,
      FAILED: '任务未通过自动重试，已保留失败证据供检查',
    };
    if (job.status === 'SUCCEEDED') {
      const resultResponse = await fetch(`/api/v1/auditory/jobs/${encodeURIComponent(jobId)}/result`);
      const result = await resultResponse.json();
      if (!resultResponse.ok) throw new Error(apiError(result, resultResponse.status));
      renderResult(row, result);
      setBusy(false);
      return;
    }
    row.querySelector('.bubble').textContent = labels[job.status] || `任务状态：${job.status}`;
    if (job.status === 'FAILED') {
      setBusy(false);
      return;
    }
    activePoll = setTimeout(() => pollJob(jobId, row), 4000);
  } catch (error) {
    row.querySelector('.bubble').textContent = `状态查询暂时失败：${error.message}，稍后自动重试。`;
    activePoll = setTimeout(() => pollJob(jobId, row), 8000);
  }
}

function renderResult(row, result) {
  const manifest = result.case_manifest || {};
  const review = result.algorithmic_review || {};
  const ranking = Array.isArray(review.ranking) ? review.ranking.join(' › ') : '证据已生成';
  row.querySelector('.bubble').innerHTML = '';
  const title = document.createElement('strong');
  title.textContent = '无人值守听觉任务已完成';
  const summary = document.createElement('p');
  summary.textContent = `Case ${manifest.case_id || 'ready'} · 算法排序 ${ranking}`;
  const card = document.createElement('div');
  card.className = 'analysis-card';
  card.innerHTML = '<header><span>Auditory evidence</span><small>Verified & persisted</small></header><div class="meter"><i></i></div><small>源文件哈希、测量、候选方案、比较与验证证据已保存</small>';
  row.querySelector('.bubble').append(title, summary, card);
  document.querySelector('.workspace')?.classList.add('evidence-open');
}

function addMessage(role, text) {
  const row = document.createElement('div');
  row.className = `message ${role}`;
  row.innerHTML = '<div class="bubble"></div>';
  row.querySelector('.bubble').textContent = text;
  conversation.appendChild(row);
  conversation.scrollTop = conversation.scrollHeight;
  return row;
}

function addAssistant(text) {
  const row = addMessage('assistant', text);
  const mark = document.createElement('img');
  mark.className = 'assistant-mark';
  mark.src = './assets/moodify-symbol.png';
  mark.alt = '';
  row.prepend(mark);
  return row;
}

function apiError(body, status) {
  const detail = body?.detail;
  const code = typeof detail === 'object' ? detail.code : null;
  return code || `HTTP ${status}`;
}

function setBusy(busy) {
  if ($('#sendButton')) $('#sendButton').disabled = busy;
  if ($('#attachButton')) $('#attachButton').disabled = busy;
}

function clearFile() {
  selectedAudio = null;
  if (audioFile) audioFile.value = '';
  if (attachment) attachment.hidden = true;
}

function resizePrompt() {
  promptBox.style.height = 'auto';
  promptBox.style.height = `${Math.min(promptBox.scrollHeight, 140)}px`;
}
