import { render, screen, waitFor } from "@testing-library/react"
import { vi, describe, it, expect, beforeEach } from "vitest"
import type React from "react"

type MockProps = {
  children?: React.ReactNode
  className?: string
  [key: string]: unknown
}

const mockPush = vi.fn()
const mockParams = { root: "ktb" }

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(() => ({ push: mockPush })),
  useParams: vi.fn(() => mockParams),
}))

vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: MockProps & { href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}))

vi.mock("@/lib/auth-client", () => ({
  useSession: vi.fn(() => ({
    data: { user: { id: "1", name: "Test User", email: "test@example.com" } },
    isPending: false,
  })),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}))

vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: MockProps) => <div {...props}>{children}</div>,
    h1: ({ children, ...props }: MockProps) => <h1 {...props}>{children}</h1>,
    p: ({ children, ...props }: MockProps) => <p {...props}>{children}</p>,
  },
  AnimatePresence: ({ children }: { children?: React.ReactNode }) => <>{children}</>,
}))

vi.mock("lucide-react", () => ({
  ArrowLeft: () => <div data-testid="arrow-left-icon" />,
}))

vi.mock("@/components/ui/glow-card", () => ({
  GlowCard: ({ children, className, ...rest }: MockProps) => <div className={className} {...rest}>{children}</div>,
}))

vi.mock("@/components/ui/skeleton", () => ({
  Skeleton: ({ className }: MockProps) => <div data-testid="skeleton" className={className} />,
}))

vi.mock("@/lib/design-system", () => ({
  springPresets: {
    snappy: { type: "spring", stiffness: 300, damping: 30 },
    fluid: { type: "spring", stiffness: 170, damping: 26 },
    gentle: { type: "spring", stiffness: 120, damping: 14 },
  },
}))

const mockEtymologyData = {
  id: 1,
  root: "كتب",
  root_buckwalter: "ktb",
  definition_en: "To write, to inscribe. Lane's Lexicon definition goes here...",
  definition_tr: "Yazmak, kaydetmek. Türkçe açıklama...",
  summary_tr: "Yazı ve kayıt kavramları ile ilgili kök.",
  summary_en: "Root related to writing and recording concepts.",
  semantic_field: "writing",
  morphological_forms: [
    {
      form_pattern: "فعل",
      form_arabic: "كتب",
      form_name: "Verb Form I",
      form_category: "verb",
      example_word: "كتب",
      occurrences: 45,
    },
  ],
  related_roots: [
    { root: "قرأ", root_buckwalter: "qr>", meaning_hint: "to read" },
  ],
  quran_frequency: 319,
  source: "lane",
  lane_match_type: "exact",
  lane_volume: 5,
  confidence: "high",
  keyword_search_url: "/keyword-search?query=ktb",
}

global.fetch = vi.fn()

import RootDetailPage from "@/app/keyword-search/root/[root]/page"

describe("RootDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: async () => mockEtymologyData,
    } as Response)
  })

  it("renders loading skeleton initially", () => {
    render(<RootDetailPage />)
    expect(screen.getAllByTestId("skeleton").length).toBeGreaterThan(0)
  })

  it("renders etymology data after successful fetch", async () => {
    render(<RootDetailPage />)

    await waitFor(() => {
      expect(screen.getByTestId("root-arabic")).toHaveTextContent("كتب")
      expect(screen.getByTestId("root-buckwalter")).toHaveTextContent("ktb")
    })

    expect(screen.getByText("319 kullanım")).toBeInTheDocument()
    expect(screen.getByText("Lane's Lexicon")).toBeInTheDocument()
    expect(screen.getByText("high")).toBeInTheDocument()
  })

  it("renders Turkish and English definition sections without summary", async () => {
    render(<RootDetailPage />)

    await waitFor(() => {
      expect(screen.getByText("Türkçe Çeviri")).toBeInTheDocument()
    })

    expect(screen.getByText("Orijinal Lane's Lexicon")).toBeInTheDocument()
    expect(screen.getByText(/Morfolojik Formlar/)).toBeInTheDocument()
    // Summary section should NOT be present on this page
    expect(screen.queryByText("Özet")).not.toBeInTheDocument()
  })

  it("renders both definitions as flat open sections (no collapsible)", async () => {
    render(<RootDetailPage />)

    await waitFor(() => {
      expect(screen.getByTestId("definition-tr-section")).toBeInTheDocument()
    })

    expect(screen.getByTestId("definition-en-section")).toBeInTheDocument()
    // Lane's definition text should be visible without clicking (no collapsible)
    expect(screen.getByText("To write, to inscribe. Lane's Lexicon definition goes here...")).toBeInTheDocument()
    expect(screen.getByText("Yazmak, kaydetmek. Türkçe açıklama...")).toBeInTheDocument()
  })

  it("renders error message when root not found (404)", async () => {
    ;(global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      status: 404,
    } as Response)

    render(<RootDetailPage />)

    await waitFor(() => {
      expect(screen.getByText("Kök bulunamadı")).toBeInTheDocument()
    })

    expect(screen.getByText("← Kelime Aramasına Dön")).toBeInTheDocument()
  })

  it("renders error message on fetch failure", async () => {
    ;(global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      status: 500,
    } as Response)

    render(<RootDetailPage />)

    await waitFor(() => {
      expect(screen.getByText("Veri yüklenirken hata oluştu")).toBeInTheDocument()
    })
  })

  it("renders back link with correct href", async () => {
    render(<RootDetailPage />)

    await waitFor(() => {
      expect(screen.getByTestId("back-link")).toBeInTheDocument()
    })

    const backLink = screen.getByTestId("back-link")
    expect(backLink).toHaveAttribute("href", "/keyword-search")
  })

  it("renders definition sections when data is present", async () => {
    render(<RootDetailPage />)

    await waitFor(() => {
      expect(screen.getByText("Türkçe Çeviri")).toBeInTheDocument()
    })

    expect(screen.getByText("Orijinal Lane's Lexicon")).toBeInTheDocument()
    expect(screen.getByText("Yazmak, kaydetmek. Türkçe açıklama...")).toBeInTheDocument()
  })

  it("renders morphological forms section", async () => {
    render(<RootDetailPage />)

    await waitFor(() => {
      expect(screen.getByText(/Morfolojik Formlar \(1\)/)).toBeInTheDocument()
    })

    expect(screen.getAllByText("كتب").length).toBeGreaterThan(0)
  })
})
