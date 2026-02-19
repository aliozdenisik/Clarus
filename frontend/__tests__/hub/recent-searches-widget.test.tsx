import { render, screen, waitFor } from "../test-utils"
import { vi, describe, it, expect, beforeEach } from "vitest"
import type React from "react"

vi.mock("@/lib/api/sdk.gen", () => ({
  getSearchHistoryApiSearchHistoryGet: vi.fn(),
}))

vi.mock("@/lib/auth-client", () => ({
  useSession: vi.fn(),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}))

vi.mock("@/components/ui/magic-card", () => ({
  MagicCard: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div className={className}>{children}</div>
  ),
}))

vi.mock("@/components/ui/skeleton", () => ({
  Skeleton: ({ className }: { className?: string }) => (
    <div data-testid="skeleton" className={className} />
  ),
}))

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode
    href: string
    [key: string]: unknown
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}))

vi.mock("lucide-react", () => ({
  Search: () => <span data-testid="icon-search" />,
}))

vi.mock("date-fns/formatDistanceToNow", () => ({
  formatDistanceToNow: () => "2 hours ago",
}))

import { RecentSearchesWidget } from "@/components/hub/recent-searches-widget"
import { useSession } from "@/lib/auth-client"
import { getSearchHistoryApiSearchHistoryGet } from "@/lib/api/sdk.gen"

describe("RecentSearchesWidget", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(useSession as ReturnType<typeof vi.fn>).mockReturnValue({
      data: { user: { id: "1", name: "Test User" } },
      isPending: false,
    })
    ;(getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>).mockReturnValue(
      new Promise(() => {})
    )
  })

  it("shows loading skeleton initially", () => {
    render(<RecentSearchesWidget />)
    const skeletons = screen.getAllByTestId("skeleton")
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it("shows empty state when no history", async () => {
    ;(getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { success: true, data: [] },
    })
    render(<RecentSearchesWidget />)
    await waitFor(
      () => {
        expect(
          screen.getByText("No searches yet. Try searching for something!")
        ).toBeInTheDocument()
      },
      { timeout: 3000 }
    )
  })

  it("renders the section label", () => {
    render(<RecentSearchesWidget />)
    expect(screen.getByText("RECENT SEARCHES")).toBeInTheDocument()
  })
})
