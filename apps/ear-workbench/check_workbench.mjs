/* Ear workbench static checks — MFY_EAR_PRODUCT_SURFACE_V1_001.
   - required routes exist with meta essentials
   - four first-class states (processing / human_required / inconclusive / failed)
     are rendered as state labels, never as generic spinners
   - no fake success, no placeholder entries, no autoplay
   - result page layers findings before raw JSON
   - private paths/audio/prompts never referenced in the UI
   - CTA links resolve to real routes */

import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const wb = path.resolve(path.dirname(fileURLToPath(import.meta.url)));
const pages = ["index.html", "new-case.html", "case.html", "result.html", "compare.html", "evidence.html", "reviews.html", "status.html"];

async function html(name) {
  return readFile(path.join(wb, name), "utf8");
}

test("all routes exist with meta essentials", async () => {
  for (const page of pages) {
    const content = await html(page);
    assert.match(content, /<title>.+<\/title>/, `${page} missing title`);
    assert.match(content, /<meta name="description" content="[^"]+">/, `${page} missing meta description`);
    assert.match(content, /<meta name="viewport" content="width=device-width, initial-scale=1">/, `${page} missing viewport`);
    assert.match(content, /data-page="[a-z]+"/, `${page} missing page hook`);
  }
});

test("first-class states exist as state labels (processing/human/inconclusive/failed)", async () => {
  const js = await readFile(path.join(wb, "assets", "workbench.js"), "utf8");
  for (const token of ["processing", "human", "inconclusive", "failed", "verified"]) {
    assert.match(js, new RegExp(`"${token}"`), `missing state key ${token}`);
  }
  // amber is reserved for human attention; red for blocking failure
  const css = await readFile(path.join(wb, "assets", "workbench.css"), "utf8");
  assert.match(css, /\.pill\.human\s*\{[^}]*var\(--attention\)/, "human state must be amber");
  assert.match(css, /\.pill\.failed\s*\{[^}]*var\(--blocking\)/, "failed state must be red");
});

test("no fake success, no placeholder entries, no autoplay", async () => {
  for (const page of pages) {
    const content = await html(page);
    // PLACEHOLDER(?!\s*=) excludes the legitimate input placeholder attribute
    assert.doesNotMatch(content, /PLACEHOLDER(?!\s*=)|media-placeholder|demo-case|fake-\w/i, `${page} contains placeholder/fake entries`);
    assert.doesNotMatch(content, /<audio[^>]*autoplay/i, `${page} must not autoplay`);
  }
});

test("result page leads with findings, not raw JSON", async () => {
  const result = await html("result.html");
  const findings = result.indexOf("Findings");
  const measurements = result.indexOf("Measurements");
  assert.ok(findings !== -1 && measurements !== -1 && findings < measurements, "findings must precede measurements");
  assert.doesNotMatch(result, /<pre>|<code>/, "result page must not dump raw JSON");
  // second and third layers exist for progressive disclosure
  assert.match(result, /Method &amp; versions/);
});

test("private paths, audio bodies and prompts never leak into the UI", async () => {
  const all = await Promise.all([...pages.map(html), readFile(path.join(wb, "assets", "workbench.js"), "utf8")]);
  const joined = all.join("\n");
  // case_dir/output_root are public API contract fields consumed by the
  // client for availability logic; their values are never rendered as paths.
  for (const token of ["C:\\", "/home/", "state_dir", "case_config.json", "production_case.json"]) {
    assert.doesNotMatch(joined, new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")), `UI leaks internal token: ${token}`);
  }
  // uploads never go to analytics/localStorage beyond the job id
  assert.doesNotMatch(joined, /localStorage\.setItem\("[^"]*audio|setItem\("[^"]*file/i, "audio bodies must not be persisted client-side");
});

test("CTA links resolve to real routes", async () => {
  const routes = new Set(pages);
  for (const page of pages) {
    const content = await html(page);
    for (const match of content.matchAll(/href="(\/[a-z-]*\.html)"/g)) {
      const target = match[1].slice(1);
      assert.ok(routes.has(target), `${page} links to missing route: ${match[1]}`);
    }
  }
});

test("assets exist", async () => {
  await stat(path.join(wb, "assets", "workbench.css"));
  await stat(path.join(wb, "assets", "workbench.js"));
});
