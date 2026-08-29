/**
 * Build-time adapter for the LA Node deployment.
 *
 * The canonical public Music API is `/api/v1/music` through the LA BFF. Legacy
 * Cloudflare-only D1/R2 routes remain in source for Cloudflare deployments but
 * must not prevent the self-hosted listener UI from starting.
 */
export const env = new Proxy({} as Cloudflare.Env, {
  get() {
    throw new Error(
      "CLOUDFLARE_BINDING_UNAVAILABLE: use /api/v1/music on the self-hosted deployment",
    );
  },
});

// The Cloudflare Vite plugin's virtual type module imports these names while
// assembling the bundle, even though the LA runtime never instantiates them.
export class WorkerEntrypoint {}
export class DurableObject {}
export class WorkflowEntrypoint {}
