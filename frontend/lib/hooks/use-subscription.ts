"use client"

import { useQuery } from "@tanstack/react-query"
import { useSession } from "@/lib/auth-client"
import { API_BASE } from "@/lib/config"

interface SubscriptionStatus {
  tier: "free" | "starter" | "pro"
  limit: number
}

export function useSubscription() {
  const { data: session } = useSession()
  const userId = session?.user?.id

  const { data } = useQuery<SubscriptionStatus>({
    queryKey: ["subscription-status", userId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/api/subscription/status`, {
        headers: { "Content-Type": "application/json" },
      })
      if (!response.ok) {
        return { tier: "free" as const, limit: 5 }
      }
      return response.json() as Promise<SubscriptionStatus>
    },
    enabled: !!userId,
    staleTime: 5 * 60 * 1000,
    retry: false,
  })

  const tier = data?.tier ?? "free"
  const limit = data?.limit ?? 5
  const isPaid = tier === "starter" || tier === "pro"
  const isStarter = tier === "starter"
  const isPro = tier === "pro"

  return { tier, limit, isPaid, isStarter, isPro }
}
