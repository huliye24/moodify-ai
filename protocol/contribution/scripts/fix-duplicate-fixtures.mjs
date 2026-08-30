// Force duplicate fixtures to share fingerprints with their originals.
// This simulates exact-duplicate and cross-contributor-duplicate scenarios.
import { computeContentFingerprint } from '../src/fingerprint.js';
import { readFileSync, writeFileSync } from 'fs';

function updateContentFingerprint(targetFile, sourceFile) {
  const target = JSON.parse(readFileSync(targetFile, 'utf8'));
  const source = JSON.parse(readFileSync(sourceFile, 'utf8'));
  // Use source's computed fingerprint as the target's
  target.contentFingerprint = computeContentFingerprint(source);
  writeFileSync(targetFile, JSON.stringify(target, null, 2) + '\n');
  console.log(`${targetFile} fingerprint now matches ${sourceFile}`);
}

// Exact duplicate: same contributor, same category, same content
updateContentFingerprint(
  './fixtures/duplicate-contribution.json',
  './fixtures/valid-code-contribution.json',
);

// Cross-contributor duplicate: same content fingerprint, different contributor
updateContentFingerprint(
  './fixtures/cross-contributor-duplicate.json',
  './fixtures/valid-docs-contribution.json',
);