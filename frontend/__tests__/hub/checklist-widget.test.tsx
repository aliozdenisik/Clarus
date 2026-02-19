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

vi.mock("@/components/ui/magic-card", () => ({
  MagicCard: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div className={className}>{children}</div>
  ),
}))

vi.mock("@/components/ui/blur-fade", () => ({
  BlurFade: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

vi.mock("lucide-react", () => ({
  CheckCircle2: () => <span data-testid="icon-check-circle" />,
  Circle: () => <span data-testid="icon-circle" />,
  ChevronRight: () => <span data-testid="icon-chevron-right" />,
}))

import { useChecklistStore } from "@/lib/stores/checklist-store"
import { ChecklistWidget } from "@/components/hub/checklist-widget"

const FRESH_ITEMS = [
  { id: "first-search", completed: false },
  { id: "try-compare", completed: false },
  { id: "keyword-search", completed: false },
  { id: "browse-quran", completed: false },
  { id: "view-history", completed: false },
]

describe("ChecklistWidget", () => {
  beforeEach(() => {
    useChecklistStore.setState({
      items: FRESH_ITEMS.map((i) => ({ ...i })),
      dismissed: false,
    })
  })

  it("renders all 5 checklist items when not dismissed", () => {
    render(<ChecklistWidget />)
    expect(screen.getByText("Run your first search")).toBeInTheDocument()
    expect(screen.getByText("Try a comparative analysis")).toBeInTheDocument()
    expect(screen.getByText("Explore morphological keyword search")).toBeInTheDocument()
    expect(screen.getByText("Browse a Quran surah")).toBeInTheDocument()
    expect(screen.getByText("View your search history")).toBeInTheDocument()
  })

  it("returns null when dismissed", () => {
    useChecklistStore.setState({ dismissed: true })
    const { container } = render(<ChecklistWidget />)
    expect(container.firstChild).toBeNull()
  })

  it("shows a progress indicator with completed/total counts", () => {
    useChecklistStore.setState({
      items: [
        { id: "first-search", completed: true },
        { id: "try-compare", completed: false },
        { id: "keyword-search", completed: false },
        { id: "browse-quran", completed: false },
        { id: "view-history", completed: false },
      ],
      dismissed: false,
    })
    render(<ChecklistWidget />)
    expect(screen.getByText("1/5 completed")).toBeInTheDocument()
  })
})
