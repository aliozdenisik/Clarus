"use client"

import { useState } from "react"

import { Info, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { useTranslations } from "next-intl"

interface ExperimentalDisclaimerProps {
  className?: string
}

export function ExperimentalDisclaimer({ className }: ExperimentalDisclaimerProps) {
  const t = useTranslations("KeywordSearch")
  const [dismissed, setDismissed] = useState(false)

  if (dismissed) {
    return null
  }

  return (
    <div
      className={cn(
        "flex items-start justify-between gap-3 rounded-lg px-4 py-2",
        "border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/60",
        "text-xs text-[var(--color-text-secondary)]",
        className
      )}
    >
      <div className="flex items-start gap-2">
        <Info
          aria-hidden="true"
          className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-[var(--color-text-muted)]"
        />
        <span>
          <strong className="font-semibold text-[var(--color-text-primary)]">
            {t("experimental.title")}:
          </strong>{" "}
          {t("experimental.content")}
        </span>
      </div>
      <button
        type="button"
        onClick={() => setDismissed(true)}
        className="text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-text-primary)]"
        aria-label={t("experimental.dismiss")}
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  )
}
