/**
 * MOOD Protocol Scoring Engine
 *
 * Dimension-level scoring for verified contributions.
 * Scoring is only allowed after VERIFIED status.
 *
 * Each dimension exposes:
 *   - numeric value (0-100)
 *   - scale ("0-100")
 *   - ruleId
 *   - evidenceIds
 *   - source (human_review | deterministic_rule)
 *
 * Aggregate is null when policy weights are not approved.
 */

export const REQUIRED_DIMENSIONS = [
  'contribution',
  'impact',
  'quality',
  'persistence',
  'early',
];

/**
 * Apply a manual score to a dimension.
 *
 * @param {string} dimension - Dimension name
 * @param {number} value - Score value 0-100
 * @param {string} ruleId - Scoring rule version
 * @param {string[]} evidenceIds - Evidence IDs supporting this score
 * @param {object} source - Source info (reviewer ID, etc.)
 * @returns {object} Dimension score object
 */
export function scoreDimension(dimension, value, ruleId, evidenceIds = [], source = {}) {
  if (!REQUIRED_DIMENSIONS.includes(dimension)) {
    throw new Error(`Unknown dimension: ${dimension}`);
  }
  if (typeof value !== 'number' || value < 0 || value > 100) {
    throw new Error(`Score value must be a number between 0 and 100, got: ${value}`);
  }

  return {
    value,
    scale: '0-100',
    ruleId,
    evidenceIds,
    source,
  };
}

/**
 * Apply scoring to all dimensions of a contribution.
 * Accepts per-dimension score values and metadata.
 *
 * @param {object} contribution - Verified contribution record
 * @param {object} dimensionScores - Map of dimension → { value, ruleId, evidenceIds, source }
 * @param {object} [policy] - Policy object (for weight lookup)
 * @returns {{ scores: object, aggregate: number|null, policyLocked: boolean }}
 */
export function scoreContribution(contribution, dimensionScores, policy = null) {
  if (contribution.status !== 'verified') {
    throw new Error('Contribution must be verified before scoring');
  }

  const scores = {};
  const evidenceIds = new Set();

  for (const dimension of REQUIRED_DIMENSIONS) {
    const dimScore = dimensionScores[dimension];

    if (dimScore && typeof dimScore.value === 'number') {
      scores[dimension] = scoreDimension(
        dimension,
        dimScore.value,
        dimScore.ruleId || 'manual.v1',
        dimScore.evidenceIds || [],
        dimScore.source || {},
      );
      for (const id of (dimScore.evidenceIds || [])) {
        evidenceIds.add(id);
      }
    } else {
      scores[dimension] = null;
    }
  }

  // Aggregate: only compute if policy has approved weights
  let aggregate = null;
  let policyLocked = false;

  if (policy && policy.weights && !isWeightsDraft(policy.weights)) {
    aggregate = computeWeightedAggregate(scores, policy.weights);
    policyLocked = policy.status === 'locked';
  }

  return {
    scores,
    aggregate,
    policyLocked,
    evidenceIds: [...evidenceIds],
  };
}

/**
 * Compute weighted aggregate from dimension scores.
 *
 * @param {object} scores - Dimension scores map
 * @param {object} weights - Weight map (dimension → 0-1, sums to 1)
 * @returns {number} Weighted average (0-100)
 */
function computeWeightedAggregate(scores, weights) {
  let totalScore = 0;
  let totalWeight = 0;

  for (const dimension of REQUIRED_DIMENSIONS) {
    const dimScore = scores[dimension];
    if (dimScore !== null && weights[dimension] !== undefined) {
      totalScore += dimScore.value * weights[dimension];
      totalWeight += weights[dimension];
    }
  }

  if (totalWeight === 0) return null;
  return Math.round(totalScore / totalWeight * 100) / 100;
}

/**
 * Check if weights are in draft/unapproved state.
 *
 * @param {any} weights - Weights value from policy
 * @returns {boolean}
 */
function isWeightsDraft(weights) {
  if (weights === null || weights === undefined) return true;
  if (typeof weights !== 'object') return true;
  // If weights is an object, check for 'draft' flag or null values
  if (weights._status === 'draft') return true;
  return false;
}

/**
 * Validate that a scores object has all required dimensions.
 *
 * @param {object} scores - Scores object
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateScores(scores) {
  const errors = [];

  for (const dimension of REQUIRED_DIMENSIONS) {
    const dimScore = scores[dimension];
    if (dimScore === null || dimScore === undefined) continue; // null is allowed

    if (typeof dimScore !== 'object') {
      errors.push(`Dimension '${dimension}' must be null or an object`);
      continue;
    }

    if (typeof dimScore.value !== 'number') {
      errors.push(`Dimension '${dimension}.value' must be a number`);
    } else if (dimScore.value < 0 || dimScore.value > 100) {
      errors.push(`Dimension '${dimension}.value' must be between 0 and 100`);
    }

    if (dimScore.scale !== '0-100') {
      errors.push(`Dimension '${dimension}.scale' must be '0-100'`);
    }
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Derive persistence score from contribution history.
 * Requires at least 2 accepted contributions in the same category.
 * Formula: min(100, count * 20)
 *
 * @param {number} acceptedContributionCount - Number of accepted contributions
 * @param {string} ruleId - Rule version used
 * @returns {object} Persistence dimension score
 */
export function derivePersistenceScore(acceptedContributionCount, ruleId = 'persistence.v1') {
  const value = Math.min(100, acceptedContributionCount * 20);
  return scoreDimension('persistence', value, ruleId, [], { type: 'deterministic_rule' });
}

/**
 * Derive early score from submission timestamp and protocol epoch.
 *
 * @param {string} submittedAt - ISO-8601 submission timestamp
 * @param {string} protocolEpochStart - ISO-8601 epoch start
 * @param {string} ruleId - Rule version
 * @returns {object} Early dimension score
 */
export function deriveEarlyScore(submittedAt, protocolEpochStart, ruleId = 'early.v1') {
  const submitted = new Date(submittedAt);
  const epochStart = new Date(protocolEpochStart);
  const daysSinceEpoch = (submitted - epochStart) / (1000 * 60 * 60 * 24);

  // Linear decay: 100 at day 0, 0 at day 180
  const value = Math.max(0, Math.min(100, Math.round(100 - (daysSinceEpoch / 180) * 100)));
  return scoreDimension('early', value, ruleId, [], { type: 'deterministic_rule' });
}
