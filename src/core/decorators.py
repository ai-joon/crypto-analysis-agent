"""Decorators for common functionality."""

import functools
import logging
from typing import Callable, TypeVar, ParamSpec

from src.core.exceptions import CryptoAnalysisError

P = ParamSpec("P")
T = TypeVar("T")

logger = logging.getLogger(__name__)


def handle_errors(
    error_message: str = "An error occurred",
    reraise: bool = False,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to handle exceptions and log them.

    Args:
        error_message: Custom error message prefix
        reraise: If True, re-raise the exception after logging

    Returns:
        Decorated function
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except CryptoAnalysisError:
                # Re-raise application-specific errors
                raise
            except Exception as e:
                logger.error(
                    f"{error_message} in {func.__name__}: {str(e)}", exc_info=True
                )
                if reraise:
                    raise
                raise CryptoAnalysisError(f"{error_message}: {str(e)}") from e

        return wrapper

    return decorator


def validate_input(
    validator: Callable[[str], bool],
    error_message: str = "Invalid input",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to validate function input.

    Args:
        validator: Function that returns True if input is valid
        error_message: Error message if validation fails

    Returns:
        Decorated function
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Validate first string argument
            if args and isinstance(args[0], str):
                if not validator(args[0]):
                    raise ValueError(f"{error_message}: {args[0]}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
