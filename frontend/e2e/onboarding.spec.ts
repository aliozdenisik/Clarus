import { test, expect, type Page } from "@playwright/test"

// ---------------------------------------------------------------------------
// Credentials — mirrors compare.spec.ts pattern
// ---------------------------------------------------------------------------
const TEST_EMAIL = process.env.TEST_EMAIL ?? "browser-test@example.com"
const TEST_PASSWORD = process.env.TEST_PASSWORD ?? "test123"

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Mock the backend preferences API so wizard step transitions don't require a
 * live backend and don't mutate test-user state between runs.
 *
 * Routes intercepted (regex: /\/api\/preferences/):
 *   GET  →  { language: "en", custom_settings: { onboarding_completed: false } }
 *   PUT  →  200 OK (no-op, returns same shape)
 *   *    →  continue (all other methods pass through)
 *
 * Note: Intercepting GET is important so the OnboardingGuard sees
 * onboarding_completed=false and does not redirect away from /en/onboarding.
 */
async function mockPreferencesEndpoint(page: Page): Promise<void> {
  await page.route(/\/api\/preferences/, async (route) => {
    const method = route.request().method()

    if (method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          language: "en",
          custom_settings: { onboarding_completed: false },
        }),
      })
    } else if (method === "PUT") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          language: "en",
          custom_settings: { onboarding_completed: false },
        }),
      })
    } else {
      await route.continue()
    }
  })
}

/**
 * Authenticate with test credentials and wait for a redirect to an
 * authenticated, locale-prefixed page.  Follows the same pattern as
 * compare.spec.ts.
 */
async function loginWithTestUser(page: Page): Promise<void> {
  await page.goto("/en/login")
  await page.fill('input[type="email"]', TEST_EMAIL)
  await page.fill('input[type="password"]', TEST_PASSWORD)
  await page.click('button[type="submit"]')
  // Wait for redirect to any page under /en/. The OnboardingGuard may send the
  // user directly to /en/onboarding (if onboarding not completed) or to /en/.
  await page.waitForURL(/\/en\//, { timeout: 10000 })
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

test.describe("Onboarding Flow", () => {
  /**
   * Common setup executed before every test:
   *   1. Register API route mocks (before any network traffic)
   *   2. Authenticate with test credentials
   *   3. Reset the Zustand persist store so the wizard starts at step 0
   *   4. Navigate to /en/onboarding
   */
  test.beforeEach(async ({ page }) => {
    // Route mocks must be registered before the first navigation that triggers
    // API calls. Register them before login.
    await mockPreferencesEndpoint(page)

    await loginWithTestUser(page)

    // Clear the Zustand persist key so every test opens at step 0 (Welcome).
    // The persist key is "onboarding-storage" (onboarding-store.ts, line 102).
    await page.evaluate(() => {
      localStorage.removeItem("onboarding-storage")
    })

    await page.goto("/en/onboarding")
  })

  // -------------------------------------------------------------------------
  // Happy path — walk through all 6 steps and confirm home redirect
  // -------------------------------------------------------------------------
  test("complete onboarding flow — happy path", async ({ page }) => {
    // ── Step 0: Welcome ──────────────────────────────────────────────────────
    // WelcomeStep renders a headline and a ShimmerButton CTA.
    // The CTA calls goNext() directly — no API call at this step transition.
    await expect(page.getByText("Welcome to Clarus")).toBeVisible()
    await expect(page.getByText("Let's Begin")).toBeVisible()

    await page.getByText("Let's Begin").click()

    // ── Step 1: Purpose ──────────────────────────────────────────────────────
    // PurposeStep renders 5 cards via AnimatedBackground.  Each wrapper div
    // carries data-id="<PurposeKey>" (e.g. "academic", "personal", …).
    await expect(page.getByText("How will you use Clarus?")).toBeVisible()

    // Select "Academic Research" by its data-id attribute
    await page.locator('[data-id="academic"]').click()

    // The "Next" button text comes from t("nav.next") / t("next").
    // Using a case-insensitive regex so the test is resilient to i18n key
    // fallbacks (e.g. if the key renders as "nav.next" instead of "Next").
    // This triggers PUT /api/preferences { custom_settings: { usage_purpose: "academic" } }
    await page.getByRole("button", { name: /next/i }).click()

    // ── Step 2: Language ─────────────────────────────────────────────────────
    // LanguageStep renders two <button data-id="tr|en"> inside AnimatedBackground.
    await expect(page.getByText("Preferred Language")).toBeVisible()

    // Select English via data-id="en" (language-step.tsx line 98)
    await page.locator('[data-id="en"]').click()

    // Triggers PUT /api/preferences { language: "en" }
    await page.getByRole("button", { name: /next/i }).click()

    // ── Step 3: Arabic Proficiency ───────────────────────────────────────────
    // ArabicStep renders a heading, a Slider (min=0, max=3, step=1), and
    // level-label buttons below the slider.
    // Default proficiency is "none" (index 0) — no interaction required.
    await expect(page.getByText("Arabic Proficiency")).toBeVisible()

    // Triggers PUT /api/preferences { custom_settings: { arabic_proficiency: "none" } }
    await page.getByRole("button", { name: /next/i }).click()

    // ── Step 4: Academic Interests ───────────────────────────────────────────
    // InterestsStep renders 10 toggle <motion.button> elements with aria-pressed.
    await expect(page.getByText("Academic Interests")).toBeVisible()

    // Click the "Theology" interest pill (aria-pressed toggles true/false)
    await page.getByRole("button", { name: "Theology" }).click()

    // Triggers PUT /api/preferences { custom_settings: { interests: ["theology"] } }
    await page.getByRole("button", { name: /next/i }).click()

    // ── Step 5: Completion ───────────────────────────────────────────────────
    // CompletionStep renders a headline, a summary card, and a "Start Exploring"
    // ShimmerButton.  Clicking it calls markComplete() then router.push("/").
    // No API call occurs at this final transition.
    await expect(page.getByText("You're All Set!")).toBeVisible()
    await expect(page.getByText("Start Exploring")).toBeVisible()

    await page.getByText("Start Exploring").click()

    // Wizard complete — expect redirect to locale-prefixed home page
    await page.waitForURL(/\/en\/?$/, { timeout: 5000 })
  })

  // -------------------------------------------------------------------------
  // Skip flow — "Skip setup" calls the API and redirects to home
  // -------------------------------------------------------------------------
  test("skip setup redirects to home", async ({ page }) => {
    // "Skip setup" is rendered in OnboardingShell's top bar and is visible on
    // every step of the wizard (onboarding-shell.tsx).
    await expect(page.getByText("Welcome to Clarus")).toBeVisible()

    // Clicking "Skip setup" calls
    //   PUT /api/preferences { custom_settings: { onboarding_completed: true } }
    // and then router.push("/").  The mocked PUT returns 200, so the redirect fires.
    await page.getByText("Skip setup").click()

    // Should land on the locale-prefixed home page (not on /onboarding)
    await page.waitForURL(/\/en\/?$/, { timeout: 5000 })
  })

  // -------------------------------------------------------------------------
  // Back navigation — going back from step 2 preserves the step-1 selection
  // -------------------------------------------------------------------------
  test("back navigation preserves step selection", async ({ page }) => {
    // Navigate welcome → purpose (step 0 → 1, no API call)
    await expect(page.getByText("Welcome to Clarus")).toBeVisible()
    await page.getByText("Let's Begin").click()

    // Select "Academic Research" on the Purpose step
    await expect(page.getByText("How will you use Clarus?")).toBeVisible()
    await page.locator('[data-id="academic"]').click()

    // Advance to Language step (step 1 → 2, triggers mocked API)
    await page.getByRole("button", { name: /next/i }).click()
    await expect(page.getByText("Preferred Language")).toBeVisible()

    // Navigate back to Purpose step via the "Back" button
    // (aria-label + text come from t("nav.back") / t("back"))
    await page.getByRole("button", { name: /back/i }).click()

    // Assert we are back on the Purpose step
    await expect(page.getByText("How will you use Clarus?")).toBeVisible()

    // The PurposeStep cards are always rendered (AnimatedBackground does not
    // unmount unselected cards), so "Academic Research" text is always visible.
    await expect(page.getByText("Academic Research")).toBeVisible()

    // Confirm the Zustand store preserved the selection in localStorage.
    // Zustand persist stores the state under the key "onboarding-storage"
    // in the shape { state: { usagePurpose: string | null, ... }, version: 0 }.
    const storedPurpose = await page.evaluate((): string | null => {
      const raw = localStorage.getItem("onboarding-storage")
      if (!raw) return null
      const parsed = JSON.parse(raw) as { state?: { usagePurpose?: string | null } }
      return parsed.state?.usagePurpose ?? null
    })
    expect(storedPurpose).toBe("academic")

    // Navigate forward again — wizard advances from the preserved state
    await page.getByRole("button", { name: /next/i }).click()
    await expect(page.getByText("Preferred Language")).toBeVisible()
  })

  // -------------------------------------------------------------------------
  // Page-refresh resilience — wizard resumes at the correct step
  // -------------------------------------------------------------------------
  test("wizard resumes at correct step after page refresh", async ({ page }) => {
    // Navigate from step 0 to step 1 (Purpose).
    // Clicking "Let's Begin" calls goNext() which writes currentStep=1 to
    // localStorage via Zustand's persist middleware.
    await expect(page.getByText("Welcome to Clarus")).toBeVisible()
    await page.getByText("Let's Begin").click()
    await expect(page.getByText("How will you use Clarus?")).toBeVisible()

    // Reload the page.  Zustand persist middleware will rehydrate from
    // localStorage key "onboarding-storage", restoring currentStep=1.
    await page.reload()

    // After hydration the wizard should render step 1 (Purpose), not step 0
    // (Welcome).  Playwright auto-waits until the locator becomes visible.
    await expect(page.getByText("How will you use Clarus?")).toBeVisible()
    await expect(page.getByText("Welcome to Clarus")).not.toBeVisible()
  })
})
