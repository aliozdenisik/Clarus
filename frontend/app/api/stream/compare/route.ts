import { NextRequest } from "next/server"

import { auth } from "@/lib/auth"
import { logger } from "@/lib/logger"
import { consumeDistributedFixedWindow } from "@/lib/security/rate-limit"
import {
  buildAuthCookieHeader,
  buildCompareProxyParams,
  getClientErrorMessage,
  getClientIdentifier,
  truncateForLog,
} from "@/lib/security/stream-proxy"

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || "http://127.0.0.1:8000"
const STREAM_RATE_LIMIT_MAX_REQUESTS = 20
const STREAM_RATE_LIMIT_WINDOW_MS = 60_000
const log = logger.child({ component: "StreamCompareProxy" })

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

const buildRateLimitHeaders = (remaining: number, resetAt: number): Record<string, string> => ({
  "X-RateLimit-Limit": String(STREAM_RATE_LIMIT_MAX_REQUESTS),
  "X-RateLimit-Remaining": String(remaining),
  "X-RateLimit-Reset": String(Math.ceil(resetAt / 1000)),
})

export async function GET(request: NextRequest) {
  const session = await auth.api.getSession({ headers: request.headers })
  if (!session) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    })
  }

  const rateLimit = await consumeDistributedFixedWindow(
    `stream-compare:${getClientIdentifier(request.headers)}`,
    STREAM_RATE_LIMIT_MAX_REQUESTS,
    STREAM_RATE_LIMIT_WINDOW_MS
  )
  const rateLimitHeaders = buildRateLimitHeaders(rateLimit.remaining, rateLimit.resetAt)

  if (!rateLimit.allowed) {
    log.warn("Compare stream rate limit exceeded", { action: "rate-limit" })
    return new Response(JSON.stringify({ error: "Rate limit exceeded" }), {
      status: 429,
      headers: {
        "Content-Type": "application/json",
        "Retry-After": String(rateLimit.retryAfterSeconds),
        ...rateLimitHeaders,
      },
    })
  }

  const filteredParams = buildCompareProxyParams(request.nextUrl.searchParams)
  if (!filteredParams.get("topic")) {
    return new Response(JSON.stringify({ error: "Invalid request parameters" }), {
      status: 400,
      headers: {
        "Content-Type": "application/json",
        ...rateLimitHeaders,
      },
    })
  }

  const queryString = filteredParams.toString()
  const backendUrl = `${BACKEND_URL}/api/stream/compare${queryString ? `?${queryString}` : ""}`
  const cookieHeader = buildAuthCookieHeader(request.headers.get("cookie") || "")
  const acceptLanguage = request.headers.get("accept-language") || "tr"

  try {
    const upstreamHeaders: Record<string, string> = {
      Accept: "text/event-stream",
      "Accept-Language": acceptLanguage,
    }
    if (cookieHeader) {
      upstreamHeaders.Cookie = cookieHeader
    }

    const response = await fetch(backendUrl, {
      headers: upstreamHeaders,
      cache: "no-store",
    })

    if (!response.ok) {
      const body = await response.text().catch(() => "")
      log.error("Compare stream backend responded with error", undefined, {
        action: "proxy",
        status: response.status,
        body: truncateForLog(body),
      })

      return new Response(JSON.stringify({ error: getClientErrorMessage(response.status) }), {
        status: response.status,
        headers: {
          "Content-Type": "application/json",
          ...rateLimitHeaders,
        },
      })
    }

    if (!response.body) {
      log.error("Compare stream backend returned empty body", undefined, { action: "proxy" })
      return new Response(JSON.stringify({ error: "Service temporarily unavailable" }), {
        status: 502,
        headers: {
          "Content-Type": "application/json",
          ...rateLimitHeaders,
        },
      })
    }

    const { readable, writable } = new TransformStream()
    const writer = writable.getWriter()
    const reader = response.body.getReader()

    const pump = async () => {
      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) {
            break
          }
          await writer.write(value)
        }
      } catch (error) {
        log.debug("Compare stream closed by client", {
          action: "stream",
          error: error instanceof Error ? error.message : String(error),
        })
      } finally {
        try {
          writer.close()
        } catch (error) {
          log.debug("Compare stream writer already closed", {
            action: "stream",
            error: error instanceof Error ? error.message : String(error),
          })
        }
      }
    }

    void pump()

    return new Response(readable, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
        "X-Accel-Buffering": "no",
        ...rateLimitHeaders,
      },
    })
  } catch (error) {
    log.error("Compare stream proxy connection failed", error, { action: "proxy" })
    return new Response(JSON.stringify({ error: "Backend connection failed" }), {
      status: 502,
      headers: {
        "Content-Type": "application/json",
        ...rateLimitHeaders,
      },
    })
  }
}
