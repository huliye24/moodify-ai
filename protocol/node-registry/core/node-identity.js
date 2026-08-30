/**
 * MOOD Protocol Node Identity Module
 *
 * Generates stable node IDs independent of infrastructure location.
 * Node IDs must remain stable when IP/endpoint changes.
 */

import crypto from 'crypto';

// Constants
const NODE_ID_PREFIX = 'mood:node:';
const NODE_ID_VERSION = '1';

/**
 * Node ID types supported
 */
export const NODE_TYPES = [
  'developer',
  'compute',
  'data',
  'storage',
  'validation',
  'gateway'
];

/**
 * Generate a stable node ID from identity components
 * @param {object} options - Node identity options
 * @param {string} options.operatorProtocolId - Operator's protocol ID
 * @param {string} options.nodeType - Node type
 * @param {string} [options.stableNonce] - Stable public nonce (optional)
 * @returns {string} Stable node ID
 */
export function generateNodeId(options) {
  const { operatorProtocolId, nodeType, stableNonce = '' } = options;

  if (!operatorProtocolId) {
    throw new Error('operatorProtocolId is required');
  }

  if (!NODE_TYPES.includes(nodeType)) {
    throw new Error(`Invalid node type: ${nodeType}`);
  }

  // Create deterministic input for hashing
  const input = [
    NODE_ID_VERSION,
    operatorProtocolId,
    nodeType,
    stableNonce
  ].join('|');

  const hash = crypto.createHash('sha256').update(input).digest('hex');

  return `${NODE_ID_PREFIX}${hash}`;
}

/**
 * Generate a stable nonce for node identity
 * @returns {string} Random but stable nonce (not a secret)
 */
export function generateStableNonce() {
  return crypto.randomBytes(16).toString('hex');
}

/**
 * Parse a node ID
 * @param {string} nodeId - Node ID to parse
 * @returns {object|null} Parsed node ID components
 */
export function parseNodeId(nodeId) {
  if (!nodeId || !nodeId.startsWith(NODE_ID_PREFIX)) {
    return null;
  }

  const hash = nodeId.substring(NODE_ID_PREFIX.length);

  if (hash.length !== 64) {
    return null;
  }

  // Hash itself doesn't contain decomposed info, but we can validate format
  return {
    prefix: NODE_ID_PREFIX,
    hash,
    format: 'valid'
  };
}

/**
 * Validate node ID format
 * @param {string} nodeId - Node ID to validate
 * @returns {boolean} Whether valid
 */
export function isValidNodeId(nodeId) {
  if (!nodeId || typeof nodeId !== 'string') {
    return false;
  }

  const pattern = /^mood:node:[0-9a-f]{64}$/;
  return pattern.test(nodeId);
}

/**
 * Validate operator protocol ID format
 * @param {string} protocolId - Protocol ID to validate
 * @returns {boolean} Whether valid
 */
export function isValidOperatorProtocolId(protocolId) {
  if (!protocolId || typeof protocolId !== 'string') {
    return false;
  }

  const pattern = /^mood:contributor:[0-9a-f]{64}$/;
  return pattern.test(protocolId);
}

/**
 * Generate node record fingerprint
 * Excludes ephemeral health data to maintain stable identity
 * @param {object} nodeRecord - Node record (without fingerprint)
 * @returns {string} SHA-256 fingerprint
 */
export function generateNodeFingerprint(nodeRecord) {
  // Canonical representation excludes:
  // - health.observedAt (ephemeral)
  // - updatedAt (changes on any update)
  // - any temporary state

  const canonical = {
    nodeId: nodeRecord.nodeId,
    operatorProtocolId: nodeRecord.operatorProtocolId,
    nodeType: nodeRecord.nodeType,
    displayName: nodeRecord.displayName,
    region: nodeRecord.region,
    endpoint: nodeRecord.endpoint,
    capabilityManifestId: nodeRecord.capabilityManifestId,
    lifecycleStatus: nodeRecord.lifecycleStatus,
    registeredAt: nodeRecord.registeredAt
  };

  const canonicalString = JSON.stringify(canonical, Object.keys(canonical).sort());
  return `sha256:${crypto.createHash('sha256').update(canonicalString).digest('hex')}`;
}

/**
 * Check if node ID matches operator
 * @param {string} nodeId - Node ID
 * @param {string} operatorProtocolId - Operator protocol ID
 * @returns {boolean} Whether operator owns node
 */
export function isNodeOwnedByOperator(nodeId, operatorProtocolId) {
  // This requires querying the node record to verify operator
  // This function just validates format compatibility
  return isValidNodeId(nodeId) && isValidOperatorProtocolId(operatorProtocolId);
}

export default {
  NODE_TYPES,
  generateNodeId,
  generateStableNonce,
  parseNodeId,
  isValidNodeId,
  isValidOperatorProtocolId,
  generateNodeFingerprint
};
