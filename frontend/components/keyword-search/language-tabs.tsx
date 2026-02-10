"use client"

import { Tabs, Tab } from "@/components/ui/vercel-tabs"

export type LanguageTab = "quran" | "hebrew_ot" | "greek_nt"

interface LanguageTabsProps {
  activeTab: LanguageTab
  onTabChange: (tab: LanguageTab) => void
}

const tabs: Tab[] = [
  { id: "quran", label: "Quran Arabic" },
  { id: "hebrew_ot", label: "Hebrew Old Testament" },
  { id: "greek_nt", label: "Greek New Testament" },
]

export function LanguageTabs({ activeTab, onTabChange }: LanguageTabsProps) {
  return (
    <Tabs
      tabs={tabs}
      activeTab={activeTab}
      onTabChange={(tabId) => onTabChange(tabId as LanguageTab)}
    />
  )
}
