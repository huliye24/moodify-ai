const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const library = require('../src/music-library');
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-library-'));
const audio = path.join(root, 'input.wav');
fs.writeFileSync(audio, 'audio');
const work = library.create(root, { title: ' 测试作品 ', audio_path: audio, lyrics_text: '第一句' });
assert.equal(work.title, '测试作品');
assert.equal(work.owner_id, 'local-owner');
assert.equal(library.snapshot(root).works.length, 1);
assert.ok(fs.existsSync(work.audio_path));
assert.equal(library.markPublishing(root, work.work_id, 'QUEUED').cloud_status, 'QUEUED');
const updated = library.update(root, work.work_id, { title: '新歌名', creator: '创作者', lyrics_text: '新歌词' });
assert.equal(updated.title, '新歌名');
assert.equal(updated.creator, '创作者');
assert.equal(updated.lyrics_text, '新歌词');
assert.equal(library.remove(root, work.work_id).work_id, work.work_id);
assert.equal(library.snapshot(root).works.length, 0);
assert.throws(() => library.create(root, { title: '', audio_path: audio }), /TITLE_REQUIRED/);

// ——— 歌词读取：作品试音的滚动歌词从这里拿文本 ———
const lrcSource = path.join(root, 'song.lrc');
fs.writeFileSync(lrcSource, '[00:12.50]第一行\n[00:20.00]第二行', 'utf8');
const timed = library.create(root, { title: '带歌词', audio_path: audio, lyrics_path: lrcSource });
const timedRead = library.readLyrics(root, timed.work_id);
assert.equal(timedRead.source, 'file');
assert.equal(timedRead.text, '[00:12.50]第一行\n[00:20.00]第二行');
assert.equal(timedRead.reason, null);

// 只有手写纯文本时回落到纯文本，而不是报"没有歌词"
const plain = library.create(root, { title: '纯文本歌词', audio_path: audio, lyrics_text: '没有时间轴的一句' });
const plainRead = library.readLyrics(root, plain.work_id);
assert.equal(plainRead.source, 'text');
assert.equal(plainRead.text, '没有时间轴的一句');

// 两者都没有：明说是 none，不假装成空字符串内容
const bare = library.create(root, { title: '无歌词', audio_path: audio });
const bareRead = library.readLyrics(root, bare.work_id);
assert.equal(bareRead.source, 'none');
assert.equal(bareRead.text, '');
assert.equal(bareRead.reason, null);

// UTF-8 BOM 要被剥掉，否则首行时间戳解析不出来
const bomSource = path.join(root, 'bom.lrc');
fs.writeFileSync(bomSource, Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from('[00:01.00]有BOM', 'utf8')]));
const bom = library.create(root, { title: '有BOM', audio_path: audio, lyrics_path: bomSource });
const bomRead = library.readLyrics(root, bom.work_id);
assert.equal(bomRead.text, '[00:01.00]有BOM');

// 非 UTF-8（中文 LRC 常见的 GBK）：如实拒绝，绝不返回乱码
const gbkSource = path.join(root, 'gbk.lrc');
fs.writeFileSync(gbkSource, Buffer.from([0x5b, 0x30, 0x30, 0x3a, 0x30, 0x31, 0x2e, 0x30, 0x30, 0x5d, 0xd7, 0xd6]));
const gbk = library.create(root, { title: 'GBK', audio_path: audio, lyrics_path: gbkSource });
const gbkRead = library.readLyrics(root, gbk.work_id);
assert.equal(gbkRead.source, 'none');
assert.equal(gbkRead.text, '');
assert.equal(gbkRead.reason, 'LYRICS_ENCODING_NOT_UTF8');

// 不存在的作品要炸，不能静默返回空
assert.throws(() => library.readLyrics(root, 'no-such-work'), /WORK_NOT_FOUND/);

// ——— 已发布资产指纹：发布幂等判断的事实依据 ———
const fpWork = library.create(root, { title: '指纹', audio_path: audio });
const fp = { sha256: 'a'.repeat(64), size: 12345 };
const rec = library.recordPublishedAssets(root, fpWork.work_id, {
  audio: fp, cover: null, lyrics: null,
}, { audio_key: 'zh-cn/owner-x.wave', cover_key: null, lyrics_key: null });
assert.equal(rec.published_assets.audio.sha256, fp.sha256);
assert.equal(rec.published_assets.audio.size, 12345);
assert.equal(rec.published_assets.audio_key, 'zh-cn/owner-x.wave');
// 资产不存在时不应写入半成品指纹（null 指纹要被忽略，而不是记成 {sha256: undefined}）
assert.equal(rec.published_assets.cover, undefined);
assert.equal(rec.published_assets.lyrics, undefined);
// 快照里必须能读回（说明真的落盘了）
const reRead = library.snapshot(root).works.find((w) => w.work_id === fpWork.work_id);
assert.equal(reRead.published_assets.audio.sha256, fp.sha256);
// 重录时应整体替换，而不是与旧值合并
const rec2 = library.recordPublishedAssets(root, fpWork.work_id, {
  audio: { sha256: 'b'.repeat(64), size: 999 }, cover: null, lyrics: null,
}, { audio_key: 'zh-cn/owner-y.wave' });
assert.equal(rec2.published_assets.audio.sha256, 'b'.repeat(64));
assert.equal(rec2.published_assets.cover_key, null);
// 不存在的作品要炸
assert.throws(() => library.recordPublishedAssets(root, 'no-such-work', {}), /WORK_NOT_FOUND/);

fs.rmSync(root, { recursive: true, force: true });
console.log('music-library: ok');
