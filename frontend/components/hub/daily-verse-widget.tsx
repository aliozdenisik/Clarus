"use client"

import Link from "next/link"
import { useTranslations } from "next-intl"

import { MagicCard } from "@/components/ui/magic-card"
import { type DailyVerse } from "@/lib/daily-verse"
import { buildVerseDetailUrl } from "@/lib/utils/verse-url"
import { cn } from "@/lib/utils"

interface DailyVerseWidgetProps {
  verse: DailyVerse
}

export function DailyVerseWidget({ verse }: DailyVerseWidgetProps) {
  const t = useTranslations("Hub")

  const verseUrl = buildVerseDetailUrl(verse.surahNumber, verse.ayahNumber)

  return (
    <MagicCard
      className={cn(
        "rounded-xl border border-[var(--hub-border)] p-4 md:p-6",
        "transition-colors hover:border-[var(--hub-border-hover)]"
      )}
      gradientSize={300}
      gradientColor="rgba(79, 70, 229, 0.08)"
      gradientFrom="rgba(79, 70, 229, 0.25)"
      gradientTo="rgba(99, 102, 241, 0.06)"
    >
      <p className="text-muted-foreground mb-4 text-xs font-medium tracking-wider uppercase">
        {t("dailyVerse")}
      </p>

      <blockquote className="mb-5 border-l-2 border-indigo-500/30 pl-4">
        <p className="font-display text-base leading-relaxed text-white/90 italic md:text-lg lg:text-xl">
          {verse.text}
        </p>
      </blockquote>

      <Link
        href={verseUrl}
        className="inline-flex items-baseline gap-0 font-mono text-sm text-white transition-colors hover:text-indigo-400"
        aria-label={verse.reference}
      >
        <span>{verse.reference}</span>
      </Link>
    </MagicCard>
  )
}
