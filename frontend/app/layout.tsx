import "./globals.css"
import type { Metadata } from "next"
import { configureApiClient } from "@/lib/api/config"
import { fontVariableClassNames } from "@/lib/fonts"
import { getBaseUrl } from "@/lib/seo"
import { getLocale } from "next-intl/server"

configureApiClient()

export const metadata: Metadata = {
  metadataBase: new URL(getBaseUrl()),
  applicationName: "Clarus",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: "/favicon.ico",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
      "max-video-preview": -1,
    },
  },
  verification: {
    google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION,
  },
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const locale = await getLocale()

  return (
    <html lang={locale} className="dark" suppressHydrationWarning>
      <body className={`${fontVariableClassNames} antialiased`} suppressHydrationWarning>
        {children}
      </body>
    </html>
  )
}
