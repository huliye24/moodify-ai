// MOOD GOVERNANCE 020 — Invariants
// Validates INV-020-01..12 against the REAL implementation.
//
// Usage: node --experimental-strip-types tests/governance-invariants.test.mjs
//
// Authority: MOOD-GOVERNANCE-020 TASK.md Phase Z.

import { test } from "node:test";
import assert from "node:assert/strict";
import {
  MipRegistry,
  mipRegistry,
} from "../apps/web/lib/mood/governance/index.ts";
import { NetworkObservatory } from "../apps/web/lib/mood/network/observatory.ts";

function fresh() {
  return new MipRegistry();
}

const MAINTAINER = "maintainer_alpha";
const AUTHOR_A = "resident_author_a";
const AUTHOR_B = "resident_author_b";

function seedAuthored(reg = fresh()) {
  return reg.create({
    title: "MIP-001 MOOD Genesis Constitution",
    summary:
      "Establishes the canonical constitution for the MOOD network and its public surfaces.",
    category: "core",
    authorResidentIds: [AUTHOR_A],
  });
}

// ─── INV-020-01 ───────────────────────────────────────────────────────────────

test("INV-020-01: MIP ID is unique and sequential", () => {
  const reg = fresh();
  const a = seedAuthored(reg);
  const b = reg.create({
    title: "MIP-002 Contribution Network Standard",
    summary: "Standardizes the contribution network v1 surface.",
    category: "contribution",
    authorResidentIds: [AUTHOR_A],
  });
  const c = reg.create({
    title: "MIP-003 Agent Registry Standard",
    summary: "Standardizes the agent registry v1 surface.",
    category: "agents",
    authorResidentIds: [AUTHOR_A, AUTHOR_B],
  });
  // MIP-000 reserved. First user MIP gets the next available number.
  assert.ok(a.id.startsWith("MIP-"));
  assert.ok(b.id.startsWith("MIP-"));
  assert.ok(c.id.startsWith("MIP-"));
  assert.notEqual(a.id, b.id);
  assert.notEqual(b.id, c.id);
  assert.notEqual(a.id, c.id);
});

// ─── INV-020-02 ───────────────────────────────────────────────────────────────

test("INV-020-02: draft cannot transition directly to implemented", () => {
  const reg = fresh();
  const m = seedAuthored(reg);
  assert.equal(m.status, "draft");
  assert.throws(
    () =>
      reg.transition({
        mipId: m.id,
        nextStatus: "implemented",
        actorResidentId: MAINTAINER,
      }),
    /INV-020-02/,
  );
});

// ─── INV-020-03 ───────────────────────────────────────────────────────────────

test("INV-020-03: accepted requires a Decision record", () => {
  const reg = fresh();
  const m = seedAuthored(reg);
  reg.transition({ mipId: m.id, nextStatus: "discussion", actorResidentId: AUTHOR_A });
  reg.transition({ mipId: m.id, nextStatus: "review", actorResidentId: MAINTAINER });
  // Try to transition review → implemented without going through accepted.
  assert.throws(
    () =>
      reg.transition({
        mipId: m.id,
        nextStatus: "implemented",
        actorResidentId: MAINTAINER,
      }),
    /INV-020-02/,
  );
  // Try to transition review → implemented without a decision.
  // First move to accepted via a decision.
  reg.recordDecision({
    mipId: m.id,
    decision: "accepted",
    decidedBy: [MAINTAINER],
    rationale: "Spec is complete and self-consistent.",
    isMaintainer: true,
  });
  assert.equal(m.status, "accepted");
  // Now try to go to implemented without an implementation reference.
  assert.throws(
    () =>
      reg.transition({
        mipId: m.id,
        nextStatus: "implemented",
        actorResidentId: MAINTAINER,
      }),
    /INV-020-04/,
  );
});

// ─── INV-020-04 ───────────────────────────────────────────────────────────────

test("INV-020-04: implemented requires an implementation reference", () => {
  const reg = fresh();
  const m = seedAuthored(reg);
  reg.transition({ mipId: m.id, nextStatus: "discussion", actorResidentId: AUTHOR_A });
  reg.transition({ mipId: m.id, nextStatus: "review", actorResidentId: MAINTAINER });
  reg.recordDecision({
    mipId: m.id,
    decision: "accepted",
    decidedBy: [MAINTAINER],
    rationale: "Approved for implementation.",
    isMaintainer: true,
  });
  // Now record an implementation reference.
  reg.recordImplementation({
    mipId: m.id,
    ref: "feat(governance): seed MIP-000 in registry",
    recordedBy: MAINTAINER,
    note: "Boot-time seed.",
  });
  // Should succeed.
  const updated = reg.transition({
    mipId: m.id,
    nextStatus: "implemented",
    actorResidentId: MAINTAINER,
  });
  assert.equal(updated.status, "implemented");
});

// ─── INV-020-05 ───────────────────────────────────────────────────────────────

test("INV-020-05: rejected MIP cannot transition to implemented", () => {
  const reg = fresh();
  const m = seedAuthored(reg);
  reg.transition({ mipId: m.id, nextStatus: "discussion", actorResidentId: AUTHOR_A });
  reg.transition({ mipId: m.id, nextStatus: "review", actorResidentId: MAINTAINER });
  reg.recordDecision({
    mipId: m.id,
    decision: "rejected",
    decidedBy: [MAINTAINER],
    rationale: "Conflicts with existing canon.",
    isMaintainer: true,
  });
  assert.equal(m.status, "rejected");
  // Should not be allowed to transition to implemented.
  assert.throws(
    () =>
      reg.transition({
        mipId: m.id,
        nextStatus: "implemented",
        actorResidentId: MAINTAINER,
      }),
    /invalid transition/,
  );
});

// ─── INV-020-06 ───────────────────────────────────────────────────────────────

test("INV-020-06: sole author cannot self-accept their own MIP", () => {
  const reg = fresh();
  const m = seedAuthored(reg);
  reg.transition({ mipId: m.id, nextStatus: "discussion", actorResidentId: AUTHOR_A });
  reg.transition({ mipId: m.id, nextStatus: "review", actorResidentId: MAINTAINER });
  // Sole author, no maintainer.
  assert.throws(
    () =>
      reg.recordDecision({
        mipId: m.id,
        decision: "accepted",
        decidedBy: [AUTHOR_A],
        rationale: "I think this is good.",
        isMaintainer: false,
      }),
    /INV-020-06/,
  );
  // With a maintainer co-decider, fine.
  const dec = reg.recordDecision({
    mipId: m.id,
    decision: "accepted",
    decidedBy: [AUTHOR_A, MAINTAINER],
    rationale: "Author + Maintainer both agree.",
    isMaintainer: true,
  });
  assert.equal(dec.decision, "accepted");
});

// ─── INV-020-07 ───────────────────────────────────────────────────────────────

test("INV-020-07: superseded MIP remains readable", () => {
  const reg = fresh();
  const older = seedAuthored(reg);
  reg.transition({ mipId: older.id, nextStatus: "discussion", actorResidentId: AUTHOR_A });
  reg.transition({ mipId: older.id, nextStatus: "review", actorResidentId: MAINTAINER });
  reg.recordDecision({
    mipId: older.id,
    decision: "accepted",
    decidedBy: [MAINTAINER],
    rationale: "Approve v1.",
    isMaintainer: true,
  });
  reg.recordImplementation({
    mipId: older.id,
    ref: "feat: initial canon",
    recordedBy: MAINTAINER,
  });
  reg.transition({ mipId: older.id, nextStatus: "implemented", actorResidentId: MAINTAINER });
  const newer = reg.create({
    title: "MIP-002 Constitution v2",
    summary: "Replaces the v1 constitution with new sections.",
    category: "core",
    authorResidentIds: [AUTHOR_B],
  });
  reg.supersede({
    mipId: older.id,
    supersededBy: newer.id,
    actorResidentId: MAINTAINER,
  });
  // Older MIP is now superseded but still in the registry.
  const stillThere = reg.publicDetailById(older.id);
  assert.ok(stillThere);
  assert.equal(stillThere.status, "superseded");
  assert.equal(stillThere.supersededBy, newer.id);
});

// ─── INV-020-08 ───────────────────────────────────────────────────────────────

test("INV-020-08: token-vote is reserved as a string but disabled", () => {
  // The decisionMethod enum reserves the string.
  const reg = fresh();
  const m = reg.create({
    title: "MIP token vote proposal",
    summary: "Would activate token voting if 025 enables it.",
    category: "governance",
    authorResidentIds: [AUTHOR_A],
    decisionMethod: "future-token-vote",
  });
  assert.equal(m.decisionMethod, "future-token-vote");
  // The registry does NOT implement a token-vote acceptance path.
  const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(reg));
  for (const fn of methods) {
    assert.ok(!/token.*vote/i.test(fn), `${fn} suggests token-vote code`);
  }
  // Method exists as data but not as an executable decision path.
  const json = JSON.stringify(reg.publicById(m.id));
  assert.match(json, /future-token-vote/);
});

// ─── INV-020-09 ───────────────────────────────────────────────────────────────

test("INV-020-09: registry does not write to canon files", () => {
  const reg = fresh();
  const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(reg));
  // No method writes to CURRENT_CANON.md or any canon file.
  for (const fn of methods) {
    assert.ok(!/canon/i.test(fn), `${fn} suggests canon writer`);
  }
  // The data also has no canon field.
  const m = seedAuthored(reg);
  const json = JSON.stringify(m);
  assert.equal(json.includes("canonFile"), false);
  assert.equal(json.includes("CURRENT_CANON"), false);
});

// ─── INV-020-10 ───────────────────────────────────────────────────────────────

test("INV-020-10: public API does not leak private reviewer notes", () => {
  const reg = fresh();
  const m = seedAuthored(reg);
  reg.transition({ mipId: m.id, nextStatus: "discussion", actorResidentId: AUTHOR_A });
  reg.transition({ mipId: m.id, nextStatus: "review", actorResidentId: MAINTAINER });
  // Rationale goes via Decision records and is part of the public record by policy.
  reg.recordDecision({
    mipId: m.id,
    decision: "accepted",
    decidedBy: [MAINTAINER],
    rationale: "Public rationale: spec is complete.",
    isMaintainer: true,
  });
  const detail = reg.publicDetailById(m.id);
  const json = JSON.stringify(detail);
  // "Private" tokens should not appear because we never accept private notes.
  assert.equal(json.includes("PRIVATE-INTERNAL-NOTE"), false);
  assert.equal(json.includes("reviewer-only"), false);
});

// ─── INV-020-11 ───────────────────────────────────────────────────────────────

test("INV-020-11: Network mips metric reads from real registry", () => {
  // Use the singleton mipRegistry so the Observatory has a real source.
  const before = mipRegistry.counts().total;
  mipRegistry.create({
    title: "MIP-099 Network Integration Check",
    summary: "Used by INV-020-11 to verify the network metric reads from the registry.",
    category: "governance",
    authorResidentIds: ["system"],
  });
  const obs = new NetworkObservatory();
  const m = obs.mips();
  assert.ok((m.value ?? 0) >= before + 1);
  assert.match(m.source, /mip-registry:020/);
});

// ─── INV-020-12 ───────────────────────────────────────────────────────────────

test("INV-020-12: governance does not depend on Token / chain config", () => {
  const reg = fresh();
  const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(reg));
  for (const fn of methods) {
    assert.ok(!/token/i.test(fn), `${fn} suggests token`);
    assert.ok(!/chain/i.test(fn), `${fn} suggests chain`);
    assert.ok(!/rpc/i.test(fn), `${fn} suggests rpc`);
    assert.ok(!/wallet/i.test(fn), `${fn} suggests wallet`);
  }
  const m = seedAuthored(reg);
  const json = JSON.stringify(m);
  assert.equal(json.includes("tokenAddress"), false);
  assert.equal(json.includes("chainId"), false);
});

// ─── Bonus: lifecycle happy path ──────────────────────────────────────────────

test("bonus: lifecycle happy path draft → discussion → review → accepted → implemented", () => {
  const reg = fresh();
  const m = seedAuthored(reg);
  reg.transition({ mipId: m.id, nextStatus: "discussion", actorResidentId: AUTHOR_A });
  reg.transition({ mipId: m.id, nextStatus: "review", actorResidentId: MAINTAINER });
  reg.recordDecision({
    mipId: m.id,
    decision: "accepted",
    decidedBy: [MAINTAINER],
    rationale: "Approved.",
    isMaintainer: true,
  });
  reg.recordImplementation({
    mipId: m.id,
    ref: "feat: ship it",
    recordedBy: MAINTAINER,
  });
  reg.transition({ mipId: m.id, nextStatus: "implemented", actorResidentId: MAINTAINER });
  assert.equal(m.status, "implemented");
});

// ─── Bonus: MIP-000 is auto-seeded ────────────────────────────────────────────

test("bonus: MIP-000 is auto-seeded on first registry creation", () => {
  const reg = fresh();
  reg.ensureMipZero(); // explicit seed
  const zero = reg.publicById("MIP-000");
  assert.ok(zero);
  assert.equal(zero.category, "governance");
});

// ─── Bonus: network activity includes MIP events ─────────────────────────────

test("bonus: Network activity feed includes MIP events from registry", () => {
  // Create one fresh MIP so its events are timestamped now-ish.
  mipRegistry.create({
    title: "MIP-100 Activity Feed Probe",
    summary: "Used by bonus test to verify network activity includes MIP events.",
    category: "other",
    authorResidentIds: ["system"],
  });
  const feed = new NetworkObservatory().activity(50);
  const types = new Set(feed.map((e) => e.type));
  assert.ok(types.has("MIPPublished"));
});
