/**
 * MOOD-STAGING-023: E2E — Mobile Responsive
 *
 * Verifies core routes work at mobile, tablet, and desktop viewports.
 */

import { test, expect } from "@playwright/test";

const STAGING_URL = process.env.STAGING_URL || "https://staging.example.com";

const VIEWPORTS = [
  { name: "mobile-390", width: 390, height: 844 },
  { name: "tablet-768", width: 768, height: 1024 },
  { name: "desktop-1280", width: 1280, height: 720 },
];

const ROUTES = ["/", "/world", "/protocol", "/network", "/security", "/treasury"];

for (const viewport of VIEWPORTS) {
  test.describe(`Viewport ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } });

    for (const route of ROUTES) {
      test(`${route} renders at ${viewport.name}`, async ({ page }) => {
        await page.goto(`${STAGING_URL}${route}`);
        // Page should not have horizontal overflow
        const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
        const viewportWidth = viewport.width;
        expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 10); // small tolerance
      });
    }
  });
}