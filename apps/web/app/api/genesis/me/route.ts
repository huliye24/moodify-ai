/* GET /api/genesis/me — look up an existing Genesis registration by wallet
   address. Public endpoint; used by the /genesis page on revisit to show
   the already-registered state. */

import { ApiError, jsonError } from "@/lib/api";
import { findGenesisParticipantByAddress } from "@/lib/genesis-service";

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const address = url.searchParams.get("address") ?? "";
    if (!address) throw new ApiError(400, "ADDRESS_REQUIRED", "请提供 wallet 地址");
    const participant = await findGenesisParticipantByAddress(address);
    return Response.json({ participant });
  } catch (error) { return jsonError(error); }
}
