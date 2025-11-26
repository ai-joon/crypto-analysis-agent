"""LLM-as-a-Judge evaluation system for assessing answer quality."""

import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class LLMJudge:
    """Uses an LLM to judge the quality and accuracy of agent responses."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the LLM judge.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use for judging (default: gpt-4o-mini)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required for LLM judge")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def evaluate_response(
        self,
        question: str,
        response: str,
        expected_behaviors: List[str],
        evaluation_criteria: Dict[str, str],
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate an agent response using LLM-as-a-judge.

        Args:
            question: The user's question
            response: The agent's response
            expected_behaviors: List of expected behaviors
            evaluation_criteria: Dictionary of criteria to evaluate
            context: Optional context about previous conversation

        Returns:
            Dictionary with evaluation scores and feedback
        """
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            question, response, expected_behaviors, evaluation_criteria, context
        )

        try:
            # Get judgment from LLM
            judgment = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Evaluate cryptocurrency analysis responses objectively and thoroughly.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent judgments
                response_format={"type": "json_object"},
            )

            # Parse JSON response
            result = json.loads(judgment.choices[0].message.content)
            return result

        except Exception as e:
            return {
                "error": str(e),
                "overall_score": 0.0,
                "scores": {},
                "feedback": f"Error during evaluation: {str(e)}",
            }

    def _build_evaluation_prompt(
        self,
        question: str,
        response: str,
        expected_behaviors: List[str],
        evaluation_criteria: Dict[str, str],
        context: Optional[str] = None,
    ) -> str:
        """Build the evaluation prompt for the judge LLM."""

        criteria_list = "\n".join(
            [
                f"- {criterion}: {description}"
                for criterion, description in evaluation_criteria.items()
            ]
        )

        behaviors_list = "\n".join([f"- {behavior}" for behavior in expected_behaviors])

        context_section = ""
        if context:
            context_section = f"\n\n**Context:**\n{context}\n"

        prompt = f"""Evaluate this cryptocurrency analysis response.

**Question:** {question}
{context_section}
**Response:** {response}

**Expected Behaviors:**
{behaviors_list}

**Evaluation Criteria:**
{criteria_list}

**Scoring (0.0-1.0):**
- 0.0-0.3: Poor
- 0.4-0.6: Fair
- 0.7-0.8: Good
- 0.9-1.0: Excellent

Return JSON:
{{
    "overall_score": <float>,
    "scores": {{"<criterion>": <float>, ...}},
    "feedback": "<explanation>",
    "strengths": ["<strength>", ...],
    "weaknesses": ["<weakness>", ...],
    "accuracy_assessment": "<assessment>",
    "relevance_assessment": "<assessment>"
}}"""

        return prompt

    def evaluate_batch(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate multiple question-response pairs in batch.

        Args:
            evaluations: List of dicts with 'question', 'response', 'expected_behaviors',
                         'evaluation_criteria', and optional 'context'

        Returns:
            Dictionary with batch evaluation results
        """
        results = []

        for i, eval_data in enumerate(evaluations, 1):
            print(f"  Evaluating response {i}/{len(evaluations)}...")

            result = self.evaluate_response(
                question=eval_data["question"],
                response=eval_data["response"],
                expected_behaviors=eval_data["expected_behaviors"],
                evaluation_criteria=eval_data["evaluation_criteria"],
                context=eval_data.get("context"),
            )

            result["question_id"] = eval_data.get("id", f"q{i}")
            result["question"] = eval_data["question"]
            results.append(result)

        # Calculate aggregate metrics
        overall_scores = [
            r.get("overall_score", 0.0) for r in results if "error" not in r
        ]

        return {
            "total_evaluations": len(evaluations),
            "successful_evaluations": len(overall_scores),
            "average_score": (
                sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
            ),
            "min_score": min(overall_scores) if overall_scores else 0.0,
            "max_score": max(overall_scores) if overall_scores else 0.0,
            "individual_results": results,
        }
