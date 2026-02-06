"use client";

import { GoogleOAuthProvider } from '@react-oauth/google';
import { ThemeProvider } from 'next-themes';
import { ApiProvider } from "@/lib/api-provider";
import { AuthProvider } from "@/lib/auth/auth-context";
import { AuthUIProvider } from "@/components/providers/auth-ui-provider";
import { OfflineBannerWrapper } from "@/components/layout/offline-banner";
import { ErrorBoundary } from "@/components/error-boundary";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange>
      <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!}>
        <ApiProvider>
          <AuthProvider>
            <AuthUIProvider>
              <ErrorBoundary>
                <OfflineBannerWrapper />
                {children}
              </ErrorBoundary>
            </AuthUIProvider>
          </AuthProvider>
        </ApiProvider>
      </GoogleOAuthProvider>
    </ThemeProvider>
  );
}
