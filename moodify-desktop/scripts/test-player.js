#!/usr/bin/env node
/**
 * Headless tests for the work player's lyric timeline（作品试音 · 滚动歌词）.
 *
 * WHAT THIS PROVES, AND WHY EACH ONE MATTERS
 *
 *   1 basic parse      [mm:ss.xx] is turned into real seconds. A lyric that is
 *                      off by a factor of 100 still "works" on screen and is wrong
 *                      in the ear — this pins the unit conversion.
 *   2 multi-stamp      one line carrying several stamps expands into several
 *                      entries. Refrains are written once and reused; collapsing
 *                      them would drop every repeat but the first.
 *   3 shape variants   [mm:ss] and [mm:ss:xx] are both accepted. LRC in the wild
 *                      disagrees on the separator; the player must not care.
 *   4 metadata         [ti]/[ar]/[al]/[by] rows never enter the timeline. Title
 *                      rows are not lyrics and must not be highlighted at 0:00.
 *   5 offset           [offset:-250] shifts the whole sheet. Some files are
 *                      authored against a different master; the tag is the only
 *                      contract for that.
 *   6 ordering         out-of-order input yields an ascending timeline. Scrolling
 *                      assumes monotone time; unsorted input makes it jump back.
 *   7 untimed         plain text is NOT an error: it returns timed:false and keeps
 *                      its original order, so the UI degrades to a static sheet
 *                      instead of showing an empty pane or a lie.
 *   8 active line      the highlighted row at time t is the last one at or before
 *                      t, and -1 before the song's first lyric. Highlighting row 0
 *                      during the intro would be visibly wrong.
 *   9 no stamp residue timestamps are stripped from the displayed text.
 *
 * The parser is DOM-free on purpose, so all of this runs in plain Node.
 *
 * Run: node scripts/test-player.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const path = require('path');

const lyrics = require(path.join(__dirname, '..', 'renderer', 'lyrics.js'));

let passed = 0;
const failures = [];
async function check(label, fn) {
  try { await fn(); passed += 1; console.log('  ok   ' + label); }
  catch (err) { failures.push(label + ': ' + err.message); console.log('  FAIL ' + label + ' — ' + err.message); }
}

// ——— fixtures ————————————————————————————————————————————————————————————

const LRC = [
  '[ti:测试曲目]',
  '[ar:荣景文川]',
  '[al:内部作品集]',
  '[by:Moodify]',
  '[00:00.00]',
  '[00:12.50]第一行歌词',
  '[00:20.00][01:05.00]副歌重复两次',
  '[01:00]整秒，没有厘秒',
  '[01:30:75]冒号分隔厘秒',
].join('\n');

main();

async function main() {
  console.log('work player lyrics (parse · timeline · active line)');

  console.log('\n1. a normal LRC sheet becomes real seconds');

  await check('[00:12.50] 是 12.5 秒，不是 1250 秒也不是 0.125 秒', () => {
    const result = lyrics.parseLrc('[00:12.50]第一行歌词');
    assert.strictEqual(result.timed, true);
    assert.strictEqual(result.lines.length, 1);
    assert.strictEqual(result.lines[0].time, 12.5);
    assert.strictEqual(result.lines[0].text, '第一行歌词');
  });

  await check('厘秒位数不同也归一：.5 = 500ms，.05 = 50ms', () => {
    const result = lyrics.parseLrc('[00:01.5]A\n[00:02.05]B');
    assert.strictEqual(result.lines[0].time, 1.5);
    assert.strictEqual(result.lines[1].time, 2.05);
  });

  console.log('\n2. one line, several stamps');

  await check('[00:20.00][01:05.00]副歌 展开成两条，文案都在', () => {
    const result = lyrics.parseLrc('[00:20.00][01:05.00]副歌重复两次');
    assert.strictEqual(result.lines.length, 2);
    assert.deepStrictEqual(result.lines.map((l) => l.time), [20, 65]);
    assert.deepStrictEqual(result.lines.map((l) => l.text), ['副歌重复两次', '副歌重复两次']);
  });

  console.log('\n3. separator variants seen in the wild');

  await check('[01:00] 缺厘秒也认', () => {
    const result = lyrics.parseLrc('[01:00]整秒');
    assert.strictEqual(result.lines[0].time, 60);
  });

  await check('[01:30:75] 冒号分厘秒也认', () => {
    const result = lyrics.parseLrc('[01:30:75]冒号分隔');
    assert.strictEqual(result.lines[0].time, 90.75);
  });

  console.log('\n4. metadata rows are not lyrics');

  await check('ti/ar/al/by 四行全部不进时间轴', () => {
    const result = lyrics.parseLrc('[ti:T]\n[ar:A]\n[al:L]\n[by:B]\n[00:05.00]真歌词');
    assert.strictEqual(result.lines.length, 1);
    assert.strictEqual(result.lines[0].text, '真歌词');
  });

  await check('整张表只含元数据时，没有一行被当成歌词', () => {
    const result = lyrics.parseLrc('[ti:T]\n[ar:A]');
    assert.strictEqual(result.lines.length, 0);
    assert.strictEqual(result.timed, false);
  });

  console.log('\n5. [offset] shifts the whole sheet');

  await check('[offset:-250] 整体前移 0.25 秒', () => {
    const result = lyrics.parseLrc('[offset:-250]\n[00:10.00]歌词');
    assert.strictEqual(result.lines[0].time, 9.75);
    assert.strictEqual(result.offset, -250);
  });

  await check('偏移把首行推到 0 之前时夹到 0，不出现负时间', () => {
    const result = lyrics.parseLrc('[offset:-20000]\n[00:10.00]歌词');
    assert.strictEqual(result.lines[0].time, 0);
  });

  console.log('\n6. ordering and integrity of the full sheet');

  await check('乱序输入被排成升序（滚动不能往回跳）', () => {
    const result = lyrics.parseLrc('[01:30:75]C\n[00:12.50]A\n[01:00]B');
    const times = result.lines.map((l) => l.time);
    assert.deepStrictEqual(times, [12.5, 60, 90.75]);
  });

  await check('整表解析：元数据被丢、空行保留为间隔、共 6 行', () => {
    const result = lyrics.parseLrc(LRC);
    assert.strictEqual(result.timed, true);
    assert.strictEqual(result.lines.length, 6);
    assert.deepStrictEqual(result.lines[0], { time: 0, text: '' });
    assert.strictEqual(result.lines[1].text, '第一行歌词');
  });

  await check('CRLF 结尾的文件和 LF 解析结果一致', () => {
    const crlf = lyrics.parseLrc(LRC.replace(/\n/g, '\r\n'));
    const lf = lyrics.parseLrc(LRC);
    assert.deepStrictEqual(crlf.lines, lf.lines);
  });

  console.log('\n7. plain text degrades, it does not lie');

  await check('无时间戳的纯文本返回 timed:false，且不打乱原顺序', () => {
    const result = lyrics.parseLrc('第一段\n第二段\n第三段');
    assert.strictEqual(result.timed, false);
    assert.deepStrictEqual(result.lines.map((l) => l.text), ['第一段', '第二段', '第三段']);
  });

  await check('空输入不抛错', () => {
    const result = lyrics.parseLrc('');
    assert.strictEqual(result.lines.length, 0);
    assert.strictEqual(result.timed, false);
  });

  await check('null / undefined 也不抛错（歌没填歌词是常态）', () => {
    assert.strictEqual(lyrics.parseLrc(null).lines.length, 0);
    assert.strictEqual(lyrics.parseLrc(undefined).lines.length, 0);
  });

  console.log('\n8. which row is lit at time t');

  await check('前奏期间（-1）不高亮任何一行', () => {
    const result = lyrics.parseLrc(LRC);
    assert.strictEqual(lyrics.activeLineIndex(result.lines, 0), 0, '本表首行就在 0 秒');
    const late = lyrics.parseLrc('[00:12.50]A\n[00:20.00]B');
    assert.strictEqual(lyrics.activeLineIndex(late.lines, 3), -1);
  });

  await check('恰好等于时间戳时点亮该行，不是前一行', () => {
    const result = lyrics.parseLrc('[00:12.50]A\n[00:20.00]B');
    assert.strictEqual(lyrics.activeLineIndex(result.lines, 20), 1);
  });

  await check('两句之间是前一句在亮', () => {
    const result = lyrics.parseLrc('[00:12.50]A\n[00:20.00]B');
    assert.strictEqual(lyrics.activeLineIndex(result.lines, 18), 0);
  });

  await check('超过最后一句后停在最后一句，不越界', () => {
    const result = lyrics.parseLrc('[00:12.50]A\n[00:20.00]B');
    assert.strictEqual(lyrics.activeLineIndex(result.lines, 9999), 1);
  });

  await check('空时间轴与非法时间都返回 -1，不崩', () => {
    assert.strictEqual(lyrics.activeLineIndex([], 5), -1);
    assert.strictEqual(lyrics.activeLineIndex(null, 5), -1);
    assert.strictEqual(lyrics.activeLineIndex([{ time: 1 }], NaN), -1);
  });

  console.log('\n9. the stamp itself is not shown');

  await check('显示文本里不残留 [mm:ss.xx]', () => {
    const result = lyrics.parseLrc('[00:20.00][01:05.00]副歌');
    for (const line of result.lines) assert.ok(!line.text.includes('['), line.text);
  });

  // ——— verdict ——————————————————————————————————————————————————————————

  console.log('');
  if (failures.length) {
    console.log(failures.length + ' FAILED');
    for (const line of failures) console.log('  - ' + line);
    process.exit(1);
  }
  console.log(passed + ' passed, 0 failed');
}
