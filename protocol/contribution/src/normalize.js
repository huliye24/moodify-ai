/**
 * MOOD Protocol Contribution Normalization
 *
 * Produces a canonical JSON representation so that equivalent
 * contributions with different key ordering produce identical strings.
 *
 * Excludes mutable review fields from the canonical form.
 */

import { normalizeContributorId } from './ids.js';

const MUTABLE_FIELDS = new Set([
  'review',
  'scores',
  'reputationEvidence',
  'status',         // status changes after submission
]);

/**
 * Create a canonical normalized representation of a contribution record.
 * The same contribution in different JSON forms produces identical output.
 *
 * Mutable fields (review, scores, reputationEvidence, status) are excluded
 * so that fingerprinting is stable across state transitions.
 *
 * @param {object} contribution - Raw contribution record
 * @returns {string} Canonical JSON string
 */
export function normalizeContribution(contribution) {
  if (!contribution || typeof contribution !== 'object') {
    throw new Error('Contribution must be a plain object');
  }

  const canonical = {};

  // Schema version
  if (contribution.schemaVersion !== undefined) {
    canonical.schemaVersion = contribution.schemaVersion;
  }

  // Contributor — normalize the ID
  if (contribution.contributor) {
    canonical.contributor = {
      type: contribution.contributor.type,
      id: normalizeContributorId(contribution.contributor.id),
    };
    // Only include displayName if explicitly set
    if (contribution.contributor.displayName !== undefined &&
        contribution.contributor.displayName !== null) {
      canonical.contributor.displayName = contribution.contributor.displayName;
    }
  }

  // Immutable fields
  if (contribution.category !== undefined) canonical.category = contribution.category;
  if (contribution.title !== undefined) canonical.title = contribution.title;
  if (contribution.description !== undefined) canonical.description = contribution.description;
  if (contribution.submittedAt !== undefined) canonical.submittedAt = contribution.submittedAt;
  if (contribution.policyVersion !== undefined) canonical.policyVersion = contribution.policyVersion;
  if (contribution.supersedes !== undefined) canonical.supersedes = contribution.supersedes;

  // Evidence — sort by evidenceId for canonical order
  if (Array.isArray(contribution.evidence)) {
    const sortedEvidence = [...contribution.evidence]
      .filter(e => e && e.evidenceId)
      .sort((a, b) => a.evidenceId.localeCompare(b.evidenceId))
      .map(normalizeEvidence);
    canonical.evidence = sortedEvidence;
  } else {
    canonical.evidence = [];
  }

  return JSON.stringify(canonical, Object.keys(canonical).sort(), 0);
}

/**
 * Normalize a single evidence object canonically.
 * Excludes mutable verification fields.
 *
 * @param {object} evidence - Raw evidence
 * @returns {object} Canonical evidence
 */
export function normalizeEvidence(evidence) {
  if (!evidence) return {};

  const canonical = {};

  if (evidence.evidenceId !== undefined) canonical.evidenceId = evidence.evidenceId;
  if (evidence.type !== undefined) canonical.type = evidence.type;
  if (evidence.uri !== undefined) canonical.uri = evidence.uri;
  if (evidence.digest !== undefined) canonical.digest = evidence.digest;
  if (evidence.observedAt !== undefined) canonical.observedAt = evidence.observedAt;

  // Metadata — sort keys for canonical order
  if (evidence.metadata && typeof evidence.metadata === 'object') {
    canonical.metadata = sortObjectKeys(evidence.metadata);
  } else {
    canonical.metadata = {};
  }

  // Verification — include status but not mutable details
  if (evidence.verification && typeof evidence.verification === 'object') {
    canonical.verification = {
      status: evidence.verification.status,
    };
  }

  return canonical;
}

/**
 * Sort object keys alphabetically (recursive).
 *
 * @param {object} obj - Object to sort
 * @returns {object} Sorted object
 */
function sortObjectKeys(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(sortObjectKeys);

  const sorted = {};
  for (const key of Object.keys(obj).sort()) {
    sorted[key] = sortObjectKeys(obj[key]);
  }
  return sorted;
}

/**
 * Verify that two contributions are canonically equivalent
 * (same key order produces same normalized string).
 *
 * @param {object} a - Contribution A
 * @param {object} b - Contribution B
 * @returns {boolean} Whether they normalize to the same string
 */
export function areCanonicallyEquivalent(a, b) {
  return normalizeContribution(a) === normalizeContribution(b);
}
