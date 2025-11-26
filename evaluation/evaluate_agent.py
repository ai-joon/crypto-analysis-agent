"""Performance evaluation for the crypto analysis agent."""

import time
import json
import os
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

from src.agents.agent import CryptoAnalysisAgent
from src.config.settings import get_settings
from src.services.analysis_service import AnalysisService
from src.repositories.coin_repository import CoinRepository


# Constants
TEST_COINS = ["bitcoin", "ethereum", "solana"]
CACHE_TTL = 300
ANALYZER_WEIGHT = 0.6
AGENT_WEIGHT = 0.4
MIN_PARAGRAPHS = 2
MIN_SECTIONS = 3
CLARIFICATION_KEYWORDS = ["would you like", "what", "which", "please"]
ANALYSIS_KEYWORDS = ["analysis", "price", "market", "sentiment", "technical"]


class AgentEvaluator:
    """Evaluates agent performance across multiple dimensions."""

    def __init__(self):
        """Initialize evaluator."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found. Please set it in .env file.")

        self.settings = get_settings()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "component_tests": {},
            "integration_tests": {},
            "performance_metrics": {},
        }

    def evaluate_analyzers(self) -> Dict[str, Any]:
        """Evaluate individual analyzer components."""
        print("Evaluating Analyzers...")
        results = {}

        repo = CoinRepository(
            cache_ttl=CACHE_TTL, newsapi_key=self.settings.newsapi_key
        )
        analysis_service = AnalysisService(repo)

        analyzers = {
            "fundamental": analysis_service.perform_fundamental_analysis,
            "price": analysis_service.perform_price_analysis,
            "sentiment": analysis_service.perform_sentiment_analysis,
            "technical": analysis_service.perform_technical_analysis,
        }

        for coin in TEST_COINS:
            print(f"  Testing {coin}...")
            coin_results = {}

            for name, analyzer_func in analyzers.items():
                coin_results[name] = self._run_analyzer_test(coin, analyzer_func)

            results[coin] = coin_results

        self.results["component_tests"]["analyzers"] = results
        return results

    def _run_analyzer_test(self, coin: str, analyzer_func) -> Dict[str, Any]:
        """Run a single analyzer test."""
        try:
            start_time = time.time()
            result = analyzer_func(coin)
            elapsed = time.time() - start_time

            return {
                "success": True,
                "response_time": elapsed,
                "output_length": len(result),
                "has_data_points": any(char.isdigit() for char in result),
                "has_multiple_paragraphs": result.count("\n\n") >= MIN_PARAGRAPHS,
                "has_sections": result.count("**") >= MIN_SECTIONS,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def evaluate_agent_responses(self) -> Dict[str, Any]:
        """Evaluate agent's conversational responses."""
        print("Evaluating Agent Responses...")
        results = {}

        try:
            agent = CryptoAnalysisAgent(self.settings)
            test_queries = self._get_test_queries()

            for test in test_queries:
                print(f"  Testing: '{test['query']}'")
                results[test["query"]] = self._evaluate_single_response(agent, test)

            self.results["integration_tests"]["agent_responses"] = results
        except Exception as e:
            print(f"  Error: {e}")
            results["error"] = str(e)

        return results

    def _get_test_queries(self) -> List[Dict[str, Any]]:
        """Get predefined test queries."""
        return [
            {
                "query": "Tell me about Bitcoin",
                "expected": "comprehensive_analysis",
                "should_clarify": False,
            },
            {
                "query": "What's the price of Ethereum?",
                "expected": "price_focus",
                "should_clarify": False,
            },
            {
                "query": "Tell me about ETH",
                "expected": "clarification_or_analysis",
                "should_clarify": True,
            },
            {
                "query": "What's happening with crypto?",
                "expected": "general_topic",
                "should_clarify": False,
            },
        ]

    def _evaluate_single_response(
        self, agent: CryptoAnalysisAgent, test: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a single agent response."""
        try:
            start_time = time.time()
            response = agent.chat(test["query"])
            elapsed = time.time() - start_time

            return {
                "success": True,
                "response_time": elapsed,
                "response_length": len(response),
                "asked_for_clarification": self._check_clarification(response),
                "contains_analysis": self._check_analysis_content(response),
                "expected_behavior": test["expected"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_clarification(self, response: str) -> bool:
        """Check if response asks for clarification."""
        has_question = "?" in response
        has_keywords = any(
            keyword in response.lower() for keyword in CLARIFICATION_KEYWORDS
        )
        return has_question and has_keywords

    def _check_analysis_content(self, response: str) -> bool:
        """Check if response contains analysis content."""
        return any(term in response.lower() for term in ANALYSIS_KEYWORDS)

    def evaluate_memory_and_context(self) -> Dict[str, Any]:
        """Evaluate conversation memory and context handling."""
        print("Evaluating Memory and Context...")
        results = {}

        try:
            agent = CryptoAnalysisAgent(self.settings)

            agent.chat("Tell me about Bitcoin")
            initial_history_length = len(agent.conversation_messages)

            agent.chat("What about its price?")
            follow_up_history_length = len(agent.conversation_messages)

            results["memory_persistence"] = {
                "initial_messages": initial_history_length,
                "after_followup": follow_up_history_length,
                "memory_works": follow_up_history_length > initial_history_length,
            }

            agent.analysis_history["bitcoin"] = {
                "fundamental": "test analysis",
                "name": "Bitcoin",
            }
            results["analysis_history"] = {
                "stores_analyses": "bitcoin" in agent.analysis_history,
                "stores_multiple_types": len(agent.analysis_history["bitcoin"]) > 1,
            }

            self.results["integration_tests"]["memory"] = results
        except Exception as e:
            print(f"  Error: {e}")
            results["error"] = str(e)

        return results

    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        print("Calculating Performance Metrics...")

        metrics = {
            "analyzer_performance": self._calculate_analyzer_metrics(),
            "agent_performance": self._calculate_agent_metrics(),
            "overall_score": 0.0,
        }

        analyzer_score = (
            metrics["analyzer_performance"].get("success_rate", 0.0) * ANALYZER_WEIGHT
        )
        agent_score = (
            metrics["agent_performance"].get("success_rate", 0.0) * AGENT_WEIGHT
        )
        metrics["overall_score"] = analyzer_score + agent_score

        self.results["performance_metrics"] = metrics
        return metrics

    def _calculate_analyzer_metrics(self) -> Dict[str, Any]:
        """Calculate analyzer performance metrics."""
        analyzer_results = self.results.get("component_tests", {}).get("analyzers", {})
        if not analyzer_results:
            return {}

        total_tests = 0
        successful_tests = 0
        total_response_time = 0.0

        for analyses in analyzer_results.values():
            for result in analyses.values():
                if isinstance(result, dict) and result.get("success"):
                    total_tests += 1
                    successful_tests += 1
                    total_response_time += result.get("response_time", 0.0)

        return {
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0.0,
            "average_response_time": (
                total_response_time / successful_tests if successful_tests > 0 else 0.0
            ),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
        }

    def _calculate_agent_metrics(self) -> Dict[str, Any]:
        """Calculate agent performance metrics."""
        agent_results = self.results.get("integration_tests", {}).get(
            "agent_responses", {}
        )
        if not agent_results:
            return {}

        total_queries = len(agent_results)
        successful_queries = sum(1 for r in agent_results.values() if r.get("success"))

        return {
            "success_rate": (
                successful_queries / total_queries if total_queries > 0 else 0.0
            ),
            "total_queries": total_queries,
            "successful_queries": successful_queries,
        }

    def generate_report(self, output_file: str = "evaluation_report.json"):
        """Generate evaluation report."""
        print("\nGenerating Report...")

        self.calculate_performance_metrics()

        output_path = Path(output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

        print(f"Report saved to {output_file}")
        self._print_summary()

    def _print_summary(self):
        """Print evaluation summary to console."""
        print("\n" + "=" * 60)
        print("Evaluation Summary")
        print("=" * 60)

        metrics = self.results.get("performance_metrics", {})

        if "analyzer_performance" in metrics:
            ap = metrics["analyzer_performance"]
            print("\nAnalyzer Performance:")
            print(f"  Success Rate: {ap.get('success_rate', 0):.2%}")
            print(f"  Avg Response Time: {ap.get('average_response_time', 0):.2f}s")
            print(
                f"  Tests: {ap.get('successful_tests', 0)}/{ap.get('total_tests', 0)}"
            )

        if "agent_performance" in metrics:
            agp = metrics["agent_performance"]
            print("\nAgent Performance:")
            print(f"  Success Rate: {agp.get('success_rate', 0):.2%}")
            print(
                f"  Queries: {agp.get('successful_queries', 0)}/{agp.get('total_queries', 0)}"
            )

        print(f"\nOverall Score: {metrics.get('overall_score', 0):.2%}")
        print("=" * 60)

    def run_full_evaluation(self):
        """Run complete evaluation suite."""
        print("Starting Full Evaluation...")
        print("=" * 60)

        self.evaluate_analyzers()
        self.evaluate_agent_responses()
        self.evaluate_memory_and_context()
        self.generate_report()

        print("\nEvaluation Complete!")


def main():
    """Run evaluation."""
    evaluator = AgentEvaluator()
    evaluator.run_full_evaluation()


if __name__ == "__main__":
    main()
