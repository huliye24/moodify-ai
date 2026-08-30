/**
 * MOOD PASSPORT 015 — Index
 *
 * Public API of the Passport library.
 *
 * Consumers import from `./mood/passport` (or `./index`).
 */

export * from "./types.ts";
export { generateResidentId, isValidResidentId, formatResidentId, truncateWalletAddress, formatJoinedMonth } from "./resident-id.ts";
export { normalizeEvmAddress, checksumEvmAddress, addressesEqual, displayWalletAddress } from "./evm-address.ts";
export {
  buildSiweMessage,
  renderSiweMessage,
  parseSiweMessage,
  MOOD_SIGN_IN_STATEMENT,
  SIWE_VERSION,
  DEFAULT_NONCE_EXPIRY_MS,
} from "./siwe.ts";
export {
  verifySignatureFormat,
  assertSignedBy,
  verifySiweSignIn,
  FAIL_CLOSED_RECOVER,
} from "./signature.ts";
export { NonceRegistry, defaultNonceRegistry } from "./nonce.ts";
export { ResidentRegistry, defaultResidentRegistry } from "./resident-registry.ts";
export { Passport, defaultPassport } from "./passport.ts";
export {
  classifyPolicy,
  listActivePolicyCandidates,
} from "./policies.ts";
export {
  derivePublicProfile,
  deriveClientSession,
  displayNameOrFallback,
} from "./public-profile.ts";
