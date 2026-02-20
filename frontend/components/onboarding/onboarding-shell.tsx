"use client"

import { motion } from "motion/react"
import { useTranslations } from "next-intl"
import { useRouter } from "@/i18n/navigation"
import { springPresets } from "@/lib/design-system"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"
import { usePreferencesStore } from "@/lib/stores/preferences-store"
import { updatePreferencesApiPreferencesPut } from "@/lib/api"
import { logger } from "@/lib/logger"
import { cn } from "@/lib/utils"

/**
 * OnboardingShell
 *
 * Client component that wraps onboarding flow with:
 * - Animated progress bar (top)
 * - Clarus logo (top left)
 * - "Skip setup" link (top right)
 * - Centered content container for onboarding steps
 */
export default function OnboardingShell({ children }: { children: React.ReactNode }) {
  const t = useTranslations("Onboarding")
  const router = useRouter()
  const currentStep = useOnboardingStore((s) => s.currentStep)
  const totalSteps = useOnboardingStore((s) => s.totalSteps)

  const progressPercent = ((currentStep + 1) / totalSteps) * 100

  const setOnboardingCompleted = usePreferencesStore((s) => s.setOnboardingCompleted)

  const handleSkipSetup = async () => {
    try {
      await updatePreferencesApiPreferencesPut({
        body: {
          custom_settings: {
            onboarding_completed: true,
          },
        },
      })
    } catch (error) {
      logger.error("Failed to skip onboarding", { error })
    }
    setOnboardingCompleted(true)
    router.push("/hub" as Parameters<typeof router.push>[0])
  }

  return (
    <div className="flex min-h-screen flex-col">
      {/* Top bar: Logo + Progress + Skip link */}
      <div className="relative z-20 border-b border-white/10 bg-[var(--color-bg-app)]/80 backdrop-blur-sm">
        <div className="flex items-center justify-between px-6 py-4 sm:px-8">
          {/* Logo */}
          <div className="flex items-center">
            <span className="text-lg font-bold text-white">Clarus</span>
          </div>

          {/* Progress bar */}
          <div className="mx-8 h-1 flex-1 overflow-hidden rounded-full bg-white/10">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-purple-500 to-blue-500"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercent}%` }}
              transition={springPresets.snappy}
            />
          </div>

          {/* Skip link */}
          <button
            type="button"
            onClick={handleSkipSetup}
            className={cn(
              "text-sm font-medium whitespace-nowrap",
              "text-white/60 hover:text-white",
              "transition-colors duration-200",
              "focus-visible:ring-2 focus-visible:ring-purple-500 focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg-app)] focus-visible:outline-none"
            )}
          >
            {t("skipSetup")}
          </button>
        </div>
      </div>

      {/* Content container */}
      <div className="flex flex-1 items-center justify-center px-4 py-8 sm:px-8">
        <div className="w-full max-w-2xl">{children}</div>
      </div>
    </div>
  )
}
