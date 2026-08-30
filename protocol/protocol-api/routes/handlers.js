/**
 * MOOD Protocol API - Route Handlers
 *
 * Thin route handlers per API_CONTRACT.md.
 * Route handlers MUST:
 * - Parse input
 * - Authenticate (if needed)
 * - Call domain service
 * - Map result
 * - Return response
 *
 * Route handlers MUST NOT:
 * - Calculate reputation
 * - Score contributions
 * - Mutate node state
 * - Derive official contract addresses
 * - Calculate token rewards
 * - Call shell/SSH
 * - Send blockchain transactions
 */

import { successResponse, listResponse, generateRequestId } from '../core/envelope.js';
import { Errors, ERROR_CODES, getHttpStatus } from '../core/errors.js';

// Default pagination settings
const DEFAULT_LIMIT = 50;
const MAX_LIMIT = 200;

// Allowed sort keys for each endpoint
const ALLOWED_SORT_KEYS = {
  contributions: ['submittedAt', 'finalizedAt', 'contributionId'],
  nodes: ['registeredAt', 'updatedAt', 'nodeId'],
  contributors: ['createdAt', 'lastUpdated']
};

/**
 * Mock HTTP context for testing
 */
export class ApiContext {
  constructor(options = {}) {
    this.request = options.request || {};
    this.params = options.params || {};
    this.query = options.query || {};
    this.body = options.body || {};
    this.requestId = options.requestId || generateRequestId();
  }

  /**
   * Generate success response
   * @param {any} data - Response data
   * @param {object} [pagination] - Optional pagination
   */
  success(data, pagination = null) {
    return successResponse({
      data,
      requestId: this.requestId,
      pagination
    });
  }

  /**
   * Generate list response with pagination
   * @param {Array} data - List data
   * @param {number} total - Total count
   * @param {number} limit - Page limit
   * @param {number} offset - Page offset
   */
  list(data, total, limit, offset) {
    return listResponse({
      data,
      requestId: this.requestId,
      limit,
      offset,
      total
    });
  }

  /**
   * Generate error response
   * @param {string} code - Error code
   * @param {string} [message] - Error message
   * @param {any} [details] - Error details
   */
  error(code, message, details) {
    return {
      _error: true,
      code,
      message,
      details,
      requestId: this.requestId
    };
  }
}

/**
 * Parse and validate pagination
 * @param {object} query - Query parameters
 * @returns {object} Validated pagination
 */
export function parsePagination(query) {
  let limit = parseInt(query.limit) || DEFAULT_LIMIT;
  let offset = parseInt(query.offset) || 0;

  // Bound to safe limits
  if (limit < 1) limit = DEFAULT_LIMIT;
  if (limit > MAX_LIMIT) limit = MAX_LIMIT;
  if (offset < 0) offset = 0;

  return { limit, offset };
}

/**
 * Validate sort key
 * @param {string} sortKey - Requested sort key
 * @param {Array} allowed - Allowed sort keys
 * @returns {string|null} Validated sort key or null
 */
export function validateSortKey(sortKey, allowed) {
  if (!sortKey) return null;
  if (!allowed.includes(sortKey)) {
    return null;
  }
  return sortKey;
}

/**
 * Validate required query parameter
 * @param {object} query - Query parameters
 * @param {string} key - Required key
 * @returns {any|null} Value or null
 */
export function requireQueryParam(query, key) {
  const value = query[key];
  if (!value) return null;
  return value;
}

/**
 * Apply pagination to results
 * @param {Array} results - All results
 * @param {object} pagination - Pagination config
 * @returns {Array} Paginated results
 */
export function paginate(results, pagination) {
  return results.slice(pagination.offset, pagination.offset + pagination.limit);
}

// ==================== Route Handlers ====================

/**
 * GET /health
 */
export async function healthHandler(ctx, services) {
  const status = await services.mainnet.getProtocolStatus();

  const components = {
    protocolFacts: status ? 'ok' : 'degraded',
    contributions: 'ok',
    reputation: 'ok',
    nodeRegistry: 'ok'
  };

  const isHealthy = Object.values(components).every(s => s === 'ok');

  return ctx.success({
    status: isHealthy ? 'ok' : 'degraded',
    apiVersion: 'v1',
    components
  });
}

/**
 * GET /protocol
 */
export async function protocolHandler(ctx, services) {
  const status = await services.mainnet.getProtocolStatus();
  return ctx.success(status);
}

/**
 * GET /protocol/mainnet
 */
export async function mainnetHandler(ctx, services) {
  const facts = await services.mainnet.getMainnetFacts();
  if (!facts) {
    return ctx.error(ERROR_CODES.DEPENDENCY_UNAVAILABLE, 'Mainnet facts unavailable');
  }
  return ctx.success(facts);
}

/**
 * GET /contributions
 */
export async function listContributionsHandler(ctx, services) {
  const pagination = parsePagination(ctx.query);
  const filters = {
    contributor: ctx.query.contributor,
    category: ctx.query.category,
    status: ctx.query.status
  };

  const all = await services.contributions.listContributions(filters);
  const total = all.length;
  const paginated = paginate(all, pagination);
  const sanitized = paginated.map(c => services.contributions.sanitizeForPublic(c));

  return ctx.list(sanitized, total, pagination.limit, pagination.offset);
}

/**
 * GET /contributions/:contributionId
 */
export async function getContributionHandler(ctx, services) {
  const contributionId = ctx.params.contributionId;
  if (!contributionId) {
    return ctx.error(ERROR_CODES.INVALID_REQUEST, 'Missing contributionId');
  }

  const contribution = await services.contributions.getContribution(contributionId);
  if (!contribution) {
    return ctx.error(ERROR_CODES.NOT_FOUND, 'Contribution not found');
  }

  return ctx.success(services.contributions.sanitizeForPublic(contribution));
}

/**
 * GET /contributors/:protocolId
 */
export async function getContributorHandler(ctx, services) {
  const protocolId = ctx.params.protocolId;
  if (!protocolId) {
    return ctx.error(ERROR_CODES.INVALID_REQUEST, 'Missing protocolId');
  }

  const profile = await services.reputation.getProfile(protocolId);
  if (!profile) {
    return ctx.error(ERROR_CODES.NOT_FOUND, 'Contributor not found');
  }

  return ctx.success(profile);
}

/**
 * GET /contributors/:protocolId/reputation
 */
export async function getReputationHandler(ctx, services) {
  const protocolId = ctx.params.protocolId;
  if (!protocolId) {
    return ctx.error(ERROR_CODES.INVALID_REQUEST, 'Missing protocolId');
  }

  const snapshot = await services.reputation.getLatestSnapshot(protocolId);
  if (!snapshot) {
    return ctx.error(ERROR_CODES.NOT_FOUND, 'No reputation snapshot found');
  }

  return ctx.success(services.reputation.sanitizeForPublic(snapshot));
}

/**
 * GET /contributors/:protocolId/contributions
 */
export async function getContributorContributionsHandler(ctx, services) {
  const protocolId = ctx.params.protocolId;
  if (!protocolId) {
    return ctx.error(ERROR_CODES.INVALID_REQUEST, 'Missing protocolId');
  }

  const pagination = parsePagination(ctx.query);
  const all = await services.contributions.listContributions({ contributor: protocolId });
  const total = all.length;
  const paginated = paginate(all, pagination);
  const sanitized = paginated.map(c => services.contributions.sanitizeForPublic(c));

  return ctx.list(sanitized, total, pagination.limit, pagination.offset);
}

/**
 * GET /nodes
 */
export async function listNodesHandler(ctx, services) {
  const pagination = parsePagination(ctx.query);
  const filters = {
    nodeType: ctx.query.nodeType,
    lifecycleStatus: ctx.query.lifecycleStatus,
    country: ctx.query.country,
    health: ctx.query.health
  };

  const all = await services.nodes.listNodes(filters);
  const total = all.length;
  const paginated = paginate(all, pagination);
  const sanitized = paginated.map(n => services.nodes.sanitizeForPublic(n));

  return ctx.list(sanitized, total, pagination.limit, pagination.offset);
}

/**
 * GET /nodes/:nodeId
 */
export async function getNodeHandler(ctx, services) {
  const nodeId = ctx.params.nodeId;
  if (!nodeId) {
    return ctx.error(ERROR_CODES.INVALID_REQUEST, 'Missing nodeId');
  }

  const node = await services.nodes.getNode(nodeId);
  if (!node) {
    return ctx.error(ERROR_CODES.NOT_FOUND, 'Node not found');
  }

  return ctx.success(services.nodes.sanitizeForPublic(node));
}

/**
 * GET /nodes/:nodeId/capabilities
 */
export async function getNodeCapabilitiesHandler(ctx, services) {
  const nodeId = ctx.params.nodeId;
  if (!nodeId) {
    return ctx.error(ERROR_CODES.INVALID_REQUEST, 'Missing nodeId');
  }

  const capabilities = await services.nodes.getCapabilities(nodeId);
  if (!capabilities) {
    return ctx.error(ERROR_CODES.NOT_FOUND, 'No capabilities found');
  }

  return ctx.success(capabilities);
}

/**
 * GET /nodes/:nodeId/health
 */
export async function getNodeHealthHandler(ctx, services) {
  const nodeId = ctx.params.nodeId;
  if (!nodeId) {
    return ctx.error(ERROR_CODES.INVALID_REQUEST, 'Missing nodeId');
  }

  const health = await services.nodes.getHealth(nodeId);
  if (!health) {
    return ctx.error(ERROR_CODES.NOT_FOUND, 'Node not found');
  }

  return ctx.success(health);
}

/**
 * GET /network/summary
 */
export async function networkSummaryHandler(ctx, services) {
  const summary = await services.buildNetworkSummary();
  return ctx.success(summary);
}

/**
 * GET /network/snapshot
 */
export async function networkSnapshotHandler(ctx, services) {
  const snapshot = await services.buildNetworkSnapshot();
  return ctx.success(snapshot);
}

// ==================== Route Registry ====================

/**
 * Route registry mapping URL patterns to handlers
 */
export const ROUTES = [
  { method: 'GET', path: '/api/protocol/v1/health', handler: healthHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/protocol', handler: protocolHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/protocol/mainnet', handler: mainnetHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/contributions', handler: listContributionsHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/contributions/:contributionId', handler: getContributionHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/contributors/:protocolId', handler: getContributorHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/contributors/:protocolId/reputation', handler: getReputationHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/contributors/:protocolId/contributions', handler: getContributorContributionsHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/nodes', handler: listNodesHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/nodes/:nodeId', handler: getNodeHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/nodes/:nodeId/capabilities', handler: getNodeCapabilitiesHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/nodes/:nodeId/health', handler: getNodeHealthHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/network/summary', handler: networkSummaryHandler, auth: 'public' },
  { method: 'GET', path: '/api/protocol/v1/network/snapshot', handler: networkSnapshotHandler, auth: 'public' }
];

/**
 * Match URL pattern with params
 * @param {string} pattern - URL pattern with :params
 * @param {string} url - Request URL
 * @returns {object|null} Params or null
 */
export function matchRoute(pattern, url) {
  const patternParts = pattern.split('/');
  const urlParts = url.split('?')[0].split('/');

  if (patternParts.length !== urlParts.length) {
    return null;
  }

  const params = {};
  for (let i = 0; i < patternParts.length; i++) {
    if (patternParts[i].startsWith(':')) {
      const key = patternParts[i].substring(1);
      params[key] = urlParts[i];
    } else if (patternParts[i] !== urlParts[i]) {
      return null;
    }
  }

  return params;
}

/**
 * Find route handler for URL
 * @param {string} method - HTTP method
 * @param {string} url - Request URL
 * @returns {object|null} Route info
 */
export function findRoute(method, url) {
  for (const route of ROUTES) {
    if (route.method !== method) continue;

    const params = matchRoute(route.path, url);
    if (params) {
      return { ...route, params };
    }
  }

  return null;
}

/**
 * Simple API server for testing
 * @param {object} options - Server options
 * @param {object} options.services - Domain services
 * @returns {object} Server instance
 */
export function createServer(options) {
  const { services } = options;

  return {
    routes: ROUTES,

    /**
     * Handle incoming request
     * @param {string} method - HTTP method
     * @param {string} url - Request URL
     * @param {object} [request] - Request data
     * @returns {Promise<object>} Response
     */
    async handle(method, url, request = {}) {
      const [path, queryString] = url.split('?');
      const query = {};
      if (queryString) {
        for (const part of queryString.split('&')) {
          const [key, value] = part.split('=');
          query[decodeURIComponent(key)] = decodeURIComponent(value || '');
        }
      }

      const route = findRoute(method, path);
      if (!route) {
        const ctx = new ApiContext();
        return ctx.error(ERROR_CODES.NOT_FOUND, 'Route not found');
      }

      const ctx = new ApiContext({
        params: route.params,
        query,
        body: request.body,
        requestId: request.requestId
      });

      return await route.handler(ctx, services);
    }
  };
}

export {
  DEFAULT_LIMIT,
  MAX_LIMIT,
  ALLOWED_SORT_KEYS
};

export default {
  ApiContext,
  createServer,
  findRoute,
  matchRoute,
  ROUTES,
  DEFAULT_LIMIT,
  MAX_LIMIT,
  ALLOWED_SORT_KEYS
};
