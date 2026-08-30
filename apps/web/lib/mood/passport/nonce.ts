/**
 * MOOD PASSPORT 015 — Nonce Registry
 *
 * Single-use nonce records with expiry and address-binding.
 *
 * Storage: in-memory. This is intentional under foundation launch:
 *   - We do NOT require a database for Passport to render & sign-in.
 *   - A future INTEGRATION package (e.g. 026) may move nonces to D1.
 *
 * Properties enforced (verified by tests/passport-invariants.test.mjs):
 *   - nonce creation produces random opaque string
 *   - expiry: `isExpired` returns true once `now > expiresAt`
 *   - single-use: `consumeNonce` returns true exactly once
 *   - address-bound: nonces are tagged with their bound normalized address
 *   - sweepExpired periodically cleans up consumed/expired entries
 *   - shape validation: nonces have ≥ 16 chars and no whitespace
 */

import { globalRngBytes } from "./rng.ts";
import { normalizeEvmAddress } from "./evm-address.ts";
import type { NonceRecord } from "./types.ts";

const DEFAULT_NONCE_TTL_MS = 15 * 60 * 1000; // 15 minutes
const NONCE_BYTES = 16;
const DEFAULT_MAX_ENTRIES = 10_000;
const DEFAULT_SWEEP_INTERVAL_MS = 60_000;

function nowIso(): string {
  return new Date().toISOString();
}

function genNonce(): string {
  const bytes = globalRngBytes(NONCE_BYTES);
  let hex = "";
  for (let i = 0; i < bytes.length; i++) {
    hex += (bytes[i] ?? 0).toString(16).padStart(2, "0");
  }
  return hex;
}

function isValidNonceString(n: string): boolean {
  if (typeof n !== "string") return false;
  if (n.length < 16) return false;
  if (n.length > 128) return false;
  if (/\s/.test(n)) return false;
  for (let i = 0; i < n.length; i++) {
    const c = n[i];
    if (!c || !"0123456789abcdefABCDEF".includes(c)) return false;
  }
  return true;
}

export interface NonceRegistryOptions {
  ttlMs?: number;
  maxEntries?: number;
  now?: () => number;
}

export class NonceRegistry {
  private store: Map<string, NonceRecord> = new Map();
  private ttlMs: number;
  private maxEntries: number;
  private now: () => number;
  private sweepTimer: ReturnType<typeof setInterval> | null = null;

  constructor(opts: NonceRegistryOptions = {}) {
    this.ttlMs = opts.ttlMs ?? DEFAULT_NONCE_TTL_MS;
    this.maxEntries = opts.maxEntries ?? DEFAULT_MAX_ENTRIES;
    this.now = opts.now ?? (() => Date.now());
  }

  /**
   * Allocate a new single-use nonce bound to `address`.
   * The nonce string is opaque; clients must send it back unchanged.
   */
  issue(address: string): { nonce: string; expiresAt: string } {
    if (this.store.size >= this.maxEntries) this.sweepExpired();

    const boundAddress = normalizeEvmAddress(address);
    if (!boundAddress) throw new Error("invalid-address");

    const value = genNonce();
    const createdMs = this.now();
    const expiresMs = createdMs + this.ttlMs;
    const record: NonceRecord = {
      value,
      address: boundAddress,
      createdAt: new Date(createdMs).toISOString(),
      expiresAt: new Date(expiresMs).toISOString(),
      used: false,
    };
    this.store.set(value, record);
    return { nonce: value, expiresAt: record.expiresAt };
  }

  /**
   * Look up a nonce record for validation. Does NOT consume.
   */
  peek(nonce: string): NonceRecord | null {
    if (!isValidNonceString(nonce)) return null;
    return this.store.get(nonce) ?? null;
  }

  /**
   * Mark a nonce as used. Returns true on success; false if not found /
   * already used / expired / mismatched address.
   */
  consume(nonce: string, address: string): { ok: boolean; reason?: string } {
    const record = this.peek(nonce);
    if (!record) return { ok: false, reason: "not-found" };
    if (record.used) return { ok: false, reason: "already-used" };
    if (this.isExpired(record)) return { ok: false, reason: "expired" };

    const boundAddress = normalizeEvmAddress(address);
    if (!boundAddress) return { ok: false, reason: "invalid-address" };
    if (record.address !== boundAddress) {
      return { ok: false, reason: "address-mismatch" };
    }
    record.used = true;
    return { ok: true };
  }

  /**
   * Destroy a nonce immediately (e.g. logout / cancellation).
   */
  revoke(nonce: string): boolean {
    const record = this.peek(nonce);
    if (!record) return false;
    record.used = true;
    return true;
  }

  isExpired(record: NonceRecord): boolean {
    const expiresMs = new Date(record.expiresAt).getTime();
    if (Number.isNaN(expiresMs)) return true;
    return this.now() > expiresMs;
  }

  sweepExpired(): number {
    const removed: string[] = [];
    for (const [k, v] of this.store.entries()) {
      if (v.used || this.isExpired(v)) removed.push(k);
    }
    for (const k of removed) this.store.delete(k);
    return removed.length;
  }

  /**
   * Start a periodic sweep. Stop with stopSweep().
   * Tests should not enable this.
   */
  startSweep(intervalMs = DEFAULT_SWEEP_INTERVAL_MS): void {
    if (this.sweepTimer) return;
    this.sweepTimer = setInterval(() => this.sweepExpired(), intervalMs);
    // Allow Node process to exit cleanly even if the timer is still running.
    if (typeof this.sweepTimer.unref === "function") {
      this.sweepTimer.unref();
    }
  }

  stopSweep(): void {
    if (this.sweepTimer) {
      clearInterval(this.sweepTimer);
      this.sweepTimer = null;
    }
  }

  /**
   * Return the number of live (unused & not-expired) nonces.
   */
  live(): number {
    let count = 0;
    for (const v of this.store.values()) {
      if (!v.used && !this.isExpired(v)) count++;
    }
    return count;
  }

  /**
   * Total records (including used/expired, before sweep).
   */
  size(): number {
    return this.store.size;
  }

  /**
   * Clear all records. Used in tests.
   */
  reset(): void {
    this.store.clear();
  }
}

/**
 * Default singleton (foundation uses in-memory).
 * Tests should construct their own registry.
 */
export const defaultNonceRegistry = new NonceRegistry();
