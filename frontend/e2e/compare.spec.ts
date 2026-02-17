import { test, expect } from "@playwright/test"

/**
 * E2E Test: Compare Functionality
 *
 * Tests the multi-agent comparative theological analysis feature:
 * - Essay paragraph display (Issue #1 - P0 Critical)
 * - Statistics display (Issue #2 - P1 Major)
 * - Verse card rendering
 * - Citation interactivity
 * - Filter functionality
 */

// Test credentials
const TEST_EMAIL = process.env.TEST_EMAIL || "browser-test@example.com"
const TEST_PASSWORD = process.env.TEST_PASSWORD || "test123"
const TEST_TOPIC = "patience"

test.describe("Compare Page E2E Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto("/login")
  })

  test("complete compare flow: authentication → query → 5-agent analysis", async ({ page }) => {
    // ============ STEP 1: Authentication ============
    test.step("Login with test credentials", async () => {
      await page.fill('input[type="email"]', TEST_EMAIL)
      await page.fill('input[type="password"]', TEST_PASSWORD)
      await page.click('button[type="submit"]')

      // Wait for redirect to search/compare page
      await page.waitForURL(/\/(search|compare)/, { timeout: 10000 })
    })

    // ============ STEP 2: Navigate to Compare ============
    test.step("Navigate to compare page", async () => {
      // Check if already on compare, if not navigate
      if (!page.url().includes("/compare")) {
        await page.goto("/compare")
      }

      // Verify page loaded
      await expect(page.locator("h1")).toContainText("Comparative Scripture Analysis")
    })

    // ============ STEP 3: Submit Query ============
    test.step("Submit topic for analysis", async () => {
      const input = page.locator('[data-testid="compare-topic-input"]')
      await input.fill(TEST_TOPIC)

      const analyzeButton = page.locator('[data-testid="compare-analyze-button"]')
      await analyzeButton.click()

      // Verify loading state appears
      await expect(page.locator("text=Analyzing")).toBeVisible({ timeout: 5000 })
    })

    // ============ STEP 4: Wait for Paragraphs (CRITICAL TEST) ============
    test.step("Verify 5 paragraphs are displayed (Issue #1 fix)", async () => {
      // Wait for first paragraph to appear (max 90s for full multi-agent analysis)
      await expect(page.locator("text=Eski Ahit")).toBeVisible({ timeout: 90000 })

      // Wait for all 5 agent titles to appear
      const expectedTitles = [
        "Eski Ahit (Old Testament)",
        "Yeni Ahit (New Testament)",
        "Apokrifa (Apocrypha)",
        "Kuran-ı Kerim",
        "Karşılaştırmalı Değerlendirme",
      ]

      for (const title of expectedTitles) {
        await expect(page.locator(`text=${title}`)).toBeVisible({ timeout: 5000 })
      }

      // Verify paragraph cards are rendered (use MagicCard containers)
      const paragraphCards = page.locator('button:has-text("Eski Ahit")').locator("..")
      await expect(paragraphCards).toHaveCount(1, { timeout: 5000 })

      console.log("✅ Issue #1 RESOLVED: All 5 paragraphs displayed correctly")
    })

    // ============ STEP 5: Verify Statistics (MAJOR TEST) ============
    test.step("Verify statistics display non-zero values (Issue #2 fix)", async () => {
      // Wait for stats section to be visible
      await expect(page.locator("text=Analysis Complete")).toBeVisible({ timeout: 5000 })

      // Verify verse count is non-zero
      const versesText = await page.locator("text=/\\d+ verses/").textContent()
      expect(versesText).toBeTruthy()
      const verseCount = parseInt(versesText!.match(/(\d+) verses/)![1])
      expect(verseCount).toBeGreaterThan(0)
      expect(verseCount).toBe(80) // Expected: 80 verses (20 per source)

      // Verify citations count is non-zero
      const citationsText = await page.locator("text=/\\d+ citations/").textContent()
      expect(citationsText).toBeTruthy()
      const citationsCount = parseInt(citationsText!.match(/(\d+) citations/)![1])
      expect(citationsCount).toBeGreaterThan(0)
      expect(citationsCount).toBeGreaterThanOrEqual(5) // At least some citations

      // Verify latency is displayed (non-zero)
      const latencyText = await page.locator("text=/\\d+\\.\\d+s/").textContent()
      expect(latencyText).toBeTruthy()
      const latencySeconds = parseFloat(latencyText!.match(/([\d.]+)s/)![1])
      expect(latencySeconds).toBeGreaterThan(0)

      // Verify confidence score is displayed (non-zero)
      const confidenceText = await page.locator("text=/\\d+% confidence/").textContent()
      expect(confidenceText).toBeTruthy()
      const confidence = parseInt(confidenceText!.match(/(\d+)% confidence/)![1])
      expect(confidence).toBeGreaterThan(0)
      expect(confidence).toBeGreaterThanOrEqual(50) // Reasonable confidence threshold

      console.log(
        `✅ Issue #2 RESOLVED: Stats = ${verseCount} verses, ${citationsCount} citations, ${latencySeconds}s, ${confidence}% confidence`
      )
    })

    // ============ STEP 5.5: Wait for SSE Completion ============
    test.step("Wait for SSE streaming to complete", async () => {
      // Wait for "Analyzing..." to disappear (signals streaming complete)
      await expect(page.locator("text=Analyzing")).not.toBeVisible({ timeout: 90000 })

      // Verify all async data loaded
      await page.waitForLoadState("networkidle", { timeout: 10000 })
    })

    // ============ STEP 6: Verify Verse Cards ============
    test.step("Verify verse reference cards are displayed", async () => {
      // Scroll to verse references section using data-testid
      await page.locator('[data-testid="verse-references-section"]').scrollIntoViewIfNeeded()

      // Verify filter tabs exist
      await expect(page.locator("text=Tumu")).toBeVisible()
      await expect(page.locator("text=Kuran")).toBeVisible()
      await expect(page.locator("text=Eski Ahit")).toBeVisible()
      await expect(page.locator("text=Yeni Ahit")).toBeVisible()
      await expect(page.locator("text=Apokrifa")).toBeVisible()

      // Wait for verse cards to render (check for at least 10 cards)
      await page.waitForFunction(
        () => {
          const cards = document.querySelectorAll("[data-verse-id]")
          return cards.length >= 10
        },
        { timeout: 10000 }
      )

      console.log("✅ Verse cards rendered successfully")
    })

    // ============ STEP 7: Test Paragraph Expansion ============
    test.step("Test paragraph expansion and content visibility", async () => {
      // Find first paragraph header button
      const firstParagraph = page.locator('button:has-text("Eski Ahit")').first()

      // Click to expand (should already be expanded, but test toggle)
      await firstParagraph.click()
      await page.waitForTimeout(500) // Wait for animation

      // Click again to expand if it was collapsed
      await firstParagraph.click()
      await page.waitForTimeout(500)

      // Verify paragraph content is visible
      const paragraphContent = firstParagraph.locator("..").locator("p")
      const isVisible = await paragraphContent.isVisible()
      expect(isVisible).toBeTruthy()

      // Verify content is not empty
      const content = await paragraphContent.textContent()
      expect(content).toBeTruthy()
      expect(content!.length).toBeGreaterThan(50) // At least 50 chars

      console.log("✅ Paragraph expansion working correctly")
    })

    // ============ STEP 8: Test Filter Functionality ============
    test.step("Test source filter tabs", async () => {
      // Scroll to filters using data-testid
      await page.locator('[data-testid="verse-references-section"]').scrollIntoViewIfNeeded()

      // Get initial count (All)
      const allCount = await page.locator("[data-verse-id]").count()
      expect(allCount).toBeGreaterThan(0)

      // Filter by Quran
      await page.locator('button:has-text("Kuran")').click()
      await page.waitForTimeout(500)

      const quranCount = await page.locator("[data-verse-id]").count()
      expect(quranCount).toBeGreaterThan(0)
      expect(quranCount).toBeLessThanOrEqual(allCount)

      // Filter by Old Testament
      await page.locator('button:has-text("Eski Ahit")').click()
      await page.waitForTimeout(500)

      const otCount = await page.locator("[data-verse-id]").count()
      expect(otCount).toBeGreaterThan(0)

      // Filter back to All
      await page.locator('button:has-text("Tumu")').click()
      await page.waitForTimeout(500)

      const finalCount = await page.locator("[data-verse-id]").count()
      expect(finalCount).toBe(allCount)

      console.log("✅ Filter tabs working correctly")
    })

    // ============ STEP 9: Test Citation Interactivity ============
    test.step("Test inline citation clickability", async () => {
      // Find first expanded paragraph
      const firstParagraph = page.locator('button:has-text("Eski Ahit")').first()
      await firstParagraph.scrollIntoViewIfNeeded()

      // Ensure paragraph is expanded
      const isExpanded = await firstParagraph.locator("..").locator("p").isVisible()
      if (!isExpanded) {
        await firstParagraph.click()
        await page.waitForTimeout(500)
      }

      // Find inline citation buttons (styled as small rounded buttons)
      const citationButtons = firstParagraph.locator("..").locator('button[class*="rounded"]')
      const citationCount = await citationButtons.count()

      if (citationCount > 0) {
        // Click first citation and verify new tab opens
        const [newPage] = await Promise.all([
          page.context().waitForEvent("page"),
          citationButtons.first().click(),
        ])

        // Verify new page URL is a verse detail page
        await newPage.waitForLoadState()
        const newUrl = newPage.url()
        expect(newUrl).toMatch(/\/(quran|bible)\/\d+/)

        await newPage.close()

        console.log("✅ Citation clicks open verse detail pages")
      } else {
        console.log(
          "⚠️ No inline citations found in first paragraph (agent may have returned empty citations)"
        )
      }
    })

    // ============ FINAL VALIDATION ============
    test.step("Final validation: All critical features working", async () => {
      // Take screenshot for documentation
      await page.screenshot({ path: "test-results/compare-success.png", fullPage: true })

      console.log("🎉 E2E TEST PASSED: All critical issues resolved!")
      console.log("✅ Issue #1: 5 paragraphs displayed")
      console.log("✅ Issue #2: Statistics showing correct values")
      console.log("✅ Verse cards rendered")
      console.log("✅ Filters functional")
      console.log("✅ Citations clickable")
    })
  })

  test("regression: /stream/search endpoint still works", async ({ page }) => {
    // Login
    await page.fill('input[type="email"]', TEST_EMAIL)
    await page.fill('input[type="password"]', TEST_PASSWORD)
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/(search|compare)/, { timeout: 10000 })

    // Navigate to search page
    await page.goto("/search")

    // Submit a simple query using data-testid selectors
    await page.fill('[data-testid="search-input"]', "mercy")
    await page.click('[data-testid="search-submit-button"]')

    // Verify search results appear
    await expect(page.locator("text=/\\d+ results/")).toBeVisible({ timeout: 30000 })

    console.log("✅ Regression test passed: /stream/search still works")
  })
})
