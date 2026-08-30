import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync(new URL("../app/token/page.tsx", import.meta.url), "utf8");
const layout = readFileSync(new URL("../app/token/layout.tsx", import.meta.url), "utf8");
const source = `${page}\n${layout}`;

test("token surface truthfully declares preparation state", () => {
  assert.match(source, /HONG KONG ISSUANCE PREPARATION/);
  assert.match(source, /BNB Smart Chain/);
  assert.match(source, /Chain ID 56/);
  assert.match(source, /尚未发行/);
  assert.match(source, /没有官方合约地址/);
});

test("token surface contains no obsolete trade claims", () => {
  assert.doesNotMatch(source, /0x1BB/i);
  assert.doesNotMatch(source, /PancakeSwap/i);
  assert.doesNotMatch(source, /33,000,000/);
  assert.doesNotMatch(source, /OFFICIAL CONTRACT/);
  assert.doesNotMatch(source, /连接钱包/);
});

test("token surface defines public genesis gates", () => {
  for (const gate of ["香港法律与发行主体", "代币参数冻结", "合约与权限安全", "Genesis 真实网络", "公开 Genesis 决议"]) {
    assert.match(source, new RegExp(gate));
  }
});
