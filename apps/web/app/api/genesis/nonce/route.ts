/* POST /api/genesis/nonce — issue a one-time nonce for an EVM wallet on BNB
   Smart Chain. Returns the canonical message the user will sign. */

import { ApiError, jsonError } from "@/lib/api";
import { issueGenesisNonce } from "@/lib/genesis-service";

export async function POST(request: Request) {
  try {
    const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
    if (!body) throw new ApiError(400, "VALIDATION", "请求体格式不正确");
    const address = typeof body.address === "string" ? body.address : "";
    const chainId = typeof body.chainId === "number" ? body.chainId : Number(body.chainId);
    if (!Number.isInteger(chainId)) throw new ApiError(400, "CHAIN_REQUIRED", "chainId 必须为整数");
    const challenge = await issueGenesisNonce({ address, chainId });
    return Response.json(challenge);
  } catch (error) { return jsonError(error); }
}
