import { and, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { creatorProfiles, tracks } from "@/db/schema";
import { ApiError } from "@/lib/api";

export async function requireCreator(userId: string) {
  const creator = await getDb().query.creatorProfiles.findFirst({ where: eq(creatorProfiles.userId, userId) });
  if (!creator) throw new ApiError(409, "CREATOR_REQUIRED", "请先建立音乐馆");
  return creator;
}

export async function requireOwnedTrack(trackId: string, userId: string) {
  const creator = await requireCreator(userId);
  const track = await getDb().query.tracks.findFirst({
    where: and(eq(tracks.id, trackId), eq(tracks.creatorId, creator.id)),
  });
  if (!track) throw new ApiError(404, "TRACK_NOT_FOUND", "作品不存在或不属于当前用户");
  return { creator, track };
}
