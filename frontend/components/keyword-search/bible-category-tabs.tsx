"use client"

import { AnimatedBackground } from "@/components/motion-primitives/animated-background"
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
  const hebrewCategories = [
    { id: "all", label: t("bibleCategory.all") },
    { id: "ot", label: t("bibleCategory.oldTestament") },
    { id: "apocrypha", label: t("bibleCategory.apocrypha") },
    { id: "pseudepigrapha", label: t("bibleCategory.pseudepigrapha") },
  ]
  const greekCategories = [
    { id: "all", label: t("bibleCategory.all") },
    { id: "nt", label: t("bibleCategory.newTestament") },
    { id: "apocrypha", label: t("bibleCategory.apocrypha") },
    { id: "gnostic", label: t("bibleCategory.gnostic") },
    { id: "apostolic_fathers", label: t("bibleCategory.apostolicFathers") },
  ]

  const categories = languageMode === "hebrew_ot" ? hebrewCategories : greekCategories

  return (
    <AnimatedBackground
      defaultValue={activeCategory}
      onValueChange={(id) => id && onCategoryChange(id as BibleCategoryFilter)}
      className="rounded-lg bg-white/[0.08]"
      transition={{ type: "spring", bounce: 0.15, duration: 0.5 }}
    >
      {categories.map((tab) => (
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
