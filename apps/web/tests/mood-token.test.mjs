/* MOOD token foundation checks — MOOD-GENESIS-001.
   Config integrity, single-source discipline, public page honesty:
   the approved contract is exact, never duplicated as a second hard-coded
   authority, never replaced with placeholder data, and the public page keeps
   its risk notice without yield/ROI promises. */

import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("..", import.meta.url);

async function read(rel) {
  return readFile(new URL(rel, root), "utf8");
}

const APPROVED_ADDRESS = "0x1BB3115D43E397f7bb586F090831B02cA639e73E";

test("mood-token config exports BSC chain id 56 with exact approved facts", async () => {
  const config = await read("lib/mood-token.ts");
  assert.match(config, /chainId:\s*56\b/, "chain id must be 56");
  assert.match(config, /network:\s*"BNB Smart Chain"/, "network must be BNB Smart Chain");
  assert.match(config, /decimals:\s*18\b/, "decimals must be 18");
  assert.match(config, /totalSupply:\s*"33000000"/, "raw total supply must be 33000000");
  assert.match(config, /33,000,000 MOOD/, "display total supply must be 33,000,000 MOOD");
  assert.match(config, new RegExp(`address:\\s*"${APPROVED_ADDRESS}"`), "contract address must be the approved address");
});

test("contract address is never placeholder or example data", async () => {
  const config = await read("lib/mood-token.ts");
  for (const forbidden of [/0x0{6,}/i, /0xdead/i, /YOUR_TOKEN/i, /EXAMPLE/i, /PLACEHOLDER/i, /0x[a-f0-9]{4}\.{3}/i, /TBD/i]) {
    assert.doesNotMatch(config, forbidden, `config must not contain placeholder marker ${forbidden}`);
  }
  const hexAddresses = config.match(/0x[0-9a-fA-F]{40}/g) ?? [];
  assert.ok(hexAddresses.length >= 1, "config must contain the approved address");
  for (const addr of hexAddresses) {
    assert.equal(addr, APPROVED_ADDRESS, "every 40-hex address in config must be the approved address");
  }
});

test("explorer and trade links point at the official contract on BSC and PancakeSwap", async () => {
  const config = await read("lib/mood-token.ts");
  assert.match(config, /explorerUrl:\s*"https:\/\/bscscan\.com\/token\/0x1BB3115D43E397f7bb586F090831B02cA639e73E"/);
  assert.match(config, /tradeUrl:\s*"https:\/\/pancakeswap\.finance\/swap\?outputCurrency=0x1BB3115D43E397f7bb586F090831B02cA639e73E"/);
});

test("/token page exists and reads facts from the single config authority", async () => {
  await access(new URL("app/token/page.tsx", root));
  const page = await read("app/token/page.tsx");
  assert.match(page, /from\s+"\.\.\/\.\.\/lib\/mood-token"/, "page must import the token config");
  assert.doesNotMatch(page, new RegExp(`"${APPROVED_ADDRESS}"`), "page must not hard-code a second contract address literal");
});

test("/token page keeps copy control with visible feedback and honest failure", async () => {
  const page = await read("app/token/page.tsx");
  assert.match(page, /navigator\.clipboard\.writeText/, "copy must use the clipboard API");
  assert.match(page, /aria-live="polite"/, "copy feedback must be announced to assistive tech");
  assert.match(page, /复制失败/, "copy failure must degrade honestly");
  assert.match(page, /word-break:\s*"break-all"|wordBreak:\s*"break-all"/, "long address must not break layout");
});

test("/token page carries external links with safe rel attributes", async () => {
  const page = await read("app/token/page.tsx");
  assert.match(page, /target="_blank"\s+rel="noopener noreferrer"/, "external links must open safely");
  // Links resolve from the config authority, not page-level literals:
  for (const ref of ["MOOD_TOKEN.explorerUrl", "MOOD_TOKEN.tradeUrl", "MOOD_TOKEN.officialSite", "MOOD_TOKEN.githubUrl"]) {
    assert.ok(page.includes(ref), `missing official link reference ${ref}`);
  }
});

test("/token page has a risk notice and never promises returns", async () => {
  const page = await read("app/token/page.tsx");
  assert.match(page, /风险提示/, "risk notice section must exist");
  for (const concept of ["新上线", "流动性可能较浅", "剧烈波动", "智能合约风险", "核实合约", "不提供任何形式的回报保证"]) {
    assert.ok(page.includes(concept), `risk notice must mention ${concept}`);
  }
  for (const banned of [/APY\b/i, /\bROI\b/i, /保证收益(?!.*无关)/, /guaranteed return/i, /guaranteed appreciation/i, /staking/i, /锁仓收益/, /年化/]) {
    assert.doesNotMatch(page, banned, `page must not contain investment-promise language: ${banned}`);
  }
});

test("/token page does not fabricate unverified chain facts", async () => {
  const page = await read("app/token/page.tsx");
  const config = await read("lib/mood-token.ts");
  const sources = page + config;
  for (const banned of [/市值/i, /market ?cap/i, /持有人数/i, /holder count/i, /poolAddress/i, /24[hH]交易量|交易量.*[0-9]/, /\$[0-9]/]) {
    assert.doesNotMatch(sources, banned, `must not fabricate unverified data: ${banned}`);
  }
});
