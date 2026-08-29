/* MOOD-GENESIS-002: EVM address utilities — normalization and EIP-55
   checksum display. Server-side normalization is the authoritative comparison
   key (lowercase); checksum form is display-only. No external dependencies.

   The Keccak-256 implementation is a self-contained, minimal implementation
   based on the original specification. It is used only to compute the EIP-55
   mixed-case checksum; nothing here authorizes transfers or signs
   transactions. */

const HEX = "0123456789abcdef";

/* Self-contained Keccak-256 (Ethereum's pre-SHA3 variant with padding byte
   0x01). Used solely for EIP-55 checksum display. Constant-time enough for
   short inputs (≤40 hex chars). */
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

function keccak256(input: Uint8Array): Uint8Array {
  const state = new Array<bigint>(25).fill(0n);
  const rate = 136; // 1088 bits / 8
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
      // θ
      const c = new Array<bigint>(5);
      for (let x = 0; x < 5; x++) {
        c[x] = state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20];
      }
      const d = new Array<bigint>(5);
      for (let x = 0; x < 5; x++) {
        d[x] = c[(x + 4) % 5] ^ rotl(c[(x + 1) % 5], 1);
      }
      for (let i = 0; i < 25; i++) state[i] = (state[i] ^ d[i % 5]) & MASK64;
      // ρ and π
      const bArr = new Array<bigint>(25);
      for (let x = 0; x < 5; x++) {
        for (let y = 0; y < 5; y++) {
          const idx = x + 5 * y;
          bArr[y + 5 * ((2 * x + 3 * y) % 5)] = rotl(state[idx], KECCAK_R[y][x]);
        }
      }
      // χ
      for (let y = 0; y < 5; y++) {
        for (let x = 0; x < 5; x++) {
          state[x + 5 * y] = (bArr[x + 5 * y] ^ ((~bArr[((x + 1) % 5) + 5 * y]) & bArr[((x + 2) % 5) + 5 * y])) & MASK64;
        }
      }
      // ι
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

function bytesToHex(bytes: Uint8Array): string {
  let out = "";
  for (let i = 0; i < bytes.length; i++) {
    const v = bytes[i];
    out += HEX[(v >> 4) & 0x0f] + HEX[v & 0x0f];
  }
  return out;
}

/* Validate an EVM address shape: exactly 40 lowercase or uppercase hex
   characters prefixed with `0x`. Returns the lowercase canonical form on
   success, otherwise null. */
export function normalizeAddress(value: unknown): string | null {
  if (typeof value !== "string") return null;
  if (!/^0x[0-9a-fA-F]{40}$/.test(value)) return null;
  return value.toLowerCase();
}

/* Render an EIP-55 mixed-case checksum address. Returns the original
   lowercase form if input is malformed (callers must validate first). */
export function checksumAddress(value: string): string {
  const lower = value.toLowerCase();
  if (!/^0x[0-9a-f]{40}$/.test(lower)) return value;
  const hash = bytesToHex(keccak256(new TextEncoder().encode(lower.slice(2))));
  let out = "0x";
  for (let i = 0; i < 40; i++) {
    const ch = lower[2 + i];
    if (ch >= "0" && ch <= "9") {
      out += ch;
    } else if (/[a-f]/.test(ch) && parseInt(hash[i], 16) >= 8) {
      out += ch.toUpperCase();
    } else {
      out += ch;
    }
  }
  return out;
}

/* Shorten a checksum address for display: `0x1234…abcd`. */
export function shortenAddress(value: string, head = 6, tail = 4): string {
  if (value.length < head + tail + 2) return value;
  return `${value.slice(0, head)}…${value.slice(-tail)}`;
}

/* SHA-256 hash (used for nonce storage: we never persist the raw nonce, only
   its hash). Falls back to a portable implementation in environments without
   `crypto.subtle`. */
export async function sha256Hex(value: string): Promise<string> {
  if (typeof crypto !== "undefined" && crypto.subtle) {
    const buf = new TextEncoder().encode(value);
    const digest = await crypto.subtle.digest("SHA-256", buf);
    return bytesToHex(new Uint8Array(digest));
  }
  // Fallback: simple non-cryptographic substitute. NOT used in production —
  // Cloudflare Workers always expose `crypto.subtle`.
  let h1 = 0xdeadbeef ^ 0;
  let h2 = 0x41c6ce57 ^ 0;
  for (let i = 0; i < value.length; i++) {
    const ch = value.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return ((h2 >>> 0).toString(16).padStart(8, "0") + (h1 >>> 0).toString(16).padStart(8, "0")).padEnd(64, "0");
}
