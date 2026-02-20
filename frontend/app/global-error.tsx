"use client"

import * as Sentry from "@sentry/nextjs"
import { useEffect } from "react"

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    Sentry.captureException(error)
  }, [error])

  return (
    <html lang="en">
      <body className="bg-background flex min-h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-foreground text-2xl font-bold">Something went wrong</h1>
          <p className="text-muted-foreground mt-2">
            We&apos;ve been notified and are working on it.
          </p>
          <button
            type="button"
            onClick={reset}
            className="bg-primary text-primary-foreground mt-4 rounded px-4 py-2"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  )
}
