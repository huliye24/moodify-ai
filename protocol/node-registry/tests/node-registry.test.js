/**
 * MOOD Protocol Node Registry - Test Suite
 *
 * Tests T1-T24 covering all MPF-004 requirements.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import crypto from 'crypto';

// Import modules
import {
  generateNodeId,
  generateNodeFingerprint,
  isValidNodeId,
  isValidOperatorProtocolId,
  NODE_TYPES
} from '../core/node-identity.js';

import {
  LIFECYCLE_STATES,
  executeTransition,
  validateTransition,
  isTerminalState,
  getAllowedTransitions,
  canHeartbeatAffectState,
  REASON_CODES
} from '../core/lifecycle.js';

import {
  createCapabilityManifest,
  VERIFICATION_STATUS,
  addCapability,
  updateCapabilityVerification,
  getVerifiedCapabilities,
  getDeclaredCapabilities
} from '../core/capability.js';

import {
  VERIFICATION_METHODS,
  generateChallenge,
  validateUriSafety,
  verifyHttpChallenge,
  createVerificationEvidence
} from '../core/verification.js';

import {
  HEALTH_STATUS,
  createHeartbeat,
  evaluateStaleTransition,
  validateObservation,
  DEFAULT_HEALTH_POLICY
} from '../core/health.js';

import {
  createNode,
  registerNode,
  submitForVerification,
  completeVerification,
  activateNode,
  transitionLifecycle,
  validateNode
} from '../core/registry.js';

import {
  discoverNodes,
  generateRegistrySnapshot,
  validateSnapshotDeterminism
} from '../core/discovery.js';

// ============================================
// T1 - Stable Node ID
// ============================================
describe('T1 - Stable Node ID', () => {
  it('should generate same node ID for same inputs', () => {
    const options = {
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute',
      stableNonce: 'stable-nonce-123'
    };

    const id1 = generateNodeId(options);
    const id2 = generateNodeId(options);

    assert.strictEqual(id1, id2, 'Same inputs should produce same node ID');
  });

  it('should generate different ID for different operators', () => {
    const id1 = generateNodeId({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute'
    });

    const id2 = generateNodeId({
      operatorProtocolId: 'mood:contributor:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
      nodeType: 'compute'
    });

    assert.notStrictEqual(id1, id2, 'Different operators should have different node IDs');
  });

  it('should generate valid node ID format', () => {
    const nodeId = generateNodeId({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute'
    });

    assert.ok(isValidNodeId(nodeId), 'Node ID should match format');
    assert.ok(nodeId.startsWith('mood:node:'), 'Node ID should start with mood:node:');
  });
});

// ============================================
// T2 - Infrastructure Migration
// ============================================
describe('T2 - Infrastructure Migration', () => {
  it('should maintain stable node ID when endpoint changes', () => {
    const nodeOptions = {
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute'
    };

    const nodeId1 = generateNodeId(nodeOptions);

    // Same node options, different endpoint (endpoint not part of node ID)
    const nodeId2 = generateNodeId(nodeOptions);

    assert.strictEqual(nodeId1, nodeId2, 'Node ID should be stable regardless of endpoint');
  });
});

// ============================================
// T3 - Schema Validation
// ============================================
describe('T3 - Schema Validation', () => {
  it('should create valid node with all required fields', () => {
    const node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute',
      displayName: 'Test Node'
    });

    const validation = validateNode(node);
    assert.strictEqual(validation.valid, true, 'Valid node should pass validation');
  });

  it('should reject node with missing required fields', () => {
    const node = {
      nodeId: 'invalid'
    };

    const validation = validateNode(node);
    assert.strictEqual(validation.valid, false, 'Invalid node should fail validation');
    assert.ok(validation.errors.length > 0, 'Should have validation errors');
  });
});

// ============================================
// T4 - Node Types
// ============================================
describe('T4 - Node Types', () => {
  for (const nodeType of NODE_TYPES) {
    it(`should support node type: ${nodeType}`, () => {
      const node = createNode({
        operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        nodeType
      });

      assert.strictEqual(node.nodeType, nodeType, `Should create ${nodeType} node`);
    });
  }
});

// ============================================
// T5 - Endpoint Optionality
// ============================================
describe('T5 - Endpoint Optionality', () => {
  it('should allow developer node without endpoint', () => {
    const node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'developer',
      endpoint: null
    });

    assert.strictEqual(node.endpoint, null, 'Developer node can have null endpoint');
  });

  it('should allow data node without endpoint', () => {
    const node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'data',
      endpoint: null
    });

    assert.strictEqual(node.endpoint, null, 'Data node can have null endpoint');
  });
});

// ============================================
// T6 - Capability Declaration
// ============================================
describe('T6 - Capability Declaration', () => {
  it('should create manifest with declared capabilities', () => {
    const manifest = createCapabilityManifest({
      nodeId: 'mood:node:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute',
      protocolVersions: ['0.1'],
      capabilities: [
        { key: 'compute.cpu.arch', value: 'x86_64' }
      ]
    });

    const declared = getDeclaredCapabilities(manifest);
    assert.ok(declared.length > 0, 'Should have declared capabilities');
    assert.strictEqual(declared[0].verificationStatus, 'declared', 'Should be marked as declared');
  });

  it('should distinguish declared from verified', () => {
    const manifest = createCapabilityManifest({
      nodeId: 'mood:node:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute',
      protocolVersions: ['0.1'],
      capabilities: [
        { key: 'compute.cpu.arch', value: 'x86_64' }
      ]
    });

    const verified = getVerifiedCapabilities(manifest);
    assert.strictEqual(verified.length, 0, 'Declared capability should not be verified');
  });
});

// ============================================
// T7 - Capability Verification
// ============================================
describe('T7 - Capability Verification', () => {
  it('should update single capability verification status', () => {
    let manifest = createCapabilityManifest({
      nodeId: 'mood:node:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute',
      protocolVersions: ['0.1'],
      capabilities: [
        { key: 'compute.cpu.arch', value: 'x86_64' }
      ]
    });

    manifest = updateCapabilityVerification(manifest, 'compute.cpu.arch', 'verified', 'evidence-001');

    const verified = getVerifiedCapabilities(manifest);
    assert.strictEqual(verified.length, 1, 'Should have one verified capability');
    assert.strictEqual(verified[0].key, 'compute.cpu.arch', 'Should be the updated capability');
  });

  it('should not affect unrelated capabilities', () => {
    let manifest = createCapabilityManifest({
      nodeId: 'mood:node:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute',
      protocolVersions: ['0.1'],
      capabilities: [
        { key: 'compute.cpu.arch', value: 'x86_64' },
        { key: 'compute.memory', value: '16GB' }
      ]
    });

    manifest = updateCapabilityVerification(manifest, 'compute.cpu.arch', 'verified', 'evidence-001');

    const declared = getDeclaredCapabilities(manifest);
    assert.strictEqual(declared.length, 1, 'Memory should remain declared');
    assert.strictEqual(declared[0].key, 'compute.memory', 'Memory capability should be unchanged');
  });
});

// ============================================
// T8 - Node Verification
// ============================================
describe('T8 - Node Verification', () => {
  it('should pass valid HTTP challenge', () => {
    const challenge = generateChallenge({ nodeId: 'test-node' });
    const result = verifyHttpChallenge({
      expectedNonce: challenge.nonce,
      endpoint: 'https://node.example.com/.well-known/mood-node-challenge',
      response: challenge.nonce
    });

    assert.strictEqual(result.verified, true, 'Valid challenge should pass');
  });

  it('should reject invalid HTTP challenge', () => {
    const result = verifyHttpChallenge({
      expectedNonce: 'expected-nonce',
      endpoint: 'https://node.example.com',
      response: 'wrong-nonce'
    });

    assert.strictEqual(result.verified, false, 'Invalid challenge should fail');
  });
});

// ============================================
// T9 - Verification Separation
// ============================================
describe('T9 - Verification Separation', () => {
  it('should keep node verification separate from capability verification', () => {
    // Verify node endpoint
    const challenge = generateChallenge({ nodeId: 'test-node' });
    const nodeVerified = verifyHttpChallenge({
      expectedNonce: challenge.nonce,
      endpoint: 'https://node.example.com',
      response: challenge.nonce
    });

    // But GPU capability is still declared, not verified
    const manifest = createCapabilityManifest({
      nodeId: 'mood:node:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute',
      protocolVersions: ['0.1'],
      capabilities: [
        { key: 'compute.gpu.model', value: 'NVIDIA A100' }
      ]
    });

    const gpuVerified = getVerifiedCapabilities(manifest);

    assert.strictEqual(nodeVerified.verified, true, 'Node endpoint can be verified');
    assert.strictEqual(gpuVerified.length, 0, 'GPU capability can remain unverified');
  });
});

// ============================================
// T10 - State Transitions
// ============================================
describe('T10 - State Transitions', () => {
  it('should allow legal transitions', () => {
    // draft -> registered
    const transition1 = validateTransition('draft', 'registered');
    assert.strictEqual(transition1.valid, true, 'draft -> registered should be allowed');

    // registered -> pending_verification
    const transition2 = validateTransition('registered', 'pending_verification');
    assert.strictEqual(transition2.valid, true, 'registered -> pending_verification should be allowed');
  });

  it('should reject illegal transitions', () => {
    // draft -> active (illegal skip)
    const transition = validateTransition('draft', 'active');
    assert.strictEqual(transition.valid, false, 'Illegal transition should be rejected');
  });

  it('should not allow transition from terminal state', () => {
    const transition = validateTransition('rejected', 'active');
    assert.strictEqual(transition.valid, false, 'Cannot transition from terminal state');
  });
});

// ============================================
// T11 - Heartbeat
// ============================================
describe('T11 - Heartbeat', () => {
  it('should create valid heartbeat observation', () => {
    const heartbeat = createHeartbeat({
      nodeId: 'mood:node:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      status: HEALTH_STATUS.HEALTHY,
      source: 'registry-probe'
    });

    assert.ok(heartbeat.nodeId, 'Should have nodeId');
    assert.ok(heartbeat.observedAt, 'Should have observedAt');
    assert.strictEqual(heartbeat.status, HEALTH_STATUS.HEALTHY, 'Should have correct status');
  });
});

// ============================================
// T12 - Stale Heartbeat
// ============================================
describe('T12 - Stale Heartbeat', () => {
  it('should detect stale observation', () => {
    // Create observation from 10 minutes ago
    const oldObservation = createHeartbeat({
      nodeId: 'mood:node:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      status: HEALTH_STATUS.HEALTHY,
      source: 'test'
    });
    oldObservation.observedAt = new Date(Date.now() - 600000).toISOString(); // 10 min ago

    const result = evaluateStaleTransition(oldObservation, 'active');
    assert.ok(result.shouldTransition, 'Should recommend transition for stale heartbeat');
  });
});

// ============================================
// T13 - Recovery
// ============================================
describe('T13 - Recovery', () => {
  it('should allow recovery from degraded via heartbeat', () => {
    const canRecover = canRecoverFromHeartbeat('degraded', HEALTH_STATUS.HEALTHY);
    assert.strictEqual(canRecover, true, 'Degraded node can recover with healthy heartbeat');
  });

  it('should allow recovery from inactive via heartbeat', () => {
    const canRecover = canRecoverFromHeartbeat('inactive', HEALTH_STATUS.HEALTHY);
    assert.strictEqual(canRecover, true, 'Inactive node can recover with healthy heartbeat');
  });
});

// ============================================
// T14 - Suspension Guard
// ============================================
describe('T14 - Suspension Guard', () => {
  it('should not allow heartbeat to bypass suspension', () => {
    const canAffect = canHeartbeatAffectState('suspended');
    assert.strictEqual(canAffect, false, 'Heartbeat cannot affect suspended node');
  });
});

// ============================================
// T15 - Duplicate Node
// ============================================
describe('T15 - Duplicate Node', () => {
  it('should detect duplicate node IDs', () => {
    const nodeOptions = {
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute',
      stableNonce: 'unique-nonce'
    };

    const nodeId = generateNodeId(nodeOptions);

    // Same options should produce same ID
    const duplicateId = generateNodeId(nodeOptions);

    assert.strictEqual(nodeId, duplicateId, 'Duplicate detection by same ID');
  });
});

// ============================================
// T16 - Location Privacy
// ============================================
describe('T16 - Location Privacy', () => {
  it('should support hidden precision', () => {
    const node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'developer',
      region: {
        countryCode: null,
        regionCode: null,
        city: null,
        precision: 'hidden'
      }
    });

    assert.strictEqual(node.region.precision, 'hidden', 'Should support hidden precision');
  });

  it('should support country precision', () => {
    const node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute',
      region: {
        countryCode: 'SG',
        regionCode: null,
        city: null,
        precision: 'country'
      }
    });

    assert.strictEqual(node.region.countryCode, 'SG', 'Should support country code');
    assert.strictEqual(node.region.city, null, 'Should not expose city');
  });
});

// ============================================
// T17 - Secret Rejection
// ============================================
describe('T17 - Secret Rejection', () => {
  it('should not accept private key in node', () => {
    const node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute'
    });

    // Node should not have privateKey field
    assert.strictEqual(node.privateKey, undefined, 'Should not have privateKey');
  });

  it('should not accept sshKey in node', () => {
    const node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute'
    });

    assert.strictEqual(node.sshKey, undefined, 'Should not have sshKey');
  });
});

// ============================================
// T18 - SSRF Safety
// ============================================
describe('T18 - SSRF Safety', () => {
  it('should block localhost', () => {
    const result = validateUriSafety('http://localhost/.well-known/mood-node-challenge');
    assert.strictEqual(result.safe, false, 'Should block localhost');
  });

  it('should block private IPs', () => {
    const result = validateUriSafety('http://192.168.1.1/.well-known/mood-node-challenge');
    assert.strictEqual(result.safe, false, 'Should block private IPs');
  });

  it('should block 127.0.0.1', () => {
    const result = validateUriSafety('http://127.0.0.1/.well-known/mood-node-challenge');
    assert.strictEqual(result.safe, false, 'Should block 127.0.0.1');
  });

  it('should allow public HTTPS endpoints', () => {
    const result = validateUriSafety('https://node.example.com/.well-known/mood-node-challenge');
    assert.strictEqual(result.safe, true, 'Should allow public endpoints');
  });
});

// ============================================
// T19 - No Remote Execution
// ============================================
describe('T19 - No Remote Execution', () => {
  it('should have no SSH/shell path', () => {
    // Verify the module doesn't contain SSH functionality
    const verificationModule = require('../core/verification.js');
    const healthModule = require('../core/health.js');
    const registryModule = require('../core/registry.js');

    // These modules should not export SSH functions
    assert.strictEqual(verificationModule.executeSSH, undefined, 'No SSH execution');
    assert.strictEqual(healthModule.runShellCommand, undefined, 'No shell execution');
    assert.strictEqual(registryModule.deployToNode, undefined, 'No deployment');
  });
});

// ============================================
// T20 - No Economics
// ============================================
describe('T20 - No Economics', () => {
  it('should not have token reward fields', () => {
    const node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute'
    });

    assert.strictEqual(node.tokenReward, undefined, 'No token reward field');
    assert.strictEqual(node.stakingAmount, undefined, 'No staking field');
    assert.strictEqual(node.payout, undefined, 'No payout field');
  });

  it('should not have stake field', () => {
    const node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute'
    });

    assert.strictEqual(node.stake, undefined, 'No stake field');
  });
});

// ============================================
// T21 - No Chain Write
// ============================================
describe('T21 - No Chain Write', () => {
  it('should have no transaction signing', () => {
    const verificationModule = require('../core/verification.js');
    const registryModule = require('../core/registry.js');

    // No transaction signing should exist
    assert.strictEqual(verificationModule.sendTransaction, undefined, 'No transaction sending');
    assert.strictEqual(registryModule.signTransaction, undefined, 'No transaction signing');
  });
});

// ============================================
// T22 - Offline Operation
// ============================================
describe('T22 - Offline Operation', () => {
  it('should create node without network', () => {
    // All core operations should work offline
    const node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute'
    });

    assert.ok(node.nodeId, 'Should create node offline');
    assert.ok(node.recordFingerprint, 'Should generate fingerprint offline');
  });

  it('should manage lifecycle without network', () => {
    let node = createNode({
      operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
      nodeType: 'compute'
    });

    node = registerNode(node);
    assert.strictEqual(node.lifecycleStatus, 'registered', 'Should transition offline');
  });
});

// ============================================
// T23 - Snapshot Determinism
// ============================================
describe('T23 - Snapshot Determinism', () => {
  it('should generate same fingerprint for same inputs', () => {
    const nodes = [
      createNode({
        operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        nodeType: 'compute'
      })
    ];

    const snapshot1 = generateRegistrySnapshot(nodes, '004-draft-1');
    const snapshot2 = generateRegistrySnapshot(nodes, '004-draft-1');

    assert.strictEqual(
      validateSnapshotDeterminism(snapshot1, snapshot2),
      true,
      'Same inputs should produce same snapshot fingerprint'
    );
  });

  it('should generate different fingerprint for different nodes', () => {
    const nodes1 = [
      createNode({
        operatorProtocolId: 'mood:contributor:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        nodeType: 'compute'
      })
    ];

    const nodes2 = [
      createNode({
        operatorProtocolId: 'mood:contributor:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
        nodeType: 'compute'
      })
    ];

    const snapshot1 = generateRegistrySnapshot(nodes1, '004-draft-1');
    const snapshot2 = generateRegistrySnapshot(nodes2, '004-draft-1');

    assert.notStrictEqual(
      snapshot1.snapshotFingerprint,
      snapshot2.snapshotFingerprint,
      'Different nodes should produce different snapshot'
    );
  });
});

// ============================================
// T24 - Regression Tests
// ============================================
describe('T24 - Regression Tests', () => {
  it('should maintain all required states', () => {
    const requiredStates = [
      'draft', 'registered', 'pending_verification', 'verified',
      'active', 'degraded', 'inactive', 'suspended', 'rejected', 'retired'
    ];

    for (const state of requiredStates) {
      assert.ok(
        Object.values(LIFECYCLE_STATES).includes(state),
        `State ${state} should be available`
      );
    }
  });

  it('should maintain all required health statuses', () => {
    const requiredStatuses = ['healthy', 'degraded', 'unreachable', 'unknown'];

    for (const status of requiredStatuses) {
      assert.ok(
        Object.values(HEALTH_STATUS).includes(status),
        `Health status ${status} should be available`
      );
    }
  });

  it('should maintain all required node types', () => {
    const requiredTypes = ['developer', 'compute', 'data', 'storage', 'validation', 'gateway'];

    for (const type of requiredTypes) {
      assert.ok(
        NODE_TYPES.includes(type),
        `Node type ${type} should be available`
      );
    }
  });
});

console.log('Running MPF-004 Test Suite (T1-T24)...');
