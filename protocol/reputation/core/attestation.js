/**
 * MOOD Protocol Attestation Module
 *
 * Handles third-party attestations for reputation snapshots.
 * Attestations are evidence of verification, not automatic reputation gains.
 */

import crypto from 'crypto';
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const ATTESTATION_SCHEMA_VERSION = '1.0.0';
const DATA_DIR = './data/attestations';
const ATTESTATIONS_FILE = join(DATA_DIR, 'attestations.json');

/**
 * Create an attestation for a reputation snapshot
 * @param {object} options - Attestation options
 * @param {string} options.snapshotId - Snapshot ID to attest
 * @param {string} options.snapshotFingerprint - Snapshot fingerprint
 * @param {object} options.attestor - Attestor information
 * @param {string} options.method - Attestation method
 * @param {Array} options.evidence - Supporting evidence
 * @returns {object} Created attestation
 */
export async function createAttestation(options) {
  const { snapshotId, snapshotFingerprint, attestor, method, evidence = [] } = options;

  if (!snapshotId || !snapshotFingerprint || !attestor || !method) {
    throw new Error('snapshotId, snapshotFingerprint, attestor, and method are required');
  }

  // Ensure data directory exists
  if (!existsSync(DATA_DIR)) {
    mkdirSync(DATA_DIR, { recursive: true });
  }

  // Create attestation
  const attestation = {
    attestationVersion: ATTESTATION_SCHEMA_VERSION,
    attestationId: generateAttestationId(),
    snapshotId,
    snapshotFingerprint,
    attestor: {
      type: attestor.type || 'unknown',
      id: attestor.id,
      displayName: attestor.displayName || null
    },
    method,
    createdAt: new Date().toISOString(),
    evidence,
    attestationFingerprint: ''
  };

  // Calculate attestation fingerprint
  attestation.attestationFingerprint = calculateAttestationFingerprint(attestation);

  // Save attestation
  saveAttestation(attestation);

  return attestation;
}

/**
 * Generate unique attestation ID
 * @returns {string} Attestation ID
 */
function generateAttestationId() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
  return `mood-attestation-${timestamp.substring(0, 8)}-${random}`;
}

/**
 * Calculate attestation fingerprint
 * @param {object} attestation - Attestation data
 * @returns {string} SHA-256 fingerprint
 */
function calculateAttestationFingerprint(attestation) {
  const canonical = {
    attestationVersion: attestation.attestationVersion,
    snapshotId: attestation.snapshotId,
    snapshotFingerprint: attestation.snapshotFingerprint,
    attestor: attestation.attestor,
    method: attestation.method,
    createdAt: attestation.createdAt
  };

  const canonicalString = JSON.stringify(canonical, Object.keys(canonical).sort());
  return `sha256:${crypto.createHash('sha256').update(canonicalString).digest('hex')}`;
}

/**
 * Get attestation by ID
 * @param {string} attestationId - Attestation ID
 * @returns {object|null} Attestation or null
 */
export function getAttestation(attestationId) {
  try {
    const attestations = loadAttestations();
    return attestations[attestationId] || null;
  } catch (error) {
    console.error(`Failed to get attestation ${attestationId}: ${error.message}`);
    return null;
  }
}

/**
 * Get attestations for a snapshot
 * @param {string} snapshotId - Snapshot ID
 * @returns {Array} Array of attestations
 */
export function getSnapshotAttestations(snapshotId) {
  try {
    const attestations = loadAttestations();
    return Object.values(attestations).filter(a => a.snapshotId === snapshotId);
  } catch (error) {
    console.error(`Failed to get attestations for snapshot ${snapshotId}: ${error.message}`);
    return [];
  }
}

/**
 * Verify attestation integrity
 * @param {object} attestation - Attestation to verify
 * @returns {object} Verification result
 */
export function verifyAttestation(attestation) {
  // Check required fields
  const required = [
    'attestationVersion',
    'attestationId',
    'snapshotId',
    'snapshotFingerprint',
    'attestor',
    'method',
    'createdAt',
    'attestationFingerprint'
  ];

  for (const field of required) {
    if (!(field in attestation)) {
      return { valid: false, error: `Missing required field: ${field}` };
    }
  }

  // Verify fingerprint
  const calculatedFingerprint = calculateAttestationFingerprint(attestation);
  if (calculatedFingerprint !== attestation.attestationFingerprint) {
    return { valid: false, error: 'Fingerprint mismatch - attestation may have been tampered with' };
  }

  // Verify schema version
  if (attestation.attestationVersion !== ATTESTATION_SCHEMA_VERSION) {
    return { valid: false, error: `Invalid schema version: ${attestation.attestationVersion}` };
  }

  return { valid: true };
}

/**
 * List all attestations
 * @returns {Array} All attestations
 */
export function listAttestations() {
  try {
    const attestations = loadAttestations();
    return Object.values(attestations);
  } catch (error) {
    console.error(`Failed to list attestations: ${error.message}`);
    return [];
  }
}

/**
 * Save attestation to storage
 * @param {object} attestation - Attestation to save
 */
function saveAttestation(attestation) {
  try {
    const attestations = loadAttestations();
    attestations[attestation.attestationId] = attestation;
    writeFileSync(ATTESTATIONS_FILE, JSON.stringify(attestations, null, 2));
  } catch (error) {
    throw new Error(`Failed to save attestation: ${error.message}`);
  }
}

/**
 * Load attestations from storage
 * @returns {object} Attestations object
 */
function loadAttestations() {
  try {
    if (existsSync(ATTESTATIONS_FILE)) {
      const data = readFileSync(ATTESTATIONS_FILE, 'utf8');
      return JSON.parse(data);
    }
    return {};
  } catch (error) {
    console.warn(`Failed to load attestations: ${error.message}`);
    return {};
  }
}

/**
 * Create attestation from repository commit evidence
 * @param {object} snapshot - Snapshot to attest
 * @param {object} reviewer - Reviewer information
 * @returns {object} Created attestation
 */
export async function attestFromCommitEvidence(snapshot, reviewer) {
  return createAttestation({
    snapshotId: snapshot.snapshotId,
    snapshotFingerprint: snapshot.snapshotFingerprint,
    attestor: {
      type: 'repository_reviewer',
      id: reviewer.id,
      displayName: reviewer.displayName || reviewer.id
    },
    method: 'repository_record',
    evidence: [
      {
        type: 'commit_evidence',
        description: 'Attestation based on repository commit record',
        snapshotId: snapshot.snapshotId,
        snapshotFingerprint: snapshot.snapshotFingerprint,
        timestamp: new Date().toISOString()
      }
    ]
  });
}

/**
 * Create local attestation (unsigned, for local testing)
 * @param {object} snapshot - Snapshot to attest
 * @param {string} attestorId - Attestor ID
 * @returns {object} Created attestation
 */
export async function createLocalAttestation(snapshot, attestorId) {
  return createAttestation({
    snapshotId: snapshot.snapshotId,
    snapshotFingerprint: snapshot.snapshotFingerprint,
    attestor: {
      type: 'local',
      id: attestorId
    },
    method: 'local_observation',
    evidence: []
  });
}

/**
 * Validate attestation does not grant automatic reputation
 * @param {object} attestation - Attestation to validate
 * @returns {object} Validation result
 */
export function validateAttestationPolicy(attestation) {
  const issues = [];

  // Attestation should not contain reputation claims
  if (attestation.reputationGain) {
    issues.push('Attestation must not contain automatic reputation gain');
  }

  if (attestation.tokenAmount) {
    issues.push('Attestation must not contain token amounts');
  }

  if (attestation.votingPower) {
    issues.push('Attestation must not grant voting power');
  }

  return {
    valid: issues.length === 0,
    issues
  };
}
