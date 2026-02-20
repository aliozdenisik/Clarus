"use client"

/**
 * Skip-to-content link for keyboard and screen reader users (WCAG 2.4.1).
 * Visually hidden until focused, then appears at top of page.
 */
export function SkipToContent() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:rounded-md focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-black focus:shadow-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
    >
      Skip to main content
    </a>
  )
}
