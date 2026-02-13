import {
  DM_Sans,
  DM_Serif_Display,
  Amiri,
  Noto_Sans_Hebrew,
  Noto_Serif,
  Crimson_Text,
} from "next/font/google"
import "./globals.css"
import { configureApiClient } from "@/lib/api/config"

configureApiClient()

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
})

const dmSerif = DM_Serif_Display({
  subsets: ["latin"],
  weight: ["400"],
  variable: "--font-serif",
  display: "swap",
})

const amiri = Amiri({
  subsets: ["arabic"],
  weight: ["400", "700"],
  variable: "--font-arabic",
  display: "swap",
})

const notoSansHebrew = Noto_Sans_Hebrew({
  subsets: ["hebrew"],
  weight: ["400", "700"],
  variable: "--font-hebrew",
  display: "swap",
})

const notoSerifGreek = Noto_Serif({
  subsets: ["greek"],
  weight: ["400", "700"],
  variable: "--font-greek",
  display: "swap",
})

const crimsonText = Crimson_Text({
  subsets: ["latin"],
  weight: ["400", "600"],
  variable: "--font-crimson",
  display: "swap",
})

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html className="dark" suppressHydrationWarning>
      <body
        className={`${dmSans.variable} ${dmSerif.variable} ${amiri.variable} ${notoSansHebrew.variable} ${notoSerifGreek.variable} ${crimsonText.variable} antialiased`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  )
}
