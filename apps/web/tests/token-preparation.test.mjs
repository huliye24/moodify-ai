import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync(new URL("../app/token/page.tsx", import.meta.url), "utf8");
const layout = readFileSync(new URL("../app/token/layout.tsx", import.meta.url), "utf8");
const source = `${page}\n${layout}`;

test("token surface truthfully declares preparation state in public language", () => {
  assert.match(source, /香港/);
  assert.match(source, /BNB Smart Chain/);
  assert.match(source, /尚未开放购买/);
  assert.match(source, /没有官方合约地址/);
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
