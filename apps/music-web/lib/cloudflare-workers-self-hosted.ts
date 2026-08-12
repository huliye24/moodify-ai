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
