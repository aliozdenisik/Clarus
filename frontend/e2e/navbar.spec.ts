import { test, expect } from '@playwright/test';

test.describe('Navbar1 Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/demo-navbar');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Desktop Navigation (≥1024px)', () => {
    test.use({ viewport: { width: 1280, height: 720 } });

    test('should render logo and brand name', async ({ page }) => {
      const logo = page.locator('nav img[alt="Clarus"]');
      await expect(logo).toBeVisible();
      
      const brandName = page.locator('nav span:has-text("Clarus")').first();
      await expect(brandName).toBeVisible();
    });

    test('should render all main menu items', async ({ page }) => {
      await expect(page.locator('nav a:has-text("Home")')).toBeVisible();
      await expect(page.locator('nav button:has-text("Scripture")')).toBeVisible();
      await expect(page.locator('nav button:has-text("Features")')).toBeVisible();
      await expect(page.locator('nav a:has-text("Search")')).toBeVisible();
      await expect(page.locator('nav a:has-text("Compare")')).toBeVisible();
    });

    test('should render authentication buttons', async ({ page }) => {
      const signInButton = page.locator('nav a:has-text("Sign In")');
      const registerButton = page.locator('nav a:has-text("Register")');
      
      await expect(signInButton).toBeVisible();
      await expect(registerButton).toBeVisible();
      
      await expect(signInButton).toHaveAttribute('href', '/login');
      await expect(registerButton).toHaveAttribute('href', '/register');
    });

    test('should open Scripture dropdown menu on hover', async ({ page }) => {
      const scriptureButton = page.locator('nav button:has-text("Scripture")');
      
      // Initially, dropdown content should not be visible
      const quranLink = page.locator('nav a:has-text("Quran")').first();
      await expect(quranLink).not.toBeVisible();
      
      // Hover over Scripture
      await scriptureButton.hover();
      
      // Wait for dropdown to appear
      await expect(quranLink).toBeVisible({ timeout: 2000 });
      
      // Verify all Scripture items
      await expect(page.locator('nav a:has-text("Quran")')).toBeVisible();
      await expect(page.locator('nav a:has-text("Old Testament")')).toBeVisible();
      await expect(page.locator('nav a:has-text("New Testament")')).toBeVisible();
      await expect(page.locator('nav a:has-text("Apocrypha")')).toBeVisible();
    });

    test('should open Features dropdown menu on hover', async ({ page }) => {
      const featuresButton = page.locator('nav button:has-text("Features")');
      
      // Hover over Features
      await featuresButton.hover();
      
      // Wait for dropdown to appear
      const searchLink = page.locator('nav a:has-text("Hybrid semantic + keyword search")');
      await expect(searchLink).toBeVisible({ timeout: 2000 });
      
      // Verify all Features items
      await expect(page.locator('nav a:has-text("Multi-agent comparative analysis")')).toBeVisible();
      await expect(page.locator('nav a:has-text("View your search history")')).toBeVisible();
      await expect(page.locator('nav a:has-text("Customize your experience")')).toBeVisible();
    });

    test('should display dropdown item descriptions', async ({ page }) => {
      const scriptureButton = page.locator('nav button:has-text("Scripture")');
      await scriptureButton.hover();
      
      // Verify descriptions are present
      await expect(page.locator('text=Turkish translation with semantic search')).toBeVisible();
      await expect(page.locator('text=KJVA English translation').first()).toBeVisible();
      await expect(page.locator('text=Deuterocanonical texts')).toBeVisible();
    });

    test('should display icons in dropdown items', async ({ page }) => {
      const scriptureButton = page.locator('nav button:has-text("Scripture")');
      await scriptureButton.hover();
      
      // Wait for dropdown and check for SVG icons (lucide-react renders as SVG)
      const dropdown = page.locator('nav ul').first();
      await expect(dropdown.locator('svg').first()).toBeVisible();
    });

    test('should navigate to correct URLs when dropdown items clicked', async ({ page }) => {
      const scriptureButton = page.locator('nav button:has-text("Scripture")');
      await scriptureButton.hover();
      
      const quranLink = page.locator('nav a:has-text("Quran")').first();
      await expect(quranLink).toHaveAttribute('href', '/quran');
    });

    test('should not show mobile menu button', async ({ page }) => {
      const mobileMenuButton = page.locator('button:has-text("Menu")');
      await expect(mobileMenuButton).not.toBeVisible();
    });
  });

  test.describe('Mobile Navigation (<1024px)', () => {
    test.use({ viewport: { width: 375, height: 667 } }); // iPhone SE size

    test('should render logo and brand name', async ({ page }) => {
      const logo = page.locator('img[alt="Clarus"]');
      await expect(logo).toBeVisible();
      
      const brandName = page.locator('span:has-text("Clarus")').first();
      await expect(brandName).toBeVisible();
    });

    test('should show hamburger menu button', async ({ page }) => {
      const menuButton = page.locator('button[aria-label="Menu"]').or(page.locator('button:has(svg)'));
      await expect(menuButton.first()).toBeVisible();
    });

    test('should not show desktop navigation', async ({ page }) => {
      const desktopNav = page.locator('nav.hidden').first();
      await expect(desktopNav).not.toBeVisible();
    });

    test('should open mobile sheet when hamburger clicked', async ({ page }) => {
      const menuButton = page.locator('button:has(svg)').first();
      await menuButton.click();
      
      // Wait for sheet to open
      await page.waitForTimeout(500); // Animation delay
      
      // Verify sheet content is visible
      await expect(page.locator('text=Home')).toBeVisible();
      await expect(page.locator('text=Scripture')).toBeVisible();
      await expect(page.locator('text=Features')).toBeVisible();
    });

    test('should expand Scripture accordion in mobile menu', async ({ page }) => {
      const menuButton = page.locator('button:has(svg)').first();
      await menuButton.click();
      await page.waitForTimeout(500);
      
      // Click Scripture accordion trigger
      const scriptureTrigger = page.locator('button:has-text("Scripture")');
      await scriptureTrigger.click();
      
      // Verify accordion content expanded
      await expect(page.locator('text=Turkish translation with semantic search')).toBeVisible();
      await expect(page.locator('a:has-text("Quran")')).toBeVisible();
      await expect(page.locator('a:has-text("Old Testament")')).toBeVisible();
      await expect(page.locator('a:has-text("New Testament")')).toBeVisible();
      await expect(page.locator('a:has-text("Apocrypha")')).toBeVisible();
    });

    test('should expand Features accordion in mobile menu', async ({ page }) => {
      const menuButton = page.locator('button:has(svg)').first();
      await menuButton.click();
      await page.waitForTimeout(500);
      
      // Click Features accordion trigger
      const featuresTrigger = page.locator('button:has-text("Features")');
      await featuresTrigger.click();
      
      // Verify accordion content expanded
      await expect(page.locator('text=Hybrid semantic + keyword search')).toBeVisible();
      await expect(page.locator('text=Multi-agent comparative analysis')).toBeVisible();
    });

    test('should display mobile extra links', async ({ page }) => {
      const menuButton = page.locator('button:has(svg)').first();
      await menuButton.click();
      await page.waitForTimeout(500);
      
      // Scroll down in sheet to see extra links
      const sheet = page.locator('[role="dialog"]');
      await sheet.evaluate(el => el.scrollTop = el.scrollHeight);
      
      // Verify extra links
      await expect(page.locator('a:has-text("About")')).toBeVisible();
      await expect(page.locator('a:has-text("Contact")')).toBeVisible();
      await expect(page.locator('a:has-text("Privacy")')).toBeVisible();
      await expect(page.locator('a:has-text("Terms")')).toBeVisible();
    });

    test('should display authentication buttons in mobile menu', async ({ page }) => {
      const menuButton = page.locator('button:has(svg)').first();
      await menuButton.click();
      await page.waitForTimeout(500);
      
      // Scroll to bottom to see auth buttons
      const sheet = page.locator('[role="dialog"]');
      await sheet.evaluate(el => el.scrollTop = el.scrollHeight);
      
      await expect(page.locator('a:has-text("Sign In")')).toBeVisible();
      await expect(page.locator('a:has-text("Register")')).toBeVisible();
    });

    test('should close mobile sheet when X button clicked', async ({ page }) => {
      const menuButton = page.locator('button:has(svg)').first();
      await menuButton.click();
      await page.waitForTimeout(500);
      
      // Find and click close button
      const closeButton = page.locator('[role="dialog"] button[aria-label="Close"]').or(
        page.locator('[role="dialog"] button:has(svg)').last()
      );
      await closeButton.click();
      
      // Wait for close animation
      await page.waitForTimeout(500);
      
      // Verify sheet is closed (no longer visible)
      await expect(page.locator('[role="dialog"]')).not.toBeVisible();
    });

    test('should collapse accordion when clicked again', async ({ page }) => {
      const menuButton = page.locator('button:has(svg)').first();
      await menuButton.click();
      await page.waitForTimeout(500);
      
      const scriptureTrigger = page.locator('button:has-text("Scripture")');
      
      // Expand
      await scriptureTrigger.click();
      await expect(page.locator('a:has-text("Quran")')).toBeVisible();
      
      // Collapse
      await scriptureTrigger.click();
      await page.waitForTimeout(300);
      await expect(page.locator('a:has-text("Quran")')).not.toBeVisible();
    });
  });

  test.describe('Responsive Behavior', () => {
    test('should switch from desktop to mobile view when resizing', async ({ page }) => {
      // Start with desktop viewport
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Verify desktop nav visible
      const desktopNav = page.locator('nav.hidden.lg\\:flex');
      await expect(desktopNav).toBeVisible();
      
      // Resize to mobile
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(300);
      
      // Verify desktop nav hidden and mobile button visible
      await expect(desktopNav).not.toBeVisible();
      const mobileButton = page.locator('button:has(svg)').first();
      await expect(mobileButton).toBeVisible();
    });
  });

  test.describe('Accessibility', () => {
    test.use({ viewport: { width: 1280, height: 720 } });

    test('should have proper alt text for logo', async ({ page }) => {
      const logo = page.locator('nav img');
      await expect(logo).toHaveAttribute('alt', 'Clarus');
    });

    test('should be keyboard navigable', async ({ page }) => {
      // Tab through navigation
      await page.keyboard.press('Tab');
      
      // Verify focus visible on first link
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });

    test('should support screen readers with proper ARIA', async ({ page }) => {
      // Open mobile menu
      await page.setViewportSize({ width: 375, height: 667 });
      const menuButton = page.locator('button:has(svg)').first();
      await menuButton.click();
      
      // Verify dialog role for mobile sheet
      const sheet = page.locator('[role="dialog"]');
      await expect(sheet).toBeVisible();
    });
  });
});
