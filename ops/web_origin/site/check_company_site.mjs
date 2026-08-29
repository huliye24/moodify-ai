import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "rongjingwenchuan");
const home = () => readFile(path.join(site, "index.html"), "utf8");

test("Company Home carries the frozen company identity", async () => {
  const html = await home();
  assert.match(html, /<title>荣景文川 - Rongjing Wenchuan<\/title>/);
  assert.match(html, /We build things worth hearing\./);
  assert.match(html, /An independent company building products and research\./);
  assert.match(html, /Every voice deserves to be heard\./);
  assert.match(html, /每一种声音，都值得被世界听见。/);
  assert.doesNotMatch(html, /Auditory Intelligence Infrastructure|Give machines the ability to hear|Build with Moodify|Developers|\bACU\b|\/v1\/(listen|compare|rank|detect)/);
});

test("Moodify is the primary work with three Product Home links", async () => {
  const html = await home();
  assert.match(html, /Our primary work/i);
  assert.match(html, /Listen\. Then Play\./);
  const links = html.match(/href="https:\/\/rongjingmusic\.com\/"/g) ?? [];
  assert.ok(links.length >= 3, `expected at least three Product Home links, found ${links.length}`);
  assert.doesNotMatch(html, /rongjinwenchuan\.xyz/);
});

test("Research remains a section rather than a product", async () => {
  const html = await home();
  assert.match(html, /id="research"/);
  assert.match(html, /Can machines learn to hear\?/);
  assert.match(html, /The research stays beneath the product surface\./);
  assert.doesNotMatch(html, /Moodify Ear|Listen\s*[→/-]\s*Represent\s*[→/-]\s*Judge/i);
});

test("Company facts expose verified values only", async () => {
  const html = await home();
  assert.match(html, /荣景文川 \/ Rongjing Wenchuan/);
  assert.match(html, /荣景文川（深圳）科技有限公司/);
  assert.match(html, /hello@rongjingmusic\.com/);
  assert.doesNotMatch(html, /Founded|Location|funding|valuation|revenue|users|GPU/i);
});

test("metadata, navigation and footer are coherent", async () => {
  const html = await home();
  assert.match(html, /<link rel="canonical" href="https:\/\/rongjingwenchuan\.com\/">/);
  assert.match(html, /<link rel="icon" href="data:image\/svg\+xml,/);
  assert.match(html, /<meta property="og:title" content="荣景文川 - Rongjing Wenchuan">/);
  assert.match(html, /<meta property="og:description" content="We build things worth hearing\.">/);
  for (const target of ["#research", "#company", "#contact"]) assert.match(html, new RegExp(`href="${target}"`));
  const footer = html.match(/<footer>[\s\S]*?<\/footer>/)?.[0] ?? "";
  for (const label of ["Moodify", "Research", "Company", "Terms", "Privacy", "Contact"]) assert.match(footer, new RegExp(`>${label}<`));
});

test("local pages, styles, robots and sitemap exist", async () => {
  for (const file of ["index.html", "privacy.html", "terms.html", "styles.css", "robots.txt", "sitemap.xml"]) await stat(path.join(site, file));
  const privacy = await readFile(path.join(site, "privacy.html"), "utf8");
  assert.match(privacy, /荣景文川（深圳）科技有限公司/);
  assert.match(privacy, /hello@rongjingmusic\.com/);
  const terms = await readFile(path.join(site, "terms.html"), "utf8");
  assert.match(terms, /荣景文川（深圳）科技有限公司/);
  assert.match(terms, /hello@rongjingmusic\.com/);
  assert.match(terms, /Moodify 知识产权声明/);
  const sitemap = await readFile(path.join(site, "sitemap.xml"), "utf8");
  assert.match(sitemap, /https:\/\/rongjingwenchuan\.com\//);
  assert.match(sitemap, /terms\.html/);
  assert.doesNotMatch(sitemap, /developers|api|acu|docs/);
});

test("Company secondary pages preserve the complete company navigation", async () => {
  for (const page of ["privacy.html", "terms.html"]) {
    const html = await readFile(path.join(site, page), "utf8");
    const header = html.match(/<header[\s\S]*?<\/header>/)?.[0] ?? "";
    for (const target of ["https://rongjingmusic.com/", "/#research", "/#company", "/#contact"]) assert.match(header, new RegExp(`href="${target.replaceAll("/", "\\/")}"`), `${page} missing ${target}`);
    const footer = html.match(/<footer>[\s\S]*?<\/footer>/)?.[0] ?? "";
    for (const label of ["Moodify", "Research", "Company", "Terms", "Privacy", "Contact"]) assert.match(footer, new RegExp(`>${label}<`), `${page} missing ${label}`);
  }
});

test("accessibility and responsive safeguards are present", async () => {
  const html = await home();
  const styles = await readFile(path.join(site, "styles.css"), "utf8");
  assert.match(html, /class="skip-link"/);
  assert.match(html, /<main id="main">/);
  assert.match(styles, /:focus-visible/);
  assert.match(styles, /@media \(max-width: 760px\)/);
  assert.match(styles, /@media \(prefers-reduced-motion: reduce\)/);
  assert.doesNotMatch(html, /<script|autoplay|particle|canvas/i);
});
