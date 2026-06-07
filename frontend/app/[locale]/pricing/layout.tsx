import type { Metadata } from "next"
import { getTranslations } from "next-intl/server"
import { buildPageMetadata } from "@/lib/seo"

type Props = {
  children: React.ReactNode
  params: Promise<{ locale: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: "Metadata" })
  return buildPageMetadata({
    locale,
    path: "/pricing",
    title: t("pricingTitle"),
    description: t("pricingDescription"),
  })
}

export default function PricingLayout({ children }: Props) {
  return children
}
