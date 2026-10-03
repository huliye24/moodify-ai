/* MOOD-GENESIS-006: Admin authorization helper for the Contribution Network
 * (and any future internal review/operations surface).
 *
 * The auth model reuses the existing `users` table populated by
 * `requireMusicUser()` (ChatGPT authenticated email header). A user becomes
 * an admin only when their email matches an entry in the
 * `MOODIFY_ADMIN_EMAILS` allowlist environment variable (comma-separated).
 *
 * The allowlist is configured at deploy time. It is intentionally minimal:
 *   - no shared passwords;
 *   - no client-side isAdmin trust;
 *   - allowlist check happens server-side, on every mutation;
 *   - first-match admin gets a stable display id for audit events.
 *
 * The check is synchronous and side-effect free. Mutations should always go
 * through `requireAdminActor(request)` to get a verified admin identity for
 * audit/review events.
 *
 * Safety: never signs transactions, never holds private keys, never approves
 * token spending. Only gates internal review/operations endpoints. */

import { eq } from "drizzle-orm";
import { ApiError } from "@/lib/api";
import { requireMusicUser } from "@/lib/api";
import { getDb } from "@/db";
import { users } from "@/db/schema";

/** Parsed admin allowlist, loaded lazily on first use. */
let allowlistCache: { lower: Set<string>; display: Map<string, string> } | null = null;

function parseAllowlist(): { lower: Set<string>; display: Map<string, string> } {
  if (allowlistCache) return allowlistCache;
  const raw = process.env.MOODIFY_ADMIN_EMAILS ?? "";
  const lower = new Set<string>();
  const display = new Map<string, string>();
  for (const entry of raw.split(/[,;\s]+/)) {
    const trimmed = entry.trim();
    if (!trimmed || !trimmed.includes("@")) continue;
    lower.add(trimmed.toLowerCase());
    display.set(trimmed.toLowerCase(), trimmed);
  }
  allowlistCache = { lower, display };
  return allowlistCache;
}

/** Force re-read of the allowlist (test-only escape hatch). */
export function __resetAdminAllowlistCacheForTests(): void {
  allowlistCache = null;
}

/** Returns true when the given email is in the admin allowlist. */
export function isAdminEmail(email: string | null | undefined): boolean {
  if (!email) return false;
  return parseAllowlist().lower.has(email.toLowerCase());
}

/** Resolved admin identity returned by `requireAdminActor`. */
export interface AdminActor {
  /** The same row from `users` table used by the existing music-user auth. */
  userId: string;
  email: string;
  /** Display id used in audit events (email). Never the user's ID/UUID. */
  displayId: string;
  /** Auth subject (e.g., "chatgpt:admin@example.com"). */
  authSubject: string;
}

/** Resolve the calling request to an admin actor.
 *
 * Throws `ApiError(401)` when no authenticated user, `ApiError(403)` when
 * authenticated but not in the admin allowlist. */
export async function requireAdminActor(request: Request): Promise<AdminActor> {
  const user = await requireMusicUser(request);
  if (!isAdminEmail(user.email)) {
    throw new ApiError(403, "ADMIN_REQUIRED", "当前账号没有管理员权限");
  }
  const email = (user.email ?? "").toLowerCase();
  return {
    userId: user.id,
    email,
    displayId: user.email ?? email,
    authSubject: user.authSubject,
  };
}

/** Async helper: list current admin allowlist (for diagnostics / admin UI). */
export async function listAdminAllowlist(): Promise<{ email: string; display: string; userId: string | null }[]> {
  const { lower, display } = parseAllowlist();
  const list: { email: string; display: string; userId: string | null }[] = [];
  for (const email of lower) {
    const row = await getDb().query.users.findFirst({
      where: eq(users.email, display.get(email) ?? email),
    });
    list.push({ email, display: display.get(email) ?? email, userId: row?.id ?? null });
  }
  return list;
}
