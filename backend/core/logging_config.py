"""
logging_config.py
Shared logging configuration for the entire backend package.
Call configure_logging() once at application startup.
"""
import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure root logger with a consistent format for the entire application.

    Args:
        level: Logging level (default: INFO). Use logging.DEBUG for verbose output.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    # Silence overly chatty third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Convenience helper. Usage:
        from backend.core.logging_config import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
