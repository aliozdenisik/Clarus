"use client"

import { useTranslations } from "next-intl"
import { useRouter } from "@/i18n/navigation"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CheckCircle, ArrowLeft } from "lucide-react"

export default function BillingSuccessPage() {
  const t = useTranslations("Pricing")
  const router = useRouter()

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)] px-4">
      <Card className="w-full max-w-md border-zinc-800 bg-zinc-900/50 text-center">
        <CardHeader>
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-500/10">
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
          <CardTitle className="text-2xl text-white">{t("checkoutSuccess")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-zinc-400">{t("checkoutSuccessDesc")}</p>
        </CardContent>
        <CardFooter className="justify-center">
          <Button variant="outline" onClick={() => router.push("/search")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            {t("backToSearch")}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
