/**
 * MOOD Protocol Node Capability Manifest
 *
 * Manages capability declarations and verification states.
 * Declaration is separate from verification.
 */

import crypto from 'crypto';

// Capability verification statuses
export const VERIFICATION_STATUS = {
  DECLARED: 'declared',
  VERIFIED: 'verified',
  PARTIALLY_VERIFIED: 'partially_verified',
  UNVERIFIED: 'unverified',
  REJECTED: 'rejected'
};

// Visibility levels
export const VISIBILITY = {
  PUBLIC: 'public',
  RESTRICTED: 'restricted'
};

// Known capability namespaces
export const CAPABILITY_NAMESPACES = {
  COMPUTE: 'compute',
  STORAGE: 'storage',
  DATA: 'data',
  VALIDATION: 'validation',
  GATEWAY: 'gateway',
  DEVELOPER: 'developer'
};

// Known capability keys by type
export const CAPABILITY_KEYS = {
  compute: [
    'compute.cpu.arch',
    'compute.cpu.capacity_class',
    'compute.gpu.model',
    'compute.gpu.count',
    'compute.memory.capacity_class',
    'compute.runtime.python',
    'compute.runtime.node',
    'compute.runtime.container',
    'compute.max_job_class'
  ],
  storage: [
    'storage.protocol.s3',
    'storage.protocol.ipfs',
    'storage.capacity_class',
    'storage.retention_days'
  ],
  data: [
    'data.category',
    'data.access_mode',
    'data.provenance',
    'data.license_class'
  ],
  validation: [
    'validation.type',
    'validation.benchmark_suite',
    'validation.runtime'
  ],
  gateway: [
    'gateway.protocol_version',
    'gateway.ingress',
    'gateway.egress'
  ],
  developer: [
    'developer.repository',
    'developer.domain',
    'developer.github_id'
  ]
};

/**
 * Create a new capability manifest
 * @param {object} options - Manifest options
 * @param {string} options.nodeId - Node ID
 * @param {string} options.nodeType - Node type
 * @param {Array<string>} options.protocolVersions - Supported protocol versions
 * @param {Array<object>} options.capabilities - Capability declarations
 * @returns {object} Capability manifest
 */
export function createCapabilityManifest(options) {
  const { nodeId, nodeType, protocolVersions, capabilities = [] } = options;

  if (!nodeId) {
    throw new Error('nodeId is required');
  }

  if (!nodeType) {
    throw new Error('nodeType is required');
  }

  const manifest = {
    schemaVersion: '1.0.0',
    manifestId: generateManifestId(nodeId, capabilities),
    nodeId,
    nodeType,
    protocolVersions: protocolVersions || ['0.1'],
    capabilities: capabilities.map(cap => normalizeCapability(cap)),
    createdAt: new Date().toISOString(),
    fingerprint: ''
  };

  // Calculate fingerprint
  manifest.fingerprint = generateManifestFingerprint(manifest);

  return manifest;
}

/**
 * Generate capability manifest ID
 * @param {string} nodeId - Node ID
 * @param {Array} capabilities - Capabilities
 * @returns {string} Manifest ID
 */
function generateManifestId(nodeId, capabilities) {
  const input = `${nodeId}|${capabilities.length}|${Date.now()}`;
  const hash = crypto.createHash('sha256').update(input).digest('hex');
  return `mood:capability:${hash}`;
}

/**
 * Normalize a capability entry
 * @param {object} capability - Capability to normalize
 * @returns {object} Normalized capability
 */
export function normalizeCapability(capability) {
  return {
    key: capability.key,
    value: capability.value,
    visibility: capability.visibility || VISIBILITY.PUBLIC,
    verificationStatus: capability.verificationStatus || VERIFICATION_STATUS.DECLARED,
    evidenceIds: capability.evidenceIds || []
  };
}

/**
 * Generate manifest fingerprint
 * @param {object} manifest - Manifest (without fingerprint)
 * @returns {string} SHA-256 fingerprint
 */
export function generateManifestFingerprint(manifest) {
  const canonical = {
    nodeId: manifest.nodeId,
    nodeType: manifest.nodeType,
    protocolVersions: [...manifest.protocolVersions].sort(),
    capabilities: manifest.capabilities.map(cap => ({
      key: cap.key,
      value: cap.value,
      visibility: cap.visibility,
      verificationStatus: cap.verificationStatus
      // evidenceIds excluded - evidence is separate
    })).sort((a, b) => a.key.localeCompare(b.key))
  };

  const canonicalString = JSON.stringify(canonical);
  return `sha256:${crypto.createHash('sha256').update(canonicalString).digest('hex')}`;
}

/**
 * Add a capability to manifest
 * @param {object} manifest - Current manifest
 * @param {object} capability - Capability to add
 * @returns {object} Updated manifest
 */
export function addCapability(manifest, capability) {
  const normalized = normalizeCapability(capability);

  // Check for duplicate key
  const existingIndex = manifest.capabilities.findIndex(c => c.key === normalized.key);
  if (existingIndex >= 0) {
    manifest.capabilities[existingIndex] = normalized;
  } else {
    manifest.capabilities.push(normalized);
  }

  // Recalculate fingerprint
  manifest.fingerprint = generateManifestFingerprint(manifest);

  return manifest;
}

/**
 * Update capability verification status
 * @param {object} manifest - Current manifest
 * @param {string} capabilityKey - Capability key
 * @param {string} status - New verification status
 * @param {string} [evidenceId] - Evidence ID
 * @returns {object} Updated manifest
 */
export function updateCapabilityVerification(manifest, capabilityKey, status, evidenceId) {
  const capability = manifest.capabilities.find(c => c.key === capabilityKey);

  if (!capability) {
    throw new Error(`Capability not found: ${capabilityKey}`);
  }

  capability.verificationStatus = status;

  if (evidenceId) {
    capability.evidenceIds.push(evidenceId);
  }

  // Recalculate fingerprint
  manifest.fingerprint = generateManifestFingerprint(manifest);

  return manifest;
}

/**
 * Get capabilities by verification status
 * @param {object} manifest - Capability manifest
 * @param {string} status - Verification status
 * @returns {Array<object>} Matching capabilities
 */
export function getCapabilitiesByStatus(manifest, status) {
  return manifest.capabilities.filter(c => c.verificationStatus === status);
}

/**
 * Get verified capabilities
 * @param {object} manifest - Capability manifest
 * @returns {Array<object>} Verified capabilities
 */
export function getVerifiedCapabilities(manifest) {
  return getCapabilitiesByStatus(manifest, VERIFICATION_STATUS.VERIFIED);
}

/**
 * Get declared (unverified) capabilities
 * @param {object} manifest - Capability manifest
 * @returns {Array<object>} Declared capabilities
 */
export function getDeclaredCapabilities(manifest) {
  return getCapabilitiesByStatus(manifest, VERIFICATION_STATUS.DECLARED);
}

/**
 * Check if manifest has verified capabilities
 * @param {object} manifest - Capability manifest
 * @returns {boolean} Whether has verified capabilities
 */
export function hasVerifiedCapabilities(manifest) {
  return manifest.capabilities.some(c =>
    c.verificationStatus === VERIFICATION_STATUS.VERIFIED
  );
}

/**
 * Validate capability key format
 * @param {string} key - Capability key
 * @returns {boolean} Whether valid format
 */
export function isValidCapabilityKey(key) {
  const pattern = /^[a-z0-9_.-]+$/;
  return pattern.test(key);
}

/**
 * Validate capability value is not secret
 * @param {string} key - Capability key
 * @param {any} value - Capability value
 * @returns {object} Validation result
 */
export function validateCapabilityValue(key, value) {
  // Keys that should not contain sensitive values
  const sensitiveKeys = [
    'password',
    'secret',
    'key',
    'token',
    'credential'
  ];

  const isSensitive = sensitiveKeys.some(sensitive =>
    key.toLowerCase().includes(sensitive)
  );

  if (isSensitive && typeof value === 'string' && value.length > 0) {
    return {
      valid: false,
      error: `Capability key '${key}' should not contain sensitive values`
    };
  }

  return { valid: true };
}

export default {
  VERIFICATION_STATUS,
  VISIBILITY,
  CAPABILITY_NAMESPACES,
  CAPABILITY_KEYS,
  createCapabilityManifest,
  normalizeCapability,
  generateManifestFingerprint,
  addCapability,
  updateCapabilityVerification,
  getCapabilitiesByStatus,
  getVerifiedCapabilities,
  getDeclaredCapabilities,
  hasVerifiedCapabilities,
  isValidCapabilityKey,
  validateCapabilityValue
};
