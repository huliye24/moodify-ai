#!/usr/bin/env node

/**
 * MOOD Protocol Mainnet Lock Generator
 *
 * Generates a lock file for mainnet configuration.
 * Usage: node scripts/generate-mainnet-lock.mjs protocol/mainnet.json protocol/mainnet.lock.json
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createHash } from 'crypto';

// Get current file directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load utilities
const schemaPath = path.join(__dirname, '..', 'protocol', 'mainnet.schema.json');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

// Load config
const configPath = process.argv[2] || path.join(__dirname, '..', 'protocol', 'mainnet.json');
const lockPath = process.argv[3] || path.join(__dirname, '..', 'protocol', 'mainnet.lock.json');

// Load configuration
let config;
try {
  config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
} catch (error) {
  console.error(`❌ Failed to read config: ${error.message}`);
  process.exit(1);
}

// Check if config is locked
if (config.launch.status !== 'locked') {
  console.error('❌ Cannot generate lock for non-locked configuration');
  console.error('   Set config.launch.status = "locked" first');
  process.exit(1);
}

// Create lock file structure
function createLockFile(config) {
  // Compute SHA-256 hash of config file
  const configContent = fs.readFileSync(configPath, 'utf8');
  const configHash = createHash('sha256').update(configContent).digest('hex');

  // Create lock object
  const lock = {
    // Metadata
    version: '1.0.0',
    generatedAt: new Date().toISOString(),
    generator: 'MOOD Protocol Lock Generator',

    // Lock integrity
    integrity: {
      configHash,
      configPath: path.relative(process.cwd(), configPath),
      configSize: configContent.length,
    },

    // Fact snapshot
    facts: {
      // Protocol identity (immutable)
      protocol: {
        name: config.protocol.name,
        ticker: config.protocol.ticker,
      },

      // Chain identity (immutable)
      chain: {
        family: config.chain.family,
        network: config.chain.network,
        chainId: config.chain.chainId,
        cluster: config.chain.cluster,
      },

      // Token identity (immutable after deployment)
      token: {
        name: config.token.name,
        symbol: config.token.symbol,
        identifier: config.token.identifier,
        decimals: config.token.decimals,
        totalSupplyAtomic: config.token.totalSupplyAtomic,
      },

      // Addresses (may change)
      addresses: {
        treasury: config.addresses.treasury,
        genesisPool: config.addresses.genesisPool,
      },

      // Endpoints (may change)
      endpoints: {
        rpcUrls: [...config.endpoints.rpcUrls],
        explorerBaseUrl: config.endpoints.explorerBaseUrl,
      },
    },

    // Evidence snapshot
    evidence: {
      sourceCommit: config.evidence.sourceCommit,
      references: [...config.evidence.references],
      unresolved: [...config.evidence.unresolved],
    },

    // Lock metadata
    lock: {
      status: config.launch.status,
      lockedAt: config.launch.lockedAt,
      lockedBy: config.launch.lockedBy,
    },

    // Fact identifiers for verification
    identifiers: {
      // Token contract identifier
      tokenContract: config.token.identifier,

      // Chain identifier
      chainId: config.chain.chainId,

      // Hash of immutable facts
      immutableFactsHash: createHash('sha256')
        .update(JSON.stringify({
          protocol: config.protocol,
          chain: config.chain,
          token: {
            name: config.token.name,
            symbol: config.token.symbol,
            decimals: config.token.decimals,
            totalSupplyAtomic: config.token.totalSupplyAtomic,
          },
        }))
        .digest('hex'),
    },
  };

  return lock;
}

// Generate lock file
console.log('🔒 Generating MOOD Protocol Mainnet Lock...\n');

try {
  const lock = createLockFile(config);

  // Write lock file
  fs.writeFileSync(lockPath, JSON.stringify(lock, null, 2));

  console.log('✅ Lock file generated successfully!');
  console.log(`📁 Lock file: ${lockPath}\n`);

  // Print lock summary
  console.log('📋 Lock Summary:');
  console.log(`   Version: ${lock.version}`);
  console.log(`   Generated At: ${lock.generatedAt}`);
  console.log(`   Locked By: ${lock.lock.lockedBy}`);
  console.log(`   Config Hash: ${lock.integrity.configHash.substring(0, 16)}...`);
  console.log(`   Facts Hash: ${lock.identifiers.immutableFactsHash.substring(0, 16)}...\n`);

  // Print immutable facts
  console.log('🔒 Immutable Facts:');
  console.log(`   Protocol: ${lock.facts.protocol.name} (${lock.facts.protocol.ticker})`);
  console.log(`   Chain: ${lock.facts.chain.network} (ID: ${lock.facts.chain.chainId})`);
  console.log(`   Token: ${lock.facts.token.name} (${lock.facts.token.symbol})`);
  console.log(`   Supply: ${lock.facts.token.totalSupplyAtomic} atomic\n`);

  // Print unresolved facts
  if (lock.evidence.unresolved.length > 0) {
    console.log('⚠️  Unresolved Facts:');
    lock.evidence.unresolved.forEach(fact => {
      console.log(`   - ${fact}`);
    });
    console.log('');
  }

  console.log('🎉 Lock file ready for deployment!');

} catch (error) {
  console.error(`❌ Failed to generate lock: ${error.message}`);
  process.exit(1);
}

// Instructions
console.log('\n📝 Next Steps:');
console.log('1. Review the lock file for accuracy');
console.log('2. Deploy contracts if addresses are null');
console.log('3. Update addresses in mainnet.json');
console.log('4. Re-generate lock after deployment');
console.log('5. Commit both mainnet.json and mainnet.lock.json');

process.exit(0);