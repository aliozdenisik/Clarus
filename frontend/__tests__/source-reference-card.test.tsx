import { render, screen } from "./test-utils"
import { describe, it, expect, vi } from "vitest"
import type React from "react"
import { SourceReferenceCard } from "@/components/compare/source-reference-card"

// Mock Framer Motion
vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
      <div {...props}>{children}</div>
    ),
  },
}))

// Mock MagicCard
vi.mock("@/components/ui/magic-card", () => ({
  MagicCard: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="magic-card" className={className}>
      {children}
    </div>
  ),
}))

// Mock design-system
vi.mock("@/lib/design-system", () => ({
  springPresets: {
    snappy: { type: "spring", stiffness: 300, damping: 30 },
  },
}))

describe("SourceReferenceCard", () => {
  const mockVerse = {
    text: "In the beginning God created the heaven and the earth.",
    book_name: "Genesis",
    chapter: 1,
    verse: 1,
    source: "bible_ot", // Backend format
    translation: "King James Version with Apocrypha",
    book_nr: 1,
  }

  describe("Content Display", () => {
    it("renders verse text", () => {
      render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />)
      expect(screen.getByText(/In the beginning/)).toBeInTheDocument()
    })

    it("renders source badge with mapped value", () => {
      render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />)
      expect(screen.getByText("Old Testament")).toBeInTheDocument()
    })

    it("renders book name and verse reference", () => {
      render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />)
      expect(screen.getByText("Genesis 1:1")).toBeInTheDocument()
    })

    it("renders translation info", () => {
      render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />)
      expect(screen.getByText("King James Version with Apocrypha")).toBeInTheDocument()
    })

    it("renders MagicCard wrapper", () => {
      render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />)
      expect(screen.getByTestId("magic-card")).toBeInTheDocument()
    })
  })

  describe("Highlighting", () => {
    it("has data-verse-id for scroll targeting", () => {
      render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" />)
      expect(screen.getByTestId("verse-card")).toHaveAttribute("data-verse-id", "Genesis 1:1")
    })

    it("shows highlight ring when isHighlighted is true", () => {
      render(<SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" isHighlighted={true} />)
      const card = screen.getByTestId("verse-card")
      expect(card.className).toContain("ring-2")
      expect(card.className).toContain("shadow-lg")
    })

    it("does not show highlight ring when isHighlighted is false", () => {
      render(
        <SourceReferenceCard verse={mockVerse} reference="Genesis 1:1" isHighlighted={false} />
      )
      const card = screen.getByTestId("verse-card")
      expect(card.className).not.toContain("ring-2")
    })
  })

  describe("Source Mapping", () => {
    it("maps quran_tr source to quran badge", () => {
      const quranVerse = { ...mockVerse, source: "quran_tr", book_name: "Bakara" }
      render(<SourceReferenceCard verse={quranVerse} reference="Bakara:153" />)
      expect(screen.getByText("Quran")).toBeInTheDocument()
    })

    it("maps bible_nt source to new_testament badge", () => {
      const ntVerse = { ...mockVerse, source: "bible_nt", book_name: "John", book_nr: 43 }
      render(<SourceReferenceCard verse={ntVerse} reference="John 3:16" />)
      expect(screen.getByText("New Testament")).toBeInTheDocument()
    })

    it("maps bible_apocrypha source to apocrypha badge", () => {
      const apocryphaVerse = {
        ...mockVerse,
        source: "bible_apocrypha",
        book_name: "Wisdom",
        book_nr: 70,
      }
      render(<SourceReferenceCard verse={apocryphaVerse} reference="Wisdom 1:1" />)
      expect(screen.getByText("Apocrypha")).toBeInTheDocument()
    })
  })

  describe("URL Building - Quran", () => {
    it("builds correct URL for Quran verses", () => {
      const quranVerse = {
        text: "Test verse content",
        book_name: "Al-Baqarah",
        chapter: 2,
        verse: 153,
        source: "quran_tr",
        translation: "Turkish",
      }

      render(<SourceReferenceCard verse={quranVerse} reference="2:153" />)

      const link = screen.getByRole("link", { name: /go to verse/i })
      expect(link).toHaveAttribute("href", "/quran/2?verse=153")
      expect(link).toHaveAttribute("target", "_blank")
      expect(link).toHaveAttribute("rel", "noopener noreferrer")
    })

    it("has aria-label on Quran navigation link", () => {
      const quranVerse = {
        text: "Test verse",
        book_name: "Al-Baqarah",
        chapter: 2,
        verse: 153,
        source: "quran_tr",
        translation: "Turkish",
      }

      render(<SourceReferenceCard verse={quranVerse} reference="2:153" />)
      expect(screen.getByLabelText("Go to verse")).toBeInTheDocument()
    })
  })

  describe("URL Building - Bible Old Testament", () => {
    it("builds correct URL for Bible OT verses with book_nr", () => {
      const otVerse = {
        text: "Test verse content",
        book_name: "Proverbs",
        chapter: 4,
        verse: 18,
        source: "bible_ot",
        translation: "KJVA",
        book_nr: 20,
      }

      render(<SourceReferenceCard verse={otVerse} reference="Proverbs 4:18" />)

      const link = screen.getByRole("link", { name: /go to verse/i })
      expect(link).toHaveAttribute("href", "/bible/20?chapter=4&verse=18")
      expect(link).toHaveAttribute("target", "_blank")
    })

    it("shows non-clickable icon when Bible OT verse has no book_nr", () => {
      const otVerse = {
        text: "Test verse",
        book_name: "Proverbs",
        chapter: 4,
        verse: 18,
        source: "bible_ot",
        translation: "KJVA",
        // book_nr is missing
      }

      render(<SourceReferenceCard verse={otVerse} reference="Proverbs 4:18" />)
      expect(screen.queryByRole("link", { name: /go to verse/i })).not.toBeInTheDocument()
    })
  })

  describe("URL Building - Bible New Testament", () => {
    it("builds correct URL for Bible NT verses with book_nr", () => {
      const ntVerse = {
        text: "For God so loved the world",
        book_name: "John",
        chapter: 3,
        verse: 16,
        source: "bible_nt",
        translation: "KJVA",
        book_nr: 43,
      }

      render(<SourceReferenceCard verse={ntVerse} reference="John 3:16" />)

      const link = screen.getByRole("link", { name: /go to verse/i })
      expect(link).toHaveAttribute("href", "/bible/43?chapter=3&verse=16")
    })

    it("shows non-clickable icon when Bible NT verse has no book_nr", () => {
      const ntVerse = {
        text: "Test verse",
        book_name: "John",
        chapter: 3,
        verse: 16,
        source: "bible_nt",
        translation: "KJVA",
      }

      render(<SourceReferenceCard verse={ntVerse} reference="John 3:16" />)
      expect(screen.queryByRole("link", { name: /go to verse/i })).not.toBeInTheDocument()
    })
  })

  describe("URL Building - Bible Apocrypha", () => {
    it("builds correct URL for Bible Apocrypha verses with book_nr", () => {
      const apocryphaVerse = {
        text: "Test apocrypha verse",
        book_name: "Wisdom",
        chapter: 1,
        verse: 1,
        source: "bible_apocrypha",
        translation: "KJVA",
        book_nr: 70,
      }

      render(<SourceReferenceCard verse={apocryphaVerse} reference="Wisdom 1:1" />)

      const link = screen.getByRole("link", { name: /go to verse/i })
      expect(link).toHaveAttribute("href", "/bible/70?chapter=1&verse=1")
    })

    it("shows non-clickable icon when Bible Apocrypha verse has no book_nr", () => {
      const apocryphaVerse = {
        text: "Test verse",
        book_name: "Wisdom",
        chapter: 1,
        verse: 1,
        source: "bible_apocrypha",
        translation: "KJVA",
      }

      render(<SourceReferenceCard verse={apocryphaVerse} reference="Wisdom 1:1" />)
      expect(screen.queryByRole("link", { name: /go to verse/i })).not.toBeInTheDocument()
    })
  })

  describe("Accessibility", () => {
    it("has proper focus styles on link", () => {
      const verse = {
        text: "Test verse",
        book_name: "Al-Baqarah",
        chapter: 2,
        verse: 153,
        source: "quran_tr",
        translation: "Turkish",
      }

      render(<SourceReferenceCard verse={verse} reference="2:153" />)
      const link = screen.getByRole("link", { name: /go to verse/i })

      expect(link.className).toContain("focus:outline-none")
      expect(link.className).toContain("focus:ring-2")
    })
  })

  describe("Edge Cases", () => {
    it("handles book_nr of 0 (should still build URL)", () => {
      const verse = {
        text: "Test verse",
        book_name: "Genesis",
        chapter: 1,
        verse: 1,
        source: "bible_ot",
        translation: "KJVA",
        book_nr: 0,
      }

      render(<SourceReferenceCard verse={verse} reference="Genesis 1:1" />)

      // book_nr: 0 is falsy but should still work (0 !== undefined)
      const link = screen.getByRole("link", { name: /go to verse/i })
      expect(link).toHaveAttribute("href", "/bible/0?chapter=1&verse=1")
    })

    it("handles unknown source gracefully", () => {
      const verse = {
        text: "Test verse",
        book_name: "Unknown",
        chapter: 1,
        verse: 1,
        source: "unknown_source",
        translation: "Unknown",
      }

      render(<SourceReferenceCard verse={verse} reference="Unknown 1:1" />)

      // Should not crash, should show non-clickable icon
      expect(screen.queryByRole("link", { name: /go to verse/i })).not.toBeInTheDocument()
    })

    it("handles very long verse text", () => {
      const longText = "A".repeat(1000)
      const verse = {
        text: longText,
        book_name: "Al-Baqarah",
        chapter: 2,
        verse: 153,
        source: "quran_tr",
        translation: "Turkish",
      }

      render(<SourceReferenceCard verse={verse} reference="2:153" />)
      expect(screen.getByText(longText)).toBeInTheDocument()
    })
  })
})
