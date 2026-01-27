import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: process.env.NODE_ENV === "development" ? 1.0 : 0.1,
  environment: process.env.NODE_ENV,
  // NO replay integration - explicitly excluded
  
  // Filter out expected EventSource reconnection errors (SSE compatibility)
  beforeSend(event, hint) {
    const error = hint.originalException;
    if (error instanceof Error) {
      // EventSource reconnection errors are EXPECTED behavior
      if (error.message?.includes('EventSource') || 
          error.message?.includes('EventSource connection') ||
          error.message?.includes('net::ERR_') ||
          error.message?.includes('NetworkError') ||
          error.message?.includes('network connection was lost') ||
          (error.message?.includes('Failed to fetch') && 
           event.request?.url?.includes('/stream'))) {
        return null; // Don't send to Sentry
      }
      // Filter benign browser warnings
      if (error.message?.includes('ResizeObserver loop')) {
        return null;
      }
    }
    return event;
  },
  
  // Adjust transaction handling for long-running SSE streams
  beforeSendTransaction(transaction) {
    if (transaction.name?.includes('/compare') || 
        transaction.name?.includes('/stream')) {
      if (transaction.contexts) {
        transaction.contexts.trace = {
          ...transaction.contexts.trace,
          op: 'sse.stream',
        };
      }
    }
    return transaction;
  },
});
