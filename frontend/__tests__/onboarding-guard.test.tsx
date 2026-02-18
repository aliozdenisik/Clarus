import React from "react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import * as AuthClient from "@/lib/auth-client"
import * as PreferencesStore from "@/lib/stores/preferences-store"
import { OnboardingGuard } from "@/components/providers/onboarding-guard"

const { mockRouterPush, pathnameRef } = vi.hoisted(() => ({
  mockRouterPush: vi.fn(),
  pathnameRef: { current: "/dashboard" },
}))

vi.mock("@/i18n/navigation", () => ({
  useRouter: () => ({ push: mockRouterPush, replace: vi.fn() }),
  usePathname: () => pathnameRef.current,
  Link: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  redirect: vi.fn(),
}))

const mockFetchPreferences = vi.fn()

function setupSession(userId: string | null = null) {
  vi.spyOn(AuthClient, "useSession").mockReturnValue({
    data: userId
      ? {
          user: {
            id: userId,
            email: "test@example.com",
            name: "Test User",
            createdAt: new Date(),
          },
        }
      : null,
    isPending: false,
    error: null,
  } as never)
}

function setupPreferencesStore(onboardingCompleted: boolean, error: string | null = null) {
  const storeState = {
    onboarding_completed: onboardingCompleted,
    error,
    fetchPreferences: mockFetchPreferences,
  }
  vi.spyOn(PreferencesStore, "usePreferencesStore").mockImplementation(((
    selector?: (s: typeof storeState) => unknown
  ) => {
    if (typeof selector === "function") return selector(storeState)
    return storeState
  }) as never)
}

describe("OnboardingGuard", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    pathnameRef.current = "/dashboard"
    mockFetchPreferences.mockResolvedValue(undefined)
  })

  it("renders children when not authenticated (no session)", () => {
    setupSession(null)
    setupPreferencesStore(false)

    render(
      <OnboardingGuard>
        <div>Child Content</div>
      </OnboardingGuard>
    )

    expect(screen.getByText("Child Content")).toBeDefined()
    expect(mockRouterPush).not.toHaveBeenCalled()
  })

  it("redirects to /onboarding when authenticated and onboarding not completed", async () => {
    pathnameRef.current = "/dashboard"
    setupSession("user-1")
    setupPreferencesStore(false)

    render(
      <OnboardingGuard>
        <div>Child Content</div>
      </OnboardingGuard>
    )

    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith("/onboarding")
    })
  })

  it("does not redirect when authenticated and already on /onboarding", async () => {
    pathnameRef.current = "/onboarding"
    setupSession("user-1")
    setupPreferencesStore(false)

    render(
      <OnboardingGuard>
        <div>Child Content</div>
      </OnboardingGuard>
    )

    await waitFor(() => expect(mockFetchPreferences).toHaveBeenCalled())
    expect(mockRouterPush).not.toHaveBeenCalled()
  })

  it("redirects from /onboarding to / when onboarding is already completed", async () => {
    pathnameRef.current = "/onboarding"
    setupSession("user-1")
    setupPreferencesStore(true)

    render(
      <OnboardingGuard>
        <div>Child Content</div>
      </OnboardingGuard>
    )

    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith("/")
    })
  })

  it("does not redirect when authenticated and on an auth route (/login)", async () => {
    pathnameRef.current = "/login"
    setupSession("user-1")
    setupPreferencesStore(false)

    render(
      <OnboardingGuard>
        <div>Child Content</div>
      </OnboardingGuard>
    )

    await waitFor(() => expect(mockFetchPreferences).toHaveBeenCalled())
    expect(mockRouterPush).not.toHaveBeenCalled()
  })

  it("does not redirect when authenticated and on an auth route (/register)", async () => {
    pathnameRef.current = "/register"
    setupSession("user-1")
    setupPreferencesStore(false)

    render(
      <OnboardingGuard>
        <div>Child Content</div>
      </OnboardingGuard>
    )

    await waitFor(() => expect(mockFetchPreferences).toHaveBeenCalled())
    expect(mockRouterPush).not.toHaveBeenCalled()
  })
})
