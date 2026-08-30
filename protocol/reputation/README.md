# MOOD Protocol Reputation Core

The Reputation Core module implements the reputation system for the MOOD Protocol. It provides a robust, verifiable system for tracking and aggregating participant contributions across the protocol.

## Overview

The Reputation Core implements:

- **Identity Management**: Verifiable identity linking and proof
- **Profile Management**: Comprehensive participant profiles with achievement tracking
- **Contribution Aggregation**: Multi-dimensional reputation scoring with various aggregation methods
- **Immutable Snapshots**: Cryptographically verified snapshots of reputation state
- **Third-Party Attestations**: External verification and attestation system

## Architecture

### Core Components

```
protocol/reputation/
├── core/                 # Core logic modules
│   ├── identity.js      # Identity management and fingerprinting
│   ├── profile.js       # Profile creation and management
│   ├── aggregator.js    # Reputation aggregation engine
│   ├── snapshot.js      # Snapshot generation and validation
│   └── attestation.js   # Third-party attestation handling
├── schema/              # JSON Schema definitions
│   ├── reputation-profile.schema.json
│   ├── reputation-snapshot.schema.json
│   ├── reputation-attestation.schema.json
│   └── reputation-evidence.schema.json
├── cli/                 # Command-line interface
│   ├── index.js         # Main CLI entry point
│   ├── package.json     # Dependencies
│   ├── test.js          # Tests
│   └── package.json
└── README.md           # This file
```

## Key Concepts

### Identity System

The reputation system uses SHA-256 fingerprinting for identity verification:

- **Protocol ID**: `mood:contributor:<sha256-fingerprint>`
- **Identity Proofs**: Support for multiple identity types (email, Ethereum, GitHub, Discord)
- **Identity Linking**: Link multiple proofs to a single participant
- **Conflict Resolution**: Mechanisms for resolving identity disputes

### Reputation Dimensions

The system evaluates participants across 5 dimensions:

1. **Contribution**: Volume and frequency of contributions
2. **Impact**: Quality and reach of contributions
3. **Quality**: Technical excellence and execution
4. **Persistence**: Long-term engagement and consistency
5. **Early**: Early adoption and pioneering contributions

### Aggregation Methods

Multiple aggregation methods are supported:

- **Weighted Average**: Default method with configurable dimension weights
- **Median**: Robust against outliers
- **Maximum**: Highlights strongest performance

## Usage

### Installation

```bash
cd protocol/reputation
npm install
```

### CLI Usage

The CLI provides comprehensive reputation operations:

#### Create a Profile

```bash
# Create a new profile
mood-reputation create-profile -i "test@example.com" -t "developer"

# Create with initial contributions
mood-reputation create-profile -i "0x1234567890abc...def" -c "mood-contrib-001,mood-contrib-002"

# Dry run
mood-reputation create-profile -i "github:huliye24" --dry-run
```

#### Manage Profiles

```bash
# Show profile information
mood-reputation show-profile mood:contributor:abcdef...

# Validate profile integrity
mood-reputation validate-profile mood:contributor:abcdef...
```

#### Calculate Reputation

```bash
# Aggregate reputation
mood-reputation aggregate mood:contributor:abcdef...

# Aggregate specific epoch
mood-reputation aggregate mood:contributor:abcdef -e epoch-001

# Use custom weights
mood-reputation aggregate mood:contributor:abcdef -w '{"contribution": 0.4, "impact": 0.3}'
```

#### Generate Snapshots

```bash
# Generate a snapshot
mood-reputation generate-snapshot mood:contributor:abcdef epoch-001 v1.0.0

# Generate with custom contributions
mood-reputation generate-snapshot mood:contributor:abcdef epoch-001 v1.0.0 -c "mood-contrib-001,mood-contrib-002"

# Generate with aggregation method
mood-reputation generate-snapshot mood:contributor:abcdef epoch-001 v1.0.0 -m median
```

#### Manage Snapshots

```bash
# Get snapshot by ID
mood-reputation get-snapshot mood-reputation-2024-08-29-123456

# Validate snapshot integrity
mood-reputation get-snapshot mood-reputation-2024-08-29-123456 --validate

# List all snapshots
mood-reputation list-snapshots

# List snapshots for a participant
mood-reputation list-snapshots -p mood:contributor:abcdef...

# List snapshots for an epoch
mood-reputation list-snapshots -e epoch-001
```

#### System Information

```bash
# Show system information
mood-reputation info
```

### Programmatic Usage

#### Identity Management

```javascript
import { generateProtocolId, parseIdentityProof } from './core/identity.js';

// Generate protocol ID
const protocolId = generateProtocolId('test@example.com');
console.log(protocolId); // "mood:contributor:a1b2c3..."

// Parse identity proof
const parsed = parseIdentityProof('github:huliye24');
console.log(parsed); // { type: 'github', username: 'huliye24' }
```

#### Profile Management

```javascript
import { createProfile, getProfile, updateProfile } from './core/profile.js';

// Create profile
const profile = await createProfile({
  identityProof: 'test@example.com',
  contributionIds: ['mood-contrib-001'],
  metadata: { tags: ['developer'] }
});

// Get profile
const existingProfile = getProfile('mood:contributor:a1b2c3...');

// Update profile
const updatedProfile = await updateProfile('mood:contributor:a1b2c3...', ['mood-contrib-002']);
```

#### Reputation Aggregation

```javascript
import { aggregateReputation, batchAggregate } from './core/aggregator.js';

// Aggregate individual reputation
const reputation = await aggregateReputation('mood:contributor:a1b2c3...', [], {
  method: 'weighted-average',
  weights: { contribution: 0.4, impact: 0.3 }
});

// Batch aggregate multiple participants
const batchResults = await batchAggregate([
  'mood:contributor:a1b2c3...',
  'mood:contributor:d4e5f6...'
]);
```

#### Snapshot Generation

```javascript
import { generateSnapshot, validateSnapshot } from './core/snapshot.js';

// Generate snapshot
const snapshot = await generateSnapshot({
  protocolId: 'mood:contributor:a1b2c3...',
  epochId: 'epoch-001',
  policyVersion: 'v1.0.0',
  inputContributionIds: ['mood-contrib-001']
});

// Validate snapshot
const isValid = validateSnapshot(snapshot);
```

## Configuration

### Default Dimension Weights

```javascript
const DEFAULT_WEIGHTS = {
  contribution: 0.30,  // 30%
  impact: 0.25,      // 25%
  quality: 0.20,      // 20%
  persistence: 0.15,  // 15%
  early: 0.10         // 10%
};
```

### Confidence Levels

- **Insufficient**: Not enough data
- **Low**: Limited reliability
- **Medium**: Moderate reliability
- **High**: High reliability
- **Certainty**: Maximum confidence

## Security Features

### Fingerprinting

All critical operations use SHA-256 fingerprinting:

- Identity fingerprints
- Snapshot fingerprints
- Content integrity verification

### Immutability

Snapshots are cryptographically verifiable and tamper-proof:

- SHA-256 fingerprints for integrity
- Provenance tracking
- Version control

### Access Control

- Protocol ID format validation
- Identity proof verification
- Snapshot access control

## Integration with MOOD Protocol

### MPF-002 Contribution Integration

The Reputation Core integrates with the Contribution Module (MPF-002):

```javascript
import { consumeContributions } from './core/aggregator.js';

// Process MPF-002 contributions
const results = await consumeContributions({
  contributions: [
    {
      id: 'mood-contrib-001',
      contributorId: 'contributor@example.com',
      contributionData: { ... }
    }
  ]
});
```

### Third-Party Attestations

Future integration with the Attestation Module (MPF-004) will provide:

- External verification
- Community attestations
- Trust network integration

## Testing

```bash
# Run CLI tests
npm test

# Run specific test
node cli/test.js
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure backward compatibility

## License

Apache-2.0

## Support

For support and questions:

- GitHub Issues
- Community Forum
- Documentation Updates