import { test, expect } from '@playwright/test';

test.describe('Ghost Protocol: Visual Regression', () => {
  test('Home Page meets Apple-level Perceptual rendering', async ({ page }) => {
    await page.goto('/');

    // Wait for the ~1s boot sequence to complete "The Veil" transition
    await page.waitForTimeout(1500);

    // Verify visual perfection against baseline
    await expect(page).toHaveScreenshot('home-page-perceptual-baseline.png', {
      maxDiffPixelRatio: 0.01,
      fullPage: true,
    });
  });

  test('Skill Tree displays atomic luxury alignment', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(1500);

    // Click Skill Tree navigation
    await page.click('text=Skill Tree');
    await page.waitForTimeout(500); // wait for spring physics to settle

    await expect(page).toHaveScreenshot('skill-tree-perceptual-baseline.png', {
      maxDiffPixelRatio: 0.01,
      fullPage: true,
    });
  });
});
