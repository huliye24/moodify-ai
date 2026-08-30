/**
 * MOOD PASSPORT 015 — Active Policy Lookups
 *
 * Passport onboarding reads from the 014 Library registry for active
 * policies. This module provides a passive filter:
 *
 *   - active policies may be recorded as accepted
 *   - draft policies MAY be displayed informationally but MAY NOT be
 *     recorded as accepted (consent is private + per-version)
 *
 * The Library registry source is `apps/web/lib/mood/library/registry.ts`
 * (built in 014). This module accepts a snapshot via dependency injection
 * to avoid circular imports.
 */

import type { LibraryDocument } from "../library/types.ts";

/**
 * Filter to active-only documents that look like privacy / policy / terms
 * candidates. The actual "this is the Privacy Policy you must accept" mapping
 * is decided by the Library registry's `slug` values. 014 already uses:
 *   - mood-canon
 *   - public-brand-constitution
 *   - public-form-canon
 *   - mood-product-relationship
 *   - mood-launch-gate
 *
 * v1 mandatory policies for Passport onboarding (subject to human sign-off):
 *   - privacy-policy          : Optional until governance defines a real one
 *   - terms-of-service        : Optional until governance defines a real one
 *   - wallet-signature-policy : 015's own SIWE/SIWS-style policy
 *
 * Until real governance documents exist, this function falls back to the
 * docs/mood/ canon documents as "informational, not mandatory".
 */
export interface PassportPolicyCandidate {
  slug: string;
  title: string;
  version: string;
  status: string;
  mandatory: boolean;
  reason: string;
}

const MANDATORY_SLUGS: ReadonlySet<string> = new Set([
  // No policy is currently MANDATORY in the foundation state. Listed here so
  // that a future governance-approved slug becomes mandatory automatically.
  // e.g. "privacy-policy-v1" when ratified.
]);

export function classifyPolicy(
  doc: LibraryDocument,
): PassportPolicyCandidate {
  const slug = doc.slug;
  const status = doc.status;

  let mandatory = false;
  let reason = "informational";

  if (MANDATORY_SLUGS.has(slug)) {
    mandatory = true;
    reason = "marked-mandatory";
  }
  if (status !== "active") {
    mandatory = false;
    if (status === "draft") reason = "draft-not-mandatory";
    else if (status === "superseded") reason = "superseded-not-mandatory";
    else if (status === "archived") reason = "archived-not-mandatory";
    else reason = "inactive";
  }

  return {
    slug,
    title: doc.title,
    version: doc.version,
    status,
    mandatory,
    reason,
  };
}

export function listActivePolicyCandidates(
  docs: ReadonlyArray<LibraryDocument>,
): PassportPolicyCandidate[] {
  const candidates: PassportPolicyCandidate[] = [];
  for (const d of docs) {
    const c = classifyPolicy(d);
    if (c.status === "active" || c.status === "draft") {
      // Show active AND draft so users can read drafts, but mark draft
      // as not-mandatory in the consumer (see `classifyPolicy`).
      candidates.push(c);
    }
  }
  return candidates;
}
