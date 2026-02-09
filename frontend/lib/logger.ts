import * as Sentry from "@sentry/nextjs";

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

const LOG_LEVELS: Record<string, LogLevel> = {
  debug: LogLevel.DEBUG,
  info: LogLevel.INFO,
  warn: LogLevel.WARN,
  error: LogLevel.ERROR,
};

export interface LogContext {
  component?: string;
  action?: string;
  [key: string]: unknown;
}

interface StructuredLog {
  timestamp: string;
  level: keyof typeof LogLevel;
  message: string;
  correlationId?: string;
  component?: string;
  action?: string;
  context?: Record<string, unknown>;
}

class ChildLogger {
  constructor(
    private parent: Logger,
    private defaultContext: LogContext
  ) {}

  debug(message: string, context?: LogContext): void {
    this.parent.debug(message, { ...this.defaultContext, ...context });
  }

  info(message: string, context?: LogContext): void {
    this.parent.info(message, { ...this.defaultContext, ...context });
  }

  warn(message: string, context?: LogContext): void {
    this.parent.warn(message, { ...this.defaultContext, ...context });
  }

  error(message: string, error?: unknown, context?: LogContext): void {
    this.parent.error(message, error, { ...this.defaultContext, ...context });
  }
}

export class Logger {
  private static instance: Logger | undefined;
  private level: LogLevel;
  private correlationId?: string;

  private constructor() {
    const envLevel = process.env.NEXT_PUBLIC_LOG_LEVEL?.toLowerCase() || "info";
    this.level = LOG_LEVELS[envLevel] ?? LogLevel.INFO;
  }

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  setLevel(level: LogLevel): void {
    this.level = level;
  }

  setCorrelationId(correlationId: string): void {
    this.correlationId = correlationId;
  }

  clearCorrelationId(): void {
    this.correlationId = undefined;
  }

  generateCorrelationId(): string {
    const correlationId = crypto.randomUUID();
    this.setCorrelationId(correlationId);
    return correlationId;
  }

  child(defaultContext: LogContext): ChildLogger {
    return new ChildLogger(this, defaultContext);
  }

  debug(message: string, context?: LogContext): void {
    this.log(LogLevel.DEBUG, message, undefined, context);
  }

  info(message: string, context?: LogContext): void {
    this.log(LogLevel.INFO, message, undefined, context);
  }

  warn(message: string, context?: LogContext): void {
    this.log(LogLevel.WARN, message, undefined, context);
  }

  error(message: string, error?: unknown, context?: LogContext): void {
    this.log(LogLevel.ERROR, message, error, context);
  }

  private log(level: LogLevel, message: string, error?: unknown, context?: LogContext): void {
    if (level < this.level) {
      return;
    }

    const entry = this.buildEntry(level, message, context);
    const payload = JSON.stringify(entry);

    switch (level) {
      case LogLevel.DEBUG:
        console.debug(payload);
        break;
      case LogLevel.INFO:
        console.info(payload);
        break;
      case LogLevel.WARN:
        console.warn(payload);
        break;
      case LogLevel.ERROR:
      default:
        console.error(payload);
        break;
    }

    if (level >= LogLevel.WARN) {
      Sentry.addBreadcrumb({
        category: entry.component || "frontend",
        message: entry.message,
        level: level === LogLevel.ERROR ? "error" : "warning",
        data: {
          ...entry.context,
          action: entry.action,
          correlationId: entry.correlationId,
        },
      });
    }

    if (level === LogLevel.ERROR && error) {
      Sentry.captureException(error, {
        tags: {
          component: entry.component,
          action: entry.action,
          correlationId: entry.correlationId,
        },
        extra: entry.context,
      });
    }
  }

  private buildEntry(level: LogLevel, message: string, context?: LogContext): StructuredLog {
    const { component, action, ...rest } = context || {};

    return {
      timestamp: new Date().toISOString(),
      level: LogLevel[level] as keyof typeof LogLevel,
      message,
      correlationId: this.correlationId,
      component,
      action,
      context: Object.keys(rest).length > 0 ? rest : undefined,
    };
  }
}

export const logger = Logger.getInstance();

export function useLogger(component: string): ChildLogger {
  return logger.child({ component });
}

export function logPerformance(
  operation: string,
  context?: LogContext
): (extraContext?: Record<string, unknown>) => void {
  const startedAt = performance.now();

  return (extraContext?: Record<string, unknown>) => {
    logger.info(`${operation} completed`, {
      ...context,
      operation,
      latency_ms: performance.now() - startedAt,
      ...extraContext,
    });
  };
}
