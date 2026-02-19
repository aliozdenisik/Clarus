import { render, screen } from "../test-utils"
import { vi, describe, it, expect, beforeEach } from "vitest"
import type React from "react"

const mockRouterPush = vi.fn()

vi.mock("@/i18n/navigation", () => ({
  useRouter: () => ({
    push: mockRouterPush,
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
  }),
}))

vi.mock("lucide-react", () => ({
  BookOpen: () => <span data-testid="icon-book-open" />,
  ChevronRight: () => <span data-testid="icon-chevron-right" />,
  GitCompareArrows: () => <span data-testid="icon-compare" />,
  Languages: () => <span data-testid="icon-languages" />,
  Search: () => <span data-testid="icon-search" />,
}))

import { useOnboardingStore } from "@/lib/stores/onboarding-store"
import { SuggestionsWidget } from "@/components/hub/suggestions-widget"

describe("SuggestionsWidget", () => {
  beforeEach(() => {
    useOnboardingStore.setState({ interests: [] })
    mockRouterPush.mockClear()
  })

  it("renders default suggestions when no interests are selected", () => {
    render(<SuggestionsWidget />)
    expect(screen.getByText("Try semantic search")).toBeInTheDocument()
    expect(screen.getByText("Browse scripture collections")).toBeInTheDocument()
    expect(screen.getByText("Compare across traditions")).toBeInTheDocument()
  })

  it("renders suggestion pills as buttons", () => {
    render(<SuggestionsWidget />)
    const buttons = screen.getAllByRole("button")
    expect(buttons.length).toBeGreaterThanOrEqual(3)
  })

  it("each pill contains an icon and a label", () => {
    render(<SuggestionsWidget />)
    const buttons = screen.getAllByRole("button")
    buttons.forEach((btn) => {
      expect(btn.querySelector("[data-testid]")).toBeTruthy()
      expect(btn.textContent?.trim().length).toBeGreaterThan(0)
    })
  })
})
