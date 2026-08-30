/*
 * MOOD FOUNDATION 012 — Launch Gate Boundary tests.
 *
 * These tests verify the invariants called out in 012 TASK.md Phase I and
 * TEST_PLAN.md:
 *
 *   INV-012-01  foundation builds without MOOD_TOKEN facts.
 *   INV-012-06  foundation exposes no production Buy / Trade / Claim.
 *   INV-012-07  unknown launch state fails closed.
 *   INV-012-08  legacy Token adapters cannot auto-promote to canonical.
 *
 * The tests do not depend on any chain, DB, or wallet provider.
 * They are pure module-load assertions of the launch gate boundary.
 *
 * Implementation: node:test (matches the existing apps/web/tests/*.test.mjs
 * convention).
 */

import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const LIB_DIR = join(here, "..", "lib");
const SOURCE_FILE = join(LIB_DIR, "mood-launch-state.ts");
const SOURCE_TEXT = readFileSync(SOURCE_FILE, "utf8");

const launchStateModule = await import("../lib/mood-launch-state.ts");
const {
  MOOD_LAUNCH_STATE,
  getMoodLaunchState,
  isFoundation,
  mayExposePublicToken,
  moodLaunchFeatures,
  normalizeMoodLaunchState,
  assertMoodLaunchState,
} = launchStateModule;

test("INV-012-01 default launch state is foundation", () => {
  assert.equal(MOOD_LAUNCH_STATE, "foundation");
  assert.equal(getMoodLaunchState(), "foundation");
  assert.equal(isFoundation(), true);
});

test("INV-012-01 source file declares default 'foundation'", () => {
  // The literal "foundation" must be the only default in the file. We do
  // not allow a future maintainer to silently change the default without
  // also updating this test (and the Canon gate documentation).
  const matches = SOURCE_TEXT.match(/:\s*MoodLaunchState\s*=\s*"([^"]+)"/g) ?? [];
  assert.equal(matches.length, 1, "expected exactly one launch-state default literal");
  assert.match(matches[0], /"foundation"/);
});

test("INV-012-06 foundation exposes no token CTAs or balances", () => {
  assert.equal(mayExposePublicToken(), false);
  assert.equal(moodLaunchFeatures.showTokenInfoPage, false);
  assert.equal(moodLaunchFeatures.showTokenCTAs, false);
  assert.equal(moodLaunchFeatures.showWalletTokenBalance, false);
  assert.equal(moodLaunchFeatures.showTreasuryTokenBalance, false);
});

test("INV-012-06 pending reward never settles as token under foundation", () => {
  assert.equal(moodLaunchFeatures.allowTokenRewardSettlement, false);
});

test("INV-012-07 unknown launch state is rejected (fail closed)", () => {
  for (const bad of [undefined, null, "", " ", "mainnet", "live", "TOKEN_ACTIVE", "Foundation"]) {
    assert.equal(normalizeMoodLaunchState(bad), null, `expected null for ${JSON.stringify(bad)}`);
  }
});

test("INV-012-07 known launch states round-trip through normalize", () => {
  for (const state of ["foundation", "staging", "token-ready", "token-active"]) {
    assert.equal(normalizeMoodLaunchState(state), state);
  }
});

test("INV-012-07 assertMoodLaunchState throws for forbidden states", () => {
  assert.throws(
    () => assertMoodLaunchState(["token-active"], "test-context"),
    (err) => {
      assert.equal(err.code, "LAUNCH_STATE_FORBIDDEN");
      assert.match(err.message, /foundation/);
      return true;
    },
  );
});

test("INV-012-07 assertMoodLaunchState passes when state is allowed", () => {
  const result = assertMoodLaunchState(["foundation"], "test-context");
  assert.equal(result, "foundation");
});

test("INV-012-08 launch-state features are frozen at module load", () => {
  // Freezing prevents accidental runtime mutation that would auto-promote
  // a legacy token adapter to canonical config.
  assert.equal(Object.isFrozen(moodLaunchFeatures), true);
  assert.throws(() => {
    "use strict";
    moodLaunchFeatures.showTokenCTAs = true;
  });
});

test("INV-012-08 source does not silently auto-promote foundation", () => {
  // The file must not contain patterns like
  //   - `MOOD_LAUNCH_STATE = <expr>` outside the single literal default
  //   - `process.env` reads (no runtime config service)
  // Foundation must come from a hard-coded constant that only humans can change.
  assert.doesNotMatch(SOURCE_TEXT, /process\.env/);

  // Find every assignment site of MOOD_LAUNCH_STATE and require each to be a
  // literal string default. The pattern `= "foundation"` is the only legal one.
  // Use a non-comparison assignment: `MOOD_LAUNCH_STATE = ...` not `===`.
  // Match `MOOD_LAUNCH_STATE` followed by optional type annotation, then `=`,
  // then capture the RHS up to `;`.
  const assignmentPattern = /MOOD_LAUNCH_STATE(?:\s*:\s*MoodLaunchState)?\s*=(?!=)\s*([^;]+);/g;
  let match;
  const assignments = [];
  while ((match = assignmentPattern.exec(SOURCE_TEXT)) !== null) {
    assignments.push(match[1].trim());
  }
  assert.equal(
    assignments.length,
    1,
    `expected exactly one MOOD_LAUNCH_STATE non-comparison assignment, found ${assignments.length}: ${JSON.stringify(assignments)}`,
  );
  assert.equal(
    assignments[0],
    '"foundation"',
    "MOOD_LAUNCH_STATE must default to the literal \"foundation\"",
  );
});

test("012 launch-state source declares the G0..G11 dependency in comments", () => {
  // We do not enforce a regex against the comment text, but we require the
  // file to at least mention the gate document, so future readers know
  // where the authority is.
  assert.match(SOURCE_TEXT, /TOKEN_LAUNCH_GATE\.md/);
});