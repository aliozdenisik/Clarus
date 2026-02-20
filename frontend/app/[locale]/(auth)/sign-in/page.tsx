"use client"

import { AuthView } from "@daveyplate/better-auth-ui"
import "@daveyplate/better-auth-ui/css"
import Link from "next/link"
import { ChevronLeft } from "lucide-react"
import { useTranslations } from "next-intl"

/**
 * Sign In Page
 *
 * Uses Better Auth UI's AuthView component for authentication.
 * Supports email/password and Google OAuth sign-in.
 */
export default function SignInPage() {
  const t = useTranslations("Auth")
  const tCommon = useTranslations("Common")

  return (
    <>
      {/* Header with back button */}
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-md border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] px-3 py-2 text-sm font-medium text-[var(--color-text-secondary)] transition-colors hover:border-[var(--color-border-glow)] hover:text-[var(--color-text-primary)]"
        >
          <ChevronLeft size={17} />
          <span>{tCommon("back")}</span>
        </Link>
      </div>

      {/* Branding */}
      <div className="space-y-1.5">
        <span className="bg-gradient-to-r from-indigo-400 to-indigo-600 bg-clip-text text-3xl font-bold text-transparent">
          Clarus
        </span>
        <p className="text-sm text-[var(--color-text-secondary)]">{t("welcomeBack")}</p>
      </div>

      <AuthView
        pathname="sign-in"
        className="max-w-none border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] shadow-sm"
        classNames={{
          header: "gap-2",
          title: "text-xl font-semibold text-[var(--color-text-primary)]",
          description: "text-sm text-[var(--color-text-secondary)]",
          content: "gap-5",
          footer: "text-[var(--color-text-muted)]",
          footerLink: "text-[var(--color-accent-secondary)] hover:text-[var(--color-text-primary)]",
          form: {
            label: "text-[var(--color-text-secondary)]",
            input:
              "border-[var(--color-border-subtle)] bg-[var(--color-bg-app)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)] focus-visible:border-[var(--color-border-glow)]",
            forgotPasswordLink:
              "text-[var(--color-accent-secondary)] hover:text-[var(--color-text-primary)]",
            button: "h-10 font-medium",
            primaryButton:
              "bg-[var(--color-accent-primary)] text-white hover:bg-[var(--color-accent-hover)]",
          },
        }}
      />

      <p className="text-center text-xs text-[var(--color-text-muted)]">
        {t("termsSignIn")}{" "}
        <Link
          href="#"
          className="text-[var(--color-accent-secondary)] underline underline-offset-2"
        >
          {t("terms")}
        </Link>{" "}
        {t("and")}{" "}
        <Link
          href="#"
          className="text-[var(--color-accent-secondary)] underline underline-offset-2"
        >
          {t("privacyPolicy")}
        </Link>
        .
      </p>
    </>
  )
}
