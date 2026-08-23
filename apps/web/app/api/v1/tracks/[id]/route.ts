import { and, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { creatorProfiles, tracks } from "@/db/schema";
import { jsonError } from "@/lib/api";

export async function GET(_request: Request, context: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await context.params;
    const [result] = await getDb().select({ id: tracks.id, title: tracks.title, description: tracks.description, sourceType: tracks.sourceType, licenseStatus: tracks.licenseStatus, creatorHandle: creatorProfiles.handle, creatorName: creatorProfiles.displayName })
      .from(tracks).innerJoin(creatorProfiles, eq(tracks.creatorId, creatorProfiles.id)).where(and(eq(tracks.id, id), eq(tracks.status, "published"))).limit(1);
    return result ? Response.json({ track: result }) : Response.json({ error: { code: "TRACK_NOT_FOUND" } }, { status: 404 });
  } catch (error) { return jsonError(error); }
}
