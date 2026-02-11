"use client"

import { motion } from "framer-motion"
import { springPresets, tactileScale } from "@/lib/design-system"
import { ClickableVerse } from "./clickable-verse"
import { cn } from "@/lib/utils"

interface VerseBlockProps {
  surahId: number
  verse: {
    id: number
    text: string
    translation: string
  }
  isHighlighted?: boolean
  onClick?: () => void
}

export function VerseBlock({ surahId, verse, isHighlighted, onClick }: VerseBlockProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={springPresets.gentle}
      whileHover={{ y: -1 }}
      whileTap={tactileScale.press}
      onClick={onClick}
      data-testid="verse-block"
      data-verse={verse.id}
      data-verse-id={verse.id}
      className={cn(
        "cursor-pointer rounded-lg p-6 transition-all duration-300",
        isHighlighted
          ? "bg-[var(--color-accent-primary)]/5 shadow-[var(--color-accent-primary)]/20 shadow-lg ring-2 ring-[var(--color-accent-primary)]"
          : "hover:bg-[var(--color-bg-surface)]/30"
      )}
    >
      <div className="flex gap-4">
        <div className="flex-shrink-0">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-bg-secondary)] text-xl font-medium text-[var(--color-accent-primary)]">
            {verse.id}
          </div>
        </div>
        <div className="flex flex-1 flex-col gap-4">
          <ClickableVerse surahId={surahId} ayahNumber={verse.id} arabicText={verse.text} />
          {verse.translation ? (
            <p
              lang="tr"
              className="font-crimson verse-translation text-xl text-[var(--color-text-secondary)]"
            >
              {verse.translation}
            </p>
          ) : (
            <p className="text-sm text-[var(--color-text-muted)] italic">
              Translation not available
            </p>
          )}
        </div>
      </div>
    </motion.div>
  )
}
