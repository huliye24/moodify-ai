#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';

const file = process.argv[2] || 'protocol/mainnet.json';
const resolved = path.resolve(process.cwd(), file);

const errors = [];
const warnings = [];

function fail(message) {
  errors.push(message);
}

function warn(message) {
  warnings.push(message);
}

function isNonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

function containsPlaceholder(value) {
  if (typeof value === 'string') {
    return /HUMAN_DECISION_REQUIRED|TODO|TBD|PLACEHOLDER|example\.invalid/i.test(value);
  }
  if (Array.isArray(value)) return value.some(containsPlaceholder);
  if (value && typeof value === 'object') return Object.values(value).some(containsPlaceholder);
  return false;
}

function isHttpUrl(value) {
  try {
    const u = new URL(value);
    return u.protocol === 'http:' || u.protocol === 'https:';
  } catch {
    return false;
  }
}

function isEvmAddress(value) {
  return typeof value === 'string' && /^0x[a-fA-F0-9]{40}$/.test(value);
}

function isSolanaAddress(value) {
  // Conservative structural check only. Runtime/public-chain verification remains required.
  return typeof value === 'string' && /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(value);
}

function validateAddress(value, label, family, nullable = false) {
  if (value === null && nullable) return;
  if (!isNonEmptyString(value)) {
    fail(`${label} must be a non-empty public address${nullable ? ' or null in draft' : ''}`);
    return;
  }
  if (family === 'evm' && !isEvmAddress(value)) fail(`${label} is not a valid EVM address shape`);
  if (family === 'solana' && !isSolanaAddress(value)) fail(`${label} is not a valid Solana public-key shape`);
}

let config;
try {
  config = JSON.parse(fs.readFileSync(resolved, 'utf8'));
} catch (err) {
  console.error(`[FAIL] Cannot read/parse ${file}: ${err.message}`);
  process.exit(1);
}

for (const key of ['schemaVersion', 'protocol', 'chain', 'token', 'addresses', 'endpoints', 'evidence', 'launch']) {
  if (!(key in config)) fail(`missing top-level field: ${key}`);
}

if (!/^\d+\.\d+\.\d+$/.test(config.schemaVersion || '')) fail('schemaVersion must be semver-like x.y.z');
if (config.protocol?.ticker !== 'MOOD') fail('protocol.ticker must be MOOD');
if (config.token?.symbol !== 'MOOD') fail('token.symbol must be MOOD');

const family = config.chain?.family;
if (!['evm', 'solana', 'other'].includes(family)) fail('chain.family must be evm, solana, or other');
if (!isNonEmptyString(config.chain?.network)) fail('chain.network must be a non-empty string');

if (family === 'evm') {
  if (!Number.isInteger(config.chain?.chainId) || config.chain.chainId <= 0) fail('EVM chain.chainId must be a positive integer');
  if (config.chain?.cluster !== null) warn('EVM chain.cluster is normally null');
} else if (family === 'solana') {
  if (config.chain?.chainId !== null) fail('Solana chain.chainId must be null');
  if (!isNonEmptyString(config.chain?.cluster)) fail('Solana chain.cluster must be set');
}

validateAddress(config.token?.identifier, 'token.identifier', family, false);
validateAddress(config.addresses?.treasury, 'addresses.treasury', family, true);
validateAddress(config.addresses?.genesisPool, 'addresses.genesisPool', family, true);

if (!Number.isInteger(config.token?.decimals) || config.token.decimals < 0 || config.token.decimals > 36) {
  fail('token.decimals must be an integer from 0 to 36');
}
if (!/^[0-9]+$/.test(config.token?.totalSupplyAtomic || '')) fail('token.totalSupplyAtomic must be an unsigned decimal integer string');

const rpcUrls = config.endpoints?.rpcUrls;
if (!Array.isArray(rpcUrls)) {
  fail('endpoints.rpcUrls must be an array');
} else {
  for (const url of rpcUrls) if (!isHttpUrl(url)) fail(`invalid RPC URL: ${String(url)}`);
  if (new Set(rpcUrls).size !== rpcUrls.length) fail('endpoints.rpcUrls contains duplicate entries');
}
if (!isHttpUrl(config.endpoints?.explorerBaseUrl)) fail('endpoints.explorerBaseUrl must be an http(s) URL');

if (!Array.isArray(config.evidence?.references)) fail('evidence.references must be an array');
if (!Array.isArray(config.evidence?.unresolved)) fail('evidence.unresolved must be an array');

const status = config.launch?.status;
if (!['draft', 'locked'].includes(status)) fail('launch.status must be draft or locked');

if (status === 'locked') {
  if (family === 'other') fail('locked config cannot use chain.family=other without explicit validator support');
  if (containsPlaceholder(config)) fail('locked config contains unresolved placeholder text');
  if ((config.evidence?.unresolved || []).length > 0) fail('locked config cannot contain evidence.unresolved items');
  if (!isNonEmptyString(config.evidence?.sourceCommit)) fail('locked config requires evidence.sourceCommit');
  if (!isNonEmptyString(config.launch?.lockedAt) || Number.isNaN(Date.parse(config.launch.lockedAt))) fail('locked config requires valid launch.lockedAt ISO date-time');
  if (!isNonEmptyString(config.launch?.lockedBy)) fail('locked config requires launch.lockedBy');
  if (!Array.isArray(config.evidence?.references) || config.evidence.references.length === 0) fail('locked config requires evidence.references');
  if (!Array.isArray(rpcUrls) || rpcUrls.length === 0) fail('locked config requires at least one public/approved RPC URL');
  if (config.addresses?.treasury === null) warn('locked config has null treasury; confirm this is intentionally NOT_APPLICABLE');
  if (config.addresses?.genesisPool === null) warn('locked config has null genesisPool; confirm this is intentionally NOT_APPLICABLE');
} else {
  if (containsPlaceholder(config)) warn('draft config contains unresolved placeholders (expected until evidence is complete)');
}

for (const w of warnings) console.warn(`[WARN] ${w}`);
for (const e of errors) console.error(`[FAIL] ${e}`);

if (errors.length > 0) {
  console.error(`\nValidation failed: ${errors.length} error(s), ${warnings.length} warning(s).`);
  process.exit(1);
}

console.log(`[PASS] ${file}`);
console.log(`launch.status=${status}`);
console.log(`chain.family=${family}`);
console.log(`token.identifier=${config.token?.identifier}`);
console.log(`Validation passed with ${warnings.length} warning(s).`);
