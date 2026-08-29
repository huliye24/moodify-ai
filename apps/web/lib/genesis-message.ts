/* MOOD-GENESIS-002: Canonical Genesis registration message template +
   EIP-191 `personal_sign` signature recovery.

   The human-readable message is deterministic: identical inputs on the
   client (when the user clicks "Sign") and on the server (when reconstructing
   for verification) must produce byte-for-byte the same string. The signed
   payload is exactly that string with the EIP-191 prefix
   "\x19Ethereum Signed Message:\n<length>" applied per the standard.

   The message MUST include an explicit statement that the signature does not
   authorize any token transfer. This is a product-bound contract: any
   change to the wording requires bumping `signatureVersion` in
   `genesis-config.ts`. */

import { GENESIS_CONFIG } from "./genesis-config";

export type GenesisMessageFields = {
  address: string; // checksum form (display only; server compares normalized)
  chainId: number;
  nonce: string;
  issuedAt: string; // ISO 8601
  expiresAt: string; // ISO 8601
  termsVersion: string;
  signatureVersion: string;
  domain: string;
};

/* Build the exact human-readable string the wallet signs. Whitespace and
   ordering are part of the contract; do not reorder fields. */
export function buildGenesisMessage(fields: GenesisMessageFields): string {
  const lines = [
    "Moodify Protocol Genesis Registration",
    "",
    `Wallet: ${fields.address}`,
    `Chain ID: ${fields.chainId}`,
    `Nonce: ${fields.nonce}`,
    `Issued At: ${fields.issuedAt}`,
    `Expires At: ${fields.expiresAt}`,
    `Signature Version: ${fields.signatureVersion}`,
    `Terms Version: ${fields.termsVersion}`,
    `Domain: ${fields.domain}`,
    "",
    "I am registering this wallet as a Moodify Genesis Participant.",
    "This signature does not authorize any token transfer or transaction.",
  ];
  return lines.join("\n");
}

/* Default field bundle matching GENESIS_CONFIG. The caller (API route) fills
   in `address` and `nonce`; everything else is the active protocol constant. */
export function defaultGenesisFields(address: string, nonce: string, issuedAt: string, expiresAt: string): GenesisMessageFields {
  return {
    address,
    chainId: GENESIS_CONFIG.chainId,
    nonce,
    issuedAt,
    expiresAt,
    termsVersion: GENESIS_CONFIG.termsVersion,
    signatureVersion: GENESIS_CONFIG.signatureVersion,
    domain: GENESIS_CONFIG.officialDomain,
  };
}

/* EIP-191 `personal_sign` digest = keccak256( "\x19Ethereum Signed Message:\n"
   + len(message) + message ). Returns the 32-byte digest. */
export function personalSignDigest(message: string): Uint8Array {
  const prefix = new TextEncoder().encode(`\x19Ethereum Signed Message:\n${message.length}`);
  const body = new TextEncoder().encode(message);
  const combined = new Uint8Array(prefix.length + body.length);
  combined.set(prefix, 0);
  combined.set(body, prefix.length);
  return keccak256Bytes(combined);
}

/* Hex helpers used here and re-exported for convenience. */
const HEX = "0123456789abcdef";

export function bytesToHex(bytes: Uint8Array): string {
  let out = "";
  for (let i = 0; i < bytes.length; i++) {
    const v = bytes[i];
    out += HEX[(v >> 4) & 0x0f] + HEX[v & 0x0f];
  }
  return out;
}

export function hexToBytes(hex: string): Uint8Array | null {
  const trimmed = hex.startsWith("0x") ? hex.slice(2) : hex;
  if (!/^[0-9a-fA-F]*$/.test(trimmed)) return null;
  if (trimmed.length % 2 !== 0) return null;
  const out = new Uint8Array(trimmed.length / 2);
  for (let i = 0; i < out.length; i++) {
    out[i] = parseInt(trimmed.slice(i * 2, i * 2 + 2), 16);
  }
  return out;
}

/* Self-contained Keccak-256. Duplicated here from evm-address.ts to keep this
   module importable from both client and server without circular dependencies.
   Both implementations are byte-equivalent. */
const KECCAK_RC = [
  0x0000000000000001n, 0x0000000000008082n, 0x800000000000808an, 0x8000000080008000n,
  0x000000000000808bn, 0x0000000080000001n, 0x8000000080008081n, 0x8000000000008009n,
  0x000000000000008an, 0x0000000000000088n, 0x0000000080008009n, 0x000000008000000an,
  0x000000008000808bn, 0x800000000000008bn, 0x8000000000008089n, 0x8000000000008003n,
  0x8000000000008002n, 0x8000000000000080n, 0x000000000000800an, 0x800000008000000an,
  0x8000000080008081n, 0x8000000000008080n, 0x0000000080000001n, 0x8000000080008008n,
];

const KECCAK_R = [
  [0, 1, 62, 28, 27],
  [36, 44, 6, 55, 20],
  [3, 10, 43, 25, 39],
  [41, 45, 15, 21, 8],
  [18, 2, 61, 56, 14],
];

const MASK64 = (1n << 64n) - 1n;

function rotl(x: bigint, n: number): bigint {
  return ((x << BigInt(n)) | (x >> BigInt(64 - n))) & MASK64;
}

function keccak256Bytes(input: Uint8Array): Uint8Array {
  const state = new Array<bigint>(25).fill(0n);
  const rate = 136;
  const padded = new Uint8Array(Math.ceil((input.length + 1) / rate) * rate);
  padded.set(input);
  padded[input.length] = 0x01;
  padded[padded.length - 1] |= 0x80;

  for (let block = 0; block < padded.length; block += rate) {
    for (let i = 0; i < rate / 8; i++) {
      let lane = 0n;
      for (let b = 0; b < 8; b++) {
        lane |= BigInt(padded[block + i * 8 + b]) << BigInt(b * 8);
      }
      state[i] = (state[i] ^ lane) & MASK64;
    }
    for (let round = 0; round < 24; round++) {
      const c = new Array<bigint>(5);
      for (let x = 0; x < 5; x++) {
        c[x] = state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20];
      }
      const d = new Array<bigint>(5);
      for (let x = 0; x < 5; x++) {
        d[x] = c[(x + 4) % 5] ^ rotl(c[(x + 1) % 5], 1);
      }
      for (let i = 0; i < 25; i++) state[i] = (state[i] ^ d[i % 5]) & MASK64;
      const bArr = new Array<bigint>(25);
      for (let x = 0; x < 5; x++) {
        for (let y = 0; y < 5; y++) {
          const idx = x + 5 * y;
          bArr[y + 5 * ((2 * x + 3 * y) % 5)] = rotl(state[idx], KECCAK_R[y][x]);
        }
      }
      for (let y = 0; y < 5; y++) {
        for (let x = 0; x < 5; x++) {
          state[x + 5 * y] = (bArr[x + 5 * y] ^ ((~bArr[((x + 1) % 5) + 5 * y]) & bArr[((x + 2) % 5) + 5 * y])) & MASK64;
        }
      }
      state[0] = (state[0] ^ KECCAK_RC[round]) & MASK64;
    }
  }

  const out = new Uint8Array(32);
  for (let i = 0; i < 4; i++) {
    let lane = state[i];
    for (let b = 0; b < 8; b++) {
      out[i * 8 + b] = Number(lane & 0xffn);
      lane >>= 8n;
    }
  }
  return out;
}

/* Recover the signing address (lowercase) from an EIP-191 `personal_sign`
   signature and the original message string. The signature must be 65 bytes
   formatted as R || S || V, with V as 27 or 28 (or the EIP-155 normalized
   values 0/1). Returns null if the signature is malformed or recovery
   fails. */
export function recoverPersonalSign(message: string, signature: Uint8Array): string | null {
  if (signature.length !== 65) return null;
  const r = readBig(signature, 0, 32);
  const s = readBig(signature, 32, 32);
  const vRaw = signature[64];
  // EIP-2 malleability guard: S must be in the lower half-order.
  // SECP256K1_N is the module-level constant from the secp256k1 block below;
  // we reuse it here rather than re-declaring it.
  if (r <= 0n || r >= SECP256K1_N) return null;
  if (s <= 0n || s > SECP256K1_N_HALF) return null;
  if (vRaw !== 27 && vRaw !== 28 && vRaw !== 0 && vRaw !== 1) return null;
  const recovery = vRaw >= 27 ? vRaw - 27 : vRaw;
  const digest = personalSignDigest(message);
  const recovered = ecrecover(digest, recovery, r, s);
  return recovered ? "0x" + recovered.toLowerCase().slice(-40) : null;
}

function readBig(bytes: Uint8Array, offset: number, length: number): bigint {
  let n = 0n;
  for (let i = 0; i < length; i++) {
    n |= BigInt(bytes[offset + i]) << BigInt(i * 8);
  }
  return n;
}

/* Minimal secp256k1 point arithmetic for public-key recovery. This is a
   well-known algorithm used by every Ethereum client; we re-implement it here
   to avoid pulling in a 100+ KB crypto library just for `ecrecover`.

   Constants: y² = x³ + 7 over GF(P) where P = 2^256 − 2^32 − 977. */
const SECP256K1_P = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2fn;
const SECP256K1_N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141n;
const SECP256K1_N_HALF = SECP256K1_N >> 1n;
const SECP256K1_GX = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798n;
const SECP256K1_GY = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8n;
/* High bit of the 256-bit coordinate, used as the EIP-2098 / secp256k1
   "y is odd" recovery parity bit mask. */
const SECP256K1_X_HIGH_BIT = (1n << 255n);

type Point = { x: bigint; y: bigint };

function mod(a: bigint, p: bigint = SECP256K1_P): bigint {
  const r = a % p;
  return r < 0n ? r + p : r;
}

function modInv(a: bigint, p: bigint): bigint {
  // Extended Euclidean
  let [oldR, r] = [a, p];
  let [oldS, s] = [1n, 0n];
  while (r !== 0n) {
    const q = oldR / r;
    [oldR, r] = [r, oldR - q * r];
    [oldS, s] = [s, oldS - q * s];
  }
  return mod(oldS, p);
}

function pointDouble(p: Point): Point {
  const slope = mod(mod(3n * p.x * p.x) * modInv(2n * p.y, SECP256K1_P));
  const x = mod(slope * slope - 2n * p.x);
  const y = mod(slope * (p.x - x) - p.y);
  return { x, y };
}

function pointAdd(p: Point, q: Point): Point {
  if (p.x === q.x && p.y === q.y) return pointDouble(p);
  if (p.x === q.x) return { x: 0n, y: 0n }; // infinity
  const slope = mod((q.y - p.y) * modInv(q.x - p.x, SECP256K1_P));
  const x = mod(slope * slope - p.x - q.x);
  const y = mod(slope * (p.x - x) - p.y);
  return { x, y };
}

function scalarMul(k: bigint, p: Point): Point {
  let result: Point = { x: 0n, y: 0n };
  let addend = p;
  let scalar = mod(k, SECP256K1_N);
  while (scalar > 0n) {
    if ((scalar & 1n) === 1n) result = result.x === 0n && result.y === 0n ? addend : pointAdd(result, addend);
    addend = pointDouble(addend);
    scalar >>= 1n;
  }
  return result;
}

function ecrecover(digest: Uint8Array, recovery: number, r: bigint, s: bigint): string | null {
  if (r <= 0n || r >= SECP256K1_N) return null;
  if (s <= 0n || s >= SECP256K1_N) return null;
  // x = r + recovery bit in the high position
  let x = r;
  if (recovery & 2) x |= SECP256K1_X_HIGH_BIT;
  if (x >= SECP256K1_P) return null;
  // y² = x³ + 7 (mod P)
  const ySquared = mod(mod(mod(x * x) * x) + 7n);
  let y = modPow(ySquared, (SECP256K1_P + 1n) / 4n, SECP256K1_P);
  if (y === 0n) return null;
  if ((y & 1n) !== BigInt(recovery & 1)) y = SECP256K1_P - y;
  const R: Point = { x, y };
  const rInv = modInv(r, SECP256K1_N);
  const z = readBig(digest, 0, 32);
  const u1 = mod(-z * rInv, SECP256K1_N);
  const u2 = mod(s * rInv, SECP256K1_N);
  const Q = pointAdd(scalarMul(u1, { x: SECP256K1_GX, y: SECP256K1_GY }), scalarMul(u2, R));
  if (Q.x === 0n && Q.y === 0n) return null;
  // Address = keccak256(Qx || Qy)[12:32]
  const pub = new Uint8Array(64);
  for (let i = 0; i < 32; i++) {
    pub[i] = Number((Q.x >> BigInt(i * 8)) & 0xffn);
    pub[32 + i] = Number((Q.y >> BigInt(i * 8)) & 0xffn);
  }
  const hashed = keccak256Bytes(pub);
  return bytesToHex(hashed.slice(12));
}

function modPow(base: bigint, exp: bigint, mod: bigint): bigint {
  let result = 1n;
  let b = base % mod;
  let e = exp;
  while (e > 0n) {
    if ((e & 1n) === 1n) result = (result * b) % mod;
    b = (b * b) % mod;
    e >>= 1n;
  }
  return result;
}
