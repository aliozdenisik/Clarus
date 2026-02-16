"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { Info, ChevronDown, ExternalLink } from "lucide-react"
import { cn } from "@/lib/utils"
import { useTranslations } from "next-intl"

interface VerificationEntry {
  strong: string
  word: string
  ourCount: number
  blbCount: number
}

const VERIFICATION_DATA: VerificationEntry[] = [
  { strong: "H1697", word: "dabar", ourCount: 1440, blbCount: 1439 },
  { strong: "H8451", word: "torah", ourCount: 219, blbCount: 219 },
  { strong: "H430", word: "elohim", ourCount: 2596, blbCount: 2606 },
  { strong: "G2316", word: "theos", ourCount: 1307, blbCount: 1318 },
]

function calculateDelta(
  ours: number,
  blb: number
): { value: number; percent: string; status: "exact" | "pass" } {
  const delta = ours - blb
  const percent = ((Math.abs(delta) / blb) * 100).toFixed(2)
  return {
    value: delta,
    percent,
    status: delta === 0 ? "exact" : "pass",
  }
}

interface AccuracyDisclaimerProps {
  className?: string
}

export function AccuracyDisclaimer({ className }: AccuracyDisclaimerProps) {
  const t = useTranslations("KeywordSearch")
  const tCommon = useTranslations("Common")
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className={cn("w-full", className)}>
      {/* Collapsed state - just a subtle link */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="group mx-auto flex items-center gap-2 text-xs text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-text-secondary)]"
      >
        <Info className="h-3.5 w-3.5" />
        <span>{t("accuracy.verifyInfo")}</span>
        <ChevronDown
          className={cn(
            "h-3.5 w-3.5 transition-transform duration-200",
            isExpanded && "rotate-180"
          )}
        />
      </button>

      {/* Expanded state - full accuracy report */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={springPresets.snappy}
            className="overflow-hidden"
          >
            <div className="mt-4 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-4">
              {/* Header */}
              <div className="mb-3 flex items-center justify-between">
                <h4 className="text-sm font-medium text-[var(--color-text-primary)]">
                  {t("accuracy.verificationTitle")}
                </h4>
                <a
                  href="https://www.blueletterbible.org/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-xs text-[var(--color-accent-primary)] hover:underline"
                >
                  {t("accuracy.verificationTitle")}
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>

              {/* Explanation */}
              <p className="mb-3 text-xs text-[var(--color-text-muted)]">
                {t("disclaimer.content")}
              </p>

              {/* Data Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-[var(--color-border-subtle)]">
                      <th className="py-2 text-left font-medium text-[var(--color-text-muted)]">
                        {t("stats.root")}
                      </th>
                      <th className="py-2 text-left font-medium text-[var(--color-text-muted)]">
                        {t("derivedWords.title")}
                      </th>
                      <th className="py-2 text-right font-medium text-[var(--color-text-muted)]">
                        {t("pageTitle")}
                      </th>
                      <th className="py-2 text-right font-medium text-[var(--color-text-muted)]">
                        {t("rootInfo.buckwalter")}
                      </th>
                      <th className="py-2 text-right font-medium text-[var(--color-text-muted)]">
                        Δ
                      </th>
                      <th className="py-2 text-right font-medium text-[var(--color-text-muted)]">
                        {tCommon("success")}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {VERIFICATION_DATA.map((entry) => {
                      const delta = calculateDelta(entry.ourCount, entry.blbCount)
                      return (
                        <tr
                          key={entry.strong}
                          className="border-b border-[var(--color-border-subtle)] last:border-0"
                        >
                          <td className="py-2 font-mono text-[var(--color-text-secondary)]">
                            {entry.strong}
                          </td>
                          <td className="py-2 text-[var(--color-text-primary)]">{entry.word}</td>
                          <td className="py-2 text-right font-mono text-[var(--color-text-primary)]">
                            {entry.ourCount.toLocaleString()}
                          </td>
                          <td className="py-2 text-right font-mono text-[var(--color-text-secondary)]">
                            {entry.blbCount.toLocaleString()}
                          </td>
                          <td className="py-2 text-right font-mono">
                            <span
                              className={cn(
                                delta.value === 0 ? "text-emerald-400" : "text-amber-400"
                              )}
                            >
                              {delta.value > 0 ? "+" : ""}
                              {delta.value} ({delta.percent}%)
                            </span>
                          </td>
                          <td className="py-2 text-right">
                            <span
                              className={cn(
                                "rounded px-1.5 py-0.5 text-[10px] font-medium",
                                delta.status === "exact"
                                  ? "bg-emerald-500/20 text-emerald-400"
                                  : "bg-amber-500/20 text-amber-400"
                              )}
                            >
                              {delta.status === "exact" ? tCommon("success") : tCommon("failed")}
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              {/* Footer note */}
              <div className="mt-3 border-t border-[var(--color-border-subtle)] pt-3">
                <p className="text-[10px] leading-relaxed text-[var(--color-text-muted)]">
                  <strong>{t("disclaimer.title")}:</strong> {t("disclaimer.content")}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
