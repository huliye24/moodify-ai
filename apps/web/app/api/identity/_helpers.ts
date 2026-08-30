/**
 * MOOD PASSPORT 015 — Identity API helper
 *
 * Helpers for /api/identity/* routes: same auth pattern everywhere.
 */

import type { Resident } from "@/lib/mood/passport/types.ts";
import { defaultResidentRegistry } from "@/lib/mood/passport/index.ts";

export const SESSION_COOKIE_NAME = "mood_session";

/**
 * Read the session cookie from a request. Returns null if absent.
 */
export function readSessionCookie(request: Request): string | null {
  const header = request.headers.get("cookie");
  if (!header) return null;
  for (const part of header.split(";")) {
    const [name, ...rest] = part.trim().split("=");
    if (name === SESSION_COOKIE_NAME) {
      return decodeURIComponent(rest.join("="));
    }
  }
  return null;
}

/**
 * Resolve the current Resident from the request's session cookie.
 * Returns null when no valid session.
 */
export function requireResident(request: Request): Resident | null {
  const sessionId = readSessionCookie(request);
  if (!sessionId) return null;
  const session = defaultResidentRegistry.getSession(sessionId);
  if (!session) return null;
  return defaultResidentRegistry.getResident(session.residentId);
}

/**
 * Common JSON error response shape.
 */
export function jsonError(status: number, code: string, message: string) {
  return Response.json({ error: { code, message } }, { status });
}

/**
 * Build a Set-Cookie value for a session. HttpOnly + SameSite=Lax +
 * Path=/ + secure-when-https.
 */
export function buildSessionCookie(
  sessionId: string,
  expiresAt: string,
  secure: boolean,
): string {
  const parts = [
    `${SESSION_COOKIE_NAME}=${encodeURIComponent(sessionId)}`,
    "Path=/",
    "HttpOnly",
    "SameSite=Lax",
    `Expires=${new Date(expiresAt).toUTCString()}`,
  ];
  if (secure) parts.push("Secure");
  return parts.join("; ");
}

/**
 * Build a Set-Cookie clearing the session.
 */
export function buildClearSessionCookie(secure: boolean): string {
  const parts = [
    `${SESSION_COOKIE_NAME}=`,
    "Path=/",
    "HttpOnly",
    "SameSite=Lax",
    "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
  ];
  if (secure) parts.push("Secure");
  return parts.join("; ");
}

export function isHttps(url: string): boolean {
  try {
    return new URL(url).protocol === "https:";
  } catch {
    return false;
  }
}

/**
 * Public-domain-bound InsecureOriginException helper.
 */
export function isRequestOnHttpsOrigin(request: Request): boolean {
  try {
    return new URL(request.url).protocol === "https:";
  } catch {
    return false;
  }
}
