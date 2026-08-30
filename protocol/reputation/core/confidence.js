/**
 * MOOD Protocol Confidence Module
 *
 * Calculates confidence/completeness levels for reputation snapshots.
 * Confidence reflects evidence completeness, not human worth.
 */

import crypto from 'crypto';

/**
 * Confidence levels in order of increasing reliability
 */
export const CONFIDENCE_LEVELS = ['insufficient', 'low', 'medium', 'high', 'certainty'];

/**
 * Minimum contributions for each confidence level
 */
const MIN_CONTRIBUTIONS = {
  insufficient: 0,
  low: 1,
  medium: 3,
  high: 5,
  certainty: 10
};

/**
 * Minimum valid dimensions for each confidence level
 */
const MIN_DIMENSIONS = {
  insufficient: 0,
  low: 1,
  medium: 2,
  high: 3,
  certainty: 4
};

/**
 * Calculate confidence from contribution data
 * @param {object} options - Calculation options
 * @param {number} options.contributionCount - Number of contributions
 * @param {number} options.validDimensionCount - Number of valid dimensions
 * @param {number} options.categoryDiversity - Number of unique categories
 * @param {number} options.epochCount - Number of epochs with contributions
 * @param {string} options.persistenceStatus - Persistence calculation status
 * @returns {object} Confidence result
 */
export function calculateConfidence(options) {
  const {
    contributionCount = 0,
    validDimensionCount = 0,
    categoryDiversity = 0,
    epochCount = 0,
    persistenceStatus = 'INSUFFICIENT_HISTORY'
  } = options;

  // Calculate individual scores
  const contributionScore = scoreContributions(contributionCount);
  const dimensionScore = scoreDimensions(validDimensionCount);
  const diversityScore = scoreDiversity(categoryDiversity);
  const epochScore = scoreEpochs(epochCount);
  const persistenceScore = scorePersistence(persistenceStatus);

  // Weighted combined score
  const weights = {
    contribution: 0.35,
    dimension: 0.25,
    diversity: 0.10,
    epoch: 0.15,
    persistence: 0.15
  };

  const combinedScore =
    contributionScore * weights.contribution +
    dimensionScore * weights.dimension +
    diversityScore * weights.diversity +
    epochScore * weights.epoch +
    persistenceScore * weights.persistence;

  // Determine confidence level
  const level = scoreToLevel(combinedScore);

  return {
    level,
    score: Math.round(combinedScore * 100) / 100,
    breakdown: {
      contribution: contributionScore,
      dimension: dimensionScore,
      diversity: diversityScore,
      epoch: epochScore,
      persistence: persistenceScore
    },
    meetsMinimum: meetsMinimumRequirements(contributionCount, validDimensionCount),
    recommendations: generateRecommendations(options, level)
  };
}

/**
 * Score contributions count (0-1)
 * @param {number} count - Contribution count
 * @returns {number} Score
 */
function scoreContributions(count) {
  if (count === 0) return 0;
  if (count >= 20) return 1;
  return Math.min(count / 20, 1);
}

/**
 * Score valid dimensions count (0-1)
 * @param {number} count - Valid dimensions count
 * @returns {number} Score
 */
function scoreDimensions(count) {
  // 5 total dimensions
  return Math.min(count / 5, 1);
}

/**
 * Score category diversity (0-1)
 * @param {number} count - Unique categories
 * @returns {number} Score
 */
function scoreDiversity(count) {
  // More categories = higher diversity score
  // But diversity beyond 5 categories is capped
  if (count === 0) return 0;
  if (count >= 5) return 1;
  return count / 5;
}

/**
 * Score epoch count (0-1)
 * @param {number} count - Epochs with contributions
 * @returns {number} Score
 */
function scoreEpochs(count) {
  // Consider 6+ epochs as "certain"
  if (count === 0) return 0;
  if (count >= 6) return 1;
  return count / 6;
}

/**
 * Score persistence status (0-1)
 * @param {string} status - Persistence status
 * @returns {number} Score
 */
function scorePersistence(status) {
  switch (status) {
    case 'VERIFIED_LONGITUDINAL':
      return 1;
    case 'VERIFIED_SHORT':
      return 0.6;
    case 'PARTIAL':
      return 0.3;
    case 'INSUFFICIENT_HISTORY':
    default:
      return 0;
  }
}

/**
 * Convert numeric score to confidence level
 * @param {number} score - Numeric score (0-1)
 * @returns {string} Confidence level
 */
function scoreToLevel(score) {
  if (score >= 0.85) return 'certainty';
  if (score >= 0.70) return 'high';
  if (score >= 0.45) return 'medium';
  if (score >= 0.20) return 'low';
  return 'insufficient';
}

/**
 * Check if minimum requirements are met
 * @param {number} contributionCount - Contribution count
 * @param {number} validDimensionCount - Valid dimensions count
 * @returns {boolean} Whether minimums are met
 */
function meetsMinimumRequirements(contributionCount, validDimensionCount) {
  return contributionCount > 0 && validDimensionCount > 0;
}

/**
 * Generate recommendations based on current state
 * @param {object} options - Current options
 * @param {string} level - Current confidence level
 * @returns {Array} Recommendations
 */
function generateRecommendations(options, level) {
  const recommendations = [];

  if (options.contributionCount < MIN_CONTRIBUTIONS.medium) {
    recommendations.push({
      type: 'contribution_count',
      message: `Need ${MIN_CONTRIBUTIONS.medium - options.contributionCount} more contributions for medium confidence`,
      priority: 'high'
    });
  }

  if (options.validDimensionCount < MIN_DIMENSIONS.medium) {
    recommendations.push({
      type: 'dimension_count',
      message: `Need ${MIN_DIMENSIONS.medium - options.validDimensionCount} more valid dimensions`,
      priority: 'medium'
    });
  }

  if (options.epochCount < 2) {
    recommendations.push({
      type: 'epoch_coverage',
      message: 'Contribute across multiple epochs for higher confidence',
      priority: 'medium'
    });
  }

  if (options.persistenceStatus === 'INSUFFICIENT_HISTORY') {
    recommendations.push({
      type: 'persistence',
      message: 'Continue contributing over time to establish persistence',
      priority: 'low'
    });
  }

  if (recommendations.length === 0) {
    recommendations.push({
      type: 'sufficient',
      message: 'Sufficient evidence for current confidence level',
      priority: 'info'
    });
  }

  return recommendations;
}

/**
 * Validate confidence level
 * @param {string} level - Level to validate
 * @returns {boolean} Whether valid
 */
export function isValidConfidenceLevel(level) {
  return CONFIDENCE_LEVELS.includes(level);
}

/**
 * Compare two confidence levels
 * @param {string} level1 - First level
 * @param {string} level2 - Second level
 * @returns {number} Comparison result (-1, 0, 1)
 */
export function compareConfidence(level1, level2) {
  const idx1 = CONFIDENCE_LEVELS.indexOf(level1);
  const idx2 = CONFIDENCE_LEVELS.indexOf(level2);
  return idx1 - idx2;
}

/**
 * Get minimum requirements for a confidence level
 * @param {string} level - Target level
 * @returns {object} Minimum requirements
 */
export function getMinimumRequirements(level) {
  const levelIndex = CONFIDENCE_LEVELS.indexOf(level);
  if (levelIndex === -1) {
    throw new Error(`Invalid confidence level: ${level}`);
  }

  return {
    minContributions: MIN_CONTRIBUTIONS[level] || 0,
    minDimensions: MIN_DIMENSIONS[level] || 0,
    minEpochs: levelIndex >= 2 ? levelIndex : 1
  };
}

/**
 * Calculate fingerprint of confidence calculation
 * @param {object} inputs - Calculation inputs
 * @returns {string} SHA-256 fingerprint
 */
export function fingerprintConfidence(inputs) {
  const canonical = {
    contributionCount: inputs.contributionCount,
    validDimensionCount: inputs.validDimensionCount,
    categoryDiversity: inputs.categoryDiversity,
    epochCount: inputs.epochCount,
    persistenceStatus: inputs.persistenceStatus
  };

  const canonicalString = JSON.stringify(canonical, Object.keys(canonical).sort());
  return `sha256:${crypto.createHash('sha256').update(canonicalString).digest('hex')}`;
}

export default {
  calculateConfidence,
  isValidConfidenceLevel,
  compareConfidence,
  getMinimumRequirements,
  fingerprintConfidence,
  CONFIDENCE_LEVELS
};
