import { render, screen, waitFor, fireEvent } from "@testing-library/react"
import { vi, describe, it, expect, beforeEach } from "vitest"
import type React from "react"

type MockProps = {
  children?: React.ReactNode
  className?: string
  [key: string]: unknown
}

vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: MockProps) => <div {...props}>{children}</div>,
    a: ({ children, ...props }: MockProps) => <a {...props}>{children}</a>,
    button: ({ children, ...props }: MockProps) => <button {...props}>{children}</button>,
  },
}))

vi.mock("lucide-react", () => ({
  ChevronDown: () => <div data-testid="chevron-down-icon" />,
  ChevronRight: () => <div data-testid="chevron-right-icon" />,
  ExternalLink: () => <div data-testid="external-link-icon" />,
}))

vi.mock("@/lib/design-system", () => ({
  springPresets: {
    fluid: { type: "spring", stiffness: 170, damping: 26 },
    snappy: { type: "spring", stiffness: 300, damping: 30 },
  },
  tactileScale: {
    hover: { y: -2 },
    press: { scale: 0.98 },
  },
}))

vi.mock("@/components/ui/glow-card", () => ({
  GlowCard: ({ children, className }: MockProps) => <div className={className}>{children}</div>,
}))

vi.mock("@/components/ui/skeleton", () => ({
  Skeleton: ({ className }: MockProps) => <div data-testid="skeleton" className={className} />,
}))

vi.mock("@/lib/utils", () => ({
  cn: (...classes: string[]) => classes.filter(Boolean).join(" "),
}))

const mockGetEtymology = vi.fn()

vi.mock("@/lib/api/sdk.gen", () => ({
  getEtymologyApiEtymologyRootGet: (...args: unknown[]) => mockGetEtymology(...args),
}))

const mockUseQuery = vi.fn()

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => mockUseQuery(options),
}))

import { RichRootCard } from "@/components/keyword-search/rich-root-card"

const mockEtymologyData = {
  root: "كتب",
  root_buckwalter: "ktb",
  definition_tr: "Yazmak, kaydetmek, kitap yazmak",
  definition_en: "To write, record, prescribe",
  quran_frequency: 319,
  source: "lane",
  confidence: "high",
  morphological_forms: [
    { form_arabic: "كَتَبَ", form_category: "Verb Form I", example_word: "كَتَبَ" },
    { form_arabic: "كِتَاب", form_category: "Noun", example_word: "الْكِتَاب" },
    { form_arabic: "كَاتِب", form_category: "Active Participle", example_word: "كَاتِب" },
    { form_arabic: "مَكْتُوب", form_category: "Passive Participle", example_word: "مَكْتُوب" },
    { form_arabic: "مَكْتَب", form_category: "Place Noun", example_word: "مَكْتَب" },
    { form_arabic: "كُتَّاب", form_category: "Intensive Form", example_word: "كُتَّاب" },
  ],
}

describe("RichRootCard", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders Arabic root in RTL", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="كتب"
        rootSource="exact_match"
        rootBuckwalter="ktb"
        query="كتب"
        language="arabic"
      />
    )

    await waitFor(() => {
      const rootElement = screen.getByText("كتب")
      expect(rootElement).toBeInTheDocument()
      expect(rootElement.closest("p")).toHaveAttribute("lang", "ar")
      expect(rootElement.closest("p")).toHaveAttribute("dir", "rtl")
    })
  })

  it("renders Turkish definition", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="كتب"
        rootSource="exact_match"
        rootBuckwalter="ktb"
        query="كتب"
        language="arabic"
      />
    )

    await waitFor(() => {
      expect(screen.getByTestId("root-definition-tr")).toBeInTheDocument()
      expect(screen.getByText("Yazmak, kaydetmek, kitap yazmak")).toBeInTheDocument()
    })
  })

  it("renders English definition", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="كتب"
        rootSource="exact_match"
        rootBuckwalter="ktb"
        query="كتب"
        language="arabic"
      />
    )

    await waitFor(() => {
      expect(screen.getByTestId("root-definition-en")).toBeInTheDocument()
      expect(screen.getByText("To write, record, prescribe")).toBeInTheDocument()
    })
  })

  it("renders frequency badge", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="كتب"
        rootSource="exact_match"
        rootBuckwalter="ktb"
        query="كتب"
        language="arabic"
      />
    )

    await waitFor(() => {
      expect(screen.getByTestId("root-frequency")).toBeInTheDocument()
      expect(screen.getByText("319 occurrences")).toBeInTheDocument()
    })
  })

  it("renders morphological forms", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="كتب"
        rootSource="exact_match"
        rootBuckwalter="ktb"
        query="كتب"
        language="arabic"
      />
    )

    await waitFor(() => {
      const formsSection = screen.getByTestId("morphological-forms")
      expect(formsSection).toBeInTheDocument()
      expect(formsSection.textContent).toContain("Verb Form I")
      expect(formsSection.textContent).toContain("Noun")
      expect(screen.getAllByText("كَتَبَ").length).toBeGreaterThan(0)
      expect(screen.getByText("كِتَاب")).toBeInTheDocument()
    })
  })

  it("shows confidence badge with high confidence", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="كتب"
        rootSource="exact_match"
        rootBuckwalter="ktb"
        query="كتب"
        language="arabic"
      />
    )

    await waitFor(() => {
      expect(screen.getByText("high")).toBeInTheDocument()
    })
  })

  it("shows source badge for Lane's Lexicon", async () => {
    mockUseQuery.mockReturnValue({
      data: mockEtymologyData,
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="كتب"
        rootSource="exact_match"
        rootBuckwalter="ktb"
        query="كتب"
        language="arabic"
      />
    )

    await waitFor(() => {
      expect(screen.getByText("Lane's Lexicon")).toBeInTheDocument()
    })
  })

  it("shows loading state with skeletons", () => {
    mockUseQuery.mockReturnValue({
      data: null,
      isLoading: true,
      isError: false,
    })

    render(
      <RichRootCard
        root="كتب"
        rootSource="exact_match"
        rootBuckwalter="ktb"
        query="كتب"
        language="arabic"
      />
    )

    const skeletons = screen.getAllByTestId("skeleton")
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it("shows fallback when etymology fetch fails", () => {
    mockUseQuery.mockReturnValue({
      data: null,
      isLoading: false,
      isError: true,
    })

    render(
      <RichRootCard
        root="كتب"
        rootSource="exact_match"
        rootBuckwalter="ktb"
        query="كتب"
        language="arabic"
      />
    )

    expect(screen.getByText("كتب")).toBeInTheDocument()
    expect(screen.getByText("ktb")).toBeInTheDocument()
  })

  it("expands and collapses morphological forms", async () => {
    const manyForms = Array.from({ length: 10 }, (_, i) => ({
      form_arabic: `Form ${i}`,
      form_category: `Category ${i}`,
      example_word: `Example ${i}`,
    }))

    mockUseQuery.mockReturnValue({
      data: { ...mockEtymologyData, morphological_forms: manyForms },
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="كتب"
        rootSource="exact_match"
        rootBuckwalter="ktb"
        query="كتب"
        language="arabic"
      />
    )

    await waitFor(() => {
      expect(screen.getByText(/Show all \(10\)/)).toBeInTheDocument()
    })

    const showAllButton = screen.getByText(/Show all \(10\)/)
    fireEvent.click(showAllButton)

    await waitFor(() => {
      expect(screen.getByText("Show less")).toBeInTheDocument()
    })
  })

  it("renders Hebrew root for non-Arabic language", () => {
    mockUseQuery.mockReturnValue({
      data: null,
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="תורה"
        rootSource="exact_match"
        rootBuckwalter="torah"
        query="torah"
        language="hebrew"
      />
    )

    expect(screen.getByText("תורה")).toBeInTheDocument()
    expect(screen.getByText("torah")).toBeInTheDocument()
  })

  it("renders Greek root for Greek language", () => {
    mockUseQuery.mockReturnValue({
      data: null,
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="θεός"
        rootSource="exact_match"
        rootBuckwalter="theos"
        query="theos"
        language="greek"
      />
    )

    expect(screen.getByText("θεός")).toBeInTheDocument()
    expect(screen.getByText("theos")).toBeInTheDocument()
  })

  it("does not fetch etymology for non-Arabic roots", () => {
    mockUseQuery.mockReturnValue({
      data: null,
      isLoading: false,
      isError: false,
    })

    render(
      <RichRootCard
        root="torah"
        rootSource="exact_match"
        rootBuckwalter="torah"
        query="torah"
        language="hebrew"
      />
    )

    expect(mockUseQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        enabled: false,
      })
    )
  })
})
