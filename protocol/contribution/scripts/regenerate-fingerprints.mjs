// Regenerate fingerprints in all fixtures
import { computeContentFingerprint } from '../src/fingerprint.js';
import { readFileSync, writeFileSync, readdirSync } from 'fs';

const fixturesDir = './fixtures';
const files = readdirSync(fixturesDir).filter(f =>
  f.endsWith('.json') && !f.includes('example')
);

let updated = 0;
for (const file of files) {
  const path = `${fixturesDir}/${file}`;
  const data = JSON.parse(readFileSync(path, 'utf8'));
  if (!data.contentFingerprint) continue;

  // Compute directly on the fixture data (excluding only mutable review fields)
  const computed = computeContentFingerprint(data);
  if (computed !== data.contentFingerprint) {
    data.contentFingerprint = computed;
    writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
    console.log(`Updated: ${file}`);
    updated++;
  }
}

console.log(`\nTotal updated: ${updated}`);