"""Logging configuration for the application."""

import logging
import sys


def setup_logging(level: int = logging.INFO, verbose: bool = False) -> logging.Logger:
    """
    Configure application-wide logging.

    Args:
        level: Logging level (default: INFO)
        verbose: If True, use DEBUG level and detailed formatting

    Returns:
        Configured logger instance
    """
    if verbose:
        level = logging.DEBUG
    else:
        # Suppress INFO and below for non-verbose mode
        # Only show WARNING and ERROR
        level = logging.WARNING

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger("src")
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler - only for warnings and errors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Suppress LangChain verbose output
    langchain_loggers = [
        "langchain",
        "langchain_core",
        "langchain_openai",
        "langsmith",
    ]
    for logger_name in langchain_loggers:
        langchain_logger = logging.getLogger(logger_name)
        langchain_logger.setLevel(logging.WARNING)
        langchain_logger.propagate = False

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
