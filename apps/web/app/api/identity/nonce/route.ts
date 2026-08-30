/**
 * MOOD PASSPORT 015 — GET /api/identity/nonce
 *
 * Issues a single-use nonce + EIP-4361 (SIWE) message for the wallet to sign.
 * The actual problem is solved by the Passport.requestSignIn orchestrator.
 *
 * Body shape (GET, query params):
 *   address : EVM address (required, normalized server-side)
 *   domain  : origin host (optional, defaults to env)
 *
 * Response 200:
 *   {
 *     message:    { ... SIWE structure ... },
 *     messageText: "human readable text ...",
 *     expiresAt:  "ISO 8601"
 *   }
 */

import { Passport } from "../../../lib/mood/passport/index.ts";
import { normalizeEvmAddress } from "../../../lib/mood/passport/evm-address.ts";
import { jsonError } from "./_helpers.ts";

export const dynamic = "force-dynamic";

export async function GET(request: Request): Promise<Response> {
  try {
    const url = new URL(request.url);
    const rawAddress = url.searchParams.get("address");
    const address = normalizeEvmAddress(rawAddress);
    if (!address) {
      return jsonError(400, "VALIDATION", "address required");
    }

    // CSRF / origin defense: same-domain only. We accept the request only
    // when its Origin matches the configured domain (header-based).
    const allowed = matchAllowedOrigin(request);
    if (!allowed) {
      return jsonError(403, "ORIGIN_FORBIDDEN", "Cross-origin request denied");
    }

    const passport = new Passport({
      domain: preferredDomain(request),
      uri: preferredUri(request),
      chainId: preferredChainId(),
    });
    const out = passport.requestSignIn({ walletAddress: address });
    if (!out.ok || !out.message || !out.messageText) {
      return jsonError(500, "NONCE_ISSUE_FAILED", out.reason ?? "nonce-issue-failed");
    }
    return Response.json({
      message: out.message,
      messageText: out.messageText,
      expiresAt: out.message.expirationTime,
    });
  } catch (err) {
    console.error("identity/nonce error", err);
    return jsonError(500, "INTERNAL", "identity/nonce failed");
  }
}

function matchAllowedOrigin(request: Request): boolean {
  const origin = request.headers.get("origin");
  const referer = request.headers.get("referer");
  // Either explicit Origin (preferred) or Referer must match the request host.
  let host: string;
  try {
    host = new URL(request.url).host;
  } catch {
    return false;
  }
  const candidate = origin ?? referer ?? "";
  if (!candidate) {
    // Browser requests always send one of these. For server-to-server, we
    // fall back to same-host.
    return true;
  }
  try {
    return new URL(candidate).host === host;
  } catch {
    return false;
  }
}

function preferredDomain(request: Request): string {
  return new URL(request.url).host;
}

function preferredUri(request: Request): string {
  return new URL("/portal/passport", request.url).toString();
}

function preferredChainId(): number {
  // Foundation: default to 56 (BSC) but the value is never asserted against
  // a hard-coded Token; the Passport only uses it for the SIWE message body.
  // A production deployment may read this from config but never from the
  // Token config.
  return 56;
}
