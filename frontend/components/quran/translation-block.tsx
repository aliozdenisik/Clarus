"use client"

import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"

interface TranslationBlockProps {
  translator: string
  translatorDisplay: string
  text: string
  index: number
}

export function TranslationBlock({ translatorDisplay, text, index }: TranslationBlockProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...springPresets.gentle, delay: index * 0.06 }}
      data-testid="translation-block"
      className="group relative rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-6 transition-all duration-300 hover:border-[var(--color-accent-primary)]/30 hover:shadow-[var(--color-accent-primary)]/5 hover:shadow-lg"
    >
      <div className="relative flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-[var(--color-border-subtle)] to-transparent" />
          <span
            data-testid="translator-name"
            className="text-xs font-medium tracking-wider text-[var(--color-text-muted)] uppercase transition-colors group-hover:text-[var(--color-accent-primary)]"
          >
            {translatorDisplay}
          </span>
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-[var(--color-border-subtle)] to-transparent" />
        </div>
        <p
          lang="tr"
          data-testid="translation-text"
          className="font-crimson verse-translation text-lg leading-relaxed text-[var(--color-text-primary)]"
        >
          {text}
        </p>
      </div>
    </motion.div>
  )
}
