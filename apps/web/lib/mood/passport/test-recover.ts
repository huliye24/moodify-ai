/**
 * MOOD PASSPORT 015 — Test Recovery Function
 *
 * This module wires a TEST-ONLY recoverer used by the /api/identity/verify
 * route in development. It is NOT used in production:
 *
 *   - When `MOOD_PASSPORT_DEV_MODE=1`, the route uses this stub. Signatures
 *     are matched against an internal in-memory table that's seeded by the
 *     test harness. Any other signature fails.
 *   - When unset (production default), the route uses FAIL_CLOSED_RECOVER
 *     which always returns null → 401 response.
 *
 * The test recoverer is intentional. Real signature recovery requires
 * keccak256 + secp256k1, which would couple the foundation passport path to
 * token/chain libraries. 015 deliberately keeps the foundation path
 * dep-free so the launch-gate promise holds. INTEGRATION will bring a
 * real recoverer.
 */

import type { RecoverAddressFn } from "./signature.ts";

type DevSignatureRecord = {
  messageText: string;
  signature: string;
  recoveredAddress: string;
};

const devSignatures: DevSignatureRecord[] = [];

/**
 * Register a (messageText, signature) → recoveredAddress mapping.
 * In test harnesses this is called by sign-test helpers.
 */
export function registerDevSignature(record: DevSignatureRecord): void {
  devSignatures.push(record);
}

/**
 * Test-only recoverer used by /api/identity/verify when dev mode is set.
 */
export const FAKE_RECOVER_FOR_TEST: RecoverAddressFn = (messageText, signature) => {
  // Walk the in-memory table; reject everything if multiple matches disagree.
  let matched: string | null = null;
  for (const r of devSignatures) {
    if (r.messageText === messageText && r.signature === signature) {
      if (matched !== null && matched !== r.recoveredAddress) {
        return null; // disagreement → null
      }
      matched = r.recoveredAddress;
    }
  }
  return matched;
};

/**
 * Clear the dev table. Test harnesses use this in setup/teardown.
 */
export function resetDevSignatures(): void {
  devSignatures.length = 0;
}

/**
 * Read-only size, for tests.
 */
export function devSignatureCount(): number {
  return devSignatures.length;
}
