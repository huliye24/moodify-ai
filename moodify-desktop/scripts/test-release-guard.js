#!/usr/bin/env node
/**
 * 发布守卫的行为测试（MOODIFY_DESKTOP_TRUST_CHAIN_001 §18）。
 *
 * WHY THIS EXISTS
 *   `release-guard.ps1` 是供应链上最后一个不可撤回动作（发布）前面的闸门。
 *   一条「只在真实发布时才第一次执行」的检查等于没有检查——所以这里用**合成的产物集**
 *   把每一种它必须挡住的情况都跑一遍，证明它真的会失败，而不是只是"看起来有判断"。
 *
 * 这些反例都不是假想，每一条都对应一个真实的失败模式：
 *   · 校验和是上一版算的        → 用户 `sha256sum -c` 失败，或更坏：以为没问题
 *   · 只发布了一个产物          → portable 静默丢失
 *   · 签名启用但清单说未签名    → 未签名包以官方身份发出（本任务审计发现的缺陷 A）
 *   · 签名没有时间戳            → 证书到期后用户手里的包变成「签名无效」
 *
 * Run: node scripts/test-release-guard.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const crypto = require('crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const GUARD = path.join(__dirname, 'release-guard.ps1');
const tmpDirs = [];
let failures = 0;

function check(name, fn) {
  try {
    fn();
    console.log(`  ok    ${name}`);
  } catch (err) {
    failures += 1;
    console.error(`  FAIL  ${name}`);
    console.error(`        ${err.message}`);
  }
}

function tmp() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-rg-'));
  tmpDirs.push(dir);
  return dir;
}

const sha256 = (buf) => crypto.createHash('sha256').update(buf).digest('hex');

/**
 * 造一个"看起来像发布目录"的东西。
 * 每个选项都刻意可注入错误——因为我们要测的正是**错误能不能被挡住**。
 */
function makeRelease(dir, opts = {}) {
  fs.mkdirSync(dir, { recursive: true });
  const exes = opts.exes || ['Moodify_Studio_1.0.0_Setup_x64.exe',
    'Moodify_Studio_1.0.0_Portable_x64.exe'];
  const bodies = new Map();
  for (const name of exes) {
    // 内容里带文件名，保证不同产物的指纹不同
    const body = Buffer.from(`fake PE bytes for ${name}\n`);
    bodies.set(name, body);
    fs.writeFileSync(path.join(dir, name), body);
  }

  if (opts.sums !== false) {
    const lines = exes.map((name) => {
      const digest = opts.sumsAllSame
        ? sha256(Buffer.from('stale checksum from a previous build'))
        : sha256(bodies.get(name));
      return `${digest}  ${name}`;
    });
    if (opts.sumsCountMismatch) lines.pop();
    if (opts.sumsExtraEntry) lines.push(`${sha256(Buffer.from('x'))}  SIGNATURE_FACTS.json`);
    fs.writeFileSync(path.join(dir, 'SHA256SUMS.txt'), lines.join('\n') + '\n', 'ascii');
  }

  if (opts.manifest !== false) {
    const manifest = {
      product: 'Moodify Studio',
      version: '1.0.0',
      commit: 'deadbeef',
      code_signed: opts.code_signed === true,
      signature_valid: opts.signature_valid === true,
      signature_timestamped: opts.signature_timestamped === true,
      signer_subject: opts.signer_subject || null,
      artifacts: exes.map((n) => ({ name: n, sha256: sha256(bodies.get(n)) })),
    };
    fs.writeFileSync(path.join(dir, 'RELEASE_MANIFEST.json'),
      JSON.stringify(manifest, null, 2), 'utf8');
  }
  return dir;
}

function runGuard(dir, signingEnabled) {
  const args = ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', GUARD,
    '-ReleaseDir', dir];
  if (signingEnabled) args.push('-SigningEnabled');
  return spawnSync('powershell', args, { encoding: 'utf8' });
}

console.log('moodify-desktop release guard (trust chain §18)');

// ── 必须通过的情况 ──────────────────────────────────────────────────────────────
console.log('\n1. 合法产物集：必须通过');

check('未签名 + 校验和吻合 + 清单一致 → 通过（并 warn 未签名）', () => {
  const dir = makeRelease(tmp(), { code_signed: false });
  const res = runGuard(dir, false);
  assert.strictEqual(res.status, 0, `expected pass\n${res.stdout}\n${res.stderr}`);
  assert.match(res.stdout, /release guard passed/);
  assert.match(res.stdout, /Unsigned release/, 'must warn that it is unsigned');
});

check('已签名 + 校验和吻合 + 清单齐全 → 通过（签名启用）', () => {
  const dir = makeRelease(tmp(), {
    code_signed: true, signature_valid: true, signature_timestamped: true,
    signer_subject: 'CN=SignPath Foundation',
  });
  const res = runGuard(dir, true);
  assert.strictEqual(res.status, 0, `expected pass\n${res.stdout}\n${res.stderr}`);
  assert.match(res.stdout, /signed release confirmed/);
});

// ── 必须挡住的情况 ──────────────────────────────────────────────────────────────
console.log('\n2. 不可发布的产物集：必须全部失败');

check('校验和是上一版算的（stale）→ 失败', () => {
  const dir = makeRelease(tmp(), { sumsAllSame: true });
  const res = runGuard(dir, false);
  assert.notStrictEqual(res.status, 0, 'stale checksums must be rejected');
  assert.match(res.stdout, /sha256 mismatch/);
});

check('SHA256SUMS 条目数少于产物数 → 失败', () => {
  const dir = makeRelease(tmp(), { sumsCountMismatch: true });
  const res = runGuard(dir, false);
  assert.notStrictEqual(res.status, 0, 'a partially checksummed set must be rejected');
  assert.match(res.stdout, /lists 1 entr/);
});

check('SHA256SUMS 混入非二进制条目 → 失败', () => {
  const dir = makeRelease(tmp(), { sumsExtraEntry: true });
  const res = runGuard(dir, false);
  assert.notStrictEqual(res.status, 0, 'checksums must cover exactly the published binaries');
});

check('没有 SHA256SUMS.txt → 失败', () => {
  const dir = makeRelease(tmp(), { sums: false });
  const res = runGuard(dir, false);
  assert.notStrictEqual(res.status, 0);
  assert.match(res.stdout, /SHA256SUMS\.txt is missing/);
});

check('没有 RELEASE_MANIFEST.json → 失败', () => {
  const dir = makeRelease(tmp(), { manifest: false });
  const res = runGuard(dir, false);
  assert.notStrictEqual(res.status, 0);
  assert.match(res.stdout, /RELEASE_MANIFEST\.json is missing/);
});

check('发布目录里没有可执行产物 → 失败', () => {
  const dir = tmp();
  fs.mkdirSync(dir, { recursive: true });
  const res = runGuard(dir, false);
  assert.notStrictEqual(res.status, 0);
  assert.match(res.stdout, /no executable artifacts/);
});

check('发布目录不存在 → 失败', () => {
  const res = runGuard(path.join(os.tmpdir(), 'moodify-rg-does-not-exist'), false);
  assert.notStrictEqual(res.status, 0);
  assert.match(res.stdout, /release directory not found/);
});

console.log('\n3. 未签名产物不得以官方身份发布（缺陷 A 的回归测试）');

check('签名已启用但清单 code_signed=false → 失败（这是最关键的一条）', () => {
  const dir = makeRelease(tmp(), { code_signed: false });
  const res = runGuard(dir, true);
  assert.notStrictEqual(res.status, 0,
    'an unsigned set must never pass while signing is enabled');
  assert.match(res.stdout, /code_signed=false/);
  assert.match(res.stdout, /Refusing to publish an unsigned build/);
});

check('签名已启用但签名无效 → 失败', () => {
  const dir = makeRelease(tmp(), {
    code_signed: true, signature_valid: false, signature_timestamped: true,
  });
  const res = runGuard(dir, true);
  assert.notStrictEqual(res.status, 0);
  assert.match(res.stdout, /signature_valid=false/);
});

check('签名已启用但没有时间戳 → 失败（否则证书到期后签名失效）', () => {
  const dir = makeRelease(tmp(), {
    code_signed: true, signature_valid: true, signature_timestamped: false,
  });
  const res = runGuard(dir, true);
  assert.notStrictEqual(res.status, 0);
  assert.match(res.stdout, /unsigned timestamp/);
});

check('同样这个未签名集合，在签名未启用时是允许的（证明严格性来自开关）', () => {
  const dir = makeRelease(tmp(), { code_signed: false });
  assert.strictEqual(runGuard(dir, false).status, 0);
  assert.notStrictEqual(runGuard(dir, true).status, 0);
});

// ── cleanup ────────────────────────────────────────────────────────────────────
for (const d of tmpDirs) {
  try { fs.rmSync(d, { recursive: true, force: true }); } catch { /* best effort */ }
}

console.log(`\n${failures ? `${failures} FAILED` : 'all release-guard checks passed'}`);
process.exit(failures ? 1 : 0);
