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

// 必须是**绝对路径**：PowerShell 的 `-File` 拿到相对路径时会把它当成命令名，
// 报 `CommandNotFoundException: release-guard.ps1` —— 而 spawnSync 的退出码非 0
// 看起来又像「守卫拒绝了」，于是每一格的失败原因都会被误读。
const GUARD = path.resolve(__dirname, 'release-guard.ps1');
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
    '-ReleaseDir', path.resolve(dir)];
  if (signingEnabled) args.push('-SigningEnabled');
  return spawnSync(POWERSHELL, args, { encoding: 'utf8' });
}

/**
 * 找到可用的 PowerShell。
 *
 * 为什么需要这一步：Windows 上是 `powershell`（5.1，随系统），
 * Linux/macOS 上是 `pwsh`（PowerShell 7）。若直接 spawn `powershell`，
 * 在 Linux 上会得到 ENOENT —— 而 spawnSync 的 ENOENT 表现为 `status === null`
 * 且 stdout 为 undefined，于是**每一条断言都会以误导性的方式失败**
 * （"The string argument must be of type string. Received undefined"），
 * 看起来像守卫坏了，实际是测试环境的可执行文件名字不对。
 * 这正是 CI 抓到的那个问题。
 */
function findPowerShell() {
  const candidates = process.platform === 'win32'
    ? ['powershell', 'pwsh']
    : ['pwsh', 'powershell'];
  for (const exe of candidates) {
    const res = spawnSync(exe, ['-NoProfile', '-Command', '$PSVersionTable.PSVersion.Major'],
      { encoding: 'utf8' });
    if (!res.error && res.status === 0) return exe;
  }
  return null;
}

const POWERSHELL = findPowerShell();

/**
 * 确认守卫**真的运行了**，返回它的退出码。
 *
 * 这一步不能省：spawnSync 在可执行文件缺失时返回 `status: null`、stdout 为 undefined。
 * 若测试直接断言 `status !== 0`，那么「根本没跑起来」会被当成「守卫正确地拒绝了」——
 * 一个**假通过**。所以先把「跑起来了」和「它判了什么」分开：
 * 跑不起来是测试环境错误（抛异常），跑起来了才看退出码。
 */
function expectRan(res) {
  if (res.error) throw new Error(`guard could not be executed: ${res.error.message}`);
  if (res.status === null) {
    throw new Error(`guard produced no exit status (signal=${res.signal})\n${res.stdout || ''}`);
  }
  // 把 PowerShell 自己的「找不到脚本 / 解析失败」和「守卫判定了」分开。
  // 前者也会给出非 0 退出码，若不区分就会被读成「守卫正确地挡住了」——
  // 一个假通过。CI 上正是这样暴露了 -File 收到相对路径的问题。
  const out = `${res.stdout || ''}\n${res.stderr || ''}`;
  if (/CommandNotFoundException|Cannot find (path|the file)|ParserError|is not recognized/.test(out)) {
    throw new Error(`PowerShell could not run the guard (this is a test-harness error, `
      + `not a guard verdict):\n${out}`);
  }
  return res.status;
}

console.log('moodify-desktop release guard (trust chain §18)');

if (!POWERSHELL) {
  // 如实跳过，不假装通过。守卫本身在 windows-latest 上由发布流程强制执行，
  // 这里缺的只是**跑测试用的解释器**。
  console.log('\n  SKIP  no PowerShell available on this runner (tests are skipped, not passed)');
  console.log('        the guard is enforced for real in .github/workflows/desktop-release.yml');
  process.exit(0);
}
console.log(`  using: ${POWERSHELL}\n`);

// ── 必须通过的情况 ──────────────────────────────────────────────────────────────
console.log('\n1. 合法产物集：必须通过');

check('未签名 + 校验和吻合 + 清单一致 → 通过（并 warn 未签名）', () => {
  const dir = makeRelease(tmp(), { code_signed: false });
  const res = runGuard(dir, false);
  assert.strictEqual(expectRan(res), 0, `expected pass\n${res.stdout}\n${res.stderr}`);
  assert.match(res.stdout, /release guard passed/);
  assert.match(res.stdout, /Unsigned release/, 'must warn that it is unsigned');
});

check('已签名 + 校验和吻合 + 清单齐全 → 通过（签名启用）', () => {
  const dir = makeRelease(tmp(), {
    code_signed: true, signature_valid: true, signature_timestamped: true,
    signer_subject: 'CN=SignPath Foundation',
  });
  const res = runGuard(dir, true);
  assert.strictEqual(expectRan(res), 0, `expected pass\n${res.stdout}\n${res.stderr}`);
  assert.match(res.stdout, /signed release confirmed/);
});

// ── 必须挡住的情况 ──────────────────────────────────────────────────────────────
console.log('\n2. 不可发布的产物集：必须全部失败');

check('校验和是上一版算的（stale）→ 失败', () => {
  const dir = makeRelease(tmp(), { sumsAllSame: true });
  const res = runGuard(dir, false);
  assert.notStrictEqual(expectRan(res), 0, 'stale checksums must be rejected');
  assert.match(res.stdout, /sha256 mismatch/);
});

check('SHA256SUMS 条目数少于产物数 → 失败', () => {
  const dir = makeRelease(tmp(), { sumsCountMismatch: true });
  const res = runGuard(dir, false);
  assert.notStrictEqual(expectRan(res), 0, 'a partially checksummed set must be rejected');
  assert.match(res.stdout, /lists 1 entr/);
});

check('SHA256SUMS 混入非二进制条目 → 失败', () => {
  const dir = makeRelease(tmp(), { sumsExtraEntry: true });
  const res = runGuard(dir, false);
  assert.notStrictEqual(expectRan(res), 0, 'checksums must cover exactly the published binaries');
});

check('没有 SHA256SUMS.txt → 失败', () => {
  const dir = makeRelease(tmp(), { sums: false });
  const res = runGuard(dir, false);
  assert.notStrictEqual(expectRan(res), 0);
  assert.match(res.stdout, /SHA256SUMS\.txt is missing/);
});

check('没有 RELEASE_MANIFEST.json → 失败', () => {
  const dir = makeRelease(tmp(), { manifest: false });
  const res = runGuard(dir, false);
  assert.notStrictEqual(expectRan(res), 0);
  assert.match(res.stdout, /RELEASE_MANIFEST\.json is missing/);
});

check('发布目录里没有可执行产物 → 失败', () => {
  const dir = tmp();
  fs.mkdirSync(dir, { recursive: true });
  const res = runGuard(dir, false);
  assert.notStrictEqual(expectRan(res), 0);
  assert.match(res.stdout, /no executable artifacts/);
});

check('发布目录不存在 → 失败', () => {
  const res = runGuard(path.join(os.tmpdir(), 'moodify-rg-does-not-exist'), false);
  assert.notStrictEqual(expectRan(res), 0);
  assert.match(res.stdout, /release directory not found/);
});

console.log('\n3. 未签名产物不得以官方身份发布（缺陷 A 的回归测试）');

check('签名已启用但清单 code_signed=false → 失败（这是最关键的一条）', () => {
  const dir = makeRelease(tmp(), { code_signed: false });
  const res = runGuard(dir, true);
  assert.notStrictEqual(expectRan(res), 0,
    'an unsigned set must never pass while signing is enabled');
  assert.match(res.stdout, /code_signed=false/);
  assert.match(res.stdout, /Refusing to publish an unsigned build/);
});

check('签名已启用但签名无效 → 失败', () => {
  const dir = makeRelease(tmp(), {
    code_signed: true, signature_valid: false, signature_timestamped: true,
  });
  const res = runGuard(dir, true);
  assert.notStrictEqual(expectRan(res), 0);
  assert.match(res.stdout, /signature_valid=false/);
});

check('签名已启用但没有时间戳 → 失败（否则证书到期后签名失效）', () => {
  const dir = makeRelease(tmp(), {
    code_signed: true, signature_valid: true, signature_timestamped: false,
  });
  const res = runGuard(dir, true);
  assert.notStrictEqual(expectRan(res), 0);
  assert.match(res.stdout, /unsigned timestamp/);
});

check('同样这个未签名集合，在签名未启用时是允许的（证明严格性来自开关）', () => {
  const dir = makeRelease(tmp(), { code_signed: false });
  assert.strictEqual(expectRan(runGuard(dir, false)), 0);
  assert.notStrictEqual(expectRan(runGuard(dir, true)), 0);
});

// ── cleanup ────────────────────────────────────────────────────────────────────
for (const d of tmpDirs) {
  try { fs.rmSync(d, { recursive: true, force: true }); } catch { /* best effort */ }
}

console.log(`\n${failures ? `${failures} FAILED` : 'all release-guard checks passed'}`);
process.exit(failures ? 1 : 0);
