/**
 * MOOD-STAGING-023: E2E — Treasury Public Read
 *
 * Verifies the treasury endpoint exposes HONEST inactive state.
 */

import { test, expect } from "@playwright/test";

const STAGING_URL = process.env.STAGING_URL || "https://staging.example.com";

test.describe("Treasury Public Read", () => {
  test("GET /api/protocol/treasury returns inactive state", async ({ request }) => {
    const response = await request.get(`${STAGING_URL}/api/protocol/treasury`);
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.schema).toBe("moodify-treasury-v1");
    expect(body.treasuryStatus).toBe("inactive");
    expect(body.accounts).toEqual([]);
    expect(body.executions).toEqual([]);
  });

  test("GET /api/protocol/treasury/status returns Launch-Gated economics", async ({ request }) => {
    const response = await request.get(
      `${STAGING_URL}/api/protocol/treasury/status`
    );
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.schema).toBe("moodify-treasury-status-v1");
    expect(body.economics).toBe("Launch-Gated");
    expect(body.disabledSlots).toContain("liquidity");
    expect(body.disabledSlots).toContain("holder-rewards");
    expect(body.disabledSlots).toContain("token-reserve");
  });

  test("Forbidden transfer route returns 404", async ({ request }) => {
    const response = await request.post(
      `${STAGING_URL}/api/protocol/treasury/transfer`,
      { data: {} }
    );
    expect(response.status()).toBe(404);
  });

  test("Forbidden execute route returns 404", async ({ request }) => {
    const response = await request.post(
      `${STAGING_URL}/api/protocol/treasury/execute`,
      { data: {} }
    );
    expect(response.status()).toBe(404);
  });

  test("Future revenue sources are launch-gated", async ({ request }) => {
    const response = await request.get(`${STAGING_URL}/api/protocol/treasury`);
    const body = await response.json();
    const futureTradingTax = body.revenue.find(
      (r: any) => r.source === "Future Trading Tax"
    );
    expect(futureTradingTax.status).toBe("FUTURE / LAUNCH-GATED");
  });

  test("Allocation categories include launch-gated disabled", async ({ request }) => {
    const response = await request.get(`${STAGING_URL}/api/protocol/treasury`);
    const body = await response.json();
    const liquidity = body.allocations.find(
      (a: any) => a.category === "Liquidity"
    );
    expect(liquidity.status).toBe("DISABLED");
  });

  test("Risks are exposed (single-operator custody)", async ({ request }) => {
    const response = await request.get(`${STAGING_URL}/api/protocol/treasury`);
    const body = await response.json();
    const hasCustodyRisk = body.risks.some((r: string) =>
      /single-operator/i.test(r)
    );
    expect(hasCustodyRisk).toBeTruthy();
  });
});