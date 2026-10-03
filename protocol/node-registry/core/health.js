/**
 * MOOD Protocol Node Health Module
 *
 * Manages heartbeat observations and health state.
 * Health is separate from lifecycle state.
 * Health is separate from reputation.
 */

import crypto from 'crypto';

// Health statuses
export const HEALTH_STATUS = {
  HEALTHY: 'healthy',
  DEGRADED: 'degraded',
  UNREACHABLE: 'unreachable',
  UNKNOWN: 'unknown'
};

// Default health policy (draft)
const DEFAULT_HEALTH_POLICY = {
  healthyFreshnessSeconds: 300,    // 5 minutes
  degradedAfterSeconds: 900,       // 15 minutes
  inactiveAfterSeconds: 3600       // 1 hour
};

/**
 * Create a heartbeat observation
 * @param {object} options - Observation options
 * @param {string} options.nodeId - Node ID
 * @param {string} options.status - Health status
 * @param {string} options.source - Observation source
 * @param {number} [options.latencyMs] - Latency in milliseconds
 * @param {boolean} [options.protocolCompatible] - Protocol version compatible
 * @param {string} [options.reason] - Reason for status
 * @returns {object} Heartbeat observation
 */
export function createHeartbeat(options) {
  const {
    nodeId,
    status,
    source,
    latencyMs = null,
    protocolCompatible = true,
    reason = null
  } = options;

  if (!nodeId) {
    throw new Error('nodeId is required');
  }

  if (!Object.values(HEALTH_STATUS).includes(status)) {
    throw new Error(`Invalid health status: ${status}`);
  }

  const observation = {
    nodeId,
    observedAt: new Date().toISOString(),
    source,
    status,
    protocolCompatible,
    latencyMs,
    reason,
    fingerprint: ''
  };

  // Generate observation fingerprint
  observation.fingerprint = generateObservationFingerprint(observation);

  return observation;
}

/**
 * Generate heartbeat observation fingerprint
 * @param {object} observation - Observation (without fingerprint)
 * @returns {string} Fingerprint
 */
function generateObservationFingerprint(observation) {
  const canonical = {
    nodeId: observation.nodeId,
    observedAt: observation.observedAt,
    source: observation.source,
    status: observation.status,
    protocolCompatible: observation.protocolCompatible
  };

  return `sha256:${crypto.createHash('sha256')
    .update(JSON.stringify(canonical))
    .digest('hex')}`;
}

/**
 * Evaluate health from observation
 * @param {object} observation - Heartbeat observation
 * @param {object} [policy] - Health policy
 * @returns {string} Evaluated health status
 */
export function evaluateHealth(observation, policy = DEFAULT_HEALTH_POLICY) {
  // If observation indicates unhealthy, use that
  if (observation.status === HEALTH_STATUS.UNREACHABLE) {
    return HEALTH_STATUS.UNREACHABLE;
  }

  if (observation.status === HEALTH_STATUS.DEGRADED) {
    return HEALTH_STATUS.DEGRADED;
  }

  // Check freshness
  const observedAt = new Date(observation.observedAt);
  const now = new Date();
  const ageSeconds = (now - observedAt) / 1000;

  if (ageSeconds <= policy.healthyFreshnessSeconds) {
    return HEALTH_STATUS.HEALTHY;
  }

  if (ageSeconds <= policy.degradedAfterSeconds) {
    return HEALTH_STATUS.DEGRADED;
  }

  return HEALTH_STATUS.UNREACHABLE;
}

/**
 * Determine if node should transition due to stale heartbeat
 * @param {object} lastObservation - Last heartbeat observation
 * @param {string} currentLifecycleState - Current lifecycle state
 * @param {object} [policy] - Health policy
 * @returns {object} Transition recommendation
 */
export function evaluateStaleTransition(lastObservation, currentLifecycleState, policy = DEFAULT_HEALTH_POLICY) {
  if (!lastObservation) {
    return {
      shouldTransition: true,
      newHealthStatus: HEALTH_STATUS.UNKNOWN,
      reason: 'NO_HEARTBEAT'
    };
  }

  const observedAt = new Date(lastObservation.observedAt);
  const now = new Date();
  const ageSeconds = (now - observedAt) / 1000;

  if (ageSeconds <= policy.healthyFreshnessSeconds) {
    return {
      shouldTransition: false,
      newHealthStatus: HEALTH_STATUS.HEALTHY,
      reason: 'FRESH'
    };
  }

  if (ageSeconds <= policy.degradedAfterSeconds) {
    return {
      shouldTransition: ageSeconds > policy.healthyFreshnessSeconds,
      newHealthStatus: HEALTH_STATUS.DEGRADED,
      reason: 'STALE_DEGRADED'
    };
  }

  if (ageSeconds <= policy.inactiveAfterSeconds) {
    return {
      shouldTransition: ageSeconds > policy.degradedAfterSeconds,
      newHealthStatus: HEALTH_STATUS.UNREACHABLE,
      reason: 'STALE_INACTIVE'
    };
  }

  return {
    shouldTransition: true,
    newHealthStatus: HEALTH_STATUS.UNREACHABLE,
    reason: 'STALE_EXPIRED'
  };
}

/**
 * Update node health from observation
 * @param {object} node - Node record
 * @param {object} observation - Heartbeat observation
 * @returns {object} Updated node
 */
export function updateNodeHealth(node, observation) {
  return {
    ...node,
    health: {
      status: observation.status,
      observedAt: observation.observedAt
    },
    updatedAt: new Date().toISOString()
  };
}

/**
 * Record health observation history
 * @param {string} nodeId - Node ID
 * @param {object} observation - Heartbeat observation
 * @returns {object} History entry
 */
export function createHealthHistoryEntry(nodeId, observation) {
  return {
    eventId: `HEALTH-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
    nodeId,
    timestamp: observation.observedAt,
    status: observation.status,
    source: observation.source,
    latencyMs: observation.latencyMs,
    reason: observation.reason
  };
}

/**
 * Check if heartbeat can recover degraded node
 * @param {string} currentLifecycleState - Current lifecycle state
 * @param {string} currentHealth - Current health status
 * @returns {boolean} Whether recovery is possible
 */
export function canRecoverFromHeartbeat(currentLifecycleState, currentHealth) {
  // Cannot recover if suspended (requires admin action)
  if (currentLifecycleState === 'suspended') {
    return false;
  }

  // Can recover if degraded or inactive
  if (currentHealth === HEALTH_STATUS.HEALTHY) {
    return currentLifecycleState === 'degraded' ||
           currentLifecycleState === 'inactive';
  }

  return false;
}

/**
 * Validate health observation
 * @param {object} observation - Observation to validate
 * @returns {object} Validation result
 */
export function validateObservation(observation) {
  if (!observation.nodeId) {
    return { valid: false, error: 'nodeId is required' };
  }

  if (!observation.observedAt) {
    return { valid: false, error: 'observedAt is required' };
  }

  if (!observation.source) {
    return { valid: false, error: 'source is required' };
  }

  if (!Object.values(HEALTH_STATUS).includes(observation.status)) {
    return { valid: false, error: `Invalid status: ${observation.status}` };
  }

  if (observation.latencyMs !== null && observation.latencyMs < 0) {
    return { valid: false, error: 'latencyMs cannot be negative' };
  }

  return { valid: true };
}

/**
 * Get latency bucket for privacy
 * @param {number} latencyMs - Exact latency
 * @returns {string} Latency bucket
 */
export function getLatencyBucket(latencyMs) {
  if (latencyMs === null || latencyMs === undefined) {
    return 'unknown';
  }

  if (latencyMs < 50) return '<50ms';
  if (latencyMs < 100) return '50-100ms';
  if (latencyMs < 250) return '100-250ms';
  if (latencyMs < 500) return '250-500ms';
  if (latencyMs < 1000) return '500-1000ms';
  return '>1000ms';
}

export default {
  HEALTH_STATUS,
  DEFAULT_HEALTH_POLICY,
  createHeartbeat,
  evaluateHealth,
  evaluateStaleTransition,
  updateNodeHealth,
  createHealthHistoryEntry,
  canRecoverFromHeartbeat,
  validateObservation,
  getLatencyBucket
};
