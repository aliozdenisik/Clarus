import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, it, expect, vi } from "vitest"
import { InlineCitation } from "@/components/compare/inline-citation"

vi.mock("next-intl", () => ({
  useLocale: () => "en",
}))

const mockVerseDetail = {
  text: "In the beginning God created the heaven and the earth.",
  book_name: "Genesis",
  chapter: 1,
  verse: 1,
  source: "bible_ot",
  translation: "King James Version with Apocrypha",
  book_nr: 1,
}

describe("InlineCitation", () => {
  describe("with verseDetail (HoverCard mode)", () => {
    it("renders as button element", () => {
      render(
        <InlineCitation
          reference="Genesis 1:1"
          verseDetail={mockVerseDetail}
          onNavigate={vi.fn()}
        />
      )
      expect(screen.getByRole("button")).toBeInTheDocument()
    })

    it("displays reference text without brackets", () => {
      render(
        <InlineCitation
          reference="Genesis 1:1"
          verseDetail={mockVerseDetail}
          onNavigate={vi.fn()}
        />
      )
      expect(screen.getByText("Genesis 1:1")).toBeInTheDocument()
    })

    it("has accessible aria-label", () => {
      render(
        <InlineCitation
          reference="Genesis 1:1"
          verseDetail={mockVerseDetail}
          onNavigate={vi.fn()}
        />
      )
      expect(screen.getByRole("button")).toHaveAttribute("aria-label", "View Genesis 1:1")
    })

    it("renders HoverCard trigger button", () => {
      const handleNavigate = vi.fn()
      render(
        <InlineCitation
          reference="Genesis 1:1"
          verseDetail={mockVerseDetail}
          onNavigate={handleNavigate}
        />
      )

      // Verify trigger button exists
      const button = screen.getByRole("button")
      expect(button).toBeInTheDocument()
      expect(button).toHaveTextContent("Genesis 1:1")
    })

    it("handles Quran citation format", () => {
      const quranVerse = {
        text: "الحمد لله رب العالمين",
        book_name: "Fatiha",
        chapter: 1,
        verse: 2,
        source: "quran_tr",
        translation: "Diyanet İşleri Başkanlığı Meali",
        surah_id: 1,
        verse_id: 2,
      }

      render(
        <InlineCitation reference="Bakara:153" verseDetail={quranVerse} onNavigate={vi.fn()} />
      )
      expect(screen.getByText("Bakara:153")).toBeInTheDocument()
      expect(screen.getByRole("button")).toHaveAttribute("aria-label", "View Bakara:153")
    })
  })

  describe("without verseDetail (fallback mode)", () => {
    it("renders as clickable button with accent style", () => {
      render(<InlineCitation reference="Genesis 1:1" onNavigate={vi.fn()} />)

      const element = screen.getByRole("button")
      expect(element).toHaveTextContent("Genesis 1:1")
      expect(element).toHaveAttribute("aria-label", "View Genesis 1:1")
    })

    it("opens Bible verse page in new tab for Bible reference", async () => {
      const openSpy = vi.spyOn(window, "open").mockImplementation(() => null)
      render(<InlineCitation reference="1 Corinthians 15:46" onNavigate={vi.fn()} />)

      await userEvent.click(screen.getByRole("button"))
      expect(openSpy).toHaveBeenCalledWith(
        "/bible/46?chapter=15&verse=46",
        "_blank",
        "noopener,noreferrer"
      )
      openSpy.mockRestore()
    })

    it("opens Quran verse page in new tab for Quran reference", async () => {
      const openSpy = vi.spyOn(window, "open").mockImplementation(() => null)
      render(<InlineCitation reference="Bakara:153" onNavigate={vi.fn()} />)

      await userEvent.click(screen.getByRole("button"))
      expect(openSpy).toHaveBeenCalledWith("/quran/2/153", "_blank", "noopener,noreferrer")
      openSpy.mockRestore()
    })
  })
})
