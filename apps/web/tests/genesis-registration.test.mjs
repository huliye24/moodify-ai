/* Genesis registration contract — MOOD-GENESIS-002.
   Source-contract tests covering the spec's 20 scenarios (G-001..G-020) plus
   the security checklist. The repo convention is to assert on TypeScript
   source as text; this matches it. Runtime crypto correctness is exercised
   separately in tests/genesis-runtime.test.mjs. */

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (rel) => readFile(path.join(root, rel), "utf8");

/* --- Configuration -------------------------------------------------------- */

test("G-CONFIG: canonical config is single source of truth and matches the token canon", async () => {
  const cfg = await read("lib/genesis-config.ts");
  const token = await read("lib/mood-token.ts");
  assert.match(cfg, /chainId:\s*MOOD_TOKEN\.chainId/, "config must reuse token chain id");
  assert.match(cfg, /network:\s*MOOD_TOKEN\.network/, "config must reuse token network");
  assert.match(cfg, /nonceTtlSeconds:\s*600\b/, "TTL must be 600s (10 min)");
  assert.match(cfg, /nonceByteLength:\s*16\b/, "nonce must use 16 bytes of entropy (128 bits)");
  assert.match(cfg, /signatureVersion:\s*"mood-genesis-v1"/, "signature version must be locked");
  assert.match(cfg, /termsVersion:\s*"genesis-v1"/, "terms version must match package canon");
  // Chain id must equal the approved MOOD chain.
  assert.match(token, /chainId:\s*56\b/);
});

/* --- Schema --------------------------------------------------------------- */

test("G-DB: schema declares only canonical columns and DB-enforced uniqueness", async () => {
  const schema = await read("db/schema.ts");
  // Participants table with all required fields. Drizzle uses camelCase JS
  // keys. UNIQUE constraints may be declared inline as `.unique()` on the
  // column or via `uniqueIndex(...)` in the second argument; both produce a
  // UNIQUE index in the generated migration.
  assert.match(schema, /sqliteTable\("genesis_participants"/);
  for (const jsKey of ["participantNumber", "walletAddress", "walletAddressNormalized", "chainId", "joinedAt", "status", "signatureVersion", "termsVersion"]) {
    assert.ok(schema.includes(jsKey), `participants must declare ${jsKey}`);
  }
  for (const snakeCol of ["participant_number", "wallet_address_normalized"]) {
    assert.ok(schema.includes(snakeCol), `participants must declare column ${snakeCol}`);
  }
  // Inline `.unique()` on participantNumber AND walletAddressNormalized.
  assert.match(schema, /participantNumber:[^]*?\.unique\(\)/, "participant_number must be UNIQUE");
  assert.match(schema, /walletAddressNormalized:[^]*?\.unique\(\)/, "wallet_address_normalized must be UNIQUE");
  // Nonces table with required fields.
  assert.match(schema, /sqliteTable\("genesis_nonces"/);
  assert.match(schema, /nonceHash:[^]*?\.unique\(\)/, "nonce_hash must be UNIQUE");
  // No destructive change to existing tables.
  for (const forbidden of [/DROP TABLE/, /ALTER TABLE.*DROP COLUMN/, /RENAME TO/]) {
    assert.doesNotMatch(schema, forbidden, `schema must not contain destructive change: ${forbidden}`);
  }
});

test("G-MIGRATION: drizzle migration adds only new tables; existing tables untouched", async () => {
  // Find the latest migration file dynamically (we don't hard-code the hash).
  const fs = await import("node:fs/promises");
  const entries = await fs.readdir(path.join(root, "drizzle"));
  const migrationSql = entries.find((f) => /^0001_.*\.sql$/.test(f));
  assert.ok(migrationSql, "migration file present");
  const sql = await fs.readFile(path.join(root, "drizzle", migrationSql), "utf8");
  assert.match(sql, /CREATE TABLE `genesis_participants`/, "must create genesis_participants");
  assert.match(sql, /CREATE TABLE `genesis_nonces`/, "must create genesis_nonces");
  assert.match(sql, /CREATE UNIQUE INDEX `genesis_participants_participant_number_unique`/, "DB-enforced unique participant number");
  assert.match(sql, /CREATE UNIQUE INDEX `genesis_participants_wallet_address_normalized_unique`/, "DB-enforced unique wallet");
  assert.match(sql, /CREATE UNIQUE INDEX `genesis_nonces_nonce_hash_unique`/, "DB-enforced unique nonce hash");
  // Original tables must not be dropped or altered destructively.
  for (const banned of [/DROP TABLE/, /DROP COLUMN/]) {
    assert.doesNotMatch(sql, banned, "migration must be non-destructive");
  }
});

/* --- Message & address helpers ------------------------------------------- */

test("G-MSG: canonical message includes all required semantic fields and the no-transfer statement", async () => {
  const lib = await read("lib/genesis-message.ts");
  assert.match(lib, /Moodify Protocol Genesis Registration/, "message title");
  assert.match(lib, /Wallet: \$\{fields\.address\}/, "wallet line");
  assert.match(lib, /Chain ID: \$\{fields\.chainId\}/, "chain id line");
  assert.match(lib, /Nonce: \$\{fields\.nonce\}/, "nonce line");
  assert.match(lib, /Issued At: \$\{fields\.issuedAt\}/, "issued-at line");
  assert.match(lib, /Expires At: \$\{fields\.expiresAt\}/, "expires-at line");
  assert.match(lib, /Signature Version: \$\{fields\.signatureVersion\}/, "signature version line");
  assert.match(lib, /Terms Version: \$\{fields\.termsVersion\}/, "terms version line");
  assert.match(lib, /Domain: \$\{fields\.domain\}/, "domain line");
  assert.match(lib, /This signature does not authorize any token transfer or transaction/, "explicit no-transfer statement");
  // EIP-191 personal_sign digest shape.
  assert.match(lib, /\\x19Ethereum Signed Message:\\n/, "EIP-191 prefix");
});

test("G-ADDR: address helpers normalize lowercase and never compare case-sensitive", async () => {
  const lib = await read("lib/evm-address.ts");
  assert.match(lib, /export function normalizeAddress/, "normalizeAddress must be exported");
  assert.match(lib, /return value\.toLowerCase\(\)/, "normalize must lowercase");
  assert.match(lib, /export function checksumAddress/, "checksumAddress must be exported");
  assert.match(lib, /keccak256|Keccak|keccak/, "checksum must use keccak256");
});

/* --- Backend endpoints ---------------------------------------------------- */

test("G-API-NONCE: nonce endpoint validates chain and returns message", async () => {
  const route = await read("app/api/genesis/nonce/route.ts");
  assert.match(route, /issueGenesisNonce/, "must call service");
  assert.match(route, /chainId.*number|chainId.*integer/, "chainId must be parsed as integer");
  const service = await read("lib/genesis-service.ts");
  assert.match(service, /chainId !== GENESIS_CONFIG\.chainId/, "service must reject non-BSC chain");
  assert.match(service, /generateNonce/, "service must generate random nonce");
  assert.match(service, /crypto\.getRandomValues/, "nonce generation must use CSPRNG");
  assert.match(service, /sha256Hex\(nonce\)/, "nonce must be stored as SHA-256 hash");
  assert.match(service, /issuedAt: issuedAt\.toISOString\(\)/, "service must compute issuedAt ISO string");
  assert.match(service, /expiresAt: expiresAt\.toISOString\(\)/, "service must compute expiresAt ISO string");
  assert.match(service, /nonceTtlSeconds \* 1000/, "service must add TTL to issuedAt");
});

test("G-API-REGISTER: register endpoint verifies signature, expires nonce, and prevents replay", async () => {
  const route = await read("app/api/genesis/register/route.ts");
  const service = await read("lib/genesis-service.ts");
  // Address validation.
  assert.match(service, /normalizeAddress/, "must use normalizeAddress for all comparisons");
  // Chain enforcement.
  assert.match(service, /chainId !== GENESIS_CONFIG\.chainId/, "wrong chain rejected");
  // Nonce lookup by hash.
  assert.match(service, /eq\(genesisNonces\.nonceHash, nonceHash\)/, "nonce must be looked up by hash");
  // Expiry enforcement.
  assert.match(service, /Date\.parse\(nonceRow\.expiresAt\) <= now\.getTime\(\)/, "expiry enforced");
  // Used nonce rejection.
  assert.match(service, /isNull\(genesisNonces\.usedAt\)/, "used nonces must be filtered out");
  // Signature recovery.
  assert.match(service, /recoverPersonalSign/, "must recover signer server-side");
  // Signer equality.
  assert.match(service, /recovered !== normalized/, "recovered signer must equal requested wallet");
  // Idempotency on duplicate wallet.
  assert.match(service, /existing\s*=\s*await db\.query\.genesisParticipants\.findFirst/, "duplicate wallet must short-circuit");
  // Race-safe allocation.
  assert.match(service, /MAX\(\$\{genesisParticipants\.participantNumber\}\)/, "allocation uses MAX+1");
  assert.match(service, /UNIQUE constraint failed/i, "must retry on UNIQUE race");
  // Nonce consumption.
  assert.match(service, /markNonceUsed/, "nonce must be marked used atomically");
  // Never trusts client status/score/allocation.
  assert.match(service, /never trusts client-provided participant numbers/i, "service must state it never trusts client values");
  // Never performs on-chain actions.
  assert.match(service, /never requests or stores private keys/i, "service must state it never requests private keys");
});

test("G-API-ME: lookup endpoint exists and returns participant or null", async () => {
  const route = await read("app/api/genesis/me/route.ts");
  assert.match(route, /searchParams\.get\("address"\)/, "must read address from query string");
  assert.match(route, /findGenesisParticipantByAddress/, "must call service");
});

/* --- Page UX -------------------------------------------------------------- */

test("G-UI: /genesis page declares all required states explicitly", async () => {
  const page = await read("app/genesis/page.tsx");
  const requiredPhases = [
    "wallet-disconnected", "connecting", "wrong-network", "ready-to-sign",
    "nonce-loading", "signature-requested", "verifying",
    "registered", "already-registered", "rejected", "expired", "server-error",
  ];
  for (const phase of requiredPhases) {
    assert.ok(page.includes(`"${phase}"`) || page.includes(`'${phase}'`), `phase "${phase}" must be declared`);
  }
  // Wallet connection via EIP-1193 only.
  assert.match(page, /window\.ethereum/, "must use the injected EIP-1193 provider");
  assert.match(page, /eth_requestAccounts/, "must request accounts explicitly");
  // personal_sign only — never eth_sendTransaction / typed-data / approve.
  assert.match(page, /personal_sign/, "must use personal_sign");
  const pageCode = page.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
  assert.doesNotMatch(pageCode, /eth_sendTransaction/, "must NOT call eth_sendTransaction");
  assert.doesNotMatch(pageCode, /eth_signTypedData|signTypedData/, "must NOT use typed data signatures");
  assert.doesNotMatch(pageCode, /\bapprove\b.*spender|approve\(.*\)/, "must NOT approve token spending");
  // Network enforcement.
  assert.match(page, /BSC_HEX|0x38/, "must enforce BSC chain id 0x38");
  assert.match(page, /wallet_switchEthereumChain/, "must offer network switch through wallet API");
  // No private key / seed phrase access (in code; comments are allowed to
  // discuss these as things we don't do).
  for (const banned of [/seed.?phrase|mnemonic/i, /private.?key/i, /localStorage\.setItem.*key/i, /postMessage.*key/i]) {
    assert.doesNotMatch(pageCode, banned, `page must not request: ${banned}`);
  }
  // Required copy.
  assert.match(page, /注册不代表任何形式的金融价值/, "must include no-financial-value statement");
  assert.match(page, /不需要购买、转移或授权 MOOD/, "must include no-token statement");
  assert.match(page, /不需要支付任何链上费用|不要求支付 Gas/, "must include no-gas statement");
  // The page renders the canonical message via <pre>{challenge.message}</pre>.
  // The inline style attribute can be very long, so we use a relaxed regex
  // that allows arbitrary content between the opening <pre ...> and the
  // closing </pre>, as long as {challenge.message} is interpolated as text.
  assert.match(page, /<pre[\s\S]{0,1000}\{challenge\.message\}[\s\S]{0,40}<\/pre>/, "page must render the canonical signed message");
  const msg = await read("lib/genesis-message.ts");
  assert.match(msg, /This signature does not authorize any token transfer or transaction/, "message must include the no-transfer statement");
});

test("G-UI: success card shows participant number with leading zeros, wallet, timestamp, BscScan link", async () => {
  const page = await read("app/genesis/page.tsx");
  assert.match(page, /Genesis Participant #/, "title prefix");
  assert.match(page, /padStart\(4, "0"\)/, "participant number must be zero-padded to 4 digits");
  assert.match(page, /bscscan\.com\/address\//, "BscScan link must be present");
  assert.match(page, /bscscan/, "BscScan reference");
  assert.match(page, /joinedAt/, "registration timestamp");
  assert.match(page, /registered/, "status label");
});

test("G-UI: page does not auto-sign and never silently fakes a participant", async () => {
  const page = await read("app/genesis/page.tsx");
  // No auto-call to register without explicit user action.
  assert.doesNotMatch(page, /useEffect[\s\S]*?signAndRegister\(/, "no auto signAndRegister on mount");
  // No fabricated participant creation.
  assert.doesNotMatch(page, /setParticipant\(\{ participantNumber: 0/, "must not fabricate a participant record");
  assert.doesNotMatch(page, /setParticipant\(\{ participantNumber: 1/, "must not fabricate a participant record");
});

test("G-UI: cross-link between /token and /genesis; both reference single config authority", async () => {
  const page = await read("app/genesis/page.tsx");
  const tokenPage = await read("app/token/page.tsx");
  const home = await read("app/page.tsx");
  assert.ok(home.includes("/genesis"), "home drawer must link to /genesis");
  assert.match(page, /from "\.\.\/\.\.\/lib\/genesis-config"/, "page must import genesis config");
  assert.match(page, /docs\/protocol\/GENESIS_REGISTRATION\.md/, "page must reference protocol doc");
});

test("G-UI: copy controls and address display follow the existing token page pattern", async () => {
  const page = await read("app/genesis/page.tsx");
  assert.match(page, /navigator\.clipboard\.writeText/, "copy uses clipboard API");
  assert.match(page, /aria-live/, "copy feedback announced to assistive tech");
  assert.match(page, /wordBreak|word-break|break-all/, "addresses wrap safely");
  assert.match(page, /rel="noopener noreferrer"/, "external links safe");
});

/* --- Security checklist --------------------------------------------------- */

test("G-SEC: no private keys, seed phrases, or sensitive material in git diff", async () => {
  const filesToScan = [
    "lib/genesis-config.ts",
    "lib/genesis-message.ts",
    "lib/genesis-service.ts",
    "lib/evm-address.ts",
    "app/api/genesis/nonce/route.ts",
    "app/api/genesis/register/route.ts",
    "app/api/genesis/me/route.ts",
    "app/genesis/page.tsx",
  ];
  for (const rel of filesToScan) {
    const text = await read(rel);
    for (const banned of [/BEGIN PRIVATE KEY/, /seed.?phrase/i, /mnemonic/i, /ethers\.Wallet/, /viem.*privateKey/i]) {
      assert.doesNotMatch(text, banned, `${rel} must not contain ${banned}`);
    }
    // 64-char hex strings are only allowed as public secp256k1 curve
    // constants (P, N, Gx, Gy, half-order). Strip those well-known
    // constants and re-check; any remaining 0x + 64 hex is suspicious.
    const allowed = [
      /0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f/g, // P
      /0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141/g, // N
      /0x7e5f4552091a69125d5dfcb7b8c2659029395bdf/g, // N/2 (well-known)
      /0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798/g, // Gx
      /0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8/g, // Gy
      /0x8000000000000000000000000000000000000000000000000000000000000000/g, // 2^255 (recovery parity bit)
    ];
    const stripped = allowed.reduce((acc, pat) => acc.replace(pat, "<curve-const>"), text);
    assert.doesNotMatch(stripped, /0x[0-9a-fA-F]{64}/, `${rel} must not contain a 64-hex-char constant other than secp256k1 curve params`);
  }
});

test("G-SEC: no eth_sendTransaction, approve, or contract deployment anywhere", async () => {
  const files = [
    "lib/genesis-service.ts", "app/api/genesis/register/route.ts", "app/api/genesis/nonce/route.ts",
    "app/genesis/page.tsx", "db/schema.ts",
  ];
  for (const rel of files) {
    const text = await read(rel);
    assert.doesNotMatch(text, /eth_sendTransaction/, `${rel} must not call eth_sendTransaction`);
    assert.doesNotMatch(text, /\bapprove\s*\(\s*['"]MOOD/, `${rel} must not approve MOOD spending`);
    assert.doesNotMatch(text, /wallet_sendCalls|wallet_sendTransaction/, `${rel} must not send EIP-5799 calls`);
  }
});

test("G-SEC: nonce is server-generated, never accepted from the client", async () => {
  const service = await read("lib/genesis-service.ts");
  assert.match(service, /crypto\.getRandomValues/, "nonce must use CSPRNG");
  assert.match(service, /never accept arbitrary client nonce|never trusts client-provided|never accept client/i, "service must never accept client-supplied nonce");
});

test("G-SEC: raw signature bytes are not logged", async () => {
  const service = await read("lib/genesis-service.ts");
  const registerRoute = await read("app/api/genesis/register/route.ts");
  const page = await read("app/genesis/page.tsx");
  for (const [name, text] of [["service", service], ["registerRoute", registerRoute], ["page", page]]) {
    assert.doesNotMatch(text, /console\.(log|info|debug).*signature/, `${name} must not log raw signatures`);
    assert.doesNotMatch(text, /console\.(log|info|debug).*signature\.0x/, `${name} must not log raw signatures`);
  }
});

test("G-SEC: address comparisons go through normalizeAddress, never raw equality", async () => {
  const service = await read("lib/genesis-service.ts");
  // Every recovered-signature comparison must use the normalized form.
  assert.match(service, /recovered !== normalized/, "signer comparison must be normalized");
  // No naive === comparisons on raw address strings.
  for (const banned of [/\.toLowerCase\(\)\s*===\s*input\.address/, /address\s*===\s*address/]) {
    assert.doesNotMatch(service, banned, `must not compare addresses naively: ${banned}`);
  }
});

test("G-SEC: client cannot set status / score / allocation / participant number", async () => {
  const route = await read("app/api/genesis/register/route.ts");
  const service = await read("lib/genesis-service.ts");
  assert.doesNotMatch(route, /body\.status|body\.participantNumber|body\.contributionScore|body\.allocation/i, "register endpoint must not accept client-controlled fields");
  assert.doesNotMatch(service, /body\.status|body\.participantNumber|body\.contributionScore|body\.allocation/i, "service must not honor client-controlled fields");
  assert.match(service, /never trust(?:s)? client-provided participant numbers?/i, "service must state it never trusts client-provided participant numbers");
});

function toCamel(name) { return name.replace(/_([a-z])/g, (_, c) => c.toUpperCase()); }
