import "./globals.css"
import { configureApiClient } from "@/lib/api/config"
import { fontVariableClassNames } from "@/lib/fonts"

configureApiClient()

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="tr" className="dark" suppressHydrationWarning>
      <body className={`${fontVariableClassNames} antialiased`} suppressHydrationWarning>
        {children}
      </body>
    </html>
  )
}
