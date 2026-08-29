#!/usr/bin/env node

import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const input = process.argv[2] || 'protocol/mainnet.json';
const output = process.argv[3] || 'protocol/mainnet.lock.json';
const inputPath = path.resolve(process.cwd(), input);
const outputPath = path.resolve(process.cwd(), output);

let raw;
let config;
try {
  raw = fs.readFileSync(inputPath);
  config = JSON.parse(raw.toString('utf8'));
} catch (err) {
  console.error(`[FAIL] Cannot read/parse ${input}: ${err.message}`);
  process.exit(1);
}

if (config.launch?.status !== 'locked') {
  console.error('[FAIL] Refusing to create lock artifact because launch.status is not locked.');
  process.exit(1);
}

if (!config.evidence?.sourceCommit) {
  console.error('[FAIL] Refusing to create lock artifact without evidence.sourceCommit.');
  process.exit(1);
}

if (!config.launch?.lockedAt) {
  console.error('[FAIL] Refusing to create lock artifact without launch.lockedAt.');
  process.exit(1);
}

if ((config.evidence?.unresolved || []).length > 0) {
  console.error('[FAIL] Refusing to create lock artifact with unresolved evidence items.');
  process.exit(1);
}

const lock = {
  lockVersion: '1.0.0',
  schemaVersion: config.schemaVersion,
  configPath: input.replaceAll('\\', '/'),
  configSha256: crypto.createHash('sha256').update(raw).digest('hex'),
  sourceCommit: config.evidence.sourceCommit,
  lockedAt: config.launch.lockedAt,
  lockedBy: config.launch.lockedBy,
  chain: {
    family: config.chain?.family,
    network: config.chain?.network,
    chainId: config.chain?.chainId ?? null,
    cluster: config.chain?.cluster ?? null
  },
  token: {
    symbol: config.token?.symbol,
    identifier: config.token?.identifier,
    decimals: config.token?.decimals,
    totalSupplyAtomic: config.token?.totalSupplyAtomic
  }
};

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, `${JSON.stringify(lock, null, 2)}\n`, 'utf8');
console.log(`[PASS] Wrote ${output}`);
console.log(`configSha256=${lock.configSha256}`);
