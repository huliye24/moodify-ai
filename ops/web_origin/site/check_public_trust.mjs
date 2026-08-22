import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "rongjingmusic");
const pages = ["release.html", "research-log.html", "letter.html", "press.html", "developers.html"];
const read = (name) => readFile(path.join(site, name), "utf8");

test("all public trust pages implement the P4-02 metadata contract", async () => {
  for (const page of pages) {
    const html = await read(page);
    const url = `https://rongjingmusic.com/${page}`;
    assert.match(html, /<title>[^<]+<\/title>/, `${page} title`);
    assert.match(html, /<meta name="description" content="[^"]+">/, `${page} description`);
    assert.ok(html.includes(`<link rel="canonical" href="${url}">`), `${page} canonical`);
    for (const property of ["og:title", "og:description", "og:type", "og:url", "og:image"]) assert.ok(html.includes(`property="${property}"`), `${page} ${property}`);
    assert.match(html, /<meta name="twitter:card" content="summary_large_image">/, `${page} twitter card`);
    const json = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)?.[1];
    assert.ok(json, `${page} JSON-LD`);
    assert.doesNotThrow(() => JSON.parse(json), `${page} valid JSON-LD`);
  }
});

test("public trust pages share identity, navigation and operating entity", async () => {
  for (const page of pages) {
    const html = await read(page);
    assert.match(html, /href="https:\/\/play\.rongjingmusic\.com">Play/, `${page} Play`);
    assert.match(html, /href="https:\/\/rongjingwenchuan\.com\/">Company/, `${page} Company`);
    assert.match(html, /Every voice deserves to be heard\./, `${page} belief`);
    assert.match(html, /荣景文川（深圳）科技有限公司/, `${page} entity`);
    for (const target of pages) assert.ok(html.includes(`/${target}`), `${page} missing trust link ${target}`);
  }
});

test("research log uses the complete bounded experiment format", async () => {
  const html = await read("research-log.html");
  for (const label of ["Research Question", "Method", "Experiment", "Observation", "Next Step"]) assert.equal((html.match(new RegExp(`<dt>${label}<\\/dt>`, "g")) ?? []).length, 3, label);
  assert.match(html, /省略核心算法、私有音频、商业机密与未验证实现/);
});

test("release history distinguishes public stable from validated packages", async () => {
  const html = await read("release.html");
  assert.match(html, /Moodify Android 2\.0\.0/);
  assert.match(html, /Current public stable/);
  assert.match(html, /Moodify Android 3\.1\.0/);
  assert.match(html, /Not the current website stable download/);
  assert.doesNotMatch(html, /planned|coming soon|roadmap/i);
});

test("press assets are real and public claims stay bounded", async () => {
  const html = await read("press.html");
  await stat(path.join(site, "assets", "moodify-logo.png"));
  await stat(path.join(site, "assets", "moodify-open-graph.png"));
  assert.match(html, /hello@rongjingmusic\.com/);
  assert.doesNotMatch(html, /\d+[万亿]用户|raised\s+[$¥￥]|valuation\s*[:：]|partner-logo|investor-logo/i);
});

test("technical page remains an overview rather than an API promise", async () => {
  const html = await read("developers.html");
  assert.match(html, /Audio Intelligence/);
  assert.match(html, /Cloud Processing/);
  assert.match(html, /Research Direction/);
  assert.match(html, /不是开放 API 文档/);
  assert.doesNotMatch(html, /api key|endpoint|sdk|curl\s|client secret/i);
});

test("sitemap and homepage expose every public trust asset", async () => {
  const sitemap = await read("sitemap.xml");
  const home = await read("index.html");
  for (const page of pages) {
    assert.ok(sitemap.includes(`https://rongjingmusic.com/${page}`), `sitemap missing ${page}`);
    assert.ok(home.includes(`href="/${page}"`), `home missing ${page}`);
  }
});
