/**
 * MOOD FOUNDATION 012 — Launch Gate Boundary.
 *
 * Single authoritative runtime / build-time source for the MOOD launch state.
 * No other module may mint or override the launch state.
 *
 * The launch state answers one question:
 *   "May the public MOOD surface expose Token / DEX / Claim / Official CA / Treasury?"
 *
 * The default is `foundation`. `foundation` means:
 *   - No new official MOOD token CA is exposed to the public surface.
 *   - No Buy / Trade / Claim / Airdrop CTA is allowed to render.
 *   - No token-gated identity or content.
 *   - Pending reward records exist (off-chain accounting) but do not settle.
 *   - Treasury token balance is read-only and may be omitted entirely.
 *
 * Other states exist ONLY to describe future gated packages (024 / 025). They
 * MUST NOT be reachable from `foundation` by a public request, query string,
 * client-controlled input, or feature flag flip without an explicit human
 * authority record (see docs/mood/TOKEN_LAUNCH_GATE.md).
 *
 * This module is the only place that resolves `MoodLaunchState`. Pages,
 * components, lib services, and API routes MUST read it from here.
 *
 * 012 deliberately does not couple this gate to a runtime config service.
 * The intent is "fail-closed with a single, hand-auditable constant."
 */

/**
 * Canonical MOOD launch states.
 *
 *  - foundation   : current default. Public surface is token-free.
 *  - staging      : reserved for 023 (Public Staging E2E). May render test
 *                   surface but never exposes live token address / DEX.
 *  - token-ready  : reserved for 024 (Genesis Readiness Review). Token
 *                   config may be loaded but no public CTA activation.
 *  - token-active : reserved for 025 (MOOD Token Activation). Reachable only
 *                   after G0..G11 PASS in TOKEN_LAUNCH_GATE.md.
 */
export type MoodLaunchState =
  | "foundation"
  | "staging"
  | "token-ready"
  | "token-active";

/**
 * The single source of truth for the launch state.
 *
 * Edit ONLY after:
 *   - the relevant Gate(s) PASS in docs/mood/TOKEN_LAUNCH_GATE.md, AND
 *   - a human authority record is added to docs/mood/DECISION_LOG.md.
 *
 * 012 leaves the default at `foundation`.
 */
export const MOOD_LAUNCH_STATE: MoodLaunchState = "foundation";

/**
 * Set of all canonical launch states. Used by `isMoodLaunchState` for input
 * validation. Keep in sync with `MoodLaunchState`.
 */
const ALL_LAUNCH_STATES: ReadonlySet<MoodLaunchState> = new Set([
  "foundation",
  "staging",
  "token-ready",
  "token-active",
]);

/**
 * Normalize an arbitrary input to a valid `MoodLaunchState`.
 *
 * - Returns the input if it is a valid state.
 * - Returns `null` for `undefined`, `null`, empty string, unknown values, or
 *   non-string inputs.
 *
 * `normalizeMoodLaunchState` is intentionally strict: any unrecognized value
 * is treated as `null` (fail-closed). It MUST NOT coerce unknown values to
 * `foundation` silently; callers should branch on the `null` case.
 */
export function normalizeMoodLaunchState(value: unknown): MoodLaunchState | null {
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  return ALL_LAUNCH_STATES.has(trimmed as MoodLaunchState)
    ? (trimmed as MoodLaunchState)
    : null;
}

/**
 * Returns the active launch state. This is the value every consumer should
 * use; do not read `MOOD_LAUNCH_STATE` directly.
 */
export function getMoodLaunchState(): MoodLaunchState {
  return MOOD_LAUNCH_STATE;
}

/**
 * Returns true iff the launch state is `foundation`.
 */
export function isFoundation(): boolean {
  return MOOD_LAUNCH_STATE === "foundation";
}

/**
 * Returns true iff a public MOOD token (contract address, DEX entry, claim
 * flow, treasury token balance) may be exposed by the current launch state.
 *
 * INV-012-06 / INV-012-08: under `foundation`, this is false.
 */
export function mayExposePublicToken(): boolean {
  return MOOD_LAUNCH_STATE === "token-active";
}

/**
 * Throws if the current launch state is not in the allowed set.
 *
 * Use this to fail-closed at API / module boundaries. The thrown error is a
 * plain `Error` with a stable `.code` field so callers can branch without
 * importing internal symbols.
 */
export function assertMoodLaunchState(
  allowed: ReadonlyArray<MoodLaunchState>,
  context: string,
): MoodLaunchState {
  if (allowed.includes(MOOD_LAUNCH_STATE)) return MOOD_LAUNCH_STATE;
  const error = new Error(
    `launch state '${MOOD_LAUNCH_STATE}' is not allowed for ${context}; ` +
      `required one of: ${allowed.join(", ")}`,
  ) as Error & { code: string };
  error.code = "LAUNCH_STATE_FORBIDDEN";
  throw error;
}

/**
 * Read-only feature flags derived from the launch state. Pages and components
 * SHOULD branch on these helpers rather than testing the launch state directly
 * so that adding a future state never requires editing call sites.
 */
export const moodLaunchFeatures = Object.freeze({
  /**
   * May the public surface render a Token page that lists contract address,
   * total supply, and DEX entry? Under `foundation` this is false.
   */
  showTokenInfoPage: mayExposePublicToken(),

  /**
   * May the public surface render a Buy / Trade / Claim / Airdrop button?
   * Under `foundation` this is false.
   */
  showTokenCTAs: mayExposePublicToken(),

  /**
   * May the public surface render live token balance for a connected wallet?
   * Under `foundation` this is false; balance reads are dark.
   */
  showWalletTokenBalance: mayExposePublicToken(),

  /**
   * May the contribution workflow settle pending reward records as MOOD
   * token allocations? Under `foundation` this is always false. Pending
   * rewards remain accounting-only.
   */
  allowTokenRewardSettlement: false,

  /**
   * May transparency reports include live treasury token balance? Under
   * `foundation` this is false; provenance / policies may still be shown.
   */
  showTreasuryTokenBalance: mayExposePublicToken(),
});