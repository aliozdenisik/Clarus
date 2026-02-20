"use client"

import React, { useEffect, useState } from "react"
import { useSession } from "@/lib/auth-client"
import { usePreferencesStore } from "@/lib/stores/preferences-store"
import { useRouter, usePathname } from "@/i18n/navigation"

export function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const { data: session, isPending } = useSession()
  const onboarding_completed = usePreferencesStore((s) => s.onboarding_completed)
  const storeError = usePreferencesStore((s) => s.error)
  const fetchPreferences = usePreferencesStore((s) => s.fetchPreferences)
  const router = useRouter()
  const pathname = usePathname()

  const userId = session?.user?.id ?? null
  const [prefetchedUserId, setPrefetchedUserId] = useState<string | null>(null)
  const prefetchDone = userId !== null && prefetchedUserId === userId

  useEffect(() => {
    if (!userId || prefetchedUserId === userId) return
    const currentUserId = userId
    void fetchPreferences().finally(() => {
      setPrefetchedUserId(currentUserId)
    })
  }, [userId, prefetchedUserId, fetchPreferences])

  useEffect(() => {
    if (isPending || !session || !prefetchDone || storeError) return

    const isOnboardingRoute = pathname.includes("/onboarding")
    const isAuthRoute =
      pathname.includes("/sign-in") ||
      pathname.includes("/sign-up") ||
      pathname.includes("/login") ||
      pathname.includes("/register")

    if (!onboarding_completed && !isOnboardingRoute && !isAuthRoute) {
      router.push("/onboarding")
    } else if (onboarding_completed && isOnboardingRoute) {
      router.push("/hub" as Parameters<typeof router.push>[0])
    }
  }, [onboarding_completed, isPending, session, prefetchDone, storeError, pathname, router])

  return <>{children}</>
}
