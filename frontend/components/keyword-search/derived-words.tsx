"use client";

import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { cn } from "@/lib/utils";

interface DerivedWordsProps {
  words: string[];
  selectedWord: string | null;
  onWordSelect: (word: string | null) => void;
}

export function DerivedWords({ words, selectedWord, onWordSelect }: DerivedWordsProps) {
  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center gap-3">
        <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">
          Derived Words
        </h3>
        <span className="text-[var(--color-text-muted)]">◆</span>
      </div>

      {/* Word Tags */}
      <div className="flex flex-wrap gap-2">
        {/* "All Words" tag */}
        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={springPresets.snappy}
          onClick={() => onWordSelect(null)}
          className={cn(
            "px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
            selectedWord === null
              ? "bg-indigo-500 text-white"
              : "bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)]/80"
          )}
        >
          All Words
        </motion.button>

        {/* Individual word tags */}
        {words.map((word, index) => (
          <motion.button
            key={word}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ ...springPresets.snappy, delay: (index + 1) * 0.03 }}
            onClick={() => onWordSelect(selectedWord === word ? null : word)}
            lang="ar"
            className={cn(
              "font-arabic px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
              selectedWord === word
                ? "bg-indigo-500 text-white"
                : "bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)]/80"
            )}
          >
            {word}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
