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

test("self-hosted builds fail closed for Cloudflare-only bindings", async () => {
  const config = await readFile(new URL("../vite.config.ts", import.meta.url), "utf8");
  const selfHostedBuild = await readFile(
    new URL("../scripts/build-self-hosted.sh", import.meta.url),
    "utf8",
  );
  const adapter = await readFile(
    new URL("../lib/cloudflare-workers-self-hosted.ts", import.meta.url),
    "utf8",
  );
  assert.match(config, /MOODIFY_SELF_HOSTED/);
  assert.match(config, /cloudflare:workers/);
  assert.match(adapter, /CLOUDFLARE_BINDING_UNAVAILABLE/);
  assert.match(selfHostedBuild, /export MOODIFY_SELF_HOSTED=1/);
  assert.match(selfHostedBuild, /build-verified\.sh/);
});
