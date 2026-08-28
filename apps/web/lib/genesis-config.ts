/* MOOD-GENESIS-002: Genesis Registration canonical configuration — single
   source of truth for protocol-level constants consumed by both server
   (`app/api/genesis/...`) and client (`app/genesis/page.tsx`). Update only with
   human confirmation; chain ID, network, and terms-version changes affect the
   signature message format and invalidate in-flight nonces. */

import { MOOD_TOKEN } from "./mood-token";

export const GENESIS_CONFIG = {
  /* Server-bound, deterministic. Mirrored from MOOD-GENESIS-001 token canon. */
  chainId: MOOD_TOKEN.chainId,
  network: MOOD_TOKEN.network,
  /* Public-facing identifier for the active message format. Bumping this value
     forces wallets to sign under a new format and rejects all in-flight
     nonces. Documented in docs/protocol/GENESIS_REGISTRATION.md. */
  signatureVersion: "mood-genesis-v1",
  /* Version identifier for the registration terms the participant is
     acknowledging. This is a version label, not the legal text itself. */
  termsVersion: "genesis-v1",
  /* Server-issued nonce lifetime. Spec recommends 5–15 minutes; 10 is the
     canonical choice. */
  nonceTtlSeconds: 600,
  /* Length of the random nonce in bytes. 16 bytes ≈ 128 bits of entropy —
     well beyond brute-force feasibility for short-lived tokens. */
  nonceByteLength: 16,
  /* Public canonical domain the participant is asked to acknowledge. Display
     only; never used for signature verification. */
  officialDomain: MOOD_TOKEN.officialSite,
  /* Maximum clock skew tolerated between client-issuedAt / expiresAt and the
     server clock when reconstructing the canonical message. Server uses its
     own clock for expiry; client values are echoed back in the signed
     message but not trusted for authorization decisions. */
  clientTimestampToleranceSeconds: 60,
} as const;

export type GenesisConfig = typeof GENESIS_CONFIG;
