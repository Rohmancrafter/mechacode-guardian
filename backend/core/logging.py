"""
Structured request logging for MechaCode Guardian.

Each log record carries the fields required by NFR-11:
  session_id, query_hash (not raw query), provider_used, latency_ms,
  confidence_band, escalation_flag.

Usage:
    from backend.core.logging import get_logger, log_request
    logger = get_logger(__name__)
    log_request(logger, session_id=sid, ...)
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from typing import Any


def configure_root_logger(level: str = "INFO") -> None:
    """Configure the root logger with a structured JSON formatter."""
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_StructuredFormatter())
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Call configure_root_logger() once at startup."""
    return logging.getLogger(name)


class _StructuredFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Attach any extra fields added via log_request()
        for key in ("session_id", "provider", "latency_ms",
                    "confidence_band", "escalation_flag",
                    "event", "query_hash"):
            if hasattr(record, key):
                log_obj[key] = getattr(record, key)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


def _hash_query(query: str) -> str:
    """Return a short SHA-256 prefix of the query — never the raw text (NFR-06)."""
    return hashlib.sha256(query.encode()).hexdigest()[:12]


def log_request(
    logger: logging.Logger,
    *,
    session_id: str,
    query: str,
    provider: str,
    latency_ms: float,
    confidence_band: str,
    escalation_flag: bool,
    extra_event: str | None = None,
) -> None:
    """Emit a single structured log line for a diagnosis request (NFR-11)."""
    logger.info(
        "diagnosis_request",
        extra={
            "session_id": session_id,
            "query_hash": _hash_query(query),
            "provider": provider,
            "latency_ms": round(latency_ms, 2),
            "confidence_band": confidence_band,
            "escalation_flag": escalation_flag,
            "event": extra_event or "diagnosis_request",
        },
    )


class Timer:
    """Context manager that measures elapsed wall-clock time in milliseconds."""

    def __init__(self) -> None:
        self._start: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_: Any) -> None:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000
