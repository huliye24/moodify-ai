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

test("homepage carries the single public Music product and sound-first test", async () => {
  const home = await html("index.html");
  assert.match(home, /MOODIFY/);
  assert.match(home, /LISTEN\. THEN\s*<em>PLAY\.<\/em>/i);
  assert.match(home, /Moodify 先听，再为你播放/);
  assert.match(home, /Does the sound stand on its own/);
  assert.doesNotMatch(home, /href="\/ear\.html"/);
  assert.doesNotMatch(home, /One ear\. Two products/);
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

test("sitemap keeps public pages and excludes Ear", async () => {
  const sitemap = await readFile(path.join(site, "sitemap.xml"), "utf8");
  for (const page of ["/", "/music.html", "/evidence.html", "/about.html", "/contact.html", "/privacy.html"]) {
    assert.match(sitemap, new RegExp(`<loc>https://rongjingmusic\\.com${page}</loc>`), `sitemap must keep ${page}`);
  }
  assert.doesNotMatch(sitemap, /ear\.html/, "sitemap must not list /ear.html");
});

test("every public page carries the three-item primary nav", async () => {
  const NAV = ["/", "/music.html", "/evidence.html"];
  for (const page of pages) {
    const content = await html(page);
    const block = content.match(/<nav class="site-nav" aria-label="Primary">\r?\n([\s\S]*?)\r?\n\s*<\/nav>/);
    assert.ok(block, `${page} missing primary nav`);
    const links = [...block[1].matchAll(/<a href="([^"]+)"[^>]*>/g)].map((m) => m[1]);
    assert.deepEqual(links, NAV, `${page} primary nav must be exactly ${NAV.join(", ")}`);
  }
});

test("no public page links Ear as a consumer entry", async () => {
  for (const page of pages) {
    const content = await html(page);
    assert.doesNotMatch(content, /<a\b[^>]*href="\/ear\.html"/, `${page} must not link /ear.html in the public site`);
    assert.doesNotMatch(content, /Enter Ear|Explore Ear|Enter Moodify Ear|One ear\. Two products|Ear and Music are separate products/i, `${page} contains a forbidden dual-product expression`);
  }
});

test("the Ear explanation page is retained but internalized", async () => {
  const ear = await html("ear.html");
  assert.match(ear, /<meta name="robots" content="noindex,nofollow">/, "ear.html must carry noindex,nofollow");
  assert.match(ear, /INTERNAL CAPABILITY · HISTORICAL EXPLANATION/, "ear.html must be marked as internal/historical");
  assert.doesNotMatch(ear, /href="https?:\/\/[^"]*workbench|href="\/apps\//i, "ear.html must not link to the public Workbench");
});

test("footer keeps legal and contact pages reachable", async () => {
  for (const page of pages) {
    const content = await html(page);
    const footer = content.match(/<footer[\s\S]*?<\/footer>/);
    assert.ok(footer, `${page} missing footer`);
    for (const href of ["/about.html", "/contact.html", "/privacy.html"]) {
      assert.match(footer[0], new RegExp(`href="${href}"`), `${page} footer must keep ${href}`);
    }
  }
});
