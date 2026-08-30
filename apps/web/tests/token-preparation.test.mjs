import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync(new URL("../app/token/page.tsx", import.meta.url), "utf8");
const layout = readFileSync(new URL("../app/token/layout.tsx", import.meta.url), "utf8");
const source = `${page}\n${layout}`;

test("public surface follows the whitepaper architecture", () => {
  for (const layer of ["WORLD", "PROTOCOL", "PORTAL", "Network", "Library", "Moodify Gate"]) {
    assert.match(source, new RegExp(layer));
  }
  assert.match(source, /MOOD is the world\. Moodify is only the beginning\./);
});

test("token surface contains no obsolete trade claims", () => {
  assert.doesNotMatch(source, /0x1BB/i);
  assert.doesNotMatch(source, /PancakeSwap/i);
  assert.doesNotMatch(source, /33,000,000/);
  assert.doesNotMatch(source, /OFFICIAL CONTRACT/);
  assert.doesNotMatch(source, /连接钱包/);
});

test("token surface keeps internal readiness notes off the public site", () => {
  for (const internalNote of ["CURRENT VERIFIED STATE", "PUBLIC GENESIS GATES", "AML/KYC", "多签", "密钥保管", "税率", "审查中", "待决定", "未满足", "未签署"]) {
    assert.doesNotMatch(source, new RegExp(internalNote));
  }
});

test("token preparation is not a public homepage module", () => {
  for (const copy of ["MOOD TOKEN · COMING SOON", "香港", "BNB Smart Chain", "Every voice deserves to be heard"] ) {
    assert.doesNotMatch(source, new RegExp(copy));
  }
});
