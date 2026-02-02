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

// ── RootCard Tests ──────────────────────────────────────────────────────────

describe("RootCard", () => {
  it("renders Arabic root in RTL", () => {
    render(<RootCard root="كتب" rootSource="exact_match" />);

    const rootText = screen.getByText("كتب");
    expect(rootText).toBeInTheDocument();
    expect(rootText).toHaveAttribute("lang", "ar");
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
      <StatsBar totalOccurrences={319} uniqueWords={5} surahCount={12} />
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

    render(<SurahChart data={data} />);

    expect(screen.getByText(/Show all 25 surahs/i)).toBeInTheDocument();
  });

  it("shows empty state when no data", () => {
    render(<SurahChart data={[]} />);

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
