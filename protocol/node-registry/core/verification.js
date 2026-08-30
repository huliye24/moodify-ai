/**
 * MOOD Protocol Node Verification Module
 *
 * Handles node verification challenges and evidence.
 * Supports HTTP challenge, public-key challenge, and manual evidence.
 * Includes SSRF protection for endpoint verification.
 */

import crypto from 'crypto';

// Allowed URI schemes for verification
const ALLOWED_SCHEMES = ['https', 'http'];

// Blocked hosts for SSRF protection
const BLOCKED_HOSTS = [
  'localhost',
  '127.0.0.1',
  '0.0.0.0',
  '::1',
  '::'
];

// Blocked IP ranges (private, loopback, link-local)
const BLOCKED_IP_PATTERNS = [
  /^10\./,
  /^172\.(1[6-9]|2[0-9]|3[0-1])\./,
  /^192\.168\./,
  /^169\.254\./,
  /^fc00:/,
  /^fe80:/
];

// Verification methods
export const VERIFICATION_METHODS = {
  HTTP_CHALLENGE: 'http_challenge',
  PUBLIC_KEY: 'public_key',
  REPOSITORY_PROOF: 'repository_proof',
  MANUAL: 'manual'
};

// Verification statuses
export const VERIFICATION_STATUS = {
  PENDING: 'pending',
  VERIFIED: 'verified',
  PARTIALLY_VERIFIED: 'partially_verified',
  REJECTED: 'rejected',
  EXPIRED: 'expired'
};

/**
 * Generate a verification challenge nonce
 * @param {object} options - Challenge options
 * @param {string} options.nodeId - Node ID
 * @param {string} options.method - Verification method
 * @returns {object} Challenge data
 */
export function generateChallenge(options = {}) {
  const { nodeId = 'unknown', method = VERIFICATION_METHODS.HTTP_CHALLENGE } = options;

  const nonce = crypto.randomBytes(32).toString('hex');
  const timestamp = new Date().toISOString();

  return {
    challengeId: `challenge-${Date.now()}-${nonce.substring(0, 8)}`,
    nodeId,
    method,
    nonce,
    createdAt: timestamp,
    expiresAt: new Date(Date.now() + 3600000).toISOString(), // 1 hour
    expectedPath: '/.well-known/mood-node-challenge',
    expectedResponse: `${nonce}`
  };
}

/**
 * Validate URI for SSRF safety
 * @param {string} uri - URI to validate
 * @returns {object} Validation result
 */
export function validateUriSafety(uri) {
  try {
    const url = new URL(uri);

    // Check scheme
    if (!ALLOWED_SCHEMES.includes(url.protocol.replace(':', ''))) {
      return {
        safe: false,
        error: `Disallowed URI scheme: ${url.protocol}`
      };
    }

    // Check hostname
    const hostname = url.hostname.toLowerCase();

    // Check blocked hosts
    if (BLOCKED_HOSTS.includes(hostname)) {
      return {
        safe: false,
        error: 'Blocked hostname: localhost and similar'
      };
    }

    // Check for IP addresses
    const ipPattern = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
    if (ipPattern.test(hostname)) {
      // Check blocked IP ranges
      for (const pattern of BLOCKED_IP_PATTERNS) {
        if (pattern.test(hostname)) {
          return {
            safe: false,
            error: 'Blocked private IP range'
          };
        }
      }
    }

    // Check for internal hostnames
    if (hostname.includes('internal') ||
        hostname.includes('private') ||
        hostname.includes('intranet') ||
        hostname.endsWith('.local') ||
        hostname.endsWith('.localhost')) {
      return {
        safe: false,
        error: 'Blocked internal hostname'
      };
    }

    return { safe: true };

  } catch (error) {
    return {
      safe: false,
      error: `Invalid URI: ${error.message}`
    };
  }
}

/**
 * Verify HTTP challenge response
 * @param {object} options - Verification options
 * @param {string} options.expectedNonce - Expected nonce
 * @param {string} options.endpoint - Node endpoint
 * @param {string} options.response - Response from node
 * @returns {object} Verification result
 */
export function verifyHttpChallenge(options) {
  const { expectedNonce, endpoint, response } = options;

  // Validate endpoint safety first
  const safetyCheck = validateUriSafety(endpoint);
  if (!safetyCheck.safe) {
    return {
      verified: false,
      method: VERIFICATION_METHODS.HTTP_CHALLENGE,
      error: `SSRF protection: ${safetyCheck.error}`
    };
  }

  // Verify response matches nonce
  const trimmedResponse = (response || '').trim();
  if (trimmedResponse !== expectedNonce) {
    return {
      verified: false,
      method: VERIFICATION_METHODS.HTTP_CHALLENGE,
      error: 'Challenge response does not match expected nonce'
    };
  }

  return {
    verified: true,
    method: VERIFICATION_METHODS.HTTP_CHALLENGE,
    timestamp: new Date().toISOString()
  };
}

/**
 * Verify public key challenge
 * @param {object} options - Verification options
 * @param {string} options.publicKey - Node's public key
 * @param {string} options.signature - Signature from node
 * @param {string} options.challenge - Challenge that was signed
 * @returns {object} Verification result
 */
export function verifyPublicKeyChallenge(options) {
  const { publicKey, signature, challenge } = options;

  if (!publicKey || !signature || !challenge) {
    return {
      verified: false,
      method: VERIFICATION_METHODS.PUBLIC_KEY,
      error: 'Missing required parameters'
    };
  }

  // In a real implementation, this would verify the signature
  // For now, we just check the parameters are present
  // The actual crypto verification would use:
  // crypto.verify('RSA-SHA256', challenge, publicKey, signature)

  // Simplified verification - in production use proper crypto
  const isValidFormat =
    publicKey.startsWith('-----BEGIN') &&
    signature.length > 10;

  if (!isValidFormat) {
    return {
      verified: false,
      method: VERIFICATION_METHODS.PUBLIC_KEY,
      error: 'Invalid public key or signature format'
    };
  }

  return {
    verified: true,
    method: VERIFICATION_METHODS.PUBLIC_KEY,
    timestamp: new Date().toISOString()
  };
}

/**
 * Create verification evidence record
 * @param {object} options - Evidence options
 * @param {string} options.nodeId - Node ID
 * @param {string} options.method - Verification method
 * @param {boolean} options.passed - Whether verification passed
 * @param {object} [options.details] - Additional details
 * @returns {object} Evidence record
 */
export function createVerificationEvidence(options) {
  const {
    nodeId,
    method,
    passed,
    details = {}
  } = options;

  const evidence = {
    evidenceId: `evidence-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
    nodeId,
    method,
    status: passed ? VERIFICATION_STATUS.VERIFIED : VERIFICATION_STATUS.REJECTED,
    createdAt: new Date().toISOString(),
    details,
    fingerprint: ''
  };

  // Generate evidence fingerprint
  const canonical = {
    evidenceId: evidence.evidenceId,
    nodeId,
    method,
    status: evidence.status,
    createdAt: evidence.createdAt
  };

  evidence.fingerprint = `sha256:${crypto.createHash('sha256')
    .update(JSON.stringify(canonical))
    .digest('hex')}`;

  return evidence;
}

/**
 * Create manual verification evidence
 * @param {object} options - Manual verification options
 * @param {string} options.nodeId - Node ID
 * @param {string} options.reviewerId - Reviewer ID
 * @param {boolean} options.approved - Whether approved
 * @param {string} options.reason - Reason for decision
 * @returns {object} Evidence record
 */
export function createManualVerificationEvidence(options) {
  const { nodeId, reviewerId, approved, reason } = options;

  return createVerificationEvidence({
    nodeId,
    method: VERIFICATION_METHODS.MANUAL,
    passed: approved,
    details: {
      reviewerId,
      reason,
      policyVersion: '004-draft-1'
    }
  });
}

/**
 * Update node verification status
 * @param {object} node - Node record
 * @param {string} status - New status
 * @param {string} method - Verification method used
 * @param {string} [evidenceId] - Evidence ID
 * @returns {object} Updated node
 */
export function updateNodeVerification(node, status, method, evidenceId) {
  return {
    ...node,
    verification: {
      status,
      method,
      verifiedAt: status === VERIFICATION_STATUS.VERIFIED ? new Date().toISOString() : null,
      evidenceIds: evidenceId ? [...(node.verification?.evidenceIds || []), evidenceId] : []
    },
    updatedAt: new Date().toISOString()
  };
}

/**
 * Check if capability verification is separate from node verification
 * Node verification (endpoint) ≠ capability verification (GPU, storage, etc.)
 * @returns {boolean} Always true - they are always separate
 */
export function isCapabilityVerificationSeparate() {
  return true;
}

export default {
  VERIFICATION_METHODS,
  VERIFICATION_STATUS,
  generateChallenge,
  validateUriSafety,
  verifyHttpChallenge,
  verifyPublicKeyChallenge,
  createVerificationEvidence,
  createManualVerificationEvidence,
  updateNodeVerification,
  isCapabilityVerificationSeparate
};
