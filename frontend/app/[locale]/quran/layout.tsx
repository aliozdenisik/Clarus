import type { Metadata } from "next"
import { getTranslations } from "next-intl/server"
import { buildPageMetadata, type Locale } from "@/lib/seo"

interface Props {
  children: React.ReactNode
  params: Promise<{ locale: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: "Metadata" })
  return buildPageMetadata({
    locale: locale as Locale,
    path: "/quran",
    title: t("quranTitle"),
    description: t("quranDescription"),
  })
}

export default function QuranLayout({ children }: Props) {
  return children
}
