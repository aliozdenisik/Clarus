"use client"

import React, { useMemo } from "react"
import { MagicCard } from "@/components/ui/magic-card"
import { Skeleton } from "@/components/ui/skeleton"
import { ExternalLink } from "lucide-react"
import { stripArabicDiacritics } from "@/lib/utils/arabic"
import { stripHebrewDiacritics } from "@/lib/utils/hebrew"
import { stripGreekDiacritics } from "@/lib/utils/greek"
import { useTranslations } from "next-intl"

interface VerseCardProps {
  surahId: number
  surahName: string
  ayahNumber: number
  textUthmani: string // Full Uthmani verse text (display) OR Hebrew text
  textClean: string // Normalized clean text (for matching)
  matchedWords: string[] // Matched word forms (from API)
  turkishTranslation?: string // Optional — may still be loading (Quran only)
  englishTranslation?: string | null // Optional — English translation (Bible only)
  isTranslationLoading?: boolean
  language?: "arabic" | "hebrew" | "greek" // Language of the text
  chapter?: number // Chapter number (Bible only)
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
    return [textDisplay]
  }

  const stripFn =
    language === "arabic"
      ? stripArabicDiacritics
      : language === "hebrew"
        ? stripHebrewDiacritics
        : stripGreekDiacritics

  // Split both texts into words
  const displayWords = textDisplay.split(/\s+/)
  const cleanWords = textClean.split(/\s+/)

  // Create a set of matched words normalized for O(1) lookup
  const matchSet = new Set(matchedWords.map((w) => stripFn(w.trim())))

  const wordOccurrences = new Map<string, number>()

  // Map clean words to display words by index, comparing normalized forms
  return displayWords.map((displayWord, i) => {
    const cleanWord = cleanWords[i] || ""
    const isMatch = matchSet.has(stripFn(cleanWord))
    const normalizedWord = stripFn(cleanWord || displayWord)
    const occurrence = (wordOccurrences.get(normalizedWord) ?? 0) + 1
    wordOccurrences.set(normalizedWord, occurrence)
    const wordKey = `${normalizedWord}-${occurrence}`

    if (isMatch) {
      return (
        <mark key={wordKey} className="mx-0.5 rounded bg-indigo-500/20 px-0.5 text-indigo-300">
          {displayWord}
        </mark>
      )
    }
    return (
      <span key={wordKey}>
        {i > 0 ? " " : ""}
        {displayWord}
      </span>
    )
  })
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
  language = "arabic",
  chapter,
}: VerseCardProps) {
  const t = useTranslations("KeywordSearch")
  const tCommon = useTranslations("Common")
  const highlightedText = useMemo(
    () => highlightText(textUthmani, textClean, matchedWords, language),
    [textUthmani, textClean, matchedWords, language]
  )
  const isHebrew = language === "hebrew"
  const isGreek = language === "greek"

  return (
    <div>
      <MagicCard className="border-l-2 border-l-indigo-500 rounded-lg border border-[var(--color-border-subtle)] p-6" gradientSize={200} gradientColor="#1a1a2e" gradientFrom="#7c3aed" gradientTo="#4f46e5">
        {/* Header: Book/Surah name + Chapter:Verse */}
        <div className="mb-3 flex items-center justify-between">
          <span className="text-sm text-[var(--color-text-muted)]">
            {(isHebrew || isGreek) && chapter
              ? `${surahName} ${chapter}:${ayahNumber}`
              : `${surahName} : ${ayahNumber}`}
          </span>
          {language === "arabic" && (
            <a
              href={`/quran/${surahId}?verse=${ayahNumber}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-accent-primary)]"
              aria-label={tCommon("read")}
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          )}
        </div>

        {/* Greek Interlinear View */}
        {isGreek ? (
          <div className="space-y-4">
            {/* Greek text with highlighting */}
            <div className="font-greek mb-2 text-xl leading-loose" lang="el" dir="ltr">
              {highlightedText}
            </div>

            {/* English translation below */}
            <div
              className="text-base leading-relaxed text-[var(--color-text-secondary)] italic"
              dir="ltr"
            >
              {englishTranslation || (
                <span className="text-[var(--color-text-muted)]">
                  {t("translationNotAvailable")}
                </span>
              )}
            </div>
          </div>
        ) : (
          <>
            {/* Original text with highlighting (Arabic/Hebrew) */}
            <div
              className={`${isHebrew ? "font-hebrew" : "font-arabic"} mb-4 text-right text-xl leading-loose`}
              lang={isHebrew ? "he" : "ar"}
              dir="rtl"
            >
              <bdi>{highlightedText}</bdi>
            </div>

            {/* Separator */}
            <div className="my-3 border-t border-zinc-800" />

            {/* Translation */}
            <div className="text-base leading-relaxed text-[var(--color-text-primary)]" dir="ltr">
              {isHebrew ? (
                englishTranslation ? (
                  englishTranslation
                ) : (
                  <span className="text-[var(--color-text-muted)] italic">
                    {t("translationNotAvailable")}
                  </span>
                )
              ) : isTranslationLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                </div>
              ) : turkishTranslation ? (
                turkishTranslation
              ) : (
                <span className="text-[var(--color-text-muted)] italic">
                  {t("translationNotAvailable")}
                </span>
              )}
            </div>
          </>
        )}
      </MagicCard>
    </div>
  )
})
