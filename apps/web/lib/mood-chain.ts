/**
 * MOOD-GENESIS-007: Read-Only Chain Service
 *
 * Typed reads for on-chain MOOD data.
 * No signer required.
 * No write capabilities.
 */

import { MOOD_TOKEN } from "./mood-token";
import { TREASURY_CONFIG, TreasuryAccount } from "./mood-treasury";

/** RPC configuration */
const RPC_ENDPOINT = TREASURY_CONFIG.rpcEndpoint;

/** BEP-20 token ABI (read-only) */
const TOKEN_ABI = [
  // totalSupply
  {
    constant: true,
    inputs: [],
    name: "totalSupply",
    outputs: [{ name: "", type: "uint256" }],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  // balanceOf
  {
    constant: true,
    inputs: [{ name: "account", type: "address" }],
    name: "balanceOf",
    outputs: [{ name: "", type: "uint256" }],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
  // decimals
  {
    constant: true,
    inputs: [],
    name: "decimals",
    outputs: [{ name: "", type: "uint8" }],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
];

/** Distributor ABI (read-only) */
const DISTRIBUTOR_ABI = [
  // merkleRoot
  {
    inputs: [],
    name: "merkleRoot",
    outputs: [{ name: "", type: "bytes32" }],
    stateMutability: "view",
    type: "function",
  },
  // token
  {
    inputs: [],
    name: "token",
    outputs: [{ name: "", type: "address" }],
    stateMutability: "view",
    type: "function",
  },
  // claimedParticipant
  {
    inputs: [{ name: "participantNumber", type: "uint256" }],
    name: "claimedParticipant",
    outputs: [{ name: "", type: "bool" }],
    stateMutability: "view",
    type: "function",
  },
  // totalClaimed
  {
    inputs: [],
    name: "totalClaimed",
    outputs: [{ name: "", type: "uint256" }],
    stateMutability: "view",
    type: "function",
  },
  // distributorBalance
  {
    inputs: [],
    name: "distributorBalance",
    outputs: [{ name: "", type: "uint256" }],
    stateMutability: "view",
    type: "function",
  },
];

/** RPC call payload */
interface RPCCall {
  jsonrpc: "2.0";
  method: string;
  params: unknown[];
  id: number;
}

/** RPC response */
interface RPCResponse {
  jsonrpc: "2.0";
  id: number;
  result?: string;
  error?: {
    code: number;
    message: string;
  };
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

/** Make RPC call */
async function makeRPCCall(call: RPCCall): Promise<RPCResponse> {
  try {
    const response = await fetch(RPC_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(call),
    });

    if (!response.ok) {
      throw new ChainReadError(
        "RPC_HTTP_ERROR",
        `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    throw new ChainReadError(
      "RPC_NETWORK_ERROR",
      error instanceof Error ? error.message : "Network error"
    );
  }
}

/** Encode function call */
function encodeCall(signature: string, params: string[]): string {
  // Simple encoder for common function signatures
  // In production, use ethers.js or viem
  const hash = signature; // Placeholder - would use proper ABI encoding
  return hash;
}

/** Decode uint256 result */
function decodeUint256(hex: string): bigint {
  return BigInt(hex);
}

/** Get total supply */
export async function getTotalSupply(): Promise<ChainData<bigint>> {
  try {
    // Using eth_call for totalSupply
    const callData = "0x18160ddd"; // totalSupply() selector

    const response = await makeRPCCall({
      jsonrpc: "2.0",
      method: "eth_call",
      params: [
        {
          to: MOOD_TOKEN.address,
          data: callData,
        },
        "latest",
      ],
      id: 1,
    });

    if (response.error) {
      throw new ChainReadError(
        "RPC_CALL_ERROR",
        response.error.message,
        { code: response.error.code }
      );
    }

    const value = decodeUint256(response.result || "0x0");

    return {
      value,
      source: "rpc",
      updatedAt: new Date().toISOString(),
      isStale: false,
    };
  } catch (error) {
    // Fallback to config value
    return {
      value: BigInt(MOOD_TOKEN.totalSupply) * BigInt(10 ** MOOD_TOKEN.decimals),
      source: "config",
      updatedAt: new Date().toISOString(),
      isStale: true,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/** Get balance of address */
export async function getBalance(address: string): Promise<ChainData<bigint>> {
  try {
    // balanceOf(address) selector + padded address
    const selector = "0x70a08231";
    const paddedAddress = address.toLowerCase().replace("0x", "").padStart(64, "0");
    const callData = selector + paddedAddress;

    const response = await makeRPCCall({
      jsonrpc: "2.0",
      method: "eth_call",
      params: [
        {
          to: MOOD_TOKEN.address,
          data: callData,
        },
        "latest",
      ],
      id: 2,
    });

    if (response.error) {
      throw new ChainReadError(
        "RPC_CALL_ERROR",
        response.error.message,
        { code: response.error.code }
      );
    }

    const value = decodeUint256(response.result || "0x0");

    return {
      value,
      source: "rpc",
      updatedAt: new Date().toISOString(),
      isStale: false,
    };
  } catch (error) {
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
    // This would make multiple eth_calls in parallel
    // For now, return unavailable state
    return {
      merkleRoot: {
        value: "0x0",
        source: "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: true,
        error: "Distributor reads not implemented",
      },
      token: {
        value: "0x0",
        source: "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: true,
        error: "Distributor reads not implemented",
      },
      totalClaimed: {
        value: BigInt(0),
        source: "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: true,
        error: "Distributor reads not implemented",
      },
      balance: {
        value: BigInt(0),
        source: "unavailable",
        updatedAt: new Date().toISOString(),
        isStale: true,
        error: "Distributor reads not implemented",
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
