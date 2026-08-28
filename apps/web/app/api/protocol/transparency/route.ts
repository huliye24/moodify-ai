/**
 * MOOD-GENESIS-007: Protocol Transparency API
 *
 * GET /api/protocol/transparency
 *
 * Returns safe aggregate data with source metadata.
 * No private data exposed.
 */

import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/db";
import { genesisParticipants } from "@/db/schema";
import { eq, sql } from "drizzle-orm";
import {
  TREASURY_CONFIG,
  getPublicTreasuryAccounts,
  findDuplicateAddresses,
  getMoodTokenConfig,
} from "@/lib/mood-treasury";
import {
  getTotalSupply,
  getTreasuryBalances,
  formatMood,
  calculatePercentage,
  reconcileTreasury,
} from "@/lib/mood-chain";
import { MOOD_TOKEN } from "@/lib/mood-token";

/** Transparency data response */
interface TransparencyData {
  schema: string;
  generatedAt: string;
  token: {
    name: string;
    symbol: string;
    address: string;
    decimals: number;
    totalSupply: {
      value: string;
      source: string;
      updatedAt: string;
      isStale: boolean;
      error?: string;
    };
    explorerUrl: string;
    tradeUrl: string;
  };
  accounts: {
    id: string;
    label: string;
    category: string;
    address: string;
    balance: {
      value: string;
      source: string;
      updatedAt: string;
      isStale: boolean;
      error?: string;
    };
    percentageOfSupply: number;
    controlModel?: string;
    notes?: string;
  }[];
  genesis: {
    totalParticipants: number;
    allocatedParticipants: number;
    totalAllocation: string;
    claimedAmount: string;
    unclaimedAmount: string;
    distributorDeployed: boolean;
    distributorAddress?: string;
    merkleRoot?: string;
  };
  contributions: {
    status: string;
    description: string;
  };
  liquidity: {
    status: string;
    description: string;
  };
  methodology: {
    circulatingSupply: {
      status: string;
      description: string;
    };
    dataSources: string[];
    limitations: string[];
  };
  reconciliation: {
    isBalanced: boolean;
    warnings: string[];
  };
}

export async function GET(request: NextRequest) {
  try {
    // Get token config
    const tokenConfig = getMoodTokenConfig();

    // Get total supply
    const totalSupply = await getTotalSupply();

    // Get public treasury accounts
    const publicAccounts = getPublicTreasuryAccounts();

    // Get balances for public accounts
    const balances = await getTreasuryBalances(publicAccounts);

    // Reconcile treasury
    const reconciliation = await reconcileTreasury(balances);

    // Check for duplicate addresses
    const duplicates = findDuplicateAddresses();
    if (duplicates.length > 0) {
      reconciliation.warnings.push(
        `Duplicate treasury addresses found: ${duplicates.join(", ")}`
      );
      reconciliation.isBalanced = false;
    }

    // Get Genesis aggregates from database
    const db = getDb();
    const genesisStats = await db
      .select({
        total: sql<number>`COUNT(*)`,
        allocated: sql<number>`SUM(CASE WHEN ${genesisParticipants.status} = 'allocated' THEN 1 ELSE 0 END)`,
      })
      .from(genesisParticipants)
      .get();

    // Build account data
    const accountData = publicAccounts.map((account) => {
      const balance = balances[account.id];
      const percentage = totalSupply.value
        ? calculatePercentage(balance?.value || BigInt(0), totalSupply.value)
        : 0;

      return {
        id: account.id,
        label: account.label,
        category: account.category,
        address: account.address,
        balance: {
          value: formatMood(balance?.value || BigInt(0)),
          source: balance?.source || "unavailable",
          updatedAt: balance?.updatedAt || new Date().toISOString(),
          isStale: balance?.isStale ?? true,
          error: balance?.error,
        },
        percentageOfSupply: percentage,
        controlModel: account.controlModel,
        notes: account.notes,
      };
    });

    // Build response
    const response: TransparencyData = {
      schema: "moodify-transparency-v1",
      generatedAt: new Date().toISOString(),
      token: {
        name: tokenConfig.name,
        symbol: tokenConfig.symbol,
        address: tokenConfig.address,
        decimals: tokenConfig.decimals,
        totalSupply: {
          value: formatMood(totalSupply.value),
          source: totalSupply.source,
          updatedAt: totalSupply.updatedAt,
          isStale: totalSupply.isStale,
          error: totalSupply.error,
        },
        explorerUrl: tokenConfig.explorerUrl,
        tradeUrl: tokenConfig.tradeUrl,
      },
      accounts: accountData,
      genesis: {
        totalParticipants: genesisStats?.total || 0,
        allocatedParticipants: genesisStats?.allocated || 0,
        totalAllocation: "0", // Would come from Package 004 snapshot
        claimedAmount: "0", // Would come from on-chain reads
        unclaimedAmount: "0",
        distributorDeployed: false, // Would check if distributor address configured
      },
      contributions: {
        status: "not_implemented",
        description:
          "Contribution network aggregates not yet implemented. See Package 006.",
      },
      liquidity: {
        status: "not_verified",
        description:
          "Liquidity positions not yet verified. PancakeSwap pool data pending.",
      },
      methodology: {
        circulatingSupply: {
          status: TREASURY_CONFIG.circulatingSupply.status,
          description: TREASURY_CONFIG.circulatingSupply.description,
        },
        dataSources: [
          "BNB Smart Chain RPC (bsc-dataseed.binance.org)",
          "Moodify Genesis database",
          "Approved Package 004 snapshot artifacts",
          "On-chain event logs (when indexed)",
        ],
        limitations: [
          "RPC reads may fail or be stale",
          "Database aggregates reflect last-known state",
          "On-chain events require indexing",
          "Circulating supply methodology not yet approved",
        ],
      },
      reconciliation: {
        isBalanced: reconciliation.isBalanced,
        warnings: reconciliation.warnings,
      },
    };

    return NextResponse.json(response, {
      headers: {
        "Cache-Control": "public, s-maxage=60, stale-while-revalidate=300",
      },
    });
  } catch (error) {
    console.error("Transparency API error:", error);
    return NextResponse.json(
      {
        error: "Failed to generate transparency data",
        schema: "moodify-transparency-v1",
        generatedAt: new Date().toISOString(),
        token: {
          name: MOOD_TOKEN.name,
          symbol: MOOD_TOKEN.symbol,
          address: MOOD_TOKEN.address,
          decimals: MOOD_TOKEN.decimals,
          totalSupply: {
            value: MOOD_TOKEN.totalSupply,
            source: "config",
            updatedAt: new Date().toISOString(),
            isStale: true,
          },
          explorerUrl: MOOD_TOKEN.explorerUrl,
          tradeUrl: MOOD_TOKEN.tradeUrl,
        },
        accounts: [],
        genesis: {
          totalParticipants: 0,
          allocatedParticipants: 0,
          totalAllocation: "0",
          claimedAmount: "0",
          unclaimedAmount: "0",
          distributorDeployed: false,
        },
        contributions: {
          status: "error",
          description: "Failed to load contribution data",
        },
        liquidity: {
          status: "error",
          description: "Failed to load liquidity data",
        },
        methodology: {
          circulatingSupply: {
            status: "not_published",
            description: "Circulating supply methodology not yet formally published",
          },
          dataSources: [],
          limitations: ["API error occurred"],
        },
        reconciliation: {
          isBalanced: false,
          warnings: [error instanceof Error ? error.message : "Unknown error"],
        },
      },
      { status: 500 }
    );
  }
}
