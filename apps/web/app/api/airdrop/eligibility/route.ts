/**
 * MOOD-GENESIS-005: Airdrop Eligibility API
 *
 * GET /api/airdrop/eligibility?address=0x...
 *
 * Returns only public claim fields:
 * - eligible: boolean
 * - participantNumber: number
 * - amountMood: string
 * - amountAtomic: string
 * - proof: string[]
 * - claimStatus: "unclaimed" | "claimed"
 *
 * Does NOT return:
 * - Internal admin notes
 * - Raw signatures
 * - Nonces
 * - Private user profile fields
 */

import { NextRequest, NextResponse } from "next/server";
import { normalizeAddress } from "@/lib/evm-address";
import { getDb } from "@/db";
import { genesisParticipants } from "@/db/schema";
import { eq } from "drizzle-orm";

// In production, this would load from the approved Package 004 merkle.json
// For now, we return mock data for development
const MOCK_MERKLE_DATA: Record<
  string,
  {
    participantNumber: number;
    amountMood: string;
    amountAtomic: string;
    proof: string[];
  }
> = {
  // Development test address
  "0x1111111111111111111111111111111111111111": {
    participantNumber: 1,
    amountMood: "1000",
    amountAtomic: "1000000000000000000000",
    proof: ["0x..."],
  },
};

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const address = searchParams.get("address");

    if (!address) {
      return NextResponse.json(
        { error: "Address required" },
        { status: 400 }
      );
    }

    // Normalize address
    const normalized = normalizeAddress(address);
    if (!normalized) {
      return NextResponse.json(
        { error: "Invalid address format" },
        { status: 400 }
      );
    }

    // Check database for participant status
    const db = getDb();
    const participant = await db.query.genesisParticipants.findFirst({
      where: eq(genesisParticipants.walletAddressNormalized, normalized),
    });

    // Participant must exist and be allocated
    if (!participant || participant.status !== "allocated") {
      return NextResponse.json(
        { eligible: false },
        { status: 404 }
      );
    }

    // Must have allocation amount
    if (!participant.allocationMood || !participant.allocationAtomic) {
      return NextResponse.json(
        { eligible: false },
        { status: 404 }
      );
    }

    // In production, load proof from approved Package 004 merkle.json
    // For development, return mock data if available
    const mockData = MOCK_MERKLE_DATA[normalized];

    if (process.env.NODE_ENV === "development" && mockData) {
      return NextResponse.json({
        eligible: true,
        participantNumber: mockData.participantNumber,
        amountMood: mockData.amountMood,
        amountAtomic: mockData.amountAtomic,
        proof: mockData.proof,
        claimStatus: "unclaimed",
      });
    }

    // Production: return eligibility without proof (proof loaded client-side from artifact)
    return NextResponse.json({
      eligible: true,
      participantNumber: participant.participantNumber,
      amountMood: participant.allocationMood,
      amountAtomic: participant.allocationAtomic,
      proof: [], // Client loads from static merkle.json
      claimStatus: "unclaimed", // TODO: Check on-chain claim status
    });
  } catch (error) {
    console.error("Airdrop eligibility error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
