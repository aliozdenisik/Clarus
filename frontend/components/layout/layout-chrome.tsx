"use client"

import { usePathname } from "next/navigation"
import Navigation from "@/components/layout/navigation"
import { Footer } from "@/components/ui/large-name-footer"

function shouldHideChrome(pathname: string): boolean {
  return pathname.includes("/onboarding")
}

export function LayoutChrome() {
  const pathname = usePathname()

  if (shouldHideChrome(pathname)) {
    return null
  }

  return <Navigation />
}

export function LayoutFooter() {
  const pathname = usePathname()

  if (shouldHideChrome(pathname)) {
    return null
  }

  return <Footer />
}
