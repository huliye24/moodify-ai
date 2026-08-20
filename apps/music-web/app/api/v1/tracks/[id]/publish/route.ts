import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { creationPassports, publicationEvents, tracks } from "@/db/schema";
import { ApiError, jsonError, requireMusicUser } from "@/lib/api";
import { requireOwnedTrack } from "@/lib/ownership";

export async function POST(request: Request, context: { params: Promise<{ id: string }> }) {
  try {
    const user = await requireMusicUser(request);
    const { id } = await context.params;
    const { track } = await requireOwnedTrack(id, user.id);
    if (track.status !== "draft" || !track.currentVersionId) throw new ApiError(409, "TRACK_NOT_READY", "作品缺少可发布的音频版本");
    const passport = await getDb().query.creationPassports.findFirst({ where: eq(creationPassports.trackVersionId, track.currentVersionId) });
    if (!passport?.rightsStatement) throw new ApiError(409, "PASSPORT_REQUIRED", "作品缺少基础创作护照和权利声明");
    const now = new Date().toISOString();
    await getDb().batch([
      getDb().update(tracks).set({ status: "published", publishedAt: now, updatedAt: now }).where(eq(tracks.id, id)),
      getDb().insert(publicationEvents).values({ id: crypto.randomUUID(), trackId: id, actorUserId: user.id, fromStatus: "draft", toStatus: "published" }),
    ]);
    return Response.json({ track: { id, status: "published", publicUrl: `/track/${id}` } });
  } catch (error) { return jsonError(error); }
}
