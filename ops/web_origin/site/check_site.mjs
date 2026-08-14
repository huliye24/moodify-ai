/* Official website static checks — MFY_OFFICIAL_WEBSITE_V1_001.
   - required routes exist with meta essentials
   - identity hero + Chinese core sentence on the homepage
   - no forbidden public claims (positive form)
   - every CTA href resolves to a real route or an approved external target
   - no autoplay; claim maturity labels on evidence items */

import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "rongjingmusic");
const pages = ["index.html", "ear.html", "music.html", "evidence.html", "about.html", "contact.html", "privacy.html"];

async function html(name) {
  return readFile(path.join(site, name), "utf8");
}

const FORBIDDEN_CLAIMS = [
  /保证(更)?好/,           // guaranteed improvement
  /自动母带(?!产品|项目|工具|身份)/, // auto-mastering as a product identity (negation contexts allowed)
  /版权认证(?!，|。|；|\.)/, // copyright certification as a feature
  /完全机器(最终)?裁决/,     // unlimited machine authority
  /机器说了算/,
];

test("all required pages exist with meta essentials", async () => {
  for (const page of pages) {
    const content = await html(page);
    assert.match(content, /<title>.+<\/title>/, `${page} missing title`);
    assert.match(content, /<meta name="description" content="[^"]+">/, `${page} missing meta description`);
    assert.match(content, /<link rel="canonical" href="https:\/\/rongjingmusic\.com\/[^"]*">/, `${page} missing canonical`);
    assert.match(content, /<meta name="viewport" content="width=device-width, initial-scale=1">/, `${page} missing viewport`);
    assert.match(content, /lang="zh-CN"/, `${page} missing lang`);
  }
});

test("homepage carries the identity hero and Chinese core sentence", async () => {
  const home = await html("index.html");
  assert.match(home, /MOODIFY/);
  assert.match(home, /THE\s*<em>EAR<\/em>\s*OF\s*AI/i);
  assert.match(home, /让机器不只会生成声音，也真正学会听/);
  assert.match(home, /Generation is not hearing/);
});

test("no forbidden positive claims on any page", async () => {
  for (const page of pages) {
    const content = await html(page);
    for (const pattern of FORBIDDEN_CLAIMS) {
      const matches = content.match(new RegExp(pattern.source, "gi")) ?? [];
      for (const m of matches) {
        assert.doesNotMatch(m, pattern, `${page} contains forbidden claim: ${m.trim()}`);
      }
    }
    assert.doesNotMatch(content, /<audio[^>]*autoplay/i, `${page} must not autoplay audio`);
  }
});

test("every CTA resolves to a real route or approved external target", async () => {
  const internal = new Set(pages);
  const approvedExternal = [/^https:\/\/rongjinwenchuan\.xyz(\/|$)/, /^mailto:/, /^#/];
  for (const page of pages) {
    const content = await html(page);
    // CTA check applies to <a href> navigation links, not meta/canonical/og:url.
    const links = [...content.matchAll(/<a\b[^>]*href="([^"]+)"/g)].map((m) => m[1]).filter((h) => !h.startsWith("/assets/"));
    for (const href of links) {
      if (href.startsWith("/")) {
        const target = href.slice(1) || "index.html";
        assert.ok(internal.has(target), `${page} links to missing route: ${href}`);
      } else if (!approvedExternal.some((re) => re.test(href))) {
        assert.fail(`${page} links to unapproved external target: ${href}`);
      }
    }
  }
});

test("evidence items carry claim maturity labels", async () => {
  const evidence = await html("evidence.html");
  const items = evidence.match(/class="maturity[^"]*"/g) ?? [];
  assert.ok(items.length >= 4, `expected at least 4 maturity labels, found ${items.length}`);
  const states = new Set(items.map((m) => (m.includes("experimental") ? "experimental" : m.includes("human-reviewed") ? "human-reviewed" : m.includes("verified") ? "verified" : "concept")));
  assert.ok(states.has("verified") && states.has("experimental"), "evidence must include verified and experimental maturities");
});

test("robots and sitemap exist", async () => {
  await stat(path.join(site, "robots.txt"));
  const sitemap = await readFile(path.join(site, "sitemap.xml"), "utf8");
  assert.match(sitemap, /<loc>https:\/\/rongjingmusic\.com\/[^<]+<\/loc>/);
});
