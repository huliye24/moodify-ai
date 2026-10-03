/**
 * MOOD Protocol Profile Management
 *
 * Creates and manages participant reputation profiles
 */

import { generateProtocolId, generateFingerprint, IdentityHistory } from './identity.js';
import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'fs';
import { join } from 'path';
import crypto from 'crypto';

const PROFILE_SCHEMA_VERSION = '1.0.0';
const DATA_DIR = './data/reputation';
const PROFILE_FILE = join(DATA_DIR, 'profiles.json');

/**
 * Create a new reputation profile
 * @param {object} options - Profile creation options
 * @param {string} options.identityProof - Identity proof
 * @param {Array<string>} options.contributionIds - Initial contribution IDs
 * @param {object} [options.metadata] - Additional metadata
 * @returns {object} Created profile
 */
export async function createProfile(options) {
  const { identityProof, contributionIds = [], metadata = {} } = options;

  if (!identityProof) {
    throw new Error('Identity proof is required');
  }

  // Ensure data directory exists
  if (!existsSync(DATA_DIR)) {
    mkdirSync(DATA_DIR, { recursive: true });
  }

  // Generate protocol ID
  const protocolId = generateProtocolId(identityProof);
  const fingerprint = generateFingerprint(identityProof);

  // Create base profile
  const profile = {
    profileVersion: PROFILE_SCHEMA_VERSION,
    protocolId,
    identityFingerprint: fingerprint,
    createdAt: new Date().toISOString(),
    lastUpdated: new Date().toISOString(),
    epochs: [],
    totalContributions: 0,
    dimensionSummary: {
      contribution: { mean: 0, median: 0, min: 0, max: 0, stdDev: 0, count: 0 },
      impact: { mean: 0, median: 0, min: 0, max: 0, stdDev: 0, count: 0 },
      quality: { mean: 0, median: 0, min: 0, max: 0, stdDev: 0, count: 0 },
      persistence: { mean: 0, median: 0, min: 0, max: 0, stdDev: 0, count: 0 },
      early: { mean: 0, median: 0, min: 0, max: 0, stdDev: 0, count: 0 },
      participationRate: 0
    },
    identityHistory: [],
    metadata: {
      categoryTags: [],
      achievements: [],
      preferences: {},
      verificationStatus: 'PENDING',
      ...metadata
    }
  };

  // Record identity creation event
  const identityHistory = new IdentityHistory('./data/identity');
  identityHistory.recordEvent({
    eventType: 'CREATED',
    identityProof,
    fingerprint,
    contributionsAffected: contributionIds.length
  });

  // Add to identity history
  profile.identityHistory.push({
    eventId: `IDENTITY-${Date.now()}-${Math.floor(Math.random() * 1000000).toString().padStart(6, '0')}`,
    timestamp: new Date().toISOString(),
    eventType: 'CREATED',
    identityProof,
    fingerprint,
    contributionsAffected: contributionIds.length
  });

  // Save profile
  saveProfile(profile);

  return profile;
}

/**
 * Get existing profile by protocol ID
 * @param {string} protocolId - Participant protocol ID
 * @returns {object|null} Profile or null if not found
 */
export function getProfile(protocolId) {
  try {
    const profiles = loadProfiles();
    return profiles[protocolId] || null;
  } catch (error) {
    console.error(`Failed to get profile for ${protocolId}: ${error.message}`);
    return null;
  }
}

/**
 * Update profile with new contributions
 * @param {string} protocolId - Participant protocol ID
 * @param {Array<string>} contributionIds - New contribution IDs
 * @param {object} [contributions] - Contribution data
 * @returns {object} Updated profile
 */
export async function updateProfile(protocolId, contributionIds, contributions = {}) {
  const profile = getProfile(protocolId);
  if (!profile) {
    throw new Error(`Profile not found for ${protocolId}`);
  }

  // Update total contributions
  profile.totalContributions += contributionIds.length;

  // Update last updated timestamp
  profile.lastUpdated = new Date().toISOString();

  // In a real implementation, this would:
  // 1. Fetch contribution details
  // 2. Update epoch summaries
  // 3. Recalculate dimension statistics
  // 4. Update achievements

  // For now, just mark contributions as processed
  if (!profile.metadata.processedContributions) {
    profile.metadata.processedContributions = [];
  }
  profile.metadata.processedContributions.push(...contributionIds);

  // Save updated profile
  saveProfile(profile);

  return profile;
}

/**
 * Update epoch summary for profile
 * @param {string} protocolId - Participant protocol ID
 * @param {object} epochSummary - Epoch summary data
 * @returns {object} Updated profile
 */
export function updateEpochSummary(protocolId, epochSummary) {
  const profile = getProfile(protocolId);
  if (!profile) {
    throw new Error(`Profile not found for ${protocolId}`);
  }

  // Find existing epoch or create new
  const existingEpochIndex = profile.epochs.findIndex(e => e.epochId === epochSummary.epochId);
  if (existingEpochIndex >= 0) {
    profile.epochs[existingEpochIndex] = epochSummary;
  } else {
    profile.epochs.push(epochSummary);
  }

  // Update last updated
  profile.lastUpdated = new Date().toISOString();

  // Recalculate dimension summary
  recalculateDimensionSummary(profile);

  // Save profile
  saveProfile(profile);

  return profile;
}

/**
 * Add achievement to profile
 * @param {string} protocolId - Participant protocol ID
 * @param {object} achievement - Achievement data
 * @returns {object} Updated profile
 */
export function addAchievement(protocolId, achievement) {
  const profile = getProfile(protocolId);
  if (!profile) {
    throw new Error(`Profile not found for ${protocolId}`);
  }

  // Ensure achievements array exists
  if (!profile.metadata.achievements) {
    profile.metadata.achievements = [];
  }

  // Generate achievement ID if not provided
  if (!achievement.achievementId) {
    achievement.achievementId = `ACH-${Date.now()}`;
  }
  if (!achievement.earnedAt) {
    achievement.earnedAt = new Date().toISOString();
  }

  // Add achievement
  profile.metadata.achievements.push(achievement);

  // Update verification status
  profile.metadata.verificationStatus = 'VERIFIED';

  // Save profile
  saveProfile(profile);

  return profile;
}

/**
 * Recalculate dimension summary from epochs
 * @param {object} profile - Profile to update
 * @private
 */
function recalculateDimensionSummary(profile) {
  const dimensions = ['contribution', 'impact', 'quality', 'persistence', 'early'];
  const allEpochs = profile.epochs.filter(e => e.participated);

  // Initialize summary
  const summary = {
    participationRate: allEpochs.length / getMaxEpochs()
  };

  // Calculate statistics for each dimension
  dimensions.forEach(dimension => {
    const scores = allEpochs
      .map(epoch => epoch.dimensions[dimension])
      .filter(score => score !== null);

    if (scores.length > 0) {
      summary[dimension] = calculateStatistics(scores);
    } else {
      summary[dimension] = {
        mean: 0,
        median: 0,
        min: 0,
        max: 0,
        stdDev: 0,
        count: 0
      };
    }
  });

  profile.dimensionSummary = summary;
}

/**
 * Calculate statistics for an array of scores
 * @param {Array<number>} scores - Array of scores
 * @returns {object} Statistics object
 */
function calculateStatistics(scores) {
  const sorted = [...scores].sort((a, b) => a - b);
  const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length;
  const median = sorted[Math.floor(sorted.length / 2)];
  const min = sorted[0];
  const max = sorted[sorted.length - 1];
  const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length;
  const stdDev = Math.sqrt(variance);

  return {
    mean: Number(mean.toFixed(2)),
    median: Number(median.toFixed(2)),
    min,
    max,
    stdDev: Number(stdDev.toFixed(2)),
    count: scores.length
  };
}

/**
 * Get maximum number of epochs (for participation rate calculation)
 * @returns {number} Maximum epochs
 */
function getMaxEpochs() {
  // This would typically come from configuration
  return 10; // Placeholder
}

/**
 * Save profile to storage
 * @param {object} profile - Profile to save
 */
function saveProfile(profile) {
  try {
    const profiles = loadProfiles();
    profiles[profile.protocolId] = profile;
    writeFileSync(PROFILE_FILE, JSON.stringify(profiles, null, 2));
  } catch (error) {
    throw new Error(`Failed to save profile: ${error.message}`);
  }
}

/**
 * Load all profiles from storage
 * @returns {object} Profiles object
 */
function loadProfiles() {
  try {
    if (existsSync(PROFILE_FILE)) {
      const data = readFileSync(PROFILE_FILE, 'utf8');
      return JSON.parse(data);
    }
    return {};
  } catch (error) {
    console.warn(`Failed to load profiles: ${error.message}`);
    return {};
  }
}

/**
 * Generate profile fingerprint for integrity
 * @param {object} profile - Profile to fingerprint
 * @returns {string} SHA-256 fingerprint
 */
export function generateProfileFingerprint(profile) {
  // Create a canonical representation of the profile
  const canonical = {
    protocolId: profile.protocolId,
    totalContributions: profile.totalContributions,
    lastUpdated: profile.lastUpdated,
    epochsCount: profile.epochs.length,
    dimensionSummary: profile.dimensionSummary,
    verificationStatus: profile.metadata.verificationStatus
  };

  const canonicalString = JSON.stringify(canonical, Object.keys(canonical).sort());
  return crypto.createHash('sha256').update(canonicalString).digest('hex');
}

/**
 * Validate profile integrity
 * @param {object} profile - Profile to validate
 * @returns {boolean} Whether profile is valid
 */
export function validateProfile(profile) {
  // Check required fields
  const required = ['profileVersion', 'protocolId', 'identityFingerprint', 'createdAt', 'lastUpdated'];
  for (const field of required) {
    if (!(field in profile)) {
      return false;
    }
  }

  // Check protocol ID format
  if (!/^mood:contributor:[a-f0-9]{64}$/.test(profile.protocolId)) {
    return false;
  }

  // Check identity fingerprint format
  if (!/^sha256:[a-f0-9]{64}$/.test(profile.identityFingerprint)) {
    return false;
  }

  // Check timestamps are valid
  const now = new Date();
  const createdAt = new Date(profile.createdAt);
  const lastUpdated = new Date(profile.lastUpdated);

  if (isNaN(createdAt.getTime()) || isNaN(lastUpdated.getTime())) {
    return false;
  }

  if (lastUpdated > now) {
    return false;
  }

  return true;
}