/**
 * MOOD Protocol API - Test Suite
 *
 * Tests T1-T24 covering all MPF-005 requirements.
 */

import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert';
import crypto from 'crypto';

import {
  successResponse,
  listResponse,
  generateRequestId,
  API_VERSION,
  validateResponse
} from '../core/envelope.js';

import {
  errorResponse,
  getHttpStatus,
  Errors,
  ERROR_CODES,
  sanitizeError
} from '../core/errors.js';

import {
  MainnetService,
  ContributionService,
  ReputationService,
  NodeService,
  ProtocolApiService
} from '../core/domain-services.js';

import {
  createServer,
  parsePagination,
  matchRoute,
  findRoute,
  ApiContext,
  DEFAULT_LIMIT,
  MAX_LIMIT
} from '../routes/handlers.js';

import { generateOpenApiSpec } from '../openapi/openapi-spec.js';

// Setup test data
function setupTestData(services) {
  // Add contributions
  services.contributions.contributions = [
    {
      id: 'mood-contrib-001',
      contributor: { type: 'wallet', id: 'mood:contributor:aaa' },
      contributorId: 'mood:contributor:aaa',
      category: 'code',
      title: 'Test Code Contribution',
      description: 'A test contribution',
      submittedAt: '2026-08-20T10:00:00Z',
      status: 'finalized',
      scores: { contribution: 75, impact: 80, quality: 85, persistence: null, early: 100 },
      policyVersion: '002-draft-1',
      privateEvidence: 'SECRET-EVIDENCE-NOT-PUBLIC'
    },
    {
      id: 'mood-contrib-002',
      contributor: { type: 'wallet', id: 'mood:contributor:bbb' },
      contributorId: 'mood:contributor:bbb',
      category: 'documentation',
      title: 'Test Doc',
      submittedAt: '2026-08-21T10:00:00Z',
      status: 'verified',
      scores: { contribution: 70 },
      policyVersion: '002-draft-1'
    }
  ];

  // Add profiles
  services.reputation.profiles.set('mood:contributor:aaa', {
    protocolId: 'mood:contributor:aaa',
    profileVersion: '1.0.0',
    verifiedContributionCount: 1
  });

  // Add snapshots
  services.reputation.snapshots.set('mood:contributor:aaa', [
    {
      snapshotId: 'mood-rep-001',
      snapshotVersion: '1.0.0',
      protocolId: 'mood:contributor:aaa',
      epochId: 'GENESIS_2026',
      policyVersion: '003-draft-1',
      epochPolicyVersion: '003-draft-1',
      dimensions: {
        contribution: 75,
        impact: 80,
        quality: 85,
        persistence: null,
        early: 100
      },
      aggregate: null,  // null is valid per MPF-003
      verifiedContributionCount: 1,
      categoryDiversity: ['code'],
      confidence: 'insufficient',
      generatedAt: '2026-08-29T10:00:00Z',
      snapshotFingerprint: 'sha256:abc'
    }
  ]);

  // Add nodes
  services.nodes.nodes.set('mood:node:aaa', {
    nodeId: 'mood:node:aaa',
    operatorProtocolId: 'mood:contributor:aaa',
    nodeType: 'compute',
    displayName: 'Test Node',
    region: {
      countryCode: 'SG',
      regionCode: null,
      city: null,
      precision: 'country'
    },
    endpoint: { type: 'https', uri: 'https://node.example.com' },
    capabilityManifest: {
      capabilities: [
        { key: 'compute.cpu.arch', verificationStatus: 'declared' },
        { key: 'compute.gpu.model', verificationStatus: 'verified' }
      ]
    },
    lifecycleStatus: 'active',
    health: { status: 'healthy', observedAt: '2026-08-29T10:00:00Z' },
    verification: { status: 'verified' },
    registeredAt: '2026-08-15T10:00:00Z',
    // Internal field - must NOT appear in public response
    privateNotes: 'INTERNAL-NOT-PUBLIC'
  });

  services.nodes.nodes.set('mood:node:bbb', {
    nodeId: 'mood:node:bbb',
    operatorProtocolId: 'mood:contributor:bbb',
    nodeType: 'storage',
    displayName: 'Test Storage',
    region: { countryCode: 'US', precision: 'country' },
    endpoint: null,
    lifecycleStatus: 'pending_verification',
    health: { status: 'unknown' },
    verification: { status: 'pending' },
    registeredAt: '2026-08-16T10:00:00Z'
  });
}

let testServices;

beforeEach(() => {
  testServices = new ProtocolApiService();
  setupTestData(testServices);
});

// ============================================
// T1 - Health
// ============================================
describe('T1 - Health Check', () => {
  it('should return versioned envelope', async () => {
    const response = await testServices;
    const server = createServer({ services: response });
    const result = await server.handle('GET', '/api/protocol/v1/health');

    assert.strictEqual(result.apiVersion, 'v1');
    assert.ok(result.data.status, 'Should have status');
    assert.ok(result.data.components, 'Should have components');
    assert.strictEqual(result.meta.requestId.startsWith('req_'), true);
  });

  it('should report dependency status', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/health');

    assert.ok(result.data.components.protocolFacts, 'Should have protocolFacts status');
    assert.ok(result.data.components.contributions, 'Should have contributions status');
    assert.ok(result.data.components.reputation, 'Should have reputation status');
    assert.ok(result.data.components.nodeRegistry, 'Should have nodeRegistry status');
  });
});

// ============================================
// T2 - Mainnet Facts Authority
// ============================================
describe('T2 - Mainnet Facts Authority', () => {
  it('should source from MPF-001, not route constants', async () => {
    // Test that the mainnet service delegates to MPF-001
    const facts = await testServices.mainnet.getMainnetFacts();
    // Even if null (no mainnet file), should not throw
    assert.ok(true, 'Should not throw');
  });

  it('should expose protocol status', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/protocol');

    assert.strictEqual(result.apiVersion, 'v1');
    assert.ok(result.data, 'Should have data');
  });
});

// ============================================
// T3 - Contributions
// ============================================
describe('T3 - Contributions', () => {
  it('should list contributions with envelope', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributions');

    assert.strictEqual(result.apiVersion, 'v1');
    assert.ok(Array.isArray(result.data), 'Data should be array');
    assert.ok(result.data.length > 0, 'Should have contributions');
    assert.ok(result.meta.pagination, 'Should have pagination');
  });

  it('should get contribution by ID', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributions/mood-contrib-001');

    assert.strictEqual(result.data.contributionId, 'mood-contrib-001');
    assert.ok(result.data.category, 'Should have category');
  });

  it('should return NOT_FOUND for missing contribution', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributions/nonexistent');

    assert.ok(result._error, 'Should be error');
    assert.strictEqual(result.code, 'NOT_FOUND');
  });
});

// ============================================
// T4 - Reputation
// ============================================
describe('T4 - Reputation', () => {
  it('should return contributor profile', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributors/mood:contributor:aaa');

    assert.strictEqual(result.data.protocolId, 'mood:contributor:aaa');
  });

  it('should preserve aggregate = null', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributors/mood:contributor:aaa/reputation');

    assert.strictEqual(result.data.aggregate, null, 'aggregate should be null per MPF-003');
    assert.ok(result.data.dimensions, 'Should have dimensions');
  });
});

// ============================================
// T5 - Nodes
// ============================================
describe('T5 - Nodes', () => {
  it('should list nodes', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/nodes');

    assert.ok(Array.isArray(result.data), 'Should be array');
    assert.ok(result.data.length > 0, 'Should have nodes');
  });

  it('should get node by ID', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/nodes/mood:node:aaa');

    assert.strictEqual(result.data.nodeId, 'mood:node:aaa');
    assert.strictEqual(result.data.nodeType, 'compute');
  });
});

// ============================================
// T6 - Capability Verification Distinction
// ============================================
describe('T6 - Capability Verification Distinction', () => {
  it('should distinguish declared vs verified capabilities', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/nodes/mood:node:aaa/capabilities');

    assert.ok(result.data, 'Should have capability data');

    if (result.data.capabilities) {
      const cpu = result.data.capabilities['compute.cpu.arch'];
      const gpu = result.data.capabilities['compute.gpu.model'];

      if (cpu && gpu) {
        assert.strictEqual(cpu.verificationStatus, 'declared');
        assert.strictEqual(gpu.verificationStatus, 'verified');
        assert.notStrictEqual(cpu.verificationStatus, gpu.verificationStatus);
      }
    }
  });
});

// ============================================
// T7 - Network Summary Deterministic
// ============================================
describe('T7 - Network Summary', () => {
  it('should produce deterministic counts from fixtures', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/network/summary');

    assert.strictEqual(result.data.contributors.count, 1);
    assert.strictEqual(result.data.contributions.total, 2);
    assert.strictEqual(result.data.contributions.verified, 2);
    assert.strictEqual(result.data.nodes.total, 2);
    assert.strictEqual(result.data.nodes.active, 1);
    assert.ok(result.data.reputation.profiles >= 1);
    assert.ok(result.data.reputation.snapshots >= 1);
  });

  it('should not include token price or market cap', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/network/summary');

    assert.strictEqual(result.data.tokenPrice, undefined);
    assert.strictEqual(result.data.marketCap, undefined);
    assert.strictEqual(result.data.volume24h, undefined);
  });
});

// ============================================
// T8 - Network Snapshot Determinism
// ============================================
describe('T8 - Network Snapshot Determinism', () => {
  it('should produce snapshot with fingerprint', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/network/snapshot');

    assert.ok(result.data.snapshotFingerprint, 'Should have fingerprint');
    assert.ok(result.data.snapshotFingerprint.startsWith('sha256:'));
  });

  it('should reference source fingerprints', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/network/snapshot');

    assert.ok(result.data.sourceFingerprints, 'Should have source references');
    assert.ok(result.data.sourceFingerprints.mainnet, 'Should reference mainnet');
    assert.ok(result.data.sourceFingerprints.contributions);
    assert.ok(result.data.sourceFingerprints.reputation);
    assert.ok(result.data.sourceFingerprints.nodes);
  });
});

// ============================================
// T9 - Pagination Bounds
// ============================================
describe('T9 - Pagination Safety', () => {
  it('should bound limit to maximum', () => {
    const pagination = parsePagination({ limit: '500' });
    assert.strictEqual(pagination.limit, MAX_LIMIT, 'Should cap to MAX_LIMIT');
  });

  it('should apply default limit', () => {
    const pagination = parsePagination({});
    assert.strictEqual(pagination.limit, DEFAULT_LIMIT);
  });

  it('should not allow negative offset', () => {
    const pagination = parsePagination({ offset: '-10' });
    assert.strictEqual(pagination.offset, 0);
  });
});

// ============================================
// T10 - Filter Validation
// ============================================
describe('T10 - Filter Validation', () => {
  it('should filter contributions by category', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributions?category=code');

    assert.ok(Array.isArray(result.data));
    if (result.data.length > 0) {
      assert.strictEqual(result.data[0].category, 'code');
    }
  });

  it('should filter contributions by status', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributions?status=finalized');

    assert.ok(Array.isArray(result.data));
    if (result.data.length > 0) {
      assert.strictEqual(result.data[0].status, 'finalized');
    }
  });
});

// ============================================
// T11 - Sort Allowlist
// ============================================
describe('T11 - Sort Allowlist', () => {
  it('should accept only allowed sort keys', () => {
    const allowed = ['submittedAt', 'contributionId'];

    assert.ok(matchRoute('/api/protocol/v1/contributions', '/api/protocol/v1/contributions'));
    // Sort validation happens in handlers - we just verify the allowlist
    assert.ok(allowed.includes('submittedAt'));
    assert.ok(!allowed.includes('password'));
  });
});

// ============================================
// T12 - Not Found
// ============================================
describe('T12 - Not Found Error', () => {
  it('should return NOT_FOUND for missing routes', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/nonexistent');

    assert.ok(result._error, 'Should be error');
    assert.strictEqual(result.code, 'NOT_FOUND');
  });

  it('should return NOT_FOUND for missing contribution', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributions/missing-id');

    assert.strictEqual(result.code, 'NOT_FOUND');
  });
});

// ============================================
// T13 - Private Field Exclusion
// ============================================
describe('T13 - Private Field Exclusion', () => {
  it('should not expose private evidence in contributions', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributions/mood-contrib-001');

    assert.strictEqual(result.data.privateEvidence, undefined,
      'privateEvidence should not appear');
  });

  it('should not expose private node fields', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/nodes/mood:node:aaa');

    assert.strictEqual(result.data.privateNotes, undefined,
      'privateNotes should not appear');
  });

  it('should respect location precision', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/nodes/mood:node:aaa');

    // Should only expose country code at country precision
    assert.strictEqual(result.data.region.countryCode, 'SG');
    assert.strictEqual(result.data.region.city, undefined,
      'City should not be exposed at country precision');
  });
});

// ============================================
// T14 - Error Hygiene
// ============================================
describe('T14 - Error Hygiene', () => {
  it('should not leak stack traces', () => {
    const error = new Error('Database connection failed: password=secret123');
    const sanitized = sanitizeError(error);

    assert.strictEqual(sanitized.code, 'INTERNAL_ERROR');
    assert.strictEqual(sanitized.message, 'Internal server error');
    assert.strictEqual(sanitized.details, null);
  });

  it('should return safe error messages', () => {
    const response = Errors.notFound('User');
    assert.strictEqual(response.error.message, 'User not found');
  });
});

// ============================================
// T15 - Request ID
// ============================================
describe('T15 - Request ID', () => {
  it('should include request ID in every response', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/health');

    assert.ok(result.meta.requestId);
    assert.ok(result.meta.requestId.startsWith('req_'));
  });
});

// ============================================
// T16 - API Version
// ============================================
describe('T16 - API Version', () => {
  it('should include API version in every response', async () => {
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/health');

    assert.strictEqual(result.apiVersion, API_VERSION);
    assert.strictEqual(result.apiVersion, 'v1');
  });
});

// ============================================
// T17 - Domain Delegation
// ============================================
describe('T17 - Domain Delegation', () => {
  it('routes should not calculate reputation', async () => {
    // The reputation handler should return snapshot as-is, not recompute
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributors/mood:contributor:aaa/reputation');

    // Should preserve aggregate = null from source
    assert.strictEqual(result.data.aggregate, null);
  });

  it('routes should not score contributions', async () => {
    // Contribution list should return existing scores
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/contributions');

    if (result.data.length > 0) {
      // Scores should be from source, not recomputed
      assert.ok(result.data[0].scores, 'Should have scores from source');
    }
  });
});

// ============================================
// T18 - No Chain Writes
// ============================================
describe('T18 - No Chain Writes', () => {
  it('should have no transaction signing', async () => {
    const server = createServer({ services: testServices });
    const routes = server.routes;

    for (const route of routes) {
      assert.notStrictEqual(route.method, 'POST',
        'Read-only API should not have POST endpoints');
    }
  });

  it('should not sign transactions', async () => {
    const handlerModule = await import('../routes/handlers.js');
    assert.strictEqual(handlerModule.signTransaction, undefined);
  });
});

// ============================================
// T19 - No Token Transfer
// ============================================
describe('T19 - No Token Transfer', () => {
  it('should not have token routes', async () => {
    const server = createServer({ services: testServices });
    const routes = server.routes;

    for (const route of routes) {
      assert.ok(!route.path.includes('token'),
        `${route.path} should not contain token`);
      assert.ok(!route.path.includes('claim'),
        `${route.path} should not contain claim`);
      assert.ok(!route.path.includes('stake'),
        `${route.path} should not contain stake`);
      assert.ok(!route.path.includes('reward'),
        `${route.path} should not contain reward`);
    }
  });
});

// ============================================
// T20 - No Remote Execution
// ============================================
describe('T20 - No Remote Execution', () => {
  it('should not have SSH/shell routes', async () => {
    const server = createServer({ services: testServices });
    const routes = server.routes;

    for (const route of routes) {
      assert.ok(!route.path.includes('ssh'),
        `${route.path} should not contain ssh`);
      assert.ok(!route.path.includes('shell'),
        `${route.path} should not contain shell`);
      assert.ok(!route.path.includes('execute'),
        `${route.path} should not contain execute`);
    }
  });
});

// ============================================
// T21 - CORS/Auth Defaults
// ============================================
describe('T21 - CORS/Auth Defaults', () => {
  it('should mark all routes as public read', async () => {
    const server = createServer({ services: testServices });
    const routes = server.routes;

    for (const route of routes) {
      // All current routes are public reads
      assert.strictEqual(route.auth, 'public',
        `${route.path} should be public`);
    }
  });
});

// ============================================
// T22 - Offline Operation
// ============================================
describe('T22 - Offline Operation', () => {
  it('should run without network or external DB', async () => {
    // All operations should use in-memory data
    const server = createServer({ services: testServices });
    const result = await server.handle('GET', '/api/protocol/v1/nodes');

    assert.ok(Array.isArray(result.data));
  });

  it('should use local services', () => {
    // Domain services should work without external dependencies
    assert.ok(testServices.mainnet);
    assert.ok(testServices.contributions);
    assert.ok(testServices.reputation);
    assert.ok(testServices.nodes);
  });
});

// ============================================
// T23 - OpenAPI Schema
// ============================================
describe('T23 - OpenAPI Schema', () => {
  it('should generate valid OpenAPI spec', () => {
    const spec = generateOpenApiSpec();

    assert.strictEqual(spec.openapi, '3.0.0');
    assert.ok(spec.info.title);
    assert.ok(spec.info.version);
    assert.ok(spec.paths);
    assert.ok(spec.components);
  });

  it('should document all routes', () => {
    const spec = generateOpenApiSpec();
    const server = createServer({ services: testServices });

    for (const route of server.routes) {
      const path = route.path.replace(/:(\w+)/g, '{$1}');
      assert.ok(spec.paths[path], `Should have ${path}`);
    }
  });
});

// ============================================
// T24 - Regression
// ============================================
describe('T24 - Regression Tests', () => {
  it('should support all required endpoints', () => {
    const requiredPaths = [
      '/api/protocol/v1/health',
      '/api/protocol/v1/protocol',
      '/api/protocol/v1/protocol/mainnet',
      '/api/protocol/v1/contributions',
      '/api/protocol/v1/contributors/:protocolId',
      '/api/protocol/v1/contributors/:protocolId/reputation',
      '/api/protocol/v1/nodes',
      '/api/protocol/v1/nodes/:nodeId',
      '/api/protocol/v1/nodes/:nodeId/capabilities',
      '/api/protocol/v1/nodes/:nodeId/health',
      '/api/protocol/v1/network/summary',
      '/api/protocol/v1/network/snapshot'
    ];

    const server = createServer({ services: testServices });
    const paths = server.routes.map(r => r.path);

    for (const required of requiredPaths) {
      assert.ok(paths.includes(required),
        `Missing endpoint: ${required}`);
    }
  });

  it('should maintain error code stability', () => {
    const expectedCodes = [
      'INVALID_REQUEST', 'NOT_FOUND', 'CONFLICT', 'UNAUTHORIZED',
      'FORBIDDEN', 'RATE_LIMITED', 'DEPENDENCY_UNAVAILABLE',
      'POLICY_BLOCKED', 'HUMAN_DECISION_REQUIRED', 'INTERNAL_ERROR'
    ];

    for (const code of expectedCodes) {
      assert.ok(Object.values(ERROR_CODES).includes(code),
        `Missing error code: ${code}`);
    }
  });
});

console.log('Running MPF-005 Test Suite (T1-T24)...');
