/* Design system baseline tests — MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001.
   Static guards over tokens.css and the ui/ component library:
   - single token source (no drifting hex in components)
   - semantic discipline (amber = human attention, red = blocking failure)
   - a11y essentials (focus-visible, reduced-motion, no autoplay) */

import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const tokensPath = path.join(root, "app", "tokens.css");
const globalsPath = path.join(root, "app", "globals.css");
const componentsDir = path.join(root, "components", "ui");

async function componentSources() {
  const files = (await readdir(componentsDir)).filter((f) => f.endsWith(".tsx"));
  const sources = await Promise.all(
    files.map(async (f) => ({ name: f, src: await readFile(path.join(componentsDir, f), "utf8") })),
  );
  return sources;
}

test("tokens.css defines the canonical semantic tokens", async () => {
  const tokens = await readFile(tokensPath, "utf8");
  for (const token of ["--bg", "--surface", "--line", "--text", "--text-muted", "--text-faint", "--evidence", "--attention", "--blocking", "--focus", "--brand-violet", "--brand-cyan"]) {
    assert.match(tokens, new RegExp(`--${token.slice(2)}\\s*:`), `missing token ${token}`);
  }
  assert.match(tokens, /--evidence:\s*#7fb8a8/i, "evidence token must be the canonical value");
  assert.match(tokens, /--attention:\s*#d9a466/i, "attention token must be the canonical value");
  assert.match(tokens, /--blocking:\s*#c87070/i, "blocking token must be the canonical value");
});

test("globals.css imports tokens.css and keeps a single token root", async () => {
  const globals = await readFile(globalsPath, "utf8");
  assert.match(globals, /@import\s+["']\.\/tokens\.css["']/, "tokens.css must be imported");
  const rootBlocks = [...globals.matchAll(/:root\{([^}]*)\}/g)].map((m) => m[1]);
  const definedTokens = rootBlocks.flatMap((b) => [...b.matchAll(/--[\w-]+\s*:/g)].map((m) => m[0]));
  assert.ok(definedTokens.every((t) => ["--muted:"].includes(t)), "no drifting color tokens may be redefined in globals.css root: " + definedTokens.join(","));
});

test("components never hardcode colors — they use tokens only", async () => {
  const sources = await componentSources();
  for (const { name, src } of sources) {
    const hexes = src.match(/#[0-9a-fA-F]{3,8}\b/g) ?? [];
    assert.deepEqual(hexes, [], `${name} hardcodes colors not in the token set: ${hexes.join(", ")}`);
  }
});

test("semantic discipline: amber is human-attention only, red is blocking only", async () => {
  const sources = await componentSources();
  const byName = Object.fromEntries(sources.map(({ name, src }) => [name, src]));
  // status.tsx owns the human_required state (amber) and failed state (red).
  assert.match(byName["status.tsx"], /human_required[\s\S]*var\(--attention\)/, "amber must represent human_required");
  assert.match(byName["status.tsx"], /failed[\s\S]*var\(--blocking\)/, "red must represent failed");
  // states.tsx owns blocking error surfaces.
  assert.match(byName["states.tsx"], /var\(--blocking\)/, "error surfaces must use blocking red");
  // audio transport is neutral + evidence only: never amber/red.
  assert.doesNotMatch(byName["audio.tsx"], /var\(--attention\)|var\(--blocking\)/, "transport must not use attention/blocking");
  // no component may pair attention with an evidence-positive meaning.
  for (const { name, src } of sources) {
    assert.doesNotMatch(src, /var\(--attention\)[^;]*background.*var\(--evidence\)/s, `${name} mixes attention into evidence`);
  }
});

test("reduced-motion guard exists in global CSS", async () => {
  const globals = await readFile(globalsPath, "utf8");
  assert.match(globals, /prefers-reduced-motion:\s*reduce/);
  assert.match(globals, /animation-duration:\s*\.01ms/);
});

test("no autoplay and icon-only buttons carry aria-labels", async () => {
  const sources = await componentSources();
  for (const { name, src } of sources) {
    assert.doesNotMatch(src, /autoPlay|autoplay/i, `${name} must not autoplay media`);
    // scan <button> opening tags manually: JSX expressions ({...}) may contain
    // '>' (arrow functions), so a plain [^>]* scan is not safe.
    for (const match of src.matchAll(/<button\b/g)) {
      let depth = 0;
      let end = match.index;
      for (; end < src.length; end += 1) {
        const c = src[end];
        if (c === "{") depth += 1;
        else if (c === "}") depth = Math.max(0, depth - 1);
        else if (c === ">" && depth === 0) break;
      }
      const tag = src.slice(match.index, end + 1);
      if (tag.includes("aria-label")) continue;
      const after = src.slice(end + 1, end + 81);
      // accessible name may come from an aria-label, plain text, or a JSX
      // expression that renders text (e.g. {productLabel[entry]}).
      const text = after.match(/^([^<{]*[A-Za-z][^<{]*)</)?.[1]?.trim();
      const dynamic = /^\s*\{/.test(after);
      assert.ok(text || dynamic, `${name} has a button without accessible name: ${tag.slice(0, 60)}…`);
    }
  }
});

test("focus-visible styles exist in globals", async () => {
  const globals = await readFile(globalsPath, "utf8");
  assert.match(globals, /:focus-visible\s*\{/);
  assert.match(globals, /var\(--focus\)/);
});
