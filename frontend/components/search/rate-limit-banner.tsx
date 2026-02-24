"use client"

import { motion } from "framer-motion"
import { ShieldAlert } from "lucide-react"
import { useTranslations } from "next-intl"
import { Button } from "@/components/ui/button"
import { useRouter } from "@/i18n/navigation"
import { springPresets } from "@/lib/design-system"
import { cn } from "@/lib/utils"

interface RateLimitBannerProps {
  className?: string
}

export function RateLimitBanner({ className }: RateLimitBannerProps) {
  const t = useTranslations("RateLimit")
  const router = useRouter()

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...springPresets.gentle, duration: 0.45 }}
      className={cn(
        "mb-8 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/90 p-6 backdrop-blur-sm md:p-7",
        className
      )}
    >
      <div className="flex items-start gap-4">
        <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-indigo-400/35 bg-indigo-500/15 text-indigo-200">
          <ShieldAlert className="h-5 w-5" />
        </div>

        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">{t("title")}</h3>
          <p className="mt-2 text-sm leading-relaxed text-[var(--color-text-secondary)]">
            {t("description")}
          </p>
          <p className="mt-2 text-xs text-[var(--color-text-muted)]">{t("resetInfo")}</p>

          <Button
            onClick={() => router.push("/pricing")}
            className="mt-4 bg-gradient-to-r from-indigo-500 to-violet-500 text-white hover:from-indigo-600 hover:to-violet-600"
          >
            {t("upgradeButton")}
          </Button>
        </div>
      </div>
    </motion.div>
  )
}
