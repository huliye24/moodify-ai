/**
 * MOOD-GENESIS-004-D: Golden Fixture Generator
 *
 * Generates cross-stack test fixtures using OpenZeppelin StandardMerkleTree.
 * These fixtures are consumed by both TypeScript tests and Forge Solidity tests.
 *
 * MOOD Merkle Standard v1:
 * - Leaf types: ["uint256", "address", "uint256"]
 * - Leaf values: [participantNumber, account, amountAtomic]
 * - Leaf hash: keccak256(bytes.concat(keccak256(abi.encode(...))))
 * - Tree: OpenZeppelin StandardMerkleTree (sorted pairs)
 */

import { StandardMerkleTree } from "@openzeppelin/merkle-tree";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

interface FixtureParticipant {
  participantNumber: number;
  account: string;
  amountAtomic: string;
}

interface FixtureEntry extends FixtureParticipant {
  leaf: string;
  proof: string[];
}

interface GoldenFixture {
  schema: string;
  version: string;
  description: string;
  participantCount: number;
  root: string;
  participants: FixtureEntry[];
}

const MOOD_MERKLE_SCHEMA = "mood-merkle-standard-v1";

/**
 * Generate a golden fixture for given participants.
 */
function generateFixture(
  name: string,
  participants: FixtureParticipant[]
): GoldenFixture {
  // Sort participants by participantNumber (deterministic ordering)
  const sorted = [...participants].sort((a, b) => a.participantNumber - b.participantNumber);

  // Build values array for StandardMerkleTree
  const values = sorted.map((p) => [
    p.participantNumber,
    p.account,
    BigInt(p.amountAtomic), // Convert string to bigint
  ]);

  // Create StandardMerkleTree with explicit leaf encoding
  const tree = StandardMerkleTree.of(values, ["uint256", "address", "uint256"]);

  // Generate entries with proofs
  // Note: We don't store individual leaf hashes - they can be computed
  // using the same OpenZeppelin library in Solidity
  const entries: FixtureEntry[] = sorted.map((p, index) => {
    const proof = tree.getProof(index);

    return {
      participantNumber: p.participantNumber,
      account: p.account,
      amountAtomic: p.amountAtomic,
      leaf: "computed-in-solidity", // Placeholder - actual leaf computed in contract
      proof,
    };
  });

  return {
    schema: MOOD_MERKLE_SCHEMA,
    version: "1.0.0",
    description: `Golden fixture for ${name}`,
    participantCount: participants.length,
    root: tree.root,
    participants: entries,
  };
}

/**
 * Generate all golden fixtures.
 */
function generateAllFixtures(): void {
  const fixturesDir = path.join(process.cwd(), "contracts", "test", "fixtures");
  fs.mkdirSync(fixturesDir, { recursive: true });

  // Fixture 1: Single participant
  const fixture1 = generateFixture("single-participant", [
    {
      participantNumber: 1,
      account: "0x1111111111111111111111111111111111111111",
      amountAtomic: "1000000000000000000000", // 1000 MOOD
    },
  ]);

  // Fixture 2: Two participants
  const fixture2 = generateFixture("two-participants", [
    {
      participantNumber: 1,
      account: "0x1111111111111111111111111111111111111111",
      amountAtomic: "1000000000000000000000", // 1000 MOOD
    },
    {
      participantNumber: 2,
      account: "0x2222222222222222222222222222222222222222",
      amountAtomic: "2000000000000000000000", // 2000 MOOD
    },
  ]);

  // Fixture 3: Three participants (odd count - important for tree structure)
  const fixture3 = generateFixture("three-participants", [
    {
      participantNumber: 1,
      account: "0x1111111111111111111111111111111111111111",
      amountAtomic: "1000000000000000000000", // 1000 MOOD
    },
    {
      participantNumber: 2,
      account: "0x2222222222222222222222222222222222222222",
      amountAtomic: "2000000000000000000000", // 2000 MOOD
    },
    {
      participantNumber: 3,
      account: "0x3333333333333333333333333333333333333333",
      amountAtomic: "1500000000000000000000", // 1500 MOOD
    },
  ]);

  // Fixture 5: Five participants (odd count)
  const fixture5 = generateFixture("five-participants", [
    {
      participantNumber: 1,
      account: "0x1111111111111111111111111111111111111111",
      amountAtomic: "1000000000000000000000",
    },
    {
      participantNumber: 2,
      account: "0x2222222222222222222222222222222222222222",
      amountAtomic: "2000000000000000000000",
    },
    {
      participantNumber: 3,
      account: "0x3333333333333333333333333333333333333333",
      amountAtomic: "1500000000000000000000",
    },
    {
      participantNumber: 4,
      account: "0x4444444444444444444444444444444444444444",
      amountAtomic: "500000000000000000000",
    },
    {
      participantNumber: 5,
      account: "0x5555555555555555555555555555555555555555",
      amountAtomic: "3000000000000000000000",
    },
  ]);

  // Write fixtures
  const fixtures = {
    "golden-single.json": fixture1,
    "golden-two.json": fixture2,
    "golden-three.json": fixture3,
    "golden-five.json": fixture5,
  };

  for (const [filename, fixture] of Object.entries(fixtures)) {
    const filepath = path.join(fixturesDir, filename);
    fs.writeFileSync(filepath, JSON.stringify(fixture, null, 2));
    console.log(`✓ ${filepath}`);
    console.log(`  Root: ${fixture.root}`);
    console.log(`  Participants: ${fixture.participantCount}`);
    console.log();
  }

  // Generate Solidity fixture loader
  generateSolidityLoader(fixturesDir, fixtures);

  console.log("=".repeat(60));
  console.log("Golden fixtures generated successfully!");
  console.log("=".repeat(60));
  console.log();
  console.log("Location:", fixturesDir);
  console.log();
  console.log("Cross-stack invariant:");
  console.log("  TypeScript generator → JSON fixture → Solidity test");
  console.log();
}

/**
 * Generate Solidity test helper for loading fixtures.
 */
function generateSolidityLoader(
  fixturesDir: string,
  fixtures: Record<string, GoldenFixture>
): void {
  const loaderPath = path.join(fixturesDir, "GoldenFixtures.sol");

  const fixtureStructs = Object.entries(fixtures)
    .map(([filename, fixture]) => {
      const name = filename.replace(".json", "").replace(/-/g, "_");
      return `
    // ${filename}
    bytes32 public constant ${name.toUpperCase()}_ROOT = ${fixture.root};
    uint256 public constant ${name.toUpperCase()}_COUNT = ${fixture.participantCount};`;
    })
    .join("\n");

  const content = `// SPDX-License-Identifier: GPL-3.0-only
pragma solidity ^0.8.20;

/**
 * @title GoldenFixtures
 * @notice Auto-generated fixture constants for cross-stack testing
 * @dev Generated by scripts/generate-golden-fixtures.ts
 *      DO NOT EDIT MANUALLY
 */

library GoldenFixtures {
    // MOOD Merkle Standard v1
    string public constant SCHEMA = "${MOOD_MERKLE_SCHEMA}";
    string public constant VERSION = "1.0.0";

    // Fixture roots${fixtureStructs}
}
`;

  fs.writeFileSync(loaderPath, content);
  console.log(`✓ ${loaderPath}`);
}

// Run if called directly
const __filename = fileURLToPath(import.meta.url);
if (__filename === process.argv[1]) {
  generateAllFixtures();
}

export { generateFixture, generateAllFixtures };
