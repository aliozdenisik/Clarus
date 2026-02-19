import { headers } from "next/headers"
import { redirect } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { auth } from "@/lib/auth"
import { getDailyVerse } from "@/lib/daily-verse"
import { BlurFade } from "@/components/ui/blur-fade"
import { DailyVerseWidget } from "@/components/hub/daily-verse-widget"
import { ChecklistWidget } from "@/components/hub/checklist-widget"
import { RecentSearchesWidget } from "@/components/hub/recent-searches-widget"
import { SuggestionsWidget } from "@/components/hub/suggestions-widget"

export default async function HubPage() {
  const session = await auth.api.getSession({ headers: await headers() })
  if (!session) {
    redirect("/")
  }

  const t = await getTranslations("Hub")
  const dailyVerse = getDailyVerse()

  const hour = new Date().getHours()
  let greeting: string
  if (hour < 12) {
    greeting = t("greeting.morning")
  } else if (hour < 18) {
    greeting = t("greeting.afternoon")
  } else {
    greeting = t("greeting.evening")
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-8 md:py-12">
      <BlurFade delay={0}>
        <div className="mb-8">
          <h1 className="font-serif text-3xl md:text-4xl">{greeting}</h1>
          <p className="text-muted-foreground mt-2 text-xs">{t("cmdkHint", { shortcut: "⌘K" })}</p>
        </div>
      </BlurFade>

      <BlurFade delay={0.1}>
        <DailyVerseWidget verse={dailyVerse} />
      </BlurFade>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        <BlurFade delay={0.2}>
          <ChecklistWidget />
        </BlurFade>
        <BlurFade delay={0.25}>
          <RecentSearchesWidget />
        </BlurFade>
      </div>

      <BlurFade delay={0.3}>
        <div className="mt-6">
          <SuggestionsWidget />
        </div>
      </BlurFade>
    </div>
  )
}
