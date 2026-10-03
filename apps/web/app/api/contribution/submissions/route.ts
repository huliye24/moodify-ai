/* GET /api/contribution/submissions — list my submissions (requires participant wallet)
 * POST /api/contribution/submissions — create a submission (requires participant) */

import { jsonError } from "@/lib/api";
import { findGenesisParticipantByAddress } from "@/lib/genesis-service";
import {
  createSubmission,
  listPublicTasksForParticipant,
} from "@/lib/contribution-service";

/* GET: participant identifies via wallet query param (public endpoint).
 * No need for full wallet sign — we look up the registered participant. */
export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const address = url.searchParams.get("address") ?? "";
    if (!address) {
      return Response.json({ error: { code: "ADDRESS_REQUIRED", message: "请提供 wallet 地址" } }, { status: 400 });
    }
    const participant = await findGenesisParticipantByAddress(address);
    if (!participant) {
      return Response.json({ error: { code: "PARTICIPANT_NOT_FOUND", message: "该钱包未注册为 Genesis Participant" } }, { status: 404 });
    }
    const submissions = await listPublicTasksForParticipant(participant.id);
    return Response.json({
      participant: { participantNumber: participant.participantNumber, address: participant.address },
      submissions,
    });
  } catch (error) { return jsonError(error); }
}

/* POST: also identifies by address; body carries submission data. */
export async function POST(request: Request) {
  try {
    const url = new URL(request.url);
    const address = url.searchParams.get("address") ?? "";
    if (!address) {
      return Response.json({ error: { code: "ADDRESS_REQUIRED", message: "请提供 wallet 地址" } }, { status: 400 });
    }
    const participant = await findGenesisParticipantByAddress(address);
    if (!participant) {
      return Response.json({ error: { code: "PARTICIPANT_NOT_FOUND", message: "该钱包未注册为 Genesis Participant" } }, { status: 404 });
    }
    const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
    if (!body) throw new Error("请求体格式不正确");
    const submission = await createSubmission(
      {
        taskId: typeof body.taskId === "string" ? body.taskId : "",
        summary: typeof body.summary === "string" ? body.summary : "",
        evidenceText: typeof body.evidenceText === "string" ? body.evidenceText : "",
        evidenceUrls: Array.isArray(body.evidenceUrls) ? body.evidenceUrls : [],
        resubmit: Boolean(body.resubmit),
      },
      participant.id,
    );
    return Response.json({ submission }, { status: 201 });
  } catch (error) { return jsonError(error); }
}
