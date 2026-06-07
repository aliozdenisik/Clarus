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
    path: "/old-testament",
    title: t("oldTestamentTitle"),
    description: t("oldTestamentDescription"),
  })
}

export default function OldTestamentLayout({ children }: Props) {
  return children
}
