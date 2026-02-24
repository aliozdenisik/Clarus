import { describe, it, expect } from "vitest"
import {
  getDailyVerse,
  CURATED_VERSES,
  CURATED_VERSES_EN,
  CURATED_VERSES_TR,
} from "@/lib/daily-verse"

describe("getDailyVerse", () => {
  it("returns a valid DailyVerse object with all required fields", () => {
    const verse = getDailyVerse("en", new Date("2025-01-01"))
    expect(verse).toHaveProperty("text")
    expect(verse).toHaveProperty("reference")
    expect(verse).toHaveProperty("surahNumber")
    expect(verse).toHaveProperty("ayahNumber")
    expect(typeof verse.text).toBe("string")
    expect(typeof verse.reference).toBe("string")
    expect(typeof verse.surahNumber).toBe("number")
    expect(typeof verse.ayahNumber).toBe("number")
    expect(verse.text.length).toBeGreaterThan(0)
    expect(verse.reference.length).toBeGreaterThan(0)
  })

  it("is deterministic: same date always returns the same verse", () => {
    const date = new Date("2025-06-15")
    const verseA = getDailyVerse("en", date)
    const verseB = getDailyVerse("en", date)
    expect(verseA.reference).toBe(verseB.reference)
    expect(verseA.text).toBe(verseB.text)
  })

  it("different dates produce different verses (>20 unique out of 90 days)", () => {
    const uniqueRefs = new Set<string>()
    const start = new Date("2025-01-01")
    for (let day = 0; day < 90; day++) {
      const date = new Date(start)
      date.setUTCDate(start.getUTCDate() + day)
      uniqueRefs.add(getDailyVerse("en", date).reference)
    }
    expect(uniqueRefs.size).toBeGreaterThan(20)
  })

  it("default (no locale argument) returns a verse from the English curated list", () => {
    const verse = getDailyVerse()
    const allRefs = CURATED_VERSES.map((v) => v.reference)
    expect(allRefs).toContain(verse.reference)
  })

  it("returns English verses for locale 'en'", () => {
    const verse = getDailyVerse("en", new Date("2025-03-15"))
    const allRefs = CURATED_VERSES_EN.map((v) => v.reference)
    expect(allRefs).toContain(verse.reference)
  })

  it("returns Turkish verses for locale 'tr'", () => {
    const verse = getDailyVerse("tr", new Date("2025-03-15"))
    const allRefs = CURATED_VERSES_TR.map((v) => v.reference)
    expect(allRefs).toContain(verse.reference)
  })

  it("English and Turkish collections have different verse texts", () => {
    const enTexts = new Set(CURATED_VERSES_EN.map((v) => v.text))
    const trTexts = new Set(CURATED_VERSES_TR.map((v) => v.text))
    // No overlap between the two language sets
    for (const text of enTexts) {
      expect(trTexts.has(text)).toBe(false)
    }
  })
})
