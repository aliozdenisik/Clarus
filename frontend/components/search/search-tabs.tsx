"use client"

import { AnimatedBackground } from "@/components/motion-primitives/animated-background"
import { useTranslations } from "next-intl"

export type SearchSource = "quran" | "ot" | "nt" | "apocrypha"

interface SearchTabsProps {
  activeTab: SearchSource
  onTabChange: (tab: SearchSource) => void
}

export function SearchTabs({ activeTab, onTabChange }: SearchTabsProps) {
  const t = useTranslations("Search.tabs")

  const tabs = [
    { id: "quran", label: t("quran") },
    { id: "ot", label: t("oldTestament") },
    { id: "nt", label: t("newTestament") },
    { id: "apocrypha", label: t("apocrypha") },
  ]

  return (
    <div className="mb-8 flex justify-center">
      <AnimatedBackground
        defaultValue={activeTab}
        onValueChange={(id) => id && onTabChange(id as SearchSource)}
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
