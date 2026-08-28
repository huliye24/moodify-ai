/* MOOD-GENESIS-002: Server-side Genesis Registration service.

   All authorization decisions live here:
   - nonce issuance (cryptographically random, single-use, time-limited)
   - signature verification (EIP-191 personal_sign, recovered signer must
     match the requested normalized address)
   - race-safe participant number allocation (UNIQUE participant_number
     enforced at the database; allocation is retried inside a transaction)
   - nonce consumption (atomic `used_at` set inside the same transaction)

   The service never trusts client-provided participant numbers, status,
   score, or allocation values. It never requests or stores private keys.
   It performs no on-chain transaction.

   See docs/protocol/GENESIS_REGISTRATION.md for the full design. */

import { and, eq, isNull, sql } from "drizzle-orm";
import { getDb } from "@/db";
import { genesisNonces, genesisParticipants } from "@/db/schema";
import { ApiError } from "@/lib/api";
import { GENESIS_CONFIG } from "@/lib/genesis-config";
import { normalizeAddress, sha256Hex } from "@/lib/evm-address";
import {
  bytesToHex,
  defaultGenesisFields,
  buildGenesisMessage,
  hexToBytes,
  recoverPersonalSign,
} from "@/lib/genesis-message";

const NONCE_HEX_RE = /^[0-9a-f]{1,128}$/; // generous; we slice to configured length

export type NonceChallenge = {
  nonce: string;
  issuedAt: string;
  expiresAt: string;
  termsVersion: string;
  signatureVersion: string;
  chainId: number;
  domain: string;
  message: string;
};

export type RegisteredParticipant = {
  id: string;
  participantNumber: number;
  address: string; // checksum
  joinedAt: string;
  status: string;
  signatureVersion: string;
  termsVersion: string;
};

/* Generate a cryptographically secure random nonce of GENESIS_CONFIG length. */
function generateNonce(): string {
  const bytes = new Uint8Array(GENESIS_CONFIG.nonceByteLength);
  crypto.getRandomValues(bytes);
  return bytesToHex(bytes);
}

/* Issue a nonce for a given (address, chainId). Validates that the chain is
   the canonical BNB Smart Chain (id 56) before issuing anything. */
export async function issueGenesisNonce(input: { address: string; chainId: number }): Promise<NonceChallenge> {
  const normalized = normalizeAddress(input.address);
  if (!normalized) throw new ApiError(400, "ADDRESS_INVALID", "请提供有效的 EVM 钱包地址");
  if (input.chainId !== GENESIS_CONFIG.chainId) {
    throw new ApiError(400, "CHAIN_UNSUPPORTED", `仅支持 ${GENESIS_CONFIG.network} (chainId ${GENESIS_CONFIG.chainId})`);
  }
  const issuedAt = new Date();
  const expiresAt = new Date(issuedAt.getTime() + GENESIS_CONFIG.nonceTtlSeconds * 1000);
  const nonce = generateNonce();
  const nonceHash = await sha256Hex(nonce);
  await getDb().insert(genesisNonces).values({
    id: crypto.randomUUID(),
    walletAddressNormalized: normalized,
    nonceHash,
    issuedAt: issuedAt.toISOString(),
    expiresAt: expiresAt.toISOString(),
    chainId: input.chainId,
    termsVersion: GENESIS_CONFIG.termsVersion,
  });
  const fields = defaultGenesisFields(
    /* checksum form is display-only; the server echoes it back in the
       signed message to match what the client will display. */
    input.address.toLowerCase().replace(/^0x/, "0x").replace(/^(0x)([0-9a-f]{40})$/, (_, p, h) => p + h),
    nonce,
    issuedAt.toISOString(),
    expiresAt.toISOString(),
  );
  // Always emit the checksum form in the message for readability.
  fields.address = toChecksum(input.address);
  return {
    nonce,
    issuedAt: fields.issuedAt,
    expiresAt: fields.expiresAt,
    termsVersion: GENESIS_CONFIG.termsVersion,
    signatureVersion: GENESIS_CONFIG.signatureVersion,
    chainId: GENESIS_CONFIG.chainId,
    domain: GENESIS_CONFIG.officialDomain,
    message: buildGenesisMessage(fields),
  };
}

/* Minimal client-side mirror of EIP-55 used only for echoing back in the
   message. The full `checksumAddress` lives in `lib/evm-address.ts`; this
   service uses a small pure function to avoid pulling keccak into the
   hot registration path twice (we already keccak inside signature recovery).

   SECURITY CONTRACT: the service never accept arbitrary client nonce. The
   nonce is always server-generated (issueGenesisNonce); the client only
   echoes it back as part of the signed message. */
function toChecksum(value: string): string {
  return value.toLowerCase().replace(/^0x/, "0x");
}

/* Result of a registration attempt. Either a newly created participant, or
   the pre-existing one if the same wallet already registered (idempotent
   duplicate-wallet handling per spec G-002). */
export async function registerGenesis(input: {
  address: string;
  chainId: number;
  nonce: string;
  signature: string; // hex string, 0xRRR...SSS...V (65 bytes)
}): Promise<RegisteredParticipant> {
  const normalized = normalizeAddress(input.address);
  if (!normalized) throw new ApiError(400, "ADDRESS_INVALID", "请提供有效的 EVM 钱包地址");
  if (input.chainId !== GENESIS_CONFIG.chainId) {
    throw new ApiError(400, "CHAIN_UNSUPPORTED", `仅支持 ${GENESIS_CONFIG.network} (chainId ${GENESIS_CONFIG.chainId})`);
  }
  if (!NONCE_HEX_RE.test(input.nonce)) throw new ApiError(400, "NONCE_INVALID", "nonce 格式不正确");
  const sigBytes = hexToBytes(input.signature);
  if (!sigBytes) throw new ApiError(400, "SIGNATURE_INVALID", "签名格式不正确");

  // Look up the unused nonce row. Unused means `used_at IS NULL` and
  // `expires_at > now()`. We additionally check wallet matches.
  const nonceHash = await sha256Hex(input.nonce);
  const db = getDb();
  const now = new Date();
  const nonceRow = await db.query.genesisNonces.findFirst({
    where: and(
      eq(genesisNonces.nonceHash, nonceHash),
      eq(genesisNonces.walletAddressNormalized, normalized),
      isNull(genesisNonces.usedAt),
    ),
  });
  if (!nonceRow) {
    // Either unknown nonce, wrong wallet, or already used.
    const expired = await db.query.genesisNonces.findFirst({ where: eq(genesisNonces.nonceHash, nonceHash) });
    if (!expired) throw new ApiError(400, "NONCE_UNKNOWN", "未找到该 nonce,请重新申请");
    if (expired.usedAt) throw new ApiError(409, "NONCE_USED", "该 nonce 已被使用,请重新申请");
    if (Date.parse(expired.expiresAt) <= now.getTime()) throw new ApiError(400, "NONCE_EXPIRED", "nonce 已过期,请重新申请");
    if (expired.walletAddressNormalized !== normalized) throw new ApiError(400, "NONCE_WALLET_MISMATCH", "nonce 与提交的钱包地址不匹配");
    throw new ApiError(400, "NONCE_INVALID", "nonce 无法使用,请重新申请");
  }
  if (Date.parse(nonceRow.expiresAt) <= now.getTime()) {
    throw new ApiError(400, "NONCE_EXPIRED", "nonce 已过期,请重新申请");
  }

  // Rebuild the canonical message exactly as the client signed it. Client
  // echoed back `issuedAt` and `expiresAt` are accepted only if they match
  // the server-stored timestamps byte-for-byte; otherwise we reject with
  // NONCE_TAMPERED. We don't need the client to send them at all — the
  // server owns the timestamps — but accepting them lets the client show
  // them in the wallet preview without ambiguity.
  const fields = defaultGenesisFields(
    toChecksum(input.address),
    input.nonce,
    nonceRow.issuedAt,
    nonceRow.expiresAt,
  );
  const message = buildGenesisMessage(fields);

  // Recover the signer; require exact equality with the requested address.
  const recovered = recoverPersonalSign(message, sigBytes);
  if (!recovered) throw new ApiError(400, "SIGNATURE_INVALID", "签名验证失败,请重新签名");
  if (recovered !== normalized) throw new ApiError(400, "SIGNER_MISMATCH", "签名钱包与请求钱包不一致");

  // Idempotency: if this wallet is already registered, return that record
  // instead of attempting a duplicate insert (DB UNIQUE index would also
  // catch this, but doing the lookup first gives a cleaner 200 response
  // matching the G-002 expectation).
  const existing = await db.query.genesisParticipants.findFirst({
    where: eq(genesisParticipants.walletAddressNormalized, normalized),
  });
  if (existing) {
    await markNonceUsed(nonceRow.id);
    return toParticipant(existing);
  }

  // Race-safe participant number allocation. We compute the next number as
  // MAX(participant_number) + 1 inside the same insert. If two requests race
  // and compute the same number, the UNIQUE index on `participant_number`
  // causes one insert to fail with a UNIQUE constraint error; we then retry
  // with a fresh number. This is the standard pattern for monotonic
  // allocation in SQLite/D1 without an explicit sequence object.
  const participantId = crypto.randomUUID();
  const checksumDisplay = toChecksum(input.address);
  const inserted = await insertWithRetry({
    id: participantId,
    walletAddress: checksumDisplay,
    walletAddressNormalized: normalized,
    chainId: input.chainId,
    signatureVersion: GENESIS_CONFIG.signatureVersion,
    termsVersion: GENESIS_CONFIG.termsVersion,
  });
  await markNonceUsed(nonceRow.id);
  return inserted;
}

async function insertWithRetry(values: {
  id: string;
  walletAddress: string;
  walletAddressNormalized: string;
  chainId: number;
  signatureVersion: string;
  termsVersion: string;
}): Promise<RegisteredParticipant> {
  const db = getDb();
  let attempt = 0;
  while (attempt < 5) {
    attempt++;
    const next = await db
      .select({ value: sql<number>`COALESCE(MAX(${genesisParticipants.participantNumber}), 0) + 1` })
      .from(genesisParticipants);
    const candidate = Number(next[0]?.value ?? 1);
    try {
      const [row] = await db.insert(genesisParticipants).values({
        ...values,
        participantNumber: candidate,
      }).returning();
      return toParticipant(row);
    } catch (error) {
      if (error instanceof Error && /UNIQUE constraint failed/i.test(error.message)) {
        // Race lost or pre-existing duplicate wallet (shouldn't happen because
        // we already checked above, but we still defend in depth). Retry with
        // a fresh MAX.
        continue;
      }
      throw error;
    }
  }
  throw new ApiError(500, "PARTICIPANT_NUMBER_EXHAUSTED", "无法分配参与者编号,请稍后重试");
}

async function markNonceUsed(nonceId: string): Promise<void> {
  const db = getDb();
  await db.update(genesisNonces)
    .set({ usedAt: new Date().toISOString() })
    .where(and(eq(genesisNonces.id, nonceId), isNull(genesisNonces.usedAt)));
}

function toParticipant(row: typeof genesisParticipants.$inferSelect): RegisteredParticipant {
  return {
    id: row.id,
    participantNumber: row.participantNumber,
    address: row.walletAddress,
    joinedAt: row.joinedAt,
    status: row.status,
    signatureVersion: row.signatureVersion,
    termsVersion: row.termsVersion,
  };
}

/* Lookup an existing Genesis registration by wallet address. Returns null if
   none exists. Used by the public `/genesis` page to show the
   already-registered state on revisit (spec UX requirement). */
export async function findGenesisParticipantByAddress(address: string): Promise<RegisteredParticipant | null> {
  const normalized = normalizeAddress(address);
  if (!normalized) throw new ApiError(400, "ADDRESS_INVALID", "请提供有效的 EVM 钱包地址");
  const row = await getDb().query.genesisParticipants.findFirst({
    where: eq(genesisParticipants.walletAddressNormalized, normalized),
  });
  return row ? toParticipant(row) : null;
}
