/**
 * MOOD-STAGING-023: E2E — Anonymous Browse
 *
 * Verifies an anonymous visitor can navigate core routes without errors.
 *
 * Run:  npx playwright test e2e/staging/01-anonymous-browse.spec.ts
 */

import { test, expect } from "@playwright/test";

const STAGING_URL = process.env.STAGING_URL || "https://staging.example.com";

test.describe("Anonymous Browse", () => {
  test("homepage loads with staging banner", async ({ page }) => {
    await page.goto(STAGING_URL);
    await expect(page.locator("body")).toContainText(/MOOD STAGING/i);
  });

  test("/world loads", async ({ page }) => {
    await page.goto(`${STAGING_URL}/world`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("/protocol loads", async ({ page }) => {
    await page.goto(`${STAGING_URL}/protocol`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("/library loads", async ({ page }) => {
    await page.goto(`${STAGING_URL}/library`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("/network loads with real metrics", async ({ page }) => {
    await page.goto(`${STAGING_URL}/network`);
    await expect(page.locator("body")).toBeVisible();
    // Network should show treasury section
    await expect(page.locator("text=/Treasury/i")).toBeVisible();
  });

  test("/security loads with audit-not-completed disclaimer", async ({ page }) => {
    await page.goto(`${STAGING_URL}/security`);
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("text=/audit/i")).toBeVisible();
  });

  test("/treasury shows Not Activated", async ({ page }) => {
    await page.goto(`${STAGING_URL}/treasury`);
    await expect(page.locator("text=/Not Activated/i")).toBeVisible();
  });

  test("/transparency loads", async ({ page }) => {
    await page.goto(`${STAGING_URL}/transparency`);
    await expect(page.locator("body")).toBeVisible();
  });

  test("no wallet connection forced on public pages", async ({ page }) => {
    await page.goto(STAGING_URL);
    // Should NOT redirect to wallet or login
    await expect(page).not.toHaveURL(/connect|login|auth/);
  });

  test("staging page does not allow SEO indexing", async ({ page }) => {
    await page.goto(STAGING_URL);
    const robots = await page
      .locator('meta[name="robots"]')
      .first()
      .getAttribute("content");
    expect(robots).toMatch(/noindex/);
  });
});