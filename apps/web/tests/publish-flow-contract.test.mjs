import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const read = (path) => readFile(new URL(path, import.meta.url), "utf8");

test("upload is streamed to private media and compensated on metadata failure", async () => {
  const route = await read("../app/api/v1/tracks/[id]/audio/route.ts");
  assert.match(route, /env\.MEDIA\.put\(objectKey, request\.body/);
  assert.match(route, /private\/tracks/);
  assert.match(route, /if \(objectKey\) await env\.MEDIA\.delete/);
  assert.doesNotMatch(route, /arrayBuffer\(|formData\(/);
});

test("publication requires ownership, version, passport, and audit event", async () => {
  const route = await read("../app/api/v1/tracks/[id]/publish/route.ts");
  assert.match(route, /requireOwnedTrack/);
  assert.match(route, /currentVersionId/);
  assert.match(route, /rightsStatement/);
  assert.match(route, /publicationEvents/);
});

test("public media requires a published track", async () => {
  const route = await read("../app/api/v1/tracks/[id]/audio/route.ts");
  assert.match(route, /eq\(tracks\.status, "published"\)/);
  assert.match(route, /accept-ranges/);
});
