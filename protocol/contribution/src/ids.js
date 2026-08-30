/**
 * MOOD Protocol Contribution ID Generation
 *
 * Deterministic and collision-resistant contribution ID generation.
 * IDs are derived from canonical inputs so that the same contribution
 * always produces the same ID across runs.
 */

import crypto from 'crypto';

const ID_PREFIX = 'mood-contrib-';
const SCHEMA_VERSION = '1.0.0';

/**
 * Generate a deterministic contribution ID from canonical inputs.
 *
 * Canonical input (ordered):
 *   schemaVersion, contributor.type, normalized contributor.id,
 *   category, contentFingerprint, submittedAt
 *
 * @param {object} params - Contribution inputs
 * @param {string} params.schemaVersion - Schema version
 * @param {string} params.contributorType - Contributor type (wallet/github/protocol_id)
 * @param {string} params.contributorId - Contributor ID (will be normalized)
 * @param {string} params.category - Contribution category
 * @param {string} params.contentFingerprint - SHA-256 fingerprint
 * @param {string} params.submittedAt - ISO-8601 timestamp
 * @returns {string} Contribution ID
 */
export function generateContributionId({
  schemaVersion,
  contributorType,
  contributorId,
  category,
  contentFingerprint,
  submittedAt,
}) {
  if (!schemaVersion || !contributorType || !contributorId || !category ||
      !contentFingerprint || !submittedAt) {
    throw new Error('All canonical inputs are required for contribution ID generation');
  }

  // Normalize contributor ID: lowercase, strip leading/trailing whitespace
  const normalizedId = normalizeContributorId(contributorId);

  const canonical = [
    schemaVersion,
    contributorType,
    normalizedId,
    category,
    contentFingerprint,
    submittedAt,
  ].join('|');

  const hash = crypto.createHash('sha256').update(canonical).digest('hex');

  // Encode first 12 hex chars as base36 for a readable ID
  const short = parseInt(hash.substring(0, 12), 16).toString(36);

  return `${ID_PREFIX}${short}`;
}

/**
 * Generate a deterministic evidence ID.
 *
 * Canonical input:
 *   contributionId, evidenceId input
 *
 * @param {string} contributionId - Parent contribution ID
 * @param {string} evidenceId - Evidence identifier
 * @returns {string} Deterministic evidence ID
 */
export function generateEvidenceId(contributionId, evidenceId) {
  if (!contributionId || !evidenceId) {
    throw new Error('contributionId and evidenceId are required');
  }
  const canonical = `${contributionId}|${evidenceId}`;
  const hash = crypto.createHash('sha256').update(canonical).digest('hex');
  const short = parseInt(hash.substring(0, 10), 16).toString(36);
  return `evidence-${short}`;
}

/**
 * Normalize a contributor ID.
 * Wallet addresses are lowercased.
 * Other IDs are lowercased and trimmed.
 *
 * @param {string} id - Contributor ID
 * @returns {string} Normalized ID
 */
export function normalizeContributorId(id) {
  if (!id || typeof id !== 'string') {
    throw new Error('Contributor ID must be a non-empty string');
  }

  let normalized = id.trim().toLowerCase();

  // For wallet addresses (0x...), ensure consistent checksum handling
  if (normalized.startsWith('0x')) {
    // Keep as lowercase (EIP-55 mixed-case is not enforced here;
    // the raw string normalized to lowercase is used as the canonical form)
    normalized = normalized.toLowerCase();
  }

  return normalized;
}

/**
 * Generate a reviewer ID from a contributor ID (for self-review guard).
 *
 * @param {string} contributorId - Contributor ID
 * @returns {string} Reviewer ID
 */
export function reviewerIdFromContributor(contributorId) {
  const hash = crypto.createHash('sha256').update(contributorId).digest('hex');
  return `reviewer-${hash.substring(0, 12)}`;
}

/**
 * Build a contributor key for duplicate lookups.
 * Format: contributor:{type}:{normalized_id}:{category}
 *
 * @param {object} contributor - Contributor object
 * @param {string} category - Category
 * @returns {string} Lookup key
 */
export function buildContributorCategoryKey(contributor, category) {
  const normalized = normalizeContributorId(contributor.id);
  return `contributor:${contributor.type}:${normalized}:${category}`;
}
