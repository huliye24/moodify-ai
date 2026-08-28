/**
 * MOOD-GENESIS-007: Treasury Configuration
 *
 * Single source of truth for treasury account classification.
 * Only approved public accounts are configured.
 * Safe empty-state supported.
 *
 * Safety:
 * - Read-only configuration
 * - No private keys
 * - No transfer capabilities
 */

import { MOOD_TOKEN } from "./mood-token";

/** Treasury account category */
export type TreasuryCategory =
  | "ecosystem"
  | "treasury"
  | "liquidity"
  | "contributors"
  | "team"
  | "strategic"
  | "genesis-distributor"
  | "other";

/** Control model for the account */
export type ControlModel = "EOA" | "Safe" | "Contract" | "Unknown";

/** Treasury account definition */
export interface TreasuryAccount {
  /** Unique identifier */
  id: string;
  /** Human-readable label */
  label: string;
  /** Purpose description */
  purpose: string;
  /** Chain ID (always 56 for MOOD) */
  chainId: 56;
  /** Wallet address */
  address: `0x${string}`;
  /** Account category */
  category: TreasuryCategory;
  /** Whether this account is publicly disclosed */
  public: boolean;
  /** Control model if known */
  controlModel?: ControlModel;
  /** Optional notes (public) */
  notes?: string;
}

/** Circulating supply methodology status */
export interface CirculatingSupplyMethodology {
  /** Version identifier */
  version: string;
  /** Approval status */
  status: "draft" | "approved" | "not_published";
  /** Description of methodology */
  description: string;
  /** When methodology was last updated */
  updatedAt?: string;
}

/** Treasury configuration */
export interface TreasuryConfig {
  /** Schema version */
  schema: string;
  /** Last updated timestamp */
  updatedAt: string;
  /** Approved treasury accounts */
  accounts: TreasuryAccount[];
  /** Circulating supply methodology */
  circulatingSupply: CirculatingSupplyMethodology;
  /** Known distributor addresses (Package 005) */
  distributorAddresses: `0x${string}`[];
  /** RPC endpoint for reads */
  rpcEndpoint: string;
}

/** Current treasury configuration */
export const TREASURY_CONFIG: TreasuryConfig = {
  schema: "moodify-treasury-v1",
  updatedAt: new Date().toISOString(),

  // Approved treasury accounts
  // Only populate with human-approved addresses
  accounts: [
    // Example structure (not populated until approved):
    // {
    //   id: "genesis-distributor-001",
    //   label: "Genesis Distributor",
    //   purpose: "MOOD-GENESIS-005 airdrop distribution",
    //   chainId: 56,
    //   address: "0x...",
    //   category: "genesis-distributor",
    //   public: true,
    //   controlModel: "Contract",
    //   notes: "Immutable Merkle distributor"
    // }
  ],

  // Circulating supply methodology
  circulatingSupply: {
    version: "v0.1",
    status: "not_published",
    description: "Circulating supply methodology not yet formally published. See docs/protocol/TRANSPARENCY.md for methodology status.",
  },

  // Known distributor addresses from Package 005
  distributorAddresses: [],

  // RPC endpoint for BNB Smart Chain
  rpcEndpoint: "https://bsc-dataseed.binance.org",
};

/** Get public treasury accounts */
export function getPublicTreasuryAccounts(): TreasuryAccount[] {
  return TREASURY_CONFIG.accounts.filter((account) => account.public);
}

/** Get accounts by category */
export function getAccountsByCategory(
  category: TreasuryCategory
): TreasuryAccount[] {
  return TREASURY_CONFIG.accounts.filter(
    (account) => account.category === category && account.public
  );
}

/** Validate treasury address */
export function isValidTreasuryAddress(address: string): boolean {
  if (!address.startsWith("0x")) return false;
  if (address.length !== 42) return false;
  return /^0x[0-9a-fA-F]{40}$/.test(address);
}

/** Check for duplicate addresses in config */
export function findDuplicateAddresses(): string[] {
  const seen = new Set<string>();
  const duplicates: string[] = [];

  for (const account of TREASURY_CONFIG.accounts) {
    const normalized = account.address.toLowerCase();
    if (seen.has(normalized)) {
      duplicates.push(account.address);
    }
    seen.add(normalized);
  }

  return duplicates;
}

/** Get treasury account by address */
export function getTreasuryAccountByAddress(
  address: string
): TreasuryAccount | undefined {
  const normalized = address.toLowerCase();
  return TREASURY_CONFIG.accounts.find(
    (account) => account.address.toLowerCase() === normalized
  );
}

/** Get MOOD token config */
export function getMoodTokenConfig() {
  return {
    chainId: MOOD_TOKEN.chainId,
    network: MOOD_TOKEN.network,
    name: MOOD_TOKEN.name,
    symbol: MOOD_TOKEN.symbol,
    address: MOOD_TOKEN.address as `0x${string}`,
    decimals: MOOD_TOKEN.decimals,
    totalSupply: MOOD_TOKEN.totalSupply,
    explorerUrl: MOOD_TOKEN.explorerUrl,
    tradeUrl: MOOD_TOKEN.tradeUrl,
  };
}
