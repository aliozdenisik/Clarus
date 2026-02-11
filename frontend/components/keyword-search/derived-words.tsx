"use client"

import { motion } from "framer-motion"
import { springPresets, tactileScale } from "@/lib/design-system"
import { cn } from "@/lib/utils"

interface DerivedWordsProps {
  words: string[]
  selectedWord: string | null
  onWordSelect: (word: string | null) => void
  transliterations?: Record<string, string>
  language?: "arabic" | "hebrew" | "greek"
}

export function DerivedWords({
  words,
  selectedWord,
  onWordSelect,
  transliterations,
  language = "arabic",
}: DerivedWordsProps) {
  const isHebrew = language === "hebrew"
  const isGreek = language === "greek"

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center gap-3">
        <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">Derived Words</h3>
        <span className="text-[var(--color-text-muted)]">◆</span>
      </div>

      {/* Word Tags */}
      <div className="flex flex-wrap gap-2">
        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          whileTap={tactileScale.press}
          transition={springPresets.bouncy}
          onClick={() => onWordSelect(null)}
          className={cn(
            "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
            selectedWord === null
              ? "bg-indigo-500 text-white"
              : "bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)]/80"
          )}
        >
          All Words
        </motion.button>

        {words.map((word, index) => (
          <motion.button
            key={word}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            whileTap={tactileScale.press}
            transition={{ ...springPresets.bouncy, delay: (index + 1) * 0.03 }}
            onClick={() => onWordSelect(selectedWord === word ? null : word)}
            className={cn(
              "flex flex-col items-center gap-0.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              selectedWord === word
                ? "bg-indigo-500 text-white"
                : "bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)]/80"
            )}
          >
            <span
              lang={isGreek ? "el" : isHebrew ? "he" : "ar"}
              className={isGreek ? "font-greek" : isHebrew ? "font-hebrew" : "font-arabic"}
              dir={isGreek ? "ltr" : "rtl"}
            >
              {isGreek ? word : <bdi>{word}</bdi>}
            </span>
            {transliterations?.[word] && (
              <span className="font-sans text-[10px] opacity-70">{transliterations[word]}</span>
            )}
          </motion.button>
        ))}
      </div>
    </div>
  )
}
