/**
 * MOOD CONTRIBUTION 016 — Anti-Abuse Policies
 *
 * Rate limits + dedupe + reviewer safety checks.
 * Authority: MOOD-CONTRIBUTION-016 TASK.md Phase N.
 */

import type { ResidentId } from "../passport/types.ts";
import type { ContributionSubmission } from "./types.ts";

/** Max submissions a single Resident can have in non-terminal status. */
export const MAX_OPEN_SUBMISSIONS_PER_RESIDENT = 5;

/** Per-submission evidence items cap (also enforced in evidence.ts). */
export const MIN_RESUBMISSION_INTERVAL_MS = 30 * 1000;

export interface SubmissionOpenCount {
  count: number;
  allowed: boolean;
}

export function countOpenSubmissions(
  submissions: ReadonlyArray<ContributionSubmission>,
  residentId: ResidentId,
): SubmissionOpenCount {
  const open = submissions.filter(
    (s) =>
      s.residentId === residentId &&
      (s.status === "submitted" ||
        s.status === "under_review" ||
        s.status === "changes_requested"),
  );
  return {
    count: open.length,
    allowed: open.length < MAX_OPEN_SUBMISSIONS_PER_RESIDENT,
  };
}

/** INV-016-02: a Resident cannot review their own submission. */
export function isSelfReview(
  submission: ContributionSubmission,
  reviewerResidentId: ResidentId,
): boolean {
  return submission.residentId === reviewerResidentId;
}

/** INV-016-09: duplicate review actions are idempotent. */
export function isAlreadyReviewed(submission: ContributionSubmission): boolean {
  return (
    submission.status === "approved" ||
    submission.status === "rejected" ||
    submission.status === "withdrawn"
  );
}