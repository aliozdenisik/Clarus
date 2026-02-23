"use client"

import { Lock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useRouter } from "@/i18n/navigation"
import { useTranslations } from "next-intl"
import { cn } from "@/lib/utils"

interface UpgradeGateProps {
  locked: boolean
  children: React.ReactNode
  className?: string
}

export function UpgradeGate({ locked, children, className }: UpgradeGateProps) {
  const router = useRouter()
  const t = useTranslations("Pricing")

  if (!locked) {
    return <>{children}</>
  }

  return (
    <div className={cn("relative", className)}>
      <div className="pointer-events-none blur-sm select-none" aria-hidden="true">
        {children}
      </div>
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 rounded-lg bg-zinc-950/60 backdrop-blur-[2px]">
        <Lock className="size-5 text-zinc-400" />
        <Button
          variant="secondary"
          size="sm"
          onClick={() => router.push("/pricing")}
          className="gap-1.5"
        >
          {t("upgradePrompt")}
        </Button>
      </div>
    </div>
  )
}
