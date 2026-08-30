/**
 * MOOD-GENESIS-007: Real BSC Mainnet Chain Service
 *
 * Typed reads for on-chain MOOD data using viem.
 * No signer required.
 * No write capabilities.
 *
 * This implementation replaces the placeholder version with real BSC mainnet RPC.
 */

import { createPublicClient, http, parseAbi } from "viem";
import { bsc } from "viem/chains";
import { MOOD_TOKEN } from "./mood-token";
import { TREASURY_CONFIG, TreasuryAccount } from "./mood-treasury";

/** BEP-20 token ABI (read-only) */
const MOOD_ABI = parseAbi([
  "function totalSupply() view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function balanceOf(address account) view returns (uint256)",
]);

/** Distributor ABI (read-only) */
const DISTRIBUTOR_ABI = parseAbi([
  "function merkleRoot() view returns (bytes32)",
  "function token() view returns (address)",
  "function claimedParticipant(uint256 participantNumber) view returns (bool)",
  "function totalClaimed() view returns (uint256)",
  "function distributorBalance() view returns (uint256)",
]);

/** Public RPC endpoint for BSC mainnet */
const BSC_RPC_URL = process.env.NEXT_PUBLIC_BSC_RPC || "https://bsc-dataseed-public.bnbchain.org";

/** Create viem public client for BSC with timeout */
function createBSCClient() {
  return createPublicClient({
    chain: bsc,
    transport: http(BSC_RPC_URL, {
      timeout: 10000, // 10 second timeout
    }),
  });
}

/** Bounded RPC call wrapper with timeout */
async function callWithTimeout<T>(
  fn: () => Promise<T>,
  timeoutMs: number = 10000
): Promise<T> {
  return Promise.race([
    fn(),
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error("RPC_TIMEOUT")), timeoutMs)
    ),
  ]);
}

/** Chain data with metadata */
export interface ChainData<T> {
  /** The data value */
  value: T;
  /** Data source */
  source: "rpc" | "cache" | "config" | "unavailable";
  /** Last updated timestamp */
  updatedAt: string;
  /** Block number if available */
  blockNumber?: number;
  /** Whether data is stale */
  isStale: boolean;
  /** Error if read failed */
  error?: string;
}

/** Chain read error */
export class ChainReadError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "ChainReadError";
  }
}

/** Get total supply from BSC */
export async function getTotalSupply(): Promise<ChainData<bigint>> {
  try {
    const client = createBSCClient();
    const result = await callWithTimeout(() =>
      client.readContract({
        address: MOOD_TOKEN.address as `0x${string}`,
        abi: MOOD_ABI,
        functionName: "totalSupply",
      })
    );

    return {
      value: result,
      source: "rpc",
      updatedAt: new Date().toISOString(),
      isStale: false,
    };
  } catch (error) {
    console.error("Failed to read totalSupply:", error);
    return {
      value: BigInt(MOOD_TOKEN.totalSupply) * BigInt(10 ** MOOD_TOKEN.decimals),
      source: "unavailable",
      updatedAt: new Date().toISOString(),
      isStale: true,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/** Get decimals from BSC */
export async function getDecimals(): Promise<ChainData<number>> {
  try {
    const client = createBSCClient();
    const result = await callWithTimeout(() =>
      client.readContract({
        address: MOOD_TOKEN.address as `0x${string}`,
        abi: MOOD_ABI,
        functionName: "decimals",
      })
    );

    return {
      value: result,
      source: "rpc",
      updatedAt: new Date().toISOString(),
      isStale: false,
    };
  } catch (error) {
    console.error("Failed to read decimals:", error);
    return {
      value: MOOD_TOKEN.decimals,
      source: "unavailable",
      updatedAt: new Date().toISOString(),
      isStale: true,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/** Get MOOD balance of address from BSC */
export async function getBalance(address: string): Promise<ChainData<bigint>> {
  try {
    const client = createBSCClient();
    const result = await callWithTimeout(() =>
      client.readContract({
        address: MOOD_TOKEN.address as `0x${string}`,
        abi: MOOD_ABI,
        functionName: "balanceOf",
        args: [address as `0x${string}`],
      })
    );

    return {
      value: result,
      source: "rpc",
      updatedAt: new Date().toISOString(),
      isStale: false,
    };
  } catch (error) {
    console.error("Failed to read balance:", error);
    return {
      value: BigInt(0),
      source: "unavailable",
      updatedAt: new Date().toISOString(),
      isStale: true,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/** Get distributor state */
export async function getDistributorState(
  distributorAddress: string
): Promise<{
  merkleRoot: ChainData<string>;
  token: ChainData<string>;
  totalClaimed: ChainData<bigint>;
  balance: ChainData<bigint>;
}> {
  try {
    const client = createBSCClient();

    const [merkleRoot, token, totalClaimed, balance] = await Promise.all([
      client.readContract({
        address: distributorAddress as `0x${string}`,
        abi: DISTRIBUTOR_ABI,
        functionName: "merkleRoot",
      }).catch(() => null),
      client.readContract({
        address: distributorAddress as `0x${string}`,
        abi: DISTRIBUTOR_ABI,
        functionName: "token",
      }).catch(() => null),
      client.readContract({
        address: distributorAddress as `0x${string}`,
        abi: DISTRIBUTOR_ABI,
        functionName: "totalClaimed",
      }).catch(() => null),
      client.readContract({
        address: distributorAddress as `0x${string}`,
        abi: DISTRIBUTOR_ABI,
        functionName: "distributorBalance",
      }).catch(() => null),
    ]);

    return {
      merkleRoot: {
        value: merkleRoot ? `0x${merkleRoot.toString(16)}` : "0x0",
        source: merkleRoot ? "rpc" : "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: !merkleRoot,
        error: merkleRoot ? undefined : "Distributor not deployed",
      },
      token: {
        value: token || "0x0",
        source: token ? "rpc" : "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: !token,
        error: token ? undefined : "Distributor not deployed",
      },
      totalClaimed: {
        value: totalClaimed || BigInt(0),
        source: totalClaimed ? "rpc" : "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: !totalClaimed,
        error: totalClaimed ? undefined : "Distributor not deployed",
      },
      balance: {
        value: balance || BigInt(0),
        source: balance ? "rpc" : "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: !balance,
        isStaleerror: balance ? undefined : "Distributor not deployed",
      },
    };
  } catch (error) {
    return {
      merkleRoot: {
        value: "0x0",
        source: "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: true,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      token: {
        value: "0x0",
        source: "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: true,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      totalClaimed: {
        value: BigInt(0),
        source: "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: true,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      balance: {
        value: BigInt(0),
        source: "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: true,
        error: error instanceof Error ? error.message : "Unknown error",
      },
    };
  }
}

/** Get treasury account balances */
export async function getTreasuryBalances(
  accounts: TreasuryAccount[]
): Promise<Record<string, ChainData<bigint>>> {
  const balances: Record<string, ChainData<bigint>> = {};

  for (const account of accounts) {
    balances[account.id] = await getBalance(account.address);
  }

  return balances;
}

/** Format atomic amount to MOOD */
export function formatMood(atomicAmount: bigint): string {
  const divisor = BigInt(10 ** MOOD_TOKEN.decimals);
  const whole = atomicAmount / divisor;
  const remainder = atomicAmount % divisor;

  const remainderStr = remainder.toString().padStart(MOOD_TOKEN.decimals, "0");
  const trimmed = remainderStr.replace(/0+$/, "");

  return trimmed ? `${whole}.${trimmed}` : whole.toString();
}

/** Calculate percentage of total supply */
export function calculatePercentage(
  amount: bigint,
  totalSupply: bigint
): number {
  if (totalSupply === BigInt(0)) return 0;
  return Number((amount * BigInt(10000)) / totalSupply) / 100;
}

/** Reconciliation check */
export interface ReconciliationResult {
  /** Whether reconciliation passed */
  isBalanced: boolean;
  /** Total configured balance */
  configuredTotal: bigint;
  /** Expected total supply */
  expectedTotal: bigint;
  /** Difference (should be 0) */
  difference: bigint;
  /** Warnings */
  warnings: string[];
}

/** Reconcile treasury balances against total supply */
export async function reconcileTreasury(
  balances: Record<string, ChainData<bigint>>
): Promise<ReconciliationResult> {
  const totalSupply = await getTotalSupply();
  const warnings: string[] = [];

  let configuredTotal = BigInt(0);

  for (const [id, balance] of Object.entries(balances)) {
    if (balance.error) {
      warnings.push(`Balance read failed for ${id}: ${balance.error}`);
    } else {
      configuredTotal += balance.value;
    }
  }

  const difference = totalSupply.value - configuredTotal;
  const isBalanced = difference === BigInt(0);

  if (!isBalanced) {
    warnings.push(
      `Treasury reconciliation: ${formatMood(difference)} MOOD unaccounted for`
    );
  }

  return {
    isBalanced,
    configuredTotal,
    expectedTotal: totalSupply.value,
    difference,
    warnings,
  };
}
