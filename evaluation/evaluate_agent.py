"""Comprehensive evaluation script for the crypto analysis agent."""

import json
import time
import os
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

from src.agents.agent import CryptoAnalysisAgent
from src.config.settings import get_settings
from src.services.analysis_service import AnalysisService
from src.repositories.coin_repository import CoinRepository
from src.core.logging_config import get_logger
from llm_judge import LLMJudge
from evaluation.config import (
    PROJECT_ROOT,
    TEST_QUESTIONS_FILE,
    DEFAULT_REPORT_FILE,
    DEFAULT_TEST_COINS,
    DEFAULT_CACHE_TTL,
    ANSWER_TRUNCATE_LENGTH,
    ANALYZER_WEIGHT,
    AGENT_WEIGHT,
    ANALYZER_TYPES,
    MIN_PARAGRAPHS,
    MIN_SECTIONS,
    CLARIFICATION_KEYWORDS,
    ANALYSIS_KEYWORDS,
)
from evaluation.models import EvaluationReport

logger = get_logger(__name__)


def _load_environment() -> None:
    """Load environment variables from .env file."""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
    else:
        load_dotenv()


def _validate_api_key() -> None:
    """Validate that OpenAI API key is available.

    Raises:
        ValueError: If API key is not found
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables.\n"
            "Please ensure:\n"
            "1. A .env file exists in the project root\n"
            "2. The .env file contains: OPENAI_API_KEY=sk-your-key-here\n"
            "3. The .env file is in the same directory as main.py"
        )


class AgentEvaluator:
    """Evaluates agent performance across multiple dimensions."""

    def __init__(self):
        """Initialize evaluator."""
        _load_environment()
        _validate_api_key()

        self.settings = get_settings()
        self.llm_judge = LLMJudge()
        self.report = EvaluationReport()

    def evaluate_analyzers(self) -> Dict[str, Any]:
        """Evaluate individual analyzer components.

        Returns:
            Dictionary mapping coin names to analyzer results
        """
        logger.info("Evaluating Analyzers...")
        results = {}

        repo = CoinRepository(
            cache_ttl=DEFAULT_CACHE_TTL, newsapi_key=self.settings.newsapi_key
        )
        analysis_service = AnalysisService(repo)

        for coin in DEFAULT_TEST_COINS:
            logger.info("  Testing with %s...", coin)
            coin_results = self._evaluate_coin_analyzers(coin, analysis_service)
            results[coin] = coin_results

        self.report.component_tests["analyzers"] = results
        return results

    def _evaluate_coin_analyzers(
        self, coin: str, analysis_service: AnalysisService
    ) -> Dict[str, Dict[str, Any]]:
        """Evaluate all analyzers for a specific coin.

        Args:
            coin: Coin identifier
            analysis_service: Analysis service instance

        Returns:
            Dictionary mapping analyzer names to results
        """
        coin_results = {}

        for analyzer_name, method_name in ANALYZER_TYPES.items():
            analyzer_func = getattr(analysis_service, method_name)
            coin_results[analyzer_name] = self._run_analyzer_test(
                coin, analyzer_name, analyzer_func
            )

        return coin_results

    def _run_analyzer_test(
        self, coin: str, analyzer_name: str, analyzer_func: callable
    ) -> Dict[str, Any]:
        """Run a single analyzer test.

        Args:
            coin: Coin identifier
            analyzer_name: Name of the analyzer
            analyzer_func: Analyzer function to test

        Returns:
            Test result dictionary
        """
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
            logger.error("Analyzer %s failed for %s: %s", analyzer_name, coin, e)
            return {"success": False, "error": str(e)}

    def evaluate_agent_responses(self) -> Dict[str, Any]:
        """Evaluate agent's conversational responses.

        Returns:
            Dictionary mapping queries to response results
        """
        logger.info("Evaluating Agent Responses...")
        results = {}

        try:
            agent = CryptoAnalysisAgent(self.settings)
            test_queries = self._get_test_queries()

            for test in test_queries:
                query = test["query"]
                logger.info("  Testing query: '%s'", query)
                results[query] = self._evaluate_single_response(agent, test)

            self.report.integration_tests["agent_responses"] = results
        except Exception as e:
            logger.error("Error evaluating agent: %s", e)
            results["error"] = str(e)

        return results

    def _get_test_queries(self) -> List[Dict[str, Any]]:
        """Get predefined test queries.

        Returns:
            List of test query dictionaries
        """
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
        """Evaluate a single agent response.

        Args:
            agent: Agent instance
            test: Test case dictionary

        Returns:
            Evaluation result dictionary
        """
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
            logger.error("Error evaluating query '%s': %s", test["query"], e)
            return {"success": False, "error": str(e)}

    def _check_clarification(self, response: str) -> bool:
        """Check if response asks for clarification.

        Args:
            response: Agent response text

        Returns:
            True if clarification is requested
        """
        has_question = "?" in response
        has_keywords = any(
            keyword in response.lower() for keyword in CLARIFICATION_KEYWORDS
        )
        return has_question and has_keywords

    def _check_analysis_content(self, response: str) -> bool:
        """Check if response contains analysis content.

        Args:
            response: Agent response text

        Returns:
            True if analysis content is present
        """
        return any(term in response.lower() for term in ANALYSIS_KEYWORDS)

    def evaluate_memory_and_context(self) -> Dict[str, Any]:
        """Evaluate conversation memory and context handling.

        Returns:
            Memory evaluation results
        """
        logger.info("Evaluating Memory and Context...")
        results = {}

        try:
            agent = CryptoAnalysisAgent(self.settings)

            # Test conversation flow
            agent.chat("Tell me about Bitcoin")
            initial_history_length = len(agent.conversation_messages)

            agent.chat("What about its price?")
            follow_up_history_length = len(agent.conversation_messages)

            results["memory_persistence"] = {
                "initial_messages": initial_history_length,
                "after_followup": follow_up_history_length,
                "memory_works": follow_up_history_length > initial_history_length,
            }

            # Test analysis history
            agent.analysis_history["bitcoin"] = {
                "fundamental": "test analysis",
                "name": "Bitcoin",
            }
            results["analysis_history"] = {
                "stores_analyses": "bitcoin" in agent.analysis_history,
                "stores_multiple_types": len(agent.analysis_history["bitcoin"]) > 1,
            }

            self.report.integration_tests["memory"] = results
        except Exception as e:
            logger.error("Error evaluating memory: %s", e)
            results["error"] = str(e)

        return results

    def evaluate_accuracy(self) -> Dict[str, Any]:
        """Evaluate answer accuracy using LLM-as-a-Judge.

        Returns:
            Accuracy evaluation results with scores and summaries
        """
        logger.info("Evaluating Answer Accuracy (LLM-as-a-Judge)...")
        results = {"common_questions": {}, "edge_case_questions": {}, "summary": {}}

        try:
            test_data = self._load_test_questions()
            agent = CryptoAnalysisAgent(self.settings)

            # Evaluate common questions
            common_scores = self._evaluate_question_set(
                agent,
                test_data.get("common_questions", []),
                results["common_questions"],
                "common questions",
            )

            # Evaluate edge case questions
            edge_scores = self._evaluate_question_set(
                agent,
                test_data.get("edge_case_questions", []),
                results["edge_case_questions"],
                "edge case questions",
            )

            # Calculate summary statistics
            results["summary"] = self._calculate_accuracy_summary(
                common_scores, edge_scores
            )

            self.report.accuracy_evaluation = results

            self._log_accuracy_summary(results["summary"])

        except Exception as e:
            logger.error("Error in accuracy evaluation: %s", e)
            results["error"] = str(e)

        return results

    def _load_test_questions(self) -> Dict[str, Any]:
        """Load test questions from JSON file.

        Returns:
            Test questions data dictionary

        Raises:
            FileNotFoundError: If test questions file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        if not TEST_QUESTIONS_FILE.exists():
            raise FileNotFoundError(
                f"Test questions file not found: {TEST_QUESTIONS_FILE}"
            )

        with open(TEST_QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _evaluate_question_set(
        self,
        agent: CryptoAnalysisAgent,
        test_cases: List[Dict[str, Any]],
        results_dict: Dict[str, Any],
        category_name: str,
    ) -> List[float]:
        """Evaluate a set of questions.

        Args:
            agent: Agent instance
            test_cases: List of test case dictionaries
            results_dict: Dictionary to store results
            category_name: Name of the category for logging

        Returns:
            List of scores from evaluations
        """
        logger.info("  Evaluating %s...", category_name)
        scores = []

        for test_case in test_cases:
            question = test_case["question"]
            logger.info("    Question: %s", question)

            try:
                # Handle context-dependent questions
                if test_case.get("requires_context") and test_case.get("context_query"):
                    agent.chat(test_case["context_query"])

                answer = agent.chat(question)
                context = {
                    "expected_behavior": test_case.get("expected_behavior"),
                    "expected_output_contains": test_case.get(
                        "expected_output_contains", []
                    ),
                }

                evaluation = self.llm_judge.evaluate_answer(question, answer, context)

                results_dict[question] = {
                    "answer": self._truncate_answer(answer),
                    "score": evaluation["score"],
                    "reasoning": evaluation["reasoning"],
                    "accuracy": evaluation["accuracy"],
                    "completeness": evaluation["completeness"],
                    "relevance": evaluation["relevance"],
                    "category": test_case.get("category"),
                    "expected_behavior": test_case.get("expected_behavior"),
                }

                scores.append(evaluation["score"])
                logger.info("      Score: %s/100", evaluation["score"])

            except Exception as e:
                logger.error("      Error: %s", e)
                results_dict[question] = {"error": str(e), "score": 0}

        return scores

    def _truncate_answer(self, answer: str) -> str:
        """Truncate answer to maximum length.

        Args:
            answer: Full answer text

        Returns:
            Truncated answer with ellipsis if needed
        """
        if len(answer) <= ANSWER_TRUNCATE_LENGTH:
            return answer
        return answer[:ANSWER_TRUNCATE_LENGTH] + "..."

    def _calculate_accuracy_summary(
        self, common_scores: List[float], edge_scores: List[float]
    ) -> Dict[str, Any]:
        """Calculate summary statistics for accuracy evaluation.

        Args:
            common_scores: Scores from common questions
            edge_scores: Scores from edge case questions

        Returns:
            Summary statistics dictionary
        """
        all_scores = common_scores + edge_scores

        return {
            "total_questions": len(all_scores),
            "average_score": self._safe_average(all_scores),
            "common_questions_avg": self._safe_average(common_scores),
            "edge_case_avg": self._safe_average(edge_scores),
            "min_score": min(all_scores) if all_scores else 0.0,
            "max_score": max(all_scores) if all_scores else 0.0,
        }

    def _safe_average(self, scores: List[float]) -> float:
        """Calculate average safely handling empty lists.

        Args:
            scores: List of scores

        Returns:
            Average score or 0.0 if list is empty
        """
        return sum(scores) / len(scores) if scores else 0.0

    def _log_accuracy_summary(self, summary: Dict[str, Any]) -> None:
        """Log accuracy evaluation summary.

        Args:
            summary: Summary statistics dictionary
        """
        logger.info("\n  Accuracy Summary:")
        logger.info("    Average Score: %.2f/100", summary["average_score"])
        logger.info(
            "    Common Questions Avg: %.2f/100", summary["common_questions_avg"]
        )
        logger.info("    Edge Cases Avg: %.2f/100", summary["edge_case_avg"])

    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate overall performance metrics.

        Returns:
            Performance metrics dictionary
        """
        logger.info("Calculating Performance Metrics...")

        metrics = {
            "analyzer_performance": self._calculate_analyzer_metrics(),
            "agent_performance": self._calculate_agent_metrics(),
            "overall_score": 0.0,
        }

        # Calculate overall score (weighted average)
        analyzer_score = (
            metrics["analyzer_performance"].get("success_rate", 0) * ANALYZER_WEIGHT
        )
        agent_score = metrics["agent_performance"].get("success_rate", 0) * AGENT_WEIGHT
        metrics["overall_score"] = analyzer_score + agent_score

        self.report.performance_metrics = metrics
        return metrics

    def _calculate_analyzer_metrics(self) -> Dict[str, Any]:
        """Calculate analyzer performance metrics.

        Returns:
            Analyzer metrics dictionary
        """
        analyzer_results = self.report.component_tests.get("analyzers", {})
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
        """Calculate agent performance metrics.

        Returns:
            Agent metrics dictionary
        """
        agent_results = self.report.integration_tests.get("agent_responses", {})
        if not agent_results:
            return {}

        total_queries = len(agent_results)
        successful_queries = sum(
            1
            for r in agent_results.values()
            if isinstance(r, dict) and r.get("success")
        )

        return {
            "success_rate": (
                successful_queries / total_queries if total_queries > 0 else 0.0
            ),
            "total_queries": total_queries,
            "successful_queries": successful_queries,
        }

    def generate_report(self, output_file: str = DEFAULT_REPORT_FILE) -> None:
        """Generate evaluation report.

        Args:
            output_file: Path to output report file
        """
        logger.info("\nGenerating Report...")

        self.calculate_performance_metrics()

        # Convert report to dictionary for JSON serialization
        report_dict = {
            "timestamp": self.report.timestamp,
            "component_tests": self.report.component_tests,
            "integration_tests": self.report.integration_tests,
            "performance_metrics": self.report.performance_metrics,
            "quality_metrics": self.report.quality_metrics,
            "accuracy_evaluation": self.report.accuracy_evaluation,
        }

        # Save to file
        output_path = Path(output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2)

        logger.info("Report saved to %s", output_file)
        self._print_summary(report_dict)

    def _print_summary(self, report_dict: Dict[str, Any]) -> None:
        """Print evaluation summary to console.

        Args:
            report_dict: Report dictionary
        """
        print("\n" + "=" * 60)
        print("Evaluation Summary")
        print("=" * 60)

        metrics = report_dict.get("performance_metrics", {})

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

        accuracy_eval = report_dict.get("accuracy_evaluation", {})
        if "summary" in accuracy_eval:
            acc_summary = accuracy_eval["summary"]
            print("\nAccuracy Evaluation (LLM-as-a-Judge):")
            print(f"  Average Score: {acc_summary.get('average_score', 0):.2f}/100")
            print(
                f"  Common Questions: {acc_summary.get('common_questions_avg', 0):.2f}/100"
            )
            print(f"  Edge Cases: {acc_summary.get('edge_case_avg', 0):.2f}/100")

        print("=" * 60)

    def run_full_evaluation(self) -> None:
        """Run complete evaluation suite."""
        print("Starting Full Evaluation...")
        print("=" * 60)

        self.evaluate_analyzers()
        self.evaluate_agent_responses()
        self.evaluate_memory_and_context()
        self.evaluate_accuracy()
        self.generate_report()

        print("\nEvaluation Complete!")


def main():
    """Run evaluation."""
    evaluator = AgentEvaluator()
    evaluator.run_full_evaluation()


if __name__ == "__main__":
    main()
