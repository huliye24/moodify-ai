/**
 * Static contract check for the Moodify Studio shell — no Electron needed.
 *
 * The shell is deliberately dumb: the renderer may only touch DOM ids that
 * exist in index.html and bridge methods that exist in preload.js, and every
 * channel preload invokes must be handled in main.js. Shipping a renderer that
 * calls a missing id or a missing channel produces a silent UI break at
 * runtime; this turns those into a build-time failure.
 *
 * Section 6 pins one more cross-file contract: every completion-session phase declared in
 * src/session.js must have a real step function in main.js's SESSION_STEPS. A drift there does
 * not crash — "开始完成" just stops at PHASE_HAS_NO_ACTION, which reads like a hang.
 *
 * Run: node scripts/check-contracts.js      (exit 1 on any violation)
 */

'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const read = (rel) => fs.readFileSync(path.join(ROOT, rel), 'utf8');

const html = read(path.join('renderer', 'index.html'));
const appJs = read(path.join('renderer', 'app.js'));
const preloadJs = read(path.join('src', 'preload.js'));
const mainJs = read(path.join('src', 'main.js'));

// `window.moodify.X(...)` / bare destructuring is not used by the shell; the
// renderer only ever goes through these two accessors.
const NOTE = 'renderer 里每个 id / bridge 方法都必须在真实 DOM 与 preload 中存在';

const problems = [];

function collect(text, pattern, group = 1) {
  const found = new Set();
  for (const match of text.matchAll(pattern)) found.add(match[group]);
  return found;
}

function diff(required, available, label, hint) {
  const missing = [...required].filter((name) => !available.has(name)).sort();
  if (missing.length) {
    problems.push(`${label} 缺少 ${missing.length} 项：${missing.join(', ')}${hint ? `\n    → ${hint}` : ''}`);
  }
  return missing;
}

// ——— 1) renderer DOM ids ⊂ index.html ids ∪ ids the renderer creates ————
// A handful of nodes are lazily built by the renderer itself (error banner,
// score hint): `$('x')` is null the first time by design, so their ids are
// declared here rather than in the markup.
const htmlIds = new Set([
  ...collect(html, /id="([^"]+)"/g),
  ...collect(appJs, /\.id\s*=\s*'([^']+)'/g),
  ...collect(appJs, /\.id\s*=\s*"([^"]+)"/g),
]);
const domRefs = new Set([
  ...collect(appJs, /\$\('([^']+)'\)/g),
  ...collect(appJs, /getElementById\('([^']+)'\)/g),
  ...collect(appJs, /getElementById\("([^"]+)"\)/g),
]);
diff(domRefs, htmlIds, 'DOM 引用', 'app.js 引用了 index.html 里不存在的 id');

// ——— 2) renderer bridge calls ⊂ preload exposes ————————————————————————
const exposed = collect(preloadJs, /^\s{2}([A-Za-z_$][\w$]*)\s*[:(]/gm);
const bridgeCalls = collect(appJs, /window\.moodify\.([A-Za-z_$][\w$]*)/g);
diff(bridgeCalls, exposed, '桥接方法', 'app.js 调用了 preload.js 未暴露的 window.moodify.*');

// ——— 3) preload → main channels ————————————————————————————————————————
const handled = new Set([
  ...collect(mainJs, /ipcMain\.handle\(\s*'([^']+)'/g),
  ...collect(mainJs, /ipcMain\.handle\(\s*"([^"]+)"/g),
  ...collect(mainJs, /ipcMain\.on\(\s*'([^']+)'/g),
]);
const invoked = new Set([
  ...collect(preloadJs, /ipcRenderer\.invoke\(\s*'([^']+)'/g),
  ...collect(preloadJs, /ipcRenderer\.invoke\(\s*"([^"]+)"/g),
  ...collect(preloadJs, /ipcRenderer\.send\(\s*'([^']+)'/g),
]);
diff(invoked, handled, 'IPC 通道（preload → main）',
     'preload 发起了 main.js 未注册的 channel');

// ——— 4) main → renderer events ——————————————————————————————————————————
const sent = new Set([
  ...collect(mainJs, /webContents\.send\(\s*'([^']+)'/g),
  ...collect(mainJs, /webContents\.send\(\s*"([^"]+)"/g),
]);
const listened = new Set([
  ...collect(preloadJs, /ipcRenderer\.on\(\s*'([^']+)'/g),
  ...collect(preloadJs, /ipcRenderer\.on\(\s*"([^"]+)"/g),
]);
const unhandledEvents = [...sent].filter((name) => !listened.has(name)).sort();
// main → preload events are one-way broadcasts; only report ones preload never listens to
if (unhandledEvents.length) {
  problems.push(`preload 未监听 main 事件：${unhandledEvents.join(', ')}`);
}

// ——— 5) sandbox invariants ——————————————————————————————————————————————
const webPrefs = /contextIsolation:\s*(true|false)/.exec(mainJs);
const nodeIntegration = /nodeIntegration:\s*(true|false)/.exec(mainJs);
if (!webPrefs || webPrefs[1] !== 'true') {
  problems.push('main.js 必须保持 contextIsolation: true');
}
if (nodeIntegration && nodeIntegration[1] !== 'false') {
  problems.push('main.js 必须保持 nodeIntegration: false');
}

// ——— 6) every session phase must have a real step in main ————————————————
// 一键完成机的相位表在 src/session.js，真正干活的函数在 main.js 的 SESSION_STEPS。
// 两边漂移的后果不是崩溃，而是「一键启动」在某个相位停在 PHASE_HAS_NO_ACTION ——
// 用户看到的是流程莫名停住。所以这里把两边的键对上。
const sessionJs = read(path.join('src', 'session.js'));
const sessionRuns = collect(sessionJs, /run:\s*'([^']+)'/g);
const stepsBlock = /SESSION_STEPS\s*=\s*Object\.freeze\(\{([\s\S]*?)\}\)/.exec(mainJs);
const stepKeys = stepsBlock ? collect(stepsBlock[1], /(\w+)\s*:/g) : new Set();
diff(sessionRuns, stepKeys, '会话相位步骤',
     'src/session.js 的 PHASES[].run 必须在 main.js 的 SESSION_STEPS 里有真实实现');

// ——— report —————————————————————————————————————————————————————————————
if (problems.length) {
  console.error(`✗ Studio 合约检查失败（${problems.length} 项）`);
  for (const problem of problems) console.error(`  - ${problem}`);
  process.exit(1);
}
console.log('✓ Studio 合约检查通过'
  + `（DOM id ${domRefs.size} · 桥接 ${bridgeCalls.size} · IPC ${invoked.size} · 事件 ${sent.size}`
  + ` · 会话相位 ${sessionRuns.size}）`
  + ` — ${NOTE}`);
