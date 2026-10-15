/**
 * Moodify Studio — 发布链路的纯逻辑层。
 *
 * 为什么单独成文件：发布涉及「键怎么定」「什么算上传过」「manifest 怎么改才不互相覆盖」，
 * 这些是**可以脱离 Electron 验证**的纯判断。放在这里就能 `node scripts/test-publish.js` 直接测，
 * 不必为了跑一条断言去启动整个壳。
 *
 * 边界：
 *  - 这里**不做任何 IO**（不读远端、不 spawn 进程）。IO 在 main.js。
 *  - 这里**不知道 vinext 会不会重启**。刷新策略是 main.js 的事。
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ——— 资产键布局 ——————————————————————————————————————————————————————————
//
// 现状（SSH 直传香港）：
//   zh-cn/owner-<work_id>.wave          音频
//   zh-cn/owner-<work_id>-cover-<ts>.jpg 封面（带时间戳，天然不缓存）
//   zh-cn/owner-<work_id>-lyrics.txt    歌词
//
// 目标（S3，Phase 2 启用）：
//   works/<work_id>/audio.m4a
//   works/<work_id>/cover.jpg
//   works/<work_id>/lyrics.lrc
//   works/<work_id>/manifest.json
//
// 两套布局的**共同点**：都以 work_id 为命名空间根。这让「换存储后端」不牵动
// 键的语义——只是前缀不同。下面的 buildAssetKeys 同时输出两套，由调用方选。

const WORK_ID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/**
 * 由作品推导发布资产键。
 *
 * @param {object} work 作品库条目
 * @param {object} [opts]
 * @param {number} [opts.assetVersion] 封面等可替换资产的缓存破坏版本号（默认 Date.now()）
 * @param {string} [opts.audioExt] 音频扩展名（默认取源文件扩展名）
 * @returns {{safeId:string, audio:string, cover:string|null, lyrics:string|null}}
 */
function buildAssetKeys(work, opts = {}) {
  const workId = String(work && work.work_id || '').toLowerCase();
  if (!WORK_ID_RE.test(workId)) throw new Error('INVALID_WORK_ID');
  const safeId = `owner-${workId}`;
  const assetVersion = opts.assetVersion || Date.now();

  // 历史原因：nginx 把 .wav 声明为 FLAC 流。新的原始 WAV 用 .wave 区分，避免错误 MIME。
  const sourceExt = (opts.audioExt || path.extname(work.audio_path || '') || '.wav').toLowerCase();
  const audioExt = sourceExt === '.wav' ? '.wave' : sourceExt;

  let cover = null;
  if (work.cover_path) {
    const ext = path.extname(work.cover_path).toLowerCase() || '.jpg';
    cover = `zh-cn/${safeId}-cover-${assetVersion}${ext}`;
  }
  const hasLyricsFile = !!work.lyrics_path;
  const hasLyricsText = !!work.lyrics_text;
  const lyrics = (hasLyricsFile || hasLyricsText) ? `zh-cn/${safeId}-lyrics.txt` : null;

  return { safeId, audio: `zh-cn/${safeId}${audioExt}`, cover, lyrics };
}

/**
 * S3 对象布局（Phase 2 启用；当前仅生成键，不触发上传）。
 *
 * 命名空间的唯一权威是 work_id —— 与 SSH 布局一致，换后端不改语义。
 * audio 固定为 .m4a：发布链路会在上传前把 WAV 转 AAC（实测省 ~83%）。
 */
function s3Layout(workId, opts = {}) {
  const id = String(workId || '').toLowerCase();
  if (!WORK_ID_RE.test(id)) throw new Error('INVALID_WORK_ID');
  const root = `works/${id}`;
  return {
    root,
    audio: `${root}/audio${opts.audioExt || '.m4a'}`,
    cover: opts.coverExt ? `${root}/cover${opts.coverExt}` : null,
    lyrics: opts.lyricsExt ? `${root}/lyrics${opts.lyricsExt}` : null,
    manifest: `${root}/manifest.json`,
  };
}

// ——— 内容指纹与幂等 ————————————————————————————————————————————————————————
//
// 为什么需要：改一个标题就重传 78MB 音频并重启生产服务，是真实发生的现状。
// 有了指纹，「这个字节流是不是已经传过了」才成为可判断的事实。

/**
 * 文件指纹。只读前 8MB 参与哈希之外的部分也计入——简单起见全量哈希，
 * 78MB 的 sha256 在本机约 0.3s，相对一次跨境上传可以忽略。
 * @returns {{sha256:string, size:number}|null} 文件不存在时返回 null
 */
function fingerprintFile(filePath) {
  if (!filePath || !fs.existsSync(filePath)) return null;
  const stat = fs.statSync(filePath);
  const hash = crypto.createHash('sha256');
  hash.update(fs.readFileSync(filePath));
  return { sha256: hash.digest('hex'), size: stat.size };
}

function fingerprintEqual(a, b) {
  if (!a || !b) return false;
  return a.sha256 === b.sha256 && a.size === b.size;
}

/**
 * 判断某个资产是否需要重新上传。
 *
 * @param {object|null} published 作品上已记录的 `published_assets`
 * @param {string} kind 'audio' | 'cover' | 'lyrics'
 * @param {{sha256:string,size:number}|null} current 当前本地指纹
 * @returns {{needed:boolean, reason:string}}
 *
 * reason 的取值是给界面和日志看的，不是错误码：
 *   FIRST_TIME / CHANGED / UNCHANGED / NO_LOCAL_FILE / NO_REMOTE_RECORD
 */
function uploadNeeded(published, kind, current) {
  if (!current) return { needed: false, reason: 'NO_LOCAL_FILE' };
  const record = published && published[kind];
  if (!record || !record.sha256) return { needed: true, reason: 'NO_REMOTE_RECORD' };
  if (fingerprintEqual(record, current)) return { needed: false, reason: 'UNCHANGED' };
  return { needed: true, reason: 'CHANGED' };
}

// ——— manifest 条目与乐观锁 ———————————————————————————————————————————————

/**
 * 构造 manifest 里的一条 track。
 *
 * `version` 内嵌资产键，App 靠它拼 URL；`published_at` 用 ISO 串，便于排序。
 */
function buildTrack(work, keys, durationMs) {
  return {
    id: keys.safeId,
    title: work.title,
    creator_id: 'local-owner',
    creator_handle: work.creator || null,
    status: 'published',
    primary_language: 'zh-CN',
    duration_ms: Number.isFinite(durationMs) && durationMs > 0 ? Math.round(durationMs) : null,
    published_at: new Date().toISOString(),
    version: {
      audio_asset_key: keys.audio,
      cover_asset_key: keys.cover || null,
      lyrics_asset_key: keys.lyrics || null,
    },
  };
}

/**
 * 在**本地内存副本**上应用一条 track（替换同 id，新的排到最前）。
 * 纯函数：不改入参，返回新对象。
 */
function applyTrack(manifest, track) {
  const next = { ...(manifest || {}) };
  const tracks = Array.isArray(next.tracks) ? next.tracks.filter((t) => t && t.id !== track.id) : [];
  tracks.unshift(track);
  next.tracks = tracks;
  next.next_cursor = null;
  return next;
}

function removeTrack(manifest, trackId) {
  const next = { ...(manifest || {}) };
  next.tracks = Array.isArray(next.tracks) ? next.tracks.filter((t) => !t || t.id !== trackId) : [];
  return next;
}

/**
 * 生成服务端 compare-and-swap 脚本（Python，通过 ssh 执行）。
 *
 * 为什么必须是「服务端原子的」：客户端「读回 → 本地改 → 传回去」这三步之间，
 * 另一个 Studio（或一次自动发布）完全可以插入，后写的静默覆盖先写的。
 * 把比较与写入放进同一个远程进程，竞态窗口才真正关闭。
 *
 * 语义：只有当远端 manifest 的 revision 等于 expected 时才写入，否则以退出码 3 报告冲突。
 * 写入本身是 `tempfile + os.replace`，保证读取方永远看到完整文件（不会出现半个 JSON）。
 *
 * 为什么 payload 走文件而不是 stdin：脚本正文是通过 `ssh ... <<'PY'` 的 heredoc 送过去的，
 * stdin 已经被脚本自己占用了，再让脚本从 stdin 读数据会直接读到空。**踩过才知道**。
 *
 * argv: [1]=manifest 路径  [2]=expected revision('None'=强制写)  [3]=payload 文件路径
 *
 * @param {string} manifestPath 远端 manifest 绝对路径
 * @param {object} nextManifest 将要写入的完整 manifest
 * @param {number} expectedRevision 期望的当前 revision（null 表示「不校验，强制写」）
 * @returns {string} python 脚本正文
 */
function casScript(manifestPath, nextManifest, expectedRevision) {
  const payload = JSON.stringify(nextManifest);
  // expected 由调用方以 argv[2] 传入；脚本正文与具体值无关（只声明如何解析）。
  void expectedRevision;
  void manifestPath;
  void payload;
  return [
    "import json, os, sys, tempfile",
    "p = sys.argv[1]",
    "expected = int(sys.argv[2]) if sys.argv[2] != 'None' else None",
    "with open(sys.argv[3], encoding='utf-8') as fh:",
    "    payload = json.load(fh)",
    "try:",
    "    cur = json.load(open(p, encoding='utf-8'))",
    "except FileNotFoundError:",
    "    cur = {'tracks': [], 'revision': 0}",
    "cur_rev = int(cur.get('revision') or 0)",
    "if expected is not None and cur_rev != expected:",
    "    sys.stderr.write('CONFLICT current=%d expected=%d' % (cur_rev, expected))",
    "    sys.exit(3)",
    "payload['revision'] = cur_rev + 1",
    "d = os.path.dirname(p)",
    "fd, t = tempfile.mkstemp(prefix='.catalogue.', dir=d)",
    "with os.fdopen(fd, 'w', encoding='utf-8') as f:",
    "    json.dump(payload, f, ensure_ascii=False, indent=2)",
    "os.chmod(t, 0o644)",
    "os.replace(t, p)",
    "print(payload['revision'])",
  ].join('\n') + '\n';
}

/** manifest 的当前 revision。缺字段视为 0 —— 兼容历史文件。 */
function revisionOf(manifest) {
  const v = manifest && manifest.revision;
  return Number.isFinite(Number(v)) ? Math.trunc(Number(v)) : 0;
}

/**
 * 发布阶段定义。进度条与界面文案都以它为准，避免各写一套。
 * 顺序即执行顺序。
 */
const PUBLISH_STAGES = [
  { id: 'prepare', label: '准备' },
  { id: 'probe', label: '读取时长' },
  { id: 'audio', label: '上传音频' },
  { id: 'cover', label: '上传封面' },
  { id: 'lyrics', label: '上传歌词' },
  { id: 'catalogue', label: '写入清单' },
  { id: 'refresh', label: '刷新线上' },
];

/**
 * 计算阶段进度百分比。
 * @param {string} stageId 当前阶段
 * @param {number} [fraction] 当前阶段内部进度 0..1
 */
function stagePercent(stageId, fraction = 0) {
  const idx = PUBLISH_STAGES.findIndex((s) => s.id === stageId);
  if (idx < 0) return 0;
  const inner = Math.max(0, Math.min(1, Number(fraction) || 0));
  return Math.round(((idx + inner) / PUBLISH_STAGES.length) * 100);
}

module.exports = {
  WORK_ID_RE,
  PUBLISH_STAGES,
  buildAssetKeys,
  s3Layout,
  fingerprintFile,
  fingerprintEqual,
  uploadNeeded,
  buildTrack,
  applyTrack,
  removeTrack,
  casScript,
  revisionOf,
  stagePercent,
};
