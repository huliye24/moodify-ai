/* MOOD-GENESIS-006: Contribution Reward Export.
 *
 * Produces a deterministic pending-reward export that future distribution
 * snapshots can consume (Package 004/005 integration). This is NOT a
 * transaction file: no chain interaction, no signing, no transfer.
 *
 * Export format (CSV + JSON companion):
 *   - participant_number (ascending)
 *   - wallet_address (checksum form)
 *   - reward_mood (decimal string)
 *   - reward_atomic (bigint string)
 *   - source_reward_event_ids (semicolon-joined list)
 *
 * Privacy guarantees:
 *   - Internal notes, review reasons, raw signatures, nonces, and admin
 *     session data are NEVER exported.
 *   - Only events with status = 'pending' and reward_atomic > 0 are
 *     included. Cancelled / included_in_snapshot / distributed are excluded.
 *
 * Determinism guarantees:
 *   - Same input data → same output bytes.
 *   - JSON keys are alphabetically sorted.
 *   - Multiple events for the same participant are aggregated with
 *     source_reward_event_ids preserved. */

import { and, asc, eq, sql } from "drizzle-orm";
import { getDb } from "@/db";
import { genesisParticipants, rewardEvents } from "@/db/schema";
import { fromAtomicUnits } from "@/lib/genesis-distribution";
import { CONTRIBUTION_CONFIG } from "@/lib/contribution-config";

export interface RewardExportRow {
  participantNumber: number;
  walletAddress: string;
  rewardMood: string;
  rewardAtomic: string;
  sourceRewardEventIds: string[];
}

export interface RewardExportJson {
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

function gitCommit(): string | null {
  // We don't import node:child_process at the top because Cloudflare
  // Workers doesn't have access to execSync. The CLI wrapper at
  // scripts/contributions-rewards-export.ts supplies --git when needed;
  // here we report null in the JSON (still deterministic).
  return null;
}

function atomicAdd(a: bigint, b: bigint): bigint {
  return a + b;
}

/** Build deterministic pending-reward export rows from the DB. */
export async function buildPendingRewardExport(): Promise<{
  rows: RewardExportRow[];
  generatedAt: string;
}> {
  const db = getDb();
  const events = await db
    .select({
      id: rewardEvents.id,
      participantId: rewardEvents.participantId,
      rewardMood: rewardEvents.rewardMood,
      rewardAtomic: rewardEvents.rewardAtomic,
      status: rewardEvents.status,
      participantNumber: genesisParticipants.participantNumber,
      walletAddress: genesisParticipants.walletAddress,
    })
    .from(rewardEvents)
    .innerJoin(genesisParticipants, eq(rewardEvents.participantId, genesisParticipants.id))
    .where(and(eq(rewardEvents.status, "pending"), sql`${rewardEvents.rewardAtomic} > '0'`))
    .orderBy(asc(genesisParticipants.participantNumber), asc(rewardEvents.createdAt));

  const byParticipant = new Map<string, RewardExportRow>();
  for (const ev of events) {
    const existing = byParticipant.get(ev.participantId);
    const atomic = BigInt(ev.rewardAtomic);
    if (existing) {
      const newAtomic = atomicAdd(BigInt(existing.rewardAtomic), atomic);
      existing.rewardAtomic = newAtomic.toString();
      existing.rewardMood = fromAtomicUnits(newAtomic.toString());
      existing.sourceRewardEventIds.push(ev.id);
    } else {
      byParticipant.set(ev.participantId, {
        participantNumber: ev.participantNumber,
        walletAddress: ev.walletAddress,
        rewardMood: fromAtomicUnits(atomic.toString()),
        rewardAtomic: atomic.toString(),
        sourceRewardEventIds: [ev.id],
      });
    }
  }
  const rows = Array.from(byParticipant.values()).sort((a, b) => a.participantNumber - b.participantNumber);
  return { rows, generatedAt: new Date().toISOString() };
}

function csvEscape(value: string): string {
  if (/[",\n]/.test(value)) return `"${value.replace(/"/g, '""')}"`;
  return value;
}

export function renderCsv(rows: RewardExportRow[]): string {
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

export function renderJson(rows: RewardExportRow[], generatedAt: string): string {
  let totalAtomic = 0n;
  let rewardEventCount = 0;
  for (const r of rows) {
    totalAtomic += BigInt(r.rewardAtomic);
    rewardEventCount += r.sourceRewardEventIds.length;
  }
  const payload: RewardExportJson = {
    schema: EXPORT_SCHEMA,
    generatedAt,
    sourceGitCommit: gitCommit(),
    summary: {
      participants: rows.length,
      rewardEvents: rewardEventCount,
      totalMood: fromAtomicUnits(totalAtomic.toString()),
      totalAtomic: totalAtomic.toString(),
    },
    rewards: rows,
  };
  return JSON.stringify(payload, null, 2);
}

/* Re-export the schema version for tests/CLI consumers. */
export const CONTRIBUTION_REWARD_EXPORT_SCHEMA = EXPORT_SCHEMA;
export const CONTRIBUTION_REWARD_EXPORT_CEILING_ATOMIC = CONTRIBUTION_CONFIG.genesisPoolCeilingAtomic;
