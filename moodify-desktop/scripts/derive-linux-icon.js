#!/usr/bin/env node
/**
 * Derive the Linux packaging icon from the authoritative Windows .ico.
 *
 * WHY THIS EXISTS
 *   electron-builder's Linux targets (AppImage, deb) need a square PNG icon.
 *   The only square assets in the tree are unusable: moodify_icon_64.png is
 *   64x64 (electron-builder wants at least 256x256) and moodify_watermark.png
 *   is not the application symbol. The authoritative symbol already ships as
 *   renderer/assets/moodify_icon.ico, so the honest move is to lift the largest
 *   square frame out of it rather than invent a second copy of the brand mark.
 *
 * WHY IT IS NOT COMMITTED
 *   .gitignore line 117 ignores *.png repo-wide; only canonical brand assets get
 *   an explicit `!` exception (Android drawables, website logos). A derived icon
 *   is a generated artifact, so it is produced at build time from a tracked
 *   input instead of being force-added past the ignore rule. Same input bytes
 *   always produce the same output bytes.
 *
 * Run from the moodify-desktop directory:  node scripts/derive-linux-icon.js
 * Exit 0 when the icon is present (written or already current), 1 when the .ico
 * contains no square PNG frame to derive from.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ASSETS = path.join(__dirname, '..', 'renderer', 'assets');
const ICO = path.join(ASSETS, 'moodify_icon.ico');
const OUT = path.join(ASSETS, 'icon.png');

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

/** Walk an ICO/CUR container: returns [{width, height, payload}]. */
function readIcoFrames(buf) {
  const reserved = buf.readUInt16LE(0);
  const kind = buf.readUInt16LE(2);
  const count = buf.readUInt16LE(4);
  if (reserved !== 0 || (kind !== 1 && kind !== 2)) {
    throw new Error('not an ICO container');
  }
  const frames = [];
  for (let i = 0; i < count; i += 1) {
    const off = 6 + i * 16;
    const width = buf.readUInt8(off) || 256;   // 0 encodes 256 in the ICO format
    const height = buf.readUInt8(off + 1) || 256;
    const size = buf.readUInt32LE(off + 8);
    const offset = buf.readUInt32LE(off + 12);
    frames.push({ width, height, payload: buf.subarray(offset, offset + size) });
  }
  return frames;
}

function main() {
  if (!fs.existsSync(ICO)) {
    console.error(`FAIL: authoritative icon not found: ${ICO}`);
    return 1;
  }

  const frames = readIcoFrames(fs.readFileSync(ICO));
  console.log(`ico frames        : ${frames.length}`);
  for (const f of frames) {
    const isPng = f.payload.subarray(0, 8).equals(PNG_MAGIC);
    console.log(`  ${f.width}x${f.height}  ${String(f.payload.length).padStart(7)} bytes  ${isPng ? 'PNG' : 'BMP'}`);
  }

  // Only PNG-backed frames can be lifted verbatim; a BMP-backed one would need a
  // decoder, and mixing formats would make the output non-obvious.
  const square = frames.filter(
    (f) => f.width === f.height && f.payload.subarray(0, 8).equals(PNG_MAGIC),
  );
  console.log(`square PNG frames : ${square.length}`);

  if (square.length === 0) {
    console.error('FAIL: no square PNG-backed frame to derive from');
    return 1;
  }

  const best = square.reduce((a, b) => (b.width > a.width ? b : a));
  const digest = crypto.createHash('sha256').update(best.payload).digest('hex');

  if (fs.existsSync(OUT) && fs.readFileSync(OUT).equals(best.payload)) {
    console.log(`UP TO DATE: ${OUT} (${best.width}x${best.height}, sha256 ${digest.slice(0, 16)}...)`);
    return 0;
  }

  fs.writeFileSync(OUT, best.payload);
  console.log(`WROTE: ${OUT}`);
  console.log(`  size   : ${best.width}x${best.height}`);
  console.log(`  bytes  : ${best.payload.length}`);
  console.log(`  sha256 : ${digest}`);
  return 0;
}

process.exit(main());
