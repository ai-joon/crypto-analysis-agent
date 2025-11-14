"""Main entry point for the Crypto Token Analysis Chat Agent."""

from dotenv import load_dotenv

from src.ui.cli import CLIInterface
from src.core.logging_config import setup_logging
from src.config.settings import get_settings


def main() -> None:
    """
    Main entry point for the application.

    Initializes logging, loads configuration, and starts the CLI interface.
    """
    # Load environment variables
    load_dotenv()

    try:
        # Initialize settings (this will validate configuration)
        settings = get_settings()

        # Setup logging
        setup_logging(verbose=settings.verbose)

        # Create and run CLI interface
        cli = CLIInterface()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        print("Please check your configuration and try again.")
        raise


if __name__ == "__main__":
    main()
