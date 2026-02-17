"use client"

import { AnimatedBackground } from "@/components/motion-primitives/animated-background"
import { useTranslations } from "next-intl"

export type LanguageTab = "quran" | "hebrew_ot" | "greek_nt"

interface LanguageTabsProps {
  activeTab: LanguageTab
  onTabChange: (tab: LanguageTab) => void
}

export function LanguageTabs({ activeTab, onTabChange }: LanguageTabsProps) {
  const t = useTranslations("KeywordSearch")
  const tabs = [
    { id: "quran", label: t("language.quran") },
    { id: "hebrew_ot", label: t("language.oldTestament") },
    { id: "greek_nt", label: t("language.newTestament") },
  ]

  return (
    <AnimatedBackground
      defaultValue={activeTab}
      onValueChange={(id) => id && onTabChange(id as LanguageTab)}
      className="rounded-lg bg-white/[0.08]"
      transition={{ type: "spring", bounce: 0.15, duration: 0.5 }}
    >
      {tabs.map((tab) => (
        <button
          key={tab.id}
          data-id={tab.id}
          type="button"
          className="px-3 py-1.5 text-sm font-medium text-[var(--color-text-secondary)] transition-colors data-[checked=true]:text-white"
        >
          {tab.label}
        </button>
      ))}
    </AnimatedBackground>
  )
}
