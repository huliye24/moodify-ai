/**
 * Moodify Studio — LRC 歌词解析与逐行定位（karaoke-free，逐行粒度）。
 *
 * 本文件不依赖 DOM、不依赖浏览器：它只把歌词文本变成有序时间轴，
 * 并回答「t 时刻该高亮第几行」。这样解析器可以在 Node 里被真正测到，
 * 而不是靠肉眼看 UI 滚得对不对。
 *
 * 只做**逐行**粒度：LRC 标准本身不含逐字时间戳，逐字卡拉 OK 需要
 * 增强型私有格式，本模块不假装支持它。
 *
 * UMD 形状：浏览器里挂到 window.MoodifyLyrics，Node 里 require。
 */

(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.MoodifyLyrics = api;
}(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  /** [mm:ss.xx] / [mm:ss:xx] / [mm:ss] —— 分与秒必须两位以内，厘秒 1~3 位。 */
  const TIME_TAG = /\[(\d{1,3}):(\d{1,2})(?:[.:](\d{1,3}))?\]/g;
  /** [ti:标题] [ar:歌手] [al:专辑] [by:制作] —— 元数据行，不进时间轴。 */
  const META_TAG = /^\[(ti|ar|al|by|au|length|re|ve):[^\]]*\]\s*$/i;
  /** [offset:+250] / [offset:-250] —— 整体时间偏移，单位毫秒。 */
  const OFFSET_TAG = /\[offset:([+-]?\d+)\]/i;

  /** 把厘秒字段统一还原成秒：`.5` = 500ms，`.05` = 50ms，`.005` = 5ms。 */
  function centisToSeconds(raw) {
    if (!raw) return 0;
    return Number(raw) / Math.pow(10, raw.length);
  }

  /**
   * 解析 LRC 文本。
   *
   * 无时间戳的纯文本不会报错：返回 `timed: false` 并把原文按行留下，
   * 由调用方决定降级为静态显示还是提示「这首还没有时间轴」。
   *
   * @param {string} text
   * @returns {{timed: boolean, lines: Array<{time: number, text: string}>, offset: number}}
   *          `lines` 按时间升序；未计时行 time 为 0 且保持原文顺序。
   */
  function parseLrc(text) {
    const source = String(text == null ? '' : text).replace(/\r\n?/g, '\n');
    const lines = [];
    let offset = 0;

    for (const raw of source.split('\n')) {
      const line = raw.trim();
      if (!line) continue;

      const offsetMatch = OFFSET_TAG.exec(line);
      if (offsetMatch) {
        offset += Number(offsetMatch[1]);
        continue;
      }
      if (META_TAG.test(line)) continue;

      // 一行可以带多个时间戳（`[00:12.00][01:20.00]副歌`），每个都展开成独立条目。
      TIME_TAG.lastIndex = 0;
      const stamps = [];
      let match;
      while ((match = TIME_TAG.exec(line)) !== null) {
        const minutes = Number(match[1]);
        const seconds = Number(match[2]);
        stamps.push({
          time: minutes * 60 + seconds + centisToSeconds(match[3]),
          end: match.index + match[0].length,
        });
      }

      if (!stamps.length) {
        lines.push({ time: 0, text: line });
        continue;
      }
      // 取最后一个时间戳之后的全部内容，避免把 `[mm:ss]` 自身当成歌词。
      const tail = line.slice(stamps[stamps.length - 1].end).trim();
      for (const stamp of stamps) lines.push({ time: stamp.time, text: tail });
    }

    if (!lines.length) return { timed: false, lines: [], offset };
    const timed = lines.some((item) => item.time > 0);
    if (timed) {
      // 只有存在真实时间轴时才排序；纯文本行的原始顺序是内容，不能被打乱。
      lines.sort((a, b) => a.time - b.time);
    }
    if (offset) {
      for (const item of lines) item.time = Math.max(0, item.time + offset / 1000);
    }
    return { timed, lines, offset };
  }

  /**
   * t 时刻应该高亮的行下标；早于第一行时返回 -1（此时不点亮任何行）。
   *
   * @param {Array<{time: number}>} lines 必须已按时间升序
   * @param {number} t 秒
   */
  function activeLineIndex(lines, t) {
    if (!Array.isArray(lines) || !lines.length) return -1;
    const time = Number.isFinite(t) ? t : 0;
    let lo = 0;
    let hi = lines.length - 1;
    let found = -1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      if (lines[mid].time <= time) { found = mid; lo = mid + 1; } else { hi = mid - 1; }
    }
    return found;
  }

  return { parseLrc, activeLineIndex, TIME_TAG, META_TAG, OFFSET_TAG };
}));
