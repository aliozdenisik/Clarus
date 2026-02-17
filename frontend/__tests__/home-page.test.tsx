import { createElement } from "react"
import type React from "react"
import { describe, expect, it, vi } from "vitest"
import { render, screen } from "./test-utils"
import HomePage from "../app/[locale]/page"

type MockProps = {
  children?: React.ReactNode
  className?: string
  [key: string]: unknown
}

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock("@/lib/auth-client", () => ({
  useSession: () => ({
    data: { user: { id: "1", name: "Test User", email: "test@example.com" } },
    isPending: false,
  }),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}))

vi.mock("framer-motion", () => {
  const createMotionProxy = () =>
    new Proxy(
      {},
      {
        get: (_target: object, prop: string) => {
          return ({ children, ...props }: MockProps) => {
            const domProps: Record<string, unknown> = { ...props }
            delete domProps.initial
            delete domProps.animate
            delete domProps.whileInView
            delete domProps.whileHover
            delete domProps.whileTap
            delete domProps.viewport
            delete domProps.transition
            delete domProps.exit
            return createElement(prop, domProps, children)
          }
        },
      }
    )

  return {
    motion: createMotionProxy(),
  }
})

vi.mock("next/image", () => ({
  default: ({ alt }: { alt: string }) => <div role="img" aria-label={alt} />,
}))

vi.mock("@/components/ui/dot-pattern", () => ({
  DotPattern: () => null,
  RadialGradient: () => null,
}))

vi.mock("@/components/ui/text-rotate", () => ({
  LuxuryQuote: ({
    quotes,
    className,
  }: {
    quotes?: Array<{ text: string }>
    className?: string
  }) => <div className={className}>{quotes?.[0]?.text}</div>,
}))

vi.mock("@/components/ui/bento-grid", () => ({
  BentoGrid: ({ children, className }: MockProps) => <div className={className}>{children}</div>,
  BentoCard: ({
    name,
    description,
    Icon,
  }: {
    name?: React.ReactNode
    description?: React.ReactNode
    Icon?: React.ComponentType<{ className?: string }>
  }) => (
    <article>
      {Icon ? <Icon /> : null}
      <h3>{String(name ?? "")}</h3>
      <p>{String(description ?? "")}</p>
    </article>
  ),
}))

vi.mock("lucide-react", () => {
  const Icon = () => <svg aria-hidden="true" data-testid="icon" />
  return {
    Search: Icon,
    Sparkles: Icon,
    GitCompare: Icon,
    BookOpen: Icon,
    ArrowRight: Icon,
    Brain: Icon,
    Layers: Icon,
    ScrollText: Icon,
    BookMarked: Icon,
    Library: Icon,
  }
})

describe("HomePage", () => {
  it("renders How It Works section with all steps", () => {
    render(<HomePage />)

    expect(screen.getByRole("heading", { name: "How It Works", level: 2 })).toBeInTheDocument()

    expect(screen.getByRole("heading", { name: "Ask", level: 3 })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Enrich", level: 3 })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Discover", level: 3 })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Understand", level: 3 })).toBeInTheDocument()

    expect(screen.getByText("Pose your question")).toBeInTheDocument()
    expect(screen.getByText("Context is deepened")).toBeInTheDocument()
    expect(screen.getByText("All scriptures searched")).toBeInTheDocument()
    expect(screen.getByText("Perspectives unite")).toBeInTheDocument()
  })

  it("applies responsive step grid and displays numbered badges", () => {
    render(<HomePage />)

    const grid = screen.getByTestId("how-it-works-grid")
    expect(grid).toHaveClass("grid-cols-1")
    expect(grid).toHaveClass("sm:grid-cols-2")
    expect(grid).toHaveClass("xl:grid-cols-4")

    const cards = screen.getAllByTestId(/how-it-works-step-/)
    expect(cards).toHaveLength(4)

    expect(screen.getByText(/^01$/)).toBeInTheDocument()
    expect(screen.getByText(/^02$/)).toBeInTheDocument()
    expect(screen.getByText(/^03$/)).toBeInTheDocument()
    expect(screen.getByText(/^04$/)).toBeInTheDocument()

    expect(screen.getAllByText("43,055 verses indexed").length).toBeGreaterThan(0)
  })
})
