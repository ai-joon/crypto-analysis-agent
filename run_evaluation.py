#!/usr/bin/env python3
"""Quick evaluation script for the crypto analysis agent."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Get project root directory
project_root = Path(__file__).parent

env_file = project_root / ".env"
if not env_file.exists():
    print(f"Warning: .env file not found at {env_file}")
    print("Please create a .env file with your OPENAI_API_KEY\n")

# Load environment variables from .env file first
load_dotenv(dotenv_path=env_file)

# Add src to path
sys.path.insert(0, str(project_root))

from evaluation.evaluate_agent import AgentEvaluator
from evaluation.evaluate_accuracy import AccuracyEvaluator


def main():
    """Run evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate crypto analysis agent")
    parser.add_argument(
        "--type",
        choices=["performance", "accuracy", "both"],
        default="both",
        help="Type of evaluation to run (default: both)",
    )
    parser.add_argument(
        "--judge-model",
        default="gpt-4o-mini",
        help="Model to use for LLM judge (default: gpt-4o-mini)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("CRYPTO ANALYSIS AGENT - EVALUATION")
    print("=" * 60)
    print()

    try:
        if args.type in ["performance", "both"]:
            print("Running Performance Evaluation...")
            evaluator = AgentEvaluator()
            evaluator.run_full_evaluation()
            print()

        if args.type in ["accuracy", "both"]:
            print("Running Accuracy Evaluation (LLM-as-a-Judge)...")
            accuracy_evaluator = AccuracyEvaluator(judge_model=args.judge_model)
            accuracy_evaluator.run_full_evaluation()

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
    sys.exit(main())
