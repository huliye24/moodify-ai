import { and, desc, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { creatorProfiles, tracks } from "@/db/schema";
import { jsonError } from "@/lib/api";

export async function GET(_request: Request, context: { params: Promise<{ handle: string }> }) {
  try {
    const { handle } = await context.params;
    const creator = await getDb().query.creatorProfiles.findFirst({ where: and(eq(creatorProfiles.handle, handle.toLowerCase()), eq(creatorProfiles.isPublic, true)) });
    if (!creator) return Response.json({ error: { code: "CREATOR_NOT_FOUND" } }, { status: 404 });
    const works = await getDb().select({ id: tracks.id, title: tracks.title, sourceType: tracks.sourceType, publishedAt: tracks.publishedAt }).from(tracks).where(and(eq(tracks.creatorId, creator.id), eq(tracks.status, "published"))).orderBy(desc(tracks.publishedAt)).limit(50);
    return Response.json({ creator: { handle: creator.handle, displayName: creator.displayName, bio: creator.bio, avatarUrl: creator.avatarUrl }, tracks: works });
  } catch (error) { return jsonError(error); }
}
