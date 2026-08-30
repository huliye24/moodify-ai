/**
 * MOOD CONTRIBUTION 016 — Evidence Policy
 *
 * Validates evidence records before persistence.
 * Authority: MOOD-CONTRIBUTION-016 TASK.md Phase E.
 *
 * - URL: must be http(s), reject javascript:, data:, file: etc.
 * - GitHub PR / commit: must look like a GitHub URL.
 * - Document / artifact / text: bounded length.
 */

import type { EvidenceType, ContributionEvidence } from "./types.ts";

export const MAX_EVIDENCE_PER_SUBMISSION = 20;
export const MAX_EVIDENCE_TEXT_LENGTH = 5000;
export const MAX_EVIDENCE_URL_LENGTH = 2048;
export const MAX_EVIDENCE_DOCUMENT_LENGTH = 5000;

const SAFE_URL_PROTOCOLS = new Set(["http:", "https:"]);

export interface EvidenceValidationError {
  ok: false;
  code: string;
  message: string;
}

export interface EvidenceValidationOk {
  ok: true;
}

export type EvidenceValidation = EvidenceValidationOk | EvidenceValidationError;

export function validateEvidence(
  input: { type: EvidenceType; value: string; label?: string },
): EvidenceValidation {
  if (!input.value || typeof input.value !== "string") {
    return { ok: false, code: "missing-value", message: "Evidence value required" };
  }

  if (input.label && input.label.length > 200) {
    return { ok: false, code: "label-too-long", message: "Label must be ≤ 200 chars" };
  }

  switch (input.type) {
    case "url": {
      if (input.value.length > MAX_EVIDENCE_URL_LENGTH) {
        return { ok: false, code: "url-too-long", message: "URL too long" };
      }
      let url: URL;
      try {
        url = new URL(input.value);
      } catch {
        return { ok: false, code: "invalid-url", message: "Invalid URL" };
      }
      if (!SAFE_URL_PROTOCOLS.has(url.protocol)) {
        return { ok: false, code: "unsafe-scheme", message: `Unsafe scheme: ${url.protocol}` };
      }
      return { ok: true };
    }
    case "github-pr":
    case "github-commit": {
      if (input.value.length > MAX_EVIDENCE_URL_LENGTH) {
        return { ok: false, code: "url-too-long", message: "GitHub URL too long" };
      }
      let url: URL;
      try {
        url = new URL(input.value);
      } catch {
        return { ok: false, code: "invalid-github-url", message: "Invalid GitHub URL" };
      }
      if (url.hostname !== "github.com" && url.hostname !== "www.github.com") {
        return {
          ok: false,
          code: "non-github-host",
          message: "GitHub PR/commit must be on github.com",
        };
      }
      return { ok: true };
    }
    case "text": {
      if (input.value.length > MAX_EVIDENCE_TEXT_LENGTH) {
        return { ok: false, code: "text-too-long", message: "Text evidence too long" };
      }
      return { ok: true };
    }
    case "document":
    case "artifact": {
      if (input.value.length > MAX_EVIDENCE_DOCUMENT_LENGTH) {
        return {
          ok: false,
          code: "document-too-long",
          message: "Document reference too long",
        };
      }
      return { ok: true };
    }
  }
}

export function isValidEvidenceArray(
  list: ReadonlyArray<Pick<ContributionEvidence, "type" | "value" | "label">>,
): EvidenceValidation {
  if (list.length > MAX_EVIDENCE_PER_SUBMISSION) {
    return {
      ok: false,
      code: "too-many-evidence",
      message: `At most ${MAX_EVIDENCE_PER_SUBMISSION} evidence items`,
    };
  }
  for (const e of list) {
    const v = validateEvidence(e);
    if (!v.ok) return v;
  }
  return { ok: true };
}