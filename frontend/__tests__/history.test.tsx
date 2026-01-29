import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";

// Mock SDK BEFORE imports
vi.mock('@/lib/api/sdk.gen', () => ({
  getSearchHistoryApiSearchHistoryGet: vi.fn(),
  deleteHistoryItemApiSearchHistoryHistoryIdDelete: vi.fn(),
  clearHistoryApiSearchHistoryDelete: vi.fn(),
}));

import HistoryPage from "../app/history/page";
import { useAuth } from "@/lib/auth/auth-context";
import { useRouter } from "next/navigation";
import {
  getSearchHistoryApiSearchHistoryGet,
  deleteHistoryItemApiSearchHistoryHistoryIdDelete,
  clearHistoryApiSearchHistoryDelete,
} from '@/lib/api/sdk.gen';

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
  { id: 1, query: "test query 1", search_type: "search_quran", created_at: "2024-01-20T10:00:00Z", result_count: 5 },
  { id: 2, query: "test query 2", search_type: "search_bible_ot", created_at: "2024-01-21T11:00:00Z", result_count: 10 },
];

describe("HistoryPage", () => {
  const mockPush = vi.fn();
  const mockUser = { id: 1, name: "Test User", email: "test@example.com" };

  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as ReturnType<typeof vi.fn>).mockReturnValue({ push: mockPush });
    (useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
      user: mockUser,
      isLoading: false,
      logout: vi.fn(),
    });

    // Mock window.confirm
    window.confirm = vi.fn(() => true);

    // DEFAULT mock: successful history fetch
    (getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: {
        success: true,
        data: mockHistoryItems,
        pagination: { page: 1, limit: 20, total_items: 2, total_pages: 1, has_next: false, has_prev: false },
      },
    });

    // DEFAULT: delete succeeds
    (deleteHistoryItemApiSearchHistoryHistoryIdDelete as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { success: true },
    });

    // DEFAULT: clear all succeeds
    (clearHistoryApiSearchHistoryDelete as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { success: true },
    });
  });

  it("redirects to login if user is not authenticated", () => {
    (useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
      user: null,
      isLoading: false,
      logout: vi.fn(),
    });

    render(<HistoryPage />);
    expect(mockPush).toHaveBeenCalledWith("/login");
  });

  it("shows loading state initially", () => {
    (useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
      user: mockUser,
      isLoading: true,
      logout: vi.fn(),
    });

    render(<HistoryPage />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("fetches and displays history items", async () => {
    render(<HistoryPage />);

    expect(screen.getByText("Loading history...")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument();
      expect(screen.getByText("test query 2")).toBeInTheDocument();
    });

    // search_type labels from SEARCH_TYPE_LABELS map
    expect(screen.getByText("Quran")).toBeInTheDocument();
    expect(screen.getByText("Old Testament")).toBeInTheDocument();
    expect(screen.getByText("5 results")).toBeInTheDocument();
  });

  it("handles pagination", async () => {
    // First call: page 1 with pagination
    (getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({
        data: {
          success: true,
          data: mockHistoryItems,
          pagination: { page: 1, limit: 20, total_items: 30, total_pages: 2, has_next: true, has_prev: false },
        },
      })
      .mockResolvedValueOnce({
        data: {
          success: true,
          data: [],
          pagination: { page: 2, limit: 20, total_items: 30, total_pages: 2, has_next: false, has_prev: true },
        },
      });

    render(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument();
    });

    const nextButton = screen.getByText("Next");
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(getSearchHistoryApiSearchHistoryGet).toHaveBeenCalledTimes(2);
      expect(getSearchHistoryApiSearchHistoryGet).toHaveBeenCalledWith(
        expect.objectContaining({ query: { page: 2, limit: 20 } })
      );
    });
  });

  it("deletes a history item", async () => {
    render(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("test query 1")).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole("button", { name: /delete/i });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(deleteHistoryItemApiSearchHistoryHistoryIdDelete).toHaveBeenCalledWith(
        expect.objectContaining({ path: { history_id: 1 } })
      );
    });
  });

  it("clears all history", async () => {
    render(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("Clear All")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Clear All"));

    await waitFor(() => {
      expect(clearHistoryApiSearchHistoryDelete).toHaveBeenCalled();
    });
  });

  it("displays empty state", async () => {
    (getSearchHistoryApiSearchHistoryGet as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: {
        success: true,
        data: [],
        pagination: { page: 1, limit: 20, total_items: 0, total_pages: 0, has_next: false, has_prev: false },
      },
    });

    render(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("No search history found")).toBeInTheDocument();
    });
  });
});
