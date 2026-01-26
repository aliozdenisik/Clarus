"use client";

import { GlowCard } from "@/components/ui/glow-card";
import { SourceBadge, SourceType } from "./source-badge";
import { ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";

interface VerseDetail {
  text: string;
  book_name: string;
  chapter: number;
  verse: number;
  source: string;
  translation: string;
}

interface SourceReferenceCardProps {
  verse: VerseDetail;
  reference: string;
  isHighlighted?: boolean;
  index?: number;
}

const SOURCE_MAP: Record<string, SourceType> = {
  'quran_tr': 'quran',
  'bible_ot': 'old_testament',
  'bible_nt': 'new_testament',
  'bible_apocrypha': 'apocrypha'
};

export function SourceReferenceCard({ verse, reference, isHighlighted, index = 0 }: SourceReferenceCardProps) {
  const displaySource = SOURCE_MAP[verse.source] || 'quran';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...springPresets.snappy, delay: index * 0.05 }}
      data-verse-id={reference}
      data-testid="verse-card"
      className={cn(
        isHighlighted && "ring-2 ring-[var(--color-accent-primary)] shadow-lg shadow-[var(--color-accent-primary)]/20"
      )}
    >
      <GlowCard 
        className="motion-safe:transition-all motion-safe:duration-500"
      >
        {/* Header row */}
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            <SourceBadge source={displaySource} />
            <span className="text-sm font-medium text-[var(--color-text-primary)]">
              {reference}
            </span>
          </div>
          <ExternalLink className="w-4 h-4 text-[var(--color-text-muted)]" />
        </div>
        
        {/* Translation info */}
        <p className="text-xs text-[var(--color-text-secondary)] mb-3">
          {verse.translation}
        </p>
        
        {/* Verse text */}
        <p className="text-sm text-[var(--color-text-primary)] leading-relaxed">
          {verse.text}
        </p>
      </GlowCard>
    </motion.div>
  );
}
