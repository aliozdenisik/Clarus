import { render, screen } from "../test-utils"
import { vi, describe, it, expect } from "vitest"
import type React from "react"

vi.mock("@/components/ui/magic-card", () => ({
  MagicCard: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div className={className}>{children}</div>
  ),
}))

vi.mock("@/components/ui/number-ticker", () => ({
  NumberTicker: ({ value }: { value: number }) => <span>{value}</span>,
}))

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode
    href: string
    [key: string]: unknown
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}))

import { DailyVerseWidget } from "@/components/hub/daily-verse-widget"
import type { DailyVerse } from "@/lib/daily-verse"

const TEST_VERSE: DailyVerse = {
  text: "Ey iman edenler! Sabır ve namazla yardım isteyin.",
  reference: "Bakara 2:153",
  surahNumber: 2,
  ayahNumber: 153,
}

describe("DailyVerseWidget", () => {
  it("renders verse text", () => {
    render(<DailyVerseWidget verse={TEST_VERSE} />)
    expect(screen.getByText(TEST_VERSE.text)).toBeInTheDocument()
  })

  it("renders verse reference (prefix portion)", () => {
    render(<DailyVerseWidget verse={TEST_VERSE} />)
    expect(screen.getByText("Bakara 2:")).toBeInTheDocument()
  })

  it("contains a link to the verse detail page", () => {
    render(<DailyVerseWidget verse={TEST_VERSE} />)
    const link = screen.getByRole("link", { name: TEST_VERSE.reference })
    expect(link).toBeInTheDocument()
    expect(link.getAttribute("href")).toContain("2")
  })
})
