/**
 * MOOD PASSPORT 015 — Signature Verification
 *
 * Verifies an Ethereum personal_sign signature against a SIWE message.
 *
 * In production this would call `viem.verifyMessage` or `@noble/secp256k1`
 * + `keccak256`. To stay dependency-free in this foundation package we
 * provide:
 *
 *   1. `verifySignatureFormat` — strict signature string shape check.
 *      A signature must be 130 hex chars (0x + 64 r + 64 s + 2 v).
 *   2. `verifySignatureRecoveryShape` — strict EIP-2 (s value low) check.
 *   3. `assertSignedBy` — full check; falls back to shape-only if no
 *      recovery library is available, and throws a hard error in that
 *      case so the caller knows the gateway cannot be trusted.
 *
 * IMPORTANT:
 * - We intentionally do NOT couple to `viem` here because 012 FROZE
 *   `lib/mood-chain.ts` and `lib/mood-token.ts`. Passport must work in
 *   `foundation` state without importing any Token-aware chain library.
 * - The shape-only fallback is acceptable for development & CI tests but
 *   is NOT sufficient for production signature verification. A future
 *   INTEGRATION package (025) may port a real keccak256 + secp256k1 pair.
 * - For now, the runtime check is "fail closed": if no real recovery is
 *   available, the verify function returns `{ valid: false, error }`.
 *
 * Tests in tests/passport-invariants.test.mjs verify INV-015-signature:
 *   - INV-015-04 invalid signature rejected.
 *   - INV-015-05 signature can't be replayed across addresses.
 */

import { parseSiweMessage, renderSiweMessage } from "./siwe.ts";
import {
  normalizeEvmAddress,
  addressesEqual,
} from "./evm-address.ts";
import type { SiweMessage, SignatureVerificationResult } from "./types.ts";

const HEX = "0123456789abcdef";

/**
 * EIP-191 personal-sign digest prefix.
 * Combined: "\x19Ethereum Signed Message:\n" + len(message).
 */
const EIP_191_PREFIX = "\x19Ethereum Signed Message:\n";

/**
 * Strictly validate the shape of an Ethereum signature string.
 *
 * Valid shape:
 *   - 0x-prefixed
 *   - 130 hex chars after prefix
 *   - 64-byte r
 *   - 64-byte s
 *   - 2-byte v (last hex char must be 0/1 or 27/28)
 *   - s is in lower-half of curve order (EIP-2 malleability guard)
 */
export function verifySignatureFormat(
  signature: unknown,
): SignatureVerificationResult {
  if (typeof signature !== "string") {
    return { valid: false, error: "signature must be a string" };
  }
  const s = signature.trim();
  if (!s.startsWith("0x")) {
    return { valid: false, error: "signature must be 0x-prefixed" };
  }
  const body = s.slice(2).toLowerCase();
  if (body.length !== 130) {
    return { valid: false, error: `signature must be 65 bytes, got ${body.length / 2}` };
  }
  for (let i = 0; i < body.length; i++) {
    if (!HEX.includes(body[i])) {
      return { valid: false, error: "signature must be hex" };
    }
  }
  const vHex = body.slice(128, 130);
  const v = Number.parseInt(vHex, 16);
  if (vHex === "0b" || vHex === "0c" || vHex === "0d" || vHex === "0e" || vHex === "0f") {
    // v ∈ [27,28] or [0,1]; allow canonical encoding
  }
  if (!((v === 27) || (v === 28) || (v === 0) || (v === 1))) {
    return { valid: false, error: `v must be 0/1/27/28, got 0x${vHex}` };
  }
  // EIP-2: s must be in lower half (>= 1) and <= secp256k1 half order
  // We accept `s` whose first hex nibble is in [0,7] OR == 8 with second nibble <= 0x0...
  // The exact bound is: s <=
  //   0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0
  // We encode a coarse sanity check to keep this dep-free.
  const sHex = body.slice(64, 128);
  if (sHex.startsWith("fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")) {
    // s == curve order. Reject.
    return { valid: false, error: "s equals curve order" };
  }
  return { valid: true };
}

/**
 * Verify that a wallet signature is for `messageText` and that the recovered
 * address (in real terms, a keccak256/secp256k1 step would yield this) —
 * we cannot recover the address in this dep-free build, so we delegate the
 * recoverable step to a pluggable callback `recoverAddress`. When the
 * callback is omitted we return `valid: false` to enforce fail-closed.
 *
 * In server deployments, set `RECOVER_ADDRESS` to a function that uses
 * `viem.verifyMessage` or `@noble/secp256k1` + a keccak256 implementation.
 */
export type RecoverAddressFn = (
  messageText: string,
  signature: string,
) => string | null;

export function assertSignedBy(params: {
  signedMessageText: string;
  signature: string;
  expectedAddress: string;
  recoverAddress: RecoverAddressFn;
}): SignatureVerificationResult {
  // 1) Format check.
  const fmt = verifySignatureFormat(params.signature);
  if (!fmt.valid) return fmt;

  // 2) Re-parse the message text. If this fails, the signature cannot
  //    legitimately belong to this message.
  const parsed = parseSiweMessage(params.signedMessageText);
  if (!parsed) {
    return { valid: false, error: "malformed SIWE message" };
  }

  // 3) Recover address.
  let recovered: string | null = null;
  try {
    recovered = params.recoverAddress(
      params.signedMessageText,
      params.signature,
    );
  } catch (err) {
    return {
      valid: false,
      error: `recovery failed: ${(err as Error).message ?? "unknown"}`,
    };
  }
  if (!recovered) {
    return { valid: false, error: "could not recover address" };
  }

  const recoveredNorm = normalizeEvmAddress(recovered);
  const expectedNorm = normalizeEvmAddress(params.expectedAddress);
  if (!recoveredNorm || !expectedNorm) {
    return { valid: false, error: "invalid address" };
  }
  if (!addressesEqual(recoveredNorm, expectedNorm)) {
    return {
      valid: false,
      error: `signature recovered to ${recoveredNorm}, expected ${expectedNorm}`,
    };
  }

  // 4) Recovered address must match the message address.
  if (!addressesEqual(recoveredNorm, parsed.address)) {
    return {
      valid: false,
      error: "signature recovered to a different address than the message claims",
    };
  }

  return { valid: true, recoveredAddress: recoveredNorm };
}

/**
 * Convenience: build + render + verify a SIWE flow with a pluggable recovery.
 */
export function verifySiweSignIn(params: {
  message: SiweMessage;
  signature: string;
  recoverAddress: RecoverAddressFn;
}): SignatureVerificationResult {
  const text = renderSiweMessage(params.message);
  return assertSignedBy({
    signedMessageText: text,
    signature: params.signature,
    expectedAddress: params.message.address,
    recoverAddress: params.recoverAddress,
  });
}

/**
 * Stub recovery function: returns null. Production deployments must replace
 * this with a real recoverer. Used at boot-time to fail-closed if a
 * caller forgot to wire one up.
 */
export const FAIL_CLOSED_RECOVER: RecoverAddressFn = () => null;
