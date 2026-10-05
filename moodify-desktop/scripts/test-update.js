#!/usr/bin/env node
/**
 * 内置更新（updater）的契约测试。
 *
 * WHY THIS EXISTS
 *   内置更新是这个仓库里**唯一能替换用户机器上正在运行的程序**的能力。
 *   它的失败模式不是「功能不好用」，而是：
 *
 *     · 静默下载 → 用户流量被消耗而不自知
 *     · 静默安装 / 退出即安装 → 用户没有同意就被替换了程序
 *     · 「稍后」变成「再也查不了」→ 用户想更新时找不到路
 *     · 「跳过」变成「永远不更新」→ 这条比上一条更隐蔽，也更危险
 *
 *   所以这些不变量必须被测试钉住，而不是靠注释和约定。
 *   本文件只做**静态契约**检查（读源码 / package.json），不需要 Electron、
 *   不需要网络、不需要打包，因此可以在任何 CI 上跑。
 *
 *   「真的能升级成功」属于集成测试，见 docs/session-handover-2026-10-05-studio-updater.md
 *   里记录的差分升级闭环；本文件不假装覆盖它。
 *
 * Run: node scripts/test-update.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const read = (rel) => fs.readFileSync(path.join(ROOT, rel), 'utf8');

const pkg = JSON.parse(read('package.json'));
const mainJs = read(path.join('src', 'main.js'));
const preloadJs = read(path.join('src', 'preload.js'));
const appJs = read(path.join('renderer', 'app.js'));
const html = read(path.join('renderer', 'index.html'));

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

const PRODUCTION_FEED = 'https://rongjingmusic.com/downloads/studio/windows/';

console.log('moodify-desktop in-app updater contract');

// ── 1. 依赖与 feed ─────────────────────────────────────────────────────────────
console.log('\n1. 依赖与更新源');

check('electron-updater 是**运行时**依赖（不是 devDependency）', () => {
  const dep = (pkg.dependencies || {})['electron-updater'];
  assert.ok(dep, 'electron-updater must be in dependencies: it runs inside the packaged app');
  const dev = (pkg.devDependencies || {})['electron-updater'];
  assert.ok(!dev, 'electron-updater must not be a devDependency or it will not be packaged');
});

check('generic provider 指向生产官网，且带 channel', () => {
  const publish = pkg.build && pkg.build.publish;
  assert.ok(Array.isArray(publish) && publish.length === 1, 'exactly one publish provider');
  const p = publish[0];
  assert.strictEqual(p.provider, 'generic');
  assert.strictEqual(p.url, PRODUCTION_FEED,
    'the generic feed URL is the release authority; it must be the production origin');
  assert.strictEqual(p.channel, 'latest');
});

check('feed 覆盖只走环境变量，且默认值是生产 URL', () => {
  assert.match(mainJs, /process\.env\.MOODIFY_UPDATE_URL/,
    'a test-only feed override must exist so upgrades can be tested without a fake release');
  assert.match(mainJs, /MOODIFY_UPDATE_URL[\s\S]{0,200}?setFeedURL/,
    'the override must actually be applied to the updater');
  // 默认（未设置环境变量时）必须是生产 URL —— 覆盖是显式的，不是回退
  assert.match(mainJs, new RegExp(PRODUCTION_FEED.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    .replace(/\/$/, '\\/?')),
    'the production feed must appear as the default');
});

// ── 2. 禁止静默行为 ─────────────────────────────────────────────────────────────
console.log('\n2. 绝不静默：下载与安装都必须由人触发');

check('autoDownload === false', () => {
  assert.match(mainJs, /autoDownload\s*=\s*false/,
    'autoDownload=true would download updates without the user asking');
  assert.ok(!/autoDownload\s*=\s*true/.test(mainJs), 'autoDownload must never be enabled');
});

check('autoInstallOnAppQuit === false', () => {
  assert.match(mainJs, /autoInstallOnAppQuit\s*=\s*false/,
    'autoInstallOnAppQuit=true would replace the app on exit without consent');
  assert.ok(!/autoInstallOnAppQuit\s*=\s*true/.test(mainJs),
    'autoInstallOnAppQuit must never be enabled');
});

check('没有 checkForUpdatesAndNotify 这类「检查即自动下载」的入口', () => {
  assert.ok(!/checkForUpdatesAndNotify/.test(mainJs),
    'checkForUpdatesAndNotify downloads implicitly; the user must choose');
});

check('downloadUpdate() 只出现在用户动作里', () => {
  const calls = [...mainJs.matchAll(/downloadUpdate\s*\(/g)];
  assert.ok(calls.length >= 1, 'download must be reachable at all');
  // 每个调用点前面必须能看到 action === 'download' 的分支
  for (const m of calls) {
    const before = mainJs.slice(Math.max(0, m.index - 400), m.index);
    assert.match(before, /action\s*===\s*'download'/,
      'every downloadUpdate() call must sit inside the user-triggered download action');
  }
});

check('quitAndInstall() 只在 ready 状态、且是唯一安装入口', () => {
  const calls = [...mainJs.matchAll(/quitAndInstall\s*\(/g)];
  assert.strictEqual(calls.length, 1, 'exactly one install path keeps the rule auditable');
  const before = mainJs.slice(Math.max(0, calls[0].index - 300), calls[0].index);
  assert.match(before, /status\s*===\s*'ready'/,
    'installing from any state other than ready would install something not downloaded');
});

// ── 3. 三种人类选择 ─────────────────────────────────────────────────────────────
console.log('\n3. 三种选择必须同时存在（下载 / 稍后 / 跳过）');

check('renderer 同时暴露「下载更新 / 稍后提醒 / 跳过此版本」', () => {
  assert.match(appJs, /下载更新/, 'the download choice must exist');
  assert.match(html, /id="update-later"[^>]*>稍后提醒/, 'the later choice must exist in the DOM');
  assert.match(html, /id="update-skip"[^>]*>跳过此版本/, 'the skip choice must exist in the DOM');
});

check('「稍后」与「跳过」只对当前可用版本显示，不常驻', () => {
  assert.match(appJs, /later\.hidden\s*=\s*status\s*!==\s*'available'/,
    'later must only apply to an available update');
  assert.match(appJs, /skip\.hidden\s*=\s*status\s*!==\s*'available'/,
    'skip must only apply to an available update');
});

check('「稍后提醒」之后仍能手动检查（否则就是「再也查不了」）', () => {
  // primary 在 later/skipped 下**不能**被隐藏，否则卡片上只剩关闭
  const m = /primary\.hidden\s*=\s*([^;]+);/.exec(appJs);
  assert.ok(m, 'primary.hidden must be computed in one place');
  const expr = m[1];
  assert.ok(!/later/.test(expr) && !/skipped/.test(expr),
    `primary must stay available in later/skipped so the user can change their mind; got: ${expr}`);
  assert.match(appJs, /检查更新/, 'a manual "check again" label must exist');
});

check('primary 的动作由 dataset 单一来源决定，不在两处重复推断', () => {
  assert.match(appJs, /primary\.dataset\.action\s*=/,
    'the action must be written where the label is written');
  assert.match(appJs, /dataset\.action\s*\|\|\s*'check'/,
    'the click handler must read the same action rather than re-deriving it');
});

// ── 4. skip / later 的持久化语义 ────────────────────────────────────────────────
console.log('\n4. 跳过与稍后的语义');

check('skip 持久化的是**版本号**，不是布尔值', () => {
  assert.match(mainJs, /skippedVersion\s*:\s*updateState\.version/,
    'skipping must record which version, so a later version still prompts');
  assert.match(mainJs, /skipped\s*===\s*info\.version/,
    'the comparison must be against the version being offered');
});

check('持久化位置在 userData，不动用户的 ~/.moodify/cases', () => {
  assert.match(mainJs, /updatePreferencesPath[\s\S]{0,200}?app\.getPath\('userData'\)/,
    'update preferences belong in userData');
  const start = mainJs.indexOf('function updatePreferencesPath');
  const body = mainJs.slice(start, start + 400);
  assert.ok(!/cases/.test(body),
    'the updater must never write into the case archive — upgrading must preserve cases, ledgers and settings');
});

check('更高版本出现时仍会提示（skip 不变成永久静音）', () => {
  // update-available 里必须是「等于被跳过的那个版本」才静默，而不是「曾经跳过任何版本」
  const m = /update-available[\s\S]{0,400}?skipped\s*===\s*info\.version/.exec(mainJs);
  assert.ok(m, 'update-available must compare the offered version against the skipped one specifically');
});

check('下载动作会清掉跳过标记（用户改主意要能生效）', () => {
  assert.match(mainJs, /action\s*===\s*'download'[\s\S]{0,200}?skippedVersion\s*:\s*null/,
    'starting a download must clear a previous skip');
});

// ── 5. 状态机表面 ───────────────────────────────────────────────────────────────
console.log('\n5. 状态与桥接三层一致');

check('声明的状态都真的会被发布', () => {
  const declared = ['idle', 'checking', 'available', 'downloading', 'ready',
    'installing', 'current', 'later', 'skipped', 'error', 'dev'];
  for (const s of declared) {
    // 状态可能出现在 `status: 'x'` 里，也可能出现在三元里
    // （`status: skipped === info.version ? 'skipped' : 'available'`），
    // 所以判据是「这个字面量出现在某处 status 赋值中」，而不是固定形态。
    const published = new RegExp(`status:\\s*[^,;\\n]*'${s}'`).test(mainJs);
    assert.ok(published, `state '${s}' is part of the contract but is never published`);
  }
});

check('bridge / IPC 三层名称一致', () => {
  for (const ch of ['update:status', 'update:check', 'update:action']) {
    assert.ok(preloadJs.includes(`'${ch}'`), `preload must invoke ${ch}`);
    assert.ok(mainJs.includes(`'${ch}'`), `main must handle ${ch}`);
  }
  assert.match(preloadJs, /onUpdateStatus[\s\S]{0,120}?'update:status'/,
    'the push channel must be the same one main sends on');
  assert.match(mainJs, /webContents\.send\('update:status'/,
    'main must actually send update:status');
});

check('renderer 只通过 window.moodify 桥接触碰更新能力', () => {
  for (const fn of ['updateStatus', 'updateCheck', 'updateAction', 'onUpdateStatus']) {
    assert.ok(new RegExp(`window\\.moodify\\.${fn}\\b`).test(appJs),
      `renderer must use window.moodify.${fn}`);
  }
});

check('更新失败不会静默：error 状态带可读信息', () => {
  assert.match(mainJs, /status:\s*'error'[\s\S]{0,120}?message/,
    'an updater error must surface as an error state with a message');
  assert.match(appJs, /update-message/, 'the renderer must display that message');
});

// ── 6. 不得拖累既有流程 ─────────────────────────────────────────────────────────
console.log('\n6. updater 不得改动生产流程');

check('updater 不触碰 ~/.moodify/cases（升级必须保留 case 与账本）', () => {
  const start = mainJs.indexOf('function setupAutoUpdater');
  const end = mainJs.indexOf('function pythonEnv');
  const block = mainJs.slice(start, end > start ? end : start + 4000);
  assert.ok(!/CASES_ROOT/.test(block),
    'the updater must not touch CASES_ROOT: an upgrade must preserve cases, decision ledgers and settings');
});

check('更新只发生在已打包的 Windows 构建上', () => {
  assert.match(mainJs, /!app\.isPackaged\s*\|\|\s*process\.platform\s*!==\s*'win32'/,
    'dev builds and other platforms must report dev instead of pretending to check');
});

// ── 7. 与静态合约检查的分工 ─────────────────────────────────────────────────────
console.log('\n7. 跨文件一致性由 check-contracts.js 覆盖（此处只确认它确实在链上）');

check('npm test 链里同时包含 check-contracts 与 test-update', () => {
  assert.match(pkg.scripts.test, /check-contracts/);
  assert.match(pkg.scripts.test, /test-update/,
    'the updater contract test must run as part of the suite, not only by hand');
});

console.log(`\n${failures ? `${failures} FAILED` : 'all updater contract checks passed'}`);
process.exit(failures ? 1 : 0);
