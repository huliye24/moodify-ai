import { getDb } from "@/db";
import { tracks } from "@/db/schema";
import { ApiError, jsonError, requireMusicUser, requireText } from "@/lib/api";
import { requireCreator } from "@/lib/ownership";

const sourceTypes = new Set(["ai", "human", "hybrid"]);
const disclosures = new Set(["private", "partial", "public"]);

export async function POST(request: Request) {
  try {
    const user = await requireMusicUser(request);
    const creator = await requireCreator(user.id);
    const body = await request.json() as Record<string, unknown>;
    const title = requireText(body.title, "title", 160);
    const sourceType = requireText(body.sourceType, "sourceType", 16);
    const rightsStatement = requireText(body.rightsStatement, "rightsStatement", 2000);
    const promptDisclosure = typeof body.promptDisclosure === "string" ? body.promptDisclosure : "private";
    if (!sourceTypes.has(sourceType) || !disclosures.has(promptDisclosure)) throw new ApiError(400, "VALIDATION", "创作来源或披露方式无效");
    const trackId = crypto.randomUUID();
    await getDb().insert(tracks).values({
      id: trackId, creatorId: creator.id, title, sourceType: sourceType as "ai" | "human" | "hybrid",
      description: typeof body.description === "string" ? body.description.trim().slice(0, 2000) : "",
      language: typeof body.language === "string" ? body.language.trim().slice(0, 16) : null,
      licenseStatus: body.licenseStatus === "inquiry" ? "inquiry" : "not_available",
    });
    // The passport is finalized against the immutable media version after upload.
    return Response.json({ track: { id: trackId, status: "draft" }, passportDraft: {
      promptDisclosure, aiTool: body.aiTool ?? null, modelVersion: body.modelVersion ?? null,
      lyricsAuthor: body.lyricsAuthor ?? null, vocalSource: body.vocalSource ?? null,
      humanEditing: body.humanEditing ?? null, dawTools: body.dawTools ?? null,
      rightsStatement,
    } }, { status: 201 });
  } catch (error) { return jsonError(error); }
}
