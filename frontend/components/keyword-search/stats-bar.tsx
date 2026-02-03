"use client";

import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { GlowCard } from "@/components/ui/glow-card";

interface StatsBarProps {
  totalOccurrences: number;
  uniqueWords: number;
  surahCount: number;
  language: "quran" | "hebrew_ot" | "greek_nt";
}

interface StatItem {
  label: string;
  value: number;
}

export function StatsBar({ totalOccurrences, uniqueWords, surahCount, language }: StatsBarProps) {
  const stats: StatItem[] = [
    { label: "Total Occurrences", value: totalOccurrences },
    { label: "Unique Words", value: uniqueWords },
    { label: language === "quran" ? "Surahs" : "Books", value: surahCount },
  ];

  return (
    <div className="grid grid-cols-3 gap-4">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springPresets.snappy, delay: index * 0.1 }}
        >
          <GlowCard className="flex flex-col items-center justify-center p-6">
            <div className="text-3xl font-bold text-[var(--color-text-primary)]">
              {stat.value}
            </div>
            <div className="text-xs text-[var(--color-text-muted)] mt-1">
              {stat.label}
            </div>
          </GlowCard>
        </motion.div>
      ))}
    </div>
  );
}
