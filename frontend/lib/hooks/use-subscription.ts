"use client"

import { useQuery } from "@tanstack/react-query"
import { useSession } from "@/lib/auth-client"
import { getSubscriptionStatusApiSubscriptionStatusGet } from "@/lib/api/sdk.gen"

export function useSubscription() {
  const { data: session } = useSession()
  const userId = session?.user?.id

  const { data } = useQuery({
    queryKey: ["subscription-status", userId],
    queryFn: async () => {
      try {
        const response = await getSubscriptionStatusApiSubscriptionStatusGet()
        return response.data as { tier: "free" | "starter" | "pro"; limit: number }
      } catch {
        return { tier: "free" as const, limit: 5 }
      }
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
