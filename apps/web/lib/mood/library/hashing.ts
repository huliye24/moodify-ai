// MOOD LIBRARY 014 — SHA-256 hashing utility
// Authority: docs/mood/library/014_HASH_POLICY.md

/**
 * Compute SHA-256 of a UTF-8 string.
 * Returns lowercase hex digest (64 chars).
 *
 * Works in both Node.js and Edge/browser environments
 * via Web Crypto API.
 */
export async function sha256OfText(text: string): Promise<string> {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * Compute SHA-256 of a file's contents (browser File API).
 */
export async function sha256OfFile(file: File): Promise<string> {
  const buf = await file.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * Format a SHA-256 for display.
 * Accepts full or short digest; returns `first16…last8` form.
 */
export function formatSha256(sha256: string | undefined): string {
  if (!sha256 || sha256.length < 32) return "Hash unavailable";
  return `${sha256.slice(0, 16)}…${sha256.slice(-8)}`;
}

/**
 * Mark provenance as unverified if SHA-256 cannot be cross-checked.
 */
export function provenanceLabel(opts: {
  sha256?: string;
  sourceSha?: string;
  pdfUrl?: string;
}): "verified" | "unverified" | "source-only" {
  if (opts.pdfUrl && !opts.sha256) return "unverified";
  if (opts.sha256 && opts.sourceSha) return "verified";
  if (opts.sourceSha) return "source-only";
  return "unverified";
}