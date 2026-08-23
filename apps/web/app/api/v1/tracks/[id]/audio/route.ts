import { env } from "cloudflare:workers";
import { and, eq } from "drizzle-orm";
import { getDb } from "@/db";
import { creationPassports, tracks, trackVersions } from "@/db/schema";
import { ApiError, jsonError, requireMusicUser, requireText } from "@/lib/api";
import { requireOwnedTrack } from "@/lib/ownership";

const allowedMime = new Set(["audio/wav", "audio/x-wav", "audio/mpeg", "audio/flac", "audio/mp4", "audio/ogg", "audio/aac"]);
const maxBytes = 100 * 1024 * 1024;

export async function PUT(request: Request, context: { params: Promise<{ id: string }> }) {
  let objectKey: string | null = null;
  try {
    const user = await requireMusicUser(request);
    const { id } = await context.params;
    const { track } = await requireOwnedTrack(id, user.id);
    if (track.status !== "draft") throw new ApiError(409, "TRACK_NOT_DRAFT", "只有草稿可以上传新音频");
    const mime = request.headers.get("content-type")?.split(";", 1)[0].toLowerCase() ?? "";
    const bytes = Number(request.headers.get("content-length"));
    const sha256 = request.headers.get("x-content-sha256")?.toLowerCase() ?? "";
    const filename = requireText(request.headers.get("x-filename"), "x-filename", 255);
    if (!allowedMime.has(mime)) throw new ApiError(415, "AUDIO_TYPE_UNSUPPORTED", "不支持该音频格式");
    if (!Number.isSafeInteger(bytes) || bytes <= 0 || bytes > maxBytes) throw new ApiError(413, "AUDIO_SIZE_INVALID", "音频大小必须在 100 MB 以内");
    if (!/^[a-f0-9]{64}$/.test(sha256)) throw new ApiError(400, "SHA256_REQUIRED", "必须提供有效 SHA-256");
    if (!request.body) throw new ApiError(400, "AUDIO_EMPTY", "音频内容为空");
    objectKey = `private/tracks/${id}/${crypto.randomUUID()}/${safeFilename(filename)}`;
    await env.MEDIA.put(objectKey, request.body, { httpMetadata: { contentType: mime }, customMetadata: { sha256, trackId: id } });
    const passport = JSON.parse(decodeURIComponent(request.headers.get("x-passport") ?? "%7B%7D")) as Record<string, unknown>;
    const rightsStatement = requireText(passport.rightsStatement, "rightsStatement", 2000);
    const versionId = crypto.randomUUID();
    await getDb().batch([
      getDb().insert(trackVersions).values({ id: versionId, trackId: id, versionLabel: "v1", audioObjectKey: objectKey, audioSha256: sha256, audioBytes: bytes, mimeType: mime }),
      getDb().insert(creationPassports).values({ id: crypto.randomUUID(), trackVersionId: versionId, rightsStatement,
        promptDisclosure: passport.promptDisclosure === "public" || passport.promptDisclosure === "partial" ? passport.promptDisclosure : "private",
        aiTool: optional(passport.aiTool), modelVersion: optional(passport.modelVersion), lyricsAuthor: optional(passport.lyricsAuthor), vocalSource: optional(passport.vocalSource), humanEditing: optional(passport.humanEditing), dawTools: optional(passport.dawTools),
      }),
      getDb().update(tracks).set({ currentVersionId: versionId, updatedAt: new Date().toISOString() }).where(eq(tracks.id, id)),
    ]);
    return Response.json({ version: { id: versionId, trackId: id, audioBytes: bytes, sha256 } }, { status: 201 });
  } catch (error) {
    if (objectKey) await env.MEDIA.delete(objectKey).catch(() => undefined);
    return jsonError(error);
  }
}

function safeFilename(value: string) { return value.normalize("NFKC").replace(/[^a-zA-Z0-9._-]+/g, "-").slice(-120) || "audio.bin"; }
function optional(value: unknown) { return typeof value === "string" && value.trim() ? value.trim().slice(0, 2000) : null; }

export async function GET(request: Request, context: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await context.params;
    const track = await getDb().query.tracks.findFirst({ where: and(eq(tracks.id, id), eq(tracks.status, "published")) });
    if (!track?.currentVersionId) throw new ApiError(404, "TRACK_NOT_FOUND", "作品不存在");
    const version = await getDb().query.trackVersions.findFirst({ where: eq(trackVersions.id, track.currentVersionId) });
    if (!version) throw new ApiError(404, "MEDIA_NOT_FOUND", "作品音频不存在");
    const object = await env.MEDIA.get(version.audioObjectKey, { range: request.headers });
    if (!object) throw new ApiError(404, "MEDIA_NOT_FOUND", "作品音频不存在");
    const headers = new Headers();
    object.writeHttpMetadata(headers);
    headers.set("etag", object.httpEtag);
    headers.set("accept-ranges", "bytes");
    if (request.headers.has("range") && "range" in object && object.range) {
      const range = object.range;
      let offset: number;
      let length: number;
      if ("suffix" in range) {
        length = Math.min(range.suffix, object.size);
        offset = object.size - length;
      } else {
        offset = range.offset ?? 0;
        length = range.length ?? object.size - offset;
      }
      headers.set("content-range", `bytes ${offset}-${offset + length - 1}/${object.size}`);
      headers.set("content-length", String(length));
      return new Response(object.body, { status: 206, headers });
    }
    headers.set("content-length", String(object.size));
    return new Response(object.body, { headers });
  } catch (error) { return jsonError(error); }
}
