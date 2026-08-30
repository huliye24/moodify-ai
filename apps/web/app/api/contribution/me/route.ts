/* GET /api/contribution/me — look up Genesis participant info for /contribute page.
 * Reads from `?address=` query param (same pattern as /api/genesis/me).
 * Returns participant identity + current reputation summary. */

import { jsonError } from "@/lib/api";
import { findGenesisParticipantByAddress } from "@/lib/genesis-service";
import { getDb } from "@/db";
import { contributionSubmissions, rewardEvents } from "@/db/schema";
import { eq, sql } from "drizzle-orm";
import { sumReputationFor } from "@/lib/contribution-service";

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const address = url.searchParams.get("address") ?? "";
    if (!address) return Response.json({ error: { code: "ADDRESS_REQUIRED", message: "请提供 wallet 地址" } }, { status: 400 });
    const participant = await findGenesisParticipantByAddress(address);
    if (!participant) return Response.json({ error: { code: "PARTICIPANT_NOT_FOUND", message: "该钱包未注册" } }, { status: 404 });

    const db = getDb();
    const pendingRewards = await db
      .select({ s: sql<string>`COALESCE(SUM(${rewardEvents.rewardAtomic}), '0')` })
      .from(rewardEvents)
      .where(eq(rewardEvents.participantId, participant.id));
    const submissionCount = await db
      .select({ c: sql<number>`COUNT(*)` })
      .from(contributionSubmissions)
      .where(eq(contributionSubmissions.participantId, participant.id));
    const approvedCount = await db
      .select({ c: sql<number>`COUNT(*)` })
      .from(contributionSubmissions)
      .where(eq(contributionSubmissions.status, "approved"));
    const reputation = await sumReputationFor(participant.id);
    const pendingAtomic = pendingRewards[0]?.s ?? "0";

    return Response.json({
      participant: {
        id: participant.id,
        participantNumber: participant.participantNumber,
        address: participant.address,
        reputationScore: reputation,
        pendingRewardMood: (BigInt(pendingAtomic) / 10n ** 18n).toString(),
        pendingRewardAtomic: pendingAtomic,
        submissionCount: Number(submissionCount[0]?.c ?? 0),
        approvedSubmissionCount: Number(approvedCount[0]?.c ?? 0),
      },
    });
  } catch (error) { return jsonError(error); }
}
