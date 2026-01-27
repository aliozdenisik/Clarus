'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { toast } from 'sonner';
import * as Sentry from '@sentry/nextjs';

/**
 * SSE Message format from backend
 */
interface SSEMessage {
  type?: 'token' | 'complete' | 'error' | 'section' | 'paragraph';
  content?: string;
  result?: unknown;
  error?: string;
  status?: string;
  message?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  verse_details?: any;
  token?: string;
  done?: boolean;
}

/**
 * Return type for useSSE hook
 */
export interface UseSSEReturn {
  data: SSEMessage[];
  isStreaming: boolean;
  error: string | null;
  startStream: (url: string) => void;
  stopStream: () => void;
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
const MAX_RETRIES = 3;

export function useSSE(): UseSSEReturn {
  const [data, setData] = useState<SSEMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const currentUrlRef = useRef<string | null>(null);
  const retryCountRef = useRef(0);
  const startStreamInternalRef = useRef<((url: string) => void) | null>(null);

  const startStreamInternal = useCallback((url: string) => {
    // Clean up any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // Store current URL for reconnection
    currentUrlRef.current = url;

    try {
      // Create EventSource with credentials for auth
      const eventSource = new EventSource(url, {
        withCredentials: true,
      });

      eventSourceRef.current = eventSource;

      /**
       * Handle incoming messages
       * Expected format: data: {"type": "token", "content": "..."}
       */
      eventSource.onmessage = (event: MessageEvent) => {
        try {
          const message: SSEMessage = JSON.parse(event.data);

          setData((prevData) => [...prevData, message]);

          // Close stream on completion
          if (message.type === 'complete') {
            eventSource.close();
            setIsStreaming(false);
          }
        } catch (parseError) {
           const errorMsg =
             parseError instanceof Error
               ? parseError.message
               : 'Failed to parse message';
           Sentry.captureException(parseError, { tags: { source: 'sse-parse' } });
           setError(errorMsg);
           eventSource.close();
           setIsStreaming(false);
         }
      };

      /**
       * Handle connection open
       */
      eventSource.onopen = () => {
        setError(null);
        retryCountRef.current = 0;
      };

      /**
       * Handle errors with reconnection logic
       */
      eventSource.onerror = (event: Event) => {
        const eventSource = event.target as EventSource;
        eventSource.close();

        if (eventSource.readyState === EventSource.CLOSED) {
          // Check if we should retry
          if (retryCountRef.current < MAX_RETRIES && currentUrlRef.current) {
            // Calculate exponential backoff: 1s, 2s, 4s
            const delay = Math.pow(2, retryCountRef.current) * 1000;
            
            toast.info('Connection lost', {
              description: `Reconnecting... (${retryCountRef.current + 1}/${MAX_RETRIES})`,
            });

            setTimeout(() => {
              retryCountRef.current += 1;
              startStreamInternalRef.current?.(currentUrlRef.current!);
            }, delay);
           } else {
             // Max retries reached - fall back to POST
             Sentry.captureException(new Error('SSE connection failed after max retries'), {
               tags: { source: 'sse-connection' },
             });
             setError('Connection failed after 3 retries. Falling back to standard request.');
             setIsStreaming(false);
             toast.error('Connection failed', {
               description: 'Falling back to standard request...',
             });
           }
        }
      };
     } catch (err) {
       const errorMsg =
         err instanceof Error ? err.message : 'Failed to start stream';
       Sentry.captureException(err, { tags: { source: 'sse-init' } });
       setError(errorMsg);
       setIsStreaming(false);
     }
  }, []);

  // Store function reference for recursive calls (in effect to avoid render-time ref update)
  useEffect(() => {
    startStreamInternalRef.current = startStreamInternal;
  }, [startStreamInternal]);

  const startStream = useCallback((url: string) => {
    // Reset state for new stream
    setData([]);
    setError(null);
    setIsStreaming(true);
    retryCountRef.current = 0;
    
    startStreamInternal(url);
  }, [startStreamInternal]);

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  return {
    data,
    isStreaming,
    error,
    startStream,
    stopStream,
  };
}
