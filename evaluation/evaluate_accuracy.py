"""Accuracy evaluation using LLM-as-a-Judge architecture."""

import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from src.agents.agent import CryptoAnalysisAgent
from src.config.settings import get_settings
from evaluation.llm_judge import LLMJudge


# Constants
RATE_LIMIT_DELAY = 1.0
DEFAULT_QUESTIONS_FILE = "evaluation/test_questions.json"
DEFAULT_REPORT_FILE = "accuracy_evaluation_report.json"
SCORE_TIERS = {"excellent": 0.9, "good": 0.7, "fair": 0.4}


class AccuracyEvaluator:
    """Evaluates agent accuracy using LLM-as-a-Judge."""

    def __init__(self, judge_model: str = "gpt-4o-mini"):
        """Initialize accuracy evaluator."""
        self.settings = get_settings()
        self.agent = CryptoAnalysisAgent(self.settings)
        self.judge = LLMJudge(model=judge_model)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_type": "accuracy_with_llm_judge",
            "test_questions": [],
            "evaluation_results": {},
            "summary": {},
        }

    def load_test_questions(
        self, questions_file: str = DEFAULT_QUESTIONS_FILE
    ) -> Dict[str, Any]:
        """Load test questions from JSON file."""
        questions_path = Path(questions_file)
        if not questions_path.exists():
            raise FileNotFoundError(f"Test questions file not found: {questions_file}")

        with open(questions_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_question(
        self, question_data: Dict[str, Any], context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a single question through the agent and evaluate response.

        Args:
            question_data: Question data from test_questions.json
            context: Optional context for multi-turn scenarios

        Returns:
            Dictionary with question, response, and evaluation
        """
        question = question_data["question"]
        question_id = question_data.get("id", "unknown")
        category = question_data.get("category", "unknown")

        print(f"\nQuestion {question_id} ({category}): {question}")

        try:
            start_time = time.time()
            response = self.agent.chat(question)
            response_time = time.time() - start_time

            print(
                f"  Response time: {response_time:.2f}s, Length: {len(response)} chars"
            )

        except Exception as e:
            print(f"  Error: {e}")
            return {
                "question_id": question_id,
                "question": question,
                "category": category,
                "response": None,
                "error": str(e),
                "response_time": 0,
                "evaluation": None,
            }

        print("  Evaluating...")
        try:
            evaluation = self.judge.evaluate_response(
                question=question,
                response=response,
                expected_behaviors=question_data.get("expected_behaviors", []),
                evaluation_criteria=question_data.get("evaluation_criteria", {}),
                context=context,
            )

            score = evaluation.get("overall_score", 0.0)
            print(f"  Score: {score:.2f}/1.0")

        except Exception as e:
            print(f"  Evaluation error: {e}")
            evaluation = {"error": str(e), "overall_score": 0.0}

        return {
            "question_id": question_id,
            "question": question,
            "category": category,
            "response": response,
            "response_time": response_time,
            "response_length": len(response),
            "evaluation": evaluation,
        }

    def evaluate_common_questions(
        self, questions_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate common questions."""
        print("\n" + "=" * 60)
        print("Common Questions")
        print("=" * 60)

        common_questions = questions_data.get("common_questions", [])
        results = []

        for question_data in common_questions:
            result = self.run_question(question_data)
            results.append(result)
            time.sleep(RATE_LIMIT_DELAY)

        return results

    def evaluate_edge_cases(
        self, questions_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate edge case questions."""
        print("\n" + "=" * 60)
        print("Edge Cases")
        print("=" * 60)

        edge_cases = questions_data.get("edge_case_questions", [])
        results = []

        for question_data in edge_cases:
            context = self._build_context(question_data)
            result = self.run_question(question_data, context=context)
            results.append(result)
            time.sleep(RATE_LIMIT_DELAY)

        return results

    def _build_context(self, question_data: Dict[str, Any]) -> Optional[str]:
        """Build context string from question data."""
        if "context" not in question_data:
            return None

        ctx = question_data["context"]
        return (
            f"Previous query: {ctx.get('previous_query', '')}\n"
            f"Previous response: {ctx.get('previous_response', '')}"
        )

    def evaluate_multi_turn_scenarios(
        self, questions_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate multi-turn conversation scenarios."""
        print("\n" + "=" * 60)
        print("Multi-Turn Scenarios")
        print("=" * 60)

        scenarios = questions_data.get("multi_turn_scenarios", [])
        results = []

        for scenario_data in scenarios:
            scenario_id = scenario_data.get("id", "unknown")
            turns = scenario_data.get("turns", [])

            print(f"\nScenario {scenario_id}: {scenario_data.get('scenario', '')}")
            self.agent.reset_conversation()

            scenario_results = []
            for turn_data in turns:
                turn_num = turn_data.get("turn", 0)
                question = turn_data.get("question", "")
                expected = turn_data.get("expected", "")

                print(f"  Turn {turn_num}: {question}")

                try:
                    start_time = time.time()
                    response = self.agent.chat(question)
                    response_time = time.time() - start_time

                    evaluation = self._evaluate_turn(question, response, expected)

                    scenario_results.append(
                        {
                            "turn": turn_num,
                            "question": question,
                            "response": response,
                            "response_time": response_time,
                            "evaluation": evaluation,
                        }
                    )

                    score = evaluation.get("overall_score", 0.0)
                    print(f"    Score: {score:.2f}/1.0")

                except Exception as e:
                    print(f"    Error: {e}")
                    scenario_results.append(
                        {
                            "turn": turn_num,
                            "question": question,
                            "error": str(e),
                            "evaluation": None,
                        }
                    )

                time.sleep(RATE_LIMIT_DELAY)

            results.append(
                {
                    "scenario_id": scenario_id,
                    "scenario": scenario_data.get("scenario", ""),
                    "turns": scenario_results,
                }
            )

        return results

    def _evaluate_turn(
        self, question: str, response: str, expected: str
    ) -> Dict[str, Any]:
        """Evaluate a single turn in a multi-turn scenario."""
        return self.judge.evaluate_response(
            question=question,
            response=response,
            expected_behaviors=[f"Should {expected.lower()}"],
            evaluation_criteria={
                "context_awareness": "Should maintain context",
                "relevance": f"Should {expected.lower()}",
                "accuracy": "Should be accurate",
            },
            context=f"Expected: {expected}",
        )

    def calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics."""
        all_results = []

        # Collect all individual question results
        if "common_questions" in self.results.get("evaluation_results", {}):
            all_results.extend(self.results["evaluation_results"]["common_questions"])

        if "edge_cases" in self.results.get("evaluation_results", {}):
            all_results.extend(self.results["evaluation_results"]["edge_cases"])

        # Extract scores
        scores = []
        category_scores = {}

        for result in all_results:
            if result.get("evaluation") and "error" not in result.get("evaluation", {}):
                score = result["evaluation"].get("overall_score", 0.0)
                scores.append(score)

                category = result.get("category", "unknown")
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(score)

        # Calculate statistics
        summary = {
            "total_questions": len(all_results),
            "successful_evaluations": len(scores),
            "overall_accuracy": {
                "average": sum(scores) / len(scores) if scores else 0.0,
                "min": min(scores) if scores else 0.0,
                "max": max(scores) if scores else 0.0,
                "median": sorted(scores)[len(scores) // 2] if scores else 0.0,
            },
            "category_breakdown": {
                category: {
                    "count": len(cat_scores),
                    "average": sum(cat_scores) / len(cat_scores),
                    "min": min(cat_scores),
                    "max": max(cat_scores),
                }
                for category, cat_scores in category_scores.items()
            },
            "performance_tiers": self._calculate_performance_tiers(scores),
        }

        return summary

    def _calculate_performance_tiers(self, scores: List[float]) -> Dict[str, int]:
        """Calculate performance tier distribution."""
        return {
            "excellent": len([s for s in scores if s >= SCORE_TIERS["excellent"]]),
            "good": len(
                [
                    s
                    for s in scores
                    if SCORE_TIERS["good"] <= s < SCORE_TIERS["excellent"]
                ]
            ),
            "fair": len(
                [s for s in scores if SCORE_TIERS["fair"] <= s < SCORE_TIERS["good"]]
            ),
            "poor": len([s for s in scores if s < SCORE_TIERS["fair"]]),
        }

    def generate_report(self, output_file: str = DEFAULT_REPORT_FILE):
        """Generate detailed accuracy evaluation report."""
        print("\n" + "=" * 60)
        print("Generating Report")
        print("=" * 60 + "\n")

        # Calculate summary
        self.results["summary"] = self.calculate_summary()

        # Save to file
        output_path = Path(output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"Report saved to {output_file}")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print evaluation summary."""
        summary = self.results.get("summary", {})

        print("\n" + "=" * 60)
        print("Accuracy Evaluation Summary")
        print("=" * 60)

        if "overall_accuracy" in summary:
            oa = summary["overall_accuracy"]
            print(f"\nOverall Accuracy:")
            print(f"  Average: {oa.get('average', 0.0):.2%}")
            print(f"  Min: {oa.get('min', 0.0):.2%}")
            print(f"  Max: {oa.get('max', 0.0):.2%}")
            print(f"  Median: {oa.get('median', 0.0):.2%}")

        if "category_breakdown" in summary:
            print(f"\nPerformance by Category:")
            for category, stats in summary["category_breakdown"].items():
                print(f"  {category}: {stats['average']:.2%} (n={stats['count']})")

        if "performance_tiers" in summary:
            pt = summary["performance_tiers"]
            print(f"\nPerformance Distribution:")
            print(f"  Excellent (≥90%): {pt.get('excellent', 0)}")
            print(f"  Good (70-89%): {pt.get('good', 0)}")
            print(f"  Fair (40-69%): {pt.get('fair', 0)}")
            print(f"  Poor (<40%): {pt.get('poor', 0)}")

        print("=" * 60)

    def run_full_evaluation(self, questions_file: str = DEFAULT_QUESTIONS_FILE):
        """Run complete accuracy evaluation."""
        print("=" * 60)
        print("Accuracy Evaluation - LLM-as-a-Judge")
        print("=" * 60)

        # Load test questions
        questions_data = self.load_test_questions(questions_file)
        self.results["test_questions"] = questions_data

        # Evaluate common questions
        common_results = self.evaluate_common_questions(questions_data)
        self.results["evaluation_results"]["common_questions"] = common_results

        # Evaluate edge cases
        edge_results = self.evaluate_edge_cases(questions_data)
        self.results["evaluation_results"]["edge_cases"] = edge_results

        # Evaluate multi-turn scenarios
        multi_turn_results = self.evaluate_multi_turn_scenarios(questions_data)
        self.results["evaluation_results"]["multi_turn_scenarios"] = multi_turn_results

        self.generate_report()

        print("\nEvaluation Complete!")


def main():
    """Run accuracy evaluation."""
    try:
        evaluator = AccuracyEvaluator()
        evaluator.run_full_evaluation()
        return 0
    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nEvaluation failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
