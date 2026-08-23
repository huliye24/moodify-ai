import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { creatorProfiles } from "@/db/schema";
import { ApiError, jsonError, requireMusicUser, requireText } from "@/lib/api";

export async function GET(request: Request) {
  try {
    const user = await requireMusicUser(request);
    const creator = await getDb().query.creatorProfiles.findFirst({ where: eq(creatorProfiles.userId, user.id) });
    return Response.json({ creator: creator ?? null });
  } catch (error) { return jsonError(error); }
}

export async function POST(request: Request) {
  try {
    const user = await requireMusicUser(request);
    const body = await request.json() as Record<string, unknown>;
    const handle = requireText(body.handle, "handle", 32).toLowerCase();
    if (!/^[a-z0-9][a-z0-9_-]{2,31}$/.test(handle)) throw new ApiError(400, "HANDLE_INVALID", "handle 仅支持 3–32 位英文、数字、_ 或 -");
    const displayName = requireText(body.displayName, "displayName", 80);
    const [creator] = await getDb().insert(creatorProfiles).values({
      id: crypto.randomUUID(), userId: user.id, handle, displayName,
      bio: typeof body.bio === "string" ? body.bio.trim().slice(0, 500) : "",
    }).returning();
    return Response.json({ creator }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && /UNIQUE constraint failed/.test(error.message)) return jsonError(new ApiError(409, "CREATOR_CONFLICT", "该用户已有音乐馆或 handle 已被使用"));
    return jsonError(error);
  }
}
