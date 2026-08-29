import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { users } from "@/db/schema";

const EMAIL_HEADER = "oai-authenticated-user-email";
const NAME_HEADER = "oai-authenticated-user-full-name";
const NAME_ENCODING_HEADER = "oai-authenticated-user-full-name-encoding";

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) {
    super(message);
  }
}

export function jsonError(error: unknown): Response {
  if (error instanceof ApiError) {
    return Response.json({ error: { code: error.code, message: error.message } }, { status: error.status });
  }
  console.error(JSON.stringify({ event: "music_api_error", message: error instanceof Error ? error.message : "unknown" }));
  return Response.json({ error: { code: "INTERNAL_ERROR", message: "请求暂时无法完成" } }, { status: 500 });
}

export function requireText(value: unknown, field: string, max: number): string {
  const result = typeof value === "string" ? value.trim() : "";
  if (!result || result.length > max) throw new ApiError(400, "VALIDATION", `${field} 不符合要求`);
  return result;
}

export async function requireMusicUser(request: Request) {
  const email = request.headers.get(EMAIL_HEADER)?.trim().toLowerCase();
  if (!email) throw new ApiError(401, "UNAUTHORIZED", "请先登录 Moodify");
  const encodedName = request.headers.get(NAME_HEADER);
  const displayName = encodedName && request.headers.get(NAME_ENCODING_HEADER) === "percent-encoded-utf-8"
    ? safeDecode(encodedName) ?? email
    : email;
  const authSubject = `chatgpt:${email}`;
  const db = getDb();
  const existing = await db.query.users.findFirst({ where: eq(users.authSubject, authSubject) });
  if (existing) return existing;
  const [created] = await db.insert(users).values({
    id: crypto.randomUUID(), authSubject, email, displayName,
  }).onConflictDoNothing({ target: users.authSubject }).returning();
  if (created) return created;
  const raced = await db.query.users.findFirst({ where: eq(users.authSubject, authSubject) });
  if (!raced) throw new ApiError(500, "IDENTITY_SYNC_FAILED", "无法建立用户身份");
  return raced;
}

function safeDecode(value: string): string | null {
  try { return decodeURIComponent(value); } catch { return null; }
}
