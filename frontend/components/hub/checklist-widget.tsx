"use client"

import { useEffect } from "react"
import { useTranslations } from "next-intl"
import { CheckCircle2, Circle, ChevronRight } from "lucide-react"

import { useRouter } from "@/i18n/navigation"
import { useChecklistStore, useChecklistProgress } from "@/lib/stores/checklist-store"
import { BlurFade } from "@/components/ui/blur-fade"
import { MagicCard } from "@/components/ui/magic-card"
import { cn } from "@/lib/utils"

const ITEM_ROUTES: Record<string, string> = {
  "first-search": "/search",
  "try-compare": "/compare",
  "keyword-search": "/keyword-search",
  "browse-quran": "/quran",
  "view-history": "/history",
}

const ITEM_LABEL_KEYS: Record<string, string> = {
  "first-search": "firstSearch",
  "try-compare": "tryCompare",
  "keyword-search": "keywordSearch",
  "browse-quran": "browseQuran",
  "view-history": "viewHistory",
}

export function ChecklistWidget() {
  const tHub = useTranslations("Hub")
  const tChecklist = useTranslations("Checklist")
  const router = useRouter()

  const items = useChecklistStore((s) => s.items)
  const dismissed = useChecklistStore((s) => s.dismissed)
  const dismissChecklist = useChecklistStore((s) => s.dismissChecklist)

  const { completed, total, percentage } = useChecklistProgress()
  const allComplete = completed === total

  useEffect(() => {
    if (!allComplete) return
    const timer = setTimeout(() => dismissChecklist(), 3000)
    return () => clearTimeout(timer)
  }, [allComplete, dismissChecklist])

  if (dismissed) return null

  return (
    <div className="relative overflow-hidden rounded-xl border border-[var(--hub-border)]">
      <MagicCard
        className="rounded-xl"
        gradientSize={220}
        gradientColor="#0a0a1a"
        gradientFrom="#6366f1"
        gradientTo="#312e81"
        gradientOpacity={0.12}
      >
        <div className="space-y-3 p-4">
          <div className="flex items-center justify-between gap-2">
            <span className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
              {tHub("gettingStarted")}
            </span>
            <span className="text-muted-foreground font-mono text-xs">
              {tHub("progress", { completed, total })}
            </span>
          </div>

          <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
            <div
              className={cn(
                "h-full rounded-full transition-all duration-500 ease-out",
                allComplete ? "bg-emerald-500" : "bg-indigo-500"
              )}
              style={{ width: `${percentage}%` }}
            />
          </div>

          {allComplete ? (
            <BlurFade delay={0} duration={0.5}>
              <div className="space-y-1 py-3 text-center">
                <p className="text-sm font-medium text-emerald-400">{tChecklist("allComplete")}</p>
                <p className="text-muted-foreground text-xs">{tChecklist("allCompleteDesc")}</p>
              </div>
            </BlurFade>
          ) : (
            <div className="space-y-0.5">
              {items.map((item, index) => {
                const labelKey = ITEM_LABEL_KEYS[item.id]
                const route = ITEM_ROUTES[item.id]
                const label = labelKey
                  ? tChecklist(labelKey as Parameters<typeof tChecklist>[0])
                  : item.id

                if (item.completed) {
                  return (
                    <BlurFade key={item.id} delay={index * 0.05}>
                      <div className="flex items-center gap-2.5 rounded-md px-1 py-1.5">
                        <CheckCircle2 className="size-4 shrink-0 text-emerald-500" />
                        <span className="text-muted-foreground text-sm line-through">{label}</span>
                      </div>
                    </BlurFade>
                  )
                }

                return (
                  <BlurFade key={item.id} delay={index * 0.05}>
                    <button
                      type="button"
                      onClick={() => router.push(route as Parameters<typeof router.push>[0])}
                      className={cn(
                        "group flex w-full items-center gap-2.5 rounded-md px-1 py-1.5",
                        "text-left transition-colors duration-150",
                        "cursor-pointer hover:bg-white/[0.04]"
                      )}
                    >
                      <Circle className="text-muted-foreground size-4 shrink-0" />
                      <span className="text-foreground/80 group-hover:text-foreground flex-1 text-sm transition-colors duration-150">
                        {label}
                      </span>
                      <ChevronRight className="text-muted-foreground size-3.5 shrink-0 opacity-0 transition-opacity duration-150 group-hover:opacity-100" />
                    </button>
                  </BlurFade>
                )
              })}
            </div>
          )}

          {!allComplete && (
            <div className="flex justify-end pt-1">
              <button
                type="button"
                onClick={dismissChecklist}
                className="text-muted-foreground hover:text-foreground cursor-pointer text-xs transition-colors duration-150"
              >
                {tChecklist("dismiss")}
              </button>
            </div>
          )}
        </div>
      </MagicCard>
    </div>
  )
}
