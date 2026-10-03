/**
 * MOOD Protocol Contribution State Machine
 *
 * Single authoritative state machine for contribution records.
 * Enforces legal transitions and guards against illegal mutations.
 *
 * State diagram:
 *
 *   draft
 *     ↓
 *   submitted
 *     ↓
 *   under_review
 *   ├──→ rejected
 *   ├──→ needs_more_evidence
 *   └──→ verified
 *              ↓
 *           scored
 *              ↓
 *          finalized
 */

export const ContributionStatus = {
  DRAFT: 'draft',
  SUBMITTED: 'submitted',
  UNDER_REVIEW: 'under_review',
  NEEDS_MORE_EVIDENCE: 'needs_more_evidence',
  REJECTED: 'rejected',
  VERIFIED: 'verified',
  SCORED: 'scored',
  FINALIZED: 'finalized',
};

// Valid transitions: from → [allowed targets]
const TRANSITIONS = {
  [ContributionStatus.DRAFT]: [ContributionStatus.SUBMITTED],
  [ContributionStatus.SUBMITTED]: [ContributionStatus.UNDER_REVIEW],
  [ContributionStatus.UNDER_REVIEW]: [
    ContributionStatus.REJECTED,
    ContributionStatus.NEEDS_MORE_EVIDENCE,
    ContributionStatus.VERIFIED,
  ],
  [ContributionStatus.NEEDS_MORE_EVIDENCE]: [ContributionStatus.UNDER_REVIEW],
  [ContributionStatus.REJECTED]: [],                   // terminal (correction via supersedes)
  [ContributionStatus.VERIFIED]: [ContributionStatus.SCORED],
  [ContributionStatus.SCORED]: [ContributionStatus.FINALIZED],
  [ContributionStatus.FINALIZED]: [],                 // terminal
};

const TERMINAL_STATES = new Set([
  ContributionStatus.REJECTED,
  ContributionStatus.FINALIZED,
]);

const SCOREABLE_STATES = new Set([
  ContributionStatus.VERIFIED,
]);

const FINALIZABLE_STATES = new Set([
  ContributionStatus.SCORED,
]);

/**
 * Get all valid next states from the current state.
 *
 * @param {string} currentStatus - Current status
 * @returns {string[]} Array of valid target states
 */
export function getValidTransitions(currentStatus) {
  return TRANSITIONS[currentStatus] || [];
}

/**
 * Check whether a status transition is valid.
 *
 * @param {string} from - Current status
 * @param {string} to - Target status
 * @returns {{ valid: boolean, error?: string }}
 */
export function canTransition(from, to) {
  if (from === to) {
    return { valid: false, error: `Status is already '${from}'` };
  }

  const allowed = TRANSITIONS[from];
  if (!allowed) {
    return { valid: false, error: `Unknown status: '${from}'` };
  }

  if (!allowed.includes(to)) {
    return {
      valid: false,
      error: `Illegal transition from '${from}' to '${to}'. Allowed: [${allowed.join(', ') || 'none'}]`,
    };
  }

  return { valid: true };
}

/**
 * Transition a contribution record to a new status.
 * Returns a new object (immutable operation).
 *
 * @param {object} contribution - Contribution record
 * @param {string} newStatus - Target status
 * @param {object} [opts] - Transition options
 * @param {string} [opts.reviewerId] - Reviewer performing the transition
 * @param {string} [opts.reason] - Reason for transition
 * @returns {{ contribution: object, error?: string }}
 */
export function transition(contribution, newStatus, opts = {}) {
  const currentStatus = contribution.status;
  const { valid, error } = canTransition(currentStatus, newStatus);

  if (!valid) {
    return { contribution, error };
  }

  const transitionRecord = {
    from: currentStatus,
    to: newStatus,
    at: new Date().toISOString(),
    ...(opts.reviewerId ? { by: opts.reviewerId } : {}),
    ...(opts.reason ? { reason: opts.reason } : {}),
  };

  return {
    contribution: {
      ...contribution,
      status: newStatus,
      _transitions: [...(contribution._transitions || []), transitionRecord],
      _lastTransition: transitionRecord,
    },
  };
}

/**
 * Check whether scoring is allowed for the current status.
 * Scoring is only allowed when status is VERIFIED.
 *
 * @param {string} status - Current status
 * @returns {{ allowed: boolean, error?: string }}
 */
export function canScore(status) {
  if (SCOREABLE_STATES.has(status)) {
    return { allowed: true };
  }
  return {
    allowed: false,
    error: `Scoring is not allowed in '${status}' status. Score only after verification.`,
  };
}

/**
 * Check whether finalization is allowed.
 * Finalization is only allowed from SCORED.
 *
 * @param {string} status - Current status
 * @returns {{ allowed: boolean, error?: string }}
 */
export function canFinalize(status) {
  if (FINALIZABLE_STATES.has(status)) {
    return { allowed: true };
  }
  return {
    allowed: false,
    error: `Finalization is not allowed in '${status}' status.`,
  };
}

/**
 * Check whether a status is terminal (no further transitions possible).
 *
 * @param {string} status - Status to check
 * @returns {boolean}
 */
export function isTerminal(status) {
  return TERMINAL_STATES.has(status);
}

/**
 * Check whether a contribution is immutable (finalized or rejected).
 * Attempting to mutate immutable fields should fail.
 *
 * @param {string} status - Current status
 * @returns {boolean}
 */
export function isImmutable(status) {
  return TERMINAL_STATES.has(status);
}

/**
 * Guard: ensure a finalized record cannot have its immutable fields mutated.
 *
 * @param {object} original - Original contribution
 * @param {object} updated - Updated contribution
 * @returns {{ valid: boolean, error?: string }}
 */
export function guardImmutableFields(original, updated) {
  if (!isImmutable(original.status)) {
    return { valid: true };
  }

  const immutableFields = [
    'schemaVersion', 'contributionId', 'contributor', 'category',
    'title', 'description', 'submittedAt', 'evidence',
    'contentFingerprint', 'policyVersion', 'supersedes',
  ];

  for (const field of immutableFields) {
    const origVal = JSON.stringify(original[field]);
    const updVal = JSON.stringify(updated[field]);
    if (origVal !== updVal) {
      return {
        valid: false,
        error: `Immutable field '${field}' cannot be modified after finalization`,
      };
    }
  }

  return { valid: true };
}
