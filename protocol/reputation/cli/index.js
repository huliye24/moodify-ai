#!/usr/bin/env node

/**
 * MOOD Protocol Reputation CLI
 *
 * Command-line interface for reputation operations
 */

import { Command } from 'commander';
import { program } from 'commander';
import { createProfile } from '../core/profile.js';
import { aggregateReputation } from '../core/aggregator.js';
import { generateSnapshot, getSnapshot, validateSnapshot, getParticipantSnapshots, getEpochSnapshots } from '../core/snapshot.js';
import { getProfile } from '../core/profile.js';
import { generateProtocolId, parseIdentityProof } from '../core/identity.js';
import { readFileSync, existsSync, writeFileSync } from 'fs';
import { join } from 'path';
import chalk from 'chalk';

// Initialize commander
const cli = new Command();

// Color scheme
const colors = {
  success: chalk.green,
  error: chalk.red,
  warning: chalk.yellow,
  info: chalk.blue,
  dim: chalk.gray,
  bright: chalk.bold
};

// Helper functions
function success(message) {
  console.log(colors.success(`✓ ${message}`));
}

function error(message) {
  console.error(colors.error(`✗ ${message}`));
}

function info(message) {
  console.log(colors.info(`ℹ ${message}`));
}

function warning(message) {
  console.log(colors.warning(`⚠ ${message}`));
}

function dim(message) {
  console.log(colors.dim(`• ${message}`));
}

function displayProfile(profile) {
  console.log(colors.bright('\n=== Profile Information ==='));
  console.log(colors.info('Protocol ID:'), profile.protocolId);
  console.log(colors.info('Created:'), profile.createdAt);
  console.log(colors.info('Last Updated:'), profile.lastUpdated);
  console.log(colors.info('Total Contributions:'), profile.totalContributions);

  if (profile.epochs && profile.epochs.length > 0) {
    console.log(colors.info('Epochs Participated:'), profile.epochs.length);
  }

  if (profile.metadata && profile.metadata.achievements && profile.metadata.achievements.length > 0) {
    console.log(colors.info('Achievements:'));
    profile.metadata.achievements.forEach(achievement => {
      console.log(`  - ${achievement.name} (${achievement.earnedAt})`);
    });
  }
}

function displaySnapshot(snapshot) {
  console.log(colors.bright('\n=== Reputation Snapshot ==='));
  console.log(colors.info('Snapshot ID:'), snapshot.snapshotId);
  console.log(colors.info('Epoch ID:'), snapshot.epochId);
  console.log(colors.info('Policy Version:'), snapshot.policyVersion);
  console.log(colors.info('Generated At:'), snapshot.generatedAt);

  if (snapshot.confidence) {
    const confidenceColor = snapshot.confidence === 'certainty' ? colors.success :
                          snapshot.confidence === 'high' ? colors.info :
                          snapshot.confidence === 'medium' ? colors.warning :
                          colors.error;
    console.log(confidenceColor('Confidence:'), snapshot.confidence.toUpperCase());
  }

  if (snapshot.aggregate && snapshot.aggregate.score) {
    const scoreColor = snapshot.aggregate.score >= 80 ? colors.success :
                      snapshot.aggregate.score >= 60 ? colors.info :
                      snapshot.aggregate.score >= 40 ? colors.warning :
                      colors.error;
    console.log(scoreColor('Aggregate Score:'), snapshot.aggregate.score);
  }

  console.log(colors.info('Dimensions:'));
  Object.entries(snapshot.dimensions).forEach(([dimension, score]) => {
    const scoreStr = score === null ? 'N/A' : `${score}`;
    const scoreColor = score === null ? colors.dim :
                      score >= 80 ? colors.success :
                      score >= 60 ? colors.info :
                      score >= 40 ? colors.warning :
                      colors.error;
    console.log(`  ${dimension}:`, scoreColor(scoreStr));
  });

  if (snapshot.verifiedContributionCount > 0) {
    console.log(colors.info('Verified Contributions:'), snapshot.verifiedContributionCount);
  }

  if (snapshot.categoryDiversity && snapshot.categoryDiversity.length > 0) {
    console.log(colors.info('Categories:'), snapshot.categoryDiversity.join(', '));
  }
}

// CLI Commands
cli
  .name('mood-reputation')
  .description('MOOD Protocol Reputation CLI')
  .version('1.0.0');

// Create profile command
cli
  .command('create-profile')
  .description('Create a new reputation profile')
  .option('-i, --identity <identity>', 'Identity proof (required)', '')
  .option('-c, --contributions <contributions>', 'Comma-separated contribution IDs', '')
  .option('-t, --tag <tag>', 'Category tag', '')
  .option('--dry-run', 'Show what would be created without actually creating')
  .action(async (options) => {
    try {
      if (!options.identity) {
        error('Identity proof is required');
        process.exit(1);
      }

      // Parse identity proof
      const parsed = parseIdentityProof(options.identity);
      info(`Parsed identity: ${parsed.type} (${normalized identity})`);

      // Parse contribution IDs
      const contributionIds = options.contributions ? options.contributions.split(',').map(s => s.trim()) : [];

      // Metadata
      const metadata = {
        categoryTags: options.tag ? [options.tag] : []
      };

      if (options.dryRun) {
        info('Dry run mode - not creating profile');
        console.log(colors.bright('\n=== Profile to be created ==='));
        console.log('Identity:', options.identity);
        console.log('Contributions:', contributionIds);
        console.log('Tags:', metadata.categoryTags);

        // Show what the protocol ID would be
        const protocolId = generateProtocolId(options.identity);
        console.log(colors.info('Protocol ID (would be):'), protocolId);
        process.exit(0);
      }

      // Create profile
      info('Creating profile...');
      const profile = await createProfile({
        identityProof: options.identity,
        contributionIds,
        metadata
      });

      success('Profile created successfully');
      displayProfile(profile);
    } catch (error) {
      error(`Failed to create profile: ${error.message}`);
      process.exit(1);
    }
  });

// Aggregate reputation command
cli
  .command('aggregate')
  .description('Calculate reputation for a participant')
  .argument('<protocol-id>', 'Participant protocol ID')
  .option('-e, --epoch <epoch>', 'Specific epoch to aggregate')
  .option('-m, --method <method>', 'Aggregation method', 'weighted-average')
  .option('-w, --weights <weights>', 'JSON string of dimension weights')
  .option('--dry-run', 'Show what would be calculated without actually aggregating')
  .action(async (protocolId, options) => {
    try {
      // Parse weights if provided
      let weights;
      if (options.weights) {
        try {
          weights = JSON.parse(options.weights);
        } catch (error) {
          error('Invalid weights JSON');
          process.exit(1);
        }
      }

      info(`Aggregating reputation for ${protocolId}`);

      if (options.dryRun) {
        info('Dry run mode - not aggregating');
        const profile = getProfile(protocolId);
        if (profile) {
          console.log(colors.bright('\n=== Profile information ==='));
          console.log(colors.info('Protocol ID:'), protocolId);
          console.log(colors.info('Total Contributions:'), profile.totalContributions);
          console.log(colors.info('Epochs:'), profile.epochs.length);
        } else {
          console.log(colors.warning('Profile not found'));
        }
        process.exit(0);
      }

      const reputation = await aggregateReputation(protocolId, [], {
        method: options.method,
        weights,
        epochId: options.epoch
      });

      success('Reputation calculated successfully');

      console.log(colors.bright('\n=== Reputation Summary ==='));
      console.log(colors.info('Protocol ID:'), reputation.protocolId);
      console.log(colors.info('Epoch ID:'), reputation.epochId);
      console.log(colors.info('Confidence:'), reputation.confidence.toUpperCase());

      if (reputation.aggregate) {
        console.log(colors.info('Aggregate Score:'), reputation.aggregate.score);
        console.log(colors.info('Method:'), reputation.aggregate.method);
      }

      console.log(colors.info('Dimensions:'));
      Object.entries(reputation.dimensions).forEach(([dimension, score]) => {
        const scoreStr = score === null ? 'N/A' : `${score}`;
        const scoreColor = score === null ? colors.dim :
                          score >= 80 ? colors.success :
                          score >= 60 ? colors.info :
                          score >= 40 ? colors.warning :
                          colors.error;
        console.log(`  ${dimension}:`, scoreColor(scoreStr));
      });

      console.log(colors.info('Verified Contributions:'), reputation.verifiedContributionCount);
      console.log(colors.info('Categories:'), reputation.categoryDiversity.join(', ') || 'None');

    } catch (error) {
      error(`Failed to aggregate reputation: ${error.message}`);
      process.exit(1);
    }
  });

// Generate snapshot command
cli
  .command('generate-snapshot')
  .description('Generate a reputation snapshot')
  .argument('<protocol-id>', 'Participant protocol ID')
  .argument('<epoch-id>', 'Epoch ID')
  .argument('<policy-version>', 'Policy version')
  .option('-c, --contributions <contributions>', 'Comma-separated contribution IDs')
  .option('-m, --method <method>', 'Aggregation method', 'weighted-average')
  .option('-w, --weights <weights>', 'JSON string of dimension weights')
  .option('--dry-run', 'Show what would be created without actually creating')
  .action(async (protocolId, epochId, policyVersion, options) => {
    try {
      // Parse input contribution IDs
      const inputContributionIds = options.contributions ? options.contributions.split(',').map(s => s.trim()) : [];

      // Parse weights if provided
      let weights;
      if (options.weights) {
        try {
          weights = JSON.parse(options.weights);
        } catch (error) {
          error('Invalid weights JSON');
          process.exit(1);
        }
      }

      info(`Generating snapshot for ${protocolId} in epoch ${epochId}`);

      if (options.dryRun) {
        info('Dry run mode - not generating snapshot');
        const profile = getProfile(protocolId);
        if (profile) {
          console.log(colors.bright('\n=== Profile information ==='));
          console.log(colors.info('Protocol ID:'), protocolId);
          console.log(colors.info('Epoch ID:'), epochId);
          console.log(colors.info('Policy Version:'), policyVersion);
          console.log(colors.info('Input Contributions:'), inputContributionIds.length);
        } else {
          console.log(colors.warning('Profile not found'));
        }
        process.exit(0);
      }

      const snapshot = await generateSnapshot({
        protocolId,
        epochId,
        policyVersion,
        inputContributionIds,
        method: options.method,
        weights
      });

      success('Snapshot generated successfully');
      displaySnapshot(snapshot);

    } catch (error) {
      error(`Failed to generate snapshot: ${error.message}`);
      process.exit(1);
    }
  });

// Get snapshot command
cli
  .command('get-snapshot')
  .description('Get a snapshot by ID')
  .argument('<snapshot-id>', 'Snapshot ID')
  .option('--validate', 'Validate snapshot integrity')
  .action((snapshotId, options) => {
    try {
      const snapshot = getSnapshot(snapshotId);
      if (!snapshot) {
        error(`Snapshot not found: ${snapshotId}`);
        process.exit(1);
      }

      success('Snapshot retrieved successfully');
      displaySnapshot(snapshot);

      if (options.validate) {
        info('Validating snapshot integrity...');
        const isValid = validateSnapshot(snapshot);
        if (isValid) {
          success('Snapshot integrity validated');
        } else {
          error('Snapshot integrity validation failed');
          process.exit(1);
        }
      }

    } catch (error) {
      error(`Failed to get snapshot: ${error.message}`);
      process.exit(1);
    }
  });

// List snapshots command
cli
  .command('list-snapshots')
  .description('List snapshots')
  .option('-p, --protocol <protocol>', 'Filter by protocol ID')
  .option('-e, --epoch <epoch>', 'Filter by epoch ID')
  .action((options) => {
    try {
      let snapshots = [];

      if (options.protocol) {
        snapshots = getParticipantSnapshots(options.protocol);
        info(`Found ${snapshots.length} snapshots for ${options.protocol}`);
      } else if (options.epoch) {
        snapshots = getEpochSnapshots(options.epoch);
        info(`Found ${snapshots.length} snapshots for epoch ${options.epoch}`);
      } else {
        // Load all snapshots
        const allSnapshots = require('../core/snapshot.js').loadSnapshots();
        snapshots = Object.values(allSnapshots);
        info(`Found ${snapshots.length} total snapshots`);
      }

      if (snapshots.length === 0) {
        warning('No snapshots found');
        process.exit(0);
      }

      console.log(colors.bright(`\n=== ${snapshots.length} Snapshots ===`));
      snapshots.forEach(snapshot => {
        const statusColor = validateSnapshot(snapshot) ? colors.success : colors.error;
        console.log(`${colors.info(snapshot.snapshotId)} ${statusColor('(' + (validateSnapshot(snapshot) ? 'Valid' : 'Invalid') + ')')}`);
        console.log(`  ${colors.dim('Protocol:')} ${snapshot.protocolId}`);
        console.log(`  ${colors.dim('Epoch:')} ${snapshot.epochId}`);
        console.log(`  ${colors.dim('Score:')} ${snapshot.aggregate?.score || 'N/A'}`);
        console.log(`  ${colors.dim('Generated:')} ${new Date(snapshot.generatedAt).toLocaleString()}`);
        console.log();
      });

    } catch (error) {
      error(`Failed to list snapshots: ${error.message}`);
      process.exit(1);
    }
  });

// Show profile command
cli
  .command('show-profile')
  .description('Show profile information')
  .argument('<protocol-id>', 'Participant protocol ID')
  .action((protocolId) => {
    try {
      const profile = getProfile(protocolId);
      if (!profile) {
        error(`Profile not found: ${protocolId}`);
        process.exit(1);
      }

      success('Profile retrieved successfully');
      displayProfile(profile);

    } catch (error) {
      error(`Failed to get profile: ${error.message}`);
      process.exit(1);
    }
  });

// Validate profile command
cli
  .command('validate-profile')
  .description('Validate profile integrity')
  .argument('<protocol-id>', 'Participant protocol ID')
  .action((protocolId) => {
    try {
      const profile = getProfile(protocolId);
      if (!profile) {
        error(`Profile not found: ${protocolId}`);
        process.exit(1);
      }

      const isValid = validateProfile(profile);
      if (isValid) {
        success('Profile integrity validated');
      } else {
        error('Profile integrity validation failed');
        process.exit(1);
      }

    } catch (error) {
      error(`Failed to validate profile: ${error.message}`);
      process.exit(1);
    }
  });

// Info command
cli
  .command('info')
  .description('Show reputation system information')
  .action(() => {
    try {
      info('MOOD Protocol Reputation System');
      console.log(colors.bright('Version:'), '1.0.0');
      console.log(colors.bright('Dimensions:'), 'contribution, impact, quality, persistence, early');
      console.log(colors.bright('Aggregation Methods:'), 'weighted-average, median, maximum');
      console.log(colors.bright('Schema Version:'), '1.0.0');
      console.log(colors.bright('Confidence Levels:'), 'insufficient, low, medium, high, certainty');

      // Check data directories
      const dataDirs = [
        './data/reputation',
        './data/snapshots',
        './data/identity'
      ];

      console.log(colors.bright('\nData Directories:'));
      dataDirs.forEach(dir => {
        const exists = existsSync(dir);
        const status = exists ? colors.success('Exists') : colors.error('Missing');
        console.log(`  ${dir}: ${status}`);
      });

    } catch (error) {
      error(`Failed to get system info: ${error.message}`);
      process.exit(1);
    }
  });

// Export functions for testing
export {
  cli,
  colors,
  success,
  error,
  info,
  warning,
  dim,
  displayProfile,
  displaySnapshot
};

// Run CLI if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  cli.parse();
}