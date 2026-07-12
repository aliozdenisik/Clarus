import type { Metadata } from "next"
import { NextIntlClientProvider } from "next-intl"
import { getMessages, getTranslations } from "next-intl/server"
import { notFound } from "next/navigation"
import { routing } from "@/i18n/routing"
import { Providers } from "@/components/providers"
import { Toaster } from "sonner"
import { LayoutChrome, LayoutFooter } from "@/components/layout/layout-chrome"
import { CommandPalette } from "@/components/command-palette"
import { SkipToContent } from "@/components/layout/skip-to-content"
import { LocaleSetter } from "@/components/layout/locale-setter"
import { buildAlternates, getBaseUrl, ogLocale, siteConfig, type Locale } from "@/lib/seo"

type Props = {
  children: React.ReactNode
  params: Promise<{ locale: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: "Metadata" })
  const baseUrl = getBaseUrl()
  const title = t("title")
  const description = t("description")
  const keywords = t("keywords")
    .split(",")
    .map((k) => k.trim())
    .filter(Boolean)
  const alternateLocale = routing.locales
    .filter((l) => l !== locale)
    .map((l) => ogLocale(l))

  return {
    title: {
      default: title,
      template: `%s | ${siteConfig.name}`,
    },
    description,
    keywords: keywords.length ? keywords : undefined,
    alternates: buildAlternates(locale as Locale, ""),
    openGraph: {
      title,
      description,
      siteName: siteConfig.name,
      locale: ogLocale(locale),
      alternateLocale,
      type: "website",
      url: `${baseUrl}/${locale}`,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
  }
}

export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params

  if (!routing.locales.includes(locale as never)) {
    notFound()
  }

  const messages = await getMessages()
  const t = await getTranslations({ locale, namespace: "Metadata" })
  const baseUrl = getBaseUrl()

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebSite",
        "@id": `${baseUrl}/#website`,
        name: siteConfig.name,
        url: `${baseUrl}/${locale}`,
        description: t("description"),
        inLanguage: locale,
        publisher: { "@id": `${baseUrl}/#organization` },
      },
      {
        "@type": "Organization",
        "@id": `${baseUrl}/#organization`,
        name: siteConfig.name,
        url: baseUrl,
        logo: `${baseUrl}/logo-dark-nobg.png`,
      },
    ],
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <LocaleSetter locale={locale} />
      <NextIntlClientProvider messages={messages}>
        <Providers>
          <SkipToContent />
          <LayoutChrome />
          <main id="main-content" className="min-h-screen">
            {children}
          </main>
          <LayoutFooter />
          <CommandPalette />
          <Toaster position="bottom-right" />
        </Providers>
      </NextIntlClientProvider>
    </>
  )
}
