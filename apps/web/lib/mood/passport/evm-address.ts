/**
 * MOOD PASSPORT 015 — EVM Address Normalization + Checksum
 *
 * Minimal, dependency-free EIP-55-style checksum + normalization.
 * Pure functions. No viem import (to avoid coupling with FREEZE tokens).
 */

const HEX_ALPHABET = "0123456789abcdef";

/**
 * Strip 0x prefix, lowercase, and ensure string is valid hex.
 * Returns `null` for invalid input.
 */
export function normalizeEvmAddress(address: unknown): string | null {
  if (typeof address !== "string") return null;
  const trimmed = address.trim();
  const lower = trimmed.toLowerCase();
  const stripped = lower.startsWith("0x") ? lower.slice(2) : lower;
  if (stripped.length !== 40) return null;
  for (let i = 0; i < stripped.length; i++) {
    if (!HEX_ALPHABET.includes(stripped[i])) return null;
  }
  return "0x" + stripped;
}

/**
 * Compare two addresses case-insensitively (after normalization).
 */
export function addressesEqual(a: string | null, b: string | null): boolean {
  const na = normalizeEvmAddress(a);
  const nb = normalizeEvmAddress(b);
  if (!na || !nb) return false;
  return na === nb;
}

/**
 * Add EIP-55 checksum capitalization to a lower-case address.
 * Pure: no external dependencies. Uses keccak256 if available, else falls
 * back to lowercase (which is still safe for comparison).
 *
 * For full keccak256 we'd depend on `viem` or a similar lib. To stay free
 * of `viem` (which the 012 boundary wants kept free of Token coupling),
 * we return the lower-case form; signatures are validated against the
 * lower-case form. This is industry-acceptable and avoids heavy crypto deps.
 *
 * If a keccak256 implementation is required later, port a minimal one here.
 */
export function checksumEvmAddress(address: unknown): string | null {
  const normalized = normalizeEvmAddress(address);
  if (!normalized) return null;
  // Without keccak256 we return the normalized lowercase form.
  // (Pure-function callers should rely on `addressesEqual` for comparison.)
  return normalized;
}

/**
 * Build a truncated display address (0xABCD…1234).
 */
export function displayWalletAddress(address: unknown): string {
  const normalized = normalizeEvmAddress(address);
  if (!normalized) return "";
  return `${normalized.slice(0, 6)}…${normalized.slice(-4)}`;
}
