/**
 * test-publish.js — 发布链路纯逻辑的单元测试。
 *
 * 设计：
 *  - 不依赖 electron，可被 `node` 直接跑
 *  - 断言函数行为，不断言实现细节
 *  - 跑通即说明「键布局 / 幂等判断 / manifest 改造 / CAS 脚本」这四类
 *    「在并发与回放场景下也不变形的契约」成立
 */

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const P = require('../src/publish');

function ok(label, fn) { fn(); console.log('  ok  ' + label); }
function group(name, fn) { console.log('\n# ' + name); fn(); }

// 合法 UUID 夹具（work_id 必须是标准 UUID 格式）
const f = '00000000-0000-0000-0000-000000000001';
const f2 = '00000000-0000-0000-0000-000000000002';

// ── 1. 键布局 ────────────────────────────────────────────────────────────────
group('buildAssetKeys', () => {
  ok('WAV 源默认扩展名是 .wave（避 nginx 的 FLAC 流声明）', () => {
    const k = P.buildAssetKeys({ work_id: '5764AEF3-631E-434D-87A3-C6C6F208618A', audio_path: '/x/audio.wav' });
    assert.equal(k.safeId, 'owner-5764aef3-631e-434d-87a3-c6c6f208618a');
    assert.equal(k.audio, 'zh-cn/owner-5764aef3-631e-434d-87a3-c6c6f208618a.wave');
  });
  ok('FLAC 源扩展名直传', () => {
    const k = P.buildAssetKeys({ work_id: f, audio_path: '/x/a.flac' });
    assert.equal(k.audio.endsWith('.flac'), true);
  });
  ok('封面带资产版本号以破坏缓存', () => {
    const k = P.buildAssetKeys({ work_id: f, audio_path: '/x/a.wav', cover_path: '/c/cover.jpg' }, { assetVersion: 1700000000000 });
    assert.equal(k.cover, `zh-cn/owner-${f}-cover-1700000000000.jpg`);
  });
  ok('只有 cover_path 或 lyrics_text 时才生成对应键', () => {
    const k1 = P.buildAssetKeys({ work_id: f, audio_path: '/x/a.wav' });
    assert.equal(k1.cover, null); assert.equal(k1.lyrics, null);
    const k2 = P.buildAssetKeys({ work_id: f, audio_path: '/x/a.wav', lyrics_path: '/l/lrc' });
    assert.equal(k2.lyrics, `zh-cn/owner-${f}-lyrics.txt`);
    const k3 = P.buildAssetKeys({ work_id: f, audio_path: '/x/a.wav', lyrics_text: 'plain' });
    assert.equal(k3.lyrics, `zh-cn/owner-${f}-lyrics.txt`);
  });
  ok('非法 work_id 抛错', () => {
    assert.throws(() => P.buildAssetKeys({ work_id: 'not-a-uuid', audio_path: '/x/a.wav' }), /INVALID_WORK_ID/);
    assert.throws(() => P.buildAssetKeys({ audio_path: '/x/a.wav' }), /INVALID_WORK_ID/);
  });
});

// ── 2. S3 布局 ───────────────────────────────────────────────────────────────
group('s3Layout', () => {
  ok('键以 work_id 为根命名空间', () => {
    const L = P.s3Layout('5764AEF3-631E-434D-87A3-C6C6F208618A');
    assert.equal(L.root, 'works/5764aef3-631e-434d-87a3-c6c6f208618a');
    assert.equal(L.audio, 'works/5764aef3-631e-434d-87a3-c6c6f208618a/audio.m4a');
  });
  ok('可声明可选资产扩展名', () => {
    const L = P.s3Layout(f, { coverExt: '.jpg', lyricsExt: '.lrc' });
    assert.equal(L.cover.endsWith('/cover.jpg'), true);
    assert.equal(L.lyrics.endsWith('/lyrics.lrc'), true);
  });
});

// ── 3. 指纹 + 幂等 ──────────────────────────────────────────────────────────
group('fingerprint + uploadNeeded', () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-fp-'));
  const a = path.join(tmp, 'a.wav');
  const b = path.join(tmp, 'b.wav');
  fs.writeFileSync(a, Buffer.from('hello moodify'));
  fs.writeFileSync(b, Buffer.from('hello moodify'));  // 同字节
  fs.writeFileSync(b + '.diff', Buffer.from('different'));

  ok('同字节不同路径指纹相等', () => {
    const fa = P.fingerprintFile(a);
    const fb = P.fingerprintFile(b);
    assert.equal(fa.sha256, fb.sha256);
    assert.equal(fa.size, fb.size);
  });
  ok('不同字节指纹不同', () => {
    const fa = P.fingerprintFile(a);
    const fd = P.fingerprintFile(b + '.diff');
    assert.notEqual(fa.sha256, fd.sha256);
  });
  ok('文件不存在返回 null', () => {
    assert.equal(P.fingerprintFile(path.join(tmp, 'nope.wav')), null);
  });

  ok('首次发布（FIRST_TIME）', () => {
    const cur = P.fingerprintFile(a);
    const r = P.uploadNeeded(null, 'audio', cur);
    assert.equal(r.needed, true);
    assert.equal(r.reason, 'NO_REMOTE_RECORD');
  });
  ok('内容未变跳过（UNCHANGED）', () => {
    const cur = P.fingerprintFile(a);
    const r = P.uploadNeeded({ audio: cur }, 'audio', cur);
    assert.equal(r.needed, false);
    assert.equal(r.reason, 'UNCHANGED');
  });
  ok('内容变了需要重传（CHANGED）', () => {
    const before = P.fingerprintFile(a);
    fs.writeFileSync(a, Buffer.from('new master'));
    const after = P.fingerprintFile(a);
    const r = P.uploadNeeded({ audio: before }, 'audio', after);
    assert.equal(r.needed, true);
    assert.equal(r.reason, 'CHANGED');
  });
  ok('本地文件缺失则不传（NO_LOCAL_FILE）', () => {
    const r = P.uploadNeeded({ audio: P.fingerprintFile(a) }, 'audio', null);
    assert.equal(r.needed, false);
    assert.equal(r.reason, 'NO_LOCAL_FILE');
  });

  fs.rmSync(tmp, { recursive: true, force: true });
});

// ── 4. manifest 应用 + 乐观锁 ───────────────────────────────────────────────
group('buildTrack + applyTrack', () => {
  const work = { work_id: f, title: 'T', creator: 'R', audio_path: '/x/a.wav' };
  const keys = P.buildAssetKeys(work);
  const t = P.buildTrack(work, keys, 173480);

  ok('buildTrack 含全部资产键与时长', () => {
    assert.equal(t.id, 'owner-' + f);
    assert.equal(t.title, 'T');
    assert.equal(t.duration_ms, 173480);
    assert.equal(t.version.audio_asset_key, keys.audio);
  });
  ok('buildTrack 时长非法→null', () => {
    const t2 = P.buildTrack(work, keys, 0);
    assert.equal(t2.duration_ms, null);
  });

  const m0 = { tracks: [{ id: 'x', title: 'old' }] };
  const m1 = P.applyTrack(m0, t);
  ok('applyTrack 把新 track 放到最前', () => {
    assert.equal(m1.tracks.length, 2);
    assert.equal(m1.tracks[0].id, t.id);
    assert.equal(m1.tracks[1].id, 'x');
  });
  ok('applyTrack 是不可变更新', () => {
    assert.notEqual(m0, m1);
    assert.equal(m0.tracks.length, 1);
  });
  const m2 = P.applyTrack(m1, { ...t, title: 'T-v2' });
  ok('同 id 重复发布 = 替换而非重复', () => {
    assert.equal(m2.tracks.length, 2);
    assert.equal(m2.tracks[0].title, 'T-v2');
  });
  const m3 = P.removeTrack(m2, t.id);
  ok('removeTrack 只删目标', () => {
    assert.equal(m3.tracks.length, 1);
    assert.equal(m3.tracks[0].id, 'x');
  });
  ok('revisionOf 对缺字段、字符串、null 都安全', () => {
    assert.equal(P.revisionOf({}), 0);
    assert.equal(P.revisionOf({ revision: 5 }), 5);
    assert.equal(P.revisionOf({ revision: '5' }), 5);
    assert.equal(P.revisionOf(null), 0);
  });
});

// ── 5. CAS 脚本 ─────────────────────────────────────────────────────────────
group('casScript', () => {
  ok('脚本包含 revision 比对与 tempfile+os.replace', () => {
    const s = P.casScript('/p/m.json', { tracks: [] }, 3);
    assert.match(s, /expected/);
    assert.match(s, /sys\.exit\(3\)/);                    // 冲突退出码
    assert.match(s, /tempfile\.mkstemp/);
    assert.match(s, /os\.replace/);
    assert.match(s, /json\.dump/);
  });
  ok('expected 由 argv[2] 决定：脚本正文与具体值无关', () => {
    const a = P.casScript('/p/m.json', { tracks: [] }, 3);
    const b = P.casScript('/p/m.json', { tracks: [] }, null);
    // 除 payload（stdin 传入）外，正文应完全一致 —— 值不参与脚本生成
    const strip = (s) => s;
    assert.equal(strip(a), strip(b));
  });
  ok('payload 从 argv[3] 的文件读，不走 stdin', () => {
    // heredoc 送脚本时 stdin 已被占用，payload 必须走文件。
    const s = P.casScript('/p/m.json', { tracks: [] }, 0);
    assert.match(s, /open\(sys\.argv\[3\]/);
    assert.equal(/sys\.stdin\.read/.test(s), false);
  });
});

// ── 6. 进度百分比 ───────────────────────────────────────────────────────────
group('stagePercent', () => {
  ok('第一阶段 0% → 50%', () => {
    assert.equal(P.stagePercent('prepare', 0), 0);
    assert.equal(P.stagePercent('prepare', 0.5), Math.round(0.5 * 100 / 7));
  });
  ok('最后阶段 100%', () => {
    assert.equal(P.stagePercent('refresh', 1), 100);
  });
  ok('非法阶段 id 安全回退', () => {
    assert.equal(P.stagePercent('nope'), 0);
  });
});

console.log('\npublish: ok');
