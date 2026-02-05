import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";

// Mock framer-motion (CRITICAL — prevents animation issues)
vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, layoutId, initial, animate, transition, whileHover, whileTap, ...props }: any) => <div {...props}>{children}</div>,
    h1: ({ children, layoutId, initial, animate, transition, ...props }: any) => <h1 {...props}>{children}</h1>,
    form: ({ children, layoutId, initial, animate, transition, ...props }: any) => <form {...props}>{children}</form>,
    button: ({ children, layoutId, initial, animate, transition, whileHover, whileTap, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock Lucide icons
vi.mock("lucide-react", () => ({
  Search: () => <div data-testid="search-icon" />,
  X: () => <div data-testid="x-icon" />,
  Loader2: () => <div data-testid="loader-icon" />,
  ExternalLink: () => <div data-testid="external-link-icon" />,
  ChevronLeft: () => <div data-testid="chevron-left-icon" />,
  ChevronRight: () => <div data-testid="chevron-right-icon" />,
  Info: () => <div data-testid="info-icon" />,
  ChevronDown: () => <div data-testid="chevron-down-icon" />,
  AlertTriangle: () => <div data-testid="alert-triangle-icon" />,
}));

// Mock GlowCard
vi.mock("@/components/ui/glow-card", () => ({
  GlowCard: ({ children, className }: any) => <div className={className}>{children}</div>,
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

// Mock Recharts (SVG rendering doesn't work in jsdom)
vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  BarChart: ({ children, data }: any) => <div data-testid="bar-chart" data-count={data?.length}>{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  Tooltip: () => <div data-testid="tooltip" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
}));

import { RootCard } from "@/components/keyword-search/root-card";
import { StatsBar } from "@/components/keyword-search/stats-bar";
import { DerivedWords } from "@/components/keyword-search/derived-words";
import { SurahChart } from "@/components/keyword-search/surah-chart";
import { VerseCard } from "@/components/keyword-search/verse-card";
import { Pagination } from "@/components/keyword-search/pagination";
import { AccuracyDisclaimer } from "@/components/keyword-search/accuracy-disclaimer";
import { ExperimentalDisclaimer } from "@/components/keyword-search/experimental-disclaimer";

// ── RootCard Tests ──────────────────────────────────────────────────────────

describe("RootCard", () => {
  it("renders Arabic root in RTL", () => {
    render(<RootCard root="كتب" rootSource="exact_match" />);

    const rootText = screen.getByText("كتب");
    expect(rootText).toBeInTheDocument();
    // The lang attribute is on the parent <p> element, not the text node
    expect(rootText.closest('p')).toHaveAttribute("lang", "ar");
  });

  it("displays root text without badge", () => {
    render(<RootCard root="كتب" rootSource="exact_match" />);

    // Root text should be displayed
    expect(screen.getByText("كتب")).toBeInTheDocument();
    
    // Badge should NOT be displayed
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("handles null root (not found)", () => {
    render(<RootCard root={null} rootSource="not_found" />);

    expect(screen.getByText(/No root found/i)).toBeInTheDocument();
  });
});

// ── StatsBar Tests ──────────────────────────────────────────────────────────

describe("StatsBar", () => {
  it("renders 3 metrics with correct values", () => {
    render(
      <StatsBar totalOccurrences={319} uniqueWords={5} surahCount={12} language="quran" />
    );

    expect(screen.getByText("319")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("Total Occurrences")).toBeInTheDocument();
    expect(screen.getByText("Unique Words")).toBeInTheDocument();
    expect(screen.getByText("Surahs")).toBeInTheDocument();
  });
});

// ── DerivedWords Tests ──────────────────────────────────────────────────────

describe("DerivedWords", () => {
  it("renders word tags from array", () => {
    render(
      <DerivedWords
        words={["كتاب", "كتب"]}
        selectedWord={null}
        onWordSelect={vi.fn()}
      />
    );

    expect(screen.getByRole("button", { name: "All Words" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "كتاب" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "كتب" })).toBeInTheDocument();
  });

  it("calls filter callback on tag click", () => {
    const onWordSelect = vi.fn();
    render(
      <DerivedWords
        words={["كتاب", "كتب"]}
        selectedWord={null}
        onWordSelect={onWordSelect}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "كتاب" }));
    expect(onWordSelect).toHaveBeenCalledWith("كتاب");
  });
});

// ── SurahChart Tests ────────────────────────────────────────────────────────

describe("SurahChart", () => {
  it("renders Recharts chart with data", () => {
    render(
      <SurahChart
        data={[{ surah_id: 2, surah_name: "البقرة", count: 45 }]}
        language="quran"
      />
    );

    expect(screen.getByText("Surah Distribution")).toBeInTheDocument();
    expect(screen.getByTestId("bar-chart")).toBeInTheDocument();
  });

  it("limits to 20 bars initially", () => {
    // Generate 25 items
    const data = Array.from({ length: 25 }, (_, i) => ({
      surah_id: i + 1,
      surah_name: `سورة ${i + 1}`,
      count: 100 - i,
    }));

    render(<SurahChart data={data} language="quran" />);

    expect(screen.getByText(/Show all 25 surahs/i)).toBeInTheDocument();
  });

  it("shows empty state when no data", () => {
    render(<SurahChart data={[]} language="quran" />);

    expect(screen.getByText("No surah distribution data")).toBeInTheDocument();
  });
});

// ── VerseCard Tests ─────────────────────────────────────────────────────────

describe("VerseCard", () => {
  const defaultProps = {
    surahId: 2,
    surahName: "البقرة",
    ayahNumber: 2,
    textUthmani: "ذَٰلِكَ ٱلۡكِتَٰبُ لَا رَيۡبَ فِيهِ",
    textClean: "ذلك الكتاب لا ريب فيه",
    matchedWords: ["الكتاب"],
  };

  it("renders Arabic text in RTL with Turkish translation", () => {
    render(
      <VerseCard
        {...defaultProps}
        turkishTranslation="Bu, kendisinde hiç şüphe olmayan kitaptır."
      />
    );

    // Arabic text should be present
    expect(screen.getByText(/ٱلۡكِتَٰبُ/)).toBeInTheDocument();
    // Turkish translation
    expect(
      screen.getByText("Bu, kendisinde hiç şüphe olmayan kitaptır.")
    ).toBeInTheDocument();
  });

  it("highlights matched words", () => {
    const { container } = render(<VerseCard {...defaultProps} />);

    // The highlightArabicText function wraps matched words in <mark> elements
    const marks = container.querySelectorAll("mark");
    expect(marks.length).toBeGreaterThan(0);
  });

  it("shows skeleton while translation loads", () => {
    render(<VerseCard {...defaultProps} isTranslationLoading={true} />);

    const skeletons = screen.getAllByTestId("skeleton");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("links to correct surah page", () => {
    render(<VerseCard {...defaultProps} />);

    const link = screen.getByRole("link", { name: /Go to surah/i });
    expect(link).toHaveAttribute("href", "/quran/2?verse=2");
  });
});

// ── Pagination Tests ────────────────────────────────────────────────────────

describe("Pagination", () => {
  it("shows correct page info", () => {
    render(
      <Pagination
        page={1}
        totalPages={7}
        totalVerses={319}
        hasNext={true}
        hasPrev={false}
        onPageChange={vi.fn()}
      />
    );

    expect(screen.getByText(/Page 1 of 7/)).toBeInTheDocument();
    expect(screen.getByText(/319 verses/)).toBeInTheDocument();
  });

  it("disables Previous on page 1", () => {
    render(
      <Pagination
        page={1}
        totalPages={7}
        totalVerses={319}
        hasNext={true}
        hasPrev={false}
        onPageChange={vi.fn()}
      />
    );

    const prevButton = screen.getByRole("button", { name: /Previous/i });
    expect(prevButton).toBeDisabled();
  });

  it("disables Next on last page", () => {
    render(
      <Pagination
        page={7}
        totalPages={7}
        totalVerses={319}
        hasNext={false}
        hasPrev={true}
        onPageChange={vi.fn()}
      />
    );

    const nextButton = screen.getByRole("button", { name: /Next/i });
    expect(nextButton).toBeDisabled();
  });
});

// ── AccuracyDisclaimer Tests ─────────────────────────────────────────────────

describe("AccuracyDisclaimer", () => {
  it("renders collapsed disclaimer message", () => {
    render(<AccuracyDisclaimer />);

    expect(screen.getByText(/Clarus can make mistakes/i)).toBeInTheDocument();
    expect(screen.getByText(/Verify important information/i)).toBeInTheDocument();
  });

  it("expands to show verification table on click", async () => {
    render(<AccuracyDisclaimer />);

    // Initially, the table should not be visible
    expect(screen.queryByText("Accuracy Verification")).not.toBeInTheDocument();

    // Click to expand
    fireEvent.click(screen.getByText(/Clarus can make mistakes/i));

    // Now the table should be visible
    await waitFor(() => {
      expect(screen.getByText("Accuracy Verification")).toBeInTheDocument();
    });
  });

  it("displays verification data with correct Strong's numbers", async () => {
    render(<AccuracyDisclaimer />);

    // Expand the disclaimer
    fireEvent.click(screen.getByText(/Clarus can make mistakes/i));

    await waitFor(() => {
      // Check for Strong's numbers
      expect(screen.getByText("H1697")).toBeInTheDocument();
      expect(screen.getByText("H8451")).toBeInTheDocument();
      expect(screen.getByText("H430")).toBeInTheDocument();
      expect(screen.getByText("G2316")).toBeInTheDocument();
    });
  });

  it("displays verification data with word names", async () => {
    render(<AccuracyDisclaimer />);

    // Expand the disclaimer
    fireEvent.click(screen.getByText(/Clarus can make mistakes/i));

    await waitFor(() => {
      // Check for word names
      expect(screen.getByText("dabar")).toBeInTheDocument();
      expect(screen.getByText("torah")).toBeInTheDocument();
      expect(screen.getByText("elohim")).toBeInTheDocument();
      expect(screen.getByText("theos")).toBeInTheDocument();
    });
  });

  it("shows Blue Letter Bible link", async () => {
    render(<AccuracyDisclaimer />);

    // Expand the disclaimer
    fireEvent.click(screen.getByText(/Clarus can make mistakes/i));

    await waitFor(() => {
      const blbLink = screen.getByRole("link", { name: /Blue Letter Bible/i });
      expect(blbLink).toHaveAttribute("href", "https://www.blueletterbible.org/");
      expect(blbLink).toHaveAttribute("target", "_blank");
    });
  });

  it("shows status badges for verification results", async () => {
    render(<AccuracyDisclaimer />);

    // Expand the disclaimer
    fireEvent.click(screen.getByText(/Clarus can make mistakes/i));

    await waitFor(() => {
      // Should show EXACT for torah (0 delta) and PASS for others
      expect(screen.getByText("EXACT")).toBeInTheDocument();
      expect(screen.getAllByText("PASS").length).toBe(3); // dabar, elohim, theos
    });
  });

  it("displays data source information", async () => {
    render(<AccuracyDisclaimer />);

    // Expand the disclaimer
    fireEvent.click(screen.getByText(/Clarus can make mistakes/i));

    await waitFor(() => {
      // Use getAllByText since OSHB/MorphGNT appear in multiple places
      expect(screen.getAllByText(/OSHB/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/MorphGNT/i).length).toBeGreaterThan(0);
    });
  });

  it("collapses when clicked again", async () => {
    render(<AccuracyDisclaimer />);

    const toggleButton = screen.getByText(/Clarus can make mistakes/i);

    // Expand
    fireEvent.click(toggleButton);
    await waitFor(() => {
      expect(screen.getByText("Accuracy Verification")).toBeInTheDocument();
    });

    // Collapse
    fireEvent.click(toggleButton);
    await waitFor(() => {
      expect(screen.queryByText("Accuracy Verification")).not.toBeInTheDocument();
    });
  });
});

// ── ExperimentalDisclaimer Tests ──────────────────────────────────────────────

describe("ExperimentalDisclaimer", () => {
  it("renders experimental warning message", () => {
    render(<ExperimentalDisclaimer />);

    expect(screen.getByText(/Experimental Feature/i)).toBeInTheDocument();
    expect(screen.getByText(/under active development/i)).toBeInTheDocument();
  });

  it("shows warning about academic research", () => {
    render(<ExperimentalDisclaimer />);

    expect(screen.getByText(/should not be used as the sole basis for academic or theological research/i)).toBeInTheDocument();
  });

  it("advises to verify with authoritative sources", () => {
    render(<ExperimentalDisclaimer />);

    expect(screen.getByText(/Always verify with authoritative sources/i)).toBeInTheDocument();
  });

  it("renders alert triangle icon", () => {
    render(<ExperimentalDisclaimer />);

    expect(screen.getByTestId("alert-triangle-icon")).toBeInTheDocument();
  });

  it("accepts className prop", () => {
    const { container } = render(<ExperimentalDisclaimer className="custom-class" />);

    const disclaimer = container.firstChild;
    expect(disclaimer).toHaveClass("custom-class");
  });
});
