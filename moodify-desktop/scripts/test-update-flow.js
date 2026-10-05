#!/usr/bin/env node
/**
 * 内置更新的**行为**测试：驱动真实的 main.js 状态机与三个 IPC 动作。
 *
 * 与 test-update.js 的分工
 *   test-update.js  静态契约：源码里不能出现静默下载/静默安装这类写法
 *   本文件          行为契约：真的加载 src/main.js，真的走一遍
 *                   检查 → 可用 → 下载 → 就绪 → 安装，以及 稍后 / 跳过 的语义
 *
 * 为什么必须做行为测试
 *   静态检查能发现「写了 autoDownload = true」，但发现不了
 *   「skip 之后更高版本不再提示」或「later 之后无法再检查」这类**逻辑**错误——
 *   而后者正是这次改动要修的东西。所以这里用 Electron 与 electron-updater 的替身
 *   把 main.js 装起来，再用真实的 IPC 处理器验证状态迁移。
 *
 * 替身边界（如实说明）：electron-updater 是替身，因此本文件**不**证明
 * 「真的能从网上下载并安装」。那一层由 scripts/test-update-feed.js 用真实的
 * NsisUpdater 对着本机 feed 验证；最终「重启后版本真的变了」需要真实安装，
 * 记录在会话交接文档里。
 *
 * Run: node scripts/test-update-flow.js      (exit 1 on any failure)
 */

'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const Module = require('module');

let failures = 0;
function check(name, fn) {
  try {
    const r = fn();
    if (r && typeof r.then === 'function') {
      return r.then(
        () => console.log(`  ok    ${name}`),
        (err) => { failures += 1; console.error(`  FAIL  ${name}\n        ${err.message}`); },
      );
    }
    console.log(`  ok    ${name}`);
  } catch (err) {
    failures += 1;
    console.error(`  FAIL  ${name}`);
    console.error(`        ${err.message}`);
  }
  return Promise.resolve();
}

// ── 替身：electron ──────────────────────────────────────────────────────────────

const USER_DATA = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-update-flow-'));
const CASES_ROOT = fs.mkdtempSync(path.join(os.tmpdir(), 'moodify-update-cases-'));
process.env.MOODIFY_CASES_ROOT = CASES_ROOT;
process.env.MOODIFY_CODEX_HOME = path.join(USER_DATA, 'codex-home');

// main.js 在 app.isPackaged 时会读 process.resourcesPath（bundled runtime 的位置）。
// 普通 node 进程没有这个属性；补一个指向临时目录的值，避免为了测试而改动产品代码。
process.resourcesPath = path.join(USER_DATA, 'resources');

const sentToRenderer = [];
const handlers = new Map();
const quitAndInstallCalls = [];
const downloadUpdateCalls = [];
const checkForUpdatesCalls = [];

const electronStub = {
  app: {
    isPackaged: true,              // 让 setupAutoUpdater 走"已打包"分支
    whenReady: () => ({ then: (fn) => { fn(); return { catch: () => {} }; } }),
    on: () => {},
    quit: () => {},
    getVersion: () => '1.0.1-rc.1',
    getPath: (name) => {
      if (name === 'userData') return USER_DATA;
      return path.join(USER_DATA, name);
    },
  },
  ipcMain: {
    handle: (channel, fn) => handlers.set(channel, fn),
    on: (channel, fn) => handlers.set(channel, fn),
  },
  BrowserWindow: class BrowserWindow {
    constructor() {
      this.webContents = { send: (channel, payload) => sentToRenderer.push({ channel, payload }) };
      this.destroyed = false;
    }
    loadFile() {}
    on() {}
    isDestroyed() { return false; }
    static getAllWindows() { return [windowInstance]; }
    static fromWebContents() { return windowInstance; }
  },
  dialog: {
    showOpenDialog: async () => ({ canceled: true, filePaths: [] }),
    showSaveDialog: async () => ({ canceled: true, filePath: null }),
  },
  shell: { openExternal: async () => {} },
  Menu: { setApplicationMenu: () => {}, buildFromTemplate: () => ({}) },
};
const windowInstance = new electronStub.BrowserWindow();

// ── 替身：electron-updater（一个记录调用的极简 autoUpdater）────────────────────
//
// 它只实现 main.js 真正用到的那部分接口，并把 emit 暴露给测试，
// 以便按真实事件顺序驱动状态机。

const listeners = new Map();
const fakeUpdater = {
  autoDownload: true,            // 故意先设成 true，验证 main.js 会把它改回 false
  autoInstallOnAppQuit: true,    // 同上
  allowPrerelease: false,
  feedUrl: null,
  setFeedURL(arg) { this.feedUrl = arg; },
  on(name, fn) {
    if (!listeners.has(name)) listeners.set(name, []);
    listeners.get(name).push(fn);
    return this;
  },
  emit(name, payload) {
    for (const fn of (listeners.get(name) || [])) fn(payload);
  },
  async checkForUpdates() {
    checkForUpdatesCalls.push(Date.now());
    this.emit('checking-for-update');
    return { updateInfo: { version: '1.0.2-rc.1' } };
  },
  async downloadUpdate() {
    downloadUpdateCalls.push(Date.now());
    return ['/fake/path/Moodify-Studio-1.0.2-rc.1-Windows-x64.exe'];
  },
  quitAndInstall(...args) { quitAndInstallCalls.push(args); },
};

const originalLoad = Module._load;
Module._load = function load(request, parent, isMain) {
  if (request === 'electron') return electronStub;
  if (request === 'electron-updater') return { autoUpdater: fakeUpdater };
  return originalLoad.call(this, request, parent, isMain);
};

require(path.join(__dirname, '..', 'src', 'main.js'));

const call = (channel, ...args) => {
  const fn = handlers.get(channel);
  if (!fn) throw new Error(`no handler registered for ${channel}`);
  return fn({ sender: {} }, ...args);
};
// `update:status` 是同步处理器，返回的是普通对象而不是 Promise；
// 直接 .then() 会炸。统一包一层，让测试不必记哪个处理器是异步的。
const status = async () => call('update:status');
// install 走 setImmediate 让 quitAndInstall 在 IPC 返回之后发生，
// 所以断言前必须让出一轮事件循环。
const tick = () => new Promise((resolve) => setImmediate(resolve));
const prefsPath = path.join(USER_DATA, 'update-preferences.json');
const readPrefs = () => {
  try { return JSON.parse(fs.readFileSync(prefsPath, 'utf8')); } catch { return null; }
};

// ── 测试 ────────────────────────────────────────────────────────────────────────

(async function run() {
  console.log('moodify-desktop updater flow (real main.js, stubbed updater)');

  console.log('\n1. 启动即强制关闭自动行为');

  await check('加载 main.js 本身不触发任何检查 / 下载 / 安装', () => {
    // 必须最先断言：一旦下面的用例触发过检查，这条就失去意义了。
    assert.strictEqual(checkForUpdatesCalls.length, 0,
      'no check may be triggered by merely loading main.js');
    assert.strictEqual(downloadUpdateCalls.length, 0, 'no silent download');
    assert.strictEqual(quitAndInstallCalls.length, 0, 'no silent install');
  });

  await check('main.js 把 autoDownload / autoInstallOnAppQuit 强制设为 false', async () => {
    // 读状态**不应**触发 updater 初始化（读不是做）；
    // 所以这里显式走一次检查，把 setupAutoUpdater 叫起来。
    await call('update:check');
    assert.strictEqual(fakeUpdater.autoDownload, false,
      'autoDownload must be forced off even if the updater defaults to true');
    assert.strictEqual(fakeUpdater.autoInstallOnAppQuit, false,
      'autoInstallOnAppQuit must be forced off');
  });

  await check('读状态本身不会触发检查（读不是做）', async () => {
    const before = checkForUpdatesCalls.length;
    await status();
    await status();
    assert.strictEqual(checkForUpdatesCalls.length, before,
      'reading update status must not perform a network check');
  });

  await check('环境变量 MOODIFY_UPDATE_URL 未设置时不覆盖生产 feed', () => {
    assert.strictEqual(fakeUpdater.feedUrl, null,
      'without the env var the production feed from package.json must stay in force');
  });

  console.log('\n2. 检查 → 可用 → 下载 → 就绪');

  await check('手动检查：update-available 让状态变为 available 并带上版本号', async () => {
    const p = call('update:check');
    fakeUpdater.emit('update-available', { version: '1.0.2-rc.1' });
    await p;
    const st = await status();
    assert.strictEqual(st.status, 'available');
    assert.strictEqual(st.version, '1.0.2-rc.1');
  });

  await check('available 状态下**没有**自动开始下载（人必须先选）', () => {
    assert.strictEqual(downloadUpdateCalls.length, 0,
      'discovering an update must not start a download');
  });

  await check('「下载更新」才触发 downloadUpdate，并进入 downloading', async () => {
    const p = call('update:action', 'download');
    const during = await status();
    assert.strictEqual(during.status, 'downloading');
    await p;
    assert.strictEqual(downloadUpdateCalls.length, 1, 'exactly one user-triggered download');
  });

  await check('download-progress 把百分比透传到界面', async () => {
    fakeUpdater.emit('download-progress', { percent: 42.6 });
    const st = await status();
    assert.strictEqual(st.status, 'downloading');
    assert.strictEqual(st.percent, 43, 'percent must be rounded for display');
  });

  await check('update-downloaded 进入 ready（此时才允许安装）', async () => {
    fakeUpdater.emit('update-downloaded', { version: '1.0.2-rc.1' });
    const st = await status();
    assert.strictEqual(st.status, 'ready');
    assert.strictEqual(st.percent, 100);
  });

  console.log('\n3. 只有 ready 才能安装');

  await check('ready 之前调用 install 会被拒绝（防止装一个没下完的东西）', async () => {
    // 回到 available，再尝试安装
    fakeUpdater.emit('update-available', { version: '1.0.3-rc.1' });
    const st = await call('update:action', 'install');
    assert.notStrictEqual(st.status, 'installing', 'install must not start outside ready');
    assert.strictEqual(quitAndInstallCalls.length, 0);
  });

  await check('ready 状态下 install 触发 quitAndInstall(false, true)', async () => {
    fakeUpdater.emit('update-downloaded', { version: '1.0.3-rc.1' });
    await call('update:action', 'install');
    await tick();   // quitAndInstall 由 setImmediate 触发
    assert.strictEqual(quitAndInstallCalls.length, 1, 'exactly one install');
    assert.deepStrictEqual(quitAndInstallCalls[0], [false, true],
      'isSilent=false and isForceRunAfter=true');
  });

  console.log('\n4. 「稍后提醒」与「跳过此版本」的语义');

  await check('later 只是本次不更新，不写任何持久化', async () => {
    fakeUpdater.emit('update-available', { version: '1.0.4-rc.1' });
    const st = await call('update:action', 'later');
    assert.strictEqual(st.status, 'later');
    const prefs = readPrefs();
    assert.ok(!prefs || !prefs.skippedVersion,
      'later must not persist a skip: the user only deferred this prompt');
  });

  await check('later 之后仍可再次手动检查（否则就是「再也查不了」）', async () => {
    const before = checkForUpdatesCalls.length;
    await call('update:check');
    assert.strictEqual(checkForUpdatesCalls.length, before + 1,
      'a manual check must remain possible after choosing later');
  });

  await check('skip 持久化的是被跳过的**具体版本号**', async () => {
    fakeUpdater.emit('update-available', { version: '1.0.4-rc.1' });
    await call('update:action', 'skip');
    assert.strictEqual(readPrefs().skippedVersion, '1.0.4-rc.1',
      'skip must record which version, so a later one still prompts');
  });

  await check('被跳过的同一版本再次出现 → 状态为 skipped（不打扰）', async () => {
    fakeUpdater.emit('update-available', { version: '1.0.4-rc.1' });
    const st = await status();
    assert.strictEqual(st.status, 'skipped');
  });

  await check('更高的版本出现 → 必须再次提示为 available（skip 不是永久静音）', async () => {
    fakeUpdater.emit('update-available', { version: '1.0.5-rc.1' });
    const st = await status();
    assert.strictEqual(st.status, 'available',
      'skipping 1.0.4 must not silence 1.0.5');
    assert.strictEqual(st.version, '1.0.5-rc.1');
  });

  await check('用户改主意开始下载 → 跳过标记被清除', async () => {
    await call('update:action', 'download');
    const prefs = readPrefs();
    assert.ok(prefs.skippedVersion === null || prefs.skippedVersion === undefined,
      'starting a download must clear a previous skip so the choice can be reversed');
  });

  console.log('\n5. 错误与不支持的环境要如实说');

  await check('updater error → error 状态且带可读信息（不静默）', async () => {
    fakeUpdater.emit('error', new Error('连接更新服务器失败'));
    const st = await status();
    assert.strictEqual(st.status, 'error');
    assert.match(st.message, /连接更新服务器失败/);
  });

  await check('不是最新版时会明确说「已是最新版本」', async () => {
    fakeUpdater.emit('update-not-available', {});
    const st = await status();
    assert.strictEqual(st.status, 'current');
  });

  console.log('\n6. 升级不得动用户的 case 世界');

  await check('整个 updater 流程没有在 cases 根目录写入任何东西', () => {
    const entries = fs.readdirSync(CASES_ROOT);
    assert.deepStrictEqual(entries, [],
      `the updater must not touch the case archive; found: ${entries.join(', ')}`);
  });

  await check('偏好只写在 userData 下', () => {
    assert.ok(fs.existsSync(prefsPath), 'preferences must live in userData');
    assert.ok(prefsPath.startsWith(USER_DATA), 'preferences must not live in the case archive');
  });

  // ── cleanup ──────────────────────────────────────────────────────────────────
  Module._load = originalLoad;
  for (const d of [USER_DATA, CASES_ROOT]) {
    try { fs.rmSync(d, { recursive: true, force: true }); } catch { /* best effort */ }
  }

  console.log(`\n${failures ? `${failures} FAILED` : 'all updater flow checks passed'}`);
  process.exit(failures ? 1 : 0);
})();
