/**
 * MOOD Protocol Normalize Module
 *
 * Provides deterministic normalization for identity proofs and contribution data.
 * Ensures same inputs produce same normalized outputs regardless of format.
 */

import crypto from 'crypto';

/**
 * Normalize a wallet address
 * @param {string} address - Wallet address
 * @returns {string} Normalized address
 */
export function normalizeWalletAddress(address) {
  if (!address) return '';
  
  // Remove any prefix (0x, ethereum:, etc.)
  let normalized = address.toLowerCase().replace(/^(0x|ethereum:)/i, '');
  
  // Ensure proper hex format
  if (!/^[0-9a-f]{40}$/i.test(normalized)) {
    throw new Error(`Invalid wallet address format: ${address}`);
  }
  
  return normalized;
}

/**
 * Normalize an email address
 * @param {string} email - Email address
 * @returns {string} Normalized email
 */
export function normalizeEmail(email) {
  if (!email) return '';
  
  const normalized = email.toLowerCase().trim();
  
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalized)) {
    throw new Error(`Invalid email format: ${email}`);
  }
  
  return normalized;
}

/**
 * Normalize a GitHub username
 * @param {string} username - GitHub username
 * @returns {string} Normalized username
 */
export function normalizeGitHubUsername(username) {
  if (!username) return '';
  
  // Remove any prefix
  let normalized = username.toLowerCase().replace(/^github:/i, '').trim();
  
  // GitHub usernames can only contain alphanumeric characters and hyphens
  if (!/^[a-z0-9]([a-z0-9-]*[a-z0-9])?$/i.test(normalized)) {
    throw new Error(`Invalid GitHub username format: ${username}`);
  }
  
  return normalized;
}

/**
 * Normalize a Discord ID
 * @param {string} discordId - Discord ID
 * @returns {string} Normalized ID
 */
export function normalizeDiscordId(discordId) {
  if (!discordId) return '';
  
  // Remove any prefix
  let normalized = discordId.replace(/^discord:/i, '').trim();
  
  // Discord IDs are numeric
  if (!/^\d+$/.test(normalized)) {
    throw new Error(`Invalid Discord ID format: ${discordId}`);
  }
  
  return normalized;
}

/**
 * Parse and normalize an identity proof
 * @param {string} identityProof - Identity proof string
 * @returns {object} Normalized identity
 */
export function normalizeIdentityProof(identityProof) {
  if (!identityProof) {
    throw new Error('Identity proof is required');
  }

  const trimmed = identityProof.trim();
  
  // Determine type and normalize
  if (trimmed.startsWith('0x')) {
    return {
      type: 'wallet',
      original: identityProof,
      normalized: normalizeWalletAddress(trimmed),
      canonical: `wallet:${normalizeWalletAddress(trimmed)}`
    };
  } else if (trimmed.includes('@') && trimmed.includes('.')) {
    return {
      type: 'email',
      original: identityProof,
      normalized: normalizeEmail(trimmed),
      canonical: `email:${normalizeEmail(trimmed)}`
    };
  } else if (trimmed.startsWith('github:')) {
    return {
      type: 'github',
      original: identityProof,
      normalized: normalizeGitHubUsername(trimmed),
      canonical: `github:${normalizeGitHubUsername(trimmed)}`
    };
  } else if (trimmed.startsWith('discord:')) {
    return {
      type: 'discord',
      original: identityProof,
      normalized: normalizeDiscordId(trimmed),
      canonical: `discord:${normalizeDiscordId(trimmed)}`
    };
  } else {
    // Unknown type, treat as opaque identifier
    return {
      type: 'opaque',
      original: identityProof,
      normalized: trimmed.toLowerCase(),
      canonical: `opaque:${trimmed.toLowerCase()}`
    };
  }
}

/**
 * Generate canonical fingerprint for identity
 * @param {object} normalizedIdentity - Normalized identity object
 * @returns {string} SHA-256 fingerprint
 */
export function fingerprintIdentity(normalizedIdentity) {
  const canonicalString = JSON.stringify({
    type: normalizedIdentity.type,
    normalized: normalizedIdentity.normalized
  }, Object.keys({
    type: normalizedIdentity.type,
    normalized: normalizedIdentity.normalized
  }).sort());
  
  return crypto.createHash('sha256').update(canonicalString).digest('hex');
}

/**
 * Normalize contribution data for fingerprinting
 * @param {object} contribution - Contribution data
 * @returns {object} Normalized contribution
 */
export function normalizeContribution(contribution) {
  const canonical = {
    schemaVersion: contribution.schemaVersion || contribution.schema_version || '1.0.0',
    contributorId: contribution.contributor?.id || contribution.contributorId || '',
    category: contribution.category || 'unknown',
    title: (contribution.title || '').trim(),
    description: (contribution.description || '').trim(),
    submittedAt: contribution.submittedAt || contribution.submitted_at || null
  };

  // Sort keys for deterministic output
  const sortedCanonical = {};
  Object.keys(canonical).sort().forEach(key => {
    sortedCanonical[key] = canonical[key];
  });

  return sortedCanonical;
}

/**
 * Generate contribution fingerprint
 * @param {object} contribution - Contribution data
 * @returns {string} SHA-256 fingerprint
 */
export function fingerprintContribution(contribution) {
  const normalized = normalizeContribution(contribution);
  const canonicalString = JSON.stringify(normalized);
  return crypto.createHash('sha256').update(canonicalString).digest('hex');
}

/**
 * Normalize a reputation snapshot for comparison
 * @param {object} snapshot - Snapshot data
 * @returns {object} Normalized snapshot (without fingerprint)
 */
export function normalizeSnapshot(snapshot) {
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
    categoryDiversity: [...snapshot.categoryDiversity].sort(),
    confidence: snapshot.confidence,
    generatedAt: snapshot.generatedAt,
    supersedes: snapshot.supersedes
  };

  // Sort nested objects
  if (canonical.dimensions) {
    canonical.dimensions = Object.keys(canonical.dimensions).sort().reduce((obj, key) => {
      obj[key] = canonical.dimensions[key];
      return obj;
    }, {});
  }

  if (canonical.aggregate) {
    const agg = { ...canonical.aggregate };
    canonical.aggregate = Object.keys(agg).sort().reduce((obj, key) => {
      obj[key] = agg[key];
      return obj;
    }, {});
  }

  return canonical;
}

/**
 * Check if two identity proofs are equivalent
 * @param {string} proof1 - First identity proof
 * @param {string} proof2 - Second identity proof
 * @returns {boolean} Whether equivalent
 */
export function identityProofsEquivalent(proof1, proof2) {
  try {
    const norm1 = normalizeIdentityProof(proof1);
    const norm2 = normalizeIdentityProof(proof2);
    return norm1.canonical === norm2.canonical;
  } catch {
    return false;
  }
}

/**
 * Check if two contribution fingerprints are equivalent
 * @param {object} contrib1 - First contribution
 * @param {object} contrib2 - Second contribution
 * @returns {boolean} Whether equivalent
 */
export function contributionsEquivalent(contrib1, contrib2) {
  try {
    const fp1 = fingerprintContribution(contrib1);
    const fp2 = fingerprintContribution(contrib2);
    return fp1 === fp2;
  } catch {
    return false;
  }
}
