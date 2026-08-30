/**
 * MOOD Protocol Node Lifecycle State Machine
 *
 * Manages node lifecycle states with explicit transitions.
 * Illegal transitions are rejected with clear reason codes.
 */

// Node lifecycle states
export const LIFECYCLE_STATES = {
  DRAFT: 'draft',
  REGISTERED: 'registered',
  PENDING_VERIFICATION: 'pending_verification',
  VERIFIED: 'verified',
  ACTIVE: 'active',
  DEGRADED: 'degraded',
  INACTIVE: 'inactive',
  SUSPENDED: 'suspended',
  REJECTED: 'rejected',
  RETIRED: 'retired'
};

// Allowed transitions map
const ALLOWED_TRANSITIONS = {
  [LIFECYCLE_STATES.DRAFT]: [LIFECYCLE_STATES.REGISTERED],
  [LIFECYCLE_STATES.REGISTERED]: [LIFECYCLE_STATES.PENDING_VERIFICATION],
  [LIFECYCLE_STATES.PENDING_VERIFICATION]: [
    LIFECYCLE_STATES.VERIFIED,
    LIFECYCLE_STATES.REJECTED
  ],
  [LIFECYCLE_STATES.VERIFIED]: [LIFECYCLE_STATES.ACTIVE],
  [LIFECYCLE_STATES.ACTIVE]: [
    LIFECYCLE_STATES.DEGRADED,
    LIFECYCLE_STATES.INACTIVE,
    LIFECYCLE_STATES.SUSPENDED,
    LIFECYCLE_STATES.RETIRED
  ],
  [LIFECYCLE_STATES.DEGRADED]: [
    LIFECYCLE_STATES.ACTIVE,
    LIFECYCLE_STATES.INACTIVE,
    LIFECYCLE_STATES.SUSPENDED
  ],
  [LIFECYCLE_STATES.INACTIVE]: [
    LIFECYCLE_STATES.ACTIVE,
    LIFECYCLE_STATES.PENDING_VERIFICATION,
    LIFECYCLE_STATES.RETIRED
  ],
  [LIFECYCLE_STATES.SUSPENDED]: [
    LIFECYCLE_STATES.PENDING_VERIFICATION,
    LIFECYCLE_STATES.RETIRED
  ],
  // Terminal states - no transitions allowed
  [LIFECYCLE_STATES.REJECTED]: [],
  [LIFECYCLE_STATES.RETIRED]: []
};

// Terminal states
const TERMINAL_STATES = [
  LIFECYCLE_STATES.REJECTED,
  LIFECYCLE_STATES.RETIRED
];

// Reason codes for transitions
export const REASON_CODES = {
  // Registration
  NODE_REGISTERED: 'NODE_REGISTERED',
  VERIFICATION_SUBMITTED: 'VERIFICATION_SUBMITTED',

  // Verification outcomes
  VERIFICATION_PASSED: 'VERIFICATION_PASSED',
  VERIFICATION_FAILED: 'VERIFICATION_FAILED',

  // Health-based
  HEALTH_CHECK_HEALTHY: 'HEALTH_CHECK_HEALTHY',
  HEALTH_CHECK_DEGRADED: 'HEALTH_CHECK_DEGRADED',
  HEALTH_CHECK_STALE: 'HEALTH_CHECK_STALE',

  // Administrative
  ADMIN_SUSPENDED: 'ADMIN_SUSPENDED',
  ADMIN_REACTIVATED: 'ADMIN_REACTIVATED',
  ADMIN_RETIRED: 'ADMIN_RETIRED',
  MANUAL_REVIEW_APPROVED: 'MANUAL_REVIEW_APPROVED',
  MANUAL_REVIEW_REJECTED: 'MANUAL_REVIEW_REJECTED',

  // Self-transitions
  OPERATOR_REQUESTED: 'OPERATOR_REQUESTED',
  HEARTBEAT_RECOVERY: 'HEARTBEAT_RECOVERY'
};

/**
 * Check if transition is allowed
 * @param {string} fromState - Current state
 * @param {string} toState - Target state
 * @returns {boolean} Whether allowed
 */
export function isTransitionAllowed(fromState, toState) {
  const allowed = ALLOWED_TRANSITIONS[fromState];
  if (!allowed) {
    return false;
  }
  return allowed.includes(toState);
}

/**
 * Validate a state transition
 * @param {string} fromState - Current state
 * @param {string} toState - Target state
 * @returns {object} Validation result
 */
export function validateTransition(fromState, toState) {
  if (!Object.values(LIFECYCLE_STATES).includes(fromState)) {
    return {
      valid: false,
      error: `Invalid source state: ${fromState}`
    };
  }

  if (!Object.values(LIFECYCLE_STATES).includes(toState)) {
    return {
      valid: false,
      error: `Invalid target state: ${toState}`
    };
  }

  if (!isTransitionAllowed(fromState, toState)) {
    return {
      valid: false,
      error: `Illegal transition: ${fromState} -> ${toState}`
    };
  }

  return { valid: true };
}

/**
 * Execute a state transition
 * @param {string} fromState - Current state
 * @param {string} toState - Target state
 * @param {object} options - Transition options
 * @param {string} options.reasonCode - Reason code
 * @param {string} [options.operatorId] - Operator who initiated
 * @param {string} [options.authority] - Authority source
 * @param {string} [options.evidenceId] - Supporting evidence
 * @returns {object} Transition result
 */
export function executeTransition(fromState, toState, options = {}) {
  const { reasonCode, operatorId, authority, evidenceId } = options;

  const validation = validateTransition(fromState, toState);
  if (!validation.valid) {
    throw new Error(validation.error);
  }

  return {
    previousState: fromState,
    currentState: toState,
    timestamp: new Date().toISOString(),
    reasonCode: reasonCode || 'UNKNOWN',
    operatorId: operatorId || null,
    authority: authority || 'system',
    evidenceId: evidenceId || null
  };
}

/**
 * Check if state is terminal
 * @param {string} state - State to check
 * @returns {boolean} Whether terminal
 */
export function isTerminalState(state) {
  return TERMINAL_STATES.includes(state);
}

/**
 * Get allowed transitions from a state
 * @param {string} state - Current state
 * @returns {Array<string>} Allowed target states
 */
export function getAllowedTransitions(state) {
  return ALLOWED_TRANSITIONS[state] || [];
}

/**
 * Create lifecycle history entry
 * @param {object} transition - Transition result
 * @returns {object} History entry
 */
export function createLifecycleHistoryEntry(transition) {
  return {
    eventId: `LIFECYCLE-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
    timestamp: transition.timestamp,
    previousState: transition.previousState,
    nextState: transition.currentState,
    reasonCode: transition.reasonCode,
    operatorId: transition.operatorId,
    authority: transition.authority,
    evidenceId: transition.evidenceId
  };
}

/**
 * Check if heartbeat can affect state
 * Heartbeat cannot bypass suspension
 * @param {string} currentState - Current lifecycle state
 * @returns {boolean} Whether heartbeat can affect state
 */
export function canHeartbeatAffectState(currentState) {
  // Suspended nodes require admin action, not heartbeat
  if (currentState === LIFECYCLE_STATES.SUSPENDED) {
    return false;
  }

  // Rejected and retired are terminal
  if (isTerminalState(currentState)) {
    return false;
  }

  return true;
}

/**
 * Get state category for grouping
 * @param {string} state - Lifecycle state
 * @returns {string} Category
 */
export function getStateCategory(state) {
  switch (state) {
    case LIFECYCLE_STATES.DRAFT:
    case LIFECYCLE_STATES.REGISTERED:
      return 'setup';
    case LIFECYCLE_STATES.PENDING_VERIFICATION:
      return 'verification';
    case LIFECYCLE_STATES.VERIFIED:
      return 'verified';
    case LIFECYCLE_STATES.ACTIVE:
      return 'operational';
    case LIFECYCLE_STATES.DEGRADED:
    case LIFECYCLE_STATES.INACTIVE:
      return 'degraded';
    case LIFECYCLE_STATES.SUSPENDED:
      return 'suspended';
    case LIFECYCLE_STATES.REJECTED:
    case LIFECYCLE_STATES.RETIRED:
      return 'terminal';
    default:
      return 'unknown';
  }
}

export default {
  LIFECYCLE_STATES,
  REASON_CODES,
  isTransitionAllowed,
  validateTransition,
  executeTransition,
  isTerminalState,
  getAllowedTransitions,
  createLifecycleHistoryEntry,
  canHeartbeatAffectState,
  getStateCategory
};
