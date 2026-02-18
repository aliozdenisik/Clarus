"use client"

import { useMemo, useState } from "react"
import { useTranslations } from "next-intl"

import { updatePreferencesApiPreferencesPut, type PreferencesUpdate } from "@/lib/api"
import { springPresets } from "@/lib/design-system"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"
import { TransitionPanel } from "@/components/motion-primitives/transition-panel"
import { WelcomeStep } from "@/components/onboarding/steps/welcome-step"
import { PurposeStep } from "@/components/onboarding/steps/purpose-step"
import { LanguageStep } from "@/components/onboarding/steps/language-step"
import { ArabicStep } from "@/components/onboarding/steps/arabic-step"
import { InterestsStep } from "@/components/onboarding/steps/interests-step"
import { CompletionStep } from "@/components/onboarding/steps/completion-step"

function buildPreferencesBody({
  currentStep,
  usagePurpose,
  language,
  arabicProficiency,
  interests,
}: {
  currentStep: number
  usagePurpose: string | null
  language: string
  arabicProficiency: string
  interests: string[]
}): PreferencesUpdate | null {
  switch (currentStep) {
    case 1:
      return { custom_settings: { usage_purpose: usagePurpose } }
    case 2:
      return { language }
    case 3:
      return { custom_settings: { arabic_proficiency: arabicProficiency } }
    case 4:
      return { custom_settings: { interests } }
    default:
      return null
  }
}

export default function OnboardingPage() {
  const t = useTranslations("Onboarding")
  const [isSaving, setIsSaving] = useState(false)

  const currentStep = useOnboardingStore((s) => s.currentStep)
  const direction = useOnboardingStore((s) => s.direction)
  const totalSteps = useOnboardingStore((s) => s.totalSteps)
  const goNext = useOnboardingStore((s) => s.goNext)
  const goBack = useOnboardingStore((s) => s.goBack)
  const usagePurpose = useOnboardingStore((s) => s.usagePurpose)
  const language = useOnboardingStore((s) => s.language)
  const arabicProficiency = useOnboardingStore((s) => s.arabicProficiency)
  const interests = useOnboardingStore((s) => s.interests)

  const steps = useMemo(
    () => [
      <WelcomeStep key="welcome" />,
      <PurposeStep key="purpose" />,
      <LanguageStep key="language" />,
      <ArabicStep key="arabic" />,
      <InterestsStep key="interests" />,
      <CompletionStep key="completion" />,
    ],
    []
  )

  const canGoBack = currentStep > 0
  const canGoNext = currentStep >= 1 && currentStep <= 4

  const handleNext = async () => {
    if (!canGoNext || isSaving) {
      return
    }

    const body = buildPreferencesBody({
      currentStep,
      usagePurpose,
      language,
      arabicProficiency,
      interests,
    })

    if (!body) {
      return
    }

    setIsSaving(true)
    try {
      await updatePreferencesApiPreferencesPut({ body })
      goNext()
    } catch {
      return
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-8 sm:px-6">
      <p className="text-center text-xs font-medium tracking-wide text-white/55 uppercase">
        {t("stepOf", { current: currentStep + 1, total: totalSteps })}
      </p>

      <div className="min-h-[420px]">
        <TransitionPanel
          activeIndex={currentStep}
          custom={direction}
          transition={springPresets.snappy}
          variants={{
            enter: (panelDirection: number) => ({
              x: panelDirection > 0 ? 364 : -364,
              opacity: 0,
              filter: "blur(4px)",
            }),
            center: { x: 0, opacity: 1, filter: "blur(0px)" },
            exit: (panelDirection: number) => ({
              x: panelDirection < 0 ? 364 : -364,
              opacity: 0,
              filter: "blur(4px)",
            }),
          }}
          className="w-full"
        >
          {steps}
        </TransitionPanel>
      </div>

      {(canGoBack || canGoNext) && (
        <div className="flex items-center justify-between gap-3">
          {canGoBack ? (
            <button
              type="button"
              aria-label={t("back")}
              onClick={goBack}
              className="inline-flex h-10 items-center rounded-lg border border-white/15 bg-white/[0.03] px-4 text-sm font-medium text-white/85 transition-colors hover:bg-white/[0.08] focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent focus-visible:outline-none"
            >
              {t("back")}
            </button>
          ) : (
            <span />
          )}

          {canGoNext ? (
            <button
              type="button"
              aria-label={t("next")}
              onClick={handleNext}
              disabled={isSaving}
              className="inline-flex h-10 items-center rounded-lg border border-amber-500/35 bg-amber-500/10 px-4 text-sm font-semibold text-amber-100 transition-colors hover:bg-amber-500/20 focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
            >
              {t("next")}
            </button>
          ) : (
            <span />
          )}
        </div>
      )}
    </div>
  )
}
