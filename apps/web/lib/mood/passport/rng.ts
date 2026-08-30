/**
 * MOOD PASSPORT 015 — RNG Abstraction
 *
 * Foundation use only: uses globalThis.crypto.getRandomValues.
 * Test harness injects its own RNG for determinism.
 */

export function globalRngBytes(length: number): Uint8Array {
  const buf = new Uint8Array(length);
  globalThis.crypto.getRandomValues(buf);
  return buf;
}
