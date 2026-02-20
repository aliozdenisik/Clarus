import { render, screen } from "./test-utils"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { createElement } from "react"
import type React from "react"
import HomePage from "../app/[locale]/page"

const mockPush = vi.fn()

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}))

vi.mock("@/lib/auth-client", () => ({
  useSession: () => ({ data: null, isPending: false }),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}))

type MockProps = {
  children?: React.ReactNode
  className?: string
  [key: string]: unknown
}

vi.mock("framer-motion", () => {
  const createMotionProxy = () =>
    new Proxy(
      {},
      {
        get: (_target: object, prop: string) => {
          return ({ children, ...props }: MockProps) =>
            createElement(prop, props as Record<string, unknown>, children)
        },
      }
    )

  return {
    motion: createMotionProxy(),
    AnimatePresence: ({ children }: { children?: React.ReactNode }) => <>{children}</>,
  }
})

vi.mock("next/image", () => ({
  default: ({ alt, ...props }: MockProps) =>
    createElement("img", { alt: String(alt ?? ""), ...props }),
}))

vi.mock("@/components/ui/dot-pattern", () => ({
  DotPattern: () => null,
  RadialGradient: () => null,
}))

vi.mock("@/components/ui/luxury-quote", () => ({
  LuxuryQuote: () => <div data-testid="luxury-quote" />,
}))

vi.mock("@/components/ui/bento-grid", () => ({
  BentoGrid: ({ children, className }: MockProps) => (
    <div className={String(className)}>{children}</div>
  ),
  BentoCard: ({ name, description }: { name: string; description: string }) => (
    <article>
      <h3>{name}</h3>
      <p>{description}</p>
    </article>
  ),
}))

describe("HomePage Agents Section", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders specialist and synthesis agents", () => {
    render(<HomePage />)

    expect(screen.getByText("Multi-Agent Analysis")).toBeInTheDocument()

    expect(screen.getByText("Quran Agent")).toBeInTheDocument()
    expect(screen.getByText("Old Testament Agent")).toBeInTheDocument()
    expect(screen.getByText("New Testament Agent")).toBeInTheDocument()
    expect(screen.getByText("Apocrypha Agent")).toBeInTheDocument()
    expect(screen.getByText("Synthesis Agent")).toBeInTheDocument()

    expect(screen.getByText("Comparative Theologian")).toBeInTheDocument()
    expect(screen.getByText("5-Paragraph Essay")).toBeInTheDocument()
    expect(screen.getByText("Common Themes")).toBeInTheDocument()
    expect(screen.getByText("Key Differences")).toBeInTheDocument()
    expect(screen.getByText("Full Citations")).toBeInTheDocument()
  })

  it("applies hierarchy and readability classes in agents cards", () => {
    render(<HomePage />)

    const specialistTitle = screen.getByText("Quran Agent")
    expect(specialistTitle).toHaveClass("text-lg", "font-semibold", "tracking-tight")

    const specialistRole = screen.getByText("Quran Specialist")
    expect(specialistRole).toHaveClass("rounded-md", "text-[11px]", "uppercase")

    const specialistDescription = screen.getByText(
      "Surfaces the most relevant verses with precise Surah and Ayah citations — presenting the Quran's own words on any topic."
    )
    expect(specialistDescription).toHaveClass("text-zinc-300")

    const synthesisTitle = screen.getByText("Synthesis Agent")
    expect(synthesisTitle).toHaveClass("text-2xl", "tracking-tight")

    const synthesisRole = screen.getByText("Comparative Theologian")
    expect(synthesisRole).toHaveClass("rounded-md", "border-purple-500/30", "text-[11px]")

    const synthesisTag = screen.getByText("5-Paragraph Essay")
    expect(synthesisTag).toHaveClass("capitalize", "text-[11px]", "text-zinc-300")
    expect(synthesisTag.className).not.toContain("uppercase")

    const specialistCard = specialistTitle.parentElement?.parentElement
    expect(specialistCard).toHaveClass("border-white/[0.12]")

    const synthesisCard = synthesisTitle.parentElement?.parentElement
    expect(synthesisCard).toHaveClass("border-white/[0.12]")
  })
})
