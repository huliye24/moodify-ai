#!/usr/bin/env node
/**
 * MOOD-GENESIS-006: Contribution Reward Export Script
 *
 * Usage:
 *   npm run contributions:rewards-export [-- --git=<commit>]
 *
 * Output:
 *   - artifacts/contribution-rewards/<timestamp>/rewards.csv
 *   - artifacts/contribution-rewards/<timestamp>/rewards.json
 *
 * This script produces a deterministic pending-reward export that future
 * distribution snapshots can consume. No chain interaction, no signing.
 */

import { mkdir, writeFile } from "fs/promises";
import { join } from "path";

// Import from contribution-export module
// These would be imported from the actual module in production
// For now, we define the interface here

interface RewardExportRow {
  participantNumber: number;
  walletAddress: string;
  rewardMood: string;
  rewardAtomic: string;
  sourceRewardEventIds: string[];
}

interface RewardExportJson {
  schema: string;
  generatedAt: string;
  sourceGitCommit: string | null;
  summary: {
    participants: number;
    rewardEvents: number;
    totalMood: string;
    totalAtomic: string;
  };
  rewards: RewardExportRow[];
}

const EXPORT_SCHEMA = "moodify-contribution-rewards-v1";

function getGitCommit(): string | null {
  // Try to get git commit from command line arg
  const gitArg = process.argv.find((arg) => arg.startsWith("--git="));
  if (gitArg) {
    return gitArg.slice(6);
  }
  return null;
}

function csvEscape(value: string): string {
  if (/[",\n]/.test(value)) return `"${value.replace(/"/g, '""')}"`;
  return value;
}

function renderCsv(rows: RewardExportRow[]): string {
  const header = "participant_number,wallet_address,reward_mood,reward_atomic,source_reward_event_ids";
  const lines = rows.map((r) =>
    [
      String(r.participantNumber),
      csvEscape(r.walletAddress),
      csvEscape(r.rewardMood),
      csvEscape(r.rewardAtomic),
      csvEscape(r.sourceRewardEventIds.join(";")),
    ].join(","),
  );
  return [header, ...lines].join("\n") + (rows.length > 0 ? "\n" : "");
}

function renderJson(rows: RewardExportRow[], generatedAt: string): string {
  let totalAtomic = 0n;
  let rewardEventCount = 0;
  for (const r of rows) {
    totalAtomic += BigInt(r.rewardAtomic);
    rewardEventCount += r.sourceRewardEventIds.length;
  }

  // Convert atomic to mood (divide by 10^18)
  const totalMood = (totalAtomic / BigInt(10) ** BigInt(18)).toString();

  const payload: RewardExportJson = {
    schema: EXPORT_SCHEMA,
    generatedAt,
    sourceGitCommit: getGitCommit(),
    summary: {
      participants: rows.length,
      rewardEvents: rewardEventCount,
      totalMood,
      totalAtomic: totalAtomic.toString(),
    },
    rewards: rows,
  };
  return JSON.stringify(payload, null, 2);
}

async function main() {
  console.log("MOOD-GENESIS-006: Contribution Reward Export");
  console.log("============================================");

  // In a real implementation, this would:
  // 1. Connect to the database
  // 2. Query pending reward events
  // 3. Aggregate by participant
  // 4. Generate CSV and JSON output

  // For now, we create placeholder output
  const generatedAt = new Date().toISOString();
  const timestamp = generatedAt.replace(/[:.]/g, "-").slice(0, 19);
  const outputDir = join(process.cwd(), "artifacts", "contribution-rewards", timestamp);

  // Placeholder data - in production this would come from the database
  const placeholderRows: RewardExportRow[] = [];

  // Create output directory
  await mkdir(outputDir, { recursive: true });

  // Write CSV
  const csvPath = join(outputDir, "rewards.csv");
  const csvContent = renderCsv(placeholderRows);
  await writeFile(csvPath, csvContent, "utf-8");
  console.log(`✓ CSV: ${csvPath}`);

  // Write JSON
  const jsonPath = join(outputDir, "rewards.json");
  const jsonContent = renderJson(placeholderRows, generatedAt);
  await writeFile(jsonPath, jsonContent, "utf-8");
  console.log(`✓ JSON: ${jsonPath}`);

  console.log("\nExport Summary:");
  console.log(`  Schema: ${EXPORT_SCHEMA}`);
  console.log(`  Generated: ${generatedAt}`);
  console.log(`  Participants: ${placeholderRows.length}`);
  console.log(`  Total MOOD: 0`);
  console.log(`\nNote: This is a placeholder export.");
  console.log("To export actual rewards, run against a database with pending reward events.");
}

main().catch((error) => {
  console.error("Export failed:", error);
  process.exit(1);
});
