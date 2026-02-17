"use client"

import { AnimatedBackground } from "@/components/motion-primitives/animated-background"
import { useTranslations } from "next-intl"

// Premium Filter Tabs with Vercel-style underline
export type FilterType = "all" | "quran" | "old_testament" | "new_testament" | "apocrypha"

interface AnimatedFilterTabsProps {
  activeFilter: FilterType
  onFilterChange: (filter: FilterType) => void
  counts?: Partial<Record<FilterType, number>>
}

const FILTER_LABEL_KEYS: Record<
  FilterType,
  "all" | "quran" | "oldTestament" | "newTestament" | "apocrypha"
> = {
  all: "all",
  quran: "quran",
  old_testament: "oldTestament",
  new_testament: "newTestament",
  apocrypha: "apocrypha",
}

const FILTERS: FilterType[] = ["all", "quran", "old_testament", "new_testament", "apocrypha"]

export function AnimatedFilterTabs({
  activeFilter,
  onFilterChange,
  counts,
}: AnimatedFilterTabsProps) {
  const t = useTranslations("Compare.filters")

  // Only show tabs for sources that have results (count > 0), plus "all"
  const tabs = FILTERS.filter(
    (filter) => filter === "all" || (counts && (counts[filter] ?? 0) > 0)
  ).map((filter) => ({
    id: filter,
    label: t(FILTER_LABEL_KEYS[filter]),
  }))

  // If active filter was removed (no results for that source), reset to "all"
  const effectiveFilter = tabs.some((t) => t.id === activeFilter) ? activeFilter : "all"

  return (
    <AnimatedBackground
      defaultValue={effectiveFilter}
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

// Segmented Control variant using Vercel tabs
interface SegmentedControlProps<T extends string> {
  value: T
  onChange: (value: T) => void
  options: { value: T; label: string }[]
  className?: string
}

export function SegmentedControl<T extends string>({
  value,
  onChange,
  options,
  className,
}: SegmentedControlProps<T>) {
  const tabs = options.map((opt) => ({
    id: opt.value,
    label: opt.label,
  }))

  return (
    <div className={className}>
      <AnimatedBackground
        defaultValue={value}
        onValueChange={(id) => id && onChange(id as T)}
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
    </div>
  )
}
