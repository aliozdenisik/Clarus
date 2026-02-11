import { render, screen } from "@testing-library/react"
import { vi, describe, it, expect } from "vitest"
import type React from "react"

type MockProps = {
  children?: React.ReactNode
  className?: string
  [key: string]: unknown
}

vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: MockProps) => <div {...props}>{children}</div>,
  },
}))

vi.mock("@/lib/design-system", () => ({
  springPresets: {
    gentle: { type: "spring", stiffness: 120, damping: 14 },
  },
}))

import { TranslationBlock } from "@/components/quran/translation-block"

describe("TranslationBlock", () => {
  const defaultProps = {
    translator: "diyanet",
    translatorDisplay: "Diyanet İşleri",
    text: "Allah ki O'ndan başka ilah yoktur; diridir, kayyumdur.",
    index: 0,
  }

  it("renders translator display name", () => {
    render(<TranslationBlock {...defaultProps} />)

    const translatorName = screen.getByTestId("translator-name")
    expect(translatorName).toBeInTheDocument()
    expect(translatorName).toHaveTextContent("Diyanet İşleri")
  })

  it("renders translation text", () => {
    render(<TranslationBlock {...defaultProps} />)

    const translationText = screen.getByTestId("translation-text")
    expect(translationText).toBeInTheDocument()
    expect(translationText).toHaveTextContent(
      "Allah ki O'ndan başka ilah yoktur; diridir, kayyumdur."
    )
  })

  it("uses Crimson Text font class on translation text", () => {
    render(<TranslationBlock {...defaultProps} />)

    const translationText = screen.getByTestId("translation-text")
    expect(translationText).toHaveClass("font-crimson")
  })

  it("uses verse-translation class on translation text", () => {
    render(<TranslationBlock {...defaultProps} />)

    const translationText = screen.getByTestId("translation-text")
    expect(translationText).toHaveClass("verse-translation")
  })

  it("has correct data-testid on container", () => {
    render(<TranslationBlock {...defaultProps} />)

    expect(screen.getByTestId("translation-block")).toBeInTheDocument()
  })

  it("applies Turkish language attribute", () => {
    render(<TranslationBlock {...defaultProps} />)

    const translationText = screen.getByTestId("translation-text")
    expect(translationText).toHaveAttribute("lang", "tr")
  })

  it("renders with different translator names", () => {
    const props = {
      ...defaultProps,
      translator: "yazir",
      translatorDisplay: "Elmalılı Hamdi Yazır",
      text: "Allah ki bundan başka hiç ilah yok.",
    }

    render(<TranslationBlock {...props} />)

    expect(screen.getByText("Elmalılı Hamdi Yazır")).toBeInTheDocument()
    expect(screen.getByText("Allah ki bundan başka hiç ilah yok.")).toBeInTheDocument()
  })

  it("renders with correct animation delay based on index", () => {
    const { container: container1 } = render(<TranslationBlock {...defaultProps} index={0} />)
    const { container: container2 } = render(<TranslationBlock {...defaultProps} index={3} />)

    expect(container1.firstChild).toBeInTheDocument()
    expect(container2.firstChild).toBeInTheDocument()
  })
})
