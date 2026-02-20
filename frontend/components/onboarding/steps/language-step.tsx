"use client"

import { useTranslations } from "next-intl"

import { cn } from "@/lib/utils"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"
import { BlurFade } from "@/components/ui/blur-fade"
import { TextAnimate } from "@/components/ui/text-animate"

type LanguageId = "tr" | "en"

interface LanguageOption {
  id: LanguageId
  nativeName: string
  titleKey: "language.turkish" | "language.english"
  descKey: "language.turkishDesc" | "language.englishDesc"
}

const LANGUAGE_OPTIONS: LanguageOption[] = [
  {
    id: "tr",
    nativeName: "Türkçe",
    titleKey: "language.turkish",
    descKey: "language.turkishDesc",
  },
  {
    id: "en",
    nativeName: "English",
    titleKey: "language.english",
    descKey: "language.englishDesc",
  },
]

export function LanguageStep() {
  const t = useTranslations("Onboarding")

  const language = useOnboardingStore((s) => s.language)
  const setLanguage = useOnboardingStore((s) => s.setLanguage)

  return (
    <div className="flex flex-col gap-8">
      <div className="text-center">
        <TextAnimate
          by="word"
          animation="blurInUp"
          startOnView={false}
          once
          delay={0}
          duration={0.5}
          className={cn(
            "mb-3 leading-tight font-semibold tracking-[-0.02em]",
            "text-2xl sm:text-3xl",
            "text-[var(--color-text-primary)]"
          )}
        >
          {t("language.title")}
        </TextAnimate>

        <BlurFade delay={0.2} duration={0.5}>
          <p className="text-base leading-relaxed text-[var(--color-text-secondary)]">
            {t("language.subtitle")}
          </p>
        </BlurFade>
      </div>

      <BlurFade delay={0.3} duration={0.5}>
        <div className="flex gap-4">
          {LANGUAGE_OPTIONS.map((lang) => {
            const isSelected = language === lang.id
            return (
              <button
                key={lang.id}
                type="button"
                aria-pressed={isSelected}
                onClick={() => setLanguage(lang.id)}
                className={cn(
                  "flex flex-1 flex-col items-start rounded-xl px-6 py-6",
                  "border transition-all duration-200",
                  "cursor-pointer text-left select-none",
                  "focus-visible:ring-2 focus-visible:ring-[var(--color-accent-primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-transparent focus-visible:outline-none",
                  isSelected
                    ? "border-indigo-500/50 bg-indigo-500/15 ring-1 ring-indigo-500/30"
                    : "border-white/15 bg-white/[0.06] hover:border-white/25 hover:bg-white/10"
                )}
              >
                <span
                  className={cn(
                    "leading-none font-semibold tracking-tight",
                    "text-2xl sm:text-3xl",
                    "transition-colors duration-200",
                    isSelected
                      ? "text-[var(--color-text-primary)]"
                      : "text-[var(--color-text-primary)]"
                  )}
                >
                  {lang.nativeName}
                </span>

                <span
                  className={cn(
                    "mt-1 text-xs font-medium tracking-widest uppercase",
                    "transition-colors duration-200",
                    isSelected
                      ? "text-[var(--color-accent-secondary)]"
                      : "text-[var(--color-text-secondary)]"
                  )}
                >
                  {t(lang.titleKey)}
                </span>

                <p
                  className={cn(
                    "mt-3 text-sm leading-relaxed",
                    "transition-colors duration-200",
                    isSelected
                      ? "text-[var(--color-text-secondary)]"
                      : "text-[var(--color-text-secondary)]"
                  )}
                >
                  {t(lang.descKey)}
                </p>
              </button>
            )
          })}
        </div>
      </BlurFade>
    </div>
  )
}
