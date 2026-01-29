"use client";

import * as HoverCard from "@radix-ui/react-hover-card";
import { SourceBadge, SourceType } from "./source-badge";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { ExternalLink } from "lucide-react";

interface CitationHoverCardProps {
  reference: string;
  verseDetail: {
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
}

const SOURCE_MAP: Record<string, SourceType> = {
  'quran_tr': 'quran',
  'bible_ot': 'old_testament',
  'bible_nt': 'new_testament',
  'bible_apocrypha': 'apocrypha'
};

export function CitationHoverCard({ reference, verseDetail, onNavigate }: CitationHoverCardProps) {
  const displaySource = SOURCE_MAP[verseDetail.source] || 'quran';

  return (
    <HoverCard.Root openDelay={200} closeDelay={100}>
      <HoverCard.Trigger asChild>
        <button
          type="button"
          aria-label={`View ${reference}`}
          className="text-[var(--color-accent-primary)] hover:text-[var(--color-accent-hover)] font-medium underline underline-offset-2 decoration-dotted hover:decoration-solid transition-all duration-200"
        >
          {reference}
        </button>
      </HoverCard.Trigger>
      <HoverCard.Portal>
        <HoverCard.Content
          side="top"
          sideOffset={5}
          align="center"
          className="z-50"
        >
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={springPresets.snappy}
              className="bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg shadow-lg p-4 max-w-sm"
            >
              {/* Header: Source badge + Reference title */}
              <div className="flex items-center gap-2 mb-2">
                <SourceBadge source={displaySource} />
                <span className="text-sm font-medium text-[var(--color-text-primary)]">
                  {reference}
                </span>
              </div>

              {/* Translation info */}
              <p className="text-xs text-[var(--color-text-secondary)] mb-3">
                {verseDetail.translation}
              </p>

              {/* Verse text */}
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed line-clamp-4 mb-3">
                {verseDetail.text}
              </p>

              {/* Open verse link */}
              <button
                type="button"
                onClick={() => onNavigate(reference)}
                className="flex items-center gap-1 text-xs text-[var(--color-accent-primary)] hover:text-[var(--color-accent-hover)] transition-colors duration-200"
              >
                <span>Open verse</span>
                <ExternalLink className="w-3 h-3" />
              </button>
            </motion.div>
          </AnimatePresence>
          <HoverCard.Arrow className="fill-[var(--color-border-subtle)]" />
        </HoverCard.Content>
      </HoverCard.Portal>
    </HoverCard.Root>
  );
}
