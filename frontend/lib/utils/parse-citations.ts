export type CitationPart = string | { type: "citation"; reference: string }

/**
 * Strips leading markdown headers and horizontal rules from paragraph content.
 * Defense against LLM output that includes ## headers despite structured paragraph data.
 *
 * Removes:
 * - Lines starting with ## or ### (markdown headers)
 * - Lines that are just --- or *** (horizontal rules)
 * - Leading/trailing whitespace after stripping
 */
export function stripMarkdownHeaders(content: string): string {
  if (!content) return ""
  return content
    .replace(/^#{1,6}\s+.*$/gm, "") // Remove full header lines
    .replace(/^-{3,}\s*$/gm, "") // Remove horizontal rules (---)
    .replace(/^\*{3,}\s*$/gm, "") // Remove alt horizontal rules (***)
    .replace(/\n{3,}/g, "\n\n") // Collapse 3+ newlines to 2
    .trim()
}

/**
 * Expands a range reference like "Neml:2-4" or "John 3:16-18" into individual verses
 * Returns single element array for non-range references
 */
export function expandRangeReference(ref: string): string[] {
  // Match pattern: "Prefix:StartVerse-EndVerse" (works for both Quran and Bible)
  // Prefix can be "SurahName" or "Book Chapter" (with spaces)
  const rangeMatch = ref.match(/^(.+):(\d+)-(\d+)$/)

  if (rangeMatch) {
    const [, prefix, startStr, endStr] = rangeMatch
    const start = parseInt(startStr, 10)
    const end = parseInt(endStr, 10)

    // Validate range
    if (start > end || start < 1) {
      return [ref] // Invalid range, return as-is
    }

    // Generate array of individual verse references
    return Array.from({ length: end - start + 1 }, (_, i) => `${prefix}:${start + i}`)
  }

  // Not a range, return as-is
  return [ref]
}

/**
 * Handles comma-separated citations with shorthand last verse
 * "Enfal:2, 9" → ["Enfal:2", "Enfal:9"]
 * "Bakara:45, 46, 47" → ["Bakara:45", "Bakara:46", "Bakara:47"]
 * "John 3:16, 17" → ["John 3:16", "John 3:17"]
 * "Bakara:4-5, 10-11" → ["Bakara:4-5", "Bakara:10-11"] (ranges preserved for later expansion)
 */
export function expandCommaReferences(citations: string[]): string[] {
  if (citations.length <= 1) return citations

  const expanded: string[] = []
  let lastPrefix = "" // Can be "SurahName" or "Book Chapter"

  for (const citation of citations) {
    const trimmed = citation.trim()

    // Check if this has a prefix (contains colon)
    if (trimmed.includes(":")) {
      expanded.push(trimmed)
      // Extract prefix for next iterations (everything before the colon)
      const colonIndex = trimmed.indexOf(":")
      lastPrefix = trimmed.substring(0, colonIndex)
    } else if (lastPrefix && /^\d+(-\d+)?$/.test(trimmed)) {
      // This is a verse number or range (e.g., "9" or "10-11"), prepend last prefix
      expanded.push(`${lastPrefix}:${trimmed}`)
    } else {
      // Unknown format, keep as-is
      expanded.push(trimmed)
    }
  }

  return expanded
}

/**
 * Normalizes double/triple brackets to single brackets
 * Defense-in-depth against LLM output drift
 */
function normalizeBrackets(content: string): string {
  let normalized = content

  // Strip double/triple brackets iteratively (max 10 iterations for safety)
  // Use a greedy approach that handles nested structures
  for (let i = 0; i < 10; i++) {
    const before = normalized

    // Replace [[ with [ and ]] with ]
    // This handles cases like [[Rev 5:1], [Rev 5:2]] correctly
    normalized = normalized.replace(/\[\[/g, "[")
    normalized = normalized.replace(/\]\]/g, "]")

    // If no change, we're done
    if (normalized === before) break
  }

  return normalized
}

/**
 * Parses text containing citations in square brackets
 * Only matches brackets containing a colon (filters out [sic], [Note], [1], etc.)
 * Does NOT output brackets as separate parts
 *
 * Examples:
 * - "text [Bakara:45] more" → ["text ", {type: 'citation', reference: 'Bakara:45'}, " more"]
 * - "text [sic] more" → ["text [sic] more"]
 * - "text [Bakara:4-5] more" → ["text ", {type: 'citation', reference: 'Bakara:4'}, ", ", {type: 'citation', reference: 'Bakara:5'}, " more"]
 */
export function parseCitations(content: string): CitationPart[] {
  if (!content) {
    return content === "" ? [""] : []
  }

  // Step 1: Normalize double/triple brackets
  const normalized = normalizeBrackets(content)

  const parts: CitationPart[] = []

  // Step 2: Tighter regex - only match [content] where content contains ':'
  // This filters out [sic], [Note], [1], etc.
  const regex = /\[([^\]]*:[^\]]*)\]/g

  let lastIndex = 0
  let match

  while ((match = regex.exec(normalized)) !== null) {
    // Add text before citation
    if (match.index > lastIndex) {
      parts.push(normalized.slice(lastIndex, match.index))
    }

    const rawReference = match[1].replace(/\s+/g, " ").trim() // Normalize internal whitespace (newlines→space) and trim

    // Check if this is a multi-citation (contains comma)
    let citations: string[]
    if (rawReference.includes(",")) {
      const split = rawReference.split(",").map((c) => c.trim())
      citations = expandCommaReferences(split)
    } else {
      citations = [rawReference]
    }

    // Expand each citation for ranges
    const allExpanded: string[] = []
    for (const citation of citations) {
      allExpanded.push(...expandRangeReference(citation))
    }

    // Add each expanded citation as separate clickable reference
    allExpanded.forEach((citation, idx) => {
      parts.push({
        type: "citation",
        reference: citation,
      })

      // Add comma separator between citations (not after last)
      if (idx < allExpanded.length - 1) {
        parts.push(", ")
      }
    })

    lastIndex = regex.lastIndex
  }

  // Add remaining text after last citation
  if (lastIndex < normalized.length) {
    parts.push(normalized.slice(lastIndex))
  }

  // If no citations were found, return the original normalized text
  if (parts.length === 0) {
    return [normalized]
  }

  return parts
}

/**
 * Second-pass parser: finds bare (unbracketed) references in remaining text parts.
 * Uses the known citations list to catch references the LLM wrote without brackets.
 * Handles whitespace variations (newlines treated as spaces for matching).
 */
export function parseBareReferences(
  parts: CitationPart[],
  knownCitations: string[]
): CitationPart[] {
  if (!knownCitations.length) return parts

  // Sort longest-first to prevent "John 1:1" matching before "1 John 1:1"
  const sorted = [...knownCitations].sort((a, b) => b.length - a.length)

  const patterns = sorted.map((citation) => {
    const escaped = citation.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
    const flexible = escaped.replace(/\s+/g, "\\s+")
    return { citation, regex: new RegExp(flexible) }
  })

  const result: CitationPart[] = []

  for (const part of parts) {
    if (typeof part !== "string") {
      result.push(part)
      continue
    }

    result.push(...splitByBareReferences(part, patterns))
  }

  return result
}

function splitByBareReferences(
  text: string,
  patterns: { citation: string; regex: RegExp }[]
): CitationPart[] {
  const parts: CitationPart[] = []
  let remaining = text

  while (remaining.length > 0) {
    let earliest: { index: number; length: number; citation: string } | null = null

    for (const { citation, regex } of patterns) {
      const match = regex.exec(remaining)
      if (match && (earliest === null || match.index < earliest.index)) {
        earliest = { index: match.index, length: match[0].length, citation }
      }
    }

    if (earliest) {
      if (earliest.index > 0) {
        parts.push(remaining.slice(0, earliest.index))
      }
      parts.push({ type: "citation", reference: earliest.citation })
      remaining = remaining.slice(earliest.index + earliest.length)
    } else {
      parts.push(remaining)
      break
    }
  }

  return parts
}
