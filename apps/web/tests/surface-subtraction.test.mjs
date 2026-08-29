import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (relativePath) => readFile(path.join(root, relativePath), "utf8");

test("legacy track route redirects instead of maintaining a second renderer", async () => {
  const legacy = await read("app/track/[id]/page.tsx");
  assert.match(legacy, /redirect\(`\/t\/\$\{encodeURIComponent\(id\)\}`\)/);
  assert.doesNotMatch(legacy, /<audio|fetch\(|license/i);
});

test("public home exposes listener navigation without creator operations", async () => {
  const home = await read("app/page.tsx");
  assert.match(home, /capabilities\?\.account_actions[^]*?href="\/library"/);
  for (const route of ["/studio", "/inbox", "/drafts", "/console", "/design", "/playlists", "/offline"]) {
    assert.doesNotMatch(home, new RegExp(`href=["']${route}`));
  }
  assert.doesNotMatch(home, /上传作品|授权意向|创作者中心|你的音乐/);
  assert.match(home, />聆听者</);
});

test("player drawer preserves the complete public trust path", async () => {
  const home = await read("app/page.tsx");
  for (const target of [
    "https://rongjingmusic.com/",
    "https://rongjingwenchuan.com/",
    "https://rongjingmusic.com/terms.html",
    "https://rongjingmusic.com/privacy.html",
    "https://rongjingmusic.com/contact.html",
  ]) assert.match(home, new RegExp(`href="${target.replaceAll("/", "\\/")}"`), `missing ${target}`);
});

test("canonical track surface links the real creator and has no hidden empty route", async () => {
  const track = await read("app/t/[id]/page.tsx");
  assert.match(track, /track\.creator_handle[^]*?\/c\/\$\{track\.creator_handle\}/);
  assert.doesNotMatch(track, /href=\{`\/c\/\$\{""\}`\}|display:\s*"none"/);
});

test("internal surfaces are noindexed via minimal nested layouts, not deleted", async () => {
  for (const route of ["design", "playlists", "offline", "beta-login"]) {
    const layout = await read(`app/${route}/layout.tsx`);
    assert.match(layout, /robots:\s*\{\s*index:\s*false,\s*follow:\s*false\s*\}/, `${route} layout must set robots noindex`);
    const page = await read(`app/${route}/page.tsx`);
    assert.match(page, /export default/, `${route} page must remain implemented`);
  }
});

test("drafts/console/inbox are subordinate to the creator center", async () => {
  const studio = await read("app/studio/page.tsx");
  for (const [route, label] of [["/drafts", "草稿"], ["/console", "控制台"], ["/inbox", "授权意向"]]) {
    assert.match(studio, new RegExp(`href="${route}"`), `studio must link ${route}`);
    assert.match(studio, new RegExp(`href="${route}"`), `studio must link ${route} as a subordinate entry`);
  }
  for (const route of ["drafts", "console", "inbox"]) {
    const page = await read(`app/${route}/page.tsx`);
    assert.match(page, /href="\/studio"/, `${route} must link back to the creator center`);
    assert.match(page, /返回创作者中心/, `${route} must label the creator center return path consistently`);
  }
  // subordinate entries never resurface on the public home
  const home = await read("app/page.tsx");
  for (const route of ["/drafts", "/console", "/inbox"]) {
    assert.doesNotMatch(home, new RegExp(`href=["']${route}`), `home must not link ${route}`);
  }
});

test("new public track links use /t/, legacy /track/ survives only in the compat route", async () => {
  const publicSurfaces = ["app/page.tsx", "app/t/[id]/page.tsx", "app/library/page.tsx", "app/playlists/page.tsx", "app/inbox/page.tsx", "app/console/page.tsx", "app/drafts/page.tsx"];
  for (const file of publicSurfaces) {
    const source = await read(file);
    assert.doesNotMatch(source, /href="\/track\//, `${file} must not emit new /track/ links`);
  }
  const legacy = await read("app/track/[id]/page.tsx");
  assert.match(legacy, /redirect/);
  assert.match(legacy, /\/t\//);
});
