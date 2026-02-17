import { render, screen, fireEvent, waitFor } from "./test-utils"
import { vi, describe, it, expect, beforeEach } from "vitest"
import OldTestamentPage from "../app/[locale]/old-testament/page"
import { getBibleBooksApiMetadataBibleBooksGet } from "@/lib/api/sdk.gen"

vi.mock("@/components/ui/magic-card", () => ({
  MagicCard: ({ children, onClick }: { children: React.ReactNode; onClick?: () => void }) => (
    <div data-testid="magic-card" onClick={onClick}>
      {children}
    </div>
  ),
}))

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

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

const mockPush = vi.fn()
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

vi.mock("@/lib/api/sdk.gen", () => ({
  getBibleBooksApiMetadataBibleBooksGet: vi.fn(),
}))

describe("Old Testament Browse Page", () => {
  const mockBooks = [
    { nr: 1, name: "Genesis", chapters_count: 50, testament: "old_testament" },
    { nr: 2, name: "Exodus", chapters_count: 40, testament: "old_testament" },
    { nr: 3, name: "Leviticus", chapters_count: 27, testament: "old_testament" },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(getBibleBooksApiMetadataBibleBooksGet).mockResolvedValue({
      data: { data: { books: mockBooks } },
    } as never)
  })

  it("fetches and displays OT books", async () => {
    render(<OldTestamentPage />)

    expect(getBibleBooksApiMetadataBibleBooksGet).toHaveBeenCalledWith(
      expect.objectContaining({
        query: { testament: "old_testament" },
      })
    )

    await waitFor(() => {
      expect(screen.getByText("Genesis")).toBeInTheDocument()
      expect(screen.getByText("Exodus")).toBeInTheDocument()
      expect(screen.getByText("Leviticus")).toBeInTheDocument()
    })

    expect(screen.getByText("50 chapters")).toBeInTheDocument()
  })

  it("filters books by name", async () => {
    render(<OldTestamentPage />)

    await waitFor(() => {
      expect(screen.getByText("Genesis")).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText(/search book/i)
    fireEvent.change(input, { target: { value: "Exod" } })

    expect(screen.queryByText("Genesis")).not.toBeInTheDocument()
    expect(screen.getByText("Exodus")).toBeInTheDocument()
  })

  it("navigates to search on book click", async () => {
    render(<OldTestamentPage />)

    await waitFor(() => {
      expect(screen.getByText("Genesis")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Genesis"))

    expect(mockPush).toHaveBeenCalledWith("/bible/1")
  })

  it("handles empty state or loading", async () => {
    vi.mocked(getBibleBooksApiMetadataBibleBooksGet).mockResolvedValueOnce({
      data: { data: { books: [] } },
    } as never)

    render(<OldTestamentPage />)

    await waitFor(() => {
      expect(getBibleBooksApiMetadataBibleBooksGet).toHaveBeenCalled()
    })
  })
})
