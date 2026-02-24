"use client"

import { useId, useMemo, useState } from "react"
import { motion } from "framer-motion"
import { springPresets, tactileScale } from "@/lib/design-system"
import { cn } from "@/lib/utils"
import { useTranslations } from "next-intl"
import { UpgradeGate } from "@/components/keyword-search/upgrade-gate"

interface DerivedWordsProps {
  words: string[]
  selectedWord: string | null
  onWordSelect: (word: string | null) => void
  transliterations?: Record<string, string>
  language?: "arabic" | "hebrew" | "greek"
  lockedAfter?: number
}

export function DerivedWords({
  words,
  selectedWord,
  onWordSelect,
  transliterations,
  language = "arabic",
  lockedAfter,
}: DerivedWordsProps) {
  const t = useTranslations("KeywordSearch")
  const isHebrew = language === "hebrew"
  const isGreek = language === "greek"
  const filterInputId = useId()
  const wordsSignature = useMemo(() => words.join("\u0000"), [words])
  const [filterState, setFilterState] = useState<{ signature: string; value: string }>({
    signature: wordsSignature,
    value: "",
  })
  const filterText = filterState.signature === wordsSignature ? filterState.value : ""

  const visibleWords = useMemo(() => {
    const normalizedFilter = filterText.trim().toLowerCase()
    if (!normalizedFilter) {
      return words
    }

    return words.filter((word) => {
      const normalizedWord = word.toLowerCase()
      const transliteration = transliterations?.[word]?.toLowerCase() ?? ""
      return normalizedWord.includes(normalizedFilter) || transliteration.includes(normalizedFilter)
    })
  }, [filterText, transliterations, words])

  const unlockedWords =
    lockedAfter !== undefined ? visibleWords.slice(0, lockedAfter) : visibleWords
  const lockedWords = lockedAfter !== undefined ? visibleWords.slice(lockedAfter) : []

  return (
    <div className="space-y-5">
      {/* Section Header */}
      <div className="inline-flex items-center gap-2">
        <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">
          {t("derivedWords.title")}
        </h3>
        <span className="leading-none text-[var(--color-text-muted)]">◆</span>
      </div>

      {words.length > 12 && (
        <>
          <label htmlFor={filterInputId} className="sr-only">
            {t("derivedWords.filterLabel")}
          </label>
          <input
            id={filterInputId}
            type="search"
            value={filterText}
            onChange={(event) =>
              setFilterState({
                signature: wordsSignature,
                value: event.target.value,
              })
            }
            placeholder={t("derivedWords.filterPlaceholder")}
            aria-label={t("derivedWords.filterLabel")}
            className={cn(
              "h-10 w-full rounded-md border border-[var(--color-border-subtle)]",
              "bg-[var(--color-bg-elevated)] px-3 text-sm text-[var(--color-text-primary)]",
              "placeholder:text-[var(--color-text-muted)] focus-visible:outline-none",
              "focus-visible:ring-2 focus-visible:ring-indigo-500"
            )}
          />
        </>
      )}

      {/* Word Tags */}
      <div className="flex flex-wrap gap-2.5">
        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          whileTap={tactileScale.press}
          transition={springPresets.bouncy}
          aria-pressed={selectedWord === null}
          onClick={() => onWordSelect(null)}
          className={cn(
            "min-h-11 min-w-11 rounded-md px-3 py-2 text-sm leading-tight font-medium transition-colors",
            "focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:outline-none",
            selectedWord === null
              ? "bg-indigo-500 text-white ring-1 ring-indigo-300 ring-inset"
              : "bg-[var(--color-bg-elevated)] text-[var(--color-text-primary)] ring-1 ring-transparent ring-inset hover:bg-[var(--color-bg-elevated)]/80 hover:ring-[var(--color-border-subtle)]"
          )}
        >
          {t("derivedWords.allWords")}
        </motion.button>

        {unlockedWords.map((word, index) => (
          <motion.button
            key={word}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            whileTap={tactileScale.press}
            transition={{ ...springPresets.bouncy, delay: (index + 1) * 0.03 }}
            aria-pressed={selectedWord === word}
            onClick={() => onWordSelect(selectedWord === word ? null : word)}
            title={transliterations?.[word] ? `${word} (${transliterations[word]})` : word}
            className={cn(
              "flex flex-col items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              "min-h-11 min-w-11 justify-center leading-tight",
              "focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:outline-none",
              selectedWord === word
                ? "bg-indigo-500 text-white ring-1 ring-indigo-300 ring-inset"
                : "bg-[var(--color-bg-elevated)] text-[var(--color-text-primary)] ring-1 ring-transparent ring-inset hover:bg-[var(--color-bg-elevated)]/80 hover:ring-[var(--color-border-subtle)]"
            )}
          >
            <span
              lang={isGreek ? "el" : isHebrew ? "he" : "ar"}
              className={cn(
                isGreek
                  ? "font-greek text-base"
                  : isHebrew
                    ? "font-hebrew leading-relaxed"
                    : "font-arabic"
              )}
              dir={isGreek ? "ltr" : "rtl"}
            >
              {isGreek ? word : <bdi>{word}</bdi>}
            </span>
            {transliterations?.[word] && (
              <span className="font-sans text-[11px] text-[var(--color-text-muted)]">
                {transliterations[word]}
              </span>
            )}
          </motion.button>
        ))}

        {lockedWords.length > 0 && (
          <UpgradeGate locked>
            <div className="flex flex-wrap gap-2.5">
              {lockedWords.map((word) => (
                <div
                  key={word}
                  className={cn(
                    "flex flex-col items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium",
                    "min-h-11 min-w-11 justify-center leading-tight",
                    "bg-[var(--color-bg-elevated)] text-[var(--color-text-primary)] ring-1 ring-transparent ring-inset"
                  )}
                >
                  <span
                    lang={isGreek ? "el" : isHebrew ? "he" : "ar"}
                    className={cn(
                      isGreek
                        ? "font-greek text-base"
                        : isHebrew
                          ? "font-hebrew leading-relaxed"
                          : "font-arabic"
                    )}
                    dir={isGreek ? "ltr" : "rtl"}
                  >
                    {isGreek ? word : <bdi>{word}</bdi>}
                  </span>
                  {transliterations?.[word] && (
                    <span className="font-sans text-[11px] text-[var(--color-text-muted)]">
                      {transliterations[word]}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </UpgradeGate>
        )}
      </div>

      {visibleWords.length === 0 && (
        <p className="text-sm text-[var(--color-text-muted)]">{t("derivedWords.noMatches")}</p>
      )}
    </div>
  )
}
