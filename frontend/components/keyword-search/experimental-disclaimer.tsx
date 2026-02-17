"use client"

import { Info } from "lucide-react"
import { cn } from "@/lib/utils"
import { useTranslations } from "next-intl"

interface ExperimentalDisclaimerProps {
  className?: string
}

export function ExperimentalDisclaimer({ className }: ExperimentalDisclaimerProps) {
  const t = useTranslations("KeywordSearch")

  return (
    <div
      className={cn(
        "flex items-center justify-center gap-2 rounded-lg px-4 py-2",
        "border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/60",
        "text-xs text-[var(--color-text-secondary)]",
        className
      )}
    >
      <Info
        aria-hidden="true"
        className="h-3.5 w-3.5 flex-shrink-0 text-[var(--color-text-muted)]"
      />
      <span>
        <strong className="font-semibold text-[var(--color-text-primary)]">
          {t("experimental.title")}:
        </strong>{" "}
        {t("experimental.content")}
      </span>
    </div>
  )
}
