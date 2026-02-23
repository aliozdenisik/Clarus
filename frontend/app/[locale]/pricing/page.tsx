"use client"

import { useState } from "react"
import { useRouter } from "@/i18n/navigation"
import { useSession, authClient } from "@/lib/auth-client"
import { useTranslations } from "next-intl"
import { logger } from "@/lib/logger"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Check, CreditCard } from "lucide-react"
import { cn } from "@/lib/utils"

export default function PricingPage() {
  const { data: session, isPending: authLoading } = useSession()
  const isLoggedIn = !!session?.user
  const router = useRouter()
  const t = useTranslations("Pricing")

  const [checkoutLoading, setCheckoutLoading] = useState(false)
  const [starterCheckoutLoading, setStarterCheckoutLoading] = useState(false)
  const [portalLoading, setPortalLoading] = useState(false)

  const handleCheckout = async () => {
    if (!isLoggedIn) {
      router.push("/sign-in")
      return
    }
    try {
      setCheckoutLoading(true)
      await authClient.checkout({ slug: "pro" })
    } catch (error) {
      logger.error("Checkout failed", { error })
    } finally {
      setCheckoutLoading(false)
    }
  }

  const handleStarterCheckout = async () => {
    if (!isLoggedIn) {
      router.push("/sign-in")
      return
    }
    try {
      setStarterCheckoutLoading(true)
      await authClient.checkout({ slug: "starter" })
    } catch (error) {
      logger.error("Starter checkout failed", { error })
    } finally {
      setStarterCheckoutLoading(false)
    }
  }

  const handlePortal = async () => {
    try {
      setPortalLoading(true)
      await authClient.customer.portal()
    } catch (error) {
      logger.error("Portal failed", { error })
    } finally {
      setPortalLoading(false)
    }
  }

  const freeFeatures = [
    t("freeFeature1"),
    t("freeFeature2"),
    t("freeFeature3"),
    t("freeFeature4"),
    t("freeFeature5"),
  ] as const

  const starterFeatures = [
    t("starterFeature1"),
    t("starterFeature2"),
    t("starterFeature3"),
    t("starterFeature4"),
  ] as const

  const proFeatures = [t("proFeature1"), t("proFeature2"), t("proFeature3")] as const

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-zinc-400">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg-app)] px-4 py-16">
      <div className="mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-white">{t("title")}</h1>
          <p className="mt-3 text-lg text-zinc-400">{t("subtitle")}</p>
        </div>

        {/* Plan Cards */}
        <div className="grid gap-8 md:grid-cols-3">
          {/* Free Plan Card */}
          <Card className="border-zinc-800 bg-zinc-900/50">
            <CardHeader>
              <CardTitle className="text-xl text-white">{t("freePlan")}</CardTitle>
              <CardDescription className="text-zinc-400">
                <span className="text-3xl font-bold text-white">{t("freePrice")}</span>
              </CardDescription>
            </CardHeader>

            <CardContent>
              <ul className="space-y-3">
                {freeFeatures.map((feature) => (
                  <li key={feature} className="flex items-center gap-3 text-zinc-300">
                    <Check className="h-4 w-4 shrink-0 text-green-500" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>

            <CardFooter>
              <Button variant="outline" disabled className="w-full border-zinc-700 text-zinc-400">
                {t("currentPlan")}
              </Button>
            </CardFooter>
          </Card>

          {/* Starter Plan Card */}
          <Card className={cn("relative border-indigo-500/50 bg-zinc-900/50")}>
            {/* Popular badge at top */}
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
              <Badge className="border-indigo-500/50 bg-indigo-600 text-white">
                {t("popular")}
              </Badge>
            </div>

            <CardHeader>
              <CardTitle className="text-xl text-white">{t("starterPlan")}</CardTitle>
              <CardDescription className="text-zinc-400">
                <span className="text-3xl font-bold text-white">{t("starterPrice")}</span>
                <span className="ml-1 text-base text-zinc-400">{t("perMonth")}</span>
              </CardDescription>
            </CardHeader>

            <CardContent>
              <ul className="space-y-3">
                {starterFeatures.map((feature) => (
                  <li key={feature} className="flex items-center gap-3 text-zinc-300">
                    <Check className="h-4 w-4 shrink-0 text-green-500" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>

            <CardFooter className="flex flex-col gap-3">
              {!isLoggedIn ? (
                <div className="w-full space-y-3">
                  <p className="text-center text-sm text-zinc-400">{t("loginRequired")}</p>
                  <Button
                    onClick={() => router.push("/sign-in")}
                    className="w-full bg-indigo-600 text-white hover:bg-indigo-700"
                  >
                    {t("upgradeToStarter")}
                  </Button>
                </div>
              ) : (
                <>
                  <Button
                    onClick={handleStarterCheckout}
                    disabled={starterCheckoutLoading}
                    className="w-full bg-indigo-600 text-white hover:bg-indigo-700"
                  >
                    <CreditCard className="mr-2 h-4 w-4" />
                    {starterCheckoutLoading ? "..." : t("upgradeToStarter")}
                  </Button>
                  <button
                    type="button"
                    onClick={handlePortal}
                    disabled={portalLoading}
                    className="w-full text-center text-sm text-zinc-400 underline-offset-4 hover:text-zinc-300 hover:underline disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {portalLoading ? "..." : t("manageBilling")}
                  </button>
                </>
              )}
            </CardFooter>
          </Card>

          {/* Pro Plan Card */}
          <Card className="border-zinc-800 bg-zinc-900/50">
            <CardHeader>
              <CardTitle className="text-xl text-white">{t("proPlan")}</CardTitle>
              <CardDescription className="text-zinc-400">
                <span className="text-3xl font-bold text-white">{t("proPrice")}</span>
                <span className="ml-1 text-base text-zinc-400">{t("perMonth")}</span>
              </CardDescription>
            </CardHeader>

            <CardContent>
              <ul className="space-y-3">
                {proFeatures.map((feature) => (
                  <li key={feature} className="flex items-center gap-3 text-zinc-300">
                    <Check className="h-4 w-4 shrink-0 text-green-500" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>

            <CardFooter className="flex flex-col gap-3">
              {!isLoggedIn ? (
                <div className="w-full space-y-3">
                  <p className="text-center text-sm text-zinc-400">{t("loginRequired")}</p>
                  <Button
                    onClick={() => router.push("/sign-in")}
                    className="w-full bg-zinc-100 text-zinc-900 hover:bg-zinc-200"
                  >
                    {t("upgrade")}
                  </Button>
                </div>
              ) : (
                <>
                  <Button
                    onClick={handleCheckout}
                    disabled={checkoutLoading}
                    className="w-full bg-zinc-100 text-zinc-900 hover:bg-zinc-200"
                  >
                    <CreditCard className="mr-2 h-4 w-4" />
                    {checkoutLoading ? "..." : t("upgrade")}
                  </Button>
                  <button
                    type="button"
                    onClick={handlePortal}
                    disabled={portalLoading}
                    className="w-full text-center text-sm text-zinc-400 underline-offset-4 hover:text-zinc-300 hover:underline disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {portalLoading ? "..." : t("manageBilling")}
                  </button>
                </>
              )}
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  )
}
