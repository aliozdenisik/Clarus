import type { Metadata } from "next"
import { NextIntlClientProvider } from "next-intl"
import { getMessages } from "next-intl/server"
import { notFound } from "next/navigation"
import { routing } from "@/i18n/routing"
import { Providers } from "@/components/providers"
import { Toaster } from "sonner"
import Navigation from "@/components/layout/navigation"
import { Footer } from "@/components/ui/large-name-footer"

export const metadata: Metadata = {
  title: "Clarus",
  description: "Search and explore Quran and Bible with AI-powered insights",
}

type Props = {
  children: React.ReactNode
  params: Promise<{ locale: string }>
}

export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params

  if (!routing.locales.includes(locale as never)) {
    notFound()
  }

  const messages = await getMessages()

  return (
    <NextIntlClientProvider messages={messages}>
      <Providers>
        <Navigation />
        <main className="min-h-screen">{children}</main>
        <Footer />
        <Toaster position="bottom-right" />
      </Providers>
    </NextIntlClientProvider>
  )
}
