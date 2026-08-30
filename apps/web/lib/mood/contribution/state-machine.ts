/**
 * MOOD CONTRIBUTION 016 — State Machine
 *
 * Single authoritative state machine for ContributionSubmission.
 * Authority: MOOD-CONTRIBUTION-016 TASK.md Phase D.
 *
 * Allowed transitions:
 *   submitted -> under_review
 *   submitted -> withdrawn
 *   under_review -> changes_requested
 *   under_review -> approved
 *   under_review -> rejected
 *   changes_requested -> submitted
 *
 * Forbidden:
 *   submitted -> approved (must go through review)
 *   approved -> submitted (no auto-revert)
 *   rejected -> approved (no auto-approve)
 *   withdrawn -> approved (no auto-approve)
 *
 * Override (admin override + audit) is allowed but default-disabled.
 */

import type { SubmissionStatus } from "./types.ts";

const ALLOWED: Record<SubmissionStatus, ReadonlyArray<SubmissionStatus>> = {
  submitted: ["under_review", "withdrawn"],
  under_review: ["changes_requested", "approved", "rejected"],
  changes_requested: ["submitted"],
  approved: [], // terminal
  rejected: [], // terminal
  withdrawn: [], // terminal
};

export function isTransitionAllowed(
  from: SubmissionStatus,
  to: SubmissionStatus,
): boolean {
  return ALLOWED[from].includes(to);
}

export function assertTransition(
  from: SubmissionStatus,
  to: SubmissionStatus,
  opts: { adminOverride?: boolean } = {},
): void {
  if (isTransitionAllowed(from, to)) return;
  // adminOverride is not implemented by 016; explicit "false" is the default.
  // This function MUST reject any non-allowed transition regardless of opts.
  if (opts.adminOverride === true) {
    // Reserved for a future package. 016 keeps it explicitly false.
    throw new Error(
      `INV-016-XX: transition ${from} -> ${to} not allowed (admin override disabled in 016)`,
    );
  }
  throw new Error(
    `INV-016-03: transition ${from} -> ${to} not allowed`,
  );
}

export function isTerminalStatus(s: SubmissionStatus): boolean {
  return ALLOWED[s].length === 0;
}