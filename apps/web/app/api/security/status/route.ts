/**
 * MOOD-SECURITY-022: Security Status API
 *
 * GET /api/security/status
 *
 * Returns the canonical security status payload for the /security page
 * and /network integration.
 *
 * Read-only. No secrets, no stack traces, no internal hostnames.
 */

import { NextResponse } from "next/server";
import { buildSecurityStatusPayload } from "@/lib/security/model";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const payload = buildSecurityStatusPayload();
    return NextResponse.json(payload, {
      headers: {
        "Cache-Control": "public, s-maxage=60, stale-while-revalidate=300",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        error: "Failed to generate security status",
        schema: "moodify-security-status-v1",
        generatedAt: new Date().toISOString(),
        overallStatus: "unavailable",
        stagingGate: {
          ready: false,
          blockers: ["api_error"],
          openGates: ["SG-ALL"],
        },
      },
      { status: 500 }
    );
  }
}
