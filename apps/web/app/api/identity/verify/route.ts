/**
 * MOOD PASSPORT 015 — POST /api/identity/verify
 *
 * Completes sign-in. Validates signature, consumes nonce, resolves/creates
 * the Resident, issues a session, and sets the session cookie.
 *
 * In the foundation deployment there is NO real signer-recovery library
 * bundled (we deliberately don't couple `viem` to the passport path). The
 * signature verification uses a pluggable `recoverAddress` function. When
 * it's not provided we fail closed: { ok: false, reason: "no-recoverer" }.
 *
 * Future integration packages (e.g. an INTEGRATION bridge) must wire a real
 * recoverer. Until then, the endpoint returns 503 with a deterministic
 * reason so clients can test the auth flow shape without breaking.
 *
 * Body shape (JSON):
 *   messageText : exact text the wallet signed
 *   signature   : 0x-prefixed hex signature
 */

import { Passport } from "../../../lib/mood/passport/index.ts";
import {
  FAIL_CLOSED_RECOVER,
  type RecoverAddressFn,
} from "../../../lib/mood/passport/signature.ts";
import { FAKE_RECOVER_FOR_TEST } from "../../../lib/mood/passport/test-recover.ts";
import {
  buildSessionCookie,
  isRequestOnHttpsOrigin,
  jsonError,
} from "./_helpers.ts";

export const dynamic = "force-dynamic";

export async function POST(request: Request): Promise<Response> {
  try {
    // Same-origin check.
    const url = new URL(request.url);
    const origin = request.headers.get("origin");
    if (origin && new URL(origin).host !== url.host) {
      return jsonError(403, "ORIGIN_FORBIDDEN", "Cross-origin verify denied");
    }

    let body: Record<string, unknown>;
    try {
      body = await request.json() as Record<string, unknown>;
    } catch {
      return jsonError(400, "VALIDATION", "Body must be JSON");
    }

    const messageText = typeof body.messageText === "string"
      ? body.messageText
      : null;
    const signature = typeof body.signature === "string"
      ? body.signature
      : null;
    if (!messageText || !signature) {
      return jsonError(
        400,
        "VALIDATION",
        "messageText and signature are required",
      );
    }

    // Foundation-mode recoverer:
    //   - In dev mode (`MOOD_PASSPORT_DEV_MODE=1`), uses the test recoverer.
    //   - In production, uses FAIL_CLOSED_RECOVER which always returns null.
    //   - If a real signer-recovery library is wired (future INTEGRATION),
    //     this is the place to plug it in. Failure-to-recover → fail closed.
    const recoverer: RecoverAddressFn =
      process.env.MOOD_PASSPORT_DEV_MODE === "1"
        ? FAKE_RECOVER_FOR_TEST
        : FAIL_CLOSED_RECOVER;
    const passport = new Passport({
      domain: url.host,
      uri: new URL("/portal/passport", request.url).toString(),
      chainId: 56,
      recoverAddress: recoverer,
    });

    const out = passport.completeSignIn({
      messageText,
      signature,
      expectedDomain: url.host,
      expectedUri: new URL("/portal/passport", request.url).toString(),
      expectedChainId: 56,
    });
    if (!out.ok || !out.sessionId || !out.expiresAt) {
      return jsonError(401, "AUTH_FAILED", out.reason ?? "verify-failed");
    }

    const cookie = buildSessionCookie(
      out.sessionId,
      out.expiresAt,
      isRequestOnHttpsOrigin(request),
    );

    return new Response(
      JSON.stringify({
        ok: true,
        residentId: out.residentId,
        walletId: out.walletId,
        sessionId: out.sessionId,
        expiresAt: out.expiresAt,
        isNew: out.isNew,
      }),
      {
        status: 200,
        headers: {
          "content-type": "application/json",
          "set-cookie": cookie,
        },
      },
    );
  } catch (err) {
    console.error("identity/verify error", err);
    return jsonError(500, "INTERNAL", "identity/verify failed");
  }
}
