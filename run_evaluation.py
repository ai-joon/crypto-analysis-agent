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


def main():
    """Run evaluation."""
    print("="*60)
    print("CRYPTO ANALYSIS AGENT - EVALUATION")
    print("="*60)
    print()
    
    try:
        evaluator = AgentEvaluator()
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
    sys.exit(main())

