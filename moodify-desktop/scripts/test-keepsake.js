#!/usr/bin/env node
/**
 * Headless test for the keepsake store — the **non-authoritative** completion record
 * (Phase 2.3 `docs/plan/2026-10-04_DESKTOP_PHASE2_3_FINISHING_POLISH.md` §6/§13.2).
 *
 * What this proves, and why each one matters
 *
 *   1 boundaries    280 code points, at most 4 lines — counted by code point, so 中文 and
 *                   accented French count as one character each (truncating them silently
 *                   would eat the user's text, so over-limit input is *refused*)
 *   2 atomicity     tmp file + rename: a failure leaves either the old record or the new one,
 *                   never half a JSON document
 *   3 confinement   the only path ever written is `<case>/studio/keepsake.json`
 *   4 projection    `selected` follows the effective decision; the inscription survives a
 *                   change of selection and a *lost* decision (the text is not collateral)
 *   5 resilience    damaged JSON never throws and never blocks the sound flow
 *   6 determinism   the waveform imprint is a pure function: same peaks -> same numbers,
 *                   fixed bucket count, no randomness and no clock
 *   7 card privacy  the card model carries no case_id / pair_id / hash / absolute path, and
 *                   file names are sanitised for Windows and POSIX
 *
 * Run: node scripts/test-keepsake.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');

const keepsake = require(path.join(__dirname, '..', 'src', 'keepsake'));

let passed = 0;
const failures = [];
async function check(label, fn) {
  try { await fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-keepsake-test-'));
let seq = 0;
function makeCase() {
  const dir = path.join(tmpRoot, `case_${String(++seq).padStart(4, '0')}`);
  fs.mkdirSync(path.join(dir, 'studio'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'case.json'), JSON.stringify({ case_id: path.basename(dir) }));
  return dir;
}

(async () => {
  console.log('keepsake (Phase 2.3)\n');

  // ── 1. boundaries ─────────────────────────────────────────────────────────────
  console.log('1. inscription boundaries');
  await check('280 个中文字符算 280，不是 840 个字节', () => {
    const text = '花'.repeat(280);
    assert.strictEqual(keepsake.countChars(text), 280);
    assert.strictEqual(keepsake.validateInscription(text).ok, true);
    const tooLong = keepsake.validateInscription('花'.repeat(281));
    assert.strictEqual(tooLong.ok, false);
    assert.strictEqual(tooLong.reason, 'INSCRIPTION_TOO_LONG');
  });
  await check('重音字符与组合字符按码位计数（不按字节、不按 UTF-16 单元）', () => {
    const text = 'é'.repeat(280);            // é as one code point
    assert.strictEqual(keepsake.countChars(text), 280);
    assert.strictEqual(keepsake.validateInscription(text).ok, true);
    assert.strictEqual(keepsake.validateInscription('😀'.repeat(281)).ok, false);
    assert.strictEqual(keepsake.countChars('😀'), 1, 'a non-BMP character is one code point');
  });
  await check('最多 4 行，超过就拒绝（不悄悄丢掉换行后的内容）', () => {
    assert.strictEqual(keepsake.validateInscription('a\nb\nc\nd').ok, true);
    const five = keepsake.validateInscription('a\nb\nc\nd\ne');
    assert.strictEqual(five.ok, false);
    assert.strictEqual(five.reason, 'INSCRIPTION_TOO_MANY_LINES');
  });
  await check('回车换行被归一化成 \\n', () => {
    assert.strictEqual(keepsake.validateInscription('a\r\nb').text, 'a\nb');
  });

  // ── 2/3. atomic write + confinement ───────────────────────────────────────────
  console.log('\n2. writing (atomic, confined)');
  await check('写在 <case>/studio/keepsake.json，别处不碰', () => {
    const dir = makeCase();
    const res = keepsake.writeKeepsake(dir, { selected: 'A', completed_at: '2026-10-04T10:00:00Z' });
    assert.strictEqual(res.ok, true, res.reason);
    assert.strictEqual(fs.existsSync(path.join(dir, 'studio', 'keepsake.json')), true);
    assert.deepStrictEqual(fs.readdirSync(path.join(dir, 'studio')).sort(), ['keepsake.json']);
  });
  await check('原子：写完不留临时文件，失败也不留半截', () => {
    const dir = makeCase();
    keepsake.writeKeepsake(dir, { selected: 'A' });
    assert.deepStrictEqual(
      fs.readdirSync(path.join(dir, 'studio')).filter((n) => n.includes('.tmp')), []);
    // 让写入失败：studio 变成文件 → mkdir 抛错，调用方拿到 reason 而不是异常
    const broken = makeCase();
    fs.rmSync(path.join(broken, 'studio'), { recursive: true, force: true });
    fs.writeFileSync(path.join(broken, 'studio'), 'not a directory');
    const res = keepsake.writeKeepsake(broken, { selected: 'A' });
    assert.strictEqual(res.ok, false);
    assert.strictEqual(res.reason, 'KEEPSAKE_WRITE_FAILED');
  });
  await check('写入前后 schema 与 updated_at 始终正确', () => {
    const dir = makeCase();
    const res = keepsake.writeKeepsake(dir, { selected: 'B', completed_at: '2026-10-04T10:00:00Z' });
    assert.strictEqual(res.keepsake.schema, keepsake.SCHEMA);
    assert.ok(res.keepsake.updated_at);
    const back = keepsake.readKeepsake(dir);
    assert.strictEqual(back.keepsake.selected, 'B');
    assert.strictEqual(back.keepsake.completed_at, '2026-10-04T10:00:00Z');
  });
  await check('拒绝非法 selected 与非法 imprint', () => {
    const dir = makeCase();
    assert.strictEqual(keepsake.writeKeepsake(dir, { selected: 'C' }).reason, 'BAD_SELECTION');
    assert.strictEqual(keepsake.writeKeepsake(dir, { imprint: 'x' }).reason, 'BAD_IMPRINT');
    assert.strictEqual(keepsake.readKeepsake(dir).keepsake, null, 'nothing was written');
  });
  await check('不保存音频字节或图片 base64：写入内容只有小字段与固定桶数', () => {
    const dir = makeCase();
    const imprint = keepsake.normalizeImprint([0.5, 1, 0.25]);
    keepsake.writeKeepsake(dir, { selected: 'A', imprint, inscription: '一句话' });
    const raw = fs.readFileSync(path.join(dir, 'studio', 'keepsake.json'), 'utf8');
    assert.ok(raw.length < 8 * 1024, `keepsake must stay tiny, got ${raw.length} bytes`);
    assert.ok(!/base64|data:image/i.test(raw));
    const parsed = JSON.parse(raw);
    assert.strictEqual(parsed.imprint.length, keepsake.IMPRINT_BUCKETS);
  });

  // ── 4. projection semantics ───────────────────────────────────────────────────
  console.log('\n4. projection (selection follows the decision, text survives)');
  await check('decision 改变 → selected 更新，文字保留', () => {
    const dir = makeCase();
    keepsake.writeKeepsake(dir, { selected: 'A', inscription: '写给这首歌' });
    const next = keepsake.writeKeepsake(dir, { selected: 'B' });
    assert.strictEqual(next.keepsake.selected, 'B');
    assert.strictEqual(next.keepsake.inscription, '写给这首歌');
  });
  await check('decision 失效时文字不删（只是完成层不再显示）', () => {
    const dir = makeCase();
    keepsake.writeKeepsake(dir, { selected: 'A', inscription: '留着' });
    const cleared = keepsake.writeKeepsake(dir, { selected: null, completed_at: null });
    assert.strictEqual(cleared.ok, true);
    assert.strictEqual(cleared.keepsake.selected, null);
    assert.strictEqual(cleared.keepsake.inscription, '留着', 'the text is not collateral damage');
  });
  await check('清空文字是普通编辑（空串即可，不需要任何确认流程）', () => {
    const dir = makeCase();
    keepsake.writeKeepsake(dir, { selected: 'A', inscription: '先写点什么' });
    const cleared = keepsake.writeKeepsake(dir, { inscription: '' });
    assert.strictEqual(cleared.keepsake.inscription, '');
  });

  // ── 5. resilience ─────────────────────────────────────────────────────────────
  console.log('\n5. resilience');
  await check('损坏的 JSON 不抛、不阻断，只报告可诊断的原因', () => {
    const dir = makeCase();
    fs.writeFileSync(path.join(dir, 'studio', 'keepsake.json'), '{ this is not json');
    const res = keepsake.readKeepsake(dir);
    assert.strictEqual(res.ok, true);
    assert.strictEqual(res.keepsake, null);
    assert.strictEqual(res.error, 'KEEPSAKE_CORRUPT_JSON');
    // 而且仍然可以覆写成一个好的记录
    assert.strictEqual(keepsake.writeKeepsake(dir, { selected: 'B' }).ok, true);
    assert.strictEqual(keepsake.readKeepsake(dir).keepsake.selected, 'B');
  });
  await check('schema 不符时视为没有留存内容（不猜旧格式）', () => {
    const dir = makeCase();
    fs.writeFileSync(path.join(dir, 'studio', 'keepsake.json'),
      JSON.stringify({ schema: 'something/else', inscription: 'x' }));
    const res = keepsake.readKeepsake(dir);
    assert.strictEqual(res.keepsake, null);
    assert.strictEqual(res.error, 'KEEPSAKE_SCHEMA_MISMATCH');
  });
  await check('重启后完整恢复（读回同一份记录）', () => {
    const dir = makeCase();
    const imprint = keepsake.normalizeImprint(Array.from({ length: 2000 }, (_, i) => Math.sin(i / 7)));
    keepsake.writeKeepsake(dir, { selected: 'ORIGINAL', inscription: 'é中文😀', imprint,
      completed_at: '2026-10-04T12:34:56Z', decision_request_id: 'keep:x:ORIGINAL:1' });
    const back = keepsake.readKeepsake(dir).keepsake;
    assert.strictEqual(back.selected, 'ORIGINAL');
    assert.strictEqual(back.inscription, 'é中文😀');
    assert.deepStrictEqual(back.imprint, imprint);
    assert.strictEqual(back.decision_request_id, 'keep:x:ORIGINAL:1');
  });

  // ── 6. waveform imprint determinism ───────────────────────────────────────────
  console.log('\n6. waveform imprint');
  await check('同一段音频 → 同一串数字（纯函数，无随机、无时钟）', () => {
    const peaks = Array.from({ length: 48000 }, (_, i) => Math.abs(Math.sin(i / 300)) * 0.9);
    const a = keepsake.normalizeImprint(peaks);
    const b = keepsake.normalizeImprint(peaks);
    assert.deepStrictEqual(a, b);
    assert.strictEqual(a.length, keepsake.IMPRINT_BUCKETS);
    const src = fs.readFileSync(path.join(__dirname, '..', 'src', 'keepsake.js'), 'utf8');
    const fn = /function normalizeImprint[\s\S]*?\n\}/.exec(src)[0];
    assert.ok(!/Math\.random|Date\.now|new Date/.test(fn), 'no randomness, no clock');
  });
  await check('形状与音频内容相关：不同峰值得到不同印记', () => {
    const a = keepsake.normalizeImprint([0.1, 0.2, 0.3, 0.4]);
    const b = keepsake.normalizeImprint([0.9, 0.8, 0.7, 0.6]);
    assert.notDeepStrictEqual(a, b);
  });
  await check('取值被限幅到 0..1 且四舍五入到固定小数位', () => {
    const out = keepsake.normalizeImprint([-3, 0.123456, 5]);
    for (const v of out) assert.ok(v >= 0 && v <= 1, `${v} out of range`);
    for (const v of out) assert.strictEqual(v, Math.round(v * 1000) / 1000, `${v} not rounded`);
    // 单值输入：每个桶都取到它，于是整条印记就是那个被限幅、被舍入的值
    const single = keepsake.normalizeImprint([0.123456]);
    assert.strictEqual(single.length, keepsake.IMPRINT_BUCKETS);
    assert.ok(single.every((v) => v === 0.123));
  });
  await check('空输入得到空印记（不伪造形状）', () => {
    assert.deepStrictEqual(keepsake.normalizeImprint([]), []);
    assert.deepStrictEqual(keepsake.normalizeImprint(null), []);
  });

  // ── 7. card model privacy ─────────────────────────────────────────────────────
  console.log('\n7. card model (privacy by construction)');
  await check('卡片模型只有标题/版本/日期/文字，没有 id、路径或 hash', () => {
    const model = keepsake.cardModel({
      title: 'Je ne blesserai pas ta fragilité',
      selected: 'A',
      completedAt: '2026-10-04T12:34:56Z',
      inscription: '留给自己',
      tierLabel: '快速完成（仅立体声）',
    });
    assert.deepStrictEqual(Object.keys(model).sort(),
      ['dateLabel', 'inscription', 'selectionLabel', 'title', 'versionLabel']);
    const blob = JSON.stringify(model);
    assert.ok(!/case_|tune_|[0-9a-f]{32}/.test(blob), 'no ids');
    assert.ok(!/[A-Za-z]:\\|\/(Users|home)\//.test(blob), 'no absolute paths');
    assert.ok(!/sha256|[0-9a-f]{64}/.test(blob), 'no hashes');
    assert.strictEqual(model.selectionLabel, 'A（保守）');
    assert.strictEqual(model.dateLabel, '2026.10.04');
  });
  await check('保留原版不伪装成处理版本', () => {
    const model = keepsake.cardModel({ title: 'x', selected: 'ORIGINAL', completedAt: '2026-10-04T00:00:00Z' });
    assert.strictEqual(model.selectionLabel, '保留原版');
    assert.strictEqual(model.versionLabel, '保留原版');
  });
  await check('空标题有兜底，日期缺失不编造', () => {
    const model = keepsake.cardModel({ title: '   ', selected: 'B' });
    assert.strictEqual(model.title, '未命名作品');
    assert.strictEqual(model.dateLabel, '');
  });
  await check('文件名非法字符被安全处理，且以 — Moodify.png 结尾', () => {
    const name = keepsake.defaultCardFileName('a/b\\c:d*e?f"g<h>i|j', 'png');
    assert.ok(!/[\\/:*?"<>|]/.test(name));
    assert.match(name, /— Moodify\.png$/);
    const trailing = keepsake.defaultCardFileName('..name..', 'png');
    assert.ok(!/\.\.name\.\./.test(trailing));
  });

  try { fs.rmSync(tmpRoot, { recursive: true, force: true }); } catch { /* best effort */ }

  console.log(`\n${passed} passed, ${failures.length} failed`);
  if (failures.length) {
    console.log('\nFailures:');
    for (const f of failures) console.log('  - ' + f);
    process.exit(1);
  }
})().catch((err) => {
  console.error('TEST HARNESS ERROR:', err);
  process.exit(1);
});
