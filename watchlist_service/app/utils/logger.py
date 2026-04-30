"""
JSON Structured Logger for Watchlist Service.

Every log line is valid JSON — grep-able, parseable by Datadog/Loki/CloudWatch
without any extra parsing configuration.

Replaces the plain-text formatter from the original logger.py.
All existing `logger.info(...)` / `logger.warning(...)` calls work unchanged.
"""
import json
import logging
import sys
import time
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Formats each log record as a single-line JSON object."""

    SERVICE_NAME = "watchlist_service"

    def format(self, record: logging.LogRecord) -> str:
        log: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "service": self.SERVICE_NAME,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Attach any extra fields passed via logger.info("msg", extra={...})
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith("_"):
                log[key] = value

        if record.exc_info:
            log["exc"] = self.formatException(record.exc_info)

        return json.dumps(log, default=str)


def setup_logger(name: str = "watchlist_service") -> logging.Logger:
    lgr = logging.getLogger(name)
    lgr.setLevel(logging.INFO)

    if not lgr.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JsonFormatter())
        lgr.addHandler(handler)

    # Silence noisy SQLAlchemy engine logs in production
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return lgr


logger = setup_logger()
