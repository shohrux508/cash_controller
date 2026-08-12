from __future__ import annotations

import logging
import sys
from types import FrameType

from loguru import logger

from app.core.config import settings


class _InterceptHandler(logging.Handler):
    """Redirect all stdlib logging into Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logged message originated.
        frame: FrameType | None = logging.currentframe()
        depth = 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """Configure Loguru and intercept stdlib logging."""
    # Remove default Loguru sink.
    logger.remove()

    # Add sink based on LOG_FORMAT setting.
    if settings.log_format.lower() == "json":
        logger.add(
            sys.stderr,
            level=settings.log_level.upper(),
            serialize=True,
        )
    else:
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            level=settings.log_level.upper(),
            colorize=True,
        )

    # Intercept stdlib loggers.
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(logger_name).handlers = [_InterceptHandler()]
