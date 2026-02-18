import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Onboarding - Clarus",
  description: "Set up your Clarus experience",
}

/**
 * Onboarding Layout
 *
 * Server Component that wraps onboarding flow without Navigation or Footer.
 * Features fullscreen dark background with DotPattern + RadialGradient ambiance.
 * Progress bar and skip link are rendered by OnboardingShell client component.
 */
export default async function OnboardingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-hidden bg-[var(--color-bg-app)]">
      {/* Background: DotPattern + RadialGradient */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-[linear-gradient(to_bottom,var(--color-bg-app),var(--color-bg-app))]" />

        {/* Dot pattern background */}
        <svg
          className="pointer-events-none absolute inset-0 h-full w-full text-neutral-400/40"
          width="100%"
          height="100%"
          aria-hidden="true"
        >
          <defs>
            <pattern
              id="onboarding-dot-pattern"
              x="0"
              y="0"
              width="32"
              height="32"
              patternUnits="userSpaceOnUse"
            >
              <circle cx="16" cy="16" r="1.5" fill="currentColor" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#onboarding-dot-pattern)" />
        </svg>

        {/* Radial gradient overlays (ambient glow) */}
        <div
          className="pointer-events-none absolute inset-0 opacity-20"
          style={{
            background: `radial-gradient(600px circle at 20% 50%, var(--color-accent-primary), transparent)`,
          }}
        />
        <div
          className="pointer-events-none absolute inset-0 opacity-15"
          style={{
            background: `radial-gradient(500px circle at 80% 80%, var(--color-accent-glow), transparent)`,
          }}
        />
      </div>

      {/* Content layer */}
      <div className="relative z-10 flex flex-1 flex-col">
        {/* This is where OnboardingShell will inject the progress bar and skip link */}
        {children}
      </div>
    </div>
  )
}
