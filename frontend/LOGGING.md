# Frontend Structured Logging System

This document describes the structured logging system for the Clarus frontend, providing patterns, usage guides, and code examples for consistent logging across all components.

---

## Overview

The frontend uses a singleton Logger service built on standard browser APIs:

- **JSON format** for production (machine-parseable)
- **Pretty-printed format** for development (colored console output)
- **Sentry integration** for error tracking and breadcrumbs
- **Correlation ID support** for distributed tracing
- **Child loggers** for component-scoped logging

**Key file**: `frontend/lib/logger.ts`

---

## Quick Start

```typescript
import { logger, useLogger } from '@/lib/logger';

// Direct logger usage
logger.info('User searched', { component: 'SearchPage', query: 'test' });
logger.error('API failed', error, { component: 'ApiClient' });

// In React components (recommended)
function SearchPage() {
  const log = useLogger('SearchPage');
  log.info('Page loaded');
  log.error('Search failed', error, { query });
}
```

---

## Logger Service Usage Guide

### Log Levels

| Level | Method | Use Case | Sentry |
|-------|--------|----------|--------|
| `DEBUG` | `logger.debug()` | Detailed diagnostic info | None |
| `INFO` | `logger.info()` | Normal operational messages | None |
| `WARN` | `logger.warn()` | Potential issues, degraded state | Breadcrumb |
| `ERROR` | `logger.error()` | Errors that prevent normal operation | Exception capture |

### Basic Logging

```typescript
import { logger } from '@/lib/logger';

// Info - normal operations
logger.info('User logged in', {
  component: 'AuthProvider',
  action: 'login',
});

// Warning - potential issues
logger.warn('API response slow', {
  component: 'ApiClient',
  latency_ms: 5000,
});

// Error - with Error object (automatically captured to Sentry)
logger.error('Search failed', error, {
  component: 'SearchPage',
  action: 'search',
  query: searchQuery,
});

// Debug - only shown when LOG_LEVEL=debug
logger.debug('Render cycle', {
  component: 'ResultsList',
  itemCount: results.length,
});
```

### Context Interface

Every log call accepts an optional `LogContext` object:

```typescript
interface LogContext {
  component?: string;    // Component or module name
  action?: string;       // User action being performed
  [key: string]: unknown; // Any additional context
}
```

---

## Component Logging Patterns

### Using the `useLogger` Hook (Recommended)

The `useLogger` hook creates a child logger with preset component context:

```typescript
import { useLogger } from '@/lib/logger';

function SearchPage() {
  const log = useLogger('SearchPage');

  const handleSearch = async (query: string) => {
    log.info('Search started', { action: 'search', query });

    try {
      const results = await searchApi(query);
      log.info('Search completed', {
        action: 'search',
        results: results.length,
      });
      return results;
    } catch (error) {
      log.error('Search failed', error, { action: 'search', query });
      throw error;
    }
  };

  return <SearchForm onSearch={handleSearch} />;
}
```

**Benefits:**
- Component name automatically included in all logs
- No need to repeat `component: 'SearchPage'` in every call
- Cleaner, more readable code

### Direct Logger Usage

For non-component code or when you need more control:

```typescript
import { logger } from '@/lib/logger';

// In utility functions
export async function fetchWithRetry(url: string) {
  logger.debug('Fetch attempt', {
    component: 'fetchWithRetry',
    url,
  });

  try {
    const response = await fetch(url);
    if (!response.ok) {
      logger.warn('Fetch returned non-OK status', {
        component: 'fetchWithRetry',
        url,
        status: response.status,
      });
    }
    return response;
  } catch (error) {
    logger.error('Fetch failed', error, {
      component: 'fetchWithRetry',
      url,
    });
    throw error;
  }
}
```

---

## Error Handling with Logger

### Automatic Sentry Integration

Errors logged with `logger.error()` are automatically:
1. Output to console
2. Added as Sentry breadcrumb
3. Captured as Sentry exception (if Error object provided)

```typescript
// This automatically goes to Sentry
logger.error('Payment failed', error, {
  component: 'CheckoutPage',
  action: 'payment',
  orderId: order.id,
});
```

### Error Boundaries

Use with React Error Boundaries:

```typescript
import { Component, ErrorInfo, ReactNode } from 'react';
import { logger } from '@/lib/logger';

class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    logger.error('React error boundary caught error', error, {
      component: 'ErrorBoundary',
      componentStack: info.componentStack,
    });
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

### Try-Catch Pattern

```typescript
const log = useLogger('ComparePage');

const handleCompare = async (query: string) => {
  log.info('Compare started', { action: 'compare', query });

  try {
    const results = await compareApi(query);
    log.info('Compare completed', {
      action: 'compare',
      agents: results.length,
    });
    return results;
  } catch (error) {
    // Error automatically sent to Sentry with context
    log.error('Compare failed', error, {
      action: 'compare',
      query,
    });

    // Show user-friendly message
    toast.error('Comparison failed. Please try again.');
    return null;
  }
};
```

---

## Correlation ID Usage

Correlation IDs enable tracing a user action across frontend and backend logs.

### Starting a Correlation

```typescript
import { logger } from '@/lib/logger';

function SearchPage() {
  const handleSearch = async (query: string) => {
    // Generate and set correlation ID for this user action
    const correlationId = logger.generateCorrelationId();

    // All subsequent logs include this correlation ID
    logger.info('Search initiated', {
      component: 'SearchPage',
      action: 'search',
      query,
    });

    // Pass to API (backend will use it for its logs)
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-ID': correlationId,  // Backend picks this up
      },
      body: JSON.stringify({ query }),
    });

    // Clear when action completes
    logger.clearCorrelationId();
  };
}
```

### With SSE Streaming

```typescript
const handleStreamSearch = (query: string) => {
  const correlationId = logger.generateCorrelationId();

  // EventSource with correlation ID
  const url = new URL('/api/stream/search', window.location.origin);
  url.searchParams.set('query', query);
  url.searchParams.set('correlation_id', correlationId);

  const eventSource = new EventSource(url.toString());

  eventSource.onmessage = (event) => {
    // Logs automatically include correlation ID
    logger.debug('SSE message received', {
      component: 'SearchPage',
      messageType: event.data.type,
    });
  };

  eventSource.onerror = () => {
    logger.warn('SSE connection error', {
      component: 'SearchPage',
      action: 'stream',
    });
    eventSource.close();
    logger.clearCorrelationId();
  };
};
```

### Manual Correlation ID

```typescript
// Set a specific correlation ID (e.g., from URL parameter)
logger.setCorrelationId('existing-correlation-id');

// Get current correlation ID
const currentId = logger.correlationId;

// Clear when done
logger.clearCorrelationId();
```

---

## Child Loggers

Child loggers inherit context and add preset fields to all logs:

```typescript
import { logger } from '@/lib/logger';

// Create child logger with preset context
const searchLog = logger.child({
  component: 'SearchModule',
  feature: 'hybrid-search',
});

// All calls include component and feature
searchLog.info('Initializing');  // Has component: 'SearchModule', feature: 'hybrid-search'
searchLog.debug('Cache check', { cacheKey: 'abc' });
searchLog.error('Failed', error, { stage: 'embedding' });
```

### Nested Child Loggers

```typescript
const moduleLog = logger.child({ component: 'SearchModule' });
const searcherLog = moduleLog.child({ submodule: 'QuranSearcher' });

// Logs include both component and submodule
searcherLog.info('Search started');
```

---

## Performance Logging

### Using `logPerformance` Helper

For measuring operation latency:

```typescript
import { logPerformance } from '@/lib/logger';

async function searchWithTiming(query: string) {
  // Start timing
  const endTiming = logPerformance('search', {
    component: 'SearchPage',
    action: 'search',
  });

  const results = await searchApi(query);

  // End timing and log
  endTiming({ results: results.length });

  return results;
}
```

**Output (Development):**
```
[10:30:01] INFO [SearchPage] search completed {latency_ms=150.25, results=10}
```

**Output (Production JSON):**
```json
{
  "timestamp": "2024-01-15T10:30:01.500Z",
  "level": "INFO",
  "message": "search completed",
  "component": "SearchPage",
  "action": "search",
  "operation": "search",
  "latency_ms": 150.25,
  "context": { "results": 10 }
}
```

### Manual Performance Logging

```typescript
const log = useLogger('ComparePage');

const handleCompare = async (query: string) => {
  const start = performance.now();

  const results = await compareApi(query);

  const latencyMs = performance.now() - start;
  log.info('Compare completed', {
    action: 'compare',
    latency_ms: latencyMs,
    agents: results.length,
  });

  return results;
};
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_LOG_LEVEL` | `info` | Minimum log level (`debug`, `info`, `warn`, `error`) |

### Configuration in `frontend/.env.local`

```env
# Development (verbose)
NEXT_PUBLIC_LOG_LEVEL=debug

# Production (errors and warnings only)
NEXT_PUBLIC_LOG_LEVEL=warn
```

### Runtime Level Change

```typescript
import { logger, LogLevel } from '@/lib/logger';

// Temporarily enable debug logs
logger.setLevel(LogLevel.DEBUG);

// Reset to default
logger.setLevel(LogLevel.INFO);
```

---

## Code Examples

### Complete Component Example

```typescript
'use client';

import { useState } from 'react';
import { useLogger, logPerformance } from '@/lib/logger';
import { logger } from '@/lib/logger';
import { toast } from 'sonner';

interface SearchResult {
  id: string;
  text: string;
  score: number;
}

export function SearchPage() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const log = useLogger('SearchPage');

  const handleSearch = async (query: string) => {
    // Start correlation for this user action
    const correlationId = logger.generateCorrelationId();
    log.info('Search initiated', { action: 'search', queryLength: query.length });

    // Start performance timing
    const endTiming = logPerformance('search', {
      component: 'SearchPage',
    });

    setIsLoading(true);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Correlation-ID': correlationId,
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        log.warn('Search returned error status', {
          action: 'search',
          status: response.status,
        });
        throw new Error(`Search failed: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results);

      // Log performance with result count
      endTiming({ results: data.results.length });

    } catch (error) {
      log.error('Search failed', error, {
        action: 'search',
        queryLength: query.length,
      });
      toast.error('Search failed. Please try again.');
    } finally {
      setIsLoading(false);
      logger.clearCorrelationId();
    }
  };

  return (
    <div>
      <SearchForm onSearch={handleSearch} isLoading={isLoading} />
      <ResultsList results={results} />
    </div>
  );
}
```

### API Client Example

```typescript
// lib/api/client.ts
import { logger } from '@/lib/logger';

const apiLog = logger.child({ component: 'ApiClient' });

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const correlationId = logger.correlationId || crypto.randomUUID();

  apiLog.debug('API request starting', {
    action: 'request',
    endpoint,
    method: options.method || 'GET',
  });

  const start = performance.now();

  try {
    const response = await fetch(endpoint, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-ID': correlationId,
        ...options.headers,
      },
    });

    const latencyMs = performance.now() - start;

    if (!response.ok) {
      apiLog.warn('API returned error status', {
        action: 'response',
        endpoint,
        status: response.status,
        latency_ms: latencyMs,
      });
      throw new ApiError(response.status, await response.text());
    }

    apiLog.debug('API request completed', {
      action: 'response',
      endpoint,
      status: response.status,
      latency_ms: latencyMs,
    });

    return response.json();

  } catch (error) {
    apiLog.error('API request failed', error, {
      action: 'request',
      endpoint,
    });
    throw error;
  }
}
```

### SSE Streaming Example

```typescript
// lib/hooks/use-sse.ts
import { useCallback, useState } from 'react';
import { logger, useLogger } from '@/lib/logger';

export function useSSE(endpoint: string) {
  const [data, setData] = useState<unknown[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const log = useLogger('useSSE');

  const startStream = useCallback((query: string) => {
    const correlationId = logger.generateCorrelationId();
    log.info('SSE stream starting', { action: 'connect', endpoint });

    const url = new URL(endpoint, window.location.origin);
    url.searchParams.set('query', query);
    url.searchParams.set('correlation_id', correlationId);

    const eventSource = new EventSource(url.toString());
    setIsStreaming(true);
    setData([]);

    eventSource.onmessage = (event) => {
      const message = JSON.parse(event.data);
      log.debug('SSE message received', {
        action: 'message',
        type: message.type,
      });
      setData((prev) => [...prev, message]);

      if (message.type === 'complete') {
        log.info('SSE stream completed', { action: 'complete' });
        eventSource.close();
        setIsStreaming(false);
        logger.clearCorrelationId();
      }
    };

    eventSource.onerror = () => {
      log.warn('SSE connection error', { action: 'error', endpoint });
      eventSource.close();
      setIsStreaming(false);
      logger.clearCorrelationId();
    };
  }, [endpoint, log]);

  return { data, isStreaming, startStream };
}
```

---

## Console Output Examples

### Development (Pretty-Printed)

```
[10:30:00] INFO [SearchPage] Search initiated {corr=abc12345, queryLength=25}
[10:30:00] DEBUG [ApiClient] API request starting {corr=abc12345, endpoint=/api/search}
[10:30:01] DEBUG [ApiClient] API request completed {corr=abc12345, latency_ms=150.25}
[10:30:01] INFO [SearchPage] search completed {corr=abc12345, latency_ms=155.50, results=10}
```

### Production (JSON)

```json
{"timestamp":"2024-01-15T10:30:00.123Z","level":"INFO","message":"Search initiated","component":"SearchPage","correlationId":"abc12345-...","context":{"queryLength":25}}
{"timestamp":"2024-01-15T10:30:01.500Z","level":"INFO","message":"search completed","component":"SearchPage","correlationId":"abc12345-...","context":{"latency_ms":155.5,"results":10}}
```

---

## Sentry Integration Details

### Breadcrumbs

Warnings automatically create Sentry breadcrumbs:

```typescript
logger.warn('Cache miss', { component: 'SearchCache', key: 'abc' });
// Creates breadcrumb: { category: 'SearchCache', message: 'Cache miss', level: 'warning' }
```

### Exception Capture

Errors with Error objects are captured:

```typescript
logger.error('Search failed', error, {
  component: 'SearchPage',
  action: 'search',
  query: 'test query',
});
// Sentry receives:
// - Exception with stack trace
// - Tags: component=SearchPage, action=search
// - Extra: { query: 'test query' }
```

### User Context

Set Sentry user context separately (handled by auth provider):

```typescript
import * as Sentry from '@sentry/nextjs';

// In auth provider
Sentry.setUser({ id: user.id });
```

---

## Anti-Patterns

**Never:**

```typescript
// Bad: Using console.log directly
console.log('Search started');

// Bad: Missing component context
logger.info('Something happened');  // Which component?

// Bad: Swallowing errors
try {
  await doSomething();
} catch (e) {
  // Silent failure!
}

// Bad: Not using useLogger in components
function MyComponent() {
  // Repeating component name in every call
  logger.info('...', { component: 'MyComponent' });
  logger.info('...', { component: 'MyComponent' });
}
```

**Always:**

```typescript
// Good: Using logger with context
logger.info('Search started', {
  component: 'SearchPage',
  action: 'search',
});

// Good: Using useLogger in components
function MyComponent() {
  const log = useLogger('MyComponent');
  log.info('Initialized');
  log.info('Action performed');
}

// Good: Logging and re-throwing errors
try {
  await doSomething();
} catch (error) {
  log.error('Operation failed', error, { context: 'details' });
  throw error;  // Or handle appropriately
}
```

---

## TypeScript Types

```typescript
// Log levels
enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

// Log context
interface LogContext {
  component?: string;
  action?: string;
  [key: string]: unknown;
}

// Structured log entry
interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  correlationId?: string;
  component?: string;
  action?: string;
  context?: Record<string, unknown>;
  error?: {
    name: string;
    message: string;
    stack?: string;
  };
}
```
