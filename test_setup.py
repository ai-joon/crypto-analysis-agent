"""Test script to verify the setup is correct."""

import os
import sys
from dotenv import load_dotenv


def print_status(message, status="info"):
    """Print colored status message."""
    colors = {
        "success": "\033[92m✓\033[0m",  # Green
        "error": "\033[91m✗\033[0m",  # Red
        "warning": "\033[93m⚠\033[0m",  # Yellow
        "info": "\033[94mℹ\033[0m",  # Blue
    }
    symbol = colors.get(status, "")
    print(f"{symbol} {message}")


def test_python_version():
    """Test Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_status(
            f"Python version: {version.major}.{version.minor}.{version.micro}",
            "success",
        )
        return True
    else:
        print_status(
            f"Python version {version.major}.{version.minor} is too old. Need 3.8+",
            "error",
        )
        return False


def test_imports():
    """Test required package imports."""
    packages = {
        "requests": "requests",
        "langchain": "langchain",
        "langchain_openai": "langchain-openai",
        "openai": "openai",
        "rich": "rich",
        "dotenv": "python-dotenv",
        "pandas": "pandas",
    }

    all_ok = True
    for module_name, package_name in packages.items():
        try:
            __import__(module_name)
            print_status(f"Package '{package_name}' is installed", "success")
        except ImportError:
            print_status(f"Package '{package_name}' is NOT installed", "error")
            all_ok = False

    return all_ok


def test_env_file():
    """Test .env file configuration."""
    load_dotenv()

    if not os.path.exists(".env"):
        print_status(".env file NOT found", "error")
        print("  → Create a .env file with: OPENAI_API_KEY=your-key-here")
        return False

    print_status(".env file found", "success")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print_status("OPENAI_API_KEY not set in .env file", "error")
        return False

    if api_key.startswith("sk-") and len(api_key) > 20:
        print_status("OPENAI_API_KEY looks valid", "success")
        return True
    else:
        print_status("OPENAI_API_KEY format looks incorrect", "warning")
        print("  → Make sure it starts with 'sk-' and is your actual API key")
        return False


def test_data_fetcher():
    """Test data fetcher functionality."""
    try:
        from src.data_fetcher import CryptoDataFetcher

        fetcher = CryptoDataFetcher()

        # Test coin ID resolution
        coin_id = fetcher.get_coin_id("bitcoin")
        if coin_id == "bitcoin":
            print_status("Data fetcher: Coin resolution works", "success")
        else:
            print_status("Data fetcher: Coin resolution failed", "error")
            return False

        # Test API connection
        try:
            data = fetcher.get_market_data("bitcoin")
            if data and data.get("current_price"):
                print_status(
                    f"Data fetcher: API connection works (BTC: ${data['current_price']:,.0f})",
                    "success",
                )
                return True
            else:
                print_status("Data fetcher: API returned invalid data", "error")
                return False
        except Exception as e:
            print_status(f"Data fetcher: API connection failed - {str(e)}", "error")
            return False

    except Exception as e:
        print_status(
            f"Data fetcher: Import or initialization failed - {str(e)}", "error"
        )
        return False


def test_openai_connection():
    """Test OpenAI API connection."""
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print_status("OpenAI: Cannot test - no API key", "warning")
            return False

        client = OpenAI(api_key=api_key)

        # Try a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
        )

        if response.choices:
            print_status("OpenAI: API connection works", "success")
            return True
        else:
            print_status("OpenAI: API returned invalid response", "error")
            return False

    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            print_status("OpenAI: Invalid API key", "error")
        elif "rate_limit" in error_msg.lower():
            print_status("OpenAI: Rate limit (but connection works)", "warning")
            return True
        else:
            print_status(f"OpenAI: Connection failed - {error_msg}", "error")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  Crypto Token Analysis Agent - Setup Test")
    print("=" * 60 + "\n")

    results = {
        "Python Version": test_python_version(),
        "Package Installation": test_imports(),
        "Environment Configuration": test_env_file(),
        "Data Fetcher": test_data_fetcher(),
        "OpenAI Connection": test_openai_connection(),
    }

    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60 + "\n")

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        color = "\033[92m" if result else "\033[91m"
        print(f"{color}{status}\033[0m - {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60 + "\n")

    if all_passed:
        print("\033[92m🎉 All tests passed! You're ready to run the agent.\033[0m")
        print("\nRun the agent with:")
        print("  python main.py")
    else:
        print("\033[91m⚠ Some tests failed. Please fix the issues above.\033[0m")
        print("\nCommon fixes:")
        print("  1. Install packages: pip install -r requirements.txt")
        print("  2. Create .env file with your OpenAI API key")
        print("  3. Check your internet connection")

    print("\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
