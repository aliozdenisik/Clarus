import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import HistoryPage from "../app/history/page";
import { useAuth } from "@/lib/auth/auth-context";
import { useRouter } from "next/navigation";

// Mock hooks
vi.mock("@/lib/auth/auth-context", () => ({
  useAuth: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
  useSearchParams: () => new URLSearchParams(),
}));

// Mock components
vi.mock("@/components/ui/glow-card", () => ({
  GlowCard: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="glow-card" className={className}>
      {children}
    </div>
  ),
}));

vi.mock("@/components/ui/button", () => ({
  Button: ({ children, onClick, disabled, className, ...props }: any) => (
    <button onClick={onClick} disabled={disabled} className={className} {...props}>
      {children}
    </button>
  ),
}));

// Mock Sonner toast
vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock Framer Motion
vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

const mockHistoryItems = [
  {
    id: 1,
    query: "test query 1",
    search_type: "quran",
    created_at: "2024-01-20T10:00:00Z",
    result_count: 5,
  },
  {
    id: 2,
    query: "test query 2",
    search_type: "bible",
    created_at: "2024-01-21T11:00:00Z",
    result_count: 10,
  },
];

describe("HistoryPage", () => {
  const mockPush = vi.fn();
  const mockUser = { id: 1, name: "Test User", email: "test@example.com" };

  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as any).mockReturnValue({ push: mockPush });
    (useAuth as any).mockReturnValue({
      user: mockUser,
      isLoading: false,
      logout: vi.fn(),
    });
    
    // Mock global fetch
    global.fetch = vi.fn();
    
    // Mock window.confirm
    window.confirm = vi.fn(() => true);
  });

  it("redirects to login if user is not authenticated", () => {
    (useAuth as any).mockReturnValue({
      user: null,
      isLoading: false,
      logout: vi.fn(),
    });

    render(<HistoryPage />);
    expect(mockPush).toHaveBeenCalledWith("/login");
  });

  it("shows loading state initially", () => {
    (useAuth as any).mockReturnValue({
      user: mockUser,
      isLoading: true,
      logout: vi.fn(),
    });

    render(<HistoryPage />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("fetches and displays history items", async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: mockHistoryItems,
        total: 2,
        page: 1,
        per_page: 20,
        pages: 1,
      }),
    });

    render(<HistoryPage />);

    expect(screen.getByText("Loading history...")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument();
      expect(screen.getByText("test query 2")).toBeInTheDocument();
    });

    expect(screen.getByText("Quran")).toBeInTheDocument();
    expect(screen.getByText("Bible")).toBeInTheDocument();
    expect(screen.getByText("5 results")).toBeInTheDocument();
  });

  it("handles pagination", async () => {
    (global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: mockHistoryItems,
          total: 30,
          page: 1,
          per_page: 20,
          pages: 2,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: [],
          total: 30,
          page: 2,
          per_page: 20,
          pages: 2,
        }),
      });

    render(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument();
    });

    const nextButton = screen.getByText("Next");
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("page=2"),
        expect.anything()
      );
    });
  });

  it("deletes a history item", async () => {
    (global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: mockHistoryItems,
          total: 2,
          page: 1,
          per_page: 20,
          pages: 1,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
      });

    render(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole("button", { name: /delete/i });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/search/history/1",
        expect.objectContaining({
          method: "DELETE",
        })
      );
    });
  });

  it("clears all history", async () => {
    (global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: mockHistoryItems,
          total: 2,
          page: 1,
          per_page: 20,
          pages: 1,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
      });

    render(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("Clear All")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Clear All"));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/search/history",
        expect.objectContaining({
          method: "DELETE",
        })
      );
    });
  });

  it("displays empty state", async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: [],
        total: 0,
        page: 1,
        per_page: 20,
        pages: 1,
      }),
    });

    render(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("No search history found")).toBeInTheDocument();
    });
  });
});
