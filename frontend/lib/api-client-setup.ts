/**
 * API Client Setup with Correlation ID Interceptors.
 */

import { client } from "./api/client.gen"
import { getCorrelationId } from "./correlation"
import { logger } from "./logger"
import { configureApiClient } from "./api/config"

let isSetupComplete = false

const isAbortError = (error: unknown): boolean =>
  error instanceof DOMException
    ? error.name === "AbortError"
    : error instanceof Error && error.name === "AbortError"

/**
 * Configure API client interceptors once.
 */
export function setupApiClient(): void {
  if (isSetupComplete) {
    return
  }

  client.interceptors.request.use((request) => {
    const correlationId = getCorrelationId()

    if (correlationId) {
      request.headers.set("X-Correlation-ID", correlationId)
    }

    logger.debug("API request initiated", {
      component: "ApiClient",
      action: "request",
      method: request.method,
      url: request.url,
      hasCorrelation: Boolean(correlationId),
    })

    return request
  })

  client.interceptors.response.use((response, request) => {
    const correlationId = response.headers.get("X-Correlation-ID")
    const requestId = response.headers.get("X-Request-ID")

    logger.debug("API response received", {
      component: "ApiClient",
      action: "response",
      status: response.status,
      url: request.url,
      correlationId,
      requestId,
    })

    return response
  })

  client.interceptors.error.use((error, response, request) => {
    const correlationId = response?.headers?.get("X-Correlation-ID")
    const requestId = response?.headers?.get("X-Request-ID")

    if (isAbortError(error)) {
      logger.debug("API request aborted", {
        component: "ApiClient",
        action: "aborted",
        method: request?.method,
        url: request?.url,
        correlationId,
        requestId,
      })

      return error
    }

    const errorType =
      error instanceof DOMException || error instanceof Error ? error.name : typeof error
    const errorMessage =
      error instanceof DOMException || error instanceof Error
        ? error.message
        : typeof error === "string"
          ? error
          : undefined
    const errorPayload =
      typeof error === "string"
        ? error
        : error && typeof error === "object" && !(error instanceof Error)
          ? error
          : undefined

    const context = {
      component: "ApiClient",
      action: "error",
      status: response?.status,
      method: request?.method,
      url: request?.url,
      correlationId,
      requestId,
      errorType,
      errorMessage,
      errorPayload,
    }

    // 404s are expected for optional data lookups (e.g. etymology) — warn, not error
    if (response?.status === 404) {
      logger.warn("API resource not found", context)
    } else {
      logger.error("API request failed", error instanceof Error ? error : undefined, context)
    }

    return error
  })

  isSetupComplete = true
  logger.info("API client interceptors configured", {
    component: "ApiClient",
    action: "setup",
  })
}

configureApiClient()
setupApiClient()
