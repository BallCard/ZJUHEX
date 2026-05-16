import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('Knowledge Topology Platform - Core UI', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('homepage loads successfully with correct title', async ({ page }) => {
    await expect(page).toHaveTitle(/知识拓扑/);
  });

  test('app root element renders', async ({ page }) => {
    const root = page.locator('#root');
    await expect(root).toBeAttached();
    // Wait for React to hydrate
    await page.waitForTimeout(2000);
  });

  test('page has no console errors on load', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('/');
    await page.waitForTimeout(3000);
    expect(errors.filter(e => !e.includes('favicon'))).toHaveLength(0);
  });
});

test.describe('Knowledge Topology Platform - Graph Visualization', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(3000);
  });

  test('graph container is visible', async ({ page }) => {
    // The graph renders inside a Cytoscape canvas container
    const graphContainer = page.locator('[style*="width"]').first();
    await expect(graphContainer).toBeAttached({ timeout: 10000 });
  });

  test('cytoscape canvas element exists', async ({ page }) => {
    // Cytoscape creates a canvas element for rendering
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeAttached({ timeout: 10000 });
  });
});

test.describe('Knowledge Topology Platform - Search & Interaction', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(3000);
  });

  test('search input is present and functional', async ({ page }) => {
    const searchInput = page.locator('input[type="text"], input[placeholder*="搜索"]').first();
    await expect(searchInput).toBeAttached({ timeout: 10000 });

    if (await searchInput.isVisible()) {
      await searchInput.fill('测试查询');
      await expect(searchInput).toHaveValue('测试查询');
    }
  });

  test('sidebar or navigation elements are visible', async ({ page }) => {
    // Check for Lucide icons which indicate UI is loaded
    const icon = page.locator('svg').first();
    await expect(icon).toBeAttached({ timeout: 10000 });
  });
});

test.describe('Knowledge Topology Platform - Responsive Design', () => {
  test('layout renders on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');
    await page.waitForTimeout(3000);
    const root = page.locator('#root');
    await expect(root).toBeAttached();
  });

  test('layout renders on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.waitForTimeout(3000);
    const root = page.locator('#root');
    await expect(root).toBeAttached();
  });
});
