"use client"

import { logger } from "@/lib/logger"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  logger.error("Page error", error)

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 p-4">
      <div className="max-w-md text-center">
        <h2 className="mb-4 text-2xl font-bold text-white">Something went wrong</h2>
        <p className="mb-6 text-zinc-400">
          An unexpected error occurred during keyword search. Please try again.
        </p>
        {error.digest && <p className="mb-4 text-xs text-zinc-500">Error ID: {error.digest}</p>}
        <button
          onClick={reset}
          className="rounded bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    </div>
  )
}
