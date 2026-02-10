"use client";

import * as Sentry from "@sentry/nextjs";
import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html>
      <body className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground">Something went wrong</h1>
          <p className="mt-2 text-muted-foreground">
            We&apos;ve been notified and are working on it.
          </p>
          <button
            onClick={reset}
            className="mt-4 rounded bg-primary px-4 py-2 text-primary-foreground"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
