"use client";

import React, { useMemo } from "react";
import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { GlowCard } from "@/components/ui/glow-card";
import { Skeleton } from "@/components/ui/skeleton";
import { ExternalLink } from "lucide-react";
import { stripArabicDiacritics } from "@/lib/utils/arabic";
import { stripHebrewDiacritics } from "@/lib/utils/hebrew";
import { stripGreekDiacritics } from "@/lib/utils/greek";

interface VerseCardProps {
  surahId: number;
  surahName: string;
  ayahNumber: number;
  textUthmani: string;      // Full Uthmani verse text (display) OR Hebrew text
  textClean: string;        // Normalized clean text (for matching)
  matchedWords: string[];   // Matched word forms (from API)
  turkishTranslation?: string;  // Optional — may still be loading (Quran only)
  englishTranslation?: string | null;  // Optional — English translation (Bible only)
  isTranslationLoading?: boolean;
  index?: number;           // For stagger animation
  language?: "arabic" | "hebrew" | "greek";  // Language of the text
  chapter?: number;         // Chapter number (Bible only)
}

/**
 * Highlights matched words in text using word-index-based matching.
 * CRITICAL: Do NOT use regex on RTL text. Use word-index matching ONLY.
 * 
 * Algorithm:
 * 1. Split both display and clean (normalized) texts into words
 * 2. Create a Set of matched words for O(1) lookup
 * 3. Map clean words to display words by index
 * 4. Highlight display word if corresponding clean word is in match set
 */
function highlightText(
  textDisplay: string,
  textClean: string,
  matchedWords: string[],
  language: "arabic" | "hebrew" | "greek"
): React.ReactNode[] {
  if (!matchedWords || matchedWords.length === 0) {
    return [textDisplay];
  }

  const stripFn = language === "arabic" 
    ? stripArabicDiacritics 
    : language === "hebrew" 
    ? stripHebrewDiacritics 
    : stripGreekDiacritics;

  // Split both texts into words
  const displayWords = textDisplay.split(/\s+/);
  const cleanWords = textClean.split(/\s+/);

  // Create a set of matched words normalized for O(1) lookup
  const matchSet = new Set(matchedWords.map(w => stripFn(w.trim())));

  const wordOccurrences = new Map<string, number>();

  // Map clean words to display words by index, comparing normalized forms
  return displayWords.map((displayWord, i) => {
    const cleanWord = cleanWords[i] || '';
    const isMatch = matchSet.has(stripFn(cleanWord));
    const normalizedWord = stripFn(cleanWord || displayWord);
    const occurrence = (wordOccurrences.get(normalizedWord) ?? 0) + 1;
    wordOccurrences.set(normalizedWord, occurrence);
    const wordKey = `${normalizedWord}-${occurrence}`;

    if (isMatch) {
      return (
        <mark
          key={wordKey}
          className="bg-indigo-500/20 text-indigo-300 rounded px-0.5 mx-0.5"
        >
          {displayWord}
        </mark>
      );
    }
    return <span key={wordKey}>{i > 0 ? ' ' : ''}{displayWord}</span>;
  });
}

export const VerseCard = React.memo(function VerseCard({
  surahId,
  surahName,
  ayahNumber,
  textUthmani,
  textClean,
  matchedWords,
  turkishTranslation,
  englishTranslation,
  isTranslationLoading = false,
  index = 0,
  language = "arabic",
  chapter,
}: VerseCardProps) {
  const highlightedText = useMemo(
    () => highlightText(textUthmani, textClean, matchedWords, language),
    [textUthmani, textClean, matchedWords, language]
  );
  const isHebrew = language === "hebrew";
  const isGreek = language === "greek";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...springPresets.snappy, delay: index * 0.05 }}
    >
      <GlowCard className="border-l-2 border-l-indigo-500">
        {/* Header: Book/Surah name + Chapter:Verse */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-[var(--color-text-muted)]">
            {(isHebrew || isGreek) && chapter ? `${surahName} ${chapter}:${ayahNumber}` : `${surahName} : ${ayahNumber}`}
          </span>
          {language === "arabic" && (
            <a
              href={`/quran/${surahId}?verse=${ayahNumber}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--color-text-muted)] hover:text-[var(--color-accent-primary)] transition-colors"
              aria-label="Go to surah"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>

        {/* Greek Interlinear View */}
        {isGreek ? (
          <div className="space-y-4">
            {/* Greek text with highlighting */}
            <div 
              className="font-greek text-xl leading-loose mb-2"
              lang="el" 
              dir="ltr"
            >
              {highlightedText}
            </div>
            
            {/* English translation below */}
            <div className="text-base text-[var(--color-text-secondary)] leading-relaxed italic" dir="ltr">
              {englishTranslation || (
                <span className="text-[var(--color-text-muted)]">Translation not available</span>
              )}
            </div>
          </div>
        ) : (
          <>
            {/* Original text with highlighting (Arabic/Hebrew) */}
            <div 
              className={`${isHebrew ? 'font-hebrew' : 'font-arabic'} text-xl leading-loose text-right mb-4`}
              lang={isHebrew ? "he" : "ar"} 
              dir="rtl"
            >
              <bdi>{highlightedText}</bdi>
            </div>

            {/* Separator */}
            <div className="border-t border-zinc-800 my-3" />

            {/* Translation */}
            <div className="text-base text-[var(--color-text-primary)] leading-relaxed" dir="ltr">
              {isHebrew ? (
                englishTranslation ? (
                  englishTranslation
                ) : (
                  <span className="text-[var(--color-text-muted)] italic">Translation not available</span>
                )
              ) : (
                isTranslationLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                  </div>
                ) : turkishTranslation ? (
                  turkishTranslation
                ) : (
                  <span className="text-[var(--color-text-muted)] italic">Çeviri yüklenemedi</span>
                )
              )}
            </div>
          </>
        )}
      </GlowCard>
    </motion.div>
  );
});
