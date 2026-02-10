"""
Advanced Structured Logging Configuration for Clarus Backend

Industry-standard logging with:
- JSON format for production (machine-parseable)
- Console format for development (human-readable)
- Request correlation ID injection
- User context injection
- Performance metrics support

Uses ONLY standard Python logging - no external libraries.
"""

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Optional, Any
from dataclasses import dataclass
from contextvars import ContextVar

# Context variables for request-scoped data
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[int]] = ContextVar("user_id", default=None)
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)
extra_context_var: ContextVar[dict] = ContextVar("extra_context", default={})


@dataclass
class LoggingConfig:
    """Logging configuration from environment."""

    level: str = "INFO"
    format: str = "console"  # "console" or "json"
    file_path: Optional[str] = None
    include_timestamp: bool = True
    include_module: bool = True

    @classmethod
    def from_settings(cls, settings: Any) -> "LoggingConfig":
        """Create config from app settings."""
        return cls(
            level=getattr(settings, "log_level", "INFO").upper(),
            format=getattr(settings, "log_format", "console").lower(),
            file_path=getattr(settings, "log_file", None),
        )


class JSONFormatter(logging.Formatter):
    """
    Structured JSON log formatter for production environments.

    Output format (single line):
    {"timestamp": "2024-01-15T10:30:00.123Z", "level": "INFO", "logger": "app.api.search",
     "message": "Search completed", "request_id": "abc123", "user_id": 42, "latency_ms": 150}
    """

    LEVEL_MAP = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }

    def format(self, record: logging.LogRecord) -> str:
        # Base log entry
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": self.LEVEL_MAP.get(record.levelno, "UNKNOWN"),
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context from contextvars
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id

        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_entry["correlation_id"] = correlation_id

        user_id = user_id_var.get()
        if user_id:
            log_entry["user_id"] = user_id

        # Add extra context
        extra_context = extra_context_var.get()
        if extra_context:
            log_entry.update(extra_context)

        # Add source location for errors
        if record.levelno >= logging.ERROR:
            log_entry["source"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add any extra attributes from the log record
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "exc_info",
                "exc_text",
                "thread",
                "threadName",
                "message",
                "taskName",
            ):
                try:
                    # Ensure value is JSON serializable
                    json.dumps(value)
                    log_entry[key] = value
                except (TypeError, ValueError):
                    log_entry[key] = str(value)

        return json.dumps(log_entry, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """
    Human-readable colored console formatter for development.

    Output format:
    [2024-01-15 10:30:00] INFO  app.api.search - Search completed [request_id=abc123, latency_ms=150]
    """

    # ANSI color codes
    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    def format(self, record: logging.LogRecord) -> str:
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Level with color
        color = self.COLORS.get(record.levelno, "")
        level = f"{color}{record.levelname:<7}{self.RESET}"

        # Logger name (shortened)
        logger_name = record.name
        if len(logger_name) > 30:
            parts = logger_name.split(".")
            logger_name = ".".join([p[0] for p in parts[:-1]] + [parts[-1]])

        # Message
        message = record.getMessage()

        # Context info
        context_parts = []

        request_id = request_id_var.get()
        if request_id:
            context_parts.append(f"req={request_id[:8]}")

        correlation_id = correlation_id_var.get()
        if correlation_id:
            context_parts.append(f"corr={correlation_id[:8]}")

        user_id = user_id_var.get()
        if user_id:
            context_parts.append(f"user={user_id}")

        # Add extra context
        extra_context = extra_context_var.get()
        for key, value in extra_context.items():
            if isinstance(value, float):
                context_parts.append(f"{key}={value:.2f}")
            else:
                context_parts.append(f"{key}={value}")

        # Build context string
        context_str = ""
        if context_parts:
            context_str = f" {self.DIM}[{', '.join(context_parts)}]{self.RESET}"

        # Base log line
        log_line = f"[{timestamp}] {level} {self.DIM}{logger_name}{self.RESET} - {message}{context_str}"

        # Add exception if present
        if record.exc_info:
            log_line += f"\n{self.COLORS[logging.ERROR]}{self.formatException(record.exc_info)}{self.RESET}"

        return log_line


class RequestContextFilter(logging.Filter):
    """
    Logging filter that injects request context into log records.

    This allows structured loggers to access context without
    explicitly passing it to each log call.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # Inject context vars into record for formatters that need them
        record.request_id = request_id_var.get()
        record.correlation_id = correlation_id_var.get()
        record.user_id = user_id_var.get()
        record.extra_context = extra_context_var.get()
        return True


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """
    Configure application-wide logging.

    Call this once at application startup (in lifespan).

    Args:
        config: Logging configuration. If None, uses defaults.
    """
    if config is None:
        config = LoggingConfig()

    # Get root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers.clear()

    # Set level
    level = getattr(logging, config.level.upper(), logging.INFO)
    root_logger.setLevel(level)

    # Create formatter based on format setting
    if config.format == "json":
        formatter = JSONFormatter()
    else:
        formatter = ConsoleFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestContextFilter())
    root_logger.addHandler(console_handler)

    # Optional file handler
    if config.file_path:
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            config.file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        # Always use JSON for file logs
        file_handler.setFormatter(JSONFormatter())
        file_handler.addFilter(RequestContextFilter())
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Log startup
    root_logger.info(
        f"Logging configured: level={config.level}, format={config.format}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a properly configured logger.

    Usage:
        from app.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened", extra={"key": "value"})
    """
    return logging.getLogger(name)


# Context managers for setting request context
class LogContext:
    """
    Context manager for setting logging context.

    Usage:
        with LogContext(request_id="abc123", user_id=42):
            logger.info("This log will include request_id and user_id")

    Or use the helper functions:
        set_request_id("abc123")
        set_user_id(42)
    """

    def __init__(
        self,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[int] = None,
        **extra: Any,
    ):
        self.request_id = request_id
        self.correlation_id = correlation_id
        self.user_id = user_id
        self.extra = extra
        self._tokens = []

    def __enter__(self) -> "LogContext":
        if self.request_id:
            self._tokens.append(request_id_var.set(self.request_id))
        if self.correlation_id:
            self._tokens.append(correlation_id_var.set(self.correlation_id))
        if self.user_id:
            self._tokens.append(user_id_var.set(self.user_id))
        if self.extra:
            current = extra_context_var.get().copy()
            current.update(self.extra)
            self._tokens.append(extra_context_var.set(current))
        return self

    def __exit__(self, *_args: Any) -> None:
        # Context vars automatically reset when their tokens go out of scope
        # We keep the tokens list for potential future manual reset
        self._tokens.clear()


# Helper functions for setting context
def set_request_id(request_id: str) -> None:
    """Set the current request ID for logging context."""
    request_id_var.set(request_id)


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for cross-service tracing."""
    correlation_id_var.set(correlation_id)


def set_user_id(user_id: int) -> None:
    """Set the current user ID for logging context."""
    user_id_var.set(user_id)


def set_extra_context(**kwargs: Any) -> None:
    """Add extra context fields to all subsequent logs in this context."""
    current = extra_context_var.get().copy()
    current.update(kwargs)
    extra_context_var.set(current)


def clear_context() -> None:
    """Clear all logging context (call at end of request)."""
    request_id_var.set(None)
    correlation_id_var.set(None)
    user_id_var.set(None)
    extra_context_var.set({})


# Performance logging helper
def log_performance(
    logger: logging.Logger,
    operation: str,
    latency_ms: float,
    **extra: Any,
) -> None:
    """
    Log a performance metric.

    Usage:
        start = time.perf_counter()
        # ... do work ...
        latency = (time.perf_counter() - start) * 1000
        log_performance(logger, "search", latency, collection="quran_tr", results=10)
    """
    logger.info(
        f"{operation} completed",
        extra={"operation": operation, "latency_ms": round(latency_ms, 2), **extra},
    )
