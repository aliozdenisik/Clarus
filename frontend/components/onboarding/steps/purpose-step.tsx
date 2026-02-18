"use client"

import { GraduationCap, BookOpen, Mic, GitCompare, FileText } from "lucide-react"
import { useTranslations } from "next-intl"
import type { LucideIcon } from "lucide-react"

import { AnimatedBackground } from "@/components/motion-primitives/animated-background"
import { MagicCard } from "@/components/ui/magic-card"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"

type PurposeKey = "academic" | "personal" | "preaching" | "comparative" | "textual"

interface PurposeOption {
  id: PurposeKey
  icon: LucideIcon
}

const PURPOSES: PurposeOption[] = [
  { id: "academic", icon: GraduationCap },
  { id: "personal", icon: BookOpen },
  { id: "preaching", icon: Mic },
  { id: "comparative", icon: GitCompare },
  { id: "textual", icon: FileText },
]

export function PurposeStep() {
  const t = useTranslations("Onboarding")
  const usagePurpose = useOnboardingStore((s) => s.usagePurpose)
  const setUsagePurpose = useOnboardingStore((s) => s.setUsagePurpose)

  const purposeData: Record<PurposeKey, { title: string; desc: string }> = {
    academic: {
      title: t("purpose.academic"),
      desc: t("purpose.academicDesc"),
    },
    personal: {
      title: t("purpose.personal"),
      desc: t("purpose.personalDesc"),
    },
    preaching: {
      title: t("purpose.preaching"),
      desc: t("purpose.preachingDesc"),
    },
    comparative: {
      title: t("purpose.comparative"),
      desc: t("purpose.comparativeDesc"),
    },
    textual: {
      title: t("purpose.textual"),
      desc: t("purpose.textualDesc"),
    },
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-white">{t("purpose.title")}</h2>
        <p className="mt-2 text-sm text-white/60">{t("purpose.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <AnimatedBackground
          defaultValue={usagePurpose ?? undefined}
          onValueChange={(id) => {
            if (id) setUsagePurpose(id)
          }}
          className="rounded-xl bg-gradient-to-br from-purple-500/80 to-blue-500/70"
          transition={{ type: "spring", bounce: 0.2, duration: 0.5 }}
        >
          {PURPOSES.map(({ id, icon: Icon }) => (
            <div
              key={id}
              data-id={id}
              /**
               * `block w-full` overrides AnimatedBackground's injected `inline-flex`,
               * making each card a proper full-width grid item.
               * `p-px` creates a 1-px gap so the AnimatedBackground sliding highlight
               * is visible as a gradient border around the MagicCard.
               */
              className="block w-full cursor-pointer rounded-xl p-px"
            >
              <MagicCard className="rounded-[11px] p-5" gradientColor="rgba(124, 58, 237, 0.25)">
                <div className="flex flex-col gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/10">
                    <Icon className="h-5 w-5 text-white/80" aria-hidden="true" />
                  </div>

                  <div className="space-y-1">
                    <h3 className="text-sm font-semibold text-white">{purposeData[id].title}</h3>
                    <p className="text-xs leading-relaxed text-white/60">{purposeData[id].desc}</p>
                  </div>
                </div>
              </MagicCard>
            </div>
          ))}
        </AnimatedBackground>
      </div>
    </div>
  )
}
