/**
 * MOOD-STAGING-023: E2E — Security Status
 *
 * Verifies /security and /api/security/status expose honest status.
 */

import { test, expect } from "@playwright/test";

const STAGING_URL = process.env.STAGING_URL || "https://staging.example.com";

test.describe("Security Status", () => {
  test("API: security status returns sanitized payload", async ({ request }) => {
    const response = await request.get(`${STAGING_URL}/api/security/status`);
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.schema).toBe("moodify-security-status-v1");
    expect(body.summary.auditCompleted).toBe(false);
    expect(body.summary.custodianModel).toBe("single-operator");
    expect(body.summary.treasuryActive).toBe(false);
    expect(body.summary.autoPayoutEnabled).toBe(false);
    expect(body.summary.aiSignerEnabled).toBe(false);
  });

  test("Trust claims have evidence references", async ({ request }) => {
    const response = await request.get(`${STAGING_URL}/api/security/status`);
    const body = await response.json();
    expect(body.trustClaims.length).toBeGreaterThan(0);
    body.trustClaims.forEach((claim: any) => {
      expect(claim.evidenceRef).toBeTruthy();
    });
  });

  test("Audit-not-completed is honestly disclosed", async ({ page }) => {
    await page.goto(`${STAGING_URL}/security`);
    await expect(page.locator("text=/Not completed/i")).toBeVisible();
  });

  test("API errors are sanitized", async ({ request }) => {
    // Trigger an error if possible
    const response = await request.get(
      `${STAGING_URL}/api/security/status?force_error=1`
    );
    const text = await response.text();
    // Should not contain stack trace markers
    expect(text).not.toMatch(/at Object\.|at async /);
    expect(text).not.toContain("node_modules");
  });

  test("Public response does not leak secrets", async ({ request }) => {
    const response = await request.get(`${STAGING_URL}/api/security/status`);
    const text = await response.text();
    expect(text).not.toMatch(/privateKey|seed|mnemonic/i);
    expect(text).not.toMatch(/process\.env/);
  });
});