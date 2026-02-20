import type { Metadata } from "next"
import { NextIntlClientProvider } from "next-intl"
import { getMessages, getTranslations } from "next-intl/server"
import { notFound } from "next/navigation"
import { routing } from "@/i18n/routing"
import { Providers } from "@/components/providers"
import { Toaster } from "sonner"
import { LayoutChrome, LayoutFooter } from "@/components/layout/layout-chrome"
import { CommandPalette } from "@/components/command-palette"
import { fontVariableClassNames } from "@/lib/fonts"
import { SkipToContent } from "@/components/layout/skip-to-content"

type Props = {
  children: React.ReactNode
  params: Promise<{ locale: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: "Metadata" })
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"

  return {
    title: {
      default: t("title"),
      template: `%s | ${t("title")}`,
    },
    description: t("description"),
    alternates: {
      canonical: `${baseUrl}/${locale}`,
      languages: {
        en: `${baseUrl}/en`,
        tr: `${baseUrl}/tr`,
        "x-default": `${baseUrl}/tr`,
      },
    },
    openGraph: {
      locale: locale === "tr" ? "tr_TR" : "en_US",
      alternateLocale: locale === "tr" ? ["en_US"] : ["tr_TR"],
      type: "website",
      url: `${baseUrl}/${locale}`,
    },
  }
}

export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params

  if (!routing.locales.includes(locale as never)) {
    notFound()
  }

  const messages = await getMessages()

  return (
    <html lang={locale} className="dark" suppressHydrationWarning>
      <body className={`${fontVariableClassNames} antialiased`} suppressHydrationWarning>
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
      </body>
    </html>
  )
}
