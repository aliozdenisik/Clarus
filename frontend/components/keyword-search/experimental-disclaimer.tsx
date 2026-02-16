"use client"

import { AlertTriangle } from "lucide-react"
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
        "border border-amber-500/20 bg-amber-500/10",
        "text-xs text-amber-400",
        className
      )}
    >
      <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
      <span>
        <strong>{t("experimental.title")}:</strong> {t("experimental.content")}
      </span>
    </div>
  )
}
