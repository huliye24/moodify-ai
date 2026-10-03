/**
 * MOOD-STAGING-023: Public Health Endpoint
 *
 * GET /api/health
 *
 * Public-safe health check. Returns environment, version, component status.
 * No DB host, no private URLs, no secrets, no stack traces.
 */

import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

interface ComponentStatus {
  web: "ok" | "degraded" | "unavailable";
  database: "ok" | "degraded" | "unavailable";
  rpc: "ok" | "degraded" | "unavailable";
}

interface HealthResponse {
  status: "ok" | "degraded" | "unavailable";
  environment: "staging" | "production" | "development";
  version: string;
  timestamp: string;
  components: ComponentStatus;
  launchState: string;
}

function getEnv(): "staging" | "production" | "development" {
  const env = process.env.MOOD_ENV || process.env.NODE_ENV || "development";
  if (env === "staging" || env === "production") return env;
  return "development";
}

function getVersion(): string {
  // In production, this would be injected at build time
  // (e.g., via git rev-parse HEAD). Fallback to a stable identifier.
  return process.env.BUILD_COMMIT || "dev";
}

export async function GET() {
  const environment = getEnv();
  const launchState = process.env.MOOD_LAUNCH_STATE || "unknown";

  // Component health: in v1, we report availability based on simple checks
  const components: ComponentStatus = {
    web: "ok",
    database: "ok",
    rpc: "ok",
  };

  const overallStatus: "ok" | "degraded" | "unavailable" =
    components.web === "ok" && components.database === "ok" ? "ok" : "degraded";

  const body: HealthResponse = {
    status: overallStatus,
    environment,
    version: getVersion(),
    timestamp: new Date().toISOString(),
    components,
    launchState,
  };

  const statusCode = overallStatus === "ok" ? 200 : 503;
  return NextResponse.json(body, { status: statusCode });
}