import React from "react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import * as OnboardingStore from "@/lib/stores/onboarding-store"
import * as Api from "@/lib/api"
import OnboardingPage from "../app/[locale]/onboarding/page"

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string, params?: Record<string, unknown>) =>
    params ? `${key}:${JSON.stringify(params)}` : key,
  useLocale: () => "en",
  NextIntlClientProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

vi.mock("@/i18n/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  usePathname: () => "/onboarding",
  Link: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => (
    <a {...props}>{children}</a>
  ),
  redirect: vi.fn(),
}))

vi.mock("motion/react", async () => {
  const actual = await vi.importActual<typeof import("motion/react")>("motion/react")
  return {
    ...actual,
    AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  }
})

vi.mock("@/components/motion-primitives/transition-panel", () => ({
  TransitionPanel: ({
    children,
    activeIndex,
  }: {
    children: React.ReactNode[]
    activeIndex: number
  }) => <div data-testid="transition-panel">{children[activeIndex]}</div>,
}))

vi.mock("@/components/onboarding/steps/welcome-step", () => ({
  WelcomeStep: () => <div data-testid="welcome-step">Welcome Step</div>,
}))
vi.mock("@/components/onboarding/steps/purpose-step", () => ({
  PurposeStep: () => <div data-testid="purpose-step">Purpose Step</div>,
}))
vi.mock("@/components/onboarding/steps/language-step", () => ({
  LanguageStep: () => <div data-testid="language-step">Language Step</div>,
}))
vi.mock("@/components/onboarding/steps/arabic-step", () => ({
  ArabicStep: () => <div data-testid="arabic-step">Arabic Step</div>,
}))
vi.mock("@/components/onboarding/steps/interests-step", () => ({
  InterestsStep: () => <div data-testid="interests-step">Interests Step</div>,
}))
vi.mock("@/components/onboarding/steps/completion-step", () => ({
  CompletionStep: () => <div data-testid="completion-step">Completion Step</div>,
}))

vi.mock("@/lib/design-system", () => ({
  springPresets: { snappy: { type: "spring", stiffness: 300, damping: 30 } },
}))

vi.mock("@/lib/api", () => ({
  updatePreferencesApiPreferencesPut: vi.fn(),
}))

const mockGoNext = vi.fn()
const mockGoBack = vi.fn()

type StoreOverrides = Partial<OnboardingStore.OnboardingState>

function setupStore(overrides: StoreOverrides = {}) {
  const state: OnboardingStore.OnboardingState = {
    currentStep: 0,
    direction: 1,
    totalSteps: 6,
    usagePurpose: null,
    language: "tr",
    arabicProficiency: "none",
    interests: [],
    isComplete: false,
    goNext: mockGoNext,
    goBack: mockGoBack,
    setUsagePurpose: vi.fn(),
    setLanguage: vi.fn(),
    setArabicProficiency: vi.fn(),
    toggleInterest: vi.fn(),
    reset: vi.fn(),
    markComplete: vi.fn(),
    ...overrides,
  }

  vi.spyOn(OnboardingStore, "useOnboardingStore").mockImplementation(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (selector?: (s: OnboardingStore.OnboardingState) => any) => {
      if (typeof selector === "function") return selector(state)
      return state
    }
  )
}

describe("OnboardingPage", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(Api.updatePreferencesApiPreferencesPut).mockResolvedValue({
      data: {},
      error: undefined,
    } as never)
  })

  it("renders welcome step by default (currentStep=0)", () => {
    setupStore({ currentStep: 0 })
    render(<OnboardingPage />)
    expect(screen.getByTestId("welcome-step")).toBeDefined()
  })

  it("shows step indicator with correct i18n key", () => {
    setupStore({ currentStep: 0 })
    render(<OnboardingPage />)
    expect(screen.getByText('stepOf:{"current":1,"total":6}')).toBeDefined()
  })

  it("welcome step (step 0) has no Back or Next navigation buttons", () => {
    setupStore({ currentStep: 0 })
    render(<OnboardingPage />)
    expect(screen.queryByRole("button", { name: "back" })).toBeNull()
    expect(screen.queryByRole("button", { name: "next" })).toBeNull()
  })

  it("purpose step (step 1) shows Back and Next buttons", () => {
    setupStore({ currentStep: 1, usagePurpose: "academic" })
    render(<OnboardingPage />)
    expect(screen.getByRole("button", { name: "back" })).toBeDefined()
    expect(screen.getByRole("button", { name: "next" })).toBeDefined()
  })

  it("clicking Next calls the API then calls goNext()", async () => {
    setupStore({ currentStep: 1, usagePurpose: "academic" })
    render(<OnboardingPage />)

    fireEvent.click(screen.getByRole("button", { name: "next" }))

    await waitFor(() => {
      expect(Api.updatePreferencesApiPreferencesPut).toHaveBeenCalled()
      expect(mockGoNext).toHaveBeenCalled()
    })
  })
})
