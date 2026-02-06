"use client";

import { AuthUIProvider as BetterAuthUIProvider } from "@daveyplate/better-auth-ui";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import Link from "next/link";

/**
 * Better Auth UI Provider
 * 
 * Wraps the application with Better Auth UI context, providing:
 * - Authentication state management
 * - Navigation handlers for auth flows
 * - Social provider configuration (Google)
 * - Session change handling
 * 
 * @see https://github.com/daveyplate/better-auth-ui
 */
export function AuthUIProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  return (
    <BetterAuthUIProvider
      authClient={authClient}
      basePath="/"
      navigate={router.push}
      replace={router.replace}
      onSessionChange={() => {
        // Clear Next.js router cache when session changes
        // This ensures protected routes re-validate
        router.refresh();
      }}
      Link={Link}
    >
      {children}
    </BetterAuthUIProvider>
  );
}
