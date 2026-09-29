/**
 * MOOD-TREASURY-021: Treasury API
 *
 * GET /api/protocol/treasury
 *
 * Returns the canonical Treasury snapshot. In v1 this is the HONEST
 * inactive state — there are no real protocol-controlled funds.
 *
 * SAFETY:
 *   - Read-only
 *   - No private keys, mnemonics, seeds, env secrets
 *   - No transfer / execution endpoints
 *   - No third-party credentials
 */

import { NextResponse } from "next/server";
import {
  buildTreasurySnapshot,
  type TreasurySnapshot,
} from "@/lib/treasury/model";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const snapshot: TreasurySnapshot = buildTreasurySnapshot();
    return NextResponse.json(snapshot, {
      headers: {
        "Cache-Control": "public, s-maxage=60, stale-while-revalidate=300",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        error: "Failed to generate treasury data",
        schema: "moodify-treasury-v1",
        generatedAt: new Date().toISOString(),
        treasuryStatus: "inactive",
        accounts: [],
        assets: [],
        revenue: [],
        allocations: [],
        executions: [],
        reconciliation: {
          verified: 0,
          mismatch: 0,
          unavailable: 0,
          stale: 0,
          mismatches: [],
        },
        risks: ["API error occurred"],
        governanceRefs: [],
        notes:
          error instanceof Error
            ? `Error: ${error.message}`
            : "Unknown error",
      },
      { status: 500 }
    );
  }
}
