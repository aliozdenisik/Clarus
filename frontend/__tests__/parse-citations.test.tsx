import { describe, it, expect } from "vitest"
import { parseCitations, parseBareReferences, CitationPart } from "@/lib/utils/parse-citations"

/**
 * Helper function to extract citation parts from the result
 */
const getCitations = (parts: CitationPart[]) =>
  parts.filter((p) => typeof p !== "string" && p.type === "citation")

describe("parseCitations", () => {
  // ============================================================================
  // GROUP 1: Basic Parsing (5 tests)
  // ============================================================================
  describe("Group 1: Basic parsing", () => {
    it("parses single Quran citation", () => {
      const result = parseCitations("text [Bakara:45] more")
      expect(result).toHaveLength(3)
      expect(result[0]).toBe("text ")
      expect(result[1]).toEqual({ type: "citation", reference: "Bakara:45" })
      expect(result[2]).toBe(" more")
    })

    it("parses single Bible citation", () => {
      const result = parseCitations("text [John 3:16] more")
      expect(result).toHaveLength(3)
      expect(result[0]).toBe("text ")
      expect(result[1]).toEqual({ type: "citation", reference: "John 3:16" })
      expect(result[2]).toBe(" more")
    })

    it("parses multiple citations", () => {
      const result = parseCitations("[Bakara:45] and [John 3:16]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(2)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:45" })
      expect(citations[1]).toEqual({ type: "citation", reference: "John 3:16" })
    })

    it("returns plain text without citations as single string", () => {
      const result = parseCitations("plain text")
      expect(result).toEqual(["plain text"])
    })

    it("parses citation with numbered book", () => {
      const result = parseCitations("text [1 Corinthians 13:4] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "1 Corinthians 13:4" })
    })
  })

  // ============================================================================
  // GROUP 2: Range Expansion (3 tests)
  // ============================================================================
  describe("Group 2: Range expansion", () => {
    it("expands Quran range", () => {
      const result = parseCitations("[Bakara:4-5]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(2)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:4" })
      expect(citations[1]).toEqual({ type: "citation", reference: "Bakara:5" })
    })

    it("expands Bible range", () => {
      const result = parseCitations("[John 3:16-18]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(3)
      expect(citations[0]).toEqual({ type: "citation", reference: "John 3:16" })
      expect(citations[1]).toEqual({ type: "citation", reference: "John 3:17" })
      expect(citations[2]).toEqual({ type: "citation", reference: "John 3:18" })
    })

    it("returns single reference for invalid range (start > end)", () => {
      const result = parseCitations("[Bakara:5-4]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:5-4" })
    })
  })

  // ============================================================================
  // GROUP 3: Comma-Separated Citations (3 tests)
  // ============================================================================
  describe("Group 3: Comma-separated citations", () => {
    it("expands same book with shorthand", () => {
      const result = parseCitations("[Enfal:2, 9]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(2)
      expect(citations[0]).toEqual({ type: "citation", reference: "Enfal:2" })
      expect(citations[1]).toEqual({ type: "citation", reference: "Enfal:9" })
    })

    it("parses different books in comma-separated list", () => {
      const result = parseCitations("[Bakara:4, John 3:16]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(2)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:4" })
      expect(citations[1]).toEqual({ type: "citation", reference: "John 3:16" })
    })

    it("expands multiple shorthand verses", () => {
      const result = parseCitations("[Bakara:45, 46, 47]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(3)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:45" })
      expect(citations[1]).toEqual({ type: "citation", reference: "Bakara:46" })
      expect(citations[2]).toEqual({ type: "citation", reference: "Bakara:47" })
    })
  })

  // ============================================================================
  // GROUP 4: Double Bracket Normalization (3 tests)
  // ============================================================================
  describe("Group 4: Double bracket normalization", () => {
    it("normalizes double brackets", () => {
      const result = parseCitations("text [[Rev 5:1]] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Rev 5:1" })
    })

    it("normalizes triple brackets", () => {
      const result = parseCitations("text [[[John 3:16]]] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "John 3:16" })
    })

    it("normalizes double brackets with multiple citations", () => {
      const result = parseCitations("text [[Rev 5:1], [Rev 5:2]] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(2)
      expect(citations[0]).toEqual({ type: "citation", reference: "Rev 5:1" })
      expect(citations[1]).toEqual({ type: "citation", reference: "Rev 5:2" })
    })
  })

  // ============================================================================
  // GROUP 5: Non-Citation Brackets (3 tests)
  // ============================================================================
  describe("Group 5: Non-citation brackets (must NOT be parsed)", () => {
    it("does not parse [sic] as citation", () => {
      const result = parseCitations("text [sic] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(0)
      expect(result).toEqual(["text [sic] more"])
    })

    it("does not parse [Note] as citation", () => {
      const result = parseCitations("text [Note] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(0)
      expect(result).toEqual(["text [Note] more"])
    })

    it("does not parse [1] as citation (no colon)", () => {
      const result = parseCitations("text [1] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(0)
      expect(result).toEqual(["text [1] more"])
    })
  })

  // ============================================================================
  // GROUP 6: Whitespace Handling (2 tests)
  // ============================================================================
  describe("Group 6: Whitespace handling", () => {
    it("trims whitespace around citation", () => {
      const result = parseCitations("text [ Bakara:4 ] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:4" })
    })

    it("handles whitespace in comma-separated list", () => {
      const result = parseCitations("text [Bakara:4 , 5] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(2)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:4" })
      expect(citations[1]).toEqual({ type: "citation", reference: "Bakara:5" })
    })
  })

  // ============================================================================
  // GROUP 7: Edge Cases (6 tests)
  // ============================================================================
  describe("Group 7: Edge cases", () => {
    it("handles empty string", () => {
      const result = parseCitations("")
      expect(result.length).toBeGreaterThanOrEqual(0)
      // Empty string should return empty array or array with empty string
      if (result.length > 0) {
        expect(result[0]).toBe("")
      }
    })

    it("handles citation at start", () => {
      const result = parseCitations("[Bakara:1] text")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:1" })
      expect(result[result.length - 1]).toBe(" text")
    })

    it("handles citation at end", () => {
      const result = parseCitations("text [Bakara:1]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:1" })
      expect(result[0]).toBe("text ")
    })

    it("handles adjacent citations", () => {
      const result = parseCitations("[Bakara:1][John 3:16]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(2)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:1" })
      expect(citations[1]).toEqual({ type: "citation", reference: "John 3:16" })
    })

    it("handles citation with Turkish characters", () => {
      const result = parseCitations("text [Fâtiha:1] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Fâtiha:1" })
    })

    it("handles citation with period after", () => {
      const result = parseCitations("text [Bakara:1]. More")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:1" })
      // Period should be in text part, not in citation
      const textParts = result.filter((p) => typeof p === "string")
      expect(textParts.some((p) => p.includes("."))).toBe(true)
    })
  })

  // ============================================================================
  // ADDITIONAL COMPREHENSIVE TESTS
  // ============================================================================
  describe("Additional comprehensive tests", () => {
    it("handles complex multi-citation with ranges and shorthand", () => {
      const result = parseCitations("[Bakara:4-5, 10, John 3:16-18]")
      const citations = getCitations(result)
      // Bakara:4, Bakara:5, Bakara:10, John 3:16, John 3:17, John 3:18
      expect(citations.length).toBeGreaterThanOrEqual(6)
    })

    it("preserves text between citations", () => {
      const result = parseCitations("First [Bakara:1] middle [John 3:16] last")
      const textParts = result.filter((p) => typeof p === "string")
      expect(textParts.some((p) => p.includes("First"))).toBe(true)
      expect(textParts.some((p) => p.includes("middle"))).toBe(true)
      expect(textParts.some((p) => p.includes("last"))).toBe(true)
    })

    it("does not parse mixed bracket types as citations", () => {
      const result = parseCitations("text [no colon here] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(0)
    })

    it("handles citation with multiple spaces in book name", () => {
      const result = parseCitations("[1 Corinthians 13:4]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "1 Corinthians 13:4" })
    })

    it("handles Quran surah with special characters", () => {
      const result = parseCitations("[Meâric:5]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Meâric:5" })
    })

    it("handles Bible book with numbers", () => {
      const result = parseCitations("[2 Maccabees 7:9]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "2 Maccabees 7:9" })
    })

    it("does not include brackets in citation reference", () => {
      const result = parseCitations("[Bakara:45]")
      const citations = getCitations(result)
      const citation = citations[0]
      if (citation && typeof citation !== "string" && citation.type === "citation") {
        expect(citation.reference).not.toContain("[")
        expect(citation.reference).not.toContain("]")
      }
    })

    it("handles multiple non-citations mixed with citations", () => {
      const result = parseCitations("[sic] text [Bakara:1] [note] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:1" })
    })

    it("expands range with large verse numbers", () => {
      const result = parseCitations("[Bakara:280-282]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(3)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:280" })
      expect(citations[1]).toEqual({ type: "citation", reference: "Bakara:281" })
      expect(citations[2]).toEqual({ type: "citation", reference: "Bakara:282" })
    })

    it("handles comma-separated with ranges", () => {
      const result = parseCitations("[Bakara:4-5, 10-11]")
      const citations = getCitations(result)
      expect(citations).toHaveLength(4)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:4" })
      expect(citations[1]).toEqual({ type: "citation", reference: "Bakara:5" })
      expect(citations[2]).toEqual({ type: "citation", reference: "Bakara:10" })
      expect(citations[3]).toEqual({ type: "citation", reference: "Bakara:11" })
    })
  })

  // ============================================================================
  // GROUP 8: Whitespace normalization in brackets
  // ============================================================================
  describe("Group 8: Whitespace normalization in brackets", () => {
    it("normalizes newline inside brackets to space", () => {
      const result = parseCitations("text [Revelation\n4:11] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Revelation 4:11" })
    })

    it("normalizes multiple whitespace inside brackets", () => {
      const result = parseCitations("text [Hebrews  11:3] more")
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Hebrews 11:3" })
    })
  })
})

describe("parseBareReferences", () => {
  // ============================================================================
  // GROUP 1: Basic bare reference detection
  // ============================================================================
  describe("Group 1: Basic bare reference detection", () => {
    it("detects a bare Bible reference from known citations", () => {
      const parts = parseCitations("text about Revelation 4:11 here")
      const result = parseBareReferences(parts, ["Revelation 4:11"])
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Revelation 4:11" })
    })

    it("detects multiple bare references", () => {
      const parts = parseCitations("Revelation 4:11, Hebrews 1:10 are important")
      const result = parseBareReferences(parts, ["Revelation 4:11", "Hebrews 1:10"])
      const citations = getCitations(result)
      expect(citations).toHaveLength(2)
      expect(citations[0]).toEqual({ type: "citation", reference: "Revelation 4:11" })
      expect(citations[1]).toEqual({ type: "citation", reference: "Hebrews 1:10" })
    })

    it("returns parts unchanged when knownCitations is empty", () => {
      const parts: CitationPart[] = ["some text"]
      const result = parseBareReferences(parts, [])
      expect(result).toEqual(["some text"])
    })

    it("does not double-convert already bracketed citations", () => {
      const parts = parseCitations("text [Revelation 4:11] more")
      const result = parseBareReferences(parts, ["Revelation 4:11"])
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
    })
  })

  // ============================================================================
  // GROUP 2: Mixed bracketed + bare references
  // ============================================================================
  describe("Group 2: Mixed bracketed and bare references", () => {
    it("catches bare ref alongside bracketed ref", () => {
      const parts = parseCitations("text Revelation 4:11, [Hebrews 1:10] end")
      const result = parseBareReferences(parts, ["Revelation 4:11", "Hebrews 1:10"])
      const citations = getCitations(result)
      expect(citations).toHaveLength(2)
      expect(citations[0]).toEqual({ type: "citation", reference: "Revelation 4:11" })
      expect(citations[1]).toEqual({ type: "citation", reference: "Hebrews 1:10" })
    })
  })

  // ============================================================================
  // GROUP 3: Whitespace flexibility
  // ============================================================================
  describe("Group 3: Whitespace flexibility", () => {
    it("matches bare reference with newline instead of space", () => {
      const parts: CitationPart[] = ["text Revelation\n4:11 end"]
      const result = parseBareReferences(parts, ["Revelation 4:11"])
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Revelation 4:11" })
    })

    it("matches bare reference with multiple spaces", () => {
      const parts: CitationPart[] = ["text Revelation   4:11 end"]
      const result = parseBareReferences(parts, ["Revelation 4:11"])
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Revelation 4:11" })
    })
  })

  // ============================================================================
  // GROUP 4: Longest-first matching
  // ============================================================================
  describe("Group 4: Longest-first matching", () => {
    it('matches "1 John 1:1" before "John 1:1"', () => {
      const parts: CitationPart[] = ["text 1 John 1:1 end"]
      const result = parseBareReferences(parts, ["John 1:1", "1 John 1:1"])
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "1 John 1:1" })
    })
  })

  // ============================================================================
  // GROUP 5: Quran references
  // ============================================================================
  describe("Group 5: Quran bare references", () => {
    it("detects bare Quran reference", () => {
      const parts: CitationPart[] = ["text Bakara:45 end"]
      const result = parseBareReferences(parts, ["Bakara:45"])
      const citations = getCitations(result)
      expect(citations).toHaveLength(1)
      expect(citations[0]).toEqual({ type: "citation", reference: "Bakara:45" })
    })
  })

  // ============================================================================
  // GROUP 6: No false positives
  // ============================================================================
  describe("Group 6: No false positives", () => {
    it("does not match text that is not in knownCitations", () => {
      const parts: CitationPart[] = ["text Revelation 4:11 end"]
      const result = parseBareReferences(parts, ["Hebrews 1:10"])
      const citations = getCitations(result)
      expect(citations).toHaveLength(0)
      expect(result).toEqual(["text Revelation 4:11 end"])
    })
  })
})
