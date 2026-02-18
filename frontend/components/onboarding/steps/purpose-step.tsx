"use client"

import { GraduationCap, BookOpen, Mic, GitCompare, FileText } from "lucide-react"
import { useTranslations } from "next-intl"
import type { LucideIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"

type PurposeKey = "academic" | "personal" | "preaching" | "comparative" | "textual"

interface PurposeOption {
  id: PurposeKey
  icon: LucideIcon
}

const PURPOSES: PurposeOption[] = [
  { id: "academic", icon: GraduationCap },
  { id: "personal", icon: BookOpen },
  { id: "preaching", icon: Mic },
  { id: "comparative", icon: GitCompare },
  { id: "textual", icon: FileText },
]

export function PurposeStep() {
  const t = useTranslations("Onboarding")
  const usagePurpose = useOnboardingStore((s) => s.usagePurpose)
  const setUsagePurpose = useOnboardingStore((s) => s.setUsagePurpose)

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-white">{t("purpose.title")}</h2>
        <p className="mt-2 text-sm text-white/60">{t("purpose.subtitle")}</p>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {PURPOSES.map(({ id, icon: Icon }) => {
          const isSelected = usagePurpose === id
          return (
            <button
              key={id}
              type="button"
              onClick={() => setUsagePurpose(id)}
              className={cn(
                "flex flex-col items-center gap-3 rounded-xl px-4 py-6",
                "border transition-all duration-200",
                "cursor-pointer text-center select-none",
                "focus-visible:ring-2 focus-visible:ring-[var(--color-accent-primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-transparent focus-visible:outline-none",
                isSelected
                  ? "border-indigo-500/40 bg-indigo-500/[0.08] text-white"
                  : "border-white/10 bg-white/[0.03] text-white/70 hover:border-white/20 hover:bg-white/[0.06]"
              )}
            >
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-lg transition-colors duration-200",
                  isSelected ? "bg-indigo-500/20" : "bg-white/10"
                )}
              >
                <Icon
                  className={cn(
                    "h-5 w-5 transition-colors duration-200",
                    isSelected ? "text-indigo-300" : "text-white/60"
                  )}
                  aria-hidden="true"
                />
              </div>

              <span className="text-sm leading-tight font-medium">{t(`purpose.${id}`)}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
