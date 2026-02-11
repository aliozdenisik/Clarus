"use client"

import { cn } from "@/lib/utils"

interface VerseBlockProps {
  verse: {
    id: number
    text: string
    translation: string
  }
  isHighlighted?: boolean
  onClick?: () => void
}

export function VerseBlock({ verse, isHighlighted, onClick }: VerseBlockProps) {
  return (
    <div
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
          <p lang="ar" className="font-arabic text-2xl text-[var(--color-text-primary)]">
            {verse.text}
          </p>
          {verse.translation ? (
            <p
              lang="tr"
              className="font-crimson verse-translation text-xl text-[var(--color-text-secondary)]"
            >
              {verse.translation}
            </p>
          ) : (
            <p className="text-sm text-[var(--color-text-muted)] italic">Meâl bulunamadı</p>
          )}
        </div>
      </div>
    </div>
  )
}
