/**
 * MOOD PASSPORT 015 — POST /api/identity/logout
 *
 * Invalidates the current session. Idempotent: missing/expired session
 * returns 200.
 */

import {
  buildClearSessionCookie,
  isRequestOnHttpsOrigin,
  jsonError,
  readSessionCookie,
} from "@/app/api/identity/_helpers.ts";
import { defaultResidentRegistry } from "@/lib/mood/passport/index.ts";

export const dynamic = "force-dynamic";

export async function POST(request: Request): Promise<Response> {
  try {
    const url = new URL(request.url);
    const origin = request.headers.get("origin");
    if (origin && new URL(origin).host !== url.host) {
      return jsonError(403, "ORIGIN_FORBIDDEN", "Cross-origin logout denied");
    }

    const sessionId = readSessionCookie(request);
    if (sessionId) defaultResidentRegistry.revokeSession(sessionId);

    const cookie = buildClearSessionCookie(isRequestOnHttpsOrigin(request));
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: {
        "content-type": "application/json",
        "set-cookie": cookie,
      },
    });
  } catch (err) {
    console.error("identity/logout error", err);
    return jsonError(500, "INTERNAL", "identity/logout failed");
  }
}
