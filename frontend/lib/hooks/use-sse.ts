"use client"

import { useState, useCallback, useRef, useEffect } from "react"
import { toast } from "sonner"
import * as Sentry from "@sentry/nextjs"

/**
 * SSE Message format from backend
 */
interface SSEMessage {
  type?:
    | "token"
    | "complete"
    | "error"
    | "section"
    | "paragraph"
    | "stats"
    | "no_results"
    | "progress"
  content?: string
  result?: unknown
  error?: string
  status?: string
  message?: string
  step?: string
  verse_details?: unknown
  token?: string
  done?: boolean
  stats?: unknown
  data?: unknown
}

/**
 * Return type for useSSE hook
 */
export interface UseSSEReturn {
  data: SSEMessage[]
  isStreaming: boolean
  error: string | null
  startStream: (url: string) => void
  stopStream: () => void
}

/**
 * Hook for Server-Sent Events (SSE) streaming
 * Supports both /api/stream/search and /api/stream/compare endpoints
 *
 * @returns {UseSSEReturn} Object with data, streaming state, error, and control functions
 *
 * @example
 * const { data, isStreaming, error, startStream, stopStream } = useSSE();
 *
 * const handleSearch = () => {
 *   startStream('/api/stream/search?q=test&source=quran');
 * };
 */
const MAX_RETRIES = 3

export function useSSE(): UseSSEReturn {
  const [data, setData] = useState<SSEMessage[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const currentUrlRef = useRef<string | null>(null)
  const retryCountRef = useRef(0)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const isMountedRef = useRef(true)
  const shouldReconnectRef = useRef(true)
  const startStreamInternalRef = useRef<((url: string) => void) | null>(null)

  useEffect(() => {
    isMountedRef.current = true

    return () => {
      isMountedRef.current = false
      shouldReconnectRef.current = false

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }

      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, [])

  const startStreamInternal = useCallback((url: string) => {
    if (!isMountedRef.current) {
      return
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    // Clean up any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }

    // Store current URL for reconnection
    currentUrlRef.current = url

    try {
      // Create EventSource with credentials for auth
      const eventSource = new EventSource(url, {
        withCredentials: true,
      })

      eventSourceRef.current = eventSource

      /**
       * Handle incoming messages
       * Expected format: data: {"type": "token", "content": "..."}
       */
      eventSource.onmessage = (event: MessageEvent) => {
        if (!isMountedRef.current) {
          eventSource.close()
          if (eventSourceRef.current === eventSource) {
            eventSourceRef.current = null
          }
          return
        }

        try {
          const message: SSEMessage = JSON.parse(event.data)

          setData((prevData) => [...prevData, message])

          // Close stream on completion
          if (message.type === "complete") {
            eventSource.close()
            if (eventSourceRef.current === eventSource) {
              eventSourceRef.current = null
            }
            setIsStreaming(false)
          }
        } catch (parseError) {
          if (!isMountedRef.current) {
            return
          }

          const errorMsg =
            parseError instanceof Error ? parseError.message : "Failed to parse message"
          Sentry.captureException(parseError, { tags: { source: "sse-parse" } })
          setError(errorMsg)
          eventSource.close()
          if (eventSourceRef.current === eventSource) {
            eventSourceRef.current = null
          }
          setIsStreaming(false)
        }
      }

      /**
       * Handle connection open
       */
      eventSource.onopen = () => {
        if (!isMountedRef.current) {
          return
        }

        setError(null)
        retryCountRef.current = 0
      }

      /**
       * Handle errors with reconnection logic
       */
      eventSource.onerror = (event: Event) => {
        const eventSource = event.target as EventSource
        eventSource.close()
        if (eventSourceRef.current === eventSource) {
          eventSourceRef.current = null
        }

        if (!isMountedRef.current || !shouldReconnectRef.current) {
          return
        }

        if (eventSource.readyState === EventSource.CLOSED) {
          // Check if we should retry
          if (retryCountRef.current < MAX_RETRIES && currentUrlRef.current) {
            // Calculate exponential backoff: 1s, 2s, 4s
            const delay = Math.pow(2, retryCountRef.current) * 1000

            toast.info("Connection lost", {
              description: `Reconnecting... (${retryCountRef.current + 1}/${MAX_RETRIES})`,
            })

            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectTimeoutRef.current = null

              if (!isMountedRef.current || !shouldReconnectRef.current || !currentUrlRef.current) {
                return
              }

              retryCountRef.current += 1
              startStreamInternalRef.current?.(currentUrlRef.current)
            }, delay)
          } else {
            // Max retries reached - fall back to POST
            Sentry.captureException(new Error("SSE connection failed after max retries"), {
              tags: { source: "sse-connection" },
            })
            setError("Connection failed after 3 retries. Falling back to standard request.")
            setIsStreaming(false)
            toast.error("Connection failed", {
              description: "Falling back to standard request...",
            })
          }
        }
      }
    } catch (err) {
      if (!isMountedRef.current) {
        return
      }

      const errorMsg = err instanceof Error ? err.message : "Failed to start stream"
      Sentry.captureException(err, { tags: { source: "sse-init" } })
      setError(errorMsg)
      setIsStreaming(false)
    }
  }, [])

  // Store function reference for recursive calls (in effect to avoid render-time ref update)
  useEffect(() => {
    startStreamInternalRef.current = startStreamInternal
  }, [startStreamInternal])

  const startStream = useCallback(
    (url: string) => {
      if (!isMountedRef.current) {
        return
      }

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }

      shouldReconnectRef.current = true

      // Reset state for new stream
      setData([])
      setError(null)
      setIsStreaming(true)
      retryCountRef.current = 0

      startStreamInternal(url)
    },
    [startStreamInternal]
  )

  const stopStream = useCallback(() => {
    shouldReconnectRef.current = false
    currentUrlRef.current = null

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }

    if (isMountedRef.current) {
      setIsStreaming(false)
    }
  }, [])

  return {
    data,
    isStreaming,
    error,
    startStream,
    stopStream,
  }
}
