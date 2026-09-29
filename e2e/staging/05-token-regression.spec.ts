/**
 * MOOD-STAGING-023: E2E — Token Regression
 *
 * Verifies NO production Token / Trade / Claim CTA appears in staging.
 */

import { test, expect } from "@playwright/test";

const STAGING_URL = process.env.STAGING_URL || "https://staging.example.com";

const FORBIDDEN_PHRASES = [
  /Buy MOOD\b/i,
  /Trade MOOD\b/i,
  /Claim MOOD\b/i,
  /Official CA/i,
  /PancakeSwap/i,
  /Holder Rewards/i,
  /APY\b/i,
  /Flap/i,
];

const SAFE_PAGES = [
  "/",
  "/world",
  "/protocol",
  "/network",
  "/security",
  "/treasury",
  "/transparency",
];

test.describe("Token Regression Guard", () => {
  for (const route of SAFE_PAGES) {
    test(`no token CTA on ${route}`, async ({ page }) => {
      await page.goto(`${STAGING_URL}${route}`);
      const content = await page.content();
      for (const phrase of FORBIDDEN_PHRASES) {
        expect(content).not.toMatch(phrase);
      }
    });
  }

  test("treasury page shows future revenue as launch-gated", async ({ page }) => {
    await page.goto(`${STAGING_URL}/treasury`);
    const content = await page.content();
    // Future Trading Tax should be marked launch-gated (NOT active)
    expect(content).toContain("FUTURE / LAUNCH-GATED");
    expect(content).toContain("Launch-gated");
  });

  test("API: treasury revenue confirms launch-gated", async ({ request }) => {
    const response = await request.get(`${STAGING_URL}/api/protocol/treasury`);
    const body = await response.json();
    const futureCategories = body.revenue.filter((r: any) =>
      r.source.startsWith("Future")
    );
    futureCategories.forEach((cat: any) => {
      expect(cat.status).toBe("FUTURE / LAUNCH-GATED");
    });
  });
});