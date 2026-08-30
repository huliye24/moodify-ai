/**
 * MOOD PASSPORT 015 — GET /api/resident/me/consents
 *
 * Owner-only. Returns consent history for the current Resident.
 */

import { defaultResidentRegistry } from "@/lib/mood/passport/index.ts";
import { jsonError, requireResident } from "@/app/api/identity/_helpers.ts";

export const dynamic = "force-dynamic";

export async function GET(request: Request): Promise<Response> {
  try {
    const resident = requireResident(request);
    if (!resident) return jsonError(401, "UNAUTHORIZED", "no session");
    const consents = defaultResidentRegistry.listConsents(resident.id);
    return Response.json({ consents });
  } catch (err) {
    console.error("resident/me/consents error", err);
    return jsonError(500, "INTERNAL", "consents failed");
  }
}

/**
 * POST /api/resident/me/consents
 *
 * Body: { policySlug: string, policyVersion: string, policyStatus: "active" | "draft" | ... }
 * Only `policyStatus === "active"` is accepted.
 */
export async function POST(request: Request): Promise<Response> {
  try {
    const resident = requireResident(request);
    if (!resident) return jsonError(401, "UNAUTHORIZED", "no session");
    const body = (await request.json()) as Record<string, unknown>;
    const slug = typeof body.policySlug === "string" ? body.policySlug : null;
    const version = typeof body.policyVersion === "string" ? body.policyVersion : null;
    const status = typeof body.policyStatus === "string"
      ? body.policyStatus
      : null;
    if (!slug || !version || !status) {
      return jsonError(400, "VALIDATION", "slug/version/status required");
    }
    if (status !== "active") {
      return jsonError(400, "NOT_ACTIVE", "policy is not active");
    }
    const result = defaultResidentRegistry.recordConsent(
      resident.id,
      slug,
      version,
      status,
    );
    if (!result.ok) {
      return jsonError(400, "RECORD_FAILED", result.reason ?? "record-failed");
    }
    return Response.json({ ok: true, consent: result.consent });
  } catch (err) {
    console.error("resident/me/consents POST error", err);
    return jsonError(500, "INTERNAL", "consents POST failed");
  }
}
