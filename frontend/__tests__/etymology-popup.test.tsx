import { render, screen, waitFor } from "@testing-library/react"
import { vi, describe, it, expect, beforeEach } from "vitest"
import type React from "react"
import userEvent from "@testing-library/user-event"

type MockProps = {
  children?: React.ReactNode
  className?: string
  [key: string]: unknown
}

vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: MockProps) => <div {...props}>{children}</div>,
    span: ({ children, ...props }: MockProps) => <span {...props}>{children}</span>,
    ul: ({ children, ...props }: MockProps) => <ul {...props}>{children}</ul>,
    li: ({ children, ...props }: MockProps) => <li {...props}>{children}</li>,
  },
  AnimatePresence: ({ children }: { children?: React.ReactNode }) => <>{children}</>,
}))

vi.mock("lucide-react", () => ({
  ArrowRight: () => <div data-testid="arrow-right-icon" />,
  ChevronDown: () => <div data-testid="chevron-down-icon" />,
  ChevronUp: () => <div data-testid="chevron-up-icon" />,
  AlertCircle: () => <div data-testid="alert-circle-icon" />,
}))

vi.mock("@/components/ui/skeleton", () => ({
  Skeleton: ({ className }: MockProps) => <div data-testid="skeleton" className={className} />,
}))

vi.mock("@/components/ui/popover", () => ({
  Popover: ({ children, open }: { children: React.ReactNode; open?: boolean }) =>
    open ? <>{children}</> : null,
  PopoverTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  PopoverContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

vi.mock("@/components/ui/button", () => ({
  Button: ({ children, ...props }: MockProps) => <button {...props}>{children}</button>,
}))

vi.mock("@/components/ui/popover", () => ({
  Popover: ({ children, open }: { children: React.ReactNode; open?: boolean }) =>
    open ? <>{children}</> : null,
  PopoverTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  PopoverContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: MockProps & { href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}))

vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: MockProps & { href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}))

const mockUseQuery = vi.fn()

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => mockUseQuery(options),
}))

const mockGetEtymology = vi.fn()

vi.mock("@/lib/api", () => ({
  getEtymologyApiEtymologyRootGet: (params: unknown) => mockGetEtymology(params),
  getVerseWordsApiQuranVersesSurahIdAyahNumberWordsGet: vi.fn(),
}))

import { EtymologyPopup } from "@/components/quran/etymology-popup"
import { ClickableVerse } from "@/components/quran/clickable-verse"

const mockEtymologyData = {
  id: 1,
  root: "كتب",
  root_buckwalter: "ktb",
  definition_en: "To write, to inscribe, to ordain, to decree",
  definition_tr: "Yazmak, kaydetmek, takdir etmek",
  semantic_field: "writing",
  morphological_forms: [
    { form_pattern: "فَعَلَ", form_arabic: "كَتَبَ", occurrences: 100 },
    { form_pattern: "فَاعِل", form_arabic: "كَاتِب", occurrences: 50 },
    { form_pattern: "مَفْعُول", form_arabic: "مَكْتُوب", occurrences: 30 },
    { form_pattern: "فِعَال", form_arabic: "كِتَاب", occurrences: 25 },
    { form_pattern: "مُفَاعَلَة", form_arabic: "مُكَاتَبَة", occurrences: 15 },
    { form_pattern: "تَفَاعُل", form_arabic: "تَكَاتُب", occurrences: 10 },
  ],
  related_roots: [],
  quran_frequency: 319,
  source: "lane",
  lane_match_type: "exact",
  lane_volume: 7,
  confidence: "high",
  tr_translation_source: "gemini",
  tr_translation_confidence: 0.95,
  created_at: "2024-01-01T00:00:00",
  updated_at: "2024-01-01T00:00:00",
}

describe("EtymologyPopup", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders root in Arabic and Buckwalter", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      expect(screen.getByText("كتب")).toBeInTheDocument()
      expect(screen.getByText("(ktb)")).toBeInTheDocument()
    })
  })

  it("renders Turkish definition", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      expect(screen.getByText(/Yazmak, kaydetmek, takdir etmek/)).toBeInTheDocument()
    })
  })

  it("renders English definition", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      expect(screen.getByText(/To write, to inscribe, to ordain, to decree/)).toBeInTheDocument()
    })
  })

  it("renders morphological forms", async () => {
    const user = userEvent.setup()

    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      expect(screen.getByText(/Morfolojik Formlar/)).toBeInTheDocument()
    })

    const expandButton = screen.getByRole("button", { name: /Tümünü Gör \(6\)/ })
    await user.click(expandButton)

    await waitFor(() => {
      expect(screen.getByText("كَتَبَ")).toBeInTheDocument()
      expect(screen.getByText("كَاتِب")).toBeInTheDocument()
      expect(screen.getByText(/100 kez/)).toBeInTheDocument()
    })
  })

  it("renders quran frequency count", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      expect(screen.getByText(/319 kez/)).toBeInTheDocument()
    })
  })

  it("renders keyword search link", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      expect(screen.getByTestId("detail-link")).toBeInTheDocument()
      expect(screen.getByTestId("detail-link")).toHaveAttribute("href", "/keyword-search?q=ktb")
      expect(screen.getByText("Detaylı Analiz")).toBeInTheDocument()
    })
  })

  it("renders loading skeleton when fetching", async () => {
    mockUseQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      const skeletons = screen.getAllByTestId("skeleton")
      expect(skeletons.length).toBeGreaterThan(0)
    })
  })

  it("renders error state on API failure", async () => {
    mockUseQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      expect(screen.getByText("Etimoloji bilgisi yüklenemedi")).toBeInTheDocument()
      expect(screen.getByRole("button", { name: /Tekrar Dene/ })).toBeInTheDocument()
    })
  })

  it("does not render popup for words without etymology", async () => {
    mockUseQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup
        word={{ token: "و", root: null, has_etymology: false }}
        open={true}
        onOpenChange={vi.fn()}
      >
        <button>Click me</button>
      </EtymologyPopup>
    )

    expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument()
    expect(screen.queryByText("Bu kelime için kök bilgisi mevcut değil")).not.toBeInTheDocument()
  })

  it("shows expand/collapse button for more than 5 forms", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      expect(screen.getByText(/Tümünü Gör \(6\)/)).toBeInTheDocument()
    })
  })

  it("expands to show all forms on expand button click", async () => {
    const user = userEvent.setup()

    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Tümünü Gör \(6\)/ })).toBeInTheDocument()
    })

    const expandButton = screen.getByRole("button", { name: /Tümünü Gör \(6\)/ })
    await user.click(expandButton)

    await waitFor(() => {
      expect(screen.getByText("تَكَاتُب")).toBeInTheDocument()
      expect(screen.getByText(/Daha Az/)).toBeInTheDocument()
    })
  })

  it("renders confidence badge", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    })

    render(
      <EtymologyPopup root="كتب" rootBuckwalter="ktb" open={true} onOpenChange={vi.fn()}>
        <button>Click me</button>
      </EtymologyPopup>
    )

    await waitFor(() => {
      expect(screen.getByText("Yüksek")).toBeInTheDocument()
    })
  })
})

describe("ClickableVerse", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders fallback on loading", async () => {
    mockUseQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    })

    render(<ClickableVerse surahId={1} ayahNumber={1} arabicText="بِسْمِ اللَّهِ" />)

    await waitFor(() => {
      expect(screen.getByText("بِسْمِ اللَّهِ")).toBeInTheDocument()
    })
  })

  it("renders fallback on error", async () => {
    mockUseQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
    })

    render(<ClickableVerse surahId={1} ayahNumber={1} arabicText="بِسْمِ اللَّهِ" />)

    await waitFor(() => {
      expect(screen.getByText("بِسْمِ اللَّهِ")).toBeInTheDocument()
    })
  })

  it("renders fallback when no words data", async () => {
    mockUseQuery.mockReturnValue({
      data: { words: [] },
      isLoading: false,
      isError: false,
    })

    render(<ClickableVerse surahId={1} ayahNumber={1} arabicText="بِسْمِ اللَّهِ" />)

    await waitFor(() => {
      expect(screen.getByText("بِسْمِ اللَّهِ")).toBeInTheDocument()
    })
  })

  it("renders words when data available", async () => {
    mockUseQuery.mockReturnValue({
      data: {
        words: [
          {
            position: 0,
            token: "بِسْمِ",
            root: "سمو",
            root_buckwalter: "smw",
            has_etymology: true,
          },
          {
            position: 1,
            token: "اللَّهِ",
            root: "اله",
            root_buckwalter: "Alh",
            has_etymology: true,
          },
        ],
      },
      isLoading: false,
      isError: false,
    })

    render(<ClickableVerse surahId={1} ayahNumber={1} arabicText="بِسْمِ اللَّهِ" />)

    await waitFor(() => {
      expect(screen.getByText("بِسْمِ")).toBeInTheDocument()
      expect(screen.getByText("اللَّهِ")).toBeInTheDocument()
    })
  })
})
