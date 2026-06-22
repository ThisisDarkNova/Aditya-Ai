import { test, expect } from '@playwright/test';

test('landing page loads and displays cinematic hero', async ({ page }) => {
  await page.goto('http://localhost:3000/');

  // Expect the Strict Midnight theme background
  await expect(page.locator('main')).toHaveClass(/bg-black/);

  // Expect the luxury heading to be present and visible
  const heading = page.locator('h1', { hasText: 'Absolute Authority.' });
  await expect(heading).toBeVisible();

  // Expect the glass-panel feature box to be present
  const featureBox = page.locator('text=The Symbiosis Engine');
  await expect(featureBox).toBeVisible();

  // Verify the hover effects are present on the initialize button
  const initButton = page.locator('button', { hasText: 'Initialize' });
  await expect(initButton).toHaveClass(/apple-hover/);
  await expect(initButton).toHaveClass(/glass-panel/);
});
