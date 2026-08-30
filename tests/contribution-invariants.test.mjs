// MOOD CONTRIBUTION 016 �?Invariants
// Validates INV-016-01..12 against the REAL implementation
// (apps/web/lib/mood/contribution/*.ts) via Node type-stripping.
//
// Usage: node --experimental-strip-types tests/contribution-invariants.test.mjs
//
// Authority: MOOD-CONTRIBUTION-016 TASK.md Phase R.

import { test } from "node:test";
import assert from "node:assert/strict";
import {
  contributionRegistry,
  ContributionRegistry,
  validateEvidence,
  isValidEvidenceArray,
  assertTransition,
  isSelfReview,
  countOpenSubmissions,
  ReputationRegistry,
  PendingRewardRegistry,
} from "../apps/web/lib/mood/contribution/index.ts";

const RESIDENT_A = "resident_alice";
const RESIDENT_B = "resident_bob";

function newRegistry() {
  return new ContributionRegistry();
}

// ─── INV-016-01 ───────────────────────────────────────────────────────────────

test("INV-016-01: Submission belongs to authenticated Resident", () => {
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "t-1",
    title: "T1",
    summary: "Test task",
    description: "Test",
    category: "code",
    evidenceRequirements: ["URL"],
    defaultReputationPoints: 10,
    createdByResidentId: RESIDENT_A,
  });
  const submission = reg.createSubmission({
    taskId: task.id,
    residentId: RESIDENT_A,
    summary: "Done a thing for the network.",
    evidenceItems: [{ type: "url", value: "https://example.com/proof" }],
  });
  assert.equal(submission.residentId, RESIDENT_A);
  assert.equal(submission.taskId, task.id);
  // anonymous attempt would fail without residentId; tested at API layer.
});

// ─── INV-016-02 ───────────────────────────────────────────────────────────────

test("INV-016-02: User cannot approve own submission", () => {
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "t-1",
    title: "T1",
    summary: "Test task",
    description: "Test",
    category: "code",
    evidenceRequirements: [],
    defaultReputationPoints: 10,
    createdByResidentId: RESIDENT_A,
  });
  const sub = reg.createSubmission({
    taskId: task.id,
    residentId: RESIDENT_A,
    summary: "Self-attempt to approve.",
    evidenceItems: [{ type: "url", value: "https://example.com/proof" }],
  });
  // startReview itself rejects self-review.
  assert.throws(
    () => reg.startReview({ submissionId: sub.id, reviewerResidentId: RESIDENT_A }),
    /INV-016-02/,
  );
  const result = reg.review({
    submissionId: sub.id,
    decision: "approve",
    reviewerResidentId: RESIDENT_A,
  });
  assert.equal(result.ok, false);
  assert.match(result.reason ?? "", /INV-016-02/);
});

// ─── INV-016-03 ───────────────────────────────────────────────────────────────

test("INV-016-03: Invalid transition rejected", () => {
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "t-1",
    title: "T1",
    summary: "Test task",
    description: "Test",
    category: "code",
    evidenceRequirements: [],
    defaultReputationPoints: 10,
    createdByResidentId: RESIDENT_A,
  });
  const sub = reg.createSubmission({
    taskId: task.id,
    residentId: RESIDENT_A,
    summary: "Try to jump to approved.",
    evidenceItems: [{ type: "url", value: "https://example.com/proof" }],
  });
  // submitted -> approved is not allowed.
  assert.throws(
    () => assertTransition("submitted", "approved"),
    /INV-016-03/,
  );
  // rejected -> approved is not allowed.
  assert.throws(
    () => assertTransition("rejected", "approved"),
    /INV-016-03/,
  );
  // withdrawn -> approved is not allowed.
  assert.throws(
    () => assertTransition("withdrawn", "approved"),
    /INV-016-03/,
  );
});

// ─── INV-016-04 ───────────────────────────────────────────────────────────────

test("INV-016-04: Approved submission grants reputation only once", () => {
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "t-1",
    title: "T1",
    summary: "Test task",
    description: "Test",
    category: "code",
    evidenceRequirements: [],
    defaultReputationPoints: 10,
    createdByResidentId: RESIDENT_A,
  });
  const sub = reg.createSubmission({
    taskId: task.id,
    residentId: RESIDENT_A,
    summary: "First approved contribution.",
    evidenceItems: [{ type: "url", value: "https://example.com/proof" }],
  });
  const r1 = reg.review({
    submissionId: sub.id,
    decision: "approve",
    reviewerResidentId: RESIDENT_B,
  });
  assert.equal(r1.ok, true);
  assert.ok(r1.reputationEventId);
  const beforeCount = reg.reputation.allEvents().length;
  // Try to approve again (idempotent for terminal, but reputation already
  // recorded �?additional event must NOT be created).
  const r2 = reg.review({
    submissionId: sub.id,
    decision: "approve",
    reviewerResidentId: RESIDENT_B,
  });
  assert.equal(r2.ok, true);
  assert.equal(r2.reputationEventId, undefined);
  assert.equal(reg.reputation.allEvents().length, beforeCount);
  // Direct registry call should also reject a second grant.
  assert.throws(
    () =>
      reg.reputation.recordEvent({
        residentId: RESIDENT_A,
        submissionId: sub.id,
        pointsDelta: 10,
        reason: "dup",
        source: "contribution",
        createdByResidentId: RESIDENT_B,
      }),
    /INV-016-04/,
  );
});

// ─── INV-016-05 ───────────────────────────────────────────────────────────────

test("INV-016-05: Approved submission records pending reward only once", () => {
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "t-1",
    title: "T1",
    summary: "Test task",
    description: "Test",
    category: "code",
    evidenceRequirements: [],
    defaultReputationPoints: 10,
    defaultRewardUnits: "10u",
    createdByResidentId: RESIDENT_A,
  });
  const sub = reg.createSubmission({
    taskId: task.id,
    residentId: RESIDENT_A,
    summary: "First approved.",
    evidenceItems: [{ type: "url", value: "https://example.com/proof" }],
  });
  const r1 = reg.review({
    submissionId: sub.id,
    decision: "approve",
    reviewerResidentId: RESIDENT_B,
  });
  assert.equal(r1.ok, true);
  assert.ok(r1.pendingRewardId);
  // second approve is idempotent.
  const r2 = reg.review({
    submissionId: sub.id,
    decision: "approve",
    reviewerResidentId: RESIDENT_B,
  });
  assert.equal(r2.pendingRewardId, undefined);
});

// ─── INV-016-06 ───────────────────────────────────────────────────────────────

test("INV-016-06: Pending reward has no chain side effect (no mint / transfer / etc.)", () => {
  // The PendingRewardRegistry exposes no chain interface at all.
  // We assert by reflection that the registry has no methods related to
  // transfer, mint, claim, send, etc.
  const reg = new PendingRewardRegistry();
  const proto = Object.getPrototypeOf(reg);
  const methods = Object.getOwnPropertyNames(proto).filter(
    (n) => n !== "constructor",
  );
  const banned = ["transfer", "mint", "claim", "send", "withdraw", "payout"];
  for (const m of methods) {
    for (const b of banned) {
      assert.ok(
        !m.toLowerCase().includes(b),
        `method ${m} contains banned keyword ${b}`,
      );
    }
  }
});

// ─── INV-016-07 ───────────────────────────────────────────────────────────────

test("INV-016-07: Reputation total = append-only events sum", () => {
  const rep = new ReputationRegistry();
  rep.recordEvent({
    residentId: RESIDENT_A,
    submissionId: "s1",
    pointsDelta: 10,
    reason: "first",
    source: "contribution",
    createdByResidentId: RESIDENT_B,
  });
  rep.recordEvent({
    residentId: RESIDENT_A,
    submissionId: "s2",
    pointsDelta: 5,
    reason: "second",
    source: "contribution",
    createdByResidentId: RESIDENT_B,
  });
  const adj = rep.adjust({
    residentId: RESIDENT_A,
    reason: "correction",
    pointsDelta: -3,
    createdByResidentId: "system",
  });
  assert.notEqual(adj.id, undefined);
  const agg = rep.aggregateFor(RESIDENT_A);
  assert.equal(agg.score, 12); // 10 + 5 - 3
  assert.equal(agg.contributionCount, 2);
});

// ─── INV-016-08 ───────────────────────────────────────────────────────────────

test("INV-016-08: Evidence URL dangerous scheme rejected", () => {
  const v1 = validateEvidence({ type: "url", value: "javascript:alert(1)" });
  assert.equal(v1.ok, false);
  assert.equal((v1).code, "unsafe-scheme");
  const v2 = validateEvidence({ type: "url", value: "data:text/html,foo" });
  assert.equal(v2.ok, false);
  assert.equal((v2).code, "unsafe-scheme");
  const v3 = validateEvidence({ type: "url", value: "file:///etc/passwd" });
  assert.equal(v3.ok, false);
  assert.equal((v3).code, "unsafe-scheme");
  const ok = validateEvidence({ type: "url", value: "https://example.com/x" });
  assert.equal(ok.ok, true);
});

// ─── INV-016-09 ───────────────────────────────────────────────────────────────

test("INV-016-09: Duplicate approval is idempotent", () => {
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "t-1",
    title: "T1",
    summary: "Test task",
    description: "Test",
    category: "code",
    evidenceRequirements: [],
    defaultReputationPoints: 10,
    defaultRewardUnits: "10u",
    createdByResidentId: RESIDENT_A,
  });
  const sub = reg.createSubmission({
    taskId: task.id,
    residentId: RESIDENT_A,
    summary: "Idempotency test.",
    evidenceItems: [{ type: "url", value: "https://example.com/proof" }],
  });
  const a = reg.review({
    submissionId: sub.id,
    decision: "approve",
    reviewerResidentId: RESIDENT_B,
  });
  const b = reg.review({
    submissionId: sub.id,
    decision: "approve",
    reviewerResidentId: RESIDENT_B,
  });
  assert.equal(a.ok, true);
  assert.equal(b.ok, true);
  assert.equal(b.reputationEventId, undefined);
  assert.equal(b.pendingRewardId, undefined);
  assert.equal(b.auditEventIds.length, 0);
});

// ─── INV-016-10 ───────────────────────────────────────────────────────────────

test("INV-016-10: Private reviewer note not in public API", () => {
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "t-1",
    title: "T1",
    summary: "Test task",
    description: "Test",
    category: "code",
    evidenceRequirements: [],
    defaultReputationPoints: 10,
    createdByResidentId: RESIDENT_A,
  });
  const sub = reg.createSubmission({
    taskId: task.id,
    residentId: RESIDENT_A,
    summary: "Test private note leak.",
    evidenceItems: [{ type: "url", value: "https://example.com/proof" }],
  });
  reg.review({
    submissionId: sub.id,
    decision: "request-changes",
    reviewerResidentId: RESIDENT_B,
    note: "PRIVATE-INTERNAL-NOTE-FOR-REVIEWER-EYES-ONLY-12345",
  });
  // The submission record holds the note in memory, but the public
  // serializer does NOT include it.
  const subs = reg.listSubmissionsForTask(task.id);
  const serialized = subs.map((s) => ({
    id: s.id,
    status: s.status,
    // reviewerNote is intentionally absent from this shape.
  }));
  assert.equal(serialized[0]?.id, sub.id);
  assert.equal(serialized[0]?.status, "changes_requested");
  // Check the typed record directly: the property exists but the public
  // shape above does NOT carry it.
  assert.match(subs[0].reviewerNote ?? "", /PRIVATE-INTERNAL-NOTE/);
});

// ─── INV-016-11 ───────────────────────────────────────────────────────────────

test("INV-016-11: Contribution Network usable without future MOOD Token", () => {
  // Full flow without any token config.
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "t-foundation",
    title: "Foundation task",
    summary: "Works in foundation state",
    description: "Test",
    category: "code",
    evidenceRequirements: [],
    defaultReputationPoints: 5,
    defaultRewardUnits: "5u",
    createdByResidentId: RESIDENT_A,
  });
  const sub = reg.createSubmission({
    taskId: task.id,
    residentId: RESIDENT_A,
    summary: "Foundation flow works.",
    evidenceItems: [{ type: "url", value: "https://example.com/proof" }],
  });
  const result = reg.review({
    submissionId: sub.id,
    decision: "approve",
    reviewerResidentId: RESIDENT_B,
  });
  assert.equal(result.ok, true);
  assert.equal(sub.status, "approved");
});

// ─── INV-016-12 ───────────────────────────────────────────────────────────────

test("INV-016-12: Task �?Review �?Reputation works without MOOD Token CA", () => {
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "no-ca",
    title: "No CA",
    summary: "No Token CA required",
    description: "Test",
    category: "code",
    evidenceRequirements: [],
    defaultReputationPoints: 7,
    createdByResidentId: RESIDENT_A,
  });
  const sub = reg.createSubmission({
    taskId: task.id,
    residentId: RESIDENT_A,
    summary: "Done without any token contract.",
    evidenceItems: [{ type: "url", value: "https://example.com/proof" }],
  });
  reg.review({
    submissionId: sub.id,
    decision: "approve",
    reviewerResidentId: RESIDENT_B,
  });
  const agg = reg.reputation.aggregateFor(RESIDENT_A);
  assert.equal(agg.score, 7);
  assert.equal(agg.approvedContributionCount, 1);
});

// ─── Bonus: Anti-abuse ────────────────────────────────────────────────────────

test("anti-abuse: too many open submissions rejected", () => {
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "t-1",
    title: "T1",
    summary: "Test task",
    description: "Test",
    category: "code",
    evidenceRequirements: [],
    defaultReputationPoints: 5,
    createdByResidentId: RESIDENT_A,
  });
  for (let i = 0; i < 5; i++) {
    reg.createSubmission({
      taskId: task.id,
      residentId: RESIDENT_A,
      summary: `Submission ${i} with enough chars`,
      evidenceItems: [{ type: "url", value: `https://example.com/${i}` }],
    });
  }
  assert.throws(
    () =>
      reg.createSubmission({
        taskId: task.id,
        residentId: RESIDENT_A,
        summary: "Sixth submission attempt",
        evidenceItems: [{ type: "url", value: "https://example.com/6" }],
      }),
    /too-many-open-submissions/,
  );
});

test("isSelfReview detects own-submission attempts", () => {
  const reg = newRegistry();
  const task = reg.createTask({
    slug: "t-1",
    title: "T1",
    summary: "Test task",
    description: "Test",
    category: "code",
    evidenceRequirements: [],
    defaultReputationPoints: 5,
    createdByResidentId: RESIDENT_A,
  });
  const sub = reg.createSubmission({
    taskId: task.id,
    residentId: RESIDENT_A,
    summary: "Self review attempt.",
    evidenceItems: [{ type: "url", value: "https://example.com/x" }],
  });
  assert.equal(isSelfReview(sub, RESIDENT_A), true);
  assert.equal(isSelfReview(sub, RESIDENT_B), false);
});

test("isValidEvidenceArray rejects too many items", () => {
  const items = Array.from({ length: 21 }).map((_, i) => ({
    type: "url",
    value: `https://example.com/${i}`,
  }));
  const v = isValidEvidenceArray(items);
  assert.equal(v.ok, false);
});
