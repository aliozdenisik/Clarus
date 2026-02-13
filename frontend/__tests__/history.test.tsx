import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { vi, describe, it, expect, beforeEach } from "vitest"
import type React from "react"

// Mock SDK BEFORE imports
vi.mock("@/lib/api/sdk.gen", () => ({
  getSearchHistoryApiSearchHistoryGet: vi.fn(),
  deleteHistoryItemApiSearchHistoryHistoryIdDelete: vi.fn(),
  clearHistoryApiSearchHistoryDelete: vi.fn(),
}))

import HistoryPage from "../app/[locale]/history/page"
import { useRouter } from "next/navigation"
import {
  getSearchHistoryApiSearchHistoryGet,
  deleteHistoryItemApiSearchHistoryHistoryIdDelete,
  clearHistoryApiSearchHistoryDelete,
} from "@/lib/api/sdk.gen"
import { useSession } from "@/lib/auth-client"

// Mock Better Auth
vi.mock("@/lib/auth-client", () => ({
  useSession: vi.fn(),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}))

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
  useSearchParams: () => new URLSearchParams(),
}))

// Mock components
vi.mock("@/components/ui/glow-card", () => ({
  GlowCard: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="glow-card" className={className}>
      {children}
    </div>
  ),
}))

vi.mock("@/components/ui/button", () => ({
  Button: ({
    children,
    onClick,
    disabled,
    className,
    ...props
  }: React.ButtonHTMLAttributes<HTMLButtonElement>) => (
    <button onClick={onClick} disabled={disabled} className={className} {...props}>
      {children}
    </button>
  ),
}))

// Mock Sonner toast
vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock Framer Motion
vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
      <div {...props}>{children}</div>
    ),
  },
  AnimatePresence: ({ children }: { children?: React.ReactNode }) => <>{children}</>,
}))

const mockHistoryItems = [
  {
    id: 1,
    query: "test query 1",
    search_type: "search_quran",
    created_at: "2024-01-20T10:00:00Z",
    result_count: 5,
  },
  {
    id: 2,
    query: "test query 2",
    search_type: "search_bible_ot",
    created_at: "2024-01-21T11:00:00Z",
    result_count: 10,
  },
]

describe("HistoryPage", () => {
  const mockPush = vi.fn()
  const mockUser = { id: "1", name: "Test User", email: "test@example.com" }

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useRouter as ReturnType<typeof vi.fn>).mockReturnValue({ push: mockPush })
    ;(useSession as ReturnType<typeof vi.fn>).mockReturnValue({
      data: { user: mockUser },
      isPending: false,
    })

    // Mock window.confirm
    window.confirm = vi.fn(() => true)

    // DEFAULT mock: successful history fetch
    ;(getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: {
        success: true,
        data: mockHistoryItems,
        pagination: {
          page: 1,
          limit: 20,
          total_items: 2,
          total_pages: 1,
          has_next: false,
          has_prev: false,
        },
      },
    })

    // DEFAULT: delete succeeds
    ;(
      deleteHistoryItemApiSearchHistoryHistoryIdDelete as ReturnType<typeof vi.fn>
    ).mockResolvedValue({
      data: { success: true },
    })

    // DEFAULT: clear all succeeds
    ;(clearHistoryApiSearchHistoryDelete as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { success: true },
    })
  })

  it("redirects to sign-in if user is not authenticated", () => {
    ;(useSession as ReturnType<typeof vi.fn>).mockReturnValue({
      data: null,
      isPending: false,
    })

    render(<HistoryPage />)
    expect(mockPush).toHaveBeenCalledWith("/sign-in")
  })

  it("shows loading state initially", () => {
    ;(useSession as ReturnType<typeof vi.fn>).mockReturnValue({
      data: { user: mockUser },
      isPending: true,
    })

    render(<HistoryPage />)
    expect(screen.getByText("Loading...")).toBeInTheDocument()
  })

  it("fetches and displays history items", async () => {
    render(<HistoryPage />)

    expect(screen.getByText("Loading history...")).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument()
      expect(screen.getByText("test query 2")).toBeInTheDocument()
    })

    // search_type labels from SEARCH_TYPE_LABELS map
    expect(screen.getByText("Quran")).toBeInTheDocument()
    expect(screen.getByText("Old Testament")).toBeInTheDocument()
    expect(screen.getByText("5 results")).toBeInTheDocument()
  })

  it("handles pagination", async () => {
    // First call: page 1 with pagination
    ;(getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        data: {
          success: true,
          data: mockHistoryItems,
          pagination: {
            page: 1,
            limit: 20,
            total_items: 30,
            total_pages: 2,
            has_next: true,
            has_prev: false,
          },
        },
      })
      .mockResolvedValueOnce({
        data: {
          success: true,
          data: [],
          pagination: {
            page: 2,
            limit: 20,
            total_items: 30,
            total_pages: 2,
            has_next: false,
            has_prev: true,
          },
        },
      })

    render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument()
    })

    const nextButton = screen.getByText("Next")
    fireEvent.click(nextButton)

    await waitFor(() => {
      expect(getSearchHistoryApiSearchHistoryGet).toHaveBeenCalledTimes(2)
      expect(getSearchHistoryApiSearchHistoryGet).toHaveBeenCalledWith(
        expect.objectContaining({ query: { page: 2, limit: 20 } })
      )
    })
  })

  it("deletes a history item", async () => {
    render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument()
    })

    const deleteButtons = screen.getAllByRole("button", { name: /delete/i })
    fireEvent.click(deleteButtons[0])

    await waitFor(() => {
      expect(deleteHistoryItemApiSearchHistoryHistoryIdDelete).toHaveBeenCalledWith(
        expect.objectContaining({ path: { history_id: 1 } })
      )
    })
  })

  it("clears all history", async () => {
    render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText("Clear All")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Clear All"))

    await waitFor(() => {
      expect(clearHistoryApiSearchHistoryDelete).toHaveBeenCalled()
    })
  })

  it("displays empty state", async () => {
    ;(getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: {
        success: true,
        data: [],
        pagination: {
          page: 1,
          limit: 20,
          total_items: 0,
          total_pages: 0,
          has_next: false,
          has_prev: false,
        },
      },
    })

    render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText("No search history yet")).toBeInTheDocument()
    })
  })

  it("navigates to search page when clicking a Quran search history item", async () => {
    render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument()
    })

    const queryText = screen.getByText("test query 1")
    const cardContainer = queryText.closest('[class*="cursor-pointer"]')
    fireEvent.click(cardContainer!)

    expect(mockPush).toHaveBeenCalledWith("/search?source=quran&q=test%20query%201")
  })

  it("navigates to compare page when clicking a compare history item", async () => {
    const compareItem = {
      id: 3,
      query: "creation",
      search_type: "compare_multi_agent",
      created_at: "2024-01-22T12:00:00Z",
      result_count: 5,
    }
    ;(getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: {
        success: true,
        data: [compareItem],
        pagination: {
          page: 1,
          limit: 20,
          total_items: 1,
          total_pages: 1,
          has_next: false,
          has_prev: false,
        },
      },
    })

    render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText("creation")).toBeInTheDocument()
    })

    const queryText = screen.getByText("creation")
    const cardContainer = queryText.closest('[class*="cursor-pointer"]')
    fireEvent.click(cardContainer!)

    expect(mockPush).toHaveBeenCalledWith("/compare?q=creation")
  })

  it("does not navigate when clicking delete button", async () => {
    mockPush.mockClear()
    render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument()
    })

    const deleteButtons = screen.getAllByRole("button", { name: /delete/i })
    fireEvent.click(deleteButtons[0])

    expect(mockPush).not.toHaveBeenCalled()
  })

  it("encodes special characters in query URL", async () => {
    const specialItem = {
      id: 4,
      query: "faith & works?",
      search_type: "search_quran",
      created_at: "2024-01-23T12:00:00Z",
      result_count: 3,
    }
    ;(getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: {
        success: true,
        data: [specialItem],
        pagination: {
          page: 1,
          limit: 20,
          total_items: 1,
          total_pages: 1,
          has_next: false,
          has_prev: false,
        },
      },
    })

    render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText("faith & works?")).toBeInTheDocument()
    })

    const queryText = screen.getByText("faith & works?")
    const cardContainer = queryText.closest('[class*="cursor-pointer"]')
    fireEvent.click(cardContainer!)

    expect(mockPush).toHaveBeenCalledWith("/search?source=quran&q=faith%20%26%20works%3F")
  })

  it("falls back to /search for unknown search_type", async () => {
    const unknownItem = {
      id: 5,
      query: "unknown",
      search_type: "unknown_type",
      created_at: "2024-01-24T12:00:00Z",
      result_count: 1,
    }
    ;(getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: {
        success: true,
        data: [unknownItem],
        pagination: {
          page: 1,
          limit: 20,
          total_items: 1,
          total_pages: 1,
          has_next: false,
          has_prev: false,
        },
      },
    })

    render(<HistoryPage />)

    await waitFor(() => {
      expect(screen.getByText("unknown")).toBeInTheDocument()
    })

    const queryText = screen.getByText("unknown")
    const cardContainer = queryText.closest('[class*="cursor-pointer"]')
    fireEvent.click(cardContainer!)

    expect(mockPush).toHaveBeenCalledWith("/search?q=unknown")
  })
})
