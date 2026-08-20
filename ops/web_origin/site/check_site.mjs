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

test("all retained pages have baseline metadata", async () => {
  for (const page of pages) {
    const content = await html(page);
    assert.match(content, /<title>.+<\/title>/);
    assert.match(content, /<meta name="description" content="[^"]+">/);
    assert.match(content, /<link rel="canonical" href="https:\/\/rongjingmusic\.com\/[^"]*">/);
    assert.match(content, /<meta name="viewport" content="width=device-width, initial-scale=1">/);
    assert.match(content, /lang="zh-CN"/);
    assert.doesNotMatch(content, /<audio[^>]*autoplay/i);
  }
});

test("Product Home implements the frozen Public Form identity", async () => {
  const home = await html("index.html");
  assert.match(home, /Every voice deserves to be heard\./);
  assert.match(home, /每一种声音，(?:<br>)?都值得被世界听见。/);
  assert.match(home, /href="#download">Download<\/a>/);
  assert.match(home, /href="https:\/\/github\.com\/huliye24\/moodify-ai"/);
  assert.match(home, /href="https:\/\/rongjinwenchuan\.xyz">Play/);
  assert.match(home, /href="https:\/\/rongjingwenchuan\.com\/">Company<\/a>/);
  assert.match(home, /src="\/assets\/moodify-logo\.png"/);
  assert.doesNotMatch(home, /The Ear of AI|Auditory Intelligence Infrastructure|Give machines the ability to hear|\bACU\b|Developers|Creator Platform/);
});

test("Product Home has exactly the approved content sequence", async () => {
  const home = await html("index.html");
  const sequence = [
    'class="hero wrap"',
    'id="download"',
    'aria-labelledby="evidence-title"',
    'class="section company"',
    '<footer class="site-footer">'
  ];
  let cursor = -1;
  for (const marker of sequence) {
    const next = home.indexOf(marker);
    assert.ok(next > cursor, `section marker out of order: ${marker}`);
    cursor = next;
  }
  assert.equal((home.match(/class="evidence-grid"/g) ?? []).length, 1);
  assert.equal((home.match(/<div class="evidence-grid">[\s\S]*?<\/div>/g) ?? []).length, 1);
});

test("Product Home does not present a non-functional Listen action", async () => {
  const home = await html("index.html");
  assert.doesNotMatch(home, /href="#listen"|id="listen"|>Listen<\/a>/);
  assert.doesNotMatch(home, /Listen\. Then Play\.|The principle|aria-labelledby="product-title"/);
  assert.match(home, /href="https:\/\/rongjinwenchuan\.xyz">Play/);
  assert.doesNotMatch(home, /<audio\b|data-original-src|data-moodify-src/);
});

test("download metadata and targets remain internally consistent", async () => {
  const home = await html("index.html");
  const apk = "/downloads/Moodify_Music_2.0.0_Android_20260815.apk";
  const release = "/downloads/Moodify_Music_2_0_0_Android_20260815.zip";
  assert.match(home, new RegExp(apk.replaceAll(".", "\\.")));
  assert.match(home, new RegExp(release.replaceAll(".", "\\.")));
  assert.match(home, /Version 2\.0\.0 · Android 8\.0\+/);
  assert.match(home, /moodify-android-2\.0-download-qr\.png/);
  assert.doesNotMatch(home, /\biOS\b|Coming soon/i);
});

test("homepage Evidence is bounded to three scoped, limited claims", async () => {
  const home = await html("index.html");
  const block = home.match(/<div class="evidence-grid">([\s\S]*?)<\/div>/);
  assert.ok(block);
  assert.equal((block[1].match(/<article>/g) ?? []).length, 3);
  assert.equal((block[1].match(/Scope:/g) ?? []).length, 3);
  assert.equal((block[1].match(/Limitation:/g) ?? []).length, 3);
  assert.equal((block[1].match(/class="maturity/g) ?? []).length, 3);
});

test("Product Home metadata and footer match Public Brand authority", async () => {
  const home = await html("index.html");
  assert.match(home, /<title>Moodify — Every voice deserves to be heard\.<\/title>/);
  assert.match(home, /<meta property="og:title" content="Moodify — Every voice deserves to be heard\.">/);
  assert.match(home, /<meta property="og:description" content="Every voice deserves to be heard\.">/);
  assert.match(home, /<meta property="og:url" content="https:\/\/rongjingmusic\.com\/">/);
  assert.match(home, /<meta property="og:image" content="https:\/\/rongjingmusic\.com\/assets\/moodify-open-graph\.png">/);
  const footer = home.match(/<footer[\s\S]*?<\/footer>/)?.[0] ?? "";
  for (const label of ["Product", "Web Player", "Company", "Research", "Privacy", "Contact", "GitHub"]) assert.match(footer, new RegExp(`>${label}<`));
  assert.doesNotMatch(footer, /The Ear of AI|Infrastructure|\bAPI\b|\bACU\b|Creator Platform/);
});

test("all homepage local routes and assets exist", async () => {
  const home = await html("index.html");
  const links = [...home.matchAll(/(?:href|src)="([^"]+)"/g)].map((m) => m[1]);
  for (const href of links) {
    if (!href.startsWith("/") || href.startsWith("/downloads/")) continue;
    const target = href === "/" ? "index.html" : href.slice(1);
    await stat(path.join(site, target));
  }
});

test("company signature uses the approved seal-script reference without losing accessible text", async () => {
  const home = await html("index.html");
  assert.match(home, /class="sr-only">荣景文川<\/span>/);
  assert.match(home, /src="\/assets\/rongjingwenchuan-seal-wordmark\.png"/);
});

test("secondary-page footers no longer repeat the retired public identity", async () => {
  for (const page of pages.filter((p) => p !== "index.html")) {
    const content = await html(page);
    const footer = content.match(/<footer[\s\S]*?<\/footer>/)?.[0] ?? "";
    assert.ok(footer, `${page} missing footer`);
    assert.doesNotMatch(footer, /The Ear of AI/);
  }
});

test("Ear explanation remains internal and excluded from sitemap", async () => {
  const ear = await html("ear.html");
  assert.match(ear, /<meta name="robots" content="noindex,nofollow">/);
  assert.match(ear, /INTERNAL CAPABILITY · HISTORICAL EXPLANATION/);
  const sitemap = await readFile(path.join(site, "sitemap.xml"), "utf8");
  assert.doesNotMatch(sitemap, /ear\.html/);
});

test("reduced motion and mobile layout are present", async () => {
  const styles = await readFile(path.join(site, "assets", "site-public-form-20260820.css"), "utf8");
  assert.match(styles, /@media \(max-width: 760px\)/);
  assert.match(styles, /@media \(prefers-reduced-motion: reduce\)/);
  assert.match(styles, /:focus-visible/);
});

test("public pages use a versioned stylesheet so old browser CSS cannot mix with new HTML", async () => {
  for (const page of pages) {
    const content = await html(page);
    assert.match(content, /href="\/assets\/site-public-form-20260820\.css"/);
    assert.doesNotMatch(content, /href="\/assets\/site\.css"/);
  }
});
