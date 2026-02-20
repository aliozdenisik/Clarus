"use client"

import { AuthUIProvider as BetterAuthUIProvider } from "@daveyplate/better-auth-ui"
import type { AuthLocalization } from "@daveyplate/better-auth-ui"
import { authClient } from "@/lib/auth-client"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import Link from "next/link"

function useBetterAuthLocalization(): Partial<AuthLocalization> | undefined {
  const t = useTranslations("BetterAuth")

  return {
    SIGN_IN: t("SIGN_IN"),
    SIGN_IN_ACTION: t("SIGN_IN_ACTION"),
    SIGN_IN_DESCRIPTION: t("SIGN_IN_DESCRIPTION"),
    SIGN_UP: t("SIGN_UP"),
    SIGN_UP_ACTION: t("SIGN_UP_ACTION"),
    SIGN_UP_DESCRIPTION: t("SIGN_UP_DESCRIPTION"),
    EMAIL: t("EMAIL"),
    EMAIL_PLACEHOLDER: t("EMAIL_PLACEHOLDER"),
    EMAIL_REQUIRED: t("EMAIL_REQUIRED"),
    PASSWORD: t("PASSWORD"),
    PASSWORD_PLACEHOLDER: t("PASSWORD_PLACEHOLDER"),
    PASSWORD_REQUIRED: t("PASSWORD_REQUIRED"),
    CONFIRM_PASSWORD: t("CONFIRM_PASSWORD"),
    CONFIRM_PASSWORD_PLACEHOLDER: t("CONFIRM_PASSWORD_PLACEHOLDER"),
    CONFIRM_PASSWORD_REQUIRED: t("CONFIRM_PASSWORD_REQUIRED"),
    NAME: t("NAME"),
    NAME_PLACEHOLDER: t("NAME_PLACEHOLDER"),
    FORGOT_PASSWORD_LINK: t("FORGOT_PASSWORD_LINK"),
    FORGOT_PASSWORD: t("FORGOT_PASSWORD"),
    FORGOT_PASSWORD_ACTION: t("FORGOT_PASSWORD_ACTION"),
    FORGOT_PASSWORD_DESCRIPTION: t("FORGOT_PASSWORD_DESCRIPTION"),
    FORGOT_PASSWORD_EMAIL: t("FORGOT_PASSWORD_EMAIL"),
    RESET_PASSWORD: t("RESET_PASSWORD"),
    RESET_PASSWORD_ACTION: t("RESET_PASSWORD_ACTION"),
    RESET_PASSWORD_DESCRIPTION: t("RESET_PASSWORD_DESCRIPTION"),
    RESET_PASSWORD_SUCCESS: t("RESET_PASSWORD_SUCCESS"),
    DONT_HAVE_AN_ACCOUNT: t("DONT_HAVE_AN_ACCOUNT"),
    ALREADY_HAVE_AN_ACCOUNT: t("ALREADY_HAVE_AN_ACCOUNT"),
    OR_CONTINUE_WITH: t("OR_CONTINUE_WITH"),
    SIGN_IN_WITH: t("SIGN_IN_WITH"),
    REMEMBER_ME: t("REMEMBER_ME"),
    BY_CONTINUING_YOU_AGREE: t("BY_CONTINUING_YOU_AGREE"),
    TERMS_OF_SERVICE: t("TERMS_OF_SERVICE"),
    PRIVACY_POLICY: t("PRIVACY_POLICY"),
    CANCEL: t("CANCEL"),
    SAVE: t("SAVE"),
    PASSWORDS_DO_NOT_MATCH: t("PASSWORDS_DO_NOT_MATCH"),
    INVALID_EMAIL_OR_PASSWORD: t("INVALID_EMAIL_OR_PASSWORD"),
    USER_ALREADY_EXISTS: t("USER_ALREADY_EXISTS"),
    PASSWORD_TOO_SHORT: t("PASSWORD_TOO_SHORT"),
    UNKNOWN_ERROR: t("UNKNOWN_ERROR"),
    REQUEST_FAILED: t("REQUEST_FAILED"),
    SIGN_OUT: t("SIGN_OUT"),
    GO_BACK: t("GO_BACK"),
  }
}

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
  const router = useRouter()
  const localization = useBetterAuthLocalization()

  return (
    <BetterAuthUIProvider
      authClient={authClient}
      basePath="/"
      credentials={{ confirmPassword: true }}
      navigate={router.push}
      replace={router.replace}
      onSessionChange={() => {
        // Clear Next.js router cache when session changes
        // This ensures protected routes re-validate
        router.refresh()
      }}
      Link={Link}
      localization={localization}
    >
      {children}
    </BetterAuthUIProvider>
  )
}
