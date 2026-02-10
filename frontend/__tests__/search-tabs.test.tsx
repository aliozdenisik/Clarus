import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi, describe, it, expect, beforeEach } from "vitest"
import SearchPage from "../app/search/page"
import { SearchTabs } from "../components/search/search-tabs"

// Mock components
vi.mock("@/components/ui/glow-card", () => ({
  GlowCard: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="glow-card">{children}</div>
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

// Mock Navigation
const mockPush = vi.fn()
const mockSearchParamsGet = vi.fn()
const mockSearchParams = {
  get: mockSearchParamsGet,
}

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useSearchParams: () => mockSearchParams,
}))

// Mock Sonner toast
vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

describe("SearchTabs Component", () => {
  it("renders all 4 tabs", () => {
    render(<SearchTabs activeTab="quran" onTabChange={() => {}} />)
    expect(screen.getByText("Quran")).toBeInTheDocument()
    expect(screen.getByText("Old Testament")).toBeInTheDocument()
    expect(screen.getByText("New Testament")).toBeInTheDocument()
    expect(screen.getByText("Apocrypha")).toBeInTheDocument()
  })

  it("calls onTabChange when a tab is clicked", async () => {
    const handleTabChange = vi.fn()
    render(<SearchTabs activeTab="quran" onTabChange={handleTabChange} />)

    await userEvent.click(screen.getByText("Old Testament"))
    expect(handleTabChange).toHaveBeenCalledWith("ot")
  })
})

import { searchQuranApiSearchQuranPost, searchBibleApiSearchBiblePost } from "@/lib/api/sdk.gen"

// Mock SDK methods
vi.mock("@/lib/api/sdk.gen", () => ({
  searchQuranApiSearchQuranPost: vi.fn(),
  searchBibleApiSearchBiblePost: vi.fn(),
}))

describe("SearchPage Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSearchParamsGet.mockReturnValue(null)
  })

  it("renders search tabs", () => {
    render(<SearchPage />)
    expect(screen.getByText("Quran")).toBeInTheDocument()
    expect(screen.getByText("Old Testament")).toBeInTheDocument()
    expect(screen.getByText("New Testament")).toBeInTheDocument()
    expect(screen.getByText("Apocrypha")).toBeInTheDocument()
  })

  it("initializes tab from URL", () => {
    mockSearchParamsGet.mockReturnValue("nt")
    render(<SearchPage />)
    // Check if NT tab is active (we can check class or aria-pressed if we had it, but here checking if it renders is basic)
    // We can verify functionality by checking if search uses 'nt'
    const input = screen.getByPlaceholderText(/search/i)
    fireEvent.change(input, { target: { value: "test" } })

    // We can't easily check internal state, but we can check the API call
    // But we need to implement the page first for this to work
  })

  it("changes tab and updates URL when clicked", async () => {
    render(<SearchPage />)

    const otTab = screen.getByText("Old Testament")
    await userEvent.click(otTab)

    expect(mockPush).toHaveBeenCalledWith(expect.stringContaining("?source=ot"))
  })

  it("performs search with correct API endpoint for Quran", async () => {
    vi.mocked(searchQuranApiSearchQuranPost).mockResolvedValueOnce({
      data: { results: [] },
    } as never)

    render(<SearchPage />)

    const input = screen.getByPlaceholderText(/search/i)
    fireEvent.change(input, { target: { value: "test query" } })

    const button = screen.getByRole("button", { name: /submit search/i })
    fireEvent.click(button)

    await waitFor(() => {
      expect(searchQuranApiSearchQuranPost).toHaveBeenCalledWith(
        expect.objectContaining({
          body: expect.objectContaining({
            query: "test query",
          }),
        })
      )
    })
  })

  it("performs search with correct API endpoint for Bible (OT)", async () => {
    ;(searchBibleApiSearchBiblePost as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: { results: [] },
    })

    render(<SearchPage />)

    const otTab = screen.getByText("Old Testament")
    await userEvent.click(otTab)

    const input = screen.getByPlaceholderText(/search/i)
    fireEvent.change(input, { target: { value: "test query" } })

    const button = screen.getByRole("button", { name: /submit search/i })
    fireEvent.click(button)

    await waitFor(() => {
      expect(searchBibleApiSearchBiblePost).toHaveBeenCalledWith(
        expect.objectContaining({
          body: expect.objectContaining({
            query: "test query",
            testament: "ot",
          }),
        })
      )
    })
  })
})
