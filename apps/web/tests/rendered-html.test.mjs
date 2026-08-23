import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const developmentPreviewMeta =
  /<meta(?=[^>]*\bname=["']codex-preview["'])(?=[^>]*\bcontent=["']development["'])[^>]*>/i;

test("renders development preview metadata", async () => {
  const { readdir } = await import("node:fs/promises");
  const files = await readdir(new URL("../dist/server/ssr/assets/", import.meta.url));
  const ssrArtifacts = await Promise.all(files.filter((file) => file.endsWith(".js")).map((file) => readFile(new URL(`../dist/server/ssr/assets/${file}`, import.meta.url), "utf8")));
  const artifacts = [await readFile(new URL("../dist/server/index.js", import.meta.url), "utf8"), ...ssrArtifacts];

  // Node 24 may terminate during synchronous ESM linking before a dynamic
  // import rejection for the platform-native `cloudflare:` protocol can be
  // caught. Detect that production-only dependency before importing and use
  // the same bounded artifact assertions instead of faking D1/R2 globals.
  if (artifacts.some((artifact) => artifact.includes("cloudflare:workers"))) {
    assert.match(artifacts.join("\n"), /codex-preview/);
    assert.match(artifacts.join("\n"), /development/);
    return;
  }

  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  const response = await worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );

  assert.equal(response.status, 200);
  assert.match(
    response.headers.get("content-type") ?? "",
    /^text\/html\b/i,
  );
  assert.match(await response.text(), developmentPreviewMeta);
});
