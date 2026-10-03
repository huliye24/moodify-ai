/**
 * MOOD Protocol API - Error Model
 *
 * Standardized error codes and response generation.
 * Per ERROR_MODEL.md - do not leak stack traces or internal details.
 */

import { API_VERSION, generateRequestId, generateTimestamp } from './envelope.js';

// Standard error codes
export const ERROR_CODES = {
  INVALID_REQUEST: 'INVALID_REQUEST',
  NOT_FOUND: 'NOT_FOUND',
  CONFLICT: 'CONFLICT',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  RATE_LIMITED: 'RATE_LIMITED',
  DEPENDENCY_UNAVAILABLE: 'DEPENDENCY_UNAVAILABLE',
  POLICY_BLOCKED: 'POLICY_BLOCKED',
  HUMAN_DECISION_REQUIRED: 'HUMAN_DECISION_REQUIRED',
  INTERNAL_ERROR: 'INTERNAL_ERROR'
};

// HTTP status code mapping
export const HTTP_STATUS = {
  INVALID_REQUEST: 400,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  RATE_LIMITED: 429,
  DEPENDENCY_UNAVAILABLE: 503,
  POLICY_BLOCKED: 422,
  HUMAN_DECISION_REQUIRED: 409,
  INTERNAL_ERROR: 500
};

// Default messages (safe to expose publicly)
const DEFAULT_MESSAGES = {
  INVALID_REQUEST: 'Invalid request',
  NOT_FOUND: 'Resource not found',
  CONFLICT: 'Resource conflict',
  UNAUTHORIZED: 'Authentication required',
  FORBIDDEN: 'Access denied',
  RATE_LIMITED: 'Too many requests',
  DEPENDENCY_UNAVAILABLE: 'Upstream dependency unavailable',
  POLICY_BLOCKED: 'Request blocked by current policy',
  HUMAN_DECISION_REQUIRED: 'Decision requires human authority',
  INTERNAL_ERROR: 'Internal server error'
};

/**
 * Create an error response
 * @param {string} code - Error code from ERROR_CODES
 * @param {string} [message] - Public-safe message
 * @param {any} [details] - Optional error details (public-safe)
 * @param {string} [requestId] - Request ID
 * @returns {object} Error response
 */
export function errorResponse(code, message, details, requestId) {
  if (!Object.values(ERROR_CODES).includes(code)) {
    throw new Error(`Unknown error code: ${code}`);
  }

  return {
    apiVersion: API_VERSION,
    error: {
      code,
      message: message || DEFAULT_MESSAGES[code],
      details: details || null
    },
    meta: {
      requestId: requestId || generateRequestId(),
      generatedAt: generateTimestamp()
    }
  };
}

/**
 * Get HTTP status code for error code
 * @param {string} code - Error code
 * @returns {number} HTTP status code
 */
export function getHttpStatus(code) {
  return HTTP_STATUS[code] || 500;
}

/**
 * Sanitize error to remove internal details
 * @param {Error} error - Raw error
 * @returns {object} Sanitized error
 */
export function sanitizeError(error) {
  // Do not expose stack traces or internal paths
  return {
    code: ERROR_CODES.INTERNAL_ERROR,
    message: DEFAULT_MESSAGES.INTERNAL_ERROR,
    details: null
  };
}

/**
 * Create specific error responses
 */
export const Errors = {
  invalidRequest: (details, requestId) =>
    errorResponse(ERROR_CODES.INVALID_REQUEST, null, details, requestId),

  notFound: (resource, requestId) =>
    errorResponse(ERROR_CODES.NOT_FOUND, `${resource} not found`, null, requestId),

  unauthorized: (requestId) =>
    errorResponse(ERROR_CODES.UNAUTHORIZED, null, null, requestId),

  forbidden: (requestId) =>
    errorResponse(ERROR_CODES.FORBIDDEN, null, null, requestId),

  rateLimited: (requestId) =>
    errorResponse(ERROR_CODES.RATE_LIMITED, null, null, requestId),

  dependencyUnavailable: (dependency, requestId) =>
    errorResponse(
      ERROR_CODES.DEPENDENCY_UNAVAILABLE,
      `${dependency} is currently unavailable`,
      null,
      requestId
    ),

  policyBlocked: (reason, requestId) =>
    errorResponse(
      ERROR_CODES.POLICY_BLOCKED,
      'Request blocked by current policy',
      { reason },
      requestId
    ),

  humanDecisionRequired: (details, requestId) =>
    errorResponse(
      ERROR_CODES.HUMAN_DECISION_REQUIRED,
      'Decision requires human authority',
      details,
      requestId
    ),

  internalError: (requestId) =>
    errorResponse(ERROR_CODES.INTERNAL_ERROR, null, null, requestId)
};

export default {
  ERROR_CODES,
  HTTP_STATUS,
  errorResponse,
  getHttpStatus,
  sanitizeError,
  Errors
};
