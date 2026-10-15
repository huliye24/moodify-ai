const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function safeText(value, max = 200) { return String(value || '').trim().slice(0, max); }
function readJson(file, fallback) { try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return fallback; } }
function libraryFile(root) { return path.join(root, 'library.json'); }
function atomicJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const next = `${file}.next`;
  fs.writeFileSync(next, JSON.stringify(value, null, 2), 'utf8');
  fs.renameSync(next, file);
}
function snapshot(root) {
  const value = readJson(libraryFile(root), { schema_version: 'moodify.library.v1', works: [] });
  return { schema_version: 'moodify.library.v1', works: Array.isArray(value.works) ? value.works : [] };
}
function copyAsset(root, workId, source, kind) {
  if (!source) return null;
  if (!fs.existsSync(source) || !fs.statSync(source).isFile()) throw new Error(`${kind.toUpperCase()}_FILE_NOT_FOUND`);
  const ext = path.extname(source).toLowerCase();
  const dir = path.join(root, 'works', workId);
  fs.mkdirSync(dir, { recursive: true });
  const target = path.join(dir, `${kind}${ext}`);
  fs.copyFileSync(source, target);
  return target;
}
function create(root, input = {}) {
  const title = safeText(input.title, 120);
  if (!title) throw new Error('TITLE_REQUIRED');
  if (!input.audio_path) throw new Error('AUDIO_REQUIRED');
  const now = new Date().toISOString();
  const workId = crypto.randomUUID();
  const work = {
    work_id: workId, owner_id: 'local-owner', title,
    creator: safeText(input.creator, 120),
    audio_path: copyAsset(root, workId, input.audio_path, 'audio'),
    cover_path: copyAsset(root, workId, input.cover_path, 'cover'),
    lyrics_path: copyAsset(root, workId, input.lyrics_path, 'lyrics'),
    lyrics_text: safeText(input.lyrics_text, 20000),
    status: 'LOCAL_DRAFT', cloud_status: 'NOT_PUBLISHED', created_at: now, updated_at: now,
  };
  const value = snapshot(root);
  value.works.unshift(work);
  atomicJson(libraryFile(root), value);
  return work;
}
function markPublishing(root, workId, cloudStatus, detail = '') {
  const value = snapshot(root);
  const work = value.works.find((item) => item.work_id === workId);
  if (!work) throw new Error('WORK_NOT_FOUND');
  work.cloud_status = cloudStatus;
  work.cloud_detail = safeText(detail, 500);
  work.updated_at = new Date().toISOString();
  atomicJson(libraryFile(root), value);
  return work;
}
/**
 * 记录本次实际发布到远端的资产指纹与键。
 *
 * 为什么需要：发布能否「跳过未变化的资产」，取决于是否记得上次传过的字节。
 * 没有这份记录，改一个标题就要重传 78MB 音频外加重启生产服务。
 *
 * 只存指纹与键，**不存音频内容**；指纹为 null 表示该资产本次不存在（会被清除）。
 *
 * @param {object} assets { audio, cover, lyrics } 每项为 {sha256,size}|null
 * @param {object} [keys] { audio_key, cover_key, lyrics_key }
 */
function recordPublishedAssets(root, workId, assets = {}, keys = {}) {
  const value = snapshot(root);
  const work = value.works.find((item) => item.work_id === workId);
  if (!work) throw new Error('WORK_NOT_FOUND');
  const next = {};
  for (const kind of ['audio', 'cover', 'lyrics']) {
    const fp = assets[kind];
    if (fp && fp.sha256) next[kind] = { sha256: fp.sha256, size: fp.size };
  }
  next.audio_key = keys.audio_key || null;
  next.cover_key = keys.cover_key || null;
  next.lyrics_key = keys.lyrics_key || null;
  work.published_assets = next;
  work.updated_at = new Date().toISOString();
  atomicJson(libraryFile(root), value);
  return work;
}

function update(root, workId, patch = {}) {
  const value = snapshot(root);
  const work = value.works.find((item) => item.work_id === workId);
  if (!work) throw new Error('WORK_NOT_FOUND');
  if (Object.prototype.hasOwnProperty.call(patch, 'title')) {
    const title = safeText(patch.title, 120); if (!title) throw new Error('TITLE_REQUIRED'); work.title = title;
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'creator')) work.creator = safeText(patch.creator, 120);
  if (Object.prototype.hasOwnProperty.call(patch, 'lyrics_text')) work.lyrics_text = safeText(patch.lyrics_text, 20000);
  work.updated_at = new Date().toISOString();
  atomicJson(libraryFile(root), value);
  return work;
}
function remove(root, workId) {
  const value = snapshot(root);
  const work = value.works.find((item) => item.work_id === workId);
  if (!work) throw new Error('WORK_NOT_FOUND');
  value.works = value.works.filter((item) => item.work_id !== workId);
  atomicJson(libraryFile(root), value);
  return work;
}
/**
 * 读取一首作品的歌词文本。
 *
 * 只收 work_id，**不接受任意路径**：文件位置一律由作品库自己从快照里解析，
 * 所以这里不存在路径穿越——这与 `audio:read` 那条来者不拒的旧通道不同。
 *
 * 编码：**只认 UTF-8**。中文 LRC 在外部工具里经常被存成 GBK，Node 没有内置
 * GBK 解码器；与其显示一堆乱码，不如如实告诉用户去另存为 UTF-8。
 * 「读不出内容」和「内容本来就是空的」是两件事，都要能区分。
 *
 * @returns {{text: string, source: 'file'|'text'|'none', reason: string|null}}
 */
function readLyrics(root, workId) {
  const value = snapshot(root);
  const work = value.works.find((item) => item.work_id === workId);
  if (!work) throw new Error('WORK_NOT_FOUND');
  if (work.lyrics_path && fs.existsSync(work.lyrics_path)) {
    let buffer;
    try { buffer = fs.readFileSync(work.lyrics_path); } catch { return { text: '', source: 'none', reason: 'LYRICS_FILE_UNREADABLE' }; }
    // 去掉 UTF-8 BOM；UTF-16 的 LRC 不在支持范围内，同样如实拒绝。
    if (buffer.length >= 3 && buffer[0] === 0xef && buffer[1] === 0xbb && buffer[2] === 0xbf) buffer = buffer.subarray(3);
    else if (buffer.length >= 2 && (buffer[0] === 0xff && buffer[1] === 0xfe) || (buffer[0] === 0xfe && buffer[1] === 0xff)) {
      return { text: '', source: 'none', reason: 'LYRICS_ENCODING_UTF16' };
    }
    try {
      const text = new TextDecoder('utf-8', { fatal: true }).decode(buffer);
      return { text, source: 'file', reason: null };
    } catch {
      return { text: '', source: 'none', reason: 'LYRICS_ENCODING_NOT_UTF8' };
    }
  }
  if (work.lyrics_text) return { text: work.lyrics_text, source: 'text', reason: null };
  return { text: '', source: 'none', reason: null };
}

module.exports = {
  snapshot, create, markPublishing, update, remove, readLyrics, recordPublishedAssets,
};
