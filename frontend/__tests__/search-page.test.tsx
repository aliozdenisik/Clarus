import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import userEvent from "@testing-library/user-event";
import SearchPage from "../app/search/page";
import { useRouter, useSearchParams } from "next/navigation";
import { useSSE } from "@/lib/hooks/use-sse";
import { usePreferencesStore } from "@/lib/stores/preferences-store";
import { toast } from "sonner";

// Mock Better Auth
vi.mock("@/lib/auth-client", () => ({
  useSession: vi.fn(),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}));

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
  useSearchParams: vi.fn(),
}));

vi.mock("@/lib/hooks/use-sse", () => ({
  useSSE: vi.fn(),
}));

vi.mock("@/lib/stores/preferences-store", () => ({
  usePreferencesStore: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock framer-motion to avoid animation issues in tests
vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, layoutId, initial, animate, transition, whileHover, whileTap, ...props }: any) => <div {...props}>{children}</div>,
    h1: ({ children, layoutId, initial, animate, transition, ...props }: any) => <h1 {...props}>{children}</h1>,
    form: ({ children, layoutId, initial, animate, transition, ...props }: any) => <form {...props}>{children}</form>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock Lucide icons
vi.mock("lucide-react", () => ({
  Search: () => <div data-testid="search-icon" />,
  User: () => <div data-testid="user-icon" />,
  LogOut: () => <div data-testid="logout-icon" />,
  GitCompare: () => <div data-testid="compare-icon" />,
  ExternalLink: () => <div data-testid="external-link-icon" />,
}));

// Mock fetch
global.fetch = vi.fn();

import { useSession } from "@/lib/auth-client";

describe("SearchPage", () => {
  const mockPush = vi.fn();
  const mockStartStream = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default auth state (Better Auth)
    vi.mocked(useSession).mockReturnValue({
      data: { user: { id: "1", name: "Test User", email: "test@example.com" } },
      isPending: false,
    } as any);

    // Default router state
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any);
    vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams() as any);

    // Default SSE state
    vi.mocked(useSSE).mockReturnValue({
      data: [],
      isStreaming: false,
      error: null,
      startStream: mockStartStream,
      stopStream: vi.fn(),
    } as any);

    // Default preferences
    vi.mocked(usePreferencesStore).mockReturnValue({
      enable_streaming: false,
    } as any);

    // Default fetch mock
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ results: [] }),
    });
  });

  it("renders search title and input", () => {
    render(<SearchPage />);
    expect(screen.getByRole("heading", { name: /^search$/i, level: 1 })).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Search Quran...")).toBeInTheDocument();
  });

   it("performs batch search on form submission", async () => {
     const mockResults = [
       { source: "quran", reference: "2:255", text: "Ayat al-Kursi", score: 0.95 }
     ];
     (global.fetch as any).mockResolvedValueOnce({
       ok: true,
       json: async () => ({ results: mockResults }),
     });

     render(<SearchPage />);
     
     const input = screen.getByPlaceholderText("Search Quran...");
     const submitButton = screen.getByRole("button", { name: /search/i });

     await userEvent.type(input, "test query");
     fireEvent.click(submitButton);

     await waitFor(() => {
       expect(global.fetch).toHaveBeenCalledWith(
         expect.stringContaining("/api/search/quran"),
         expect.objectContaining({
           method: "POST",
           body: expect.stringContaining('"query":"test query"')
         })
       );
     });

     await waitFor(() => {
       expect(screen.getByText("Ayat al-Kursi")).toBeInTheDocument();
       expect(screen.getByText("2:255")).toBeInTheDocument();
       expect(screen.getByText("95.0%")).toBeInTheDocument();
     });
   });

  it("displays loading state during search", async () => {
    // Delay the fetch response
    (global.fetch as any).mockReturnValue(new Promise(resolve => 
      setTimeout(() => resolve({
        ok: true,
        json: async () => ({ results: [] })
      }), 100)
    ));

    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText("Search Quran...");
    await userEvent.type(input, "test query");
    fireEvent.submit(input.closest("form")!);

    expect(screen.getByText("Searching...")).toBeInTheDocument();
  });

  it("shows toast with results count on search success", async () => {
    const mockResults = [
      { source: "quran", reference: "1:1", text: "Bismillah", score: 1.0 },
      { source: "quran", reference: "1:2", text: "Alhamdulillah", score: 0.9 }
    ];
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockResults }),
    });

    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText("Search Quran...");
    await userEvent.type(input, "praise");
    fireEvent.click(screen.getByRole("button", { name: /search/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Found 2 results");
    });
  });

  it("shows empty state when no results are found", async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });

    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText("Search Quran...");
    await userEvent.type(input, "nothing");
    fireEvent.click(screen.getByRole("button", { name: /search/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Found 0 results");
      expect(screen.queryByText(/Score:/)).not.toBeInTheDocument();
    });
  });

  it("switches search sources correctly", async () => {
    render(<SearchPage />);
    
    // Labels are in English: Quran, Old Testament, New Testament, Apocrypha
    const otTab = screen.getByText('Old Testament');
    await userEvent.click(otTab);

    expect(mockPush).toHaveBeenCalledWith("/search?source=ot");
    expect(screen.getByPlaceholderText("Search Old Testament...")).toBeInTheDocument();
  });

  it("redirects to sign-in if not authenticated", () => {
    vi.mocked(useSession).mockReturnValue({
      data: null,
      isPending: false,
    } as any);

    render(<SearchPage />);
    
    // The redirect is in a useEffect, so we might need to wait for it
    expect(mockPush).toHaveBeenCalledWith("/sign-in");
  });

   
   it("uses SSE when streaming is enabled", async () => {
     vi.mocked(usePreferencesStore).mockReturnValue({
       enable_streaming: true,
     } as any);
     
     // Mock localStorage for token
     const localStorageMock = (function() {
       let store: Record<string, string> = {
         'access_token': 'mock-token'
       };
       return {
         getItem: function(key: string) {
           return store[key];
         },
         setItem: function(key: string, value: string) {
           store[key] = value;
         },
         clear: function() {
           store = {};
         }
       };
     })();
     Object.defineProperty(window, 'localStorage', { value: localStorageMock });

     render(<SearchPage />);
     
     const input = screen.getByPlaceholderText("Search Quran...");
     await userEvent.type(input, "test streaming");
     fireEvent.click(screen.getByRole("button", { name: /search/i }));

     expect(mockStartStream).toHaveBeenCalledWith(
       expect.stringContaining("/api/stream/search?q=test%20streaming&source=quran&token=mock-token")
     );
   });

   it("auto-executes search when q param is present", async () => {
     vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams("source=quran&q=sabir") as any);
     
     render(<SearchPage />);
     
     await waitFor(() => {
       expect(global.fetch).toHaveBeenCalledWith(
         expect.stringContaining("/api/search/quran"),
         expect.objectContaining({
           method: "POST",
           body: expect.stringContaining('"query":"sabir"')
         })
       );
     });
   });

   it("does not auto-execute when q param is empty", async () => {
     vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams("q=") as any);
     
     render(<SearchPage />);
     
     await waitFor(() => {
       expect(global.fetch).not.toHaveBeenCalled();
     });
   });

   it("does not auto-execute when q param is absent", async () => {
     vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams("") as any);
     
     render(<SearchPage />);
     
     await waitFor(() => {
       expect(global.fetch).not.toHaveBeenCalled();
     });
   });

   it("sets correct source tab from URL param before auto-search", async () => {
     vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams("source=nt&q=love") as any);
     
     render(<SearchPage />);
     
     await waitFor(() => {
       expect(screen.getByPlaceholderText("Search New Testament...")).toBeInTheDocument();
     });
   });
});
