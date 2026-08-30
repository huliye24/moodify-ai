/**
 * MOOD Protocol Reputation Evidence Builder
 *
 * Produces a non-economic reputation-evidence artifact from a scored
 * contribution. The artifact may later be consumed by the Reputation package.
 *
 * MUST NOT contain: tokenAmount, payout, claimAmount, vesting, price.
 */

import { computeContentFingerprint, computeArtifactFingerprint } from './fingerprint.js';
import { validateReputationEvidence, checkForbiddenEconomicFields } from './validate.js';
import { REQUIRED_DIMENSIONS } from './score.js';

/**
 * Build a reputation evidence artifact from a scored contribution.
 *
 * @param {object} contribution - Scored contribution record
 * @param {object} scores - Dimension scores object
 * @param {number|null} aggregate - Aggregate score (may be null)
 * @param {string} policyVersion - Policy version used for scoring
 * @returns {{ reputationEvidence: object, error?: string }}
 */
export function buildReputationEvidence(contribution, scores, aggregate, policyVersion) {
  // Economic field check
  const econFields = checkForbiddenEconomicFields(scores);
  if (econFields.length > 0) {
    return {
      reputationEvidence: null,
      error: `Forbidden economic fields in scores: ${econFields.join(', ')}`,
    };
  }

  const contributionId = contribution.contributionId;
  const inputFingerprint = contribution.contentFingerprint ||
    computeContentFingerprint(contribution);

  const artifact = {
    contributionId,
    policyVersion,
    dimensions: buildDimensions(scores),
    aggregate,
    status: 'scored',
    inputFingerprint,
    artifactFingerprint: '', // filled below
  };

  // Compute artifact fingerprint (excludes itself)
  artifact.artifactFingerprint = computeArtifactFingerprint(artifact);

  // Validate schema
  const schemaResult = validateReputationEvidence(artifact);
  if (!schemaResult.valid) {
    return {
      reputationEvidence: null,
      error: `Schema validation failed: ${JSON.stringify(schemaResult.errors)}`,
    };
  }

  return { reputationEvidence: artifact };
}

/**
 * Build dimensions object for reputation evidence.
 * Ensures all 5 required dimensions are present.
 *
 * @param {object} scores - Dimension scores
 * @returns {object} Dimensions object
 */
function buildDimensions(scores) {
  const dims = {};
  for (const dimension of REQUIRED_DIMENSIONS) {
    dims[dimension] = scores[dimension] || null;
  }
  return dims;
}

/**
 * Update reputation evidence status to finalized.
 *
 * @param {object} evidence - Reputation evidence
 * @returns {{ evidence: object, error?: string }}
 */
export function finalizeReputationEvidence(evidence) {
  if (evidence.status !== 'scored') {
    return {
      evidence: null,
      error: `Can only finalize scored evidence, got: '${evidence.status}'`,
    };
  }

  const finalized = {
    ...evidence,
    status: 'finalized',
  };

  // Recompute artifact fingerprint with updated status
  finalized.artifactFingerprint = computeArtifactFingerprint(finalized);

  return { evidence: finalized };
}

/**
 * Verify that a reputation evidence artifact is self-consistent.
 *
 * @param {object} evidence - Reputation evidence
 * @returns {{ valid: boolean, error?: string }}
 */
export function verifyReputationEvidence(evidence) {
  // Check fingerprint integrity
  const expectedFingerprint = computeArtifactFingerprint(evidence);
  if (expectedFingerprint !== evidence.artifactFingerprint) {
    return {
      valid: false,
      error: `Artifact fingerprint mismatch: expected ${expectedFingerprint}, got ${evidence.artifactFingerprint}`,
    };
  }

  // Check economic fields
  const econFields = checkForbiddenEconomicFields(evidence);
  if (econFields.length > 0) {
    return {
      valid: false,
      error: `Forbidden economic fields: ${econFields.join(', ')}`,
    };
  }

  // Validate schema
  const schemaResult = validateReputationEvidence(evidence);
  if (!schemaResult.valid) {
    return {
      valid: false,
      error: `Schema validation failed: ${JSON.stringify(schemaResult.errors)}`,
    };
  }

  return { valid: true };
}
