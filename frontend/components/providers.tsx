"use client"

import { ThemeProvider } from "next-themes"
import { ApiProvider } from "@/lib/api-provider"
import { AuthUIProvider } from "@/components/providers/auth-ui-provider"
import { OnboardingGuard } from "@/components/providers/onboarding-guard"
import { OfflineBannerWrapper } from "@/components/layout/offline-banner"
import { ErrorBoundary } from "@/components/error-boundary"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange>
      <ApiProvider>
        <AuthUIProvider>
          <ErrorBoundary>
            <OfflineBannerWrapper />
            <OnboardingGuard>{children}</OnboardingGuard>
          </ErrorBoundary>
        </AuthUIProvider>
      </ApiProvider>
    </ThemeProvider>
  )
}
