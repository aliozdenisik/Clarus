"use client"

import { useTranslations } from "next-intl"
import { motion, AnimatePresence } from "motion/react"

import { cn } from "@/lib/utils"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"
import { Slider } from "@/components/ui/slider"
import { MagicCard } from "@/components/ui/magic-card"
import { BlurFade } from "@/components/ui/blur-fade"

const LEVELS = ["none", "basic", "intermediate", "advanced"] as const
type ProficiencyLevel = (typeof LEVELS)[number]

const BISMILLAH = {
  arabic: "بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ",
  transliteration: "Bismillahir-rahmanir-rahim",
  translation: "Rahman ve Rahim olan Allah'ın adıyla",
  reference: "Al-Fatiha 1:1",
} as const

interface PreviewContent {
  showArabic: boolean
  showTransliteration: boolean
  showTranslation: boolean
  showRootHint: boolean
}

const PREVIEW_CONTENT: Record<ProficiencyLevel, PreviewContent> = {
  none: {
    showArabic: false,
    showTransliteration: false,
    showTranslation: true,
    showRootHint: false,
  },
  basic: {
    showArabic: false,
    showTransliteration: true,
    showTranslation: true,
    showRootHint: false,
  },
  intermediate: {
    showArabic: true,
    showTransliteration: false,
    showTranslation: true,
    showRootHint: false,
  },
  advanced: {
    showArabic: true,
    showTransliteration: false,
    showTranslation: true,
    showRootHint: true,
  },
}

const LEVEL_COLORS: Record<ProficiencyLevel, string> = {
  none: "bg-[var(--color-text-tertiary)]",
  basic: "bg-emerald-400",
  intermediate: "bg-blue-400",
  advanced: "bg-purple-400",
}

const LEVEL_ACCENT_FROM: Record<ProficiencyLevel, string> = {
  none: "#404040",
  basic: "#059669",
  intermediate: "#3b82f6",
  advanced: "#9333ea",
}

const LEVEL_ACCENT_TO: Record<ProficiencyLevel, string> = {
  none: "#1a1a1a",
  basic: "#047857",
  intermediate: "#2563eb",
  advanced: "#7c3aed",
}

export function ArabicStep() {
  const t = useTranslations("Onboarding")

  const arabicProficiency = useOnboardingStore((s) => s.arabicProficiency)
  const setArabicProficiency = useOnboardingStore((s) => s.setArabicProficiency)

  const currentIndex = LEVELS.indexOf(arabicProficiency as ProficiencyLevel)
  const safeIndex = currentIndex === -1 ? 0 : currentIndex
  const currentLevel = LEVELS[safeIndex]
  const preview = PREVIEW_CONTENT[currentLevel]

  const handleValueChange = ([value]: number[]) => {
    setArabicProficiency(LEVELS[value])
  }

  return (
    <div className="flex flex-col gap-8 px-2 py-4">
      <BlurFade delay={0} duration={0.5}>
        <div className="space-y-1 text-center">
          <h2
            className={cn(
              "font-[family-name:var(--font-display)] font-semibold tracking-[-0.01em]",
              "text-2xl sm:text-3xl",
              "text-[var(--color-text-primary)]"
            )}
          >
            {t("arabic.title")}
          </h2>
          <p className="text-sm text-[var(--color-text-secondary)]">{t("arabic.subtitle")}</p>
        </div>
      </BlurFade>

      <BlurFade delay={0.1} duration={0.5}>
        <div className="space-y-5">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentLevel}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="flex min-h-[3rem] flex-col items-center gap-1 text-center"
            >
              <div className="flex items-center gap-2">
                <span
                  className={cn("inline-block h-2 w-2 rounded-full", LEVEL_COLORS[currentLevel])}
                />
                <span className="text-base font-semibold text-[var(--color-text-primary)]">
                  {t(`arabic.${currentLevel}`)}
                </span>
              </div>
              <p className="text-sm text-[var(--color-text-secondary)]">
                {t(`arabic.${currentLevel}Desc`)}
              </p>
            </motion.div>
          </AnimatePresence>

          <Slider
            min={0}
            max={3}
            step={1}
            value={[safeIndex]}
            onValueChange={handleValueChange}
            aria-label={t("arabic.title")}
          />

          <div className="flex justify-between px-1">
            {LEVELS.map((level, i) => (
              <button
                key={level}
                type="button"
                onClick={() => setArabicProficiency(level)}
                className={cn(
                  "text-xs transition-colors duration-200",
                  i === safeIndex
                    ? "font-medium text-[var(--color-text-primary)]"
                    : "text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]"
                )}
              >
                {t(`arabic.${level}`)}
              </button>
            ))}
          </div>
        </div>
      </BlurFade>

      <BlurFade delay={0.2} duration={0.5}>
        <div className="relative overflow-hidden rounded-xl border border-[var(--color-border-subtle)]">
          <MagicCard
            className="rounded-xl bg-[var(--color-bg-surface)]/80 p-6 backdrop-blur-sm"
            gradientSize={180}
            gradientColor="#1a1a2e"
            gradientFrom={LEVEL_ACCENT_FROM[currentLevel]}
            gradientTo={LEVEL_ACCENT_TO[currentLevel]}
          >
            <p className="mb-4 text-xs font-medium tracking-widest text-[var(--color-text-tertiary)] uppercase">
              Preview — {BISMILLAH.reference}
            </p>

            <AnimatePresence mode="wait">
              <motion.div
                key={currentLevel}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.25, ease: "easeOut" }}
                className="space-y-3"
              >
                {preview.showArabic && (
                  <p lang="ar" className="font-arabic text-2xl text-[var(--color-text-primary)]">
                    {BISMILLAH.arabic}
                  </p>
                )}

                {preview.showTransliteration && (
                  <p className="font-mono text-base text-[var(--color-text-secondary)] italic">
                    {BISMILLAH.transliteration}
                  </p>
                )}

                {preview.showTranslation && (
                  <p className="text-sm leading-relaxed text-[var(--color-text-secondary)]">
                    {BISMILLAH.translation}
                  </p>
                )}

                {preview.showRootHint && (
                  <div className="mt-2 rounded-lg border border-purple-500/20 bg-purple-500/5 px-3 py-2">
                    <p className="text-xs text-purple-300/80">
                      <span className="font-semibold">Root analysis:</span>{" "}
                      <span lang="ar" className="font-arabic text-sm">
                        ب س م
                      </span>{" "}
                      (b-s-m) · name, mark ·{" "}
                      <span lang="ar" className="font-arabic text-sm">
                        ر ح م
                      </span>{" "}
                      (r-ḥ-m) · mercy, compassion
                    </p>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </MagicCard>
        </div>
      </BlurFade>
    </div>
  )
}
