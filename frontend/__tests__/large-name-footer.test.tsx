import { render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

const mockPathname = vi.fn()

vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname(),
}))

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string, values?: { year: number }) => {
    if (key === "copyright") {
      return `copyright-${values?.year}`
    }

    return key
  },
}))

vi.mock("next/image", () => ({
  default: () => null,
}))

import { Footer } from "@/components/ui/large-name-footer"

describe("Footer", () => {
  beforeEach(() => {
    mockPathname.mockReset()
  })

  it("does not render on sign-in page", () => {
    mockPathname.mockReturnValue("/en/sign-in")

    const { container } = render(<Footer />)

    expect(container.firstChild).toBeNull()
  })

  it("does not render on sign-up page", () => {
    mockPathname.mockReturnValue("/tr/sign-up")

    const { container } = render(<Footer />)

    expect(container.firstChild).toBeNull()
  })

  it("renders on non-auth routes", () => {
    mockPathname.mockReturnValue("/en/search")

    render(<Footer />)

    expect(screen.getByText("Clarus")).toBeInTheDocument()
    expect(screen.getByText("pages")).toBeInTheDocument()
  })
})
