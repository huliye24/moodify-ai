// Stub module for `@/db/drizzle` imports used by app/nodes/api/** routes.
//
// This file exists so those modules can resolve their imports during
// the dev server's compile step. The real Drizzle client is only
// buildable once the Cloudflare D1 binding is available (which happens
// at request time, not at module load), so we expose `db` as a Proxy
// that constructs a real client on first property access and caches
// it for subsequent calls.
//
// In a local environment without a configured D1 binding, touching
// `db` throws — matching the behavior of `getDb()` in `./index.ts`.
import { env } from "cloudflare:workers";
import { drizzle } from "drizzle-orm/d1";
import * as schema from "./schema";

type DrizzleClient = ReturnType<typeof drizzle<typeof schema>>;

let cached: DrizzleClient | null = null;

function getClient(): DrizzleClient {
  if (cached) return cached;
  if (!env.DB) {
    throw new Error(
      "Cloudflare D1 binding `DB` is unavailable. Configure your local binding or .dev.vars before using @/db/drizzle."
    );
  }
  cached = drizzle(env.DB, { schema });
  return cached;
}

export const db = new Proxy({} as DrizzleClient, {
  get(_target, prop, receiver) {
    const client = getClient() as unknown as Record<PropertyKey, unknown>;
    const value = Reflect.get(client, prop, client);
    return typeof value === "function" ? (value as Function).bind(client) : value;
  },
});