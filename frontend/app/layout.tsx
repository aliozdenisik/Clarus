import "./globals.css"
import { configureApiClient } from "@/lib/api/config"

configureApiClient()

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return children
}
