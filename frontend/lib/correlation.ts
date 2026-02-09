/**
 * Correlation ID management for end-to-end request tracing.
 *
 * This module provides utilities to track user actions across frontend and backend.
 * Each user action (search, compare, etc.) gets a unique correlation ID that is:
 * 1. Generated when the action starts
 * 2. Passed to all API requests via X-Correlation-ID header
 * 3. Logged in both frontend and backend for debugging
 * 4. Cleared when the action completes
 */

import { logger } from "./logger";

let currentCorrelationId: string | undefined;

/**
 * Start a new correlation for a user action.
 */
export function startCorrelation(): string {
  currentCorrelationId = crypto.randomUUID();
  logger.setCorrelationId(currentCorrelationId);
  logger.debug("Correlation started", {
    action: "correlation_start",
    correlationId: currentCorrelationId,
  });
  return currentCorrelationId;
}

/**
 * Get the current correlation ID.
 */
export function getCorrelationId(): string | undefined {
  return currentCorrelationId;
}

/**
 * End the current correlation.
 */
export function endCorrelation(): void {
  if (currentCorrelationId) {
    logger.debug("Correlation ended", {
      action: "correlation_end",
      correlationId: currentCorrelationId,
    });
  }
  currentCorrelationId = undefined;
  logger.clearCorrelationId();
}

/**
 * Get headers object with correlation ID for API requests.
 */
export function getCorrelationHeaders(): Record<string, string> {
  return currentCorrelationId ? { "X-Correlation-ID": currentCorrelationId } : {};
}

/**
 * Wrap an async operation with correlation tracking lifecycle.
 */
export function withCorrelation<T, Args extends unknown[]>(
  operation: (...args: Args) => Promise<T>
): (...args: Args) => Promise<T> {
  return async (...args: Args): Promise<T> => {
    startCorrelation();
    try {
      return await operation(...args);
    } finally {
      endCorrelation();
    }
  };
}
