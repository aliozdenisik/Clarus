import type { Metadata } from "next"
import { getTranslations } from "next-intl/server"
import { buildPageMetadata } from "@/lib/seo"

interface Props {
  children: React.ReactNode
  params: Promise<{ locale: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: "Metadata" })
  return buildPageMetadata({
    locale,
    path: "/keyword-search",
    title: t("keywordSearchTitle"),
    description: t("keywordSearchDescription"),
  })
}

export default function KeywordSearchLayout({ children }: Props) {
  return children
}
