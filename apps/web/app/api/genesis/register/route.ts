/* POST /api/genesis/register — verify a wallet signature against a valid
   nonce and create a Genesis Participant record. Idempotent on duplicate
   wallet (returns the existing participant instead of erroring). */

import { ApiError, jsonError } from "@/lib/api";
import { registerGenesis } from "@/lib/genesis-service";

export async function POST(request: Request) {
  try {
    const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
    if (!body) throw new ApiError(400, "VALIDATION", "请求体格式不正确");
    const address = typeof body.address === "string" ? body.address : "";
    const chainId = typeof body.chainId === "number" ? body.chainId : Number(body.chainId);
    const nonce = typeof body.nonce === "string" ? body.nonce : "";
    const signature = typeof body.signature === "string" ? body.signature : "";
    if (!Number.isInteger(chainId)) throw new ApiError(400, "CHAIN_REQUIRED", "chainId 必须为整数");
    if (!address || !nonce || !signature) throw new ApiError(400, "VALIDATION", "缺少必填字段");
    const participant = await registerGenesis({ address, chainId, nonce, signature });
    return Response.json({ participant });
  } catch (error) { return jsonError(error); }
}
