/**
 * MOOD Protocol API - OpenAPI Specification
 *
 * Generates OpenAPI 3.0 spec for the Protocol API.
 * Per OPENAPI_REQUIREMENTS.md.
 */

import { ROUTES } from '../routes/handlers.js';
import { API_VERSION } from '../core/envelope.js';
import { ERROR_CODES } from '../core/errors.js';

/**
 * Generate OpenAPI specification
 * @returns {object} OpenAPI spec
 */
export function generateOpenApiSpec() {
  return {
    openapi: '3.0.0',
    info: {
      title: 'MOOD Protocol API',
      version: API_VERSION,
      description: 'Unified protocol-facing API exposing MPF-001 through MPF-004 authority',
      contact: {
        name: 'MOOD Protocol'
      }
    },
    servers: [
      { url: '/api/protocol/v1', description: 'Production' },
      { url: 'http://localhost:3000/api/protocol/v1', description: 'Local development' }
    ],
    tags: [
      { name: 'health', description: 'API health' },
      { name: 'protocol', description: 'Protocol facts' },
      { name: 'contributions', description: 'Contribution records' },
      { name: 'contributors', description: 'Contributor profiles' },
      { name: 'nodes', description: 'Node registry' },
      { name: 'network', description: 'Network aggregates' }
    ],
    paths: generatePaths(),
    components: {
      schemas: generateSchemas(),
      responses: generateResponses(),
      parameters: generateParameters()
    }
  };
}

/**
 * Generate paths from route registry
 * @returns {object} OpenAPI paths
 */
function generatePaths() {
  const paths = {};

  for (const route of ROUTES) {
    const openApiPath = route.path.replace(/:(\w+)/g, '{$1}');

    if (!paths[openApiPath]) {
      paths[openApiPath] = {};
    }

    paths[openApiPath][route.method.toLowerCase()] = generatePathItem(route);
  }

  return paths;
}

/**
 * Generate path item for a route
 * @param {object} route - Route definition
 * @returns {object} OpenAPI path item
 */
function generatePathItem(route) {
  const item = {
    tags: [route.path.split('/')[3] || 'general'],
    summary: generateSummary(route),
    description: generateDescription(route),
    operationId: route.handler.name,
    responses: {
      '200': { $ref: '#/components/responses/Success' },
      '400': { $ref: '#/components/responses/InvalidRequest' },
      '404': { $ref: '#/components/responses/NotFound' },
      '500': { $ref: '#/components/responses/InternalError' }
    }
  };

  // Add path parameters
  const paramMatches = route.path.matchAll(/:(\w+)/g);
  const pathParams = [];
  for (const match of paramMatches) {
    pathParams.push({
      name: match[1],
      in: 'path',
      required: true,
      schema: { type: 'string' }
    });
  }
  if (pathParams.length > 0) {
    item.parameters = pathParams;
  }

  // Add query parameters for list endpoints
  if (route.path.endsWith('/contributions') ||
      route.path.endsWith('/nodes') ||
      route.path.includes('/contributors/') && route.path.endsWith('/contributions')) {
    item.parameters = item.parameters || [];
    item.parameters.push(
      {
        name: 'limit',
        in: 'query',
        required: false,
        schema: { type: 'integer', default: 50, maximum: 200, minimum: 1 }
      },
      {
        name: 'offset',
        in: 'query',
        required: false,
        schema: { type: 'integer', default: 0, minimum: 0 }
      }
    );
  }

  // Filter parameters for contributions
  if (route.path.endsWith('/contributions') && !route.path.includes(':')) {
    item.parameters = item.parameters || [];
    item.parameters.push(
      { name: 'category', in: 'query', required: false, schema: { type: 'string' } },
      { name: 'status', in: 'query', required: false, schema: { type: 'string' } }
    );
  }

  // Filter parameters for nodes
  if (route.path.endsWith('/nodes') && !route.path.includes(':')) {
    item.parameters = item.parameters || [];
    item.parameters.push(
      { name: 'nodeType', in: 'query', required: false, schema: { type: 'string' } },
      { name: 'lifecycleStatus', in: 'query', required: false, schema: { type: 'string' } },
      { name: 'country', in: 'query', required: false, schema: { type: 'string' } },
      { name: 'health', in: 'query', required: false, schema: { type: 'string' } }
    );
  }

  return item;
}

/**
 * Generate summary for route
 * @param {object} route - Route definition
 * @returns {string} Summary
 */
function generateSummary(route) {
  const summaries = {
    healthHandler: 'Get API health status',
    protocolHandler: 'Get protocol status',
    mainnetHandler: 'Get mainnet facts',
    listContributionsHandler: 'List contributions',
    getContributionHandler: 'Get contribution by ID',
    getContributorHandler: 'Get contributor profile',
    getReputationHandler: 'Get reputation snapshot',
    getContributorContributionsHandler: 'List contributor contributions',
    listNodesHandler: 'List nodes',
    getNodeHandler: 'Get node by ID',
    getNodeCapabilitiesHandler: 'Get node capabilities',
    getNodeHealthHandler: 'Get node health',
    networkSummaryHandler: 'Get network summary',
    networkSnapshotHandler: 'Get network snapshot'
  };

  return summaries[route.handler.name] || 'API endpoint';
}

/**
 * Generate description for route
 * @param {object} route - Route definition
 * @returns {string} Description
 */
function generateDescription(route) {
  return 'Public read endpoint. Rate limited. No authentication required.';
}

/**
 * Generate schemas
 * @returns {object} OpenAPI schemas
 */
function generateSchemas() {
  return {
    SuccessEnvelope: {
      type: 'object',
      required: ['apiVersion', 'data', 'meta'],
      properties: {
        apiVersion: { type: 'string', const: 'v1' },
        data: {},
        meta: {
          type: 'object',
          required: ['requestId', 'generatedAt'],
          properties: {
            requestId: { type: 'string' },
            generatedAt: { type: 'string', format: 'date-time' },
            pagination: { type: 'object', nullable: true }
          }
        }
      }
    },
    ErrorEnvelope: {
      type: 'object',
      required: ['apiVersion', 'error', 'meta'],
      properties: {
        apiVersion: { type: 'string', const: 'v1' },
        error: {
          type: 'object',
          required: ['code', 'message', 'details'],
          properties: {
            code: {
              type: 'string',
              enum: Object.values(ERROR_CODES)
            },
            message: { type: 'string' },
            details: { nullable: true }
          }
        },
        meta: {
          type: 'object',
          required: ['requestId'],
          properties: {
            requestId: { type: 'string' }
          }
        }
      }
    },
    HealthResponse: {
      type: 'object',
      properties: {
        status: { type: 'string', enum: ['ok', 'degraded'] },
        apiVersion: { type: 'string' },
        components: { type: 'object' }
      }
    },
    NetworkSummary: {
      type: 'object',
      required: ['protocol', 'contributors', 'contributions', 'nodes', 'reputation', 'sources', 'generatedAt'],
      properties: {
        protocol: { type: 'object' },
        contributors: {
          type: 'object',
          properties: {
            count: { type: 'integer', minimum: 0 }
          }
        },
        contributions: {
          type: 'object',
          properties: {
            total: { type: 'integer', minimum: 0 },
            verified: { type: 'integer', minimum: 0 }
          }
        },
        nodes: {
          type: 'object',
          properties: {
            total: { type: 'integer' },
            active: { type: 'integer' },
            byType: { type: 'object' },
            byRegion: { type: 'object' }
          }
        },
        reputation: {
          type: 'object',
          properties: {
            profiles: { type: 'integer' },
            snapshots: { type: 'integer' }
          }
        },
        sources: { type: 'object' },
        generatedAt: { type: 'string', format: 'date-time' }
      }
    }
  };
}

/**
 * Generate standard responses
 * @returns {object} OpenAPI responses
 */
function generateResponses() {
  return {
    Success: {
      description: 'Successful response',
      content: {
        'application/json': {
          schema: { $ref: '#/components/schemas/SuccessEnvelope' }
        }
      }
    },
    InvalidRequest: {
      description: 'Invalid request',
      content: {
        'application/json': {
          schema: { $ref: '#/components/schemas/ErrorEnvelope' }
        }
      }
    },
    NotFound: {
      description: 'Resource not found',
      content: {
        'application/json': {
          schema: { $ref: '#/components/schemas/ErrorEnvelope' }
        }
      }
    },
    InternalError: {
      description: 'Internal server error',
      content: {
        'application/json': {
          schema: { $ref: '#/components/schemas/ErrorEnvelope' }
        }
      }
    }
  };
}

/**
 * Generate reusable parameters
 * @returns {object} OpenAPI parameters
 */
function generateParameters() {
  return {};
}

/**
 * Write OpenAPI spec to JSON string
 * @returns {string} JSON string
 */
export function writeOpenApiJson() {
  return JSON.stringify(generateOpenApiSpec(), null, 2);
}

export default {
  generateOpenApiSpec,
  writeOpenApiJson
};
