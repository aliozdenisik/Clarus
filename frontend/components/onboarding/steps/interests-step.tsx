"use client"

import { motion } from "motion/react"
import { useTranslations } from "next-intl"

import { cn } from "@/lib/utils"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"

const INTERESTS = [
  { id: "theology", key: "theology" },
  { id: "philology", key: "philology" },
  { id: "history", key: "history" },
  { id: "comparativeReligion", key: "comparativeReligion" },
  { id: "sociology", key: "sociology" },
  { id: "philosophy", key: "philosophy" },
  { id: "ethics", key: "ethics" },
  { id: "eschatology", key: "eschatology" },
  { id: "hermeneutics", key: "hermeneutics" },
  { id: "mysticism", key: "mysticism" },
] as const

type InterestKey = (typeof INTERESTS)[number]["key"]

export function InterestsStep() {
  const t = useTranslations("Onboarding")
  const interests = useOnboardingStore((s) => s.interests)
  const toggleInterest = useOnboardingStore((s) => s.toggleInterest)

  return (
    <div className="flex min-h-full flex-col items-center justify-center px-6 py-10 text-center">
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="mb-2"
      >
        <h2
          className={cn(
            "font-[family-name:var(--font-display)] leading-tight font-semibold tracking-[-0.02em]",
            "text-2xl sm:text-3xl lg:text-4xl",
            "text-[var(--color-text-primary)]"
          )}
        >
          {t("interests.title")}
        </h2>
      </motion.div>

      <motion.p
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.08, ease: "easeOut" }}
        className={cn(
          "mb-8 leading-relaxed font-light",
          "text-sm sm:text-base",
          "text-[var(--color-text-secondary)]"
        )}
      >
        {t("interests.subtitle")}
      </motion.p>

      <div className="mb-6 flex max-w-lg flex-wrap justify-center gap-3">
        {INTERESTS.map(({ id, key }, index) => {
          const isSelected = interests.includes(id)
          return (
            <motion.button
              key={id}
              initial={{ opacity: 0, scale: 0.85 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{
                duration: 0.3,
                delay: index * 0.05,
                ease: "easeOut",
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => toggleInterest(id)}
              className={cn(
                "cursor-pointer rounded-full px-4 py-2 text-sm font-medium transition-colors duration-200",
                "focus-visible:ring-2 focus-visible:ring-[var(--color-accent-primary)] focus-visible:ring-offset-2 focus-visible:outline-none",
                isSelected
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "bg-background border-border hover:border-primary/50 border text-[var(--color-text-primary)]"
              )}
              aria-pressed={isSelected}
            >
              {t(`interests.${key}` as `interests.${InterestKey}`)}
            </motion.button>
          )
        })}
      </div>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.6 }}
        className={cn(
          "text-xs font-medium",
          interests.length > 0 ? "text-amber-400" : "text-[var(--color-text-secondary)]"
        )}
      >
        {interests.length > 0
          ? t("interests.selectedCount", { count: interests.length })
          : t("interests.optional")}
      </motion.p>
    </div>
  )
}
