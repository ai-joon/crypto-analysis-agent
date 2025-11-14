"""Progress logging utility for clean, user-friendly progress messages."""

import sys
import os
from typing import Optional

# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


def _supports_color() -> bool:
    """Check if the terminal supports color output."""
    # Check if we're in a terminal
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Check for Windows
    if os.name == 'nt':
        # Windows 10+ supports ANSI colors
        return os.getenv('TERM') != 'dumb' or os.getenv('ANSICON') is not None
    
    # Unix-like systems
    return True


class ProgressLogger:
    """Simple progress logger that shows clean, structured progress messages with colors."""

    def __init__(self, enabled: bool = True, use_colors: Optional[bool] = None):
        """
        Initialize progress logger.

        Args:
            enabled: Whether to show progress messages
            use_colors: Whether to use colors (auto-detected if None)
        """
        self.enabled = enabled
        self.use_colors = use_colors if use_colors is not None else _supports_color()

    def _print(self, message: str, prefix: str = "→", color: Optional[str] = None) -> None:
        """
        Print a progress message with optional color.

        Args:
            message: Message to print
            prefix: Prefix symbol
            color: ANSI color code
        """
        if not self.enabled:
            return
        
        if self.use_colors and color:
            if prefix:
                print(f"{color}{prefix}{Colors.RESET} {color}{message}{Colors.RESET}", file=sys.stdout, flush=True)
            else:
                print(f"{color}{message}{Colors.RESET}", file=sys.stdout, flush=True)
        else:
            if prefix:
                print(f"{prefix} {message}", file=sys.stdout, flush=True)
            else:
                print(message, file=sys.stdout, flush=True)

    def api_call(self, service: str, action: str = "calling") -> None:
        """
        Log an API call.

        Args:
            service: Name of the API service (e.g., "CoinGecko", "NewsAPI")
            action: Action being performed (default: "calling")
        """
        self._print(
            f"{action} {service} API...",
            prefix="→",
            color=Colors.BRIGHT_CYAN
        )

    def success(self, message: str) -> None:
        """
        Log a success message.

        Args:
            message: Success message
        """
        self._print(
            f"✓ {message}",
            prefix="",
            color=Colors.BRIGHT_GREEN
        )

    def info(self, message: str) -> None:
        """
        Log an info message.

        Args:
            message: Info message
        """
        self._print(
            message,
            prefix="→",
            color=Colors.BRIGHT_BLUE
        )

    def warning(self, message: str) -> None:
        """
        Log a warning message.

        Args:
            message: Warning message
        """
        self._print(
            f"⚠ {message}",
            prefix="",
            color=Colors.BRIGHT_YELLOW
        )

    def error(self, message: str) -> None:
        """
        Log an error message.

        Args:
            message: Error message
        """
        self._print(
            f"✗ {message}",
            prefix="",
            color=Colors.BRIGHT_RED
        )


# Global progress logger instance
_progress_logger: Optional[ProgressLogger] = None


def get_progress_logger() -> ProgressLogger:
    """
    Get the global progress logger instance.

    Returns:
        ProgressLogger instance
    """
    global _progress_logger
    if _progress_logger is None:
        _progress_logger = ProgressLogger(enabled=True)
    return _progress_logger


def set_progress_logger(logger: ProgressLogger) -> None:
    """
    Set the global progress logger instance.

    Args:
        logger: ProgressLogger instance
    """
    global _progress_logger
    _progress_logger = logger

