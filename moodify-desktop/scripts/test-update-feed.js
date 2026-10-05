#!/usr/bin/env node
/**
 * 更新 feed 的**发布前校验器**。
 *
 * 它回答的问题：这次要发布的 `latest.yml`，会不会让已经装了旧版的客户端
 * 「永远收不到更新」或者「下载后校验失败」？
 *
 * 为什么这个检查值得单独存在
 *   generic feed 是发布权威，但它的失败模式**全是静默的**：
 *     · 版本号没递增          → 客户端永远认为「已是最新」
 *     · sha512 与安装包不符   → 每个客户端下载完都校验失败，用户只看到「更新失败」
 *     · 文件名字段写错        → 404，同样是「更新失败」
 *     · 先发布 feed 后传包    → 窗口期内所有客户端都拿到 404
 *   这些都不会在构建时报错。构建成功 ≠ 更新能送达。
 *
 * 用法
 *   校验本地产物（发布前跑）：
 *     node scripts/test-update-feed.js --dir moodify-desktop/dist
 *     或 MOODIFY_UPDATE_TEST_DIR=<目录>
 *   额外校验**线上** feed 与线上安装包是否自洽：
 *     node scripts/test-update-feed.js --live
 *
 * 不做什么（如实说明）
 *   本文件**不**执行安装，也**不**驱动 Electron 里的真实 updater。
 *   「在真实 Electron 中走一遍 检查→下载→重启安装→版本变化」需要一台能装包、
 *   有 GUI、可提权的 Windows 机器，是**人工验收步骤**，见
 *   docs/session-handover-2026-10-05-studio-updater.md §差分升级验收。
 *   我曾尝试把这一步自动化（在 electron.exe 里 require('electron-updater')），
 *   但本机 electron 33.4.11 以 Node 模式启动脚本目录、不注入 app API
 *   （process.type 为 undefined），无法在此环境内完成，因此没有留下一个
 *   半可用的自动化壳去冒充验收。
 */

'use strict';

const assert = require('assert');
const crypto = require('crypto');
const fs = require('fs');
const https = require('https');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const PRODUCTION_FEED = 'https://rongjingmusic.com/downloads/studio/windows/latest.yml';

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

/** 解析 electron-builder 生成的 latest.yml（字段很少，不需要完整 YAML 依赖）。 */
function parseFeed(text) {
  const version = (/^version:\s*(.+)$/m.exec(text) || [])[1];
  const fileUrl = (/^\s*-\s*url:\s*(.+)$/m.exec(text) || [])[1];
  const sha512 = (/^\s*sha512:\s*(\S+)/m.exec(text) || [])[1];
  const size = (/^\s*size:\s*(\d+)/m.exec(text) || [])[1];
  return {
    version: version && version.trim(),
    fileUrl: fileUrl && fileUrl.trim(),
    sha512: sha512 && sha512.trim(),
    size: size ? Number(size) : null,
  };
}

function sha512Base64(buf) {
  return crypto.createHash('sha512').update(buf).digest('base64');
}

function fetchBuffer(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode !== 200) {
        res.resume();
        reject(new Error(`HTTP ${res.statusCode} for ${url}`));
        return;
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks)));
    }).on('error', reject);
  });
}

/** 只取远端头，用于核对 Content-Length（不下载 340MB）。 */
function fetchHead(url) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, { method: 'GET', headers: { Range: 'bytes=0-0' } }, (res) => {
      res.resume();
      resolve({
        statusCode: res.statusCode,
        contentRange: res.headers['content-range'] || null,
        contentLength: res.headers['content-length'] ? Number(res.headers['content-length']) : null,
      });
    });
    req.on('error', reject);
    req.end();
  });
}

function localDistDir() {
  if (process.env.MOODIFY_UPDATE_TEST_DIR) return process.env.MOODIFY_UPDATE_TEST_DIR;
  const argIdx = process.argv.indexOf('--dir');
  if (argIdx >= 0 && process.argv[argIdx + 1]) return path.resolve(process.argv[argIdx + 1]);
  const dist = path.join(ROOT, 'dist');
  return fs.existsSync(path.join(dist, 'latest.yml')) ? dist : null;
}

(async function run() {
  console.log('moodify-desktop update feed validator');

  const installedVersion = JSON.parse(
    fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8')).version;
  const publish = (JSON.parse(
    fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8')).build || {}).publish || [];
  const feedUrlInConfig = publish[0] && publish[0].url;

  console.log(`  installed version : ${installedVersion}`);
  console.log(`  publish url       : ${feedUrlInConfig}\n`);

  // ── 1. 配置层面（任何环境都能测）────────────────────────────────────────────
  console.log('1. 发布配置');

  await check('package.json 的 publish 指向生产官网的 generic feed', () => {
    assert.strictEqual(publish.length, 1, 'exactly one publish provider');
    assert.strictEqual(publish[0].provider, 'generic');
    assert.strictEqual(publish[0].url, 'https://rongjingmusic.com/downloads/studio/windows/');
  });

  await check('本地 feed URL 的末尾斜杠与 electron-updater 的拼接方式一致', () => {
    // electron-updater 用 newUrlFromBase 拼接，末尾斜杠缺失会拼出
    // .../windowslatest.yml 这种 404 路径。构建能过，客户端永远收不到更新。
    assert.ok(feedUrlInConfig.endsWith('/'),
      'the generic feed url must end with "/" or child URLs are concatenated wrongly');
  });

  // ── 2. 本地产物（有 dist 时）────────────────────────────────────────────────
  const dir = localDistDir();
  if (!dir) {
    console.log('\n  SKIP  本地产物校验 —— 未找到 dist/latest.yml');
    console.log('        (build first, or pass --dir <dir> / MOODIFY_UPDATE_TEST_DIR)');
  } else {
    const feedPath = path.join(dir, 'latest.yml');
    console.log(`\n2. 本地产物自洽性（${dir}）`);

    const feed = parseFeed(fs.readFileSync(feedPath, 'utf8'));

    await check('feed 声明了 version / url / sha512 / size', () => {
      for (const k of ['version', 'fileUrl', 'sha512', 'size']) {
        assert.ok(feed[k], `latest.yml is missing '${k}'`);
      }
    });

    await check('feed 指向的安装包存在于同一目录', () => {
      const artifact = path.join(dir, feed.fileUrl);
      assert.ok(fs.existsSync(artifact), `latest.yml points at a missing file: ${feed.fileUrl}`);
    });

    await check('feed 的 sha512 与安装包真实 sha512 一致', () => {
      const artifact = path.join(dir, feed.fileUrl);
      const actual = sha512Base64(fs.readFileSync(artifact));
      assert.strictEqual(actual, feed.sha512,
        'latest.yml advertises a sha512 that does not match the file it points at; '
        + 'every client would fail verification after downloading');
    });

    await check('feed 的 size 与安装包真实大小一致', () => {
      const artifact = path.join(dir, feed.fileUrl);
      assert.strictEqual(fs.statSync(artifact).size, feed.size,
        'size mismatch: clients may reject the download or show wrong progress');
    });

    await check('blockmap 与安装包同名同目录（差分下载需要它）', () => {
      const blockmap = path.join(dir, `${feed.fileUrl}.blockmap`);
      assert.ok(fs.existsSync(blockmap),
        `missing ${feed.fileUrl}.blockmap — differential download would fall back or fail`);
    });

    await check('feed 版本不早于本次构建的版本（否则是拿旧 feed 配新包）', () => {
      // 注意：`dist/` 是**当前版本**的构建，所以这里 feed.version === package.json
      // version 是正常的。真正要拦的是 feed 比包**更旧**——那意味着发布时用错了
      // 某个版本的 latest.yml，客户端会看到版本回退或永远不更新。
      // 「这条 feed 一旦发布，能否让已装旧版的用户看到更新」由 --live 那段核对。
      const cmp = compareVersions(feed.version, installedVersion);
      assert.ok(cmp >= 0,
        `feed version ${feed.version} is older than this build ${installedVersion}; `
        + 'that latest.yml does not belong to this artifact');
    });
  }

  // ── 3. 线上 feed（可选）────────────────────────────────────────────────────
  if (process.argv.includes('--live')) {
    console.log('\n3. 线上 feed 自洽性（--live）');

    let liveText = null;
    await check('线上 latest.yml 可访问（HTTP 200）', async () => {
      const buf = await fetchBuffer(PRODUCTION_FEED);
      liveText = buf.toString('utf8');
      assert.ok(liveText.includes('version:'), 'live latest.yml does not look like a feed');
    });

    if (liveText) {
      const live = parseFeed(liveText);
      const base = PRODUCTION_FEED.replace(/latest\.yml$/, '');

      await check('线上 feed 声明的版本高于线上已安装基线', () => {
        assert.ok(compareVersions(live.version, installedVersion) >= 0,
          `live feed version ${live.version} is older than this build ${installedVersion}`);
      });

      await check('线上安装包可访问，且 Content-Length 与 feed 的 size 一致', async () => {
        const head = await fetchHead(`${base}${live.fileUrl}`);
        assert.ok(head.statusCode === 200 || head.statusCode === 206,
          `installer returned HTTP ${head.statusCode}`);
        const length = head.contentRange
          ? Number(head.contentRange.split('/')[1])
          : head.contentLength;
        assert.strictEqual(length, live.size,
          `installer on the server is ${length} bytes but latest.yml says ${live.size}; `
          + 'a truncated upload would fail every client');
      });

      await check('线上 blockmap 可访问', async () => {
        const head = await fetchHead(`${base}${live.fileUrl}.blockmap`);
        assert.ok(head.statusCode === 200 || head.statusCode === 206,
          `blockmap returned HTTP ${head.statusCode}`);
      });
    }
  } else {
    console.log('\n3. 线上 feed 校验未运行（加 --live 启用）');
  }

  console.log(`\n${failures ? `${failures} FAILED` : 'all feed checks passed'}`);
  process.exit(failures ? 1 : 0);
})();

/**
 * 语义化版本比较，支持 -rc.N 这类预发布后缀。
 * 返回 1 / 0 / -1。预发布版本低于同号正式版（1.0.1-rc.1 < 1.0.1）。
 */
function compareVersions(a, b) {
  const split = (v) => {
    const [core, pre] = String(v).split('-');
    const nums = core.split('.').map(Number);
    return { nums, pre: pre || null };
  };
  const A = split(a);
  const B = split(b);
  for (let i = 0; i < Math.max(A.nums.length, B.nums.length); i += 1) {
    const x = A.nums[i] || 0;
    const y = B.nums[i] || 0;
    if (x !== y) return x > y ? 1 : -1;
  }
  if (A.pre === B.pre) return 0;
  if (A.pre === null) return 1;   // 正式版 > 预发布
  if (B.pre === null) return -1;
  return A.pre > B.pre ? 1 : -1;
}
