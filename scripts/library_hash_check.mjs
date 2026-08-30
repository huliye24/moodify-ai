// MOOD LIBRARY 014 — Hash verification
// Verifies that the SHA-256 values embedded in registry.ts match the
// actual file contents at the registered sourcePath.
//
// Usage: node scripts/library_hash_check.mjs
//
// Authority: docs/mood/library/014_HASH_POLICY.md

import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

// Mirror of registry.ts. We don't import the TS module because Node can't
// execute TS without a loader. Keep this list in sync with registry.ts.
const EXPECTED = [
  ["docs/mood/CURRENT_CANON.md", "6509b960cd0cfe5c64918f6a4d7662e687ba3625544961f0fa5321052061fb1b"],
  ["docs/mood/SYSTEM_ARCHITECTURE.md", "0e9de7b203bc250fd6947688637b0589623c176f391f775b4706bcbe9ea6df64"],
  ["docs/mood/PRODUCT_RELATIONSHIP.md", "bed3e0ce7821dbebea2fa75be6e74f74d5d797e4c08eacc5162e6aef29cd5c80"],
  ["docs/mood/TOKEN_LAUNCH_GATE.md", "1bce11cf7ee2b07ca674fbe8442d81d8b8bb3cf8d07299635d33976699a136c8"],
  ["docs/mood/ASSET_CLASSIFICATION.md", "928beffe91b5ffbca26240f14fdd5db49ea2a41c97d770009d21fbcee7b23062"],
  ["docs/mood/SEPTEMBER_BUILD_ROADMAP.md", "6e1521792679c266847e8d9bcdd52f587fef92537b467b34b7ebca5ae0d43fb4"],
  ["docs/mood/DECISION_LOG.md", "0632b913dd151db43e6b18a28471391500b4166fb8224636b7dd635c1e4eff3d"],
  ["docs/mood/IN_FLIGHT_CHANGE_REGISTER.md", "9681ef7ae394f38a00e5df7389a549ae46c055fbc0fe72e99767a10aa9e99023"],
  ["docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md", "2a35578be75f0f31f0d68e62741d6bad99b5f2db69c44c3e0e8a1bafecfbc7bf"],
  ["docs/canon/CURRENT_CANON.md", "77f7763e32692ad1af1c10679e6114f366461961b4b90f0e3c02aaef6092110d"],
];

async function sha256(filePath) {
  const buf = await readFile(filePath);
  return createHash("sha256").update(buf).digest("hex");
}

async function exists(filePath) {
  try {
    await stat(filePath);
    return true;
  } catch {
    return false;
  }
}

let failed = 0;
let skipped = 0;
let passed = 0;

for (const [relPath, expected] of EXPECTED) {
  const full = path.join(repoRoot, relPath);
  if (!(await exists(full))) {
    console.error(`MISSING ${relPath}`);
    failed += 1;
    continue;
  }
  const actual = await sha256(full);
  if (actual === expected) {
    console.log(`PASS    ${relPath}`);
    passed += 1;
  } else {
    console.error(`FAIL    ${relPath}`);
    console.error(`        expected ${expected}`);
    console.error(`        actual   ${actual}`);
    failed += 1;
  }
}

console.log("");
console.log(`Hash verification: ${passed} pass, ${failed} fail, ${skipped} skip`);
process.exit(failed === 0 ? 0 : 1);