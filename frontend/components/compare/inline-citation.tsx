"use client";

import { CitationHoverCard } from "./citation-hover-card";

interface InlineCitationProps {
  reference: string;
  verseDetail?: {
    text: string;
    book_name: string;
    chapter: number;
    verse: number;
    source: string;
    translation: string;
    book_nr?: number;
    surah_id?: number;
    surah_name?: string;
    verse_id?: number;
  };
  onNavigate: (reference: string) => void;
  onClick?: () => void;  // Backward compatibility (scrollToVerse)
}

export function InlineCitation({ reference, verseDetail, onNavigate, onClick }: InlineCitationProps) {
  // If verseDetail exists, render full HoverCard with verse preview
  if (verseDetail) {
    return (
      <CitationHoverCard
        reference={reference}
        verseDetail={verseDetail}
        onNavigate={onNavigate}
      />
    );
  }

  // Fallback: render muted text (no verse data available)
  return (
    <span className="text-[var(--color-text-muted)] font-medium">
      {reference}
    </span>
  );
}
