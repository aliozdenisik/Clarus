"use client"

import { useEffect } from "react"
import { useTranslations, useLocale } from "next-intl"

import { cn } from "@/lib/utils"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"
import { AnimatedBackground } from "@/components/motion-primitives/animated-background"
import { MagicCard } from "@/components/ui/magic-card"
import { BlurFade } from "@/components/ui/blur-fade"
import { TextAnimate } from "@/components/ui/text-animate"

type LanguageId = "tr" | "en"

interface LanguageOption {
  id: LanguageId
  emoji: string
  titleKey: "language.turkish" | "language.english"
  descKey: "language.turkishDesc" | "language.englishDesc"
}

const LANGUAGE_OPTIONS: LanguageOption[] = [
  {
    id: "tr",
    emoji: "🇹🇷",
    titleKey: "language.turkish",
    descKey: "language.turkishDesc",
  },
  {
    id: "en",
    emoji: "🇬🇧",
    titleKey: "language.english",
    descKey: "language.englishDesc",
  },
]

export function LanguageStep() {
  const t = useTranslations("Onboarding")
  const locale = useLocale()

  const language = useOnboardingStore((s) => s.language)
  const setLanguage = useOnboardingStore((s) => s.setLanguage)

  useEffect(() => {
    if (language === "tr" && locale === "en") {
      setLanguage("en")
    }
  }, [locale, language, setLanguage])

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
            "mb-3 font-[family-name:var(--font-display)] leading-tight font-semibold tracking-[-0.02em]",
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
        <MagicCard
          className="rounded-2xl p-1"
          gradientFrom="#f59e0b"
          gradientTo="#d97706"
          gradientColor="#1a1400"
          gradientOpacity={0.6}
        >
          <div className="flex gap-1 p-1">
            <AnimatedBackground
              defaultValue={language}
              onValueChange={(id) => {
                if (id === "tr" || id === "en") {
                  setLanguage(id)
                }
              }}
              className="rounded-xl border border-amber-500/20 bg-amber-500/[0.12]"
              transition={{ type: "spring", bounce: 0.12, duration: 0.45 }}
            >
              {LANGUAGE_OPTIONS.map((lang) => (
                <button
                  key={lang.id}
                  data-id={lang.id}
                  type="button"
                  aria-pressed={language === lang.id}
                  className={cn(
                    "flex flex-1 flex-col items-center gap-4 rounded-xl",
                    "px-6 py-10 sm:px-10 sm:py-12",
                    "cursor-pointer text-center select-none",
                    "transition-colors duration-200",
                    "text-[var(--color-text-secondary)]",
                    "data-[checked=true]:text-[var(--color-text-primary)]"
                  )}
                >
                  <span
                    className={cn(
                      "text-5xl leading-none sm:text-6xl",
                      "transition-transform duration-200",
                      "data-[checked=true]:scale-110"
                    )}
                    role="img"
                    aria-label={lang.id === "tr" ? "Turkish flag" : "English flag"}
                  >
                    {lang.emoji}
                  </span>

                  <span
                    className={cn(
                      "font-[family-name:var(--font-display)] font-semibold",
                      "text-xl leading-snug tracking-tight sm:text-2xl",
                      "transition-colors duration-200",
                      "data-[checked=true]:text-amber-300"
                    )}
                  >
                    {t(lang.titleKey)}
                  </span>

                  <span
                    className={cn(
                      "max-w-[14ch] text-sm leading-relaxed sm:max-w-[18ch]",
                      "font-light",
                      "opacity-70 transition-opacity duration-200",
                      "data-[checked=true]:opacity-100"
                    )}
                  >
                    {t(lang.descKey)}
                  </span>
                </button>
              ))}
            </AnimatedBackground>
          </div>
        </MagicCard>
      </BlurFade>
    </div>
  )
}
