#!/usr/bin/env python3
"""Check if .env file is properly configured."""

import os
from pathlib import Path
from dotenv import load_dotenv


def main():
    """Check environment configuration."""
    print("=" * 60)
    print("ENVIRONMENT CONFIGURATION CHECK")
    print("=" * 60)
    print()

    # Check if .env file exists
    project_root = Path(__file__).parent
    env_file = project_root / ".env"

    if env_file.exists():
        print(f"Found .env file at: {env_file}")
    else:
        print(f"Error: .env file not found at: {env_file}")
        print(f"   Please create a .env file in the project root.")
        print(f"   You can copy env.template to .env:")
        print(f"   cp env.template .env")
        return 1

    # Load .env file
    load_dotenv(dotenv_path=env_file)

    # Check required variables
    print("\nChecking environment variables:")
    print()

    required_vars = {
        "OPENAI_API_KEY": "Required - Your OpenAI API key",
    }

    optional_vars = {
        "NEWSAPI_KEY": "Optional - For news features",
        "OPENAI_MODEL": "Optional - Model to use (default: gpt-4o-mini)",
        "CACHE_TTL": "Optional - Cache duration in seconds (default: 300)",
    }

    all_good = True

    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            # Mask the key for security
            masked = value[:7] + "..." + value[-4:] if len(value) > 11 else "***"
            print(f"  OK {var_name}: {masked}")
            print(f"     {description}")
        else:
            print(f"  ERROR {var_name}: NOT SET")
            print(f"     {description}")
            all_good = False
        print()

    print("Optional variables:")
    for var_name, description in optional_vars.items():
        value = os.getenv(var_name)
        if value:
            print(f"  OK {var_name}: Set")
        else:
            print(f"  - {var_name}: Not set (using default)")
        print(f"     {description}")
        print()

    if all_good:
        print("=" * 60)
        print("All required environment variables are set!")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("ERROR: Some required environment variables are missing.")
        print("   Please update your .env file and try again.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit(main())
