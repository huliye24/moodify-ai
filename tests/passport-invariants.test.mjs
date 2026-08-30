// MOOD PASSPORT 015 — Identity / Passport invariants
// Validates INV-015-01 .. INV-015-12 against the REAL implementation
// (apps/web/lib/mood/passport/*.ts), imported via Node type stripping.
//
// Usage: node tests/passport-invariants.test.mjs
//
// Authority: MOOD-PASSPORT-015 TASK.md Phase R.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { ResidentRegistry } from "../apps/web/lib/mood/passport/resident-registry.ts";
import { NonceRegistry } from "../apps/web/lib/mood/passport/nonce.ts";
import { Passport } from "../apps/web/lib/mood/passport/passport.ts";
import {
  generateResidentId,
  isValidResidentId,
  truncateWalletAddress,
} from "../apps/web/lib/mood/passport/resident-id.ts";
import { derivePublicProfile } from "../apps/web/lib/mood/passport/public-profile.ts";
import { assertSignedBy, verifySignatureFormat } from "../apps/web/lib/mood/passport/signature.ts";
import { buildSiweMessage, renderSiweMessage } from "../apps/web/lib/mood/passport/siwe.ts";
import {
  FAKE_RECOVER_FOR_TEST,
  registerDevSignature,
  resetDevSignatures,
} from "../apps/web/lib/mood/passport/test-recover.ts";

const TEST_ADDR_A = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const TEST_ADDR_B = "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

// A well-formed (shape-valid) 65-byte signature for format tests.
const SHAPE_VALID_SIG =
  "0x" + "ab".repeat(64) + "1c"; // v = 0x1c = 28

const PASSPORT_LIB_DIR = join(
  dirname(fileURLToPath(import.meta.url)),
  "../apps/web/lib/mood/passport",
);

// ─── INV-015-01 ───────────────────────────────────────────────────────────────

test("INV-015-01: Resident can be created/resolved with no Token config", () => {
  const reg = new ResidentRegistry();
  // No env, no token config, no chain library involved.
  const first = reg.resolveOrCreateByWallet(TEST_ADDR_A);
  assert.equal(first.created, true);
  assert.equal(isValidResidentId(first.resident.id), true);

  // Repeat login resolves the same resident, does not duplicate.
  const second = reg.resolveOrCreateByWallet(TEST_ADDR_A);
  assert.equal(second.created, false);
  assert.equal(second.resident.id, first.resident.id);
  assert.equal(reg.residentCount(), 1);
});

test("INV-015-01b: passport lib never imports token/chain FREEZE modules", () => {
  const files = readdirSync(PASSPORT_LIB_DIR).filter((f) => f.endsWith(".ts"));
  assert.ok(files.length > 0);
  for (const f of files) {
    const src = readFileSync(join(PASSPORT_LIB_DIR, f), "utf8");
    // Check actual import specifiers (not prose in comments).
    const importMatches = src.matchAll(
      /from\s+["']([^"']+)["']/g,
    );
    for (const m of importMatches) {
      const spec = m[1];
      assert.equal(
        /mood-(token|chain)/.test(spec),
        false,
        `${f} must not import ${spec}`,
      );
    }
  }
});

// ─── INV-015-02 ───────────────────────────────────────────────────────────────

test("INV-015-02: nonce is single-use", () => {
  const reg = new NonceRegistry();
  const { nonce } = reg.issue(TEST_ADDR_A);
  const first = reg.consume(nonce, TEST_ADDR_A);
  assert.deepEqual(first, { ok: true });
  const second = reg.consume(nonce, TEST_ADDR_A);
  assert.equal(second.ok, false);
  assert.equal(second.reason, "already-used");
});

// ─── INV-015-03 ───────────────────────────────────────────────────────────────

test("INV-015-03: expired nonce is rejected", () => {
  let now = 1_000_000;
  const reg = new NonceRegistry({ ttlMs: 60_000, now: () => now });
  const { nonce } = reg.issue(TEST_ADDR_A);
  now += 61_000; // advance past expiry
  const result = reg.consume(nonce, TEST_ADDR_A);
  assert.equal(result.ok, false);
  assert.equal(result.reason, "expired");
});

// ─── INV-015-04 ───────────────────────────────────────────────────────────────

test("INV-015-04: wrong signature is rejected (fail closed)", () => {
  // 4a) Shape-invalid signatures are rejected outright.
  for (const bad of ["", "0x1234", "xyz", "0x" + "gg".repeat(65)]) {
    const r = verifySignatureFormat(bad);
    assert.equal(r.valid, false, `expected invalid: ${bad}`);
  }

  // 4b) Shape-valid but not signed by the claimed address → recovery fails.
  const msg = buildSiweMessage({
    domain: "mood.test",
    address: TEST_ADDR_A,
    nonce: "a".repeat(16),
    chainId: 56,
    uri: "https://mood.test/portal/passport",
  });
  const text = renderSiweMessage(msg);
  const result = assertSignedBy({
    signedMessageText: text,
    signature: SHAPE_VALID_SIG,
    expectedAddress: TEST_ADDR_A,
    recoverAddress: () => null, // no valid recovery → fail closed
  });
  assert.equal(result.valid, false);

  // 4c) Signature recovering to a DIFFERENT address than the message claims.
  const cross = assertSignedBy({
    signedMessageText: text,
    signature: SHAPE_VALID_SIG,
    expectedAddress: TEST_ADDR_A,
    recoverAddress: () => TEST_ADDR_B, // forged recovery
  });
  assert.equal(cross.valid, false);
});

// ─── INV-015-05 ───────────────────────────────────────────────────────────────

test("INV-015-05: signature cannot be replayed across addresses", () => {
  const msgA = buildSiweMessage({
    domain: "mood.test",
    address: TEST_ADDR_A,
    nonce: "b".repeat(16),
    chainId: 56,
    uri: "https://mood.test/portal/passport",
  });
  const textA = renderSiweMessage(msgA);

  // Attacker B takes A's signature and claims it as their own.
  const result = assertSignedBy({
    signedMessageText: textA,
    signature: SHAPE_VALID_SIG,
    expectedAddress: TEST_ADDR_B, // B claims the signature
    recoverAddress: () => TEST_ADDR_A, // but it really recovers to A
  });
  assert.equal(result.valid, false);
});

// ─── INV-015-06 ───────────────────────────────────────────────────────────────

test("INV-015-06: session has expiry and expires", () => {
  const reg = new ResidentRegistry();
  const { resident } = reg.resolveOrCreateByWallet(TEST_ADDR_A);

  const live = reg.issueSession({
    residentId: resident.id,
    walletAddress: TEST_ADDR_A,
    ttlMs: 60_000,
  });
  assert.equal(live.ok, true);
  assert.ok(reg.getSession(live.session.id));

  const stale = reg.issueSession({
    residentId: resident.id,
    walletAddress: TEST_ADDR_A,
    ttlMs: -1, // already expired at issue time
  });
  assert.equal(stale.ok, true);
  assert.equal(reg.getSession(stale.session.id), null);
});

// ─── INV-015-07 ───────────────────────────────────────────────────────────────

test("INV-015-07: Passport never shows a fabricated reputation", () => {
  const reg = new ResidentRegistry();
  const { resident } = reg.resolveOrCreateByWallet(TEST_ADDR_A);
  const rep = reg.getReputation(resident.id) ?? reg.emptyReputation(resident.id);
  assert.equal(rep.score, null);
  assert.equal(rep.contributionCount, 0);
  assert.equal(rep.source, "no-contributions-yet");
});

// ─── INV-015-08 ───────────────────────────────────────────────────────────────

test("INV-015-08: public profile does not leak private fields", () => {
  const reg = new ResidentRegistry();
  const { resident } = reg.resolveOrCreateByWallet(TEST_ADDR_A);
  reg.updateProfile(resident.id, { displayName: "Ada" });
  reg.addSelfDeclaredRole(resident.id, "creator");

  const privacy = reg.getPrivacy(resident.id);

  // Public derivation includes only allowed fields.
  const pub = derivePublicProfile({
    resident,
    selfDeclaredRoles: reg.listSelfDeclaredRoles(resident.id),
    verifiedRoles: [],
    badges: [],
    reputation: null,
    contributionCount: 0,
    displayName: reg.getProfile(resident.id).displayName,
    privacy,
  });
  assert.ok(pub);
  const serialized = JSON.stringify(pub);
  assert.equal(serialized.includes(TEST_ADDR_A), false, "no full wallet address");
  assert.equal(serialized.includes("wallet"), false, "no wallet objects");
  assert.equal(serialized.includes("consent"), false, "no consent records");
  assert.equal(serialized.includes("session"), false, "no session records");

  // Private visibility → nothing at all.
  reg.updatePrivacy(resident.id, { profileVisibility: "private" });
  const hidden = derivePublicProfile({
    resident,
    selfDeclaredRoles: [],
    verifiedRoles: [],
    badges: [],
    reputation: null,
    contributionCount: 0,
    displayName: null,
    privacy: reg.getPrivacy(resident.id),
  });
  assert.equal(hidden, null);
});

// ─── INV-015-09 ───────────────────────────────────────────────────────────────

test("INV-015-09: draft policy is not recorded as active consent", () => {
  const reg = new ResidentRegistry();
  const { resident } = reg.resolveOrCreateByWallet(TEST_ADDR_A);

  const draft = reg.recordConsent(resident.id, "privacy-policy", "0.1", "draft");
  assert.equal(draft.ok, false);
  assert.equal(draft.reason, "policy-not-active");
  assert.equal(reg.listConsents(resident.id).length, 0);

  const active = reg.recordConsent(resident.id, "privacy-policy", "1.0", "active");
  assert.equal(active.ok, true);
});

// ─── INV-015-10 ───────────────────────────────────────────────────────────────

test("INV-015-10: token holding does not affect Resident creation", () => {
  // ResidentRegistry has no token-balance input at all; creation is purely
  // wallet-signature based. Simulate "zero balance" and "rich" wallets —
  // both must yield identical (normal) residents.
  const reg = new ResidentRegistry();
  const zeroBalance = reg.resolveOrCreateByWallet(TEST_ADDR_A);
  const rich = reg.resolveOrCreateByWallet(TEST_ADDR_B);
  assert.equal(zeroBalance.resident.status, "active");
  assert.equal(rich.resident.status, "active");
  assert.equal(isValidResidentId(zeroBalance.resident.id), true);
  assert.equal(isValidResidentId(rich.resident.id), true);
});

// ─── INV-015-11 ───────────────────────────────────────────────────────────────

test("INV-015-11: verified badge cannot be self-issued", () => {
  const reg = new ResidentRegistry();
  const { resident } = reg.resolveOrCreateByWallet(TEST_ADDR_A);

  // Self-declaration API rejects verified roles outright.
  const bad = reg.addSelfDeclaredRole(resident.id, "verified-contributor");
  assert.equal(bad.ok, false);
  assert.equal(bad.reason, "invalid-role");

  // Verified roles require an authority-provided source.
  const noSource = reg.awardVerifiedRole(resident.id, "verified-contributor", "");
  assert.equal(noSource.ok, false);
  assert.equal(noSource.reason, "missing-or-invalid-source");

  // After self-declaring the non-verified variant, verified list stays empty.
  reg.addSelfDeclaredRole(resident.id, "creator");
  assert.deepEqual(reg.listVerifiedRoles(resident.id), []);
});

// ─── INV-015-12 ───────────────────────────────────────────────────────────────

test("INV-015-12: full sign-in flow works in foundation state (no token config)", () => {
  resetDevSignatures();
  const nonceReg = new NonceRegistry();
  const residentReg = new ResidentRegistry();
  const passport = new Passport({
    nonceRegistry: nonceReg,
    residentRegistry: residentReg,
    recoverAddress: FAKE_RECOVER_FOR_TEST,
    domain: "mood.test",
    uri: "https://mood.test/portal/passport",
    chainId: 56,
  });

  // 1) Request sign-in: nonce + SIWE message.
  const step1 = passport.requestSignIn({ walletAddress: TEST_ADDR_A });
  assert.equal(step1.ok, true);
  assert.ok(step1.messageText.includes("mood.test wants you to sign in"));
  assert.ok(step1.messageText.includes("Nonce: "));

  // 2) Wallet signs (simulated by registering the dev signature table entry).
  registerDevSignature({
    messageText: step1.messageText,
    signature: SHAPE_VALID_SIG,
    recoveredAddress: TEST_ADDR_A,
  });

  // 3) Complete sign-in.
  const step3 = passport.completeSignIn({
    messageText: step1.messageText,
    signature: SHAPE_VALID_SIG,
  });
  assert.equal(step3.ok, true, `reason: ${step3.reason}`);
  assert.ok(step3.sessionId);
  assert.equal(step3.isNew, true);
  assert.equal(isValidResidentId(step3.residentId), true);

  // 4) The issued session resolves to the resident.
  const session = residentReg.getSession(step3.sessionId);
  assert.equal(session.residentId, step3.residentId);

  // 5) Replay of the same message+signature fails (nonce consumed).
  const replay = passport.completeSignIn({
    messageText: step1.messageText,
    signature: SHAPE_VALID_SIG,
  });
  assert.equal(replay.ok, false);
  assert.ok(replay.reason.startsWith("nonce-"), `reason: ${replay.reason}`);

  // 6) Repeat sign-in resolves (not creates) the same resident.
  const again1 = passport.requestSignIn({ walletAddress: TEST_ADDR_A });
  registerDevSignature({
    messageText: again1.messageText,
    signature: SHAPE_VALID_SIG,
    recoveredAddress: TEST_ADDR_A,
  });
  const again3 = passport.completeSignIn({
    messageText: again1.messageText,
    signature: SHAPE_VALID_SIG,
  });
  assert.equal(again3.ok, true);
  assert.equal(again3.isNew, false);
  assert.equal(again3.residentId, step3.residentId);

  // 7) Logout revokes the session.
  assert.equal(passport.revokeSession(step3.sessionId), true);
  assert.equal(residentReg.getSession(step3.sessionId), null);
  resetDevSignatures();
});

// ─── Supporting sanity ─────────────────────────────────────────────────────────

test("Resident ID scheme: short, non-sequential, not a wallet address", () => {
  const seen = new Set();
  for (let i = 0; i < 2_000; i++) {
    const id = generateResidentId();
    assert.equal(id.length, 7);
    assert.equal(id.startsWith("M"), true);
    assert.equal(id.startsWith("0x"), false);
    assert.equal(isValidResidentId(id), true);
    seen.add(id);
  }
  // 2k draws from 32^6 (~1.07B) space: collision probability ≈ 0.2%.
  assert.equal(seen.size, 2_000);
});

test("Wallet address display truncation hides the full address by default", () => {
  const t = truncateWalletAddress(TEST_ADDR_A);
  assert.ok(t.length < TEST_ADDR_A.length);
  assert.equal(t.includes(TEST_ADDR_A.slice(2, 38)), false);
});
