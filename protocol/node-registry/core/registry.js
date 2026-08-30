/**
 * MOOD Protocol Node Registry Core
 *
 * Central registry for node records with discovery capabilities.
 */

import crypto from 'crypto';
import { generateNodeId, generateNodeFingerprint, isValidNodeId, NODE_TYPES } from './node-identity.js';
import { LIFECYCLE_STATES, executeTransition, createLifecycleHistoryEntry, isTerminalState } from './lifecycle.js';
import { createCapabilityManifest } from './capability.js';
import { VERIFICATION_STATUS } from './verification.js';
import { HEALTH_STATUS } from './health.js';

// Default node policy
const DEFAULT_NODE_POLICY = {
  nodePolicyVersion: '004-draft-1',
  status: 'draft',
  nodeTypes: NODE_TYPES,
  publicLocationDefaultPrecision: 'country',
  endpointRequiredByType: {
    developer: false,
    compute: true,
    data: false,
    storage: true,
    validation: true,
    gateway: true
  },
  capabilityVerificationRequiredForActive: false
};

/**
 * Create a new node record
 * @param {object} options - Node options
 * @param {string} options.operatorProtocolId - Operator's protocol ID
 * @param {string} options.nodeType - Node type
 * @param {string} [options.displayName] - Display name
 * @param {object} [options.region] - Region information
 * @param {object} [options.endpoint] - Endpoint information
 * @param {object} [options.capabilities] - Capability declarations
 * @returns {object} Created node record
 */
export function createNode(options) {
  const {
    operatorProtocolId,
    nodeType,
    displayName = null,
    region = null,
    endpoint = null,
    capabilities = []
  } = options;

  // Generate stable node ID
  const nodeId = generateNodeId({
    operatorProtocolId,
    nodeType,
    stableNonce: generateNodeIdStableNonce()
  });

  // Create capability manifest if capabilities provided
  let capabilityManifestId = null;
  if (capabilities.length > 0) {
    const manifest = createCapabilityManifest({
      nodeId,
      nodeType,
      protocolVersions: ['0.1'],
      capabilities
    });
    capabilityManifestId = manifest.manifestId;
  }

  const now = new Date().toISOString();

  const node = {
    schemaVersion: '1.0.0',
    nodeId,
    operatorProtocolId,
    nodeType,
    displayName,
    region: region || {
      countryCode: null,
      regionCode: null,
      city: null,
      precision: 'hidden'
    },
    endpoint,
    capabilityManifestId,
    verification: {
      status: 'pending',
      method: null,
      verifiedAt: null,
      evidenceIds: []
    },
    health: {
      status: 'unknown',
      observedAt: null
    },
    lifecycleStatus: LIFECYCLE_STATES.DRAFT,
    registeredAt: now,
    updatedAt: now,
    recordFingerprint: '',
    lifecycleHistory: []
  };

  // Calculate fingerprint
  node.recordFingerprint = generateNodeFingerprint(node);

  return node;
}

/**
 * Generate a stable nonce for node ID
 * @returns {string} Nonce
 */
function generateNodeIdStableNonce() {
  return crypto.randomBytes(16).toString('hex');
}

/**
 * Register a node (transition from draft to registered)
 * @param {object} node - Node record
 * @param {object} [options] - Registration options
 * @returns {object} Updated node
 */
export function registerNode(node, options = {}) {
  const transition = executeTransition(
    node.lifecycleStatus,
    LIFECYCLE_STATES.REGISTERED,
    { reasonCode: 'NODE_REGISTERED', ...options }
  );

  const historyEntry = createLifecycleHistoryEntry(transition);

  return {
    ...node,
    lifecycleStatus: transition.currentState,
    updatedAt: transition.timestamp,
    lifecycleHistory: [...(node.lifecycleHistory || []), historyEntry]
  };
}

/**
 * Submit for verification
 * @param {object} node - Node record
 * @param {object} [options] - Options
 * @returns {object} Updated node
 */
export function submitForVerification(node, options = {}) {
  const transition = executeTransition(
    node.lifecycleStatus,
    LIFECYCLE_STATES.PENDING_VERIFICATION,
    { reasonCode: 'VERIFICATION_SUBMITTED', ...options }
  );

  const historyEntry = createLifecycleHistoryEntry(transition);

  return {
    ...node,
    lifecycleStatus: transition.currentState,
    updatedAt: transition.timestamp,
    lifecycleHistory: [...(node.lifecycleHistory || []), historyEntry]
  };
}

/**
 * Complete verification
 * @param {object} node - Node record
 * @param {boolean} passed - Whether verification passed
 * @param {object} [options] - Options
 * @returns {object} Updated node
 */
export function completeVerification(node, passed, options = {}) {
  const targetState = passed
    ? LIFECYCLE_STATES.VERIFIED
    : LIFECYCLE_STATES.REJECTED;

  const transition = executeTransition(node.lifecycleStatus, targetState, {
    reasonCode: passed ? 'VERIFICATION_PASSED' : 'VERIFICATION_FAILED',
    ...options
  });

  const historyEntry = createLifecycleHistoryEntry(transition);

  const updatedNode = {
    ...node,
    lifecycleStatus: transition.currentState,
    verification: {
      ...node.verification,
      status: passed ? VERIFICATION_STATUS.VERIFIED : VERIFICATION_STATUS.REJECTED,
      verifiedAt: passed ? transition.timestamp : null
    },
    updatedAt: transition.timestamp,
    lifecycleHistory: [...(node.lifecycleHistory || []), historyEntry]
  };

  // Recalculate fingerprint
  updatedNode.recordFingerprint = generateNodeFingerprint(updatedNode);

  return updatedNode;
}

/**
 * Activate node
 * @param {object} node - Node record
 * @param {object} [options] - Options
 * @returns {object} Updated node
 */
export function activateNode(node, options = {}) {
  const transition = executeTransition(
    node.lifecycleStatus,
    LIFECYCLE_STATES.ACTIVE,
    { reasonCode: 'ADMIN_ACTIVATED', ...options }
  );

  const historyEntry = createLifecycleHistoryEntry(transition);

  return {
    ...node,
    lifecycleStatus: transition.currentState,
    updatedAt: transition.timestamp,
    lifecycleHistory: [...(node.lifecycleHistory || []), historyEntry]
  };
}

/**
 * Update node health
 * @param {object} node - Node record
 * @param {string} healthStatus - New health status
 * @param {string} [observedAt] - Observation timestamp
 * @returns {object} Updated node
 */
export function updateNodeHealthStatus(node, healthStatus, observedAt = null) {
  return {
    ...node,
    health: {
      status: healthStatus,
      observedAt: observedAt || new Date().toISOString()
    },
    updatedAt: new Date().toISOString()
  };
}

/**
 * Transition lifecycle state
 * @param {object} node - Node record
 * @param {string} targetState - Target lifecycle state
 * @param {object} [options] - Transition options
 * @returns {object} Updated node
 */
export function transitionLifecycle(node, targetState, options = {}) {
  const transition = executeTransition(
    node.lifecycleStatus,
    targetState,
    options
  );

  const historyEntry = createLifecycleHistoryEntry(transition);

  const updatedNode = {
    ...node,
    lifecycleStatus: transition.currentState,
    updatedAt: transition.timestamp,
    lifecycleHistory: [...(node.lifecycleHistory || []), historyEntry]
  };

  // Recalculate fingerprint if not terminal
  if (!isTerminalState(targetState)) {
    updatedNode.recordFingerprint = generateNodeFingerprint(updatedNode);
  }

  return updatedNode;
}

/**
 * Validate node record
 * @param {object} node - Node to validate
 * @returns {object} Validation result
 */
export function validateNode(node) {
  const errors = [];

  if (!node.schemaVersion) {
    errors.push('schemaVersion is required');
  }

  if (!isValidNodeId(node.nodeId)) {
    errors.push('Invalid nodeId format');
  }

  if (!node.operatorProtocolId) {
    errors.push('operatorProtocolId is required');
  }

  if (!NODE_TYPES.includes(node.nodeType)) {
    errors.push(`Invalid nodeType: ${node.nodeType}`);
  }

  if (!Object.values(LIFECYCLE_STATES).includes(node.lifecycleStatus)) {
    errors.push('Invalid lifecycleStatus');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

export default {
  DEFAULT_NODE_POLICY,
  createNode,
  registerNode,
  submitForVerification,
  completeVerification,
  activateNode,
  updateNodeHealthStatus,
  transitionLifecycle,
  validateNode
};
