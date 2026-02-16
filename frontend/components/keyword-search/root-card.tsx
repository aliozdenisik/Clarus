"use client"

import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useTranslations } from "next-intl"

interface RootCardProps {
  root: string | null
  rootSource: string
  rootBuckwalter?: string | null
  strongNumber?: string | null
  language?: "arabic" | "hebrew" | "greek"
}

export function RootCard({
  root,
  rootSource,
  rootBuckwalter,
  strongNumber,
  language = "arabic",
}: RootCardProps) {
  const t = useTranslations("KeywordSearch")
  void rootSource
  const isHebrew = language === "hebrew"
  const isGreek = language === "greek"

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={springPresets.fluid}
      className="flex flex-col items-center gap-4 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-8"
    >
      {root ? (
        <>
          <div className="flex items-center gap-3">
            <p
              lang={isGreek ? "el" : isHebrew ? "he" : "ar"}
              className={`${isGreek ? "font-greek" : isHebrew ? "font-hebrew" : "font-arabic"} text-center text-5xl font-bold text-[var(--color-text-primary)]`}
              dir={isGreek ? "ltr" : "rtl"}
            >
              {isGreek ? root : <bdi>{root}</bdi>}
            </p>
            {(isHebrew || isGreek) && strongNumber && (
              <span className="rounded border border-indigo-500/30 bg-indigo-500/20 px-2 py-1 font-mono text-xs text-indigo-300">
                {strongNumber}
              </span>
            )}
          </div>
          {rootBuckwalter && (
            <p className="text-center text-lg tracking-wide text-[var(--color-text-muted)]">
              {rootBuckwalter}
            </p>
          )}
        </>
      ) : (
        <p className="text-center text-[var(--color-text-muted)]">{t("noResults")}</p>
      )}
    </motion.div>
  )
}
