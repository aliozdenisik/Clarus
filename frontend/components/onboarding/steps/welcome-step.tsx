"use client"

import Image from "next/image"
import { useTranslations } from "next-intl"

import { cn } from "@/lib/utils"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"
import { BlurFade } from "@/components/ui/blur-fade"
import { TextAnimate } from "@/components/ui/text-animate"
import { ShimmerButton } from "@/components/ui/shimmer-button"

export function WelcomeStep() {
  const t = useTranslations("Onboarding")
  const goNext = useOnboardingStore((s) => s.goNext)

  return (
    <div className="flex min-h-full flex-col items-center justify-center px-6 py-12 text-center">
      <BlurFade delay={0} duration={0.6} className="mb-10">
        <div className="relative mx-auto w-fit">
          <div className="absolute inset-0 scale-150 rounded-full bg-[var(--color-accent-primary)] opacity-15 blur-3xl" />
          <Image
            src="/logo-dark-nobg.png"
            alt="Clarus"
            width={88}
            height={88}
            className="relative opacity-90"
            priority
          />
        </div>
      </BlurFade>

      <TextAnimate
        by="word"
        animation="blurInUp"
        startOnView={false}
        once
        delay={0.15}
        duration={0.6}
        className={cn(
          "mb-4 font-[family-name:var(--font-display)] leading-tight font-semibold tracking-[-0.02em]",
          "text-3xl sm:text-4xl lg:text-5xl",
          "text-[var(--color-text-primary)]"
        )}
      >
        {t("welcome.title")}
      </TextAnimate>

      <BlurFade delay={0.45} duration={0.5} className="mb-3">
        <p
          className={cn(
            "font-[family-name:var(--font-display)] font-medium tracking-wide",
            "text-lg sm:text-xl lg:text-2xl",
            "text-amber-400"
          )}
        >
          {t("welcome.subtitle")}
        </p>
      </BlurFade>

      <BlurFade delay={0.6} duration={0.5} className="mb-10">
        <p
          className={cn(
            "mx-auto max-w-sm leading-relaxed font-light",
            "text-base sm:text-lg",
            "text-[var(--color-text-secondary)]"
          )}
        >
          {t("welcome.description")}
        </p>
      </BlurFade>

      <BlurFade delay={0.75} duration={0.5}>
        <ShimmerButton
          onClick={goNext}
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
          {t("welcome.cta")}
        </ShimmerButton>
      </BlurFade>
    </div>
  )
}
