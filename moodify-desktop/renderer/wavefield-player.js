/**
 * Moodify Studio — Wave Field 走带权威（single playback authority）。
 *
 * 规则（Wave Field Local v0 §17）：**一个视图只有一个播放权威**。
 * 切换候选必须先停掉上一个；绝不允许两条音轨同时响。
 * 原版永远可用，且永远只有一条在响。
 *
 * 本文件不依赖 DOM，也不依赖 WaveSurfer：它只通过注入的 `audio` 后端
 * （浏览器里是唯一一个 AudioContext）发声。这样「不会重叠」这条规则
 * 可以在 Node 里被真正测到，而不是靠肉眼看 UI。
 *
 * UMD 形状：浏览器里挂到 window.MoodifyWaveFieldPlayer，Node 里 require。
 */

(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.MoodifyWaveFieldPlayer = api;
}(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  /** 候选展示顺序：原版在前，A/B/C 依字段尺度递增。 */
  const CANDIDATE_ORDER = ['ORIGINAL', 'A', 'B', 'C'];

  /**
   * 建立走带权威。
   *
   * @param {object} deps
   * @param {object} deps.audio  音频后端，**由调用方保证唯一**：
   *   - `decode(bytesOrBuffer) -> Promise<buffer>`（buffer 至少有 `duration`）
   *   - `createSource(buffer) -> { start(when, offset), stop(), onended }`
   *   - `now() -> number`（秒）
   * @param {(state: object) => void} [deps.onStateChange]
   */
  function createPlayer(deps) {
    const audio = (deps && deps.audio) || null;
    const onStateChange = (deps && deps.onStateChange) || function () {};

    const buffers = new Map();
    /** 唯一的活动音源。同一时刻至多一个 —— 这就是「不重叠」的实现。 */
    let active = null;
    let currentId = null;
    let status = 'idle';
    let startedAt = 0;
    /** 每次切换递增；解码晚到的旧结果据此丢弃。 */
    let token = 0;

    function position() {
      if (status !== 'playing' || !audio || typeof audio.now !== 'function') return 0;
      const buffer = buffers.get(currentId);
      const elapsed = audio.now() - startedAt;
      const duration = buffer && typeof buffer.duration === 'number' ? buffer.duration : elapsed;
      return Math.max(0, Math.min(elapsed, duration));
    }

    function publish(extra) {
      const state = Object.assign({
        current: currentId,
        status: status,
        loaded: Array.from(buffers.keys()),
        position: position(),
      }, extra || {});
      try { onStateChange(state); } catch { /* 表现层回调不得影响走带 */ }
      return state;
    }

    /** 停掉唯一的活动音源。幂等。 */
    function stopActive() {
      if (!active) return;
      const node = active;
      active = null;
      try { node.stop(); } catch { /* already ended */ }
    }

    function startCurrent() {
      if (!audio || !buffers.has(currentId)) return false;
      stopActive();
      const node = audio.createSource(buffers.get(currentId));
      node.onended = function () {
        if (active !== node) return; // 已被更晚的切换取代
        active = null;
        status = 'paused';
        publish({ ended: true });
      };
      active = node;
      startedAt = typeof audio.now === 'function' ? audio.now() : 0;
      node.start(0, 0);
      status = 'playing';
      return true;
    }

    return {
      /** 已加载的候选 id（按声明顺序）。 */
      loadedIds() {
        return CANDIDATE_ORDER.filter((id) => buffers.has(id));
      },

      /** 当前候选 id —— 「现在装着哪一版」的唯一答案。 */
      current() { return currentId; },

      status() { return status; },

      isPlaying() { return status === 'playing'; },

      position,

      /** 当前候选的缓冲（供波形绘制）。 */
      buffer(id) { return buffers.get(id) || null; },

      /** 诊断/测试用：此刻有几条音源在响。恒为 0 或 1。 */
      activeCount() { return active ? 1 : 0; },

      /**
       * 载入一个候选的音频字节。
       *
       * 正在播放时切换：**先停掉上一个**，再从新候选头部开始 ——
       * 不保留旧位置，因为不同波场的「同一时间点」本来就不是同一件事。
       *
       * @param {string} id
       * @param {ArrayBuffer|Uint8Array} bytes
       * @returns {Promise<object>} 走带状态快照
       */
      async load(id, bytes) {
        if (!audio) return publish({ ok: false, reason: 'NO_AUDIO_BACKEND' });

        if (buffers.has(id)) {
          const wasPlaying = status === 'playing';
          currentId = id;
          if (wasPlaying) startCurrent();
          return publish({ ok: true, cached: true });
        }

        const previousStatus = status;
        const mine = ++token;
        status = 'loading';
        publish();

        let buffer;
        try {
          buffer = await audio.decode(bytes);
        } catch (err) {
          if (mine !== token) return publish({ ok: false, reason: 'SUPERSEDED', stale: true });
          // 失败时保持原来那一版可播放：绝不把状态切成「已切到新版」。
          status = active ? 'playing' : previousStatus;
          return publish({
            ok: false,
            reason: 'DECODE_FAILED',
            detail: (err && err.message) || String(err),
          });
        }
        if (mine !== token) return publish({ ok: false, reason: 'SUPERSEDED', stale: true });

        buffers.set(id, buffer);
        currentId = id;
        if (previousStatus === 'playing') startCurrent();
        else status = 'paused';
        return publish({ ok: true });
      },

      /**
       * 播放某个候选。未载入则明确拒绝（不隐式去取字节）。
       * 切到另一版时先停掉当前音源，再从头部开始。
       */
      play(id) {
        if (!buffers.has(id)) return publish({ ok: false, reason: 'NOT_LOADED', id: id });
        currentId = id;
        const started = startCurrent();
        return publish({ ok: started, reason: started ? undefined : 'NO_AUDIO_BACKEND' });
      },

      /** 播放 / 暂停当前候选。 */
      toggle() {
        if (status === 'playing') return this.pause();
        if (!currentId) return publish({ ok: false, reason: 'NOTHING_LOADED' });
        return this.play(currentId);
      },

      pause() {
        stopActive();
        if (status === 'playing') status = 'paused';
        return publish();
      },

      /** 停止并回到 0：切换候选前的显式动作。 */
      stop() {
        stopActive();
        status = buffers.size ? 'paused' : 'idle';
        return publish();
      },

      /** 换世界 / 换 case 时调用：清空全部缓冲与状态。 */
      reset() {
        stopActive();
        buffers.clear();
        currentId = null;
        status = 'idle';
        token += 1;
        return publish({ reset: true });
      },
    };
  }

  return { CANDIDATE_ORDER: CANDIDATE_ORDER, createPlayer: createPlayer };
}));
