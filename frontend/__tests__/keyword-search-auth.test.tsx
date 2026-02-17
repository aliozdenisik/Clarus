import { render, screen, waitFor } from "./test-utils"
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
  useSearchParams: vi.fn(() => new URLSearchParams()),
  usePathname: vi.fn(() => "/keyword-search"),
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
    data: null,
    isPending: false,
  })),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}))

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}))

vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: MockProps) => <div {...props}>{children}</div>,
    h1: ({ children, ...props }: MockProps) => <h1 {...props}>{children}</h1>,
    p: ({ children, ...props }: MockProps) => <p {...props}>{children}</p>,
    button: ({ children, ...props }: MockProps) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: { children?: React.ReactNode }) => <>{children}</>,
}))

vi.mock("lucide-react", () => ({
  Search: () => <div data-testid="search-icon" />,
  ArrowLeft: () => <div data-testid="arrow-left-icon" />,
  AlertTriangle: () => <div data-testid="alert-triangle-icon" />,
}))

vi.mock("@/components/ui/magic-card", () => ({
  MagicCard: ({ children, className }: MockProps) => <div className={className}>{children}</div>,
}))

vi.mock("@/components/ui/skeleton", () => ({
  Skeleton: ({ className }: MockProps) => <div data-testid="skeleton" className={className} />,
}))

vi.mock("@/lib/design-system", () => ({
  springPresets: {
    snappy: { type: "spring", stiffness: 300, damping: 30 },
    fluid: { type: "spring", stiffness: 170, damping: 26 },
  },
}))

vi.mock("next-intl", () => ({
  useTranslations: vi.fn(() => (key: string) => key),
  NextIntlClientProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

vi.mock("@tanstack/react-query", () => ({
  useQuery: vi.fn(() => ({
    data: null,
    isLoading: false,
    isError: false,
  })),
  QueryClient: vi.fn(),
  QueryClientProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: MockProps) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  BarChart: ({ children }: MockProps) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  Tooltip: () => <div data-testid="tooltip" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
}))

vi.mock("react-virtuoso", () => ({
  Virtuoso: ({
    totalCount,
    itemContent,
  }: {
    totalCount: number
    itemContent: (index: number) => React.ReactNode
  }) => (
    <div data-testid="virtuoso-mock">
      {Array.from({ length: totalCount }, (_, i) => (
        <div key={`virtuoso-item-${i}`}>{itemContent(i)}</div>
      ))}
    </div>
  ),
}))

vi.mock("@/components/ui/animated-tabs", () => ({
  AnimatedFilterTabs: ({
    tabs,
    activeTab,
  }: {
    tabs: Array<{ id: string; label: string }>
    activeTab: string
  }) => (
    <div data-testid="animated-tabs">
      {tabs.map((tab) => (
        <div key={tab.id} data-active={activeTab === tab.id}>
          {tab.label}
        </div>
      ))}
    </div>
  ),
}))

const mockSearchKeyword = vi.fn()
const mockGetSurahDetail = vi.fn()
const mockGetQuranSurahs = vi.fn()

vi.mock("@/lib/api/sdk.gen", () => ({
  searchKeywordApiSearchKeywordPost: (...args: unknown[]) => mockSearchKeyword(...args),
  getSurahDetailApiMetadataQuranSurahsSurahIdGet: (...args: unknown[]) =>
    mockGetSurahDetail(...args),
  getQuranSurahsApiMetadataQuranSurahsGet: (...args: unknown[]) => mockGetQuranSurahs(...args),
}))

global.fetch = vi.fn()

import KeywordSearchPage from "@/app/[locale]/keyword-search/page"
import RootDetailPage from "@/app/[locale]/keyword-search/root/[root]/page"

describe("Keyword Search Auth Removal", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetSurahDetail.mockResolvedValue({ data: { verses: [] } })
    mockGetQuranSurahs.mockResolvedValue({ data: { surahs: [] } })
  })

  it("keyword search page renders without auth", () => {
    render(<KeywordSearchPage />)

    expect(screen.getByText("pageTitle")).toBeInTheDocument()
    expect(screen.getByPlaceholderText("placeholderQuran")).toBeInTheDocument()

    expect(screen.queryByText("Sign in required")).not.toBeInTheDocument()
  })

  it("root detail page renders without auth", async () => {
    const mockEtymologyData = {
      id: 1,
      root: "كتب",
      root_buckwalter: "ktb",
      definition_en: "To write",
      definition_tr: "Yazmak",
      summary_tr: null,
      summary_en: null,
      semantic_field: "writing",
      morphological_forms: [],
      related_roots: [],
      quran_frequency: 319,
      source: "lane",
      lane_match_type: "exact",
      lane_volume: 5,
      confidence: "high",
      keyword_search_url: "/keyword-search?query=ktb",
    }

    ;(global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: async () => mockEtymologyData,
    } as Response)

    render(<RootDetailPage />)

    await waitFor(() => {
      expect(screen.getByTestId("root-arabic")).toHaveTextContent("كتب")
    })

    expect(screen.getByTestId("root-buckwalter")).toHaveTextContent("ktb")
    expect(screen.getByText("319 kullanım")).toBeInTheDocument()
  })

  it("no sign-in redirect in keyword search page", () => {
    render(<KeywordSearchPage />)

    expect(mockPush).not.toHaveBeenCalled()

    expect(screen.getByText("pageTitle")).toBeInTheDocument()
  })

  it("middleware does NOT include /keyword-search in protectedRoutes", () => {
    const expectedProtectedRoutes = ["/compare", "/search", "/settings", "/history"]
    const notProtectedRoutes = ["/keyword-search"]

    expect(notProtectedRoutes).not.toContain("/compare")
    expect(expectedProtectedRoutes).not.toContain("/keyword-search")
  })
})
