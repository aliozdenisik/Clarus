import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import userEvent from "@testing-library/user-event";
import ComparePage from "@/app/compare/page";
import { useSSE } from "@/lib/hooks/use-sse";
import { usePreferencesStore } from "@/lib/stores/preferences-store";
import { useSearchParams } from "next/navigation";

// Mock imports
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useSearchParams: vi.fn(),
}));

vi.mock("@/lib/auth-client", () => ({
  useSession: () => ({ data: { user: { id: '1', name: 'Test User', email: 'test@example.com' } }, isPending: false }),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}));

const mockStartStream = vi.fn();
const mockStopStream = vi.fn();

vi.mock("@/lib/hooks/use-sse", () => ({
  useSSE: vi.fn(() => ({
    data: [],
    isStreaming: false,
    error: null,
    startStream: mockStartStream,
    stopStream: mockStopStream,
  })),
}));

vi.mock("@/lib/stores/preferences-store", () => ({
  usePreferencesStore: vi.fn(() => ({
    enable_streaming: true,
  })),
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

// Mock components that might be complex or unnecessary to render fully
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

// Mock Lucide icons
vi.mock("lucide-react", () => ({
  Clock: () => <div data-testid="clock-icon" />,
  Sparkles: () => <div data-testid="sparkles-icon" />,
  ChevronDown: () => <div data-testid="chevron-down-icon" />,
  ChevronUp: () => <div data-testid="chevron-up-icon" />,
  Quote: () => <div data-testid="quote-icon" />,
  Search: () => <div data-testid="search-icon" />,
}));

// Mock compare components
vi.mock("@/components/compare/source-reference-card", () => ({
  SourceReferenceCard: ({ reference, verse }: any) => (
    <div data-testid="source-reference-card">{reference}</div>
  ),
}));
vi.mock("@/components/compare/inline-citation", () => ({
  InlineCitation: ({ children }: any) => <span>{children}</span>,
}));
vi.mock("@/components/compare/collection-selector", () => ({
  CollectionSelector: ({ value, onChange }: any) => (
    <div data-testid="collection-selector">Collections</div>
  ),
}));
vi.mock("@/components/compare/analysis-progress", () => ({
  AnalysisProgress: () => <div data-testid="analysis-progress">Progress</div>,
}));

// Mock animated tabs — receives counts prop, not filters array
vi.mock("@/components/ui/animated-tabs", () => ({
  AnimatedFilterTabs: ({ activeFilter, onFilterChange, counts }: any) => {
    const filters = [
      { id: "all", label: "All Sources" },
      { id: "quran", label: "Quran" },
      { id: "old_testament", label: "Old Testament" },
      { id: "new_testament", label: "New Testament" },
      { id: "apocrypha", label: "Apocrypha" },
    ];
    return (
      <div data-testid="filter-tabs">
        {filters.map((f: any) => (
          <button key={f.id} role="tab" onClick={() => onFilterChange(f.id)}>
            {f.label}
          </button>
        ))}
      </div>
    );
  },
  FilterType: {},
}));

// Mock typewriter
vi.mock("@/components/ui/typewriter", () => ({
  TypingIndicator: () => <div data-testid="typing-indicator" />,
  AIResponse: ({ children }: any) => <div>{children}</div>,
}));

// Mock citation parser — parseBareReferences receives (citationParts[], citations[])
// and must return strings (which get rendered via typeof === 'string' check)
vi.mock("@/lib/utils/parse-citations", () => ({
  parseCitations: (text: string) => [{ type: "text" as const, content: text }],
  parseBareReferences: (parts: any[]) => {
    // The compare page checks typeof part === 'string' to decide how to render
    // Return plain strings so the content shows up
    if (Array.isArray(parts)) {
      return parts.map((p: any) => typeof p === 'string' ? p : p.content || '');
    }
    return [String(parts)];
  },
  stripMarkdownHeaders: (text: string) => text,
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

// Mock search components
vi.mock("@/components/search/language-selector", () => ({
  LanguageSelector: () => null,
}));

// Mock keyword store type import
vi.mock("@/lib/stores/keyword-store", () => ({
  useKeywordStore: vi.fn(),
  KeywordSuggestion: {},
}));

// Mock sonner
vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));

// Mock fetch
global.fetch = vi.fn();

const mockCompareResult = {
  topic: "patience",
  essay: "Patience is a virtue...",
  paragraphs: [
    {
      title: "Quran Perspective",
      content: "The Quran says [quran:2:153].",
      citations: ["quran:2:153"]
    },
    {
      title: "Bible Perspective",
      content: "The Bible says [bible:1:1:1].",
      citations: ["bible:1:1:1"]
    }
  ],
  citations: {
    quran_tr: ["quran:2:153"],
    bible_ot: ["bible:1:1:1"]
  },
  confidence: 0.9,
  total_verses: 2,
  total_citations: 2,
  latency_ms: 1500,
  verse_details: {
    "quran:2:153": {
      text: "O you who have believed, seek help through patience and prayer.",
      book_name: "Al-Baqarah",
      chapter: 2,
      verse: 153,
      source: "quran_tr",
      translation: "Turkish"
    },
    "bible:1:1:1": {
      text: "In the beginning God created the heaven and the earth.",
      book_name: "Genesis",
      chapter: 1,
      verse: 1,
      source: "bible_ot",
      translation: "KJVA",
      book_nr: 1
    }
  }
};

describe("ComparePage", () => {
   beforeEach(() => {
      vi.clearAllMocks();
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockCompareResult,
      });

      // Default mock implementations
      vi.mocked(useSSE).mockReturnValue({
        data: [],
        isStreaming: false,
        error: null,
        startStream: mockStartStream,
        stopStream: mockStopStream,
      });

      vi.mocked(usePreferencesStore).mockReturnValue({
        enable_streaming: true,
      });

      // Default useSearchParams mock (no params)
      vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams() as any);
    });

  it("renders the page title and description", () => {
    render(<ComparePage />);
    expect(screen.getByRole("heading", { name: /^compare$/i, level: 1 })).toBeInTheDocument();
    expect(screen.getByText(/Comparative analysis across/)).toBeInTheDocument();
  });

  it("renders search input and analyze button", () => {
    render(<ComparePage />);
    expect(screen.getByPlaceholderText(/Enter a topic/)).toBeInTheDocument();
    expect(screen.getByTestId("compare-analyze-button")).toBeInTheDocument();
  });

   it("starts streaming when form is submitted and streaming is enabled", async () => {
     const { container } = render(<ComparePage />);
     const input = screen.getByTestId("compare-topic-input");

     fireEvent.change(input, { target: { value: "patience" } });
     fireEvent.submit(container.querySelector("form")!);

     await waitFor(() => {
       expect(mockStartStream).toHaveBeenCalled();
     });
     
     const callUrl = mockStartStream.mock.calls[0][0];
     expect(callUrl).toContain("topic=patience");
     expect(callUrl).not.toContain("token=");
   });

  it("shows loading state when isStreaming is true", () => {
    vi.mocked(useSSE).mockReturnValue({
      data: [],
      isStreaming: true,
      error: null,
      startStream: mockStartStream,
      stopStream: mockStopStream,
    });

    render(<ComparePage />);
    expect(screen.getByText(/Initializing multi-agent analysis/)).toBeInTheDocument();
  });

  it("displays results when SSE data is received", async () => {
    // Initial render
    const { rerender } = render(<ComparePage />);
    
    // Simulate receiving "complete" message
    vi.mocked(useSSE).mockReturnValue({
      data: [{ type: "complete", result: mockCompareResult }],
      isStreaming: false,
      error: null,
      startStream: mockStartStream,
      stopStream: mockStopStream,
    });

    rerender(<ComparePage />);

    await waitFor(() => {
      expect(screen.getByText("Analysis Complete")).toBeInTheDocument();
      expect(screen.getByText("Quran Perspective")).toBeInTheDocument();
      expect(screen.getByText("Bible Perspective")).toBeInTheDocument();
      expect(screen.getByText("90% confidence")).toBeInTheDocument();
    });
  });

  it("toggles paragraph expansion", async () => {
    vi.mocked(useSSE).mockReturnValue({
      data: [{ type: "complete", result: mockCompareResult }],
      isStreaming: false,
      error: null,
      startStream: mockStartStream,
      stopStream: mockStopStream,
    });

    render(<ComparePage />);

    // Wait for result to render
    await waitFor(() => {
      expect(screen.getByText("Quran Perspective")).toBeInTheDocument();
    });

    // "complete" path does NOT auto-expand paragraphs — content starts collapsed
    expect(screen.queryByText(/The Quran says/)).not.toBeInTheDocument();
    
    // Click the expand button (which wraps the title)
    fireEvent.click(screen.getByText("Quran Perspective").closest("button")!);

    // Content should now be visible
    await waitFor(() => {
      expect(screen.getByText(/The Quran says/)).toBeInTheDocument();
    });
    
    // Re-query and click again to collapse (DOM may have changed after re-render)
    fireEvent.click(screen.getByText("Quran Perspective").closest("button")!);

    // Content should be hidden after collapse
    await waitFor(() => {
      expect(screen.queryByText(/The Quran says/)).not.toBeInTheDocument();
    });
  });

  it("filters source references when filter tabs are clicked", async () => {
    vi.mocked(useSSE).mockReturnValue({
      data: [{ type: "complete", result: mockCompareResult }],
      isStreaming: false,
      error: null,
      startStream: mockStartStream,
      stopStream: mockStopStream,
    });

    const { rerender } = render(<ComparePage />);

    await waitFor(() => {
      expect(screen.getByText("Kaynak Referanslari")).toBeInTheDocument();
    });

    // Get the verse references section
    const referencesSection = screen.getByTestId("verse-references-section");
    
    // Check both references are present initially (All Sources filter is active by default)
    const allCards = within(referencesSection).getAllByTestId("source-reference-card");
    expect(allCards).toHaveLength(2);

    // Click on Quran filter tab — our mock renders buttons with role="tab"
    const quranTab = screen.getByRole("tab", { name: /^Quran$/i });
    fireEvent.click(quranTab);

    // Re-render to ensure state update is applied
    rerender(<ComparePage />);

    // After filtering, only Quran reference should be visible
    await waitFor(() => {
      const section = screen.getByTestId("verse-references-section");
      const filteredCards = within(section).getAllByTestId("source-reference-card");
      expect(filteredCards).toHaveLength(1);
      expect(within(section).getByText("quran:2:153")).toBeInTheDocument();
    });
  });

  it("handles batch compare fallback if streaming is disabled", async () => {
    vi.mocked(usePreferencesStore).mockReturnValue({
      enable_streaming: false,
    });

    const { container } = render(<ComparePage />);
    const input = screen.getByTestId("compare-topic-input");

    fireEvent.change(input, { target: { value: "faith" } });
    fireEvent.submit(container.querySelector("form")!);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/compare/",
        expect.objectContaining({
          method: "POST",
          body: expect.stringContaining('"topic":"faith"'),
        })
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Analysis Complete")).toBeInTheDocument();
    });
  });

   it("displays error message when streaming fails", async () => {
     const { rerender } = render(<ComparePage />);

     // Simulate SSE error
     vi.mocked(useSSE).mockReturnValue({
       data: [],
       isStreaming: false,
       error: "Connection lost",
       startStream: mockStartStream,
       stopStream: mockStopStream,
     });

     rerender(<ComparePage />);

     // It should fallback to batch compare
     await waitFor(() => {
       expect(global.fetch).toHaveBeenCalled();
     });
   });

   it("auto-executes comparison when q param is present", async () => {
     vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams("q=creation") as any);
     
     render(<ComparePage />);
     
     await waitFor(() => {
       expect(mockStartStream).toHaveBeenCalled();
       const callUrl = mockStartStream.mock.calls[0][0];
       expect(callUrl).toContain("topic=creation");
     });
   });

   it("does not auto-execute when q param is empty", async () => {
     vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams("q=") as any);
     
     render(<ComparePage />);
     
     await waitFor(() => {
       expect(mockStartStream).not.toHaveBeenCalled();
       expect(global.fetch).not.toHaveBeenCalled();
     });
   });

   it("does not auto-execute when q param is absent", async () => {
     vi.mocked(useSearchParams).mockReturnValue(new URLSearchParams("") as any);
     
     render(<ComparePage />);
     
     await waitFor(() => {
       expect(mockStartStream).not.toHaveBeenCalled();
       expect(global.fetch).not.toHaveBeenCalled();
     });
   });
});

