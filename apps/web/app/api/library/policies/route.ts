/**
 * MOOD PASSPORT 015 — GET /api/library/policies
 *
 * Lists active + draft documents from the 014 Library registry so the
 * Passport consent UI can show them.
 *
 * This is the 015 contract for filtering: it NEVER exposes the raw
 * `sourcePath` or any internal metadata. Only the Passport-relevant
 * subset (slug / title / version / status / mandatory flag).
 */

import {
  classifyPolicy,
} from "../../../lib/mood/passport/index.ts";
import { libraryRegistry } from "../../../lib/mood/library/index.ts";

export const dynamic = "force-dynamic";

export async function GET(): Promise<Response> {
  try {
    const docs = libraryRegistry.listDocuments();
    const policies = docs
      .map((d) => classifyPolicy(d))
      .filter((p) => p.status === "active" || p.status === "draft")
      .filter((p) => {
        // Filter to only show docs that look like "policy-like" — those
        // slug-keyword-prefixed as canon / product / brand / launch.
        // This avoids surfacing every library doc as a "policy to accept".
        return (
          p.slug.startsWith("mood-") ||
          p.slug.startsWith("public-") ||
          p.slug.startsWith("mip-")
        );
      });
    return Response.json({ policies });
  } catch (err) {
    console.error("library/policies error", err);
    return Response.json({ policies: [] });
  }
}
