"use client";

import { GoogleOAuthProvider } from '@react-oauth/google';
import { ApiProvider } from "@/lib/api-provider";
import { AuthProvider } from "@/lib/auth/auth-context";
import { OfflineBannerWrapper } from "@/components/layout/offline-banner";
import { ErrorBoundary } from "@/components/error-boundary";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!}>
      <ApiProvider>
        <AuthProvider>
          <ErrorBoundary>
            <OfflineBannerWrapper />
            {children}
          </ErrorBoundary>
        </AuthProvider>
      </ApiProvider>
    </GoogleOAuthProvider>
  );
}
