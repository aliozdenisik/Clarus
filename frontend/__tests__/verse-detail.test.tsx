import { render, screen, waitFor } from "@testing-library/react"
import { vi, describe, it, expect, beforeEach } from "vitest"
import type React from "react"

type MockProps = {
  children?: React.ReactNode
  className?: string
  [key: string]: unknown
}

// Mock next/navigation
const mockPush = vi.fn()
const mockReplace = vi.fn()
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    replace: mockReplace,
  }),
  useParams: () => ({
    surahId: "2",
    verseId: "255",
  }),
}))

// Mock Better Auth
const mockSession: {
  data: { user: { id: string; name: string; email: string } } | null
  isPending: boolean
} = {
  data: { user: { id: "1", name: "Test User", email: "test@example.com" } },
  isPending: false,
}
vi.mock("@/lib/auth-client", () => ({
  useSession: () => mockSession,
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}))

// Mock sonner toast
vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}))

// Mock framer-motion
vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: MockProps) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: MockProps) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: { children?: React.ReactNode }) => <>{children}</>,
}))

// Mock Lucide icons
vi.mock("lucide-react", () => ({
  ArrowLeft: () => <div data-testid="arrow-left-icon" />,
  ChevronLeft: () => <div data-testid="chevron-left-icon" />,
  ChevronRight: () => <div data-testid="chevron-right-icon" />,
  BookOpen: () => <div data-testid="book-open-icon" />,
  Sparkles: () => <div data-testid="sparkles-icon" />,
}))

// Mock Skeleton
vi.mock("@/components/ui/skeleton", () => ({
  Skeleton: ({ className }: MockProps) => <div data-testid="skeleton" className={className} />,
}))

// Mock Button
vi.mock("@/components/ui/button", () => ({
  Button: ({ children, onClick, disabled, ...props }: MockProps) => (
    <button onClick={onClick as () => void} disabled={disabled as boolean} {...props}>
      {children}
    </button>
  ),
}))

// Mock design-system
vi.mock("@/lib/design-system", () => ({
  springPresets: {
    snappy: { type: "spring", stiffness: 300, damping: 30 },
    fluid: { type: "spring", stiffness: 170, damping: 26 },
    bouncy: { type: "spring", stiffness: 400, damping: 10 },
  },
}))

// Mock ClickableVerse
vi.mock("@/components/quran/clickable-verse", () => ({
  ClickableVerse: ({ arabicText }: { arabicText: string }) => (
    <div data-testid="clickable-verse" lang="ar" dir="rtl">
      {arabicText}
    </div>
  ),
}))

// Mock TranslationBlock
vi.mock("@/components/quran/translation-block", () => ({
  TranslationBlock: ({ translatorDisplay, text }: { translatorDisplay: string; text: string }) => (
    <div data-testid="translation-block">
      <span data-testid="translator-name">{translatorDisplay}</span>
      <p data-testid="translation-text">{text}</p>
    </div>
  ),
}))

const mockTranslationsResponse = {
  success: true,
  surah_id: 2,
  verse_id: 255,
  surah_name: "البقرة",
  arabic_text: "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",
  translations: [
    { translator: "diyanet", translator_display: "Diyanet İşleri", text: "Allah ki..." },
    { translator: "yazir", translator_display: "Elmalılı Hamdi Yazır", text: "Allah..." },
    { translator: "ates", translator_display: "Süleyman Ateş", text: "Allah..." },
    { translator: "bulac", translator_display: "Alİ Bulaç", text: "Allah..." },
    { translator: "ozturk", translator_display: "Yaşar Nuri Öztürk", text: "Allah..." },
    { translator: "vakfi", translator_display: "Diyanet Vakfı", text: "Allah..." },
    { translator: "yildirim", translator_display: "Suat Yıldırım", text: "Allah..." },
    { translator: "yuksel", translator_display: "Edip Yüksel", text: "Allah..." },
  ],
}

import VerseDetailPage from "@/app/[locale]/quran/[surahId]/[verseId]/page"
import { toast } from "sonner"

describe("VerseDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
    mockSession.data = { user: { id: "1", name: "Test User", email: "test@example.com" } }
    mockSession.isPending = false
  })

  it("renders loading state initially", () => {
    vi.mocked(global.fetch).mockReturnValue(new Promise(() => {}) as never)

    render(<VerseDetailPage />)

    const skeletons = screen.getAllByTestId("skeleton")
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it("fetches and displays verse translations", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTranslationsResponse,
    } as Response)

    render(<VerseDetailPage />)

    await waitFor(() => {
      expect(screen.getByTestId("clickable-verse")).toBeInTheDocument()
    })

    expect(screen.getByText(mockTranslationsResponse.arabic_text)).toBeInTheDocument()
  })

  it("renders 8 translation blocks", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTranslationsResponse,
    } as Response)

    render(<VerseDetailPage />)

    await waitFor(() => {
      const blocks = screen.getAllByTestId("translation-block")
      expect(blocks).toHaveLength(8)
    })
  })

  it("renders translator names in translation blocks", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTranslationsResponse,
    } as Response)

    render(<VerseDetailPage />)

    await waitFor(() => {
      expect(screen.getByText("Diyanet İşleri")).toBeInTheDocument()
      expect(screen.getByText("Elmalılı Hamdi Yazır")).toBeInTheDocument()
      expect(screen.getByText("Süleyman Ateş")).toBeInTheDocument()
    })
  })

  it("shows breadcrumb with surah name", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTranslationsResponse,
    } as Response)

    render(<VerseDetailPage />)

    await waitFor(() => {
      expect(screen.getByTestId("breadcrumb-surah")).toBeInTheDocument()
      expect(screen.getByTestId("breadcrumb-surah")).toHaveTextContent("البقرة")
    })
  })

  it("renders previous verse button", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTranslationsResponse,
    } as Response)

    render(<VerseDetailPage />)

    await waitFor(() => {
      expect(screen.getByTestId("prev-verse-button")).toBeInTheDocument()
    })
  })

  it("renders next verse button", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTranslationsResponse,
    } as Response)

    render(<VerseDetailPage />)

    await waitFor(() => {
      expect(screen.getByTestId("next-verse-button")).toBeInTheDocument()
    })
  })

  it("redirects to sign-in when not authenticated", () => {
    mockSession.data = null
    mockSession.isPending = false

    render(<VerseDetailPage />)

    waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/sign-in")
    })
  })

  it("handles API error and redirects to surah page", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: false,
      json: async () => ({ error: "Not found" }),
    } as Response)

    render(<VerseDetailPage />)

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Failed to load verse translations")
      expect(mockReplace).toHaveBeenCalledWith("/quran/2")
    })
  })

  it("displays Arabic text section", async () => {
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => mockTranslationsResponse,
    } as Response)

    render(<VerseDetailPage />)

    await waitFor(() => {
      expect(screen.getByTestId("arabic-text")).toBeInTheDocument()
    })
  })

  it("shows no translations message when translations array is empty", async () => {
    const emptyResponse = {
      ...mockTranslationsResponse,
      translations: [],
    }

    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => emptyResponse,
    } as Response)

    render(<VerseDetailPage />)

    await waitFor(() => {
      expect(screen.getByText("Çeviri mevcut değil")).toBeInTheDocument()
    })
  })
})
