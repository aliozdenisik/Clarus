"use client";

import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { GlowCard } from "@/components/ui/glow-card";
import { Skeleton } from "@/components/ui/skeleton";
import { ExternalLink } from "lucide-react";
import { stripArabicDiacritics } from "@/lib/utils/arabic";

interface VerseCardProps {
  surahId: number;
  surahName: string;
  ayahNumber: number;
  textUthmani: string;      // Full Uthmani verse text (display)
  textClean: string;        // Normalized clean text (for matching)
  matchedWords: string[];   // Matched word forms (from API)
  turkishTranslation?: string;  // Optional — may still be loading
  isTranslationLoading?: boolean;
  index?: number;           // For stagger animation
}

/**
 * Highlights matched words in Arabic text using word-index-based matching.
 * CRITICAL: Do NOT use regex on Arabic text. Use word-index matching ONLY.
 * 
 * Algorithm:
 * 1. Split both Uthmani (display) and clean (normalized) texts into words
 * 2. Create a Set of matched words for O(1) lookup
 * 3. Map clean words to Uthmani words by index
 * 4. Highlight Uthmani word if corresponding clean word is in match set
 */
function highlightArabicText(
  textUthmani: string,
  textClean: string,
  matchedWords: string[]
): React.ReactNode[] {
  if (!matchedWords || matchedWords.length === 0) {
    return [textUthmani];
  }

  // Split both texts into words
  const uthmaniWords = textUthmani.split(/\s+/);
  const cleanWords = textClean.split(/\s+/);

  // Create a set of matched words normalized for O(1) lookup
  const matchSet = new Set(matchedWords.map(w => stripArabicDiacritics(w.trim())));

  // Map clean words to uthmani words by index, comparing normalized forms
  return uthmaniWords.map((uthmaniWord, i) => {
    const cleanWord = cleanWords[i] || '';
    const isMatch = matchSet.has(stripArabicDiacritics(cleanWord));

    if (isMatch) {
      return (
        <mark
          key={i}
          className="bg-indigo-500/20 text-indigo-300 rounded px-0.5 mx-0.5"
        >
          {uthmaniWord}
        </mark>
      );
    }
    return <span key={i}>{i > 0 ? ' ' : ''}{uthmaniWord}</span>;
  });
}

export function VerseCard({
  surahId,
  surahName,
  ayahNumber,
  textUthmani,
  textClean,
  matchedWords,
  turkishTranslation,
  isTranslationLoading = false,
  index = 0,
}: VerseCardProps) {
  const highlightedText = highlightArabicText(textUthmani, textClean, matchedWords);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...springPresets.snappy, delay: index * 0.05 }}
    >
      <GlowCard className="border-l-2 border-l-indigo-500">
        {/* Header: Surah name + Ayah number */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-[var(--color-text-muted)]">
            {surahName} : {ayahNumber}
          </span>
          <a
            href={`/quran/${surahId}?verse=${ayahNumber}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--color-text-muted)] hover:text-[var(--color-accent-primary)] transition-colors"
            aria-label="Go to surah"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>

        {/* Arabic text with highlighting */}
        <div className="font-arabic text-xl leading-loose text-right mb-4" lang="ar" dir="rtl">
          {highlightedText}
        </div>

        {/* Separator */}
        <div className="border-t border-zinc-800 my-3" />

        {/* Turkish translation */}
        <div className="text-base text-[var(--color-text-primary)] leading-relaxed" dir="ltr">
          {isTranslationLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ) : turkishTranslation ? (
            turkishTranslation
          ) : (
            <span className="text-[var(--color-text-muted)] italic">Çeviri yüklenemedi</span>
          )}
        </div>
      </GlowCard>
    </motion.div>
  );
}
