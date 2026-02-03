import type { Metadata } from "next";
import { Inter, Amiri, Noto_Sans_Hebrew } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "sonner";
import Navigation from "@/components/layout/navigation";
import { configureApiClient } from "@/lib/api/config";

configureApiClient();

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const amiri = Amiri({
  subsets: ["arabic"],
  weight: ["400", "700"],
  variable: "--font-arabic",
  display: "swap",
});

const notoSansHebrew = Noto_Sans_Hebrew({
  subsets: ["hebrew"],
  weight: ["400", "700"],
  variable: "--font-hebrew",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Clarus",
  description: "Search and explore Quran and Bible with AI-powered insights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} ${amiri.variable} ${notoSansHebrew.variable} antialiased`}>
        <Providers>
          <Navigation />
          {children}
          <Toaster position="bottom-right" />
        </Providers>
      </body>
    </html>
  );
}
