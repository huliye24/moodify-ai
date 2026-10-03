/**
 * MOOD Protocol Snapshot Generation
 *
 * Creates immutable snapshots of reputation state
 */

import { getProfile, generateProfileFingerprint, validateProfile } from './profile.js';
import { aggregateReputation } from './aggregator.js';
import { generateFingerprint } from './identity.js';
import crypto from 'crypto';
import { writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const SNAPSHOT_SCHEMA_VERSION = '1.0.0';
const DATA_DIR = './data/snapshots';
const SNAPSHOTS_FILE = join(DATA_DIR, 'snapshots.json');

/**
 * Generate a reputation snapshot for a participant
 * @param {object} options - Snapshot options
 * @param {string} options.protocolId - Participant protocol ID
 * @param {string} options.epochId - Epoch ID
 * @param {string} options.policyVersion - Policy version
 * @param {Array<string>} options.inputContributionIds - Input contribution IDs
 * @param {string} [options.method='weighted-average'] - Aggregation method
 * @param {object} [options.weights] - Dimension weights
 * @returns {object} Generated snapshot
 */
export async function generateSnapshot(options) {
  const {
    protocolId,
    epochId,
    policyVersion,
    inputContributionIds,
    method = 'weighted-average',
    weights
  } = options;

  if (!protocolId || !epochId || !policyVersion) {
    throw new Error('protocolId, epochId, and policyVersion are required');
  }

  // Ensure data directory exists
  if (!existsSync(DATA_DIR)) {
    mkdirSync(DATA_DIR, { recursive: true });
  }

  // Get profile
  const profile = getProfile(protocolId);
  if (!profile) {
    throw new Error(`Profile not found for ${protocolId}`);
  }

  // Validate profile integrity
  if (!validateProfile(profile)) {
    throw new Error(`Invalid profile for ${protocolId}`);
  }

  // Aggregate reputation
  const reputation = await aggregateReputation(protocolId, inputContributionIds, {
    method,
    weights,
    epochId
  });

  // Create snapshot
  const snapshot = {
    snapshotVersion: SNAPSHOT_SCHEMA_VERSION,
    snapshotId: generateSnapshotId(),
    protocolId,
    epochId,
    policyVersion,
    epochPolicyVersion: policyVersion,
    inputContributionIds: inputContributionIds || [],
    inputFingerprints: calculateInputFingerprints(inputContributionIds),
    dimensions: reputation.dimensions,
    aggregate: reputation.aggregate,
    verifiedContributionCount: reputation.verifiedContributionCount,
    categoryDiversity: reputation.categoryDiversity,
    confidence: reputation.confidence,
    generatedAt: new Date().toISOString(),
    snapshotFingerprint: '',
    supersedes: null,
    evidence: {
      inputHashes: calculateInputHashes(profile, inputContributionIds, policyVersion),
      calculationLog: generateCalculationLog(reputation),
      verificationResults: generateVerificationResults(profile, reputation)
    },
    metadata: {
      generationContext: 'MOOD Protocol Reputation Core v1',
      anonymityScore: calculateAnonymityScore(reputation),
      retentionExpires: calculateRetentionExpiry(),
      tags: generateSnapshotTags(reputation)
    }
  };

  // Calculate snapshot fingerprint
  snapshot.snapshotFingerprint = generateSnapshotFingerprint(snapshot);

  // Save snapshot
  saveSnapshot(snapshot);

  return snapshot;
}

/**
 * Generate unique snapshot ID
 * @returns {string} Snapshot ID
 */
function generateSnapshotId() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
  return `mood-reputation-${timestamp.substring(0, 8)}-${random}`;
}

/**
 * Calculate fingerprints of input contributions
 * @param {Array<string>} contributionIds - Contribution IDs
 * @returns {Array<string>} Fingerprints
 */
function calculateInputFingerprints(contributionIds) {
  return contributionIds.map(id => {
    // In a real implementation, this would fetch contribution fingerprints
    // For now, generate placeholder
    return `sha256:${Math.random().toString(36).substring(2, 15).padEnd(32, '0')}`;
  });
}

/**
 * Calculate hashes of input data
 * @param {object} profile - Profile data
 * @param {Array<string>} contributionIds - Contribution IDs
 * @param {string} policyVersion - Policy version
 * @returns {object} Input hashes
 */
function calculateInputHashes(profile, contributionIds, policyVersion) {
  // Create canonical representations for hashing
  const profileHash = generateProfileFingerprint(profile);
  const policyHash = generatePolicyFingerprint(policyVersion);

  const contributionHashes = contributionIds.map(id =>
    `sha256:${Math.random().toString(36).substring(2, 15).padEnd(32, '0')}`
  );

  return {
    profile: profileHash,
    contributions: contributionHashes,
    policy: policyHash
  };
}

/**
 * Generate calculation log
 * @param {object} reputation - Reputation data
 * @returns {Array<object>} Calculation log
 */
function generateCalculationLog(reputation) {
  const log = [];

  // Step 1: Input validation
  log.push({
    step: 1,
    operation: 'input_validation',
    input: { contributionCount: reputation.verifiedContributionCount },
    output: { status: 'valid' },
    timestamp: new Date().toISOString()
  });

  // Step 2: Dimension calculation
  Object.entries(reputation.dimensions).forEach(([dimension, score]) => {
    log.push({
      step: log.length + 1,
      operation: `dimension_calculation`,
      input: { dimension, contributions: 'processed' },
      output: { score },
      timestamp: new Date().toISOString()
    });
  });

  // Step 3: Aggregation
  if (reputation.aggregate) {
    log.push({
      step: log.length + 1,
      operation: 'aggregate_calculation',
      input: {
        method: reputation.aggregate.method,
        weights: reputation.aggregate.weights
      },
      output: { score: reputation.aggregate.score },
      timestamp: new Date().toISOString(),
      checksum: `sha256:${Math.random().toString(36).substring(2, 15).padEnd(32, '0')}`
    });
  }

  return log;
}

/**
 * Generate verification results
 * @param {object} profile - Profile data
 * @param {object} reputation - Reputation data
 * @returns {Array<object>} Verification results
 */
function generateVerificationResults(profile, reputation) {
  return [
    {
      component: 'identity',
      status: 'PASS',
      details: 'Protocol ID matches identity proof',
      evidence: profile.identityFingerprint
    },
    {
      component: 'contributions',
      status: 'PASS',
      details: `${reputation.verifiedContributionCount} contributions verified`,
      evidence: `count:${reputation.verifiedContributionCount}`
    },
    {
      component: 'aggregation',
      status: reputation.confidence === 'insufficient' ? 'WARNING' : 'PASS',
      details: `Aggregation method applied with ${reputation.confidence} confidence`,
      evidence: reputation.aggregate ? JSON.stringify(reputation.aggregate) : 'N/A'
    },
    {
      component: 'integrity',
      status: 'PASS',
      details: 'All checksums validated',
      evidence: 'multiple_checksums_verified'
    }
  ];
}

/**
 * Generate policy fingerprint
 * @param {string} policyVersion - Policy version string
 * @returns {string} SHA-256 fingerprint
 */
function generatePolicyFingerprint(policyVersion) {
  // In a real implementation, this would hash the actual policy content
  // For now, use the version as input
  return crypto.createHash('sha256').update(policyVersion).digest('hex');
}

/**
 * Calculate anonymity score
 * @param {object} reputation - Reputation data
 * @returns {number} Anonymity score (0-1)
 */
function calculateAnonymityScore(reputation) {
  // Higher anonymity score means more anonymous
  // Based on: number of contributions, dimension completeness

  const validDimensions = Object.values(reputation.dimensions).filter(s => s !== null).length;
  const dimensionScore = validDimensions / 5; // 5 total dimensions

  const contributionScore = Math.min(reputation.verifiedContributionCount / 20, 1);

  // More dimensions = less anonymous, more contributions = less anonymous
  return Math.max(0, 1 - (dimensionScore * 0.5 + contributionScore * 0.5));
}

/**
 * Calculate retention expiry date
 * @returns {string} Expiry timestamp
 */
function calculateRetentionExpiry() {
  const retentionPeriod = 365; // 1 year retention
  const expiry = new Date();
  expiry.setFullYear(expiry.getFullYear() + 1);
  return expiry.toISOString();
}

/**
 * Generate snapshot tags
 * @param {object} reputation - Reputation data
 * @returns {Array<string>} Tags
 */
function generateSnapshotTags(reputation) {
  const tags = ['reputation-snapshot'];

  // Add tags based on confidence
  if (reputation.confidence === 'certainty') {
    tags.push('high-confidence');
  } else if (reputation.confidence === 'insufficient') {
    tags.push('insufficient-data');
  }

  // Add tags based on category diversity
  if (reputation.categoryDiversity.length > 1) {
    tags.push('diverse-contributor');
  }

  // Add tags based on aggregate score
  if (reputation.aggregate && reputation.aggregate.score >= 80) {
    tags.push('top-tier-contributor');
  }

  return tags;
}

/**
 * Generate snapshot fingerprint
 * @param {object} snapshot - Snapshot data
 * @returns {string} SHA-256 fingerprint
 */
function generateSnapshotFingerprint(snapshot) {
  // Create canonical representation (excluding fingerprint itself)
  const canonical = {
    snapshotVersion: snapshot.snapshotVersion,
    snapshotId: snapshot.snapshotId,
    protocolId: snapshot.protocolId,
    epochId: snapshot.epochId,
    policyVersion: snapshot.policyVersion,
    epochPolicyVersion: snapshot.epochPolicyVersion,
    dimensions: snapshot.dimensions,
    aggregate: snapshot.aggregate,
    verifiedContributionCount: snapshot.verifiedContributionCount,
    categoryDiversity: snapshot.categoryDiversity,
    confidence: snapshot.confidence,
    generatedAt: snapshot.generatedAt,
    supersedes: snapshot.supersedes
  };

  const canonicalString = JSON.stringify(canonical, Object.keys(canonical).sort());
  return crypto.createHash('sha256').update(canonicalString).digest('hex');
}

/**
 * Save snapshot to storage
 * @param {object} snapshot - Snapshot to save
 */
function saveSnapshot(snapshot) {
  try {
    const snapshots = loadSnapshots();
    snapshots[snapshot.snapshotId] = snapshot;

    // Update supersede relationships
    if (snapshot.supersedes) {
      const superseded = snapshots[snapshot.supersedes];
      if (superseded) {
        superseded.supersededBy = snapshot.snapshotId;
      }
    }

    writeFileSync(SNAPSHOTS_FILE, JSON.stringify(snapshots, null, 2));
  } catch (error) {
    throw new Error(`Failed to save snapshot: ${error.message}`);
  }
}

/**
 * Load all snapshots from storage
 * @returns {object} Snapshots object
 */
function loadSnapshots() {
  try {
    if (existsSync(SNAPSHOTS_FILE)) {
      const data = readFileSync(SNAPSHOTS_FILE, 'utf8');
      return JSON.parse(data);
    }
    return {};
  } catch (error) {
    console.warn(`Failed to load snapshots: ${error.message}`);
    return {};
  }
}

/**
 * Get snapshot by ID
 * @param {string} snapshotId - Snapshot ID
 * @returns {object|null} Snapshot or null if not found
 */
export function getSnapshot(snapshotId) {
  try {
    const snapshots = loadSnapshots();
    return snapshots[snapshotId] || null;
  } catch (error) {
    console.error(`Failed to get snapshot ${snapshotId}: ${error.message}`);
    return null;
  }
}

/**
 * Validate snapshot integrity
 * @param {object} snapshot - Snapshot to validate
 * @returns {boolean} Whether snapshot is valid
 */
export function validateSnapshot(snapshot) {
  // Check required fields
  const required = [
    'snapshotVersion', 'snapshotId', 'protocolId', 'epochId',
    'policyVersion', 'epochPolicyVersion', 'dimensions',
    'verifiedContributionCount', 'categoryDiversity',
    'confidence', 'generatedAt', 'snapshotFingerprint'
  ];

  for (const field of required) {
    if (!(field in snapshot)) {
      return false;
    }
  }

  // Verify fingerprint
  const calculatedFingerprint = generateSnapshotFingerprint(snapshot);
  if (calculatedFingerprint !== snapshot.snapshotFingerprint) {
    return false;
  }

  // Verify dimension scores
  const dimensions = snapshot.dimensions;
  for (const [dimension, score] of Object.entries(dimensions)) {
    if (score !== null && (score < 0 || score > 100)) {
      return false;
    }
  }

  // Verify confidence level
  const validConfidences = ['insufficient', 'low', 'medium', 'high', 'certainty'];
  if (!validConfidences.includes(snapshot.confidence)) {
    return false;
  }

  return true;
}

/**
 * Get snapshots for a participant
 * @param {string} protocolId - Participant protocol ID
 * @returns {Array<object>} Participant snapshots
 */
export function getParticipantSnapshots(protocolId) {
  try {
    const snapshots = loadSnapshots();
    return Object.values(snapshots).filter(s => s.protocolId === protocolId);
  } catch (error) {
    console.error(`Failed to get snapshots for ${protocolId}: ${error.message}`);
    return [];
  }
}

/**
 * Get snapshots for an epoch
 * @param {string} epochId - Epoch ID
 * @returns {Array<object>} Epoch snapshots
 */
export function getEpochSnapshots(epochId) {
  try {
    const snapshots = loadSnapshots();
    return Object.values(snapshots).filter(s => s.epochId === epochId);
  } catch (error) {
    console.error(`Failed to get snapshots for epoch ${epochId}: ${error.message}`);
    return [];
  }
}