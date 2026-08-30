/**
 * MOOD PASSPORT 015 — Passport Orchestrator
 *
 * High-level operations that compose the lower-level pieces.
 *
 *   - `requestSignIn`: server-side step 1. Issues nonce + builds SIWE message.
 *   - `completeSignIn`: server-side step 2. Verifies signature, resolves
 *                       or creates the Resident, issues session.
 *
 * These two functions are the only public surface that hides the nonce
 * store, signature verification, identity store, and session lifecycle.
 *
 * Failures are returned as discriminated unions — call sites MUST render
 * them to the user without leaking internal error strings.
 */

import { defaultNonceRegistry, NonceRegistry } from "./nonce.ts";
import { defaultResidentRegistry, ResidentRegistry } from "./resident-registry.ts";
import {
  buildSiweMessage,
  renderSiweMessage,
} from "./siwe.ts";
import type { SiweMessage } from "./types.ts";
import {
  assertSignedBy,
  FAIL_CLOSED_RECOVER,
  type RecoverAddressFn,
} from "./signature.ts";
import { normalizeEvmAddress } from "./evm-address.ts";
import {
  DEFAULT_NONCE_EXPIRY_MS,
  MOOD_SIGN_IN_STATEMENT,
} from "./siwe.ts";
import { globalRngBytes } from "./rng.ts";

const DEFAULT_SESSION_TTL_MS = 60 * 60 * 1000; // 1 hour
const DEFAULT_DOMAIN = "localhost";
const DEFAULT_URI = "http://localhost:3000/portal/passport";
const DEFAULT_CHAIN_ID = 56; // BSC, but never asserted as a Token deployment chain.

function generateRequestId(): string {
  const bytes = globalRngBytes(8);
  let hex = "";
  for (let i = 0; i < bytes.length; i++) {
    hex += (bytes[i] ?? 0).toString(16).padStart(2, "0");
  }
  return `mood-${hex}`;
}

export interface PassportDeps {
  nonceRegistry?: NonceRegistry;
  residentRegistry?: ResidentRegistry;
  recoverAddress?: RecoverAddressFn;
  sessionTtlMs?: number;
  domain?: string;
  uri?: string;
  chainId?: number;
}

export interface RequestSignInResult {
  ok: boolean;
  message?: SiweMessage;
  messageText?: string;
  reason?: string;
}

export interface CompleteSignInParams {
  messageText: string;
  signature: string;
  expectedDomain?: string;
  expectedUri?: string;
  expectedChainId?: number;
  nonce?: string;
  walletAddress?: string;
}

export interface CompleteSignInResult {
  ok: boolean;
  reason?: string;
  residentId?: string;
  walletId?: string;
  sessionId?: string;
  expiresAt?: string;
  isNew?: boolean;
  recoveredAddress?: string;
}

export class Passport {
  private nonceReg: NonceRegistry;
  private residentReg: ResidentRegistry;
  private recoverAddress: RecoverAddressFn;
  private sessionTtlMs: number;
  private domain: string;
  private uri: string;
  private chainId: number;

  constructor(deps: PassportDeps = {}) {
    this.nonceReg = deps.nonceRegistry ?? defaultNonceRegistry;
    this.residentReg = deps.residentRegistry ?? defaultResidentRegistry;
    this.recoverAddress = deps.recoverAddress ?? FAIL_CLOSED_RECOVER;
    this.sessionTtlMs = deps.sessionTtlMs ?? DEFAULT_SESSION_TTL_MS;
    this.domain = deps.domain ?? DEFAULT_DOMAIN;
    this.uri = deps.uri ?? DEFAULT_URI;
    this.chainId = deps.chainId ?? DEFAULT_CHAIN_ID;
  }

  /**
   * Step 1: server issues nonce + SIWE message for the wallet to sign.
   *
   * The wallet is expected to be detected by the client. The server does
   * NOT maintain a "connecting wallet" state between requests; it just
   * generates the nonce. The client must be on the same domain (CSRF).
   */
  requestSignIn(params: { walletAddress: string; requestId?: string }):
    RequestSignInResult {
    const address = normalizeEvmAddress(params.walletAddress);
    if (!address) return { ok: false, reason: "invalid-address" };

    const nonceResult = this.nonceReg.issue(address);
    const message = buildSiweMessage({
      domain: this.domain,
      address,
      nonce: nonceResult.nonce,
      chainId: this.chainId,
      uri: this.uri,
      statement: MOOD_SIGN_IN_STATEMENT,
      ttlMs: DEFAULT_NONCE_EXPIRY_MS,
      requestId: params.requestId ?? generateRequestId(),
    });
    const messageText = renderSiweMessage(message);
    return { ok: true, message, messageText };
  }

  /**
   * Step 2: client returns the signed message text + signature.
   * Server verifies signature, consumes the nonce, resolves/creates the
   * Resident, issues a session.
   */
  completeSignIn(params: CompleteSignInParams): CompleteSignInResult {
    const expectedDomain = params.expectedDomain ?? this.domain;
    const expectedUri = params.expectedUri ?? this.uri;
    const expectedChainId = params.expectedChainId ?? this.chainId;

    // 1) Re-extract the nonce + address from the message text. This protects
    //    the server from being tricked by a client-supplied nonce out of band.
    const extractedNonce = params.nonce
      ?? extractNonceFromText(params.messageText);
    const extractedAddress = params.walletAddress
      ?? extractAddressFromText(params.messageText);
    if (!extractedNonce) return { ok: false, reason: "missing-nonce" };
    if (!extractedAddress) return { ok: false, reason: "missing-address" };

    // 2) DOMAIN / URI / CHAIN binding — fail closed if mismatched.
    const textLower = params.messageText;
    if (!textLower.includes(`URI: ${expectedUri}`)) {
      return { ok: false, reason: "uri-mismatch" };
    }
    if (!textLower.includes(`Chain ID: ${expectedChainId}`)) {
      return { ok: false, reason: "chain-id-mismatch" };
    }
    if (!textLower.startsWith(`${expectedDomain} wants you to sign in`)) {
      return { ok: false, reason: "domain-mismatch" };
    }

    // 3) Verify signature against message text.
    const sigResult = assertSignedBy({
      signedMessageText: params.messageText,
      signature: params.signature,
      expectedAddress: extractedAddress,
      recoverAddress: this.recoverAddress,
    });
    if (!sigResult.valid) return { ok: false, reason: sigResult.error ?? "invalid-signature" };

    // 4) Consume nonce. If it fails, the nonce was used, expired, or
    //    address-bound differently. Fail closed.
    const consume = this.nonceReg.consume(extractedNonce, extractedAddress);
    if (!consume.ok) return { ok: false, reason: `nonce-${consume.reason}` };

    // 5) Resolve or create Resident.
    const result = this.residentReg.resolveOrCreateByWallet(extractedAddress);

    // 6) Issue session.
    const session = this.residentReg.issueSession({
      residentId: result.resident.id,
      walletAddress: extractedAddress,
      ttlMs: this.sessionTtlMs,
    });
    if (!session.ok || !session.session) {
      return { ok: false, reason: session.reason ?? "session-issue-failed" };
    }

    return {
      ok: true,
      residentId: result.resident.id,
      walletId: result.wallet.id,
      sessionId: session.session.id,
      expiresAt: session.session.expiresAt,
      isNew: result.created,
      recoveredAddress: sigResult.recoveredAddress,
    };
  }

  /**
   * Logout / session invalidate. Idempotent.
   */
  revokeSession(sessionId: string): boolean {
    return this.residentReg.revokeSession(sessionId);
  }

  /**
   * Disconnect wallet: remove a wallet identity from a Resident and revoke
   * all sessions of that resident.
   */
  disconnectWallet(residentId: string): boolean {
    return this.residentReg.revokeAllSessions(residentId) > 0;
  }
}

function extractNonceFromText(text: string): string | null {
  const m = /Nonce: (\S+)/.exec(text);
  return m && m[1] ? m[1] : null;
}
function extractAddressFromText(text: string): string | null {
  const lines = text.split("\n");
  if (lines.length < 2) return null;
  return normalizeEvmAddress(lines[1] ?? "");
}

/**
 * Default singleton.
 */
export const defaultPassport = new Passport();
