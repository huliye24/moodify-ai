/**
 * MOOD Protocol Identity Management
 *
 * Handles identity proof, fingerprint generation, and linking
 * of participant identities across contributions.
 */

import crypto from 'crypto';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

// Constants
const IDENTITY_PREFIX = 'mood:contributor:';
const FINGERPRINT_ALGORITHM = 'sha256';

/**
 * Generate protocol ID from identity proof
 * @param {string} identityProof - The identity proof data
 * @returns {string} Protocol ID
 */
export function generateProtocolId(identityProof) {
  const fingerprint = generateFingerprint(identityProof);
  return `${IDENTITY_PREFIX}${fingerprint}`;
}

/**
 * Generate SHA-256 fingerprint from identity proof
 * @param {string} identityProof - The identity proof data
 * @returns {string} Fingerprint
 */
export function generateFingerprint(identityProof) {
  return crypto.createHash(FINGERPRINT_ALGORITHM)
    .update(identityProof)
    .digest('hex');
}

/**
 * Parse identity proof to extract information
 * @param {string} identityProof - The identity proof data
 * @returns {object} Parsed identity information
 */
export function parseIdentityProof(identityProof) {
  try {
    // Handle different identity proof formats
    if (identityProof.startsWith('0x')) {
      // Ethereum-style address
      return {
        type: 'ethereum',
        address: identityProof,
        normalized: identityProof.toLowerCase()
      };
    } else if (identityProof.includes('@')) {
      // Email-based
      return {
        type: 'email',
        email: identityProof,
        normalized: identityProof.toLowerCase()
      };
    } else if (identityProof.startsWith('github:')) {
      // GitHub username
      return {
        type: 'github',
        username: identityProof.substring(6),
        normalized: identityProof.substring(6).toLowerCase()
      };
    } else if (identityProof.startsWith('discord:')) {
      // Discord ID
      return {
        type: 'discord',
        userId: identityProof.substring(8),
        normalized: identityProof.substring(8).toLowerCase()
      };
    } else {
      // Unknown type, treat as opaque string
      return {
        type: 'opaque',
        proof: identityProof,
        normalized: identityProof.toLowerCase()
      };
    }
  } catch (error) {
    throw new Error(`Failed to parse identity proof: ${error.message}`);
  }
}

/**
 * Check if two identity proofs represent the same participant
 * @param {string} proof1 - First identity proof
 * @param {string} proof2 - Second identity proof
 * @returns {boolean} Whether they match
 */
export function identityMatches(proof1, proof2) {
  if (!proof1 || !proof2) return false;

  const parsed1 = parseIdentityProof(proof1);
  const parsed2 = parseIdentityProof(proof2);

  // Direct match
  if (proof1.toLowerCase() === proof2.toLowerCase()) return true;

  // Cross-type matching logic
  switch (parsed1.type) {
    case 'ethereum':
      // Ethereum addresses can sometimes be linked to other proofs
      if (parsed2.type === 'email' && isLinkedToEthereum(parsed2.email, parsed1.address)) {
        return true;
      }
      break;

    case 'email':
      // Email can be linked to GitHub if in same organization
      if (parsed2.type === 'github' && isSameOrganization(parsed1.email, parsed2.username)) {
        return true;
      }
      break;
  }

  return false;
}

/**
 * Link multiple identity proofs to a single participant
 * @param {Array<string>} identityProofs - Array of identity proofs
 * @returns {string} Unified protocol ID
 */
export function linkIdentities(identityProofs) {
  if (!identityProofs || identityProofs.length === 0) {
    throw new Error('At least one identity proof is required');
  }

  if (identityProofs.length === 1) {
    return generateProtocolId(identityProofs[0]);
  }

  // For multiple proofs, create a composite fingerprint
  const composite = identityProofs
    .map(proof => parseIdentityProof(proof).normalized)
    .sort()
    .join('|');

  return generateProtocolId(composite);
}

/**
 * Check if identity is linked to an Ethereum address
 * @param {string} email - Email address
 * @param {string} ethAddress - Ethereum address
 * @returns {boolean} Whether linked
 */
function isLinkedToEthereum(email, ethAddress) {
  // This would check for:
  // 1. Email-Ethereum mappings in known databases
  // 2. Commit signatures matching both
  // 3. Project-specific linking rules
  // For now, return false (no automatic linking)
  return false;
}

/**
 * Check if two accounts are in the same organization
 * @param {string} email - Email address
 * @param {string} githubUsername - GitHub username
 * @returns {boolean} Whether in same organization
 */
function isSameOrganization(email, githubUsername) {
  // This would check:
  // 1. Email domain matches GitHub organization
  // 2. GitHub email matches provided email
  // For now, return false (no automatic linking)
  return false;
}

/**
 * Identity history management
 */
export class IdentityHistory {
  constructor(dataDir = './data/identity') {
    this.dataDir = dataDir;
    this.historyFile = join(dataDir, 'history.json');
    this._ensureDirectory();
  }

  _ensureDirectory() {
    if (!existsSync(this.dataDir)) {
      mkdirSync(this.dataDir, { recursive: true });
    }
  }

  /**
   * Record identity event
   * @param {object} event - Identity event
   */
  recordEvent(event) {
    const history = this._loadHistory();

    const identityEvent = {
      eventId: event.eventId || this._generateEventId(),
      timestamp: event.timestamp || new Date().toISOString(),
      eventType: event.eventType,
      identityProof: event.identityProof,
      fingerprint: event.fingerprint,
      contributionsAffected: event.contributionsAffected || 0,
      previousIdentity: event.previousIdentity || null
    };

    history.push(identityEvent);
    this._saveHistory(history);
  }

  /**
   * Get identity history for a participant
   * @param {string} protocolId - Participant protocol ID
   * @returns {Array<object>} Identity history
   */
  getHistory(protocolId) {
    const history = this._loadHistory();
    return history.filter(event =>
      event.identityProof && generateProtocolId(event.identityProof) === protocolId
    );
  }

  /**
   * Load identity history from file
   * @private
   */
  _loadHistory() {
    try {
      if (existsSync(this.historyFile)) {
        const data = readFileSync(this.historyFile, 'utf8');
        return JSON.parse(data);
      }
      return [];
    } catch (error) {
      console.warn(`Failed to load identity history: ${error.message}`);
      return [];
    }
  }

  /**
   * Save identity history to file
   * @private
   */
  _saveHistory(history) {
    try {
      writeFileSync(this.historyFile, JSON.stringify(history, null, 2));
    } catch (error) {
      throw new Error(`Failed to save identity history: ${error.message}`);
    }
  }

  /**
   * Generate unique event ID
   * @private
   */
  _generateEventId() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const random = Math.floor(Math.random() * 1000000).toString().padStart(6, '0');
    return `IDENTITY-${timestamp}-${random}`;
  }
}

/**
 * Identity conflict resolution
 * @param {Array<string>} identityProofs - Array of conflicting proofs
 * @returns {string} Resolved protocol ID
 */
export function resolveIdentityConflict(identityProofs) {
  // For now, use the first proof as canonical
  // In production, this would involve:
  // 1. Manual review
  // 2. Evidence-based resolution
  // 3. Community voting
  // 4. Time-based seniority

  if (identityProofs.length === 0) {
    throw new Error('No identity proofs provided for conflict resolution');
  }

  console.warn(`Identity conflict detected for ${identityProofs.length} proofs. Using first proof as canonical.`);

  return generateProtocolId(identityProofs[0]);
}