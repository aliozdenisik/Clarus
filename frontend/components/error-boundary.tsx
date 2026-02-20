"use client"

import React from "react"
import * as Sentry from "@sentry/nextjs"
import { logger } from "@/lib/logger"

interface Props {
  children: React.ReactNode
}

interface State {
  hasError: boolean
  eventId: string | null
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, eventId: null }
  }

  static getDerivedStateFromError(): State {
    return { hasError: true, eventId: null }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log the error with full context
    logger.error("React component error caught by ErrorBoundary", error, {
      component: "ErrorBoundary",
      action: "componentDidCatch",
      componentStack: errorInfo.componentStack || undefined,
    })

    // Capture to Sentry and get event ID for user feedback
    const eventId = Sentry.captureException(error, {
      extra: { componentStack: errorInfo.componentStack },
    })
    this.setState({ eventId })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-zinc-950 p-4">
          <div className="max-w-md text-center">
            <h1 className="mb-4 text-2xl font-bold text-white">Something went wrong</h1>
            <p className="mb-6 text-zinc-400">
              An unexpected error occurred. Our team has been notified.
            </p>
            {this.state.eventId && (
              <p className="mb-4 text-xs text-zinc-400">Error ID: {this.state.eventId}</p>
            )}
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="rounded bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
