"use client"

import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { MagicCard } from "@/components/ui/magic-card"
import { useTranslations } from "next-intl"

interface StatsBarProps {
  totalOccurrences: number
  uniqueWords: number
  surahCount: number
  language: "quran" | "hebrew_ot" | "greek_nt"
}

interface StatItem {
  label: string
  value: number
}

export function StatsBar({ totalOccurrences, uniqueWords, surahCount, language }: StatsBarProps) {
  const t = useTranslations("KeywordSearch")
  const stats: StatItem[] = [
    { label: t("stats.totalUsage"), value: totalOccurrences },
    { label: t("stats.uniqueWord"), value: uniqueWords },
    { label: language === "quran" ? t("stats.surahs") : t("stats.books"), value: surahCount },
  ]

  return (
    <div className="grid grid-cols-3 gap-4">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springPresets.snappy, delay: index * 0.1 }}
        >
          <MagicCard className="flex flex-col items-center justify-center p-6 rounded-lg border border-[var(--color-border-subtle)]" gradientSize={200} gradientColor="#1a1a2e" gradientFrom="#7c3aed" gradientTo="#4f46e5">
            <div className="text-3xl font-bold text-[var(--color-text-primary)]">{stat.value}</div>
            <div className="mt-1 text-xs text-[var(--color-text-muted)]">{stat.label}</div>
          </MagicCard>
        </motion.div>
      ))}
    </div>
  )
}
