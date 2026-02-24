import "./globals.css"
import { configureApiClient } from "@/lib/api/config"
import { fontVariableClassNames } from "@/lib/fonts"
import { getLocale } from "next-intl/server"

configureApiClient()

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
