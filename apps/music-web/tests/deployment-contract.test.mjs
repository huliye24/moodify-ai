import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("deploy build removes copied audio before artifact validation", async () => {
  const build = await readFile(new URL("../scripts/build-verified.sh", import.meta.url), "utf8");
  const prune = await readFile(new URL("../scripts/prune-deploy-audio.sh", import.meta.url), "utf8");
  assert.match(build, /prune-deploy-audio\.sh[\s\S]*validate-artifact\.sh/);
  assert.match(prune, /dist\/client\/audio/);
});

test("public audio uses partial status only for an explicit range request", async () => {
  const route = await readFile(
    new URL("../app/api/v1/tracks/[id]/audio/route.ts", import.meta.url),
    "utf8",
  );
  assert.match(route, /request\.headers\.has\("range"\)[\s\S]*status: 206/);
});
