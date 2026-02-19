"use client"

import Link from "next/link"
import { useTranslations } from "next-intl"

import { MagicCard } from "@/components/ui/magic-card"
import { NumberTicker } from "@/components/ui/number-ticker"
import { type DailyVerse } from "@/lib/daily-verse"
import { buildVerseDetailUrl } from "@/lib/utils/verse-url"
import { cn } from "@/lib/utils"

interface DailyVerseWidgetProps {
  verse: DailyVerse
}

export function DailyVerseWidget({ verse }: DailyVerseWidgetProps) {
  const t = useTranslations("Hub")

  const verseUrl = buildVerseDetailUrl(verse.surahNumber, verse.ayahNumber)
  const colonIndex = verse.reference.lastIndexOf(":")
  const referencePrefix =
    colonIndex !== -1 ? verse.reference.slice(0, colonIndex + 1) : `${verse.reference}:`

  return (
    <MagicCard
      className={cn(
        "rounded-xl border border-[var(--hub-border)] p-6",
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
        <p className="font-display text-lg leading-relaxed text-white/90 italic md:text-xl">
          {verse.text}
        </p>
      </blockquote>

      <Link
        href={verseUrl}
        className="text-muted-foreground inline-flex items-baseline gap-0 font-mono text-sm transition-colors hover:text-indigo-400"
        aria-label={verse.reference}
      >
        <span>{referencePrefix}</span>
        <NumberTicker
          value={verse.ayahNumber}
          startValue={0}
          delay={0.2}
          className={cn("text-muted-foreground font-mono text-sm tabular-nums")}
        />
      </Link>
    </MagicCard>
  )
}
