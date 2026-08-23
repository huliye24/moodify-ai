/* Creator publishing client checks — MFY_MUSIC_CREATOR_PUBLISHING_V1_001.
   Studio surfaces: passport disclaimer, idempotent writes, recovery from
   server facts, no fake publish affordances, preview honesty. */

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

async function read(rel) {
  return readFile(path.join(root, rel), "utf8");
}

test("studio passport carries the non-certification disclaimer", async () => {
  const studio = await read("app/studio/page.tsx");
  assert.match(studio, /非版权|版权确权|版权认证(?!，|。|；|\.)/, "passport disclaimer must exist");
  assert.doesNotMatch(studio, /版权认证(?!，|。|；|\.)/, "passport must never claim certification");
});

test("every creator write uses an idempotency key", async () => {
  const client = await read("lib/music-client.ts");
  for (const action of ["createTrack", "createVersion", "upsertPassport", "createCreator"]) {
    assert.match(client, new RegExp(`${action}:\\s*\\([^)]*idempotencyKey`), `${action} must accept an idempotency key`);
  }
  const studio = await read("app/studio/page.tsx");
  assert.match(studio, /crypto\.randomUUID|idem|Idempotency/, "studio must generate idempotency keys per flow");
});

test("recovery reads server state instead of guessing", async () => {
  const studio = await read("app/studio/page.tsx");
  assert.match(studio, /resume|stage/, "resume must be derived from server stages");
  assert.doesNotMatch(studio, /localStorage[\s\S]{0,200}publish|localStorage[\s\S]{0,200}status/i, "publish state must not be trusted from localStorage");
});

test("no fake publish affordances or placeholder buttons", async () => {
  const pages = ["app/studio/page.tsx", "app/console/page.tsx", "app/drafts/page.tsx"];
  for (const rel of pages) {
    const content = await read(rel);
    // a publish affordance is honest when its handler is a real action
    assert.doesNotMatch(
      content,
      /onClick=\{(?![\s\S]{0,80}(?:publish|republish|confirm|api\.))[\s\S]{0,80}\}[^>]*>[^<]*发布[\s\S]{0,40}<\/button>/i,
      `${rel} may have a fake publish button`,
    );
    // PLACEHOLDER(?!\s*=) excludes the legitimate input placeholder attribute
    assert.doesNotMatch(content, /PLACEHOLDER(?!\s*=)|TODO|coming soon/i, `${rel} must not show placeholder affordances`);
  }
});

test("preview and blockers are explicit", async () => {
  const studio = await read("app/studio/page.tsx");
  // the confirm card is the honest preview: real public URL, fingerprint,
  // rights statement and the non-certification boundary
  assert.match(studio, /CONFIRM PUBLICATION|确认发布/, "studio must expose a publish confirmation/preview");
  assert.match(studio, /公开地址|location\.origin\/t\//, "preview must show the real public result URL");
  assert.match(studio, /不将其视为版权认证|非版权/, "preview must state the non-certification boundary");
  assert.match(studio, /creator_writes/, "capability blockers must gate the publish action");
});

test("client recovery never persists secrets or audio bodies", async () => {
  const client = await read("lib/music-client.ts");
  assert.doesNotMatch(client, /localStorage[\s\S]{0,120}(cookie|token|invite|secret|audio)/i, "client must not persist secrets or audio");
});
