"use client"

import { Tabs, Tab } from "@/components/ui/vercel-tabs"
import { useTranslations } from "next-intl"

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

export function BibleCategoryTabs({
  activeCategory,
  onCategoryChange,
  languageMode,
}: BibleCategoryTabsProps) {
  const t = useTranslations("KeywordSearch")
  const hebrewCategories: Tab[] = [
    { id: "all", label: t("bibleCategory.all") },
    { id: "ot", label: t("bibleCategory.oldTestament") },
    { id: "apocrypha", label: t("bibleCategory.apocrypha") },
    { id: "pseudepigrapha", label: t("bibleCategory.pseudepigrapha") },
  ]
  const greekCategories: Tab[] = [
    { id: "all", label: t("bibleCategory.all") },
    { id: "nt", label: t("bibleCategory.newTestament") },
    { id: "apocrypha", label: t("bibleCategory.apocrypha") },
    { id: "gnostic", label: t("bibleCategory.gnostic") },
    { id: "apostolic_fathers", label: t("bibleCategory.apostolicFathers") },
  ]

  const categories = languageMode === "hebrew_ot" ? hebrewCategories : greekCategories

  return (
    <Tabs
      tabs={categories}
      activeTab={activeCategory}
      onTabChange={(tabId) => onCategoryChange(tabId as BibleCategoryFilter)}
    />
  )
}
