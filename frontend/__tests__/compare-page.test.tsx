import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
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

// Mock components that might be complex or unnecessary to render fully
vi.mock("@/components/ui/glow-card", () => ({
  GlowCard: ({ children, className }: any) => <div className={className}>{children}</div>,
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
    expect(screen.getByText("Comparative Scripture Analysis")).toBeInTheDocument();
    expect(screen.getByText(/Multi-agent analysis across Quran/)).toBeInTheDocument();
  });

  it("renders search input and analyze button", () => {
    render(<ComparePage />);
    expect(screen.getByPlaceholderText(/Enter a topic/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze" })).toBeInTheDocument();
  });

   it("starts streaming when form is submitted and streaming is enabled", async () => {
     render(<ComparePage />);
     const input = screen.getByPlaceholderText(/Enter a topic/);
     const button = screen.getByRole("button", { name: "Analyze" });

     fireEvent.change(input, { target: { value: "patience" } });
     fireEvent.click(button);

     expect(mockStartStream).toHaveBeenCalled();
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

    const quranTitle = screen.getByText("Quran Perspective");
    fireEvent.click(quranTitle); // Toggle it

    // Check if content is visible
    expect(screen.getByText(/The Quran says/)).toBeInTheDocument();
  });

  it("filters source references when filter tabs are clicked", async () => {
    vi.mocked(useSSE).mockReturnValue({
      data: [{ type: "complete", result: mockCompareResult }],
      isStreaming: false,
      error: null,
      startStream: mockStartStream,
      stopStream: mockStopStream,
    });

    render(<ComparePage />);

    await waitFor(() => {
      expect(screen.getByText("Kaynak Referanslari")).toBeInTheDocument();
    });

    // Check both references are present initially
    const referencesSection = screen.getByText("Kaynak Referanslari").closest('div')!;
    expect(within(referencesSection).getByText("quran:2:153")).toBeInTheDocument();
    expect(within(referencesSection).getByText("bible:1:1:1")).toBeInTheDocument();

    // Click on Quran filter
    const quranTab = screen.getByRole("tab", { name: /Quran/ });
    fireEvent.click(quranTab);

    await waitFor(() => {
      expect(within(referencesSection).getByText("quran:2:153")).toBeInTheDocument();
      expect(within(referencesSection).queryByText("bible:1:1:1")).not.toBeInTheDocument();
    });
  });

  it("handles batch compare fallback if streaming is disabled", async () => {
    vi.mocked(usePreferencesStore).mockReturnValue({
      enable_streaming: false,
    });

    render(<ComparePage />);
    const input = screen.getByPlaceholderText(/Enter a topic/);
    const button = screen.getByRole("button", { name: "Analyze" });

    fireEvent.change(input, { target: { value: "faith" } });
    fireEvent.click(button);

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/compare/",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ topic: "faith", use_multi_agent: true }),
      })
    );

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

