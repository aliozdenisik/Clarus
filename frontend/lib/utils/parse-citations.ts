export type CitationPart = string | { type: 'citation'; reference: string };

/**
 * Expands a range reference like "Neml:2-4" into individual verses ["Neml:2", "Neml:3", "Neml:4"]
 * Returns single element array for non-range references
 */
function expandRangeReference(ref: string): string[] {
  // Match pattern: "SurahName:StartVerse-EndVerse" (e.g., "Neml:2-4")
  const rangeMatch = ref.match(/^(.+):(\d+)-(\d+)$/);

  if (rangeMatch) {
    const [, surah, startStr, endStr] = rangeMatch;
    const start = parseInt(startStr, 10);
    const end = parseInt(endStr, 10);

    // Validate range
    if (start > end || start < 1) {
      return [ref]; // Invalid range, return as-is
    }

    // Generate array of individual verse references
    return Array.from(
      { length: end - start + 1 },
      (_, i) => `${surah}:${start + i}`
    );
  }

  // Not a range, return as-is
  return [ref];
}

/**
 * Handles comma-separated citations with shorthand last verse
 * "Enfal:2, 9" → ["Enfal:2", "Enfal:9"]
 * "Bakara:45, 46, 47" → ["Bakara:45", "Bakara:46", "Bakara:47"]
 */
function expandCommaReferences(citations: string[]): string[] {
  if (citations.length <= 1) return citations;

  const expanded: string[] = [];
  let lastSurah = '';

  for (const citation of citations) {
    const trimmed = citation.trim();

    // Check if this has surah name (contains colon)
    if (trimmed.includes(':')) {
      expanded.push(trimmed);
      // Extract surah name for next iterations
      const colonIndex = trimmed.indexOf(':');
      lastSurah = trimmed.substring(0, colonIndex);
    } else if (lastSurah && /^\d+$/.test(trimmed)) {
      // This is just a verse number, prepend last surah
      expanded.push(`${lastSurah}:${trimmed}`);
    } else {
      // Unknown format, keep as-is
      expanded.push(trimmed);
    }
  }

  return expanded;
}

export function parseCitations(content: string): CitationPart[] {
  const parts: CitationPart[] = [];
  const regex = /\[([^\]]+)\]/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(content)) !== null) {
    // Add text before citation
    if (match.index > lastIndex) {
      parts.push(content.slice(lastIndex, match.index));
    }

    const rawReference = match[1];

    // Add opening bracket
    parts.push('[');

    // Check if this is a multi-citation (contains comma)
    let citations: string[];
    if (rawReference.includes(',')) {
      const split = rawReference.split(',').map(c => c.trim());
      citations = expandCommaReferences(split);
    } else {
      citations = [rawReference];
    }

    // Expand each citation for ranges
    const allExpanded: string[] = [];
    for (const citation of citations) {
      allExpanded.push(...expandRangeReference(citation));
    }

    // Add each expanded citation as separate clickable reference
    allExpanded.forEach((citation, idx) => {
      parts.push({
        type: 'citation',
        reference: citation
      });

      // Add comma separator between citations (not after last)
      if (idx < allExpanded.length - 1) {
        parts.push(', ');
      }
    });

    // Add closing bracket
    parts.push(']');

    lastIndex = regex.lastIndex;
  }

  // Add remaining text after last citation
  if (lastIndex < content.length) {
    parts.push(content.slice(lastIndex));
  }

  return parts;
}
