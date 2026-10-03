/**
 * MOOD Protocol API - Response Envelope
 *
 * Provides standardized response envelope for all API endpoints.
 * Per API_CONTRACT.md - every success response uses this format.
 */

import crypto from 'crypto';

// API version constant
export const API_VERSION = 'v1';

/**
 * Generate a unique request ID
 * @returns {string} Request ID
 */
export function generateRequestId() {
  const timestamp = Date.now().toString(36);
  const random = crypto.randomBytes(4).toString('hex');
  return `req_${timestamp}_${random}`;
}

/**
 * Generate ISO timestamp
 * @returns {string} ISO timestamp
 */
export function generateTimestamp() {
  return new Date().toISOString();
}

/**
 * Create a success response envelope
 * @param {object} options - Envelope options
 * @param {any} options.data - Response data
 * @param {string} options.requestId - Request ID
 * @param {object} [options.pagination] - Pagination metadata for lists
 * @param {object} [options.additionalMeta] - Additional metadata
 * @returns {object} Success response envelope
 */
export function successResponse(options) {
  const { data, requestId, pagination = null, additionalMeta = {} } = options;

  const meta = {
    requestId: requestId || generateRequestId(),
    generatedAt: generateTimestamp(),
    ...additionalMeta
  };

  if (pagination) {
    meta.pagination = pagination;
  }

  return {
    apiVersion: API_VERSION,
    data,
    meta
  };
}

/**
 * Create a list response envelope
 * @param {object} options - List options
 * @param {Array} options.data - List data
 * @param {string} options.requestId - Request ID
 * @param {number} options.limit - Page limit
 * @param {number} options.offset - Page offset
 * @param {number} options.total - Total items
 * @returns {object} List response envelope
 */
export function listResponse(options) {
  const { data, requestId, limit, offset, total } = options;

  const hasMore = offset + limit < total;

  const pagination = {
    limit,
    offset,
    total,
    hasMore,
    nextCursor: hasMore ? `${offset + limit}` : null
  };

  return successResponse({
    data,
    requestId,
    pagination
  });
}

/**
 * Validate response envelope structure
 * @param {object} response - Response to validate
 * @returns {object} Validation result
 */
export function validateResponse(response) {
  const errors = [];

  if (response.apiVersion !== API_VERSION) {
    errors.push(`Invalid apiVersion: ${response.apiVersion}`);
  }

  if (!('data' in response)) {
    errors.push('Missing data field');
  }

  if (!response.meta || !response.meta.requestId) {
    errors.push('Missing meta.requestId');
  }

  if (response.meta && !response.meta.generatedAt) {
    errors.push('Missing meta.generatedAt');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

export default {
  API_VERSION,
  generateRequestId,
  successResponse,
  listResponse,
  validateResponse
};
