/**
 * MOOD Protocol Reputation Aggregator
 *
 * Aggregates contributions into reputation scores
 */

import { getProfile } from './profile.js';
import { generateProtocolId } from './identity.js';
import crypto from 'crypto';

// Default dimension weights
const DEFAULT_WEIGHTS = {
  contribution: 0.30,
  impact: 0.25,
  quality: 0.20,
  persistence: 0.15,
  early: 0.10
};

// Aggregation methods
const METHODS = {
  WEIGHTED_AVERAGE: 'weighted-average',
  MEDIAN: 'median',
  MAXIMUM: 'maximum',
  CUSTOM: 'custom'
};

/**
 * Aggregate contributions for a participant
 * @param {string} protocolId - Participant protocol ID
 * @param {Array<string>} contributionIds - Contribution IDs to aggregate
 * @param {object} [options] - Aggregation options
 * @param {string} [options.method='weighted-average'] - Aggregation method
 * @param {object} [options.weights] - Dimension weights
 * @param {string} [options.epochId] - Specific epoch to aggregate
 * @returns {object} Aggregated reputation data
 */
export async function aggregateReputation(protocolId, contributionIds, options = {}) {
  const {
    method = METHODS.WEIGHTED_AVERAGE,
    weights = DEFAULT_WEIGHTS,
    epochId
  } = options;

  // Get participant profile
  const profile = getProfile(protocolId);
  if (!profile) {
    throw new Error(`Profile not found for ${protocolId}`);
  }

  // Filter contributions by epoch if specified
  let contributionsToAggregate;
  if (epochId) {
    // In a real implementation, this would fetch contribution data
    // For now, use profile epoch data
    const epoch = profile.epochs.find(e => e.epochId === epochId);
    if (!epoch || !epoch.participated) {
      return {
        protocolId,
        epochId,
        dimensions: {
          contribution: null,
          impact: null,
          quality: null,
          persistence: null,
          early: null
        },
        aggregate: null,
        confidence: 'insufficient',
        verifiedContributionCount: 0
      };
    }
    contributionsToAggregate = [epoch];
  } else {
    // Aggregate across all epochs
    contributionsToAggregate = profile.epochs.filter(e => e.participated);
  }

  // Calculate dimension scores
  const dimensionScores = calculateDimensionScores(contributionsToAggregate);

  // Calculate aggregate score
  const aggregateScore = calculateAggregateScore(dimensionScores, method, weights);

  // Determine confidence level
  const confidence = calculateConfidence(dimensionScores, contributionsToAggregate.length);

  // Prepare result
  const result = {
    protocolId,
    epochId: epochId || 'ALL_EPOCHS',
    dimensions: dimensionScores,
    aggregate: aggregateScore,
    confidence,
    verifiedContributionCount: contributionsToAggregate.reduce((sum, epoch) => sum + epoch.contributionCount, 0),
    categoryDiversity: calculateCategoryDiversity(contributionsToAggregate),
    calculatedAt: new Date().toISOString(),
    method,
    weights
  };

  return result;
}

/**
 * Calculate scores for each dimension
 * @param {Array<object>} contributions - Contributions to process
 * @returns {object} Dimension scores
 */
function calculateDimensionScores(contributions) {
  const dimensions = ['contribution', 'impact', 'quality', 'persistence', 'early'];
  const scores = {};

  dimensions.forEach(dimension => {
    const dimensionScores = contributions
      .map(c => c.dimensions[dimension])
      .filter(score => score !== null);

    if (dimensionScores.length > 0) {
      scores[dimension] = calculateWeightedAverage(dimensionScores);
    } else {
      scores[dimension] = null;
    }
  });

  return scores;
}

/**
 * Calculate weighted average of scores
 * @param {Array<number>} scores - Array of scores
 * @returns {number} Weighted average
 */
function calculateWeightedAverage(scores) {
  if (scores.length === 0) return 0;

  // For now, simple average. In production, this would consider:
  // - Time decay
  // - Source reliability
  // - Contribution size/complexity

  const sum = scores.reduce((acc, score) => acc + score, 0);
  return Number((sum / scores.length).toFixed(2));
}

/**
 * Calculate aggregate score from dimensions
 * @param {object} dimensions - Dimension scores
 * @param {string} method - Aggregation method
 * @param {object} weights - Dimension weights
 * @returns {object} Aggregate score
 */
function calculateAggregateScore(dimensions, method, weights) {
  // Filter out null dimensions
  const validDimensions = Object.entries(dimensions)
    .filter(([_, score]) => score !== null);

  if (validDimensions.length === 0) {
    return { score: 0, method };
  }

  let score;

  switch (method) {
    case METHODS.WEIGHTED_AVERAGE:
      score = calculateWeightedAverageScore(validDimensions, weights);
      break;
    case METHODS.MEDIAN:
      score = calculateMedianScore(validDimensions);
      break;
    case METHODS.MAXIMUM:
      score = calculateMaximumScore(validDimensions);
      break;
    default:
      score = calculateWeightedAverageScore(validDimensions, weights);
  }

  return {
    score: Number(score.toFixed(2)),
    method,
    weights,
    timestamp: new Date().toISOString()
  };
}

/**
 * Calculate weighted average score
 * @param {Array<Array<string, number>>} dimensions - [dimension, score] pairs
 * @param {object} weights - Dimension weights
 * @returns {number} Weighted average
 */
function calculateWeightedAverageScore(dimensions, weights) {
  let weightedSum = 0;
  let totalWeight = 0;

  dimensions.forEach(([dimension, score]) => {
    const weight = weights[dimension] || 0;
    weightedSum += score * weight;
    totalWeight += weight;
  });

  return totalWeight > 0 ? weightedSum / totalWeight : 0;
}

/**
 * Calculate median score
 * @param {Array<Array<string, number>>} dimensions - [dimension, score] pairs
 * @returns {number} Median score
 */
function calculateMedianScore(dimensions) {
  const scores = dimensions.map(([, score]) => score).sort((a, b) => a - b);
  const mid = Math.floor(scores.length / 2);
  return scores.length % 2 === 0
    ? (scores[mid - 1] + scores[mid]) / 2
    : scores[mid];
}

/**
 * Calculate maximum score
 * @param {Array<Array<string, number>>} dimensions - [dimension, score] pairs
 * @returns {number} Maximum score
 */
function calculateMaximumScore(dimensions) {
  return Math.max(...dimensions.map(([, score]) => score));
}

/**
 * Calculate confidence level
 * @param {object} dimensions - Dimension scores
 * @param {number} contributionCount - Number of contributions
 * @returns {string} Confidence level
 */
function calculateConfidence(dimensions, contributionCount) {
  const validDimensions = Object.values(dimensions).filter(score => score !== null);

  if (validDimensions.length === 0) {
    return 'insufficient';
  }

  // Confidence based on:
  // 1. Number of valid dimensions
  // 2. Number of contributions
  // 3. Score distribution

  const dimensionRatio = validDimensions.length / 5; // 5 total dimensions
  const contributionRatio = Math.min(contributionCount / 10, 1); // Normalize to max 10 contributions

  const combinedScore = (dimensionRatio + contributionRatio) / 2;

  if (combinedScore >= 0.8) return 'certainty';
  if (combinedScore >= 0.6) return 'high';
  if (combinedScore >= 0.4) return 'medium';
  if (combinedScore >= 0.2) return 'low';
  return 'insufficient';
}

/**
 * Calculate category diversity
 * @param {Array<object>} contributions - Contributions to analyze
 * @returns {Array<string>} List of unique categories
 */
function calculateCategoryDiversity(contributions) {
  const categories = new Set();

  contributions.forEach(contribution => {
    // In a real implementation, this would extract categories from contribution data
    // For now, use placeholder categories
    if (contribution.contributionCount > 0) {
      categories.add('code');
    }
  });

  return Array.from(categories);
}

/**
 * Consume MPF-002 contribution records
 * @param {object} input - Input data from MPF-002
 * @param {Array<string>} [identityMap] - Optional identity mapping
 * @returns {Array<object>} Aggregated reputation data
 */
export async function consumeContributions(input, identityMap = []) {
  const { contributions = [] } = input;
  const results = [];

  for (const contribution of contributions) {
    try {
      // Map contribution to identity if provided
      let protocolId = contribution.contributorId;

      if (identityMap && identityMap.length > 0) {
        const mapping = identityMap.find(m => m.contributionId === contribution.id);
        if (mapping) {
          protocolId = mapping.protocolId;
        }
      }

      // Generate protocol ID if not provided
      if (!protocolId) {
        protocolId = generateProtocolId(contribution.contributorId);
      }

      // Aggregate reputation
      const aggregated = await aggregateReputation(
        protocolId,
        [contribution.id],
        { method: METHODS.WEIGHTED_AVERAGE }
      );

      results.push({
        contributionId: contribution.id,
        protocolId,
        reputation: aggregated
      });

    } catch (error) {
      console.error(`Failed to process contribution ${contribution.id}: ${error.message}`);
      results.push({
        contributionId: contribution.id,
        error: error.message
      });
    }
  }

  return results;
}

/**
 * Batch aggregate multiple participants
 * @param {Array<string>} protocolIds - List of protocol IDs
 * @param {object} [options] - Aggregation options
 * @returns {Array<object>} Batch results
 */
export async function batchAggregate(protocolIds, options = {}) {
  const results = [];

  for (const protocolId of protocolIds) {
    try {
      const aggregated = await aggregateReputation(protocolId, [], options);
      results.push({
        protocolId,
        success: true,
        data: aggregated
      });
    } catch (error) {
      results.push({
        protocolId,
        success: false,
        error: error.message
      });
    }
  }

  return results;
}

/**
 * Validate aggregation result integrity
 * @param {object} result - Aggregation result
 * @returns {boolean} Whether result is valid
 */
export function validateAggregation(result) {
  // Check required fields
  const required = ['protocolId', 'dimensions', 'confidence', 'calculatedAt'];
  for (const field of required) {
    if (!(field in result)) {
      return false;
    }
  }

  // Check dimension format
  const dimensions = result.dimensions;
  const validDimensions = ['contribution', 'impact', 'quality', 'persistence', 'early'];
  for (const dimension of validDimensions) {
    if (dimension in dimensions && (dimensions[dimension] < 0 || dimensions[dimension] > 100)) {
      return false;
    }
  }

  // Check confidence level
  const validConfidences = ['insufficient', 'low', 'medium', 'high', 'certainty'];
  if (!validConfidences.includes(result.confidence)) {
    return false;
  }

  return true;
}