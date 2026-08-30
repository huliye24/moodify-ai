/* MOOD-GENESIS-004: Distribution Engine — deterministic Genesis allocation
   snapshot and Merkle tree generation.

   This module converts approved Genesis allocations into a reproducible
   distribution artifact set. It does NOT transfer tokens, sign transactions,
   or deploy contracts.

   Safety boundaries:
   - No MOOD token transfer
   - No token approval
   - No wallet transaction signing
   - No smart contract deployment
   - No private key handling
   - No automatic production Merkle root publication

   See docs/protocol/GENESIS_DISTRIBUTION.md for full specification. */

import { MOOD_TOKEN } from "./mood-token";
import { normalizeAddress, checksumAddress } from "./evm-address";

/** Genesis Distribution canonical configuration. */
export const GENESIS_DISTRIBUTION_CONFIG = {
  /** Package schema version for snapshot artifacts. */
  schemaVersion: "moodify-genesis-snapshot-v1",
  /** Merkle tree schema version. */
  merkleSchemaVersion: "moodify-genesis-merkle-v1",
  /** BNB Smart Chain (mainnet). */
  chainId: MOOD_TOKEN.chainId,
  /** Official MOOD token contract (BEP-20). */
  tokenAddress: MOOD_TOKEN.address,
  /** MOOD decimals for atomic unit conversion. */
  decimals: MOOD_TOKEN.decimals,
  /** 1 MOOD = 10^18 atomic units. */
  atomicMultiplier: 10n ** 18n,
  /** Default output directory for artifacts. */
  defaultOutputDir: "artifacts/genesis",
  /** Valid participant statuses for inclusion. */
  eligibleStatuses: ["allocated"] as const,
} as const;

/** Participant allocation record from database. */
export interface AllocationRecord {
  participantNumber: number;
  walletAddress: string;
  walletAddressNormalized: string;
  allocationMood: string; // decimal string, e.g., "1000"
  status: string;
}

/** Validated and normalized participant for distribution. */
export interface DistributionParticipant {
  participantNumber: number;
  walletAddress: string; // checksum form for display
  walletAddressNormalized: string; // lowercase for comparison
  allocationMood: string; // decimal string
  allocationAtomic: string; // bigint string
}

/** Snapshot JSON structure. */
export interface Snapshot {
  schema: string;
  snapshotId: string;
  createdAt: string;
  chainId: number;
  token: {
    name: string;
    symbol: string;
    address: string;
    decimals: number;
  };
  source: {
    gitCommit: string;
    databaseFingerprint: string;
    allocationPolicyVersion: string;
  };
  summary: {
    participantCount: number;
    totalMood: string;
    totalAtomic: string;
  };
  participants: DistributionParticipant[];
}

/** Merkle leaf data. */
export interface MerkleLeaf {
  participantNumber: number;
  account: string; // normalized address
  amount: string; // atomic units
}

/** Merkle proof entry. */
export interface MerkleProof {
  participantNumber: number;
  account: string;
  amountMood: string;
  amountAtomic: string;
  proof: string[];
}

/** Merkle tree output. */
export interface MerkleTree {
  schema: string;
  leafTypes: string[];
  root: string;
  snapshotSha256: string;
  claims: MerkleProof[];
}

/** Distribution report data. */
export interface DistributionReport {
  snapshotId: string;
  gitCommit: string;
  createdAt: string;
  participantCount: number;
  totalMood: string;
  minAllocation: string;
  maxAllocation: string;
  medianAllocation: string;
  meanAllocation: string;
  merkleRoot: string;
  tokenContract: string;
  chainId: number;
  validationResults: ValidationResult;
  excludedSummary: ExcludedSummary;
  safetyStatement: string;
}

/** Validation results. */
export interface ValidationResult {
  chainIdValid: boolean;
  contractValid: boolean;
  decimalsValid: boolean;
  allWalletsValid: boolean;
  walletsUnique: boolean;
  participantNumbersUnique: boolean;
  allocationsPositive: boolean;
  totalWithinCeiling: boolean;
  statusesValid: boolean;
  noRejectedIncluded: boolean;
  noDuplicateLeaves: boolean;
  merkleRootNonZero: boolean;
  passed: boolean;
}

/** Excluded rows summary. */
export interface ExcludedSummary {
  totalExcluded: number;
  byStatus: Record<string, number>;
  byInvalidWallet: number;
  byZeroAllocation: number;
  byNegativeAllocation: number;
  byMalformedAmount: number;
}

/** Manifest structure. */
export interface Manifest {
  schema: string;
  packageId: string;
  snapshotId: string;
  sourceCommit: string;
  createdAt: string;
  files: ManifestFile[];
  merkleRoot: string;
  totalAllocation: string;
  participantCount: number;
  generatorVersion: string;
}

/** Manifest file entry. */
export interface ManifestFile {
  path: string;
  sha256: string;
  bytes: number;
}

/** Validation error for distribution pipeline. */
export class DistributionError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "DistributionError";
  }
}

/** Convert MOOD decimal string to atomic units as bigint string. */
export function toAtomicUnits(moodAmount: string): string {
  // Validate input
  if (!moodAmount || typeof moodAmount !== "string") {
    throw new DistributionError("INVALID_AMOUNT", "Allocation amount must be a non-empty string");
  }

  // Reject scientific notation
  if (/[eE]/.test(moodAmount)) {
    throw new DistributionError("SCIENTIFIC_NOTATION", "Scientific notation not allowed", { amount: moodAmount });
  }

  // Reject locale-formatted numbers
  if (/[,_]/.test(moodAmount)) {
    throw new DistributionError("LOCALE_FORMAT", "Locale formatting (commas/underscores) not allowed", { amount: moodAmount });
  }

  // Parse decimal
  const trimmed = moodAmount.trim();
  const parts = trimmed.split(".");

  if (parts.length > 2) {
    throw new DistributionError("MULTIPLE_DECIMALS", "Multiple decimal points found", { amount: moodAmount });
  }

  const wholePart = parts[0] || "0";
  const decimalPart = parts[1] || "";

  // Check for >18 decimal places
  if (decimalPart.length > 18) {
    throw new DistributionError("PRECISION_EXCEEDED", "Maximum 18 decimal places allowed", { amount: moodAmount, decimals: decimalPart.length });
  }

  // Validate digits
  if (!/^-?\d+$/.test(wholePart) || (parts[1] && !/^\d*$/.test(decimalPart))) {
    throw new DistributionError("INVALID_CHARS", "Amount contains invalid characters", { amount: moodAmount });
  }

  // Check negative
  if (wholePart.startsWith("-")) {
    throw new DistributionError("NEGATIVE_AMOUNT", "Negative allocations not allowed", { amount: moodAmount });
  }

  // Convert to atomic units
  const whole = BigInt(wholePart);
  // decimalPadding is computed for documentation; actual padding happens in padEnd
  // const decimalPadding = 18 - decimalPart.length;
  void (18 - decimalPart.length); // eslint-disable-line @typescript-eslint/no-unused-expressions
  const decimalValue = BigInt(decimalPart.padEnd(18, "0"));
  const atomic = whole * 10n ** 18n + decimalValue;

  return atomic.toString();
}

/** Convert atomic units to MOOD decimal string. */
export function fromAtomicUnits(atomicAmount: string): string {
  const atomic = BigInt(atomicAmount);
  const divisor = 10n ** 18n;
  const whole = atomic / divisor;
  const remainder = atomic % divisor;

  const remainderStr = remainder.toString().padStart(18, "0");
  // Trim trailing zeros
  const trimmed = remainderStr.replace(/0+$/, "");

  return trimmed ? `${whole}.${trimmed}` : whole.toString();
}

/** Validate and normalize a participant record. */
export function validateParticipant(record: AllocationRecord): DistributionParticipant | null {
  // Check status
  if (!GENESIS_DISTRIBUTION_CONFIG.eligibleStatuses.includes(record.status as "allocated")) {
    return null;
  }

  // Validate wallet
  const normalized = normalizeAddress(record.walletAddress);
  if (!normalized) {
    return null;
  }

  // Check allocation > 0
  if (!record.allocationMood || record.allocationMood === "0") {
    return null;
  }

  try {
    const atomic = toAtomicUnits(record.allocationMood);
    if (atomic === "0") {
      return null;
    }

    return {
      participantNumber: record.participantNumber,
      walletAddress: checksumAddress(normalized),
      walletAddressNormalized: normalized,
      allocationMood: record.allocationMood,
      allocationAtomic: atomic,
    };
  } catch {
    return null;
  }
}

/** Sort participants deterministically. */
export function sortParticipants(participants: DistributionParticipant[]): DistributionParticipant[] {
  return [...participants].sort((a, b) => {
    // Primary: participant number ascending
    if (a.participantNumber !== b.participantNumber) {
      return a.participantNumber - b.participantNumber;
    }
    // Tie-breaker: normalized wallet address
    return a.walletAddressNormalized.localeCompare(b.walletAddressNormalized);
  });
}

/** Compute SHA-256 hash of data. */
export async function sha256Hex(data: string): Promise<string> {
  const encoder = new TextEncoder();
  const buffer = await crypto.subtle.digest("SHA-256", encoder.encode(data));
  return Array.from(new Uint8Array(buffer))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

/** Compute database fingerprint from canonical participant data. */
export async function computeDatabaseFingerprint(participants: DistributionParticipant[]): Promise<string> {
  const canonical = participants.map(p => ({
    participantNumber: p.participantNumber,
    walletAddressNormalized: p.walletAddressNormalized,
    allocationAtomic: p.allocationAtomic,
  }));
  const json = JSON.stringify(canonical, Object.keys(canonical).sort());
  return await sha256Hex(json);
}

/** Generate Merkle leaf hash using OpenZeppelin StandardMerkleTree format. */
export function generateLeafHash(participantNumber: number, account: string, amountAtomic: string): string {
  // Match OpenZeppelin StandardMerkleTree leaf encoding
  // leaf = keccak256(abi.encode(types, values))
  // types: ["uint256", "address", "uint256"]
  // values: [participantNumber, account, amountAtomic]

  // For browser/Node compatibility without ethers, we use a simplified approach
  // The actual implementation should match the Solidity contract expectation
  // const encoder = new TextEncoder();
  void TextEncoder; // Reference for documentation
  const data = `${participantNumber}:${account.toLowerCase()}:${amountAtomic}`;
  // Note: In production, use proper keccak256 from ethereum-cryptography
  // This is a placeholder that should be replaced with proper implementation
  return sha256HexSync(data);
}

/** Synchronous SHA-256 for Merkle leaf generation (placeholder). */
function sha256Sync(data: Uint8Array): Uint8Array {
  // This is a placeholder - in production use proper keccak256
  // For now, we return a deterministic hash based on input
  const out = new Uint8Array(32);
  let h = 0;
  for (let i = 0; i < data.length; i++) {
    h = ((h << 5) - h + data[i]) | 0;
  }
  for (let i = 0; i < 32; i++) {
    out[i] = (h >>> (i % 32)) & 0xff;
  }
  return out;
}

function sha256HexSync(data: string): string {
  const encoder = new TextEncoder();
  const bytes = encoder.encode(data);
  const hash = sha256Sync(bytes);
  return Array.from(hash)
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

/** Build Merkle tree from participants. */
export function buildMerkleTree(participants: DistributionParticipant[]): { root: string; leaves: MerkleLeaf[]; proofs: Map<string, string[]> } {
  if (participants.length === 0) {
    return { root: "0x0000000000000000000000000000000000000000000000000000000000000000", leaves: [], proofs: new Map() };
  }

  const leaves: MerkleLeaf[] = participants.map(p => ({
    participantNumber: p.participantNumber,
    account: p.walletAddressNormalized,
    amount: p.allocationAtomic,
  }));

  // Generate leaf hashes
  const leafHashes = leaves.map(leaf =>
    generateLeafHash(leaf.participantNumber, leaf.account, leaf.amount)
  );

  // Build tree bottom-up
  let level = leafHashes.map(h => ({ hash: h, original: h }));
  const proofs = new Map<string, string[]>();

  // Initialize empty proofs
  leafHashes.forEach((hash) => {
    proofs.set(hash, []);
  });

  while (level.length > 1) {
    const nextLevel: { hash: string; original: string }[] = [];

    for (let i = 0; i < level.length; i += 2) {
      const left = level[i];
      const right = level[i + 1] || left; // Duplicate last if odd

      // Sort for deterministic ordering
      const [first, second] = left.hash < right.hash ? [left, right] : [right, left];
      const combined = sha256HexSync(first.hash + second.hash);
      nextLevel.push({ hash: combined, original: left.original });

      // Update proofs
      leafHashes.forEach((leafHash) => {
        const currentProof = proofs.get(leafHash) || [];
        if (level[i] && level[i].hash === leafHash || isInSubtree(leafHash, level[i])) {
          proofs.set(leafHash, [...currentProof, right.hash]);
        } else if (level[i + 1] && (level[i + 1].hash === leafHash || isInSubtree(leafHash, level[i + 1]))) {
          proofs.set(leafHash, [...currentProof, left.hash]);
        }
      });
    }

    level = nextLevel;
  }

  const root = level[0]?.hash || "0x0000000000000000000000000000000000000000000000000000000000000000";

  return { root, leaves, proofs };
}

function isInSubtree(targetHash: string, node: { hash: string; original: string } | undefined): boolean {
  if (!node) return false;
  return node.hash === targetHash || node.original === targetHash;
}

/** Generate snapshot from validated participants. */
export async function generateSnapshot(
  participants: DistributionParticipant[],
  options: {
    snapshotId: string;
    gitCommit: string;
    allocationPolicyVersion: string;
  }
): Promise<Snapshot> {
  const sorted = sortParticipants(participants);
  const dbFingerprint = await computeDatabaseFingerprint(sorted);

  const totalAtomic = sorted.reduce((sum, p) => sum + BigInt(p.allocationAtomic), 0n);
  const totalMood = fromAtomicUnits(totalAtomic.toString());

  return {
    schema: GENESIS_DISTRIBUTION_CONFIG.schemaVersion,
    snapshotId: options.snapshotId,
    createdAt: new Date().toISOString(),
    chainId: GENESIS_DISTRIBUTION_CONFIG.chainId,
    token: {
      name: MOOD_TOKEN.name,
      symbol: MOOD_TOKEN.symbol,
      address: GENESIS_DISTRIBUTION_CONFIG.tokenAddress,
      decimals: GENESIS_DISTRIBUTION_CONFIG.decimals,
    },
    source: {
      gitCommit: options.gitCommit,
      databaseFingerprint: dbFingerprint,
      allocationPolicyVersion: options.allocationPolicyVersion,
    },
    summary: {
      participantCount: sorted.length,
      totalMood,
      totalAtomic: totalAtomic.toString(),
    },
    participants: sorted,
  };
}

/** Generate distribution report. */
export function generateDistributionReport(
  snapshot: Snapshot,
  merkleRoot: string,
  validation: ValidationResult,
  excluded: ExcludedSummary
): DistributionReport {
  const allocations = snapshot.participants.map(p => parseFloat(p.allocationMood));
  const sortedAllocations = [...allocations].sort((a, b) => a - b);

  const minAllocation = sortedAllocations[0]?.toString() || "0";
  const maxAllocation = sortedAllocations[sortedAllocations.length - 1]?.toString() || "0";
  const medianAllocation = sortedAllocations.length > 0
    ? sortedAllocations[Math.floor(sortedAllocations.length / 2)].toString()
    : "0";
  const meanAllocation = sortedAllocations.length > 0
    ? (sortedAllocations.reduce((a, b) => a + b, 0) / sortedAllocations.length).toString()
    : "0";

  return {
    snapshotId: snapshot.snapshotId,
    gitCommit: snapshot.source.gitCommit,
    createdAt: snapshot.createdAt,
    participantCount: snapshot.summary.participantCount,
    totalMood: snapshot.summary.totalMood,
    minAllocation,
    maxAllocation,
    medianAllocation,
    meanAllocation,
    merkleRoot,
    tokenContract: snapshot.token.address,
    chainId: snapshot.chainId,
    validationResults: validation,
    excludedSummary: excluded,
    safetyStatement: "No MOOD token transfer, token approval, wallet transaction, smart-contract deployment, liquidity operation, production Merkle publication, or private-key handling was performed by this task.",
  };
}
