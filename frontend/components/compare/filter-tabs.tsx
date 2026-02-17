"use client"

import { AnimatedBackground } from "@/components/motion-primitives/animated-background"

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
  const tabs = FILTERS.map((filter) => ({
    id: filter,
    label: FILTER_LABELS[filter],
    count: counts[filter],
  }))

  return (
    <AnimatedBackground
      defaultValue={activeFilter}
      onValueChange={(id) => id && onFilterChange(id as FilterType)}
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
