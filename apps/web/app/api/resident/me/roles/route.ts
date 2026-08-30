/**
 * MOOD PASSPORT 015 — GET /api/resident/me/roles
 *
 * List & manage self-declared / verified roles for the current Resident.
 *
 *   GET    : returns { selfDeclared, verified }
 *   POST   : body { role: SelfDeclaredRole } → registers a self-declared role.
 *            Resident may NOT self-issue verified roles.
 */

import { defaultResidentRegistry } from "@/lib/mood/passport/index.ts";
import { jsonError, requireResident } from "@/app/api/identity/_helpers.ts";

export const dynamic = "force-dynamic";

export async function GET(request: Request): Promise<Response> {
  try {
    const resident = requireResident(request);
    if (!resident) return jsonError(401, "UNAUTHORIZED", "no session");
    return Response.json({
      selfDeclared: defaultResidentRegistry.listSelfDeclaredRoles(resident.id),
      verified: defaultResidentRegistry.listVerifiedRoles(resident.id),
    });
  } catch (err) {
    console.error("resident/me/roles error", err);
    return jsonError(500, "INTERNAL", "roles failed");
  }
}

const SELF_DECLARED: ReadonlySet<string> = new Set([
  "creator",
  "developer",
  "researcher",
  "node-operator",
  "agent-builder",
]);

export async function POST(request: Request): Promise<Response> {
  try {
    const resident = requireResident(request);
    if (!resident) return jsonError(401, "UNAUTHORIZED", "no session");
    const body = (await request.json()) as Record<string, unknown>;
    const role = typeof body.role === "string" ? body.role : null;
    if (!role || !SELF_DECLARED.has(role)) {
      return jsonError(
        400,
        "VALIDATION",
        "role must be a self-declared role; verified roles may not be self-issued",
      );
    }
    const result = defaultResidentRegistry.addSelfDeclaredRole(
      resident.id,
      role as "creator",
    );
    if (!result.ok) return jsonError(400, "ROLE_ADD_FAILED", result.reason ?? "role-add-failed");
    return Response.json({
      ok: true,
      selfDeclared: defaultResidentRegistry.listSelfDeclaredRoles(resident.id),
      verified: defaultResidentRegistry.listVerifiedRoles(resident.id),
    });
  } catch (err) {
    console.error("resident/me/roles POST error", err);
    return jsonError(500, "INTERNAL", "roles POST failed");
  }
}
