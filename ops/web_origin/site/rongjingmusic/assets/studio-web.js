(() => {
  const fileInput = document.querySelector('#audio-file');
  const chooseFile = document.querySelector('#choose-file');
  const fileLabel = document.querySelector('#file-label');
  const hearButton = document.querySelector('#hear-button');
  const uploadPanel = document.querySelector('#upload-panel');
  const resultView = document.querySelector('#result-view');
  const resultTitle = document.querySelector('#result-title');
  const resultStatus = document.querySelector('#result-status');
  const hearingMap = document.querySelector('#hearing-map');
  const metricStrip = document.querySelector('#metric-strip');
  const judgeDecision = document.querySelector('#judge-decision');
  const judgeSummary = document.querySelector('#judge-summary');
  const jsonView = document.querySelector('#result-json');
  const notice = document.querySelector('#notice');
  const chatForm = document.querySelector('#chat-form');
  const chatInput = document.querySelector('#chat-input');
  const chatButton = document.querySelector('#chat-button');
  const conversation = document.querySelector('#conversation');
  const MAX_UPLOAD_BYTES = 50 * 1024 * 1024;
  let currentContext = {};

  const sectionLabels = {
    loudness_dynamics: '响度与动态', spectral_balance: '频谱平衡', low_frequency: '低频',
    high_frequency_cutoff: '高频', stereo_field: '立体声场', phase: '相位',
    transients: '瞬态', artifact_detection: '异常检测', musical_structure: '音乐结构',
  };

  const canvases = Object.fromEntries(['spectrogram', 'waveform', 'spectrum', 'dynamics', 'phase', 'emotion']
    .map(name => [name, document.querySelector(`#${name}-plot`)]));
  const plotColors = { ink: '#aeb9d8', grid: '#25304b', cyan: '#32d6ff', violet: '#7c65ff', lime: '#76f7b2' };

  const setupCanvas = canvas => {
    const ratio = Math.min(devicePixelRatio || 1, 2);
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(320, Math.round(rect.width * ratio));
    canvas.height = Math.max(180, Math.round(rect.height * ratio));
    const ctx = canvas.getContext('2d');
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    return { ctx, width: canvas.width / ratio, height: canvas.height / ratio };
  };

  const frame = (canvas, xLabel = 'TIME', yLabel = 'AMPLITUDE') => {
    const { ctx, width, height } = setupCanvas(canvas);
    ctx.fillStyle = '#0b1020'; ctx.fillRect(0, 0, width, height);
    ctx.strokeStyle = plotColors.grid; ctx.lineWidth = 1;
    for (let i = 1; i < 6; i += 1) { const x = 36 + (width - 52) * i / 6; ctx.beginPath(); ctx.moveTo(x, 12); ctx.lineTo(x, height - 27); ctx.stroke(); }
    for (let i = 1; i < 4; i += 1) { const y = 12 + (height - 39) * i / 4; ctx.beginPath(); ctx.moveTo(36, y); ctx.lineTo(width - 16, y); ctx.stroke(); }
    ctx.fillStyle = '#7783a3'; ctx.font = '9px ui-monospace, monospace'; ctx.fillText(xLabel, width - 42, height - 8);
    ctx.save(); ctx.translate(10, 62); ctx.rotate(-Math.PI / 2); ctx.fillText(yLabel, 0, 0); ctx.restore();
    return { ctx, width, height, left: 36, top: 12, right: width - 16, bottom: height - 27 };
  };

  const axisTicks = (plot, xTicks = [], yTicks = []) => {
    plot.ctx.fillStyle = '#7885a8'; plot.ctx.font = '8px ui-monospace, monospace';
    xTicks.forEach(([position, label]) => plot.ctx.fillText(label, plot.left + position * (plot.right - plot.left) - 7, plot.bottom + 13));
    yTicks.forEach(([position, label]) => plot.ctx.fillText(label, 2, plot.bottom - position * (plot.bottom - plot.top) + 3));
  };

  const fftMagnitudes = samples => {
    const n = samples.length, re = new Float64Array(n), im = new Float64Array(n);
    for (let i = 0; i < n; i += 1) re[i] = samples[i] * (0.5 - 0.5 * Math.cos(2 * Math.PI * i / (n - 1)));
    for (let i = 1, j = 0; i < n; i += 1) { let bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit; if (i < j) { [re[i], re[j]] = [re[j], re[i]]; } }
    for (let len = 2; len <= n; len <<= 1) {
      const angle = -2 * Math.PI / len;
      for (let i = 0; i < n; i += len) for (let j = 0; j < len / 2; j += 1) {
        const c = Math.cos(angle * j), s = Math.sin(angle * j), k = i + j + len / 2;
        const tr = re[k] * c - im[k] * s, ti = re[k] * s + im[k] * c;
        re[k] = re[i + j] - tr; im[k] = im[i + j] - ti; re[i + j] += tr; im[i + j] += ti;
      }
    }
    return Float32Array.from({ length: n / 2 }, (_, i) => 20 * Math.log10(Math.hypot(re[i], im[i]) / n + 1e-9));
  };

  const decodeAudio = async file => {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    const context = new AudioCtx();
    try { return await context.decodeAudioData(await file.arrayBuffer()); } finally { await context.close(); }
  };

  const drawScientificPlots = async file => {
    const audio = await decodeAudio(file);
    const left = audio.getChannelData(0), right = audio.numberOfChannels > 1 ? audio.getChannelData(1) : left;
    const mono = Float32Array.from(left, (v, i) => (v + right[i]) * 0.5);
    const wave = frame(canvases.waveform, 'TIME', 'AMP');
    axisTicks(wave, [[0, '0s'], [.5, `${(audio.duration / 2).toFixed(1)}s`], [1, `${audio.duration.toFixed(1)}s`]], [[0, '-1'], [.5, '0'], [1, '+1']]);
    wave.ctx.strokeStyle = plotColors.cyan; wave.ctx.lineWidth = 1; wave.ctx.beginPath();
    for (let x = wave.left; x <= wave.right; x += 1) { const i = Math.floor((x - wave.left) / (wave.right - wave.left) * mono.length); const y = (wave.top + wave.bottom) / 2 - mono[i] * (wave.bottom - wave.top) * .44; x === wave.left ? wave.ctx.moveTo(x, y) : wave.ctx.lineTo(x, y); } wave.ctx.stroke();

    const size = 1024, frames = Math.min(180, Math.max(24, Math.floor(mono.length / size))), spectra = [], average = new Float64Array(size / 2);
    for (let f = 0; f < frames; f += 1) { const start = Math.floor(f * Math.max(0, mono.length - size) / Math.max(1, frames - 1)); const windowed = new Float32Array(size); windowed.set(mono.subarray(start, Math.min(mono.length, start + size))); const spec = fftMagnitudes(windowed); spectra.push(spec); spec.forEach((v, i) => { average[i] += Math.pow(10, v / 20) / frames; }); }
    const spg = frame(canvases.spectrogram, 'TIME', 'FREQUENCY');
    const image = spg.ctx.createImageData(Math.max(1, Math.floor(spg.right - spg.left)), Math.max(1, Math.floor(spg.bottom - spg.top)));
    for (let x = 0; x < image.width; x += 1) for (let y = 0; y < image.height; y += 1) {
      const f = Math.min(frames - 1, Math.floor(x / image.width * frames)); const logBin = Math.floor((Math.exp((1 - y / image.height) * Math.log(size / 2)) - 1));
      const q = Math.max(0, Math.min(1, (spectra[f][Math.min(size / 2 - 1, logBin)] + 90) / 78)); const p = (y * image.width + x) * 4;
      image.data[p] = 8 + 247 * Math.pow(q, 2.6); image.data[p + 1] = 14 + 241 * Math.min(1, q * 1.45); image.data[p + 2] = 35 + 180 * q; image.data[p + 3] = 255;
    }
    spg.ctx.putImageData(image, spg.left, spg.top);
    axisTicks(spg, [[0, '0s'], [.25, `${(audio.duration * .25).toFixed(1)}`], [.5, `${(audio.duration * .5).toFixed(1)}`], [.75, `${(audio.duration * .75).toFixed(1)}`], [1, `${audio.duration.toFixed(1)}s`]], [[0, '20'], [.28, '100'], [.58, '1k'], [.86, '10k'], [1, `${Math.round(audio.sampleRate / 2000)}kHz`]]);
    const barX = spg.right - 8, bar = spg.ctx.createLinearGradient(0, spg.bottom, 0, spg.top); bar.addColorStop(0, '#080e23'); bar.addColorStop(.55, '#1ee69a'); bar.addColorStop(1, '#fff06a'); spg.ctx.fillStyle = bar; spg.ctx.fillRect(barX, spg.top + 5, 5, spg.bottom - spg.top - 10); spg.ctx.fillStyle = '#8290b3'; spg.ctx.fillText('0', barX - 12, spg.top + 9); spg.ctx.fillText('-90', barX - 19, spg.bottom - 4);
    const spectrum = frame(canvases.spectrum, 'Hz · LOG', 'dBFS'); spectrum.ctx.strokeStyle = plotColors.violet; spectrum.ctx.lineWidth = 1.5; spectrum.ctx.beginPath();
    axisTicks(spectrum, [[0, '20'], [.27, '100'], [.59, '1k'], [.86, '10k'], [1, '20k']], [[0, '-90'], [.5, '-50'], [1, '-10']]);
    for (let x = spectrum.left; x <= spectrum.right; x += 1) { const norm = (x - spectrum.left) / (spectrum.right - spectrum.left), hz = 20 * Math.pow((audio.sampleRate / 2) / 20, norm), bin = Math.min(average.length - 1, Math.floor(hz / audio.sampleRate * size)), db = 20 * Math.log10(average[bin] + 1e-9); const y = spectrum.bottom - Math.max(0, Math.min(1, (db + 90) / 80)) * (spectrum.bottom - spectrum.top); x === spectrum.left ? spectrum.ctx.moveTo(x, y) : spectrum.ctx.lineTo(x, y); } spectrum.ctx.stroke();

    const dynamics = frame(canvases.dynamics, 'TIME', 'RMS dBFS'); dynamics.ctx.strokeStyle = plotColors.lime; dynamics.ctx.lineWidth = 1.5; dynamics.ctx.beginPath(); let rmsTotal = 0;
    axisTicks(dynamics, [[0, '0s'], [.5, `${(audio.duration / 2).toFixed(1)}`], [1, `${audio.duration.toFixed(1)}s`]], [[0, '-60'], [.5, '-30'], [1, '0']]);
    for (let x = dynamics.left; x <= dynamics.right; x += 2) { const start = Math.floor((x - dynamics.left) / (dynamics.right - dynamics.left) * mono.length), end = Math.min(mono.length, start + 2048); let sum = 0; for (let i = start; i < end; i += 1) sum += mono[i] ** 2; const rms = Math.sqrt(sum / Math.max(1, end - start)); rmsTotal += rms; const db = 20 * Math.log10(rms + 1e-8), y = dynamics.bottom - Math.max(0, Math.min(1, (db + 60) / 60)) * (dynamics.bottom - dynamics.top); x === dynamics.left ? dynamics.ctx.moveTo(x, y) : dynamics.ctx.lineTo(x, y); } dynamics.ctx.stroke();

    const phase = frame(canvases.phase, 'SIDE', 'MID'), bins = 180, density = new Uint32Array(bins * bins); let densityMax = 1; const step = Math.max(1, Math.floor(left.length / 100000));
    for (let i = 0; i < left.length; i += step) { const mid = Math.max(-1, Math.min(1, (left[i] + right[i]) * .5)), side = Math.max(-1, Math.min(1, (left[i] - right[i]) * .5)), bx = Math.min(bins - 1, Math.floor((side + 1) * .5 * bins)), by = Math.min(bins - 1, Math.floor((1 - (mid + 1) * .5) * bins)), value = ++density[by * bins + bx]; densityMax = Math.max(densityMax, value); }
    const densityImage = phase.ctx.createImageData(bins, bins);
    for (let i = 0; i < density.length; i += 1) { const q = Math.log1p(density[i]) / Math.log1p(densityMax), p = i * 4; densityImage.data[p] = 30 + 190 * q * q; densityImage.data[p + 1] = 35 + 220 * q; densityImage.data[p + 2] = 70 + 185 * Math.sqrt(q); densityImage.data[p + 3] = q ? 255 : 0; }
    const densityLayer = document.createElement('canvas'); densityLayer.width = bins; densityLayer.height = bins; densityLayer.getContext('2d').putImageData(densityImage, 0, 0); phase.ctx.imageSmoothingEnabled = true; phase.ctx.drawImage(densityLayer, phase.left, phase.top, phase.right - phase.left, phase.bottom - phase.top); axisTicks(phase, [[0, '-1'], [.5, '0'], [1, '+1']], [[0, '-1'], [.5, '0'], [1, '+1']]);

    const emotion = frame(canvases.emotion, 'DARK ← BRIGHT', 'CALM → ACTIVE');
    const centroid = average.reduce((sum, magnitude, i) => sum + magnitude * i, 0) / Math.max(1e-9, average.reduce((sum, magnitude) => sum + magnitude, 0)) / average.length;
    const activity = Math.min(1, Math.max(.05, rmsTotal / Math.max(1, (dynamics.right - dynamics.left) / 2) * 5)); const ex = emotion.left + centroid * (emotion.right - emotion.left), ey = emotion.bottom - activity * (emotion.bottom - emotion.top);
    const gradient = emotion.ctx.createRadialGradient(ex, ey, 0, ex, ey, 42); gradient.addColorStop(0, 'rgba(255,103,175,.9)'); gradient.addColorStop(.35, 'rgba(124,101,255,.55)'); gradient.addColorStop(1, 'rgba(50,214,255,0)'); emotion.ctx.fillStyle = gradient; emotion.ctx.fillRect(ex - 44, ey - 44, 88, 88); emotion.ctx.fillStyle = '#fff'; emotion.ctx.beginPath(); emotion.ctx.arc(ex, ey, 3, 0, Math.PI * 2); emotion.ctx.fill();
  };

  const renderMetrics = metrics => {
    const priority = ['integrated_lufs', 'true_peak_dbfs', 'crest_factor_db', 'estimated_high_frequency_cutoff_hz', 'negative_correlation_ratio', 'phase_risk_ratio'];
    metricStrip.replaceChildren(...priority.filter(key => metrics[key]?.value != null).map(key => {
      const item = document.createElement('div'); const value = Number(metrics[key].value); item.innerHTML = `<span>${key.replaceAll('_', ' ').toUpperCase()}</span><strong>${Number.isFinite(value) ? value.toFixed(Math.abs(value) < 10 ? 2 : 1) : metrics[key].value}<small>${metrics[key].unit || ''}</small></strong>`; return item;
    }));
  };

  const addMessage = (role, text) => {
    const item = document.createElement('div');
    item.className = `message ${role}`;
    item.textContent = text;
    conversation.append(item);
    conversation.scrollTop = conversation.scrollHeight;
  };

  const renderEvidence = async (data, file) => {
    const report = data.report || {};
    const caseRecord = data.case || {};
    currentContext = {
      source_name: report.source_name || file.name,
      overall_status: report.overall_status || 'UNKNOWN',
      summary: report.summary || '',
      sections: report.sections || {},
      findings: report.findings || [],
      authority_state: caseRecord.authority_state || 'HUMAN_REQUIRED',
    };
    resultTitle.textContent = report.source_name || file.name;
    resultStatus.textContent = report.overall_status || 'UNKNOWN';
    renderMetrics(data.metrics || {});
    hearingMap.replaceChildren(...Object.entries(report.sections || {}).map(([key, state]) => {
      const card = document.createElement('article');
      card.className = `sense ${String(state).toLowerCase()}`;
      const label = document.createElement('span');
      label.textContent = sectionLabels[key] || key;
      const value = document.createElement('strong');
      value.textContent = state;
      card.append(label, value);
      return card;
    }));
    judgeDecision.textContent = caseRecord.authority_state || 'HUMAN_REQUIRED';
    judgeSummary.textContent = report.summary || '机器证据不足，需要人工听审。';
    jsonView.textContent = JSON.stringify(data, null, 2);
    uploadPanel.classList.add('compact');
    resultView.hidden = false;
    await new Promise(resolve => requestAnimationFrame(resolve));
    try { await drawScientificPlots(file); } catch { notice.textContent = '声学报告已完成；当前浏览器无法生成本地声学图像。'; }
    addMessage('ai', `我已经完成 HEAR。当前 Judge 状态：${judgeDecision.textContent}。你可以继续问我证据意味着什么。`);
  };

  chooseFile.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    const file = fileInput.files?.[0];
    fileLabel.textContent = file?.name || '上传音乐';
    hearButton.disabled = !file;
    notice.textContent = '';
  });

  hearButton.addEventListener('click', async () => {
    const file = fileInput.files?.[0];
    if (!file) return;
    if (file.size > MAX_UPLOAD_BYTES) {
      notice.textContent = '文件超过 50 MB，请导出较小版本后重试。';
      return;
    }
    hearButton.disabled = true;
    hearButton.textContent = 'HEARING…';
    notice.textContent = '';
    const payload = new FormData();
    payload.append('audio', file);
    try {
      const response = await fetch('/api/v1/auditory/analyze', { method: 'POST', body: payload });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail?.message || data.detail?.code || `Cloud request failed (${response.status})`);
      await renderEvidence(data, file);
    } catch (error) {
      notice.textContent = error instanceof Error ? error.message : 'HEAR 失败，请稍后重试。';
    } finally {
      hearButton.disabled = false;
      hearButton.textContent = '重新 HEAR';
    }
  });

  chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;
    addMessage('user', message);
    chatInput.value = '';
    chatButton.disabled = true;
    try {
      const response = await fetch('/api/v1/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, context: currentContext }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail?.code || `AI request failed (${response.status})`);
      addMessage('ai', data.answer);
    } catch (error) {
      addMessage('ai', error instanceof Error && error.message === 'MODEL_UNAVAILABLE'
        ? 'Moodify AI 当前未连接模型。HEAR 仍可独立使用。'
        : '对话暂时不可用，请稍后重试。');
    } finally {
      chatButton.disabled = false;
      chatInput.focus();
    }
  });
})();
