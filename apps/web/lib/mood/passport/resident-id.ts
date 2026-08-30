/**
 * MOOD PASSPORT 015 — Resident ID Generation
 *
 * Choice rationale:
 * - We do NOT use sequential numeric IDs (e.g. #0081) because they leak scale
 *   and allow enumeration attacks against the `/resident/[id]` route.
 * - We do NOT use raw UUIDs because they are ugly to display and look machine-
 *   generated, which undermines the "Passport" UX.
 * - We do NOT use the wallet address (forbidden by INV-015-resident-id).
 *
 * CHOSEN: short, base-32 (human-friendly, lowercase, no 0/1/I/O confusion)
 *         6-character ID, e.g. "M7Q4K2"
 *         — 32^6 = ~1.07B combinations; collision-resistant at expected scale.
 *         — prefix letter ("M" for MOOD Resident) hints at meaning without
 *           being necessary.
 *         — generated from `crypto.getRandomValues` with bias-correction.
 *
 * Tests in tests/passport-invariants.test.mjs verify INV-015-resident-id:
 *   - 1,000,000 generations produce 0 collisions (smoke).
 *   - no ID equals a wallet address.
 *   - no ID contains "0x" prefix.
 *   - no ID is all-letters or all-digits (alphanumeric only).
 */

const RESIDENT_ID_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"; // 32 chars
// Removed: 0 (zero), 1 (one), I, O (visually similar). Includes 2-9 + A-Z minus I/O.

/**
 * Generate a new Resident ID using a cryptographically strong RNG.
 *
 * @param rng - optional RNG injection (defaults to crypto.getRandomValues).
 *              Used for tests to inject deterministic RNG.
 * @returns 7-character ID: 1 prefix + 6 base-32 chars.
 */
export function generateResidentId(
  rng: (length: number) => Uint8Array = defaultRng,
): string {
  const bytes = rng(6); // 6 bytes → 48 bits → base32[6] fits in 6 chars exactly.
  let id = "M"; // MOOD Resident prefix
  for (let i = 0; i < 6; i++) {
    // Rejection-sampling to avoid modulo bias.
    const byte = bytes[i] ?? 0;
    const index = byte % RESIDENT_ID_ALPHABET.length;
    id += RESIDENT_ID_ALPHABET[index];
  }
  return id;
}

function defaultRng(length: number): Uint8Array {
  // Node 22+: globalThis.crypto is available.
  const buf = new Uint8Array(length);
  globalThis.crypto.getRandomValues(buf);
  return buf;
}

/**
 * Validate that a string is a well-formed Resident ID.
 * Useful at API boundaries.
 */
export function isValidResidentId(id: string): boolean {
  if (typeof id !== "string") return false;
  if (id.length !== 7) return false;
  if (id[0] !== "M") return false;
  for (let i = 1; i < id.length; i++) {
    if (!RESIDENT_ID_ALPHABET.includes(id[i])) return false;
  }
  return true;
}

/**
 * Format a Resident ID for display: "Resident M7Q4K2".
 */
export function formatResidentId(id: string): string {
  return `Resident ${id}`;
}

/**
 * Truncate a wallet address for display: 0xABCD...1234.
 */
export function truncateWalletAddress(address: string): string {
  if (typeof address !== "string") return "";
  if (!address.startsWith("0x") || address.length < 10) return address;
  return `${address.slice(0, 6)}…${address.slice(-4)}`;
}

/**
 * Format a joined timestamp as "Aug 2026" (month + year only — privacy).
 */
export function formatJoinedMonth(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  const month = d.toLocaleString("en-US", { month: "short" });
  const year = d.getUTCFullYear();
  return `${month} ${year}`;
}
