"""Command-line interface for the crypto analysis agent."""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from src.config.settings import get_settings
from src.agents.agent import CryptoAnalysisAgent


class CLIInterface:
    """Command-line interface for interacting with the crypto analysis agent."""

    def __init__(self):
        """Initialize CLI interface."""
        self.console = Console()
        self.settings = None
        self.agent = None

    def _print_welcome(self) -> None:
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

**Follow-up Questions (Context-Aware):**
- "What about its performance last week?" (refers to previously discussed token)
- "What are the risks?" (follow-up on earlier analysis)
- "What did you say about Bitcoin's sentiment earlier?" (references past conversation)
- "Compare this to the Ethereum analysis you did before" (compares multiple analyses)

**Commands:**
- Type your question naturally
- Type 'exit' or 'quit' to end the session
- Type 'clear' to reset the conversation
- Type 'cache' or 'stats' to view cache statistics
- Type 'help' for this message

*Note: This is educational information, not financial advice. Cryptocurrency investments are risky. Always DYOR (Do Your Own Research).*
        """

        self.console.print(
            Panel(Markdown(welcome_text), border_style="cyan", padding=(1, 2))
        )

    def _print_help(self) -> None:
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
- `cache` or `stats` - View semantic cache statistics
- `help` - Show this help message

**Tips:**
- Be specific with token names or symbols (BTC, Bitcoin, etc.)
- Ask follow-up questions naturally
- Reference earlier analyses for comparisons
        """

        self.console.print(
            Panel(Markdown(help_text), border_style="yellow", padding=(1, 2))
        )

    def _print_cache_stats(self) -> None:
        """Print semantic cache statistics."""
        if not self.agent:
            self.console.print("[red]Agent not initialized[/red]")
            return

        stats = self.agent.get_cache_stats()
        if not stats.get("enabled", False):
            self.console.print("[yellow]Semantic cache is not enabled[/yellow]")
            return

        stats_text = f"""
# Semantic Cache Statistics

**Cache Status:**
- Size: {stats.get('size', 0)} / {stats.get('max_size', 0)} entries
- Total Hits: {stats.get('total_hits', 0)}
- Average Hits per Entry: {stats.get('average_hits_per_entry', 0):.2f}

**Configuration:**
- Similarity Threshold: {stats.get('similarity_threshold', 0):.2f}
- TTL: {stats.get('ttl_seconds', 0)} seconds ({stats.get('ttl_seconds', 0) // 60} minutes)
        """

        self.console.print(
            Panel(Markdown(stats_text), border_style="blue", padding=(1, 2))
        )

    def _initialize_agent(self) -> bool:
        """
        Initialize the agent.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.settings = get_settings()
        except ValueError as e:
            self.console.print(
                f"[bold red]Error:[/bold red] {str(e)}\n"
                "Please create a .env file with your OpenAI API key.\n"
                "Example: OPENAI_API_KEY=sk-your-key-here",
                style="red",
            )
            return False

        self.console.print("\n[yellow]Initializing AI agent...[/yellow]")

        try:
            # Try GPT-4 first, fall back to GPT-3.5 if not available
            try:
                self.agent = CryptoAnalysisAgent(self.settings)
                self.console.print(
                    "[green]Agent initialized successfully with GPT-4![/green]\n"
                )
            except Exception as e:
                if (
                    "model_not_found" in str(e).lower()
                    or "does not exist" in str(e).lower()
                ):
                    self.console.print(
                        "[yellow]GPT-4 not available, using GPT-3.5-turbo instead...[/yellow]"
                    )
                    self.settings.openai_model = "gpt-3.5-turbo"
                    self.agent = CryptoAnalysisAgent(self.settings)
                    self.console.print(
                        "[green]Agent initialized successfully with GPT-3.5-turbo![/green]\n"
                    )
                else:
                    raise e
            return True
        except Exception as e:
            self.console.print(
                f"[bold red]Error initializing agent:[/bold red] {str(e)}", style="red"
            )
            return False

    def run(self) -> None:
        """Run the CLI interface."""
        self._print_welcome()

        if not self._initialize_agent():
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
                    self.console.print(
                        "\n[yellow]Thanks for using Crypto Analysis Agent! Goodbye![/yellow]\n"
                    )
                    break

                elif user_input_lower in ["clear", "reset"]:
                    self.agent.reset_conversation()
                    self.console.print("\n[green]Conversation memory cleared![/green]")
                    continue

                elif user_input_lower in ["help", "h", "?"]:
                    self._print_help()
                    continue

                elif user_input_lower in ["cache", "stats"]:
                    self._print_cache_stats()
                    continue

                # Process user input with agent
                self.console.print("\n[yellow]Agent is thinking...[/yellow]\n")

                response = self.agent.chat(user_input)

                # Display response
                self.console.print(
                    Panel(
                        Markdown(response),
                        title="[bold green]Agent Response[/bold green]",
                        border_style="green",
                        padding=(1, 2),
                    )
                )

            except KeyboardInterrupt:
                self.console.print(
                    "\n\n[yellow]Interrupted. Type 'exit' to quit or press Ctrl+C again.[/yellow]"
                )
                try:
                    confirm = Prompt.ask(
                        "\n[bold]Do you want to exit?[/bold]",
                        choices=["yes", "no"],
                        default="no",
                    )
                    if confirm == "yes":
                        self.console.print(
                            "\n[yellow]Thanks for using Crypto Analysis Agent! Goodbye![/yellow]\n"
                        )
                        break
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Goodbye![/yellow]\n")
                    break

            except Exception as e:
                self.console.print(
                    f"\n[bold red]Error:[/bold red] {str(e)}", style="red"
                )
                self.console.print(
                    "[yellow]Please try again with a different question.[/yellow]"
                )
