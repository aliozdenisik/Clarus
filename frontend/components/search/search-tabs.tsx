"use client"

import { Tabs, Tab } from "@/components/ui/vercel-tabs"
import { useTranslations } from "next-intl"

export type SearchSource = "quran" | "ot" | "nt" | "apocrypha"

interface SearchTabsProps {
  activeTab: SearchSource
  onTabChange: (tab: SearchSource) => void
}

export function SearchTabs({ activeTab, onTabChange }: SearchTabsProps) {
  const t = useTranslations("Search.tabs")

  const tabs: Tab[] = [
    { id: "quran", label: t("quran") },
    { id: "ot", label: t("oldTestament") },
    { id: "nt", label: t("newTestament") },
    { id: "apocrypha", label: t("apocrypha") },
  ]

  return (
    <div className="mb-8 flex justify-center">
      <Tabs
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={(tabId) => onTabChange(tabId as SearchSource)}
      />
    </div>
  )
}
