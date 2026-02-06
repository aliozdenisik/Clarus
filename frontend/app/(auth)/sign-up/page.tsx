"use client";

import { AuthView } from "@daveyplate/better-auth-ui";
import "@daveyplate/better-auth-ui/css";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";

/**
 * Sign Up Page
 * 
 * Uses Better Auth UI's AuthView component for registration.
 * Supports email/password and Google OAuth sign-up.
 */
export default function SignUpPage() {
  return (
    <div className="space-y-6">
      {/* Back to Home Button */}
      <div className="flex justify-start">
        <Link
          href="/"
          className="relative z-0 flex items-center justify-center gap-2 overflow-hidden rounded-md 
          border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]
          px-4 py-2 font-semibold text-[var(--color-text-primary)] transition-all duration-500
          before:absolute before:inset-0 before:-z-10 before:translate-x-[150%] before:translate-y-[150%] before:scale-[2.5]
          before:rounded-[100%] before:bg-[var(--color-accent-primary)] before:transition-transform before:duration-1000 before:content-['']
          hover:scale-105 hover:text-white hover:before:translate-x-[0%] hover:before:translate-y-[0%] active:scale-95"
        >
          <ChevronLeft size={16} />
          <span>Home</span>
        </Link>
      </div>

      {/* Logo */}
      <div className="flex justify-center">
        <span className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-indigo-600 bg-clip-text text-transparent">
          Clarus
        </span>
      </div>

      {/* Auth View */}
      <AuthView pathname="sign-up" />

      {/* Terms */}
      <p className="text-xs text-[var(--color-text-muted)] text-center">
        By signing up, you agree to our{" "}
        <Link href="#" className="text-[var(--color-accent-primary)] hover:underline">
          Terms & Conditions
        </Link>{" "}
        and{" "}
        <Link href="#" className="text-[var(--color-accent-primary)] hover:underline">
          Privacy Policy
        </Link>
        .
      </p>
    </div>
  );
}
