import type { Metadata } from "next"
import { getTranslations } from "next-intl/server"

export const metadata: Metadata = {
  title: "Authentication - Clarus",
  description: "Sign in or create an account to access Clarus",
}

/**
 * Auth Layout
 *
 * Split-screen layout with form on left and animated gradient hero on right.
 * Mobile: Full-width form, hero hidden.
 * Desktop: 50/50 split with animated gradient blobs.
 */
export default async function AuthLayout({ children }: { children: React.ReactNode }) {
  const t = await getTranslations("AuthLayout")

  return (
    <div className="flex min-h-screen w-full flex-col bg-[var(--color-bg-app)] lg:flex-row">
      {/* LEFT SIDE — Auth Form */}
      <div className="flex flex-1 items-center justify-center p-6 sm:p-8 lg:p-12">
        <div className="w-full max-w-md space-y-8">{children}</div>
      </div>

      {/* RIGHT SIDE — Gradient Hero (hidden on mobile) */}
      <div className="relative hidden flex-1 overflow-hidden lg:flex">
        {/* Gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900" />

        {/* Animated blobs */}
        <div className="absolute top-0 -left-4 h-72 w-72 animate-pulse rounded-full bg-indigo-500/20 mix-blend-screen blur-3xl filter" />
        <div
          className="absolute top-1/3 -right-4 h-72 w-72 animate-pulse rounded-full bg-purple-500/20 mix-blend-screen blur-3xl filter"
          style={{ animationDelay: "2s" }}
        />
        <div
          className="absolute -bottom-8 left-1/4 h-72 w-72 animate-pulse rounded-full bg-cyan-500/15 mix-blend-screen blur-3xl filter"
          style={{ animationDelay: "4s" }}
        />

        {/* Subtle grid pattern overlay */}
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' width='32' height='32' fill='none' stroke-width='2' stroke='rgb(148 163 184 / 0.15)'%3e%3cpath d='M0 .5H31.5V32'/%3e%3c/svg%3e")`,
          }}
        />

        {/* Hero content */}
        <div className="relative z-10 flex w-full items-center justify-center p-8 lg:p-12">
          <div className="max-w-sm space-y-6 text-center">
            {/* Shield icon */}
            <div className="mb-2 inline-flex rounded-full bg-white/10 p-4 backdrop-blur-sm">
              <svg
                className="h-10 w-10 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"
                />
              </svg>
            </div>

            <h2 className="text-3xl leading-tight font-bold text-white lg:text-4xl">
              {t("heroTitle")}
              <br />
              {t("heroTitleLine2")}
            </h2>
            <p className="text-lg leading-relaxed text-white/70">{t("heroDescription")}</p>

            {/* Feature pills */}
            <div className="flex flex-wrap justify-center gap-2 pt-2">
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-white/80 backdrop-blur-sm">
                {t("pillSemantic")}
              </span>
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-white/80 backdrop-blur-sm">
                {t("pillAgents")}
              </span>
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-white/80 backdrop-blur-sm">
                {t("pillVerses")}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
