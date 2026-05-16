import { test, expect } from '@playwright/test';

test.describe('Knowledge Topology Platform', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/知识拓扑/);
  });

  test('graph container is visible', async ({ page }) => {
    await page.goto('/');
    const graphContainer = page.locator('#graph-container, [data-testid="graph"]');
    await expect(graphContainer.first()).toBeVisible();
  });

  test('search input is functional', async ({ page }) => {
    await page.goto('/');
    const searchInput = page.locator('input[type="text"], input[placeholder*="搜索"]');
    await searchInput.first().fill('测试查询');
    await expect(searchInput.first()).toHaveValue('测试查询');
  });
});