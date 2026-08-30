/**
 * MOOD Protocol Node Discovery Module
 *
 * Read-only discovery and query capabilities for the node registry.
 */

import crypto from 'crypto';
import { LIFECYCLE_STATES } from './lifecycle.js';
import { HEALTH_STATUS } from './health.js';
import { NODE_TYPES } from './node-identity.js';

/**
 * Discovery filters
 */
export const DISCOVERY_FILTERS = {
  NODE_TYPE: 'nodeType',
  LIFECYCLE: 'lifecycleStatus',
  HEALTH: 'health',
  COUNTRY: 'country',
  REGION: 'region',
  CAPABILITY: 'capability',
  PROTOCOL_VERSION: 'protocolVersion',
  VERIFICATION_STATUS: 'verification'
};

/**
 * List nodes with optional filters
 * @param {Array<object>} nodes - All node records
 * @param {object} [filters] - Filter criteria
 * @param {string} [filters.nodeType] - Node type filter
 * @param {string} [filters.lifecycleStatus] - Lifecycle status filter
 * @param {string} [filters.health] - Health status filter
 * @param {string} [filters.country] - Country code filter
 * @param {string} [filters.capability] - Capability key filter
 * @param {number} [filters.limit] - Result limit
 * @param {number} [filters.offset] - Result offset
 * @returns {object} Filtered results
 */
export function discoverNodes(nodes, filters = {}) {
  let results = [...nodes];

  // Apply node type filter
  if (filters.nodeType) {
    const types = Array.isArray(filters.nodeType) ? filters.nodeType : [filters.nodeType];
    results = results.filter(n => types.includes(n.nodeType));
  }

  // Apply lifecycle status filter
  if (filters.lifecycleStatus) {
    const statuses = Array.isArray(filters.lifecycleStatus)
      ? filters.lifecycleStatus
      : [filters.lifecycleStatus];
    results = results.filter(n => statuses.includes(n.lifecycleStatus));
  }

  // Apply health status filter
  if (filters.health) {
    const healthStatuses = Array.isArray(filters.health) ? filters.health : [filters.health];
    results = results.filter(n => healthStatuses.includes(n.health?.status));
  }

  // Apply country filter
  if (filters.country) {
    const countries = Array.isArray(filters.country) ? filters.country : [filters.country];
    results = results.filter(n => {
      const country = n.region?.countryCode;
      return country && countries.includes(country);
    });
  }

  // Apply region filter
  if (filters.region) {
    const regions = Array.isArray(filters.region) ? filters.region : [filters.region];
    results = results.filter(n => {
      const region = n.region?.regionCode;
      return region && regions.includes(region);
    });
  }

  // Apply capability filter
  if (filters.capability) {
    results = results.filter(n => {
      // In a real implementation, this would check the capability manifest
      // For now, return nodes with capability manifest
      return n.capabilityManifestId !== null;
    });
  }

  // Apply verification status filter
  if (filters.verification) {
    const verificationStatuses = Array.isArray(filters.verification)
      ? filters.verification
      : [filters.verification];
    results = results.filter(n =>
      verificationStatuses.includes(n.verification?.status)
    );
  }

  // Count before pagination
  const total = results.length;

  // Apply pagination
  const limit = filters.limit || 100;
  const offset = filters.offset || 0;
  results = results.slice(offset, offset + limit);

  // Transform to discovery format
  const discovered = results.map(n => formatNodeForDiscovery(n));

  return {
    nodes: discovered,
    total,
    limit,
    offset,
    hasMore: offset + limit < total
  };
}

/**
 * Format node for discovery response
 * Distinguishes declared vs verified capabilities
 * @param {object} node - Node record
 * @returns {object} Discovery format
 */
export function formatNodeForDiscovery(node) {
  return {
    nodeId: node.nodeId,
    nodeType: node.nodeType,
    displayName: node.displayName,
    region: node.region ? {
      countryCode: node.region.countryCode,
      precision: node.region.precision
      // Omit exact city/location for privacy
    } : null,
    lifecycleStatus: node.lifecycleStatus,
    health: {
      status: node.health?.status || 'unknown',
      observedAt: node.health?.observedAt
    },
    verification: {
      status: node.verification?.status || 'pending'
      // Capabilities would be fetched separately
    },
    registeredAt: node.registeredAt
  };
}

/**
 * Get detailed node information
 * @param {object} node - Node record
 * @param {object} [capabilityManifest] - Optional capability manifest
 * @returns {object} Detailed node info
 */
export function getNodeDetails(node, capabilityManifest = null) {
  const details = formatNodeForDiscovery(node);

  // Add endpoint info (with privacy consideration)
  if (node.endpoint) {
    details.endpoint = {
      type: node.endpoint.type,
      // URI should be public if the node is active
      uri: node.lifecycleStatus === LIFECYCLE_STATES.ACTIVE
        ? node.endpoint.uri
        : null
    };
  }

  // Add capability details if available
  if (capabilityManifest) {
    details.capabilities = formatCapabilitiesForDiscovery(capabilityManifest);
  }

  // Add verification details
  details.verification = {
    status: node.verification?.status,
    method: node.verification?.method,
    verifiedAt: node.verification?.verifiedAt
  };

  // Add lifecycle history summary
  details.lifecycleHistory = {
    transitions: node.lifecycleHistory?.length || 0,
    currentSince: node.lifecycleHistory?.length > 0
      ? node.lifecycleHistory[node.lifecycleHistory.length - 1].timestamp
      : node.registeredAt
  };

  return details;
}

/**
 * Format capabilities for discovery
 * Separates declared vs verified
 * @param {object} manifest - Capability manifest
 * @returns {object} Formatted capabilities
 */
export function formatCapabilitiesForDiscovery(manifest) {
  const result = {
    manifestId: manifest.manifestId,
    protocolVersions: manifest.protocolVersions,
    capabilities: {}
  };

  for (const cap of manifest.capabilities) {
    result.capabilities[cap.key] = {
      value: cap.value,
      declared: true,
      verificationStatus: cap.verificationStatus
      // Do not expose evidence IDs in public discovery
    };
  }

  return result;
}

/**
 * Get node health details
 * @param {object} node - Node record
 * @param {Array<object>} [healthHistory] - Optional health history
 * @returns {object} Health details
 */
export function getNodeHealthDetails(node, healthHistory = []) {
  return {
    nodeId: node.nodeId,
    currentStatus: node.health?.status || 'unknown',
    lastObservedAt: node.health?.observedAt,
    history: healthHistory.slice(-10) // Last 10 observations
  };
}

/**
 * Generate registry snapshot
 * Deterministic representation of registry state
 * @param {Array<object>} nodes - All node records
 * @param {string} policyVersion - Registry policy version
 * @returns {object} Registry snapshot
 */
export function generateRegistrySnapshot(nodes, policyVersion) {
  // Sort nodes by nodeId for determinism
  const sortedNodes = [...nodes].sort((a, b) => a.nodeId.localeCompare(b.nodeId));

  const nodeIds = sortedNodes.map(n => n.nodeId);
  const fingerprints = sortedNodes.map(n => n.recordFingerprint);

  const snapshot = {
    snapshotVersion: '1.0.0',
    snapshotId: `registry-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
    registryPolicyVersion: policyVersion,
    nodeIds,
    nodeRecordFingerprints: fingerprints,
    generatedAt: new Date().toISOString(),
    snapshotFingerprint: ''
  };

  // Calculate snapshot fingerprint
  snapshot.snapshotFingerprint = generateSnapshotFingerprint(snapshot);

  return snapshot;
}

/**
 * Generate snapshot fingerprint
 * @param {object} snapshot - Snapshot (without fingerprint)
 * @returns {string} Fingerprint
 */
function generateSnapshotFingerprint(snapshot) {
  const canonical = {
    registryPolicyVersion: snapshot.registryPolicyVersion,
    nodeIds: snapshot.nodeIds,
    nodeRecordFingerprints: snapshot.nodeRecordFingerprints,
    generatedAt: snapshot.generatedAt
  };

  return `sha256:${crypto.createHash('sha256')
    .update(JSON.stringify(canonical))
    .digest('hex')}`;
}

/**
 * Validate snapshot determinism
 * @param {object} snapshot1 - First snapshot
 * @param {object} snapshot2 - Second snapshot
 * @returns {boolean} Whether deterministic
 */
export function validateSnapshotDeterminism(snapshot1, snapshot2) {
  return snapshot1.snapshotFingerprint === snapshot2.snapshotFingerprint;
}

export default {
  DISCOVERY_FILTERS,
  discoverNodes,
  formatNodeForDiscovery,
  getNodeDetails,
  formatCapabilitiesForDiscovery,
  getNodeHealthDetails,
  generateRegistrySnapshot,
  validateSnapshotDeterminism
};
