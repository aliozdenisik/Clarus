import { render, screen, fireEvent } from "../test-utils"
import { vi, describe, it, expect } from "vitest"
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
  Search: () => <span data-testid="icon-search" />,
  GitCompareArrows: () => <span data-testid="icon-compare" />,
  Book: () => <span data-testid="icon-book" />,
  BookOpen: () => <span data-testid="icon-book-open" />,
  Languages: () => <span data-testid="icon-languages" />,
  History: () => <span data-testid="icon-history" />,
  Settings: () => <span data-testid="icon-settings" />,
  ArrowRight: () => <span data-testid="icon-arrow-right" />,
  ScrollText: () => <span data-testid="icon-scroll-text" />,
  FileText: () => <span data-testid="icon-file-text" />,
}))

vi.mock("cmdk", () => ({
  Command: {
    Dialog: ({ open, children }: { open: boolean; children: React.ReactNode; label: string }) =>
      open ? <div role="dialog">{children}</div> : null,
    Input: ({ placeholder, className }: { placeholder: string; className?: string }) => (
      <input placeholder={placeholder} className={className} />
    ),
    List: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    Empty: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    Group: ({ children, heading }: { children: React.ReactNode; heading: React.ReactNode }) => (
      <div>
        {heading}
        {children}
      </div>
    ),
    Item: ({ children, onSelect }: { children: React.ReactNode; onSelect: () => void }) => (
      <button type="button" onClick={onSelect}>
        {children}
      </button>
    ),
  },
}))

import { CommandPalette } from "@/components/command-palette"

describe("CommandPalette", () => {
  it("renders without crashing", () => {
    render(<CommandPalette />)
  })

  it("contains Quick Actions and Navigation groups when opened", () => {
    render(<CommandPalette />)
    fireEvent.keyDown(document, { key: "k", ctrlKey: true })
    expect(screen.getByText("Quick Actions")).toBeInTheDocument()
    expect(screen.getByText("Navigation")).toBeInTheDocument()
  })

  it("has a search input when opened", () => {
    render(<CommandPalette />)
    fireEvent.keyDown(document, { key: "k", ctrlKey: true })
    expect(screen.getByPlaceholderText("Type a command or search...")).toBeInTheDocument()
  })
})
