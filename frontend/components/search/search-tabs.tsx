"use client"

import * as React from "react"
import { Tabs, Tab } from "@/components/ui/vercel-tabs"

export type SearchSource = "quran" | "ot" | "nt" | "apocrypha"

interface SearchTabsProps {
  activeTab: SearchSource
  onTabChange: (tab: SearchSource) => void
}

const tabs: Tab[] = [
  { id: "quran", label: "Quran" },
  { id: "ot", label: "Old Testament" },
  { id: "nt", label: "New Testament" },
  { id: "apocrypha", label: "Apocrypha" },
]

export function SearchTabs({ activeTab, onTabChange }: SearchTabsProps) {
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
