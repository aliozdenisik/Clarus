import { render, screen, fireEvent, waitFor } from "./test-utils"
import { vi, describe, it, expect, beforeEach } from "vitest"
import SettingsPage from "../app/[locale]/settings/page"
import * as PreferencesStore from "@/lib/stores/preferences-store"
import * as AuthClient from "@/lib/auth-client"

// Mock Next.js router
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}))

// Mock next-intl locale-aware navigation (used by settings page)
vi.mock("@/i18n/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  usePathname: () => "/settings",
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Link: ({ children, ...props }: Record<string, any>) => <a {...props}>{children}</a>,
  redirect: vi.fn(),
}))

// Mock Sonner toast
vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock fetch for the component's direct API calls (like DELETE)
global.fetch = vi.fn()

describe("SettingsPage", () => {
  const mockSetTheme = vi.fn()
  const mockSetLanguage = vi.fn()
  const mockSetDefaultSearchSource = vi.fn()
  const mockSetDefaultBibleTestament = vi.fn()
  const mockSetResultsPerPage = vi.fn()
  const mockSetEnableStreaming = vi.fn()
  const mockSetEnableMultiAgent = vi.fn()
  const mockSetUsagePurpose = vi.fn()
  const mockSetArabicProficiency = vi.fn()
  const mockSetInterests = vi.fn()
  const mockSetOnboardingCompleted = vi.fn()
  const mockSavePreferences = vi.fn()
  const mockFetchPreferences = vi.fn()
  const mockReset = vi.fn()

  const createMockResponse = (data: unknown): Response =>
    ({
      ok: true,
      json: async () => data,
    }) as unknown as Response

  const defaultPreferences = {
    theme: "system" as const,
    language: "tr" as const,
    default_search_source: "quran" as const,
    default_bible_testament: "all" as const,
    results_per_page: 10,
    enable_streaming: true,
    enable_multi_agent: false,
    usage_purpose: null,
    arabic_proficiency: null,
    interests: [] as string[],
    onboarding_completed: false,
    isLoading: false,
    error: null,
    setTheme: mockSetTheme,
    setLanguage: mockSetLanguage,
    setDefaultSearchSource: mockSetDefaultSearchSource,
    setDefaultBibleTestament: mockSetDefaultBibleTestament,
    setResultsPerPage: mockSetResultsPerPage,
    setEnableStreaming: mockSetEnableStreaming,
    setEnableMultiAgent: mockSetEnableMultiAgent,
    setUsagePurpose: mockSetUsagePurpose,
    setArabicProficiency: mockSetArabicProficiency,
    setInterests: mockSetInterests,
    setOnboardingCompleted: mockSetOnboardingCompleted,
    savePreferences: mockSavePreferences,
    fetchPreferences: mockFetchPreferences,
    reset: mockReset,
  }

  beforeEach(() => {
    vi.clearAllMocks()

    // Mock window.confirm
    window.confirm = vi.fn(() => true)

    // Mock Better Auth
    vi.spyOn(AuthClient, "useSession").mockReturnValue({
      data: {
        user: {
          id: "1",
          email: "test@example.com",
          name: "Test User",
          createdAt: new Date("2023-01-01"),
        },
      },
      isPending: false,
      error: null,
    } as never)

    // Mock Store
    // We need to mock the selector behavior if the component uses selectors,
    // or just return the whole state if it calls the hook without selectors.
    // Assuming the component uses: const { ... } = usePreferencesStore();
    vi.spyOn(PreferencesStore, "usePreferencesStore").mockImplementation((selector) => {
      if (selector) return selector(defaultPreferences)
      return defaultPreferences
    })
  })

  it("renders the settings form with current preferences", () => {
    render(<SettingsPage />)

    expect(screen.getByText("User Preferences")).toBeDefined()

    // Check for form field labels (Radix Select uses trigger buttons, not native select)
    expect(screen.getByText("Language")).toBeDefined()
    expect(screen.getByText("Theme")).toBeDefined()
    expect(screen.getByText("Default Source")).toBeDefined()
    expect(screen.getByText("Results Per Page")).toBeDefined()
  })

  it("fetches preferences on mount", () => {
    render(<SettingsPage />)
    expect(mockFetchPreferences).toHaveBeenCalled()
  })

  it("renders language and theme sections", () => {
    render(<SettingsPage />)

    // Verify both General and Search Defaults sections render
    expect(screen.getByText("General")).toBeDefined()
    expect(screen.getByText("Search Defaults")).toBeDefined()
    expect(screen.getByText("Advanced")).toBeDefined()
  })

  it("calls savePreferences when Save button is clicked", async () => {
    render(<SettingsPage />)

    const saveButton = screen.getByRole("button", { name: /Save Preferences/i })
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockSavePreferences).toHaveBeenCalled()
    })
  })

  it("calls DELETE api and reset when Reset button is clicked", async () => {
    vi.mocked(global.fetch).mockResolvedValueOnce(createMockResponse({ success: true }))

    render(<SettingsPage />)

    const resetButton = screen.getByRole("button", { name: /Reset to Defaults/i })
    fireEvent.click(resetButton)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/preferences"),
        expect.objectContaining({ method: "DELETE" })
      )
      expect(mockReset).toHaveBeenCalled()
    })
  })
})
