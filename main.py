"""Main entry point for the Crypto Token Analysis Chat Agent."""

from dotenv import load_dotenv
from src.ui.cli import CLIInterface


def main():
    """Main entry point for the application."""
    # Load environment variables
    load_dotenv()
    
    # Create and run CLI interface
    cli = CLIInterface()
    cli.run()


if __name__ == "__main__":
    main()
