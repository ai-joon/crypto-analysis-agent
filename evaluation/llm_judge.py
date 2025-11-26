"""LLM-as-a-Judge implementation for evaluating answer accuracy."""

import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI
from openai import APIError as OpenAIAPIError

from evaluation.config import (
    DEFAULT_JUDGE_MODEL,
    JUDGE_TEMPERATURE,
    SCORE_MIN,
    SCORE_MAX,
)


class LLMJudgeError(Exception):
    """Custom exception for LLM judge errors."""


class LLMJudge:
    """Uses an LLM to evaluate the accuracy of agent responses."""

    SYSTEM_PROMPT = (
        "You are an expert evaluator assessing the accuracy and quality of "
        "cryptocurrency analysis responses. Rate answers on a scale of 0-100 "
        "based on accuracy, completeness, and relevance. Always respond with valid JSON."
    )

    EVALUATION_CRITERIA = """
Evaluate the answer and provide a JSON response with:
1. "score": A number from 0-100 representing overall quality
2. "reasoning": Brief explanation of the score
3. "accuracy": Assessment of factual accuracy (high/medium/low)
4. "completeness": Assessment of how complete the answer is (high/medium/low)
5. "relevance": Assessment of how relevant the answer is to the question (high/medium/low)

Consider:
- Are the facts correct?
- Is the answer complete for the question asked?
- Is the answer relevant and directly addresses the question?
- Does it provide useful information?
- Are there any errors or misleading information?

Respond in JSON format only."""

    def __init__(self, model: str = DEFAULT_JUDGE_MODEL):
        """Initialize the LLM judge.

        Args:
            model: OpenAI model to use as judge

        Raises:
            LLMJudgeError: If API key is not found
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMJudgeError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def evaluate_answer(
        self, question: str, answer: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate the accuracy of an answer using LLM-as-a-Judge.

        Args:
            question: The question that was asked
            answer: The agent's answer
            context: Optional context about expected behavior

        Returns:
            Dictionary with evaluation results including score and reasoning

        Raises:
            LLMJudgeError: If evaluation fails critically
        """
        if not question or not answer:
            return self._create_error_result("Question and answer must be non-empty")

        prompt = self._build_evaluation_prompt(question, answer, context)

        try:
            response = self._call_judge_api(prompt)
            return self._parse_evaluation_response(response)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return self._create_error_result(f"JSON parsing error: {str(e)}")
        except OpenAIAPIError as e:
            return self._create_error_result(f"OpenAI API error: {str(e)}")
        except Exception as e:
            return self._create_error_result(f"Unexpected error: {str(e)}")

    def _call_judge_api(self, prompt: str) -> str:
        """Call the OpenAI API for evaluation.

        Args:
            prompt: The evaluation prompt

        Returns:
            Response content from the API

        Raises:
            OpenAIAPIError: If API call fails
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=JUDGE_TEMPERATURE,
            response_format={"type": "json_object"},
        )

        if not response.choices or not response.choices[0].message.content:
            raise LLMJudgeError("Empty response from judge API")

        return response.choices[0].message.content

    def _parse_evaluation_response(self, content: str) -> Dict[str, Any]:
        """Parse and validate the evaluation response.

        Args:
            content: JSON string from the API

        Returns:
            Parsed and validated evaluation result
        """
        result = json.loads(content)

        score = self._validate_score(result.get("score", 0))

        return {
            "score": score,
            "reasoning": result.get("reasoning", ""),
            "accuracy": result.get("accuracy", ""),
            "completeness": result.get("completeness", ""),
            "relevance": result.get("relevance", ""),
        }

    def _validate_score(self, score: Any) -> float:
        """Validate and clamp score to valid range.

        Args:
            score: Score value to validate

        Returns:
            Validated score between SCORE_MIN and SCORE_MAX
        """
        if not isinstance(score, (int, float)):
            return float(SCORE_MIN)

        return max(SCORE_MIN, min(SCORE_MAX, float(score)))

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create an error result dictionary.

        Args:
            error_message: Error message to include

        Returns:
            Error result dictionary
        """
        return {
            "score": SCORE_MIN,
            "reasoning": error_message,
            "accuracy": "error",
            "completeness": "error",
            "relevance": "error",
        }

    def _build_evaluation_prompt(
        self, question: str, answer: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the evaluation prompt for the LLM judge.

        Args:
            question: The question that was asked
            answer: The agent's answer
            context: Optional context about expected behavior

        Returns:
            Complete evaluation prompt
        """
        prompt = f"""Evaluate the following answer for accuracy, completeness, and relevance.

Question: {question}

Answer:
{answer}
"""

        if context:
            if context.get("expected_behavior"):
                prompt += f"\nExpected Behavior: {context['expected_behavior']}\n"
            if context.get("expected_output_contains"):
                expected_items = ", ".join(context["expected_output_contains"])
                prompt += f"\nExpected to contain: {expected_items}\n"

        prompt += self.EVALUATION_CRITERIA

        return prompt
