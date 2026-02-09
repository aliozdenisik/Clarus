/**
 * API Client Setup with Correlation ID Interceptors.
 */

import { client } from "./api/client.gen";
import { getCorrelationId } from "./correlation";
import { logger } from "./logger";
import { configureApiClient } from "./api/config";

let isSetupComplete = false;

/**
 * Configure API client interceptors once.
 */
export function setupApiClient(): void {
  if (isSetupComplete) {
    return;
  }

  client.interceptors.request.use((request, _options) => {
    const correlationId = getCorrelationId();

    if (correlationId) {
      request.headers.set("X-Correlation-ID", correlationId);
    }

    logger.debug("API request initiated", {
      component: "ApiClient",
      action: "request",
      method: request.method,
      url: request.url,
      hasCorrelation: Boolean(correlationId),
    });

    return request;
  });

  client.interceptors.response.use((response, request, _options) => {
    const correlationId = response.headers.get("X-Correlation-ID");
    const requestId = response.headers.get("X-Request-ID");

    logger.debug("API response received", {
      component: "ApiClient",
      action: "response",
      status: response.status,
      url: request.url,
      correlationId,
      requestId,
    });

    return response;
  });

  client.interceptors.error.use((error, response, request, _options) => {
    const correlationId = response?.headers?.get("X-Correlation-ID");
    const requestId = response?.headers?.get("X-Request-ID");

    logger.error("API request failed", error as Error, {
      component: "ApiClient",
      action: "error",
      status: response?.status,
      url: request?.url,
      correlationId,
      requestId,
    });

    return error;
  });

  isSetupComplete = true;
  logger.info("API client interceptors configured", {
    component: "ApiClient",
    action: "setup",
  });
}

configureApiClient();
setupApiClient();
