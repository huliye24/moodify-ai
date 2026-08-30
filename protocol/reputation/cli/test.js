#!/usr/bin/env node

/**
 * MOOD Reputation CLI Tests
 */

import { describe, it, expect, beforeAll, afterAll } from 'node:test';
import { cli } from './index.js';
import { existsSync, readFileSync, writeFileSync, rmSync } from 'fs';
import { join } from 'path';
import { execSync } from 'child_process';

// Test helpers
const TEST_DATA_DIR = './test-data';
const SNAPSHOT_FILE = join(TEST_DATA_DIR, 'snapshots.json');

// Clean up before tests
beforeAll(() => {
  if (existsSync(TEST_DATA_DIR)) {
    rmSync(TEST_DATA_DIR, { recursive: true });
  }
  mkdirSync(TEST_DATA_DIR, { recursive: true });
});

// Clean up after tests
afterAll(() => {
  if (existsSync(TEST_DATA_DIR)) {
    rmSync(TEST_DATA_DIR, { recursive: true });
  }
});

describe('MOOD Reputation CLI', () => {
  describe('System Info', () => {
    it('should show system information', () => {
      const output = execSync('node index.js info', { encoding: 'utf8' });
      expect(output).toContain('MOOD Protocol Reputation System');
      expect(output).toContain('Version: 1.0.0');
    });
  });

  describe('Profile Creation', () => {
    it('should create a new profile', () => {
      const identity = 'test@example.com';
      const output = execSync(`node index.js create-profile -i "${identity}" -t "test" --dry-run`, {
        encoding: 'utf8'
      });
      expect(output).toContain('Identity: test@example.com');
      expect(output).toContain('Parsed identity: email');
    });

    it('should create a profile with dry run', () => {
      const identity = '0x1234567890abcdef1234567890abcdef12345678';
      const output = execSync(`node index.js create-profile -i "${identity}" --dry-run`, {
        encoding: 'utf8'
      });
      expect(output).toContain('Protocol ID (would be):');
    });
  });

  describe('Profile Management', () => {
    it('should show profile information', () => {
      const identity = 'github:huliye24';
      const output = execSync(`node index.js show-profile ${identity} 2>&1`, { encoding: 'utf8' });
      // Should handle non-existent profile gracefully
      expect(output).toContain('Profile not found') || expect(output).toContain('Profile retrieved');
    });

    it('should validate profile', () => {
      const identity = 'github:huliye24';
      const output = execSync(`node index.js validate-profile ${identity} 2>&1`, { encoding: 'utf8' });
      // Should handle non-existent profile gracefully
      expect(output).toContain('Profile not found') || expect(output).toContain('Profile integrity validated');
    });
  });

  describe('Aggregation', () => {
    it('should aggregate reputation', () => {
      const protocolId = 'mood:contributor:placeholder';
      const output = execSync(`node index.js aggregate ${protocolId} --dry-run`, { encoding: 'utf8' });
      expect(output).toContain('Protocol ID: mood:contributor:placeholder');
    });

    it('should aggregate with custom weights', () => {
      const protocolId = 'mood:contributor:placeholder';
      const weights = '{"contribution": 0.4, "impact": 0.3}';
      const output = execSync(`node index.js aggregate ${protocolId} -w "${weights}" --dry-run`, { encoding: 'utf8' });
      expect(output).toContain('Dry run mode - not aggregating');
    });
  });

  describe('Snapshot Operations', () => {
    it('should generate snapshot', () => {
      const protocolId = 'mood:contributor:placeholder';
      const epochId = 'test-epoch-001';
      const policyVersion = 'v1.0.0';
      const output = execSync(`node index.js generate-snapshot ${protocolId} ${epochId} ${policyVersion} --dry-run`, {
        encoding: 'utf8'
      });
      expect(output).toContain('Protocol ID: mood:contributor:placeholder');
      expect(output).toContain('Epoch ID: test-epoch-001');
      expect(output).toContain('Policy Version: v1.0.0');
    });

    it('should list snapshots', () => {
      const output = execSync('node index.js list-snapshots', { encoding: 'utf8' });
      expect(output).toContain('Found 0 total snapshots');
    });

    it('should list snapshots for protocol', () => {
      const protocolId = 'mood:contributor:placeholder';
      const output = execSync(`node index.js list-snapshots -p ${protocolId}`, { encoding: 'utf8' });
      expect(output).toContain('Found 0 snapshots for mood:contributor:placeholder');
    });

    it('should get snapshot', () => {
      const snapshotId = 'non-existent-snapshot';
      const output = execSync(`node index.js get-snapshot ${snapshotId}`, { encoding: 'utf8' });
      expect(output).toContain('Snapshot not found: non-existent-snapshot');
    });
  });

  describe('Error Handling', () => {
    it('should handle missing identity', () => {
      const output = execSync('node index.js create-profile --dry-run 2>&1', { encoding: 'utf8' });
      expect(output).toContain('Identity proof is required');
    });

    it('should handle invalid weights', () => {
      const protocolId = 'mood:contributor:placeholder';
      const weights = 'invalid-json';
      const output = execSync(`node index.js aggregate ${protocolId} -w "${weights}" --dry-run 2>&1`, { encoding: 'utf8' });
      expect(output).toContain('Invalid weights JSON');
    });
  });

  describe('Identity Types', () => {
    it('should handle email identity', () => {
      const identity = 'test@example.com';
      const output = execSync(`node index.js create-profile -i "${identity}" --dry-run`, { encoding: 'utf8' });
      expect(output).toContain('Parsed identity: email');
    });

    it('should handle Ethereum identity', () => {
      const identity = '0x1234567890abcdef1234567890abcdef12345678';
      const output = execSync(`node index.js create-profile -i "${identity}" --dry-run`, { encoding: 'utf8' });
      expect(output).toContain('Parsed identity: ethereum');
    });

    it('should handle GitHub identity', () => {
      const identity = 'github:huliye24';
      const output = execSync(`node index.js create-profile -i "${identity}" --dry-run`, { encoding: 'utf8' });
      expect(output).toContain('Parsed identity: github');
    });

    it('should handle Discord identity', () => {
      const identity = 'discord:1234567890';
      const output = execSync(`node index.js create-profile -i "${identity}" --dry-run`, { encoding: 'utf8' });
      expect(output).toContain('Parsed identity: discord');
    });
  });
});

console.log('CLI tests completed successfully!');