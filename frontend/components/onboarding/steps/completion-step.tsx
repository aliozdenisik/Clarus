"use client"

import { useEffect, useRef } from "react"
import { useTranslations } from "next-intl"

import { cn } from "@/lib/utils"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"
import { useRouter } from "@/i18n/navigation"
import { Confetti, type ConfettiRef } from "@/components/ui/confetti"
import { NumberTicker } from "@/components/ui/number-ticker"
import { BlurFade } from "@/components/ui/blur-fade"
import { MagicCard } from "@/components/ui/magic-card"
import { ShimmerButton } from "@/components/ui/shimmer-button"

const PURPOSE_KEYS = ["academic", "personal", "preaching", "comparative", "textual"] as const
type PurposeKey = (typeof PURPOSE_KEYS)[number]

const ARABIC_PROFICIENCY_KEYS = ["none", "basic", "intermediate", "advanced"] as const
type ArabicProficiencyKey = (typeof ARABIC_PROFICIENCY_KEYS)[number]

const LANGUAGE_KEY_MAP: Record<string, "turkish" | "english"> = {
  tr: "turkish",
  en: "english",
}

function isPurposeKey(value: string): value is PurposeKey {
  return (PURPOSE_KEYS as readonly string[]).includes(value)
}

function isArabicProficiencyKey(value: string): value is ArabicProficiencyKey {
  return (ARABIC_PROFICIENCY_KEYS as readonly string[]).includes(value)
}

export function CompletionStep() {
  const t = useTranslations("Onboarding")
  const router = useRouter()

  const usagePurpose = useOnboardingStore((s) => s.usagePurpose)
  const language = useOnboardingStore((s) => s.language)
  const arabicProficiency = useOnboardingStore((s) => s.arabicProficiency)
  const interests = useOnboardingStore((s) => s.interests)
  const markComplete = useOnboardingStore((s) => s.markComplete)

  const confettiRef = useRef<ConfettiRef>(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      confettiRef.current?.fire({
        particleCount: 90,
        spread: 65,
        origin: { y: 0.55 },
        colors: ["#f59e0b", "#d97706", "#fbbf24", "#fcd34d", "#fffbeb"],
        gravity: 0.85,
        scalar: 0.9,
        drift: 0,
        startVelocity: 28,
        ticks: 200,
      })
    }, 350)
    return () => clearTimeout(timer)
  }, [])

  const handleGoHome = () => {
    markComplete()
    router.push("/")
  }

  const purposeLabel =
    usagePurpose && isPurposeKey(usagePurpose)
      ? t(`purpose.${usagePurpose}` as `purpose.${PurposeKey}`)
      : "—"

  const languageKey = LANGUAGE_KEY_MAP[language] ?? "english"
  const languageLabel = t(`language.${languageKey}` as `language.${"turkish" | "english"}`)

  const arabicLabel = isArabicProficiencyKey(arabicProficiency)
    ? t(`arabic.${arabicProficiency}` as `arabic.${ArabicProficiencyKey}`)
    : "—"

  const summaryRows: { label: string; value: string }[] = [
    { label: t("purpose.title"), value: purposeLabel },
    { label: t("language.title"), value: languageLabel },
    { label: t("arabic.title"), value: arabicLabel },
    { label: t("interests.title"), value: String(interests.length) },
  ]

  return (
    <div className="relative flex min-h-full flex-col items-center justify-center px-6 py-10 text-center">
      <Confetti
        ref={confettiRef}
        manualstart
        className="pointer-events-none fixed inset-0 z-50 h-full w-full"
      />

      <BlurFade delay={0} duration={0.6} className="mb-3">
        <h2
          className={cn(
            "font-[family-name:var(--font-display)] leading-tight font-semibold tracking-[-0.02em]",
            "text-3xl sm:text-4xl lg:text-5xl",
            "text-[var(--color-text-primary)]"
          )}
        >
          {t("completion.title")}
        </h2>
      </BlurFade>

      <BlurFade delay={0.15} duration={0.5} className="mb-8">
        <p
          className={cn(
            "leading-relaxed font-light",
            "text-base sm:text-lg",
            "text-[var(--color-text-secondary)]"
          )}
        >
          {t("completion.subtitle")}
        </p>
      </BlurFade>

      <BlurFade delay={0.28} duration={0.5} className="mb-8">
        <div className="flex flex-col items-center gap-1.5">
          <NumberTicker
            value={43055}
            className={cn(
              "font-[family-name:var(--font-display)] font-bold tabular-nums",
              "text-4xl sm:text-5xl",
              "text-amber-400"
            )}
          />
          <p className="text-sm font-light text-[var(--color-text-secondary)]">
            {t("completion.versesReady")}
          </p>
        </div>
      </BlurFade>

      <BlurFade delay={0.42} duration={0.5} className="mb-8 w-full max-w-sm">
        <div className="relative overflow-hidden rounded-xl border border-[var(--color-border-subtle)]">
          <MagicCard
            className="rounded-xl bg-[var(--color-bg-surface)]/80 backdrop-blur-sm"
            gradientSize={180}
            gradientColor="#1c1400"
            gradientFrom="#d97706"
            gradientTo="#92400e"
            gradientOpacity={0.15}
          >
            <div className="space-y-0 divide-y divide-[var(--color-border-subtle)]">
              {summaryRows.map(({ label, value }) => (
                <div key={label} className="flex items-center justify-between gap-4 px-5 py-3">
                  <span className="shrink-0 text-xs font-medium tracking-widest text-[var(--color-text-tertiary)] uppercase">
                    {label}
                  </span>
                  <span className="truncate text-right text-sm font-medium text-[var(--color-text-primary)]">
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </MagicCard>
        </div>
      </BlurFade>

      <BlurFade delay={0.56} duration={0.5}>
        <ShimmerButton
          onClick={handleGoHome}
          background="rgba(180, 120, 0, 0.15)"
          shimmerColor="#f59e0b"
          shimmerDuration="2.5s"
          borderRadius="12px"
          className={cn(
            "px-8 py-3 text-base font-medium",
            "border-amber-500/40 text-amber-100",
            "hover:border-amber-400/60"
          )}
        >
          {t("completion.goHome")}
        </ShimmerButton>
      </BlurFade>
    </div>
  )
}
