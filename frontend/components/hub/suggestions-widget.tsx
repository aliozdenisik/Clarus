"use client"

import { BookOpen, ChevronRight, GitCompareArrows, Languages, Search } from "lucide-react"
import { useTranslations } from "next-intl"
import type { ElementType } from "react"

import { useRouter } from "@/i18n/navigation"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"
import { cn } from "@/lib/utils"

interface SuggestionConfig {
  labelKey: string
  href: string
  icon: ElementType
}

const INTEREST_SUGGESTION_MAP: Record<string, SuggestionConfig[]> = {
  theology: [
    { labelKey: "suggestExploreQuran", href: "/quran", icon: BookOpen },
    { labelKey: "suggestSearchQuran", href: "/search", icon: Search },
  ],
  philology: [{ labelKey: "suggestKeywordSearch", href: "/keyword-search", icon: Languages }],
  hermeneutics: [
    { labelKey: "suggestKeywordSearch", href: "/keyword-search", icon: Languages },
    { labelKey: "suggestSearchFeature", href: "/search", icon: Search },
  ],
  comparativeReligion: [
    { labelKey: "suggestCompareForgiving", href: "/compare", icon: GitCompareArrows },
    { labelKey: "suggestCompare", href: "/compare", icon: GitCompareArrows },
  ],
  history: [
    { labelKey: "suggestReadBible", href: "/old-testament", icon: BookOpen },
    { labelKey: "suggestCompare", href: "/compare", icon: GitCompareArrows },
  ],
  eschatology: [
    { labelKey: "suggestCompare", href: "/compare", icon: GitCompareArrows },
    { labelKey: "suggestSearchQuran", href: "/search", icon: Search },
  ],
  philosophy: [
    { labelKey: "suggestCompareForgiving", href: "/compare", icon: GitCompareArrows },
    { labelKey: "suggestSearchFeature", href: "/search", icon: Search },
  ],
  ethics: [
    { labelKey: "suggestCompareForgiving", href: "/compare", icon: GitCompareArrows },
    { labelKey: "suggestCompare", href: "/compare", icon: GitCompareArrows },
  ],
  mysticism: [
    { labelKey: "suggestExploreQuran", href: "/quran", icon: BookOpen },
    { labelKey: "suggestSearchQuran", href: "/search", icon: Search },
  ],
  sociology: [
    { labelKey: "suggestCompare", href: "/compare", icon: GitCompareArrows },
    { labelKey: "suggestBrowseFeature", href: "/quran", icon: BookOpen },
  ],
}

const DEFAULT_SUGGESTIONS: SuggestionConfig[] = [
  { labelKey: "suggestSearchFeature", href: "/search", icon: Search },
  { labelKey: "suggestBrowseFeature", href: "/quran", icon: BookOpen },
  { labelKey: "suggestCompareFeature", href: "/compare", icon: GitCompareArrows },
]

const MAX_SUGGESTIONS = 4

function buildSuggestions(interests: string[]): SuggestionConfig[] {
  if (interests.length === 0) {
    return DEFAULT_SUGGESTIONS
  }

  const seen = new Set<string>()
  const result: SuggestionConfig[] = []

  for (const interest of interests) {
    const mapped = INTEREST_SUGGESTION_MAP[interest]
    if (!mapped) continue

    for (const suggestion of mapped) {
      if (!seen.has(suggestion.labelKey) && result.length < MAX_SUGGESTIONS) {
        seen.add(suggestion.labelKey)
        result.push(suggestion)
      }
    }

    if (result.length >= MAX_SUGGESTIONS) break
  }

  if (result.length === 0) {
    return DEFAULT_SUGGESTIONS
  }

  return result
}

export function SuggestionsWidget() {
  const t = useTranslations("Hub")
  const router = useRouter()
  const interests = useOnboardingStore((s) => s.interests)

  const suggestions = buildSuggestions(interests)

  return (
    <div>
      <p className="text-muted-foreground mb-3 text-xs font-medium tracking-wider uppercase">
        {t("suggestions")}
      </p>

      <div
        className={cn(
          "flex gap-3 overflow-x-auto",
          "[&::-webkit-scrollbar]:hidden",
          "[-ms-overflow-style:none]",
          "[scrollbar-width:none]"
        )}
      >
        {suggestions.map((suggestion) => {
          const Icon = suggestion.icon

          return (
            <button
              key={suggestion.labelKey}
              type="button"
              onClick={() => router.push(suggestion.href)}
              className={cn(
                "group",
                "inline-flex shrink-0 items-center gap-2 px-4 py-2.5",
                "rounded-full border border-white/[0.08]",
                "hover:border-white/[0.15] hover:bg-white/[0.03]",
                "transition-colors duration-200",
                "cursor-pointer"
              )}
            >
              <Icon className="text-muted-foreground h-4 w-4 shrink-0" aria-hidden />
              <span className="text-foreground/80 text-sm">
                {t(suggestion.labelKey as Parameters<typeof t>[0])}
              </span>
              <ChevronRight
                className={cn(
                  "text-muted-foreground h-3.5 w-3.5 shrink-0",
                  "opacity-0 transition-opacity duration-200 group-hover:opacity-100"
                )}
                aria-hidden
              />
            </button>
          )
        })}
      </div>
    </div>
  )
}
