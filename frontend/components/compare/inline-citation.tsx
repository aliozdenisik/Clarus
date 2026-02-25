"use client"

import { CitationHoverCard } from "./citation-hover-card"
import { buildUrlFromReference } from "@/lib/utils/verse-url"
import { localizeBibleReference } from "@/lib/utils/bible-book-names"
import { useLocale } from "next-intl"

interface InlineCitationProps {
  reference: string
  verseDetail?: {
    text: string
    book_name?: string
    chapter?: number
    verse?: number
    source: string
    translation?: string
    book_nr?: number
    surah_id?: number
    surah_name?: string
    verse_id?: number
  }
  onNavigate: (reference: string) => void
}

export function InlineCitation({ reference, verseDetail, onNavigate }: InlineCitationProps) {
  const locale = useLocale()
  const displayReference = localizeBibleReference(reference, locale)

  // If verseDetail exists, render full HoverCard with verse preview
  if (verseDetail) {
    return (
      <CitationHoverCard
        reference={reference}
        displayReference={displayReference}
        verseDetail={verseDetail}
        onNavigate={onNavigate}
      />
    )
  }

  // Fallback: parse reference string to build verse page URL directly
  const handleClick = () => {
    const url = buildUrlFromReference(reference)
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer")
    }
  }

  return (
    <button
      type="button"
      aria-label={`View ${displayReference}`}
      onClick={handleClick}
      className="font-medium text-[var(--color-accent-primary)] underline decoration-dotted underline-offset-2 transition-all duration-200 hover:text-[var(--color-accent-hover)] hover:decoration-solid"
    >
      {displayReference}
    </button>
  )
}
