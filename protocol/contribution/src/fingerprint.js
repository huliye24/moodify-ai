/**
 * MOOD Protocol Content Fingerprinting
 *
 * SHA-256 fingerprinting of contribution content.
 * The same canonical input always produces the same fingerprint.
 */

import crypto from 'crypto';
import { normalizeContribution } from './normalize.js';

const ALGORITHM = 'sha256';
const PREFIX = 'sha256';

/**
 * Compute the SHA-256 content fingerprint of a contribution record.
 * The fingerprint is derived from the canonically normalized form,
 * excluding mutable fields (review, scores, status, reputationEvidence).
 *
 * @param {object} contribution - Raw contribution record
 * @returns {string} Fingerprint in form "sha256:<hex>"
 */
export function computeContentFingerprint(contribution) {
  if (!contribution) {
    throw new Error('Contribution is required for fingerprinting');
  }

  const canonical = normalizeContribution(contribution);
  const digest = crypto.createHash(ALGORITHM).update(canonical).digest('hex');

  return `${PREFIX}:${digest}`;
}

/**
 * Compute the fingerprint of a raw string (e.g., evidence content).
 *
 * @param {string} content - Raw string content
 * @returns {string} Fingerprint in form "sha256:<hex>"
 */
export function computeFingerprint(content) {
  if (typeof content !== 'string') {
    throw new Error('Content must be a string');
  }
  const digest = crypto.createHash(ALGORITHM).update(content).digest('hex');
  return `${PREFIX}:${digest}`;
}

/**
 * Verify that a stored fingerprint matches the recomputed fingerprint
 * of the contribution.
 *
 * @param {object} contribution - Contribution record
 * @returns {boolean} Whether the stored fingerprint matches
 */
export function verifyFingerprint(contribution) {
  if (!contribution || !contribution.contentFingerprint) {
    return false;
  }
  const computed = computeContentFingerprint(contribution);
  return computed === contribution.contentFingerprint;
}

/**
 * Check if a fingerprint string is valid.
 *
 * @param {string} fingerprint - Fingerprint string
 * @returns {boolean} Whether format is "sha256:<64-hex>"
 */
export function isValidFingerprint(fingerprint) {
  if (typeof fingerprint !== 'string') return false;
  return /^sha256:[0-9a-f]{64}$/i.test(fingerprint);
}

/**
 * Build the artifact fingerprint of a reputation evidence object.
 * This hashes all fields except artifactFingerprint itself.
 *
 * @param {object} evidence - Reputation evidence object
 * @returns {string} Artifact fingerprint "sha256:<hex>"
 */
export function computeArtifactFingerprint(evidence) {
  if (!evidence) {
    throw new Error('Evidence object is required');
  }

  // Canonical representation excluding the artifact fingerprint itself
  const { artifactFingerprint, ...rest } = evidence;

  // Sort keys for deterministic output
  const canonical = JSON.stringify(sortObjectKeys(rest));
  const digest = crypto.createHash(ALGORITHM).update(canonical).digest('hex');

  return `${PREFIX}:${digest}`;
}

/**
 * Sort object keys recursively.
 *
 * @param {any} obj - Value to sort
 * @returns {any} Sorted value
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
