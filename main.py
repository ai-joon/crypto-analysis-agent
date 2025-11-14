"""Main CLI interface for the Crypto Token Analysis Chat Agent."""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from src.agent import CryptoAnalysisAgent


def print_welcome(console: Console):
    """Print welcome message."""
    welcome_text = """
# Crypto Token Analysis Chat Agent

Welcome! I'm your AI-powered cryptocurrency analyst. I can help you analyze tokens across multiple dimensions:

**Available Analysis Types:**
- **Fundamental Analysis**: Market cap, volume, supply, tokenomics, liquidity
- **Price Analysis**: Trends, volatility, support/resistance levels
- **Sentiment Analysis**: Social media metrics, community engagement
- **Technical Analysis**: Moving averages, RSI, MACD, indicators

**Example Questions:**
- "Tell me about Bitcoin"
- "What's the price trend of Ethereum?"
- "Compare Bitcoin's sentiment to Ethereum"
- "What was the RSI for Solana you mentioned earlier?"

**Commands:**
- Type your question naturally
- Type 'exit' or 'quit' to end the session
- Type 'clear' to reset the conversation
- Type 'help' for this message

*Note: This is educational information, not financial advice. Cryptocurrency investments are risky. Always DYOR (Do Your Own Research).*
    """

    console.print(Panel(Markdown(welcome_text), border_style="cyan", padding=(1, 2)))


def print_help(console: Console):
    """Print help message."""
    help_text = """
# Help - How to Use This Agent

**Basic Usage:**
Simply type your question about any cryptocurrency. For example:
- "Tell me about Bitcoin"
- "Analyze Ethereum"
- "What's the market cap of Solana?"

**Analysis Types:**
The agent will intelligently choose which analyses to run based on your question:
- For general queries: Comprehensive analysis (all types)
- For price-related questions: Price + Technical analysis
- For community questions: Sentiment analysis
- For market metrics: Fundamental analysis

**Follow-up Questions:**
I remember our conversation context! You can ask:
- "What about its performance last week?"
- "How does that compare to Ethereum?"
- "What was Bitcoin's RSI earlier?"

**Commands:**
- `exit` or `quit` - End the session
- `clear` - Reset conversation memory
- `help` - Show this help message

**Tips:**
- Be specific with token names or symbols (BTC, Bitcoin, etc.)
- Ask follow-up questions naturally
- Reference earlier analyses for comparisons
    """

    console.print(Panel(Markdown(help_text), border_style="yellow", padding=(1, 2)))


def main():
    """Main function to run the CLI interface."""
    # Load environment variables
    load_dotenv()

    console = Console()

    # Check for OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        console.print(
            "[bold red]Error:[/bold red] OPENAI_API_KEY not found in environment variables.\n"
            "Please create a .env file with your OpenAI API key.\n"
            "Example: OPENAI_API_KEY=sk-your-key-here",
            style="red",
        )
        sys.exit(1)

    # Print welcome message
    print_welcome(console)

    # Initialize agent
    console.print("\n[yellow]Initializing AI agent...[/yellow]")

    try:
        # Try GPT-4 first, fall back to GPT-3.5 if not available
        try:
            agent = CryptoAnalysisAgent(openai_api_key, model="gpt-4")
            console.print(
                "[green]✓ Agent initialized successfully with GPT-4![/green]\n"
            )
        except Exception as e:
            if (
                "model_not_found" in str(e).lower()
                or "does not exist" in str(e).lower()
            ):
                console.print(
                    "[yellow]GPT-4 not available, using GPT-3.5-turbo instead...[/yellow]"
                )
                agent = CryptoAnalysisAgent(openai_api_key, model="gpt-3.5-turbo")
                console.print(
                    "[green]✓ Agent initialized successfully with GPT-3.5-turbo![/green]\n"
                )
            else:
                raise e
    except Exception as e:
        console.print(
            f"[bold red]Error initializing agent:[/bold red] {str(e)}", style="red"
        )
        sys.exit(1)

    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

            # Handle empty input
            if not user_input.strip():
                continue

            # Handle commands
            user_input_lower = user_input.lower().strip()

            if user_input_lower in ["exit", "quit", "q"]:
                console.print(
                    "\n[yellow]Thanks for using Crypto Analysis Agent! Goodbye![/yellow]\n"
                )
                break

            elif user_input_lower in ["clear", "reset"]:
                agent.reset_conversation()
                console.print("\n[green]✓ Conversation memory cleared![/green]")
                continue

            elif user_input_lower in ["help", "h", "?"]:
                print_help(console)
                continue

            # Process user input with agent
            console.print("\n[yellow]Agent is thinking...[/yellow]\n")

            response = agent.chat(user_input)

            # Display response
            console.print(
                Panel(
                    Markdown(response),
                    title="[bold green]Agent Response[/bold green]",
                    border_style="green",
                    padding=(1, 2),
                )
            )

        except KeyboardInterrupt:
            console.print(
                "\n\n[yellow]Interrupted. Type 'exit' to quit or press Ctrl+C again.[/yellow]"
            )
            try:
                # Give user a chance to exit gracefully
                confirm = Prompt.ask(
                    "\n[bold]Do you want to exit?[/bold]",
                    choices=["yes", "no"],
                    default="no",
                )
                if confirm == "yes":
                    console.print(
                        "\n[yellow]Thanks for using Crypto Analysis Agent! Goodbye![/yellow]\n"
                    )
                    break
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]\n")
                break

        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}", style="red")
            console.print(
                "[yellow]Please try again with a different question.[/yellow]"
            )


if __name__ == "__main__":
    main()
