"use client"

import { Tabs, Tab } from "@/components/ui/vercel-tabs"

export type FilterType = "all" | "quran" | "old_testament" | "new_testament" | "apocrypha"

interface FilterTabsProps {
  activeFilter: FilterType
  onFilterChange: (filter: FilterType) => void
  counts: Partial<Record<FilterType, number>>
}

const FILTER_LABELS: Record<FilterType, string> = {
  all: "All",
  quran: "Quran",
  old_testament: "Old Testament",
  new_testament: "New Testament",
  apocrypha: "Apocrypha",
}

const FILTERS: FilterType[] = ["all", "quran", "old_testament", "new_testament", "apocrypha"]

export function FilterTabs({ activeFilter, onFilterChange, counts }: FilterTabsProps) {
  // Build tabs with counts
  const tabs: Tab[] = FILTERS.map((filter) => ({
    id: filter,
    label: FILTER_LABELS[filter],
    count: counts[filter],
  }))

  return (
    <Tabs
      tabs={tabs}
      activeTab={activeFilter}
      onTabChange={(tabId) => onFilterChange(tabId as FilterType)}
    />
  )
}
