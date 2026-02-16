"use client"

import { Tabs, Tab } from "@/components/ui/vercel-tabs"
import { useTranslations } from "next-intl"

export type LanguageTab = "quran" | "hebrew_ot" | "greek_nt"

interface LanguageTabsProps {
  activeTab: LanguageTab
  onTabChange: (tab: LanguageTab) => void
}

export function LanguageTabs({ activeTab, onTabChange }: LanguageTabsProps) {
  const t = useTranslations("KeywordSearch")
  const tabs: Tab[] = [
    { id: "quran", label: t("language.quran") },
    { id: "hebrew_ot", label: t("language.oldTestament") },
    { id: "greek_nt", label: t("language.newTestament") },
  ]

  return (
    <Tabs
      tabs={tabs}
      activeTab={activeTab}
      onTabChange={(tabId) => onTabChange(tabId as LanguageTab)}
    />
  )
}
