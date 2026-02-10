"use client"

import { Tabs, Tab } from "@/components/ui/vercel-tabs"

export type BibleCategoryFilter =
  | "all"
  | "ot"
  | "nt"
  | "apocrypha"
  | "pseudepigrapha"
  | "gnostic"
  | "apostolic_fathers"

interface BibleCategoryTabsProps {
  activeCategory: BibleCategoryFilter
  onCategoryChange: (category: BibleCategoryFilter) => void
  languageMode: "hebrew_ot" | "greek_nt"
}

// Categories available for Hebrew OT mode
const hebrewCategories: Tab[] = [
  { id: "all", label: "All" },
  { id: "ot", label: "Old Testament" },
  { id: "apocrypha", label: "Apocrypha" },
  { id: "pseudepigrapha", label: "Pseudepigrapha" },
]

// Categories available for Greek NT mode
const greekCategories: Tab[] = [
  { id: "all", label: "All" },
  { id: "nt", label: "New Testament" },
  { id: "apocrypha", label: "Apocrypha" },
  { id: "gnostic", label: "Gnostic" },
  { id: "apostolic_fathers", label: "Apostolic Fathers" },
]

export function BibleCategoryTabs({
  activeCategory,
  onCategoryChange,
  languageMode,
}: BibleCategoryTabsProps) {
  const categories = languageMode === "hebrew_ot" ? hebrewCategories : greekCategories

  return (
    <Tabs
      tabs={categories}
      activeTab={activeCategory}
      onTabChange={(tabId) => onCategoryChange(tabId as BibleCategoryFilter)}
    />
  )
}
