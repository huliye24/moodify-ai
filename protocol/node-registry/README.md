# MOOD Protocol Node Registry

## Overview

The Node Registry (MPF-004) provides an auditable registry of independent MOOD Protocol nodes. It answers:

> Which independent nodes exist, who operates them, what resources do they claim to provide, where are they logically located, what can they do, and are they currently verifiably available?

## Architecture

```
protocol/node-registry/
├── core/                    # Core modules
│   ├── node-identity.js    # Stable node ID generation
│   ├── lifecycle.js        # Node lifecycle state machine
│   ├── capability.js       # Capability manifest management
│   ├── verification.js     # Challenge and verification
│   ├── health.js          # Heartbeat and health evaluation
│   ├── registry.js        # Node registration core
│   └── discovery.js       # Read-only discovery API
├── adapters/
│   └── filesystem.js       # Offline filesystem storage
├── tests/
│   └── node-registry.test.js  # T1-T24 test suite
├── fixtures/               # 16 test fixtures
└── README.md
```

## Node Types

- `developer` - Human/developer contribution interface
- `compute` - CPU/GPU/inference/processing resource
- `data` - Data or metadata resource provider
- `storage` - Object/blob/archive resource
- `validation` - Independent verification/benchmark resource
- `gateway` - Public connectivity or protocol gateway

## Lifecycle States

```
draft → registered → pending_verification → verified → active
                                                      ↓
                              degraded ← inactive ← suspended
                                   ↓
                                rejected / retired
```

## Key Features

### Stable Node Identity
Node IDs are independent of infrastructure location. Changing IP/endpoint does not change the node ID.

### Capability Separation
Node endpoint verification is separate from capability verification. A verified node can have unverified GPU claims.

### Health ≠ Reputation
Health observations are separate from node reputation. A temporarily offline node does not lose reputation.

### Privacy by Design
- Location precision levels: country, region, city, exact, hidden
- Capacity classes instead of exact values
- No private IPs, credentials, or sensitive infrastructure details

### SSRF Protection
Endpoint verification rejects:
- localhost, 127.0.0.1, ::1
- Private IP ranges (10.x, 172.16-31.x, 192.168.x)
- Internal hostnames (.local, .internal)

## Usage

### Create a Node

```javascript
import { createNode, registerNode } from './core/registry.js';

const node = createNode({
  operatorProtocolId: 'mood:contributor:...',
  nodeType: 'compute',
  displayName: 'Singapore Compute Node',
  region: { countryCode: 'SG', precision: 'country' },
  endpoint: { type: 'https', uri: 'https://node.example.com' }
});
```

### Manage Lifecycle

```javascript
import { registerNode, submitForVerification, completeVerification, activateNode } from './core/registry.js';

let node = createNode({...});
node = registerNode(node);
node = submitForVerification(node);
node = completeVerification(node, true);
node = activateNode(node);
```

### Health Observation

```javascript
import { createHeartbeat, evaluateStaleTransition } from './core/health.js';

const heartbeat = createHeartbeat({
  nodeId: 'mood:node:...',
  status: 'healthy',
  source: 'registry-probe'
});
```

### Discovery

```javascript
import { discoverNodes, generateRegistrySnapshot } from './core/discovery.js';

const activeNodes = discoverNodes(allNodes, {
  lifecycleStatus: 'active',
  nodeType: 'compute'
});

const snapshot = generateRegistrySnapshot(activeNodes, '004-draft-1');
```

## Economic Boundaries

MPF-004 does NOT implement:
- GPU marketplace
- Token rewards
- Automatic job scheduling
- Remote shell access
- Cloud control plane
- Staking system
- Payment rail
- DAO
- Contract deployment

## Security Boundaries

Allowed:
- Public registration data
- Public node IDs
- Public HTTPS endpoint verification
- Capability declarations
- Read-only health probes
- Local fixtures

Forbidden:
- SSH private keys
- Remote shell execution
- Cloud account credentials
- Token transfers
- Treasury movement

---

*MPF-004 Status: COMPLETED*
