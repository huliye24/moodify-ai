/**
 * MOOD-TREASURY-021: Treasury Status API
 *
 * GET /api/protocol/treasury/status
 *
 * Minimal status payload intended for /network integration.
 * Read-only. No sensitive data.
 */

import { NextResponse } from "next/server";
import { buildTreasuryStatusPayload } from "@/lib/treasury/model";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const payload = buildTreasuryStatusPayload();
    return NextResponse.json(payload, {
      headers: {
        "Cache-Control": "public, s-maxage=30, stale-while-revalidate=120",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        error: "Failed to generate treasury status",
        schema: "moodify-treasury-status-v1",
        generatedAt: new Date().toISOString(),
        treasuryStatus: "unavailable",
        verifiedAccounts: 0,
        lastReport: null,
        lastActivity: null,
        economics: "Unknown",
        disabledSlots: [],
      },
      { status: 500 }
    );
  }
}
