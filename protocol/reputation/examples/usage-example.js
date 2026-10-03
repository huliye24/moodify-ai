/**
 * MOOD Protocol Reputation Core Usage Examples
 *
 * This file demonstrates how to use the Reputation Core components
 */

import { generateProtocolId, parseIdentityProof } from '../core/identity.js';
import { createProfile, getProfile, updateProfile } from '../core/profile.js';
import { aggregateReputation, consumeContributions } from '../core/aggregator.js';
import { generateSnapshot, getSnapshot, validateSnapshot } from '../core/snapshot.js';
import { existsSync, mkdirSync } from 'fs';

// Example data directory setup
const EXAMPLE_DIR = './examples/data';
if (!existsSync(EXAMPLE_DIR)) {
  mkdirSync(EXAMPLE_DIR, { recursive: true });
}

console.log('=== MOOD Protocol Reputation Core Usage Examples ===\n');

// Example 1: Identity Management
console.log('🔐 Example 1: Identity Management');
console.log('=================================');

// Generate protocol IDs from different identity types
const emailIdentity = 'alice@example.com';
const githubIdentity = 'github:huliye24';
const ethIdentity = '0x1234567890abcdef1234567890abcdef12345678';

const emailProtocolId = generateProtocolId(emailIdentity);
const githubProtocolId = generateProtocolId(githubIdentity);
const ethProtocolId = generateProtocolId(ethIdentity);

console.log(`Email Identity: ${emailIdentity} → Protocol ID: ${emailProtocolId}`);
console.log(`GitHub Identity: ${githubIdentity} → Protocol ID: ${githubProtocolId}`);
console.log(`Ethereum Identity: ${ethIdentity} → Protocol ID: ${ethProtocolId}`);

// Parse identity proofs
console.log('\nParsed Identity Proofs:');
const parsedEmail = parseIdentityProof(emailIdentity);
const parsedGithub = parseIdentityProof(githubIdentity);
const parsedEth = parseIdentityProof(ethIdentity);

console.log('Email:', parsedEmail);
console.log('GitHub:', parsedGithub);
console.log('Ethereum:', parsedEth);

// Example 2: Profile Creation
console.log('\n📝 Example 2: Profile Creation');
console.log('=============================');

async function createExampleProfiles() {
  // Create Alice's profile
  console.log('Creating Alice\'s profile...');
  const aliceProfile = await createProfile({
    identityProof: emailIdentity,
    contributionIds: ['mood-contrib-001', 'mood-contrib-002'],
    metadata: {
      categoryTags: ['developer', 'contributor'],
      preferences: { notifications: true }
    }
  });
  console.log('✓ Alice\'s profile created:', aliceProfile.protocolId);

  // Create GitHub contributor's profile
  console.log('Creating GitHub contributor\'s profile...');
  const githubProfile = await createProfile({
    identityProof: githubIdentity,
    contributionIds: ['mood-contrib-003'],
    metadata: {
      categoryTags: ['maintainer'],
      achievements: [
        { name: 'First Contribution', description: 'Made initial contribution' }
      ]
    }
  });
  console.log('✓ GitHub contributor\'s profile created:', githubProfile.protocolId);

  return { aliceProfile, githubProfile };
}

// Example 3: Reputation Aggregation
console.log('\n📊 Example 3: Reputation Aggregation');
console.log('==================================');

async function demonstrateAggregation() {
  const { aliceProfile, githubProfile } = await createExampleProfiles();

  // Aggregate Alice's reputation
  console.log('Aggregating Alice\'s reputation...');
  const aliceReputation = await aggregateReputation(aliceProfile.protocolId, [], {
    method: 'weighted-average',
    weights: {
      contribution: 0.40,
      impact: 0.30,
      quality: 0.20,
      persistence: 0.10
    }
  });
  console.log('✓ Alice\'s reputation calculated');
  console.log('  - Aggregate Score:', aliceReputation.aggregate?.score);
  console.log('  - Confidence:', aliceReputation.confidence);
  console.log('  - Verified Contributions:', aliceReputation.verifiedContributionCount);

  // Aggregate GitHub contributor's reputation with median method
  console.log('\nAggregating GitHub contributor\'s reputation (median method)...');
  const githubReputation = await aggregateReputation(githubProfile.protocolId, [], {
    method: 'median'
  });
  console.log('✓ GitHub contributor\'s reputation calculated');
  console.log('  - Aggregate Score:', githubReputation.aggregate?.score);
  console.log('  - Confidence:', githubReputation.confidence);

  return { aliceReputation, githubReputation };
}

// Example 4: Snapshot Generation
console.log('\n📸 Example 4: Snapshot Generation');
console.log('================================');

async function demonstrateSnapshots() {
  const { aliceProfile, githubProfile } = await createExampleProfiles();
  const { aliceReputation } = await demonstrateAggregation();

  // Generate snapshot for Alice
  console.log('Generating snapshot for Alice...');
  const aliceSnapshot = await generateSnapshot({
    protocolId: aliceProfile.protocolId,
    epochId: 'example-epoch-001',
    policyVersion: 'v1.0.0',
    inputContributionIds: ['mood-contrib-001', 'mood-contrib-002'],
    method: 'weighted-average'
  });
  console.log('✓ Snapshot generated:', aliceSnapshot.snapshotId);
  console.log('  - Snapshot Fingerprint:', aliceSnapshot.snapshotFingerprint);
  console.log('  - Aggregate Score:', aliceSnapshot.aggregate?.score);
  console.log('  - Confidence:', aliceSnapshot.confidence);

  // Validate snapshot
  console.log('\nValidating snapshot...');
  const isValid = validateSnapshot(aliceSnapshot);
  console.log(`  - Valid: ${isValid}`);

  // Retrieve snapshot
  console.log('\nRetrieving snapshot...');
  const retrievedSnapshot = getSnapshot(aliceSnapshot.snapshotId);
  console.log(`  - Retrieved: ${!!retrievedSnapshot}`);

  return { aliceSnapshot };
}

// Example 5: Contribution Processing
console.log('\n🔄 Example 5: Contribution Processing');
console.log('===================================');

async function demonstrateContributionProcessing() {
  // Simulate MPF-002 contribution data
  const contributionData = {
    contributions: [
      {
        id: 'mood-contrib-001',
        contributorId: 'alice@example.com',
        contributionData: {
          category: 'code',
          impact: 75,
          quality: 85,
          timestamp: '2024-08-29T10:00:00Z'
        }
      },
      {
        id: 'mood-contrib-002',
        contributorId: 'github:huliye24',
        contributionData: {
          category: 'documentation',
          impact: 60,
          quality: 70,
          timestamp: '2024-08-29T11:00:00Z'
        }
      },
      {
        id: 'mood-contrib-003',
        contributorId: '0x1234567890abcdef1234567890abcdef12345678',
        contributionData: {
          category: 'testing',
          impact: 50,
          quality: 65,
          timestamp: '2024-08-29T12:00:00Z'
        }
      }
    ]
  };

  // Process contributions
  console.log('Processing contributions...');
  const processedResults = await consumeContributions(contributionData);

  console.log('✓ Contributions processed:');
  processedResults.forEach(result => {
    if (result.success) {
      console.log(`  - ${result.contributionId}: ${result.protocolId} (Score: ${result.reputation.aggregate?.score})`);
    } else {
      console.log(`  - ${result.contributionId}: Failed (${result.error})`);
    }
  });

  return processedResults;
}

// Example 6: Batch Operations
console.log('\n📦 Example 6: Batch Operations');
console.log('=============================');

async function demonstrateBatchOperations() {
  const protocolIds = [
    generateProtocolId('alice@example.com'),
    generateProtocolId('bob@example.com'),
    generateProtocolId('carol@example.com')
  ];

  // Batch aggregation
  console.log('Performing batch aggregation...');
  const batchResults = await aggregateReputation(protocolIds[0], [], {
    method: 'weighted-average'
  });

  console.log(`✓ Batch aggregation for ${protocolIds[0]} completed`);
  console.log('  - Score:', batchResults.aggregate?.score);
  console.log('  - Confidence:', batchResults.confidence);

  // Batch snapshot generation
  console.log('\nGenerating batch snapshots...');
  const snapshotPromises = protocolIds.slice(0, 2).map(protocolId =>
    generateSnapshot({
      protocolId,
      epochId: 'batch-epoch-001',
      policyVersion: 'v1.0.0',
      inputContributionIds: []
    })
  );

  const snapshots = await Promise.all(snapshotPromises);
  console.log(`✓ Generated ${snapshots.length} snapshots`);

  return snapshots;
}

// Run all examples
async function runAllExamples() {
  try {
    await createExampleProfiles();
    await demonstrateAggregation();
    await demonstrateSnapshots();
    await demonstrateContributionProcessing();
    await demonstrateBatchOperations();

    console.log('\n🎉 All examples completed successfully!');
  } catch (error) {
    console.error('Error running examples:', error);
  }
}

// Run the examples
runAllExamples();