/**
 * MOOD-TREASURY-021: Treasury Model
 *
 * Canonical TypeScript model for the 021 Treasury & Transparency layer.
 *
 * This file is the SINGLE SOURCE OF TRUTH for treasury data shapes used
 * by the /treasury page and /api/protocol/treasury routes.
 *
 * Defaults reflect the HONEST inactive state:
 *   - treasuryStatus = "inactive"
 *   - no accounts configured
 *   - no assets
 *   - revenue sources are PLANNED or FUTURE / LAUNCH-GATED
 *   - liquidity / holder-rewards / token-reserve are DISABLED
 *   - no executions
 *
 * No private keys, mnemonics, seeds, or env-var references in this file.
 */

// ────────────────────────────────────────────────────────────────────────────
// Account types
// ────────────────────────────────────────────────────────────────────────────

export type TreasuryAccountType =
  | "protocol"
  | "operations"
  | "grants"
  | "liquidity"
  | "rewards"
  | "reserve"
  | "legacy";

export type TreasuryAccountStatus =
  | "inactive"
  | "observed"
  | "policy-ready"
  | "active"
  | "paused"
  | "retired";

export type ControlModel = "EOA" | "Safe" | "Multisig" | "Contract" | "Unknown";

export interface TreasuryAccountRecord {
  id: string;
  name: string;
  type: TreasuryAccountType;
  chain?: string;
  address?: string;
  status: TreasuryAccountStatus;
  public: boolean;
  controlModel?: ControlModel;
  authorityPolicy?: string;
  createdAt: string;
  updatedAt: string;
  notes?: string;
}

// ────────────────────────────────────────────────────────────────────────────
// Asset model
// ────────────────────────────────────────────────────────────────────────────

export type AssetType = "native" | "stable" | "future-mood" | "lp" | "other";

export type AssetVerificationState = "verified" | "unverified" | "unavailable";

export interface TreasuryAssetPosition {
  accountId: string;
  assetId: string;
  assetType: AssetType;
  chain?: string;
  contractAddress?: `0x${string}`;
  quantity?: string;
  valuationUsd?: string | null;
  valuationSource?: string;
  observedAt: string;
  verificationState: AssetVerificationState;
}

// ────────────────────────────────────────────────────────────────────────────
// Revenue model
// ────────────────────────────────────────────────────────────────────────────

export type RevenueSourceStatus =
  | "ACTIVE"
  | "PLANNED"
  | "FUTURE / LAUNCH-GATED";

export interface RevenueSource {
  source: string;
  status: RevenueSourceStatus;
  realizedThisPeriod?: string | null;
  notes?: string;
}

// ────────────────────────────────────────────────────────────────────────────
// Allocation model
// ────────────────────────────────────────────────────────────────────────────

export type AllocationStatus = "ENABLED" | "DISABLED";

export interface AllocationCategory {
  category: string;
  status: AllocationStatus;
  allocatedThisPeriod?: string | null;
  governanceRef?: string;
  reason?: string;
}

// ────────────────────────────────────────────────────────────────────────────
// Execution model
// ────────────────────────────────────────────────────────────────────────────

export type ExecutionAction =
  | "transfer"
  | "receive"
  | "allocate"
  | "reconcile"
  | "pause";

export type ExecutionStatus =
  | "proposed"
  | "approved"
  | "executed"
  | "failed"
  | "cancelled";

export interface TreasuryExecution {
  id: string;
  accountId: string;
  action: ExecutionAction;
  assetId?: string;
  amount?: string;
  destination?: string;
  reason: string;
  governanceRef?: string;
  actorIds: string[];
  txHash?: string;
  status: ExecutionStatus;
  createdAt: string;
  executedAt?: string;
}

// ────────────────────────────────────────────────────────────────────────────
// Reconciliation model
// ────────────────────────────────────────────────────────────────────────────

export type ReconciliationStatus =
  | "verified"
  | "mismatch"
  | "unavailable"
  | "stale";

export interface ReconciliationMismatch {
  accountId: string;
  config: string;
  rpc: string;
  cached: string;
  note?: string;
}

export interface ReconciliationReport {
  verified: number;
  mismatch: number;
  unavailable: number;
  stale: number;
  mismatches: ReconciliationMismatch[];
}

// ────────────────────────────────────────────────────────────────────────────
// Snapshot model
// ────────────────────────────────────────────────────────────────────────────

export type TreasuryActivationState =
  | "inactive"
  | "observed"
  | "policy-ready"
  | "active"
  | "paused";

export interface TreasurySnapshot {
  schema: "moodify-treasury-v1";
  generatedAt: string;
  treasuryStatus: TreasuryActivationState;
  accounts: TreasuryAccountRecord[];
  assets: TreasuryAssetPosition[];
  revenue: RevenueSource[];
  allocations: AllocationCategory[];
  executions: TreasuryExecution[];
  reconciliation: ReconciliationReport;
  risks: string[];
  governanceRefs: string[];
  notes?: string;
}

// ────────────────────────────────────────────────────────────────────────────
// Status payload (for /network)
// ────────────────────────────────────────────────────────────────────────────

export interface TreasuryStatusPayload {
  schema: "moodify-treasury-status-v1";
  generatedAt: string;
  treasuryStatus: TreasuryActivationState | "unavailable";
  verifiedAccounts: number;
  lastReport: string | null;
  lastActivity: string | null;
  economics: "Launch-Gated" | "Not Activated" | "Active";
  disabledSlots: string[];
}

// ────────────────────────────────────────────────────────────────────────────
// Defaults (v1 — honest inactive state)
// ────────────────────────────────────────────────────────────────────────────

export const DEFAULT_TREASURY_STATUS: TreasuryActivationState = "inactive";

export const DEFAULT_REVENUE_SOURCES: RevenueSource[] = [
  {
    source: "Protocol Service Revenue",
    status: "PLANNED",
    realizedThisPeriod: null,
    notes: "No production traffic yet.",
  },
  {
    source: "Application Revenue",
    status: "PLANNED",
    realizedThisPeriod: null,
    notes: "Application shell exists; no paid features.",
  },
  {
    source: "API Revenue",
    status: "PLANNED",
    realizedThisPeriod: null,
    notes: "Read-only public APIs; no paid tier.",
  },
  {
    source: "Node Fees",
    status: "PLANNED",
    realizedThisPeriod: null,
    notes: "Node registry exists; fees not collected.",
  },
  {
    source: "Donations",
    status: "PLANNED",
    realizedThisPeriod: null,
    notes: "Support intents schema exists; no settlement yet.",
  },
  {
    source: "Grants",
    status: "PLANNED",
    realizedThisPeriod: null,
    notes: "Contribution reward system exists; rewards not token-distributed.",
  },
  {
    source: "Future Trading Tax",
    status: "FUTURE / LAUNCH-GATED",
    realizedThisPeriod: null,
    notes: "Blocked until Token Launch Gate (024/025).",
  },
  {
    source: "Future Holder Reward Pool",
    status: "FUTURE / LAUNCH-GATED",
    realizedThisPeriod: null,
    notes: "Blocked until Token Launch Gate (024/025).",
  },
  {
    source: "Future Liquidity Yield",
    status: "FUTURE / LAUNCH-GATED",
    realizedThisPeriod: null,
    notes: "Blocked until Token Launch Gate (024/025).",
  },
];

export const DEFAULT_ALLOCATION_CATEGORIES: AllocationCategory[] = [
  { category: "Protocol Development", status: "ENABLED" },
  { category: "Infrastructure", status: "ENABLED" },
  { category: "Security", status: "ENABLED" },
  { category: "Research", status: "ENABLED" },
  { category: "Community", status: "ENABLED" },
  { category: "Grants", status: "ENABLED" },
  { category: "Operations", status: "ENABLED" },
  { category: "Reserve", status: "ENABLED" },
  {
    category: "Liquidity",
    status: "DISABLED",
    reason: "Launch-gated (024/025)",
  },
  {
    category: "Holder Rewards",
    status: "DISABLED",
    reason: "Launch-gated (024/025)",
  },
  {
    category: "Token Reserve",
    status: "DISABLED",
    reason: "Launch-gated (024/025)",
  },
];

export const DEFAULT_DISABLED_SLOTS: string[] = [
  "liquidity",
  "holder-rewards",
  "token-reserve",
];

export const DEFAULT_RISKS: string[] = [
  "Single-operator custody (v1 is process-transparent, not multi-sig)",
  "No approved valuation oracle",
  "Circulating supply methodology not yet published",
  "Treasury inactive — no execution authority available",
  "All token economics launch-gated until 024/025",
];

export const DEFAULT_GOVERNANCE_REFS: string[] = [
  "docs/mood/governance/020_FINAL_REPORT.md",
  "docs/mood/governance/020_AUTHORITY_MODEL.md",
  "docs/mood/treasury/021_TREASURY_POLICY.md",
];

// ────────────────────────────────────────────────────────────────────────────
// Snapshot builder
// ────────────────────────────────────────────────────────────────────────────

/**
 * Build the canonical Treasury snapshot.
 *
 * In v1, this returns the HONEST inactive state. There are no real
 * treasury accounts, no assets, no executions. This is by design.
 */
export function buildTreasurySnapshot(
  overrides: Partial<TreasurySnapshot> = {}
): TreasurySnapshot {
  const now = new Date().toISOString();
  return {
    schema: "moodify-treasury-v1",
    generatedAt: now,
    treasuryStatus: DEFAULT_TREASURY_STATUS,
    accounts: [],
    assets: [],
    revenue: DEFAULT_REVENUE_SOURCES,
    allocations: DEFAULT_ALLOCATION_CATEGORIES,
    executions: [],
    reconciliation: {
      verified: 0,
      mismatch: 0,
      unavailable: 0,
      stale: 0,
      mismatches: [],
    },
    risks: DEFAULT_RISKS,
    governanceRefs: DEFAULT_GOVERNANCE_REFS,
    notes:
      "Treasury is currently in inactive state. No real protocol-controlled funds exist. " +
      "Activation requires an accepted MIP and explicit human approval.",
    ...overrides,
  };
}

/**
 * Build the minimal status payload for /network.
 */
export function buildTreasuryStatusPayload(): TreasuryStatusPayload {
  return {
    schema: "moodify-treasury-status-v1",
    generatedAt: new Date().toISOString(),
    treasuryStatus: DEFAULT_TREASURY_STATUS,
    verifiedAccounts: 0,
    lastReport: null,
    lastActivity: null,
    economics: "Launch-Gated",
    disabledSlots: DEFAULT_DISABLED_SLOTS,
  };
}
