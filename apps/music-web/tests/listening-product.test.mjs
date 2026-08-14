/* Music listening product checks — MFY_MUSIC_LISTENING_PRODUCT_V1_001.
   Playback contract, discovery discipline, capability honesty, idempotency,
   and media integrity (UI never re-encodes public media). */

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const appDir = path.join(root, "app");

async function read(rel) {
  return readFile(path.join(root, rel), "utf8");
}

test("homepage has exactly one audio element and never autoplays", async () => {
  const home = await read("app/page.tsx");
  assert.equal((home.match(/<audio\b/g) ?? []).length, 1, "exactly one authoritative player element");
  assert.doesNotMatch(home, /<audio[^>]*autoplay|\.play\(\)[^}]*autoplay/i, "no autoplay");
  assert.match(home, /onError/, "media error recovery must exist");
  assert.match(home, /mediaError/, "error state must be rendered");
});

test("player controls are keyboard accessible with aria labels", async () => {
  const home = await read("app/page.tsx");
  for (const label of ["播放", "暂停", "上一首", "下一首", "播放进度", "收藏", "取消收藏"]) {
    const literal = new RegExp(`aria-label="[^"]*${label}`);
    const jsx = new RegExp(`aria-label=\\{[^}]*"${label}"`);
    assert.ok(literal.test(home) || jsx.test(home), `missing aria-label for ${label}`);
  }
  assert.match(home, /type="range"/, "seek must be keyboard-usable (range input)");
});

test("favorites and follows are idempotent on both client and server contract", async () => {
  const client = await read("lib/music-client.ts");
  assert.match(client, /favorite:[\s\S]*?Idempotency-Key/, "favorite must send Idempotency-Key");
  assert.match(client, /follow:[\s\S]*?Idempotency-Key/, "follow must send Idempotency-Key");
  // server side: set semantics with replayed flag
  const social = await read("../../moodify-music-package/src/moodify_music/api/routes_social.py");
  assert.match(social, /"replayed": True/, "server must signal idempotent replay");
});

test("discovery never uses Ear experiment scores or copyright claims", async () => {
  const pages = ["app/page.tsx", "app/library/page.tsx", "app/playlists/page.tsx", "app/studio/page.tsx", "app/console/page.tsx"];
  for (const rel of pages) {
    const content = await read(rel);
    assert.doesNotMatch(content, /Ear[^"]{0,40}评分|实验指标.*排序|auditory.*rank|版权认证(?!，|。|；|\.)/i, `${rel} must not rank by Ear experiments`);
    assert.doesNotMatch(content, /quality[ -]?score|质量评分/i, `${rel} must not present a quality score`);
  }
  const sortSource = await read("app/page.tsx");
  assert.match(sortSource, /filter|为你推荐/, "sorting source must be explainable (curation)");
});

test("capability honesty: disabled capabilities are shown as disabled, not fake", async () => {
  const globals = await read("app/globals.css");
  assert.match(globals, /nav-disabled/, "disabled nav style must exist");
  const lib = await read("lib/music-client.ts");
  assert.match(lib, /account_actions|creator_writes/, "bootstrap capabilities drive UI state");
});

test("public media integrity: UI never re-encodes or rewrites media", async () => {
  const sources = [await read("app/page.tsx"), await read("app/track/[id]/page.tsx")];
  for (const src of sources) {
    assert.doesNotMatch(src, /AudioContext|OfflineAudioContext|MediaRecorder|createObjectURL/, "UI must not process/re-encode audio");
    assert.doesNotMatch(src, /canvas[\s\S]{0,120}audio|audio[\s\S]{0,120}canvas/i, "no canvas audio pipeline");
  }
});

test("playback errors degrade honestly, mobile player does not block content", async () => {
  const globals = await read("app/globals.css");
  assert.match(globals, /player-error/, "error banner style exists");
  assert.match(globals, /@media\(max-width:760px\)[\s\S]*?\.player\{height:78px/, "mobile player is compact");
  assert.match(globals, /padding:0 19px 125px/, "mobile content clears the player");
});
