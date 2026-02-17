import { render, screen, fireEvent, waitFor } from "./test-utils"
import { vi, describe, it, expect, beforeEach } from "vitest"
import NewTestamentPage from "../app/[locale]/new-testament/page"

// Mock MagicCard to avoid complex rendering in tests
vi.mock("@/components/ui/magic-card", () => ({
  MagicCard: ({ children, onClick }: { children: React.ReactNode; onClick?: () => void }) => (
    <div data-testid="magic-card" onClick={onClick}>
      {children}
    </div>
  ),
}))

// Mock Better Auth
vi.mock("@/lib/auth-client", () => ({
  useSession: () => ({
    data: { user: { id: "1", name: "Test User", email: "test@example.com" } },
    isPending: false,
  }),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}))

// Mock Sonner
vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock Navigation
const mockPush = vi.fn()
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

describe("New Testament Browse Page", () => {
  const mockBooks = [
    { nr: 1, name: "Matthew", chapters_count: 28, testament: "new_testament" },
    { nr: 2, name: "Mark", chapters_count: 16, testament: "new_testament" },
    { nr: 3, name: "Luke", chapters_count: 24, testament: "new_testament" },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  const createMockResponse = (data: unknown): Response =>
    ({
      ok: true,
      json: async () => data,
    }) as unknown as Response

  it("fetches and displays NT books", async () => {
    vi.mocked(global.fetch).mockResolvedValueOnce(
      createMockResponse({ data: { books: mockBooks } })
    )

    render(<NewTestamentPage />)

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/metadata/bible/books?testament=new_testament"),
      expect.objectContaining({
        credentials: "include",
      })
    )

    await waitFor(() => {
      expect(screen.getByText("Matthew")).toBeInTheDocument()
      expect(screen.getByText("Mark")).toBeInTheDocument()
      expect(screen.getByText("Luke")).toBeInTheDocument()
    })

    expect(screen.getByText("28 chapters")).toBeInTheDocument()
  })

  it("filters books by name", async () => {
    vi.mocked(global.fetch).mockResolvedValueOnce(
      createMockResponse({ data: { books: mockBooks } })
    )

    render(<NewTestamentPage />)

    await waitFor(() => {
      expect(screen.getByText("Matthew")).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText(/search book/i)
    fireEvent.change(input, { target: { value: "Luke" } })

    expect(screen.queryByText("Matthew")).not.toBeInTheDocument()
    expect(screen.getByText("Luke")).toBeInTheDocument()
  })

  it("navigates to search on book click", async () => {
    vi.mocked(global.fetch).mockResolvedValueOnce(
      createMockResponse({ data: { books: mockBooks } })
    )

    render(<NewTestamentPage />)

    await waitFor(() => {
      expect(screen.getByText("Matthew")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Matthew"))

    expect(mockPush).toHaveBeenCalledWith("/bible/1")
  })

  it("handles empty state or loading", async () => {
    // Test loading state if applicable, or empty result
    vi.mocked(global.fetch).mockResolvedValueOnce(createMockResponse({ data: { books: [] } }))

    render(<NewTestamentPage />)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled()
    })
  })
})
