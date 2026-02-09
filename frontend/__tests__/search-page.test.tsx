import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import userEvent from "@testing-library/user-event";
import SearchPage from "../app/search/page";
import { useRouter, useSearchParams } from "next/navigation";
import { useSSE } from "@/lib/hooks/use-sse";
import { usePreferencesStore } from "@/lib/stores/preferences-store";
import { toast } from "sonner";
import { searchQuranApiSearchQuranPost, searchBibleApiSearchBiblePost } from "@/lib/api/sdk.gen";

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

vi.mock("@/lib/api/sdk.gen", () => ({
  searchQuranApiSearchQuranPost: vi.fn(),
  searchBibleApiSearchBiblePost: vi.fn(),
}));

// Mock framer-motion to avoid animation issues in tests
vi.mock("framer-motion", () => {
  const createMotionProxy = () => new Proxy({}, {
    get: (_target: any, prop: string) => {
      return ({ children, layoutId, initial, animate, transition, whileHover, whileTap, exit, variants, whileInView, viewport, ...props }: any) => {
        const Tag = prop as any;
        return <Tag {...props}>{children}</Tag>;
      };
    }
  });
  return {
    motion: createMotionProxy(),
    AnimatePresence: ({ children }: any) => <>{children}</>,
  };
});

// Mock Lucide icons
vi.mock("lucide-react", () => ({
  Search: () => <div data-testid="search-icon" />,
  User: () => <div data-testid="user-icon" />,
  LogOut: () => <div data-testid="logout-icon" />,
  GitCompare: () => <div data-testid="compare-icon" />,
  ExternalLink: () => <div data-testid="external-link-icon" />,
}));

// Mock GlowCard
vi.mock("@/components/ui/glow-card", () => ({
  GlowCard: ({ children, className }: any) => <div className={className}>{children}</div>,
}));

// Mock DotPattern + AuroraSectionBackground
vi.mock("@/components/ui/dot-pattern", () => ({
  DotPattern: () => null,
  RadialGradient: () => null,
}));
vi.mock("@/components/ui/aurora-background", () => ({
  AuroraSectionBackground: ({ children, className }: any) => <div className={className}>{children}</div>,
}));

// Mock Skeleton
vi.mock("@/components/ui/skeleton", () => ({
  Skeleton: ({ className }: any) => <div data-testid="skeleton" className={className} />,
}));

// Mock design-system
vi.mock("@/lib/design-system", () => ({
  springPresets: {
    snappy: { type: "spring", stiffness: 300, damping: 30 },
    fluid: { type: "spring", stiffness: 170, damping: 26 },
    gentle: { type: "spring", stiffness: 120, damping: 14 },
  },
}));

// Mock compare components
vi.mock("@/components/compare/inline-citation", () => ({
  InlineCitation: ({ children }: any) => <span>{children}</span>,
}));
vi.mock("@/components/compare/source-badge", () => ({
  SourceBadge: ({ source }: any) => <span data-testid="source-badge">{source}</span>,
  SourceType: {},
}));

// Mock search components
vi.mock("@/components/search/verse-tooltip", () => ({
  VerseDetail: {},
}));
vi.mock("@/components/search/language-selector", () => ({
  LanguageSelector: () => null,
}));
vi.mock("@/components/search/keyword-selector", () => ({
  KeywordSelector: () => null,
}));

// Mock citation parser
vi.mock("@/lib/utils/parse-citations", () => ({
  parseCitations: (text: string) => [{ type: "text" as const, content: text }],
  CitationPart: {},
}));

// Mock logger
vi.mock("@/lib/logger", () => ({
  useLogger: () => ({
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  }),
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}));

// Mock keyword store — supports both selector-based and full-store calls
const mockKeywordStoreState = {
  advancedMode: false,
  keywords: [],
  selectedKeywords: [],
  isLoading: false,
  setAdvancedMode: vi.fn(),
  setKeywords: vi.fn(),
  toggleKeyword: vi.fn(),
  selectAll: vi.fn(),
  deselectAll: vi.fn(),
  reset: vi.fn(),
};

vi.mock("@/lib/stores/keyword-store", () => ({
  useKeywordStore: vi.fn((selector?: (state: typeof mockKeywordStoreState) => unknown) =>
    selector ? selector(mockKeywordStoreState) : mockKeywordStoreState
  ),
  KeywordSuggestion: {},
}));

// Input component uses cn() from @/lib/utils which works fine unmocked

// Mock SDK
vi.mock("@/lib/api/sdk.gen", () => ({
  searchQuranApiSearchQuranPost: vi.fn(),
  searchBibleApiSearchBiblePost: vi.fn(),
}));

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

    // Default SDK mock
    vi.mocked(searchQuranApiSearchQuranPost).mockResolvedValue({
      data: { results: [] },
    } as any);
    vi.mocked(searchBibleApiSearchBiblePost).mockResolvedValue({
      data: { results: [] },
    } as any);
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
     vi.mocked(searchQuranApiSearchQuranPost).mockResolvedValueOnce({
       data: { results: mockResults },
     } as any);

     const { container } = render(<SearchPage />);
     
     const input = screen.getByTestId("search-input") as HTMLInputElement;
     
     fireEvent.change(input, { target: { value: "test query" } });
     
     expect(input.value).toBe("test query");

     const form = container.querySelector("form")!;
     fireEvent.submit(form);

     await waitFor(() => {
       expect(searchQuranApiSearchQuranPost).toHaveBeenCalledWith(
         expect.objectContaining({
           body: expect.objectContaining({
             query: "test query"
           })
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
    let resolvePromise: any;
    vi.mocked(searchQuranApiSearchQuranPost).mockReturnValue(new Promise(resolve => {
      resolvePromise = resolve;
    }) as any);

    const { container } = render(<SearchPage />);
    
    const input = screen.getByTestId("search-input");
    fireEvent.change(input, { target: { value: "test query" } });
    fireEvent.submit(container.querySelector("form")!);

    await waitFor(() => {
      expect(screen.getByTestId("search-submit-button")).toHaveTextContent("Searching...");
    });
    
    resolvePromise({ data: { results: [] } });
  });

  it("shows toast with results count on search success", async () => {
    const mockResults = [
      { source: "quran", reference: "1:1", text: "Bismillah", score: 1.0 },
      { source: "quran", reference: "1:2", text: "Alhamdulillah", score: 0.9 }
    ];
    vi.mocked(searchQuranApiSearchQuranPost).mockResolvedValueOnce({
      data: { results: mockResults },
    } as any);

    const { container } = render(<SearchPage />);
    
    const input = screen.getByTestId("search-input");
    fireEvent.change(input, { target: { value: "praise" } });
    fireEvent.submit(container.querySelector("form")!);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Found 2 results");
    });
  });

  it("shows empty state when no results are found", async () => {
    vi.mocked(searchQuranApiSearchQuranPost).mockResolvedValueOnce({
      data: { results: [] },
    } as any);

    const { container } = render(<SearchPage />);
    
    const input = screen.getByTestId("search-input");
    fireEvent.change(input, { target: { value: "nothing" } });
    fireEvent.submit(container.querySelector("form")!);

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

      const { container } = render(<SearchPage />);
      
      const input = screen.getByTestId("search-input");
      fireEvent.change(input, { target: { value: "test streaming" } });
      fireEvent.submit(container.querySelector("form")!);

      await waitFor(() => {
        expect(mockStartStream).toHaveBeenCalledWith(
          expect.stringContaining("/api/stream/search?q=test%20streaming&source=quran")
        );
      });
    });

   it("auto-executes search when q param is present", async () => {
     vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams("source=quran&q=sabir") as any);
     
     render(<SearchPage />);
     
     await waitFor(() => {
       expect(searchQuranApiSearchQuranPost).toHaveBeenCalledWith(
         expect.objectContaining({
           body: expect.objectContaining({
             query: "sabir",
           }),
         })
       );
     });
   });

   it("does not auto-execute when q param is empty", async () => {
     vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams("q=") as any);
     
     render(<SearchPage />);
     
     await waitFor(() => {
       expect(searchQuranApiSearchQuranPost).not.toHaveBeenCalled();
       expect(searchBibleApiSearchBiblePost).not.toHaveBeenCalled();
     });
   });

   it("does not auto-execute when q param is absent", async () => {
     vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams("") as any);
     
     render(<SearchPage />);
     
     await waitFor(() => {
       expect(searchQuranApiSearchQuranPost).not.toHaveBeenCalled();
       expect(searchBibleApiSearchBiblePost).not.toHaveBeenCalled();
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
