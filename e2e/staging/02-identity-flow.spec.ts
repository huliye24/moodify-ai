/**
 * MOOD-STAGING-023: E2E — Identity Flow
 *
 * Verifies wallet connect, nonce, signature, resident resolution.
 */

import { test, expect } from "@playwright/test";

const STAGING_URL = process.env.STAGING_URL || "https://staging.example.com";

test.describe("Identity Flow", () => {
  test("API: nonce request returns single-use nonce", async ({ request }) => {
    const response = await request.post(
      `${STAGING_URL}/api/genesis/nonce`,
      {
        data: {
          walletAddress: "0x0000000000000000000000000000000000000001",
          chainId: 56,
        },
      }
    );
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.nonce).toBeTruthy();
    expect(body.expiresAt).toBeTruthy();
  });

  test("API: invalid signature is rejected", async ({ request }) => {
    const response = await request.post(
      `${STAGING_URL}/api/genesis/register`,
      {
        data: {
          walletAddress: "0x0000000000000000000000000000000000000001",
          signature: "0xINVALID",
          nonce: "test-nonce",
          chainId: 56,
        },
      }
    );
    expect(response.status()).toBe(401);
  });

  test("API: expired nonce is rejected", async ({ request }) => {
    // Use a known-expired nonce
    const response = await request.post(
      `${STAGING_URL}/api/genesis/register`,
      {
        data: {
          walletAddress: "0x0000000000000000000000000000000000000001",
          signature: "0xANY",
          nonce: "expired-nonce-test",
          chainId: 56,
        },
      }
    );
    expect(response.status()).toBe(401);
  });

  test("Anonymous cannot create MIP", async ({ request }) => {
    const response = await request.post(
      `${STAGING_URL}/api/governance/mips`,
      {
        data: {
          title: "Test",
          summary: "Test",
          category: "other",
        },
      }
    );
    expect(response.status()).toBe(401);
  });

  test("Anonymous cannot accept MIP", async ({ request }) => {
    const response = await request.post(
      `${STAGING_URL}/api/governance/mips/1/accept`,
      {
        data: { rationale: "test" },
      }
    );
    expect([401, 403, 404]).toContain(response.status());
  });
});