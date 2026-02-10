"use client"

import { AuthView } from "@daveyplate/better-auth-ui"
import "@daveyplate/better-auth-ui/css"
import Link from "next/link"
import { ChevronLeft } from "lucide-react"

/**
 * Sign Up Page
 *
 * Uses Better Auth UI's AuthView component for registration.
 * Supports email/password and Google OAuth sign-up.
 */
export default function SignUpPage() {
  return (
    <>
      {/* Header with back button */}
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-sm text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-text-primary)]"
        >
          <ChevronLeft size={16} />
          <span>Home</span>
        </Link>
      </div>

      {/* Branding */}
      <div className="space-y-2">
        <span className="bg-gradient-to-r from-indigo-400 to-indigo-600 bg-clip-text text-3xl font-bold text-transparent">
          Clarus
        </span>
        <h1 className="text-2xl font-semibold text-[var(--color-text-primary)]">
          Create your account
        </h1>
        <p className="text-[var(--color-text-muted)]">Start exploring sacred texts with AI</p>
      </div>

      {/* Better Auth Form */}
      <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-6 shadow-sm">
        <AuthView pathname="sign-up" />
      </div>

      {/* Terms */}
      <p className="text-center text-xs text-[var(--color-text-muted)]">
        By creating an account, you agree to our{" "}
        <Link href="#" className="text-[var(--color-accent-primary)] hover:underline">
          Terms
        </Link>{" "}
        and{" "}
        <Link href="#" className="text-[var(--color-accent-primary)] hover:underline">
          Privacy Policy
        </Link>
        .
      </p>
    </>
  )
}
