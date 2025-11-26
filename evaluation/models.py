"""Data models for evaluation results."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class EvaluationResult:
    """Base class for evaluation results."""

    success: bool
    error: Optional[str] = None


@dataclass
class AnalyzerResult(EvaluationResult):
    """Result from analyzer evaluation."""

    response_time: float = 0.0
    output_length: int = 0
    has_data_points: bool = False
    has_multiple_paragraphs: bool = False
    has_sections: bool = False


@dataclass
class AgentResponseResult(EvaluationResult):
    """Result from agent response evaluation."""

    response_time: float = 0.0
    response_length: int = 0
    asked_for_clarification: bool = False
    contains_analysis: bool = False
    expected_behavior: str = ""


@dataclass
class AccuracyEvaluationResult(EvaluationResult):
    """Result from accuracy evaluation."""

    score: float = 0.0
    reasoning: str = ""
    accuracy: str = ""
    completeness: str = ""
    relevance: str = ""
    category: str = ""
    expected_behavior: str = ""
    answer: str = ""


@dataclass
class AccuracySummary:
    """Summary statistics for accuracy evaluation."""

    total_questions: int = 0
    average_score: float = 0.0
    common_questions_avg: float = 0.0
    edge_case_avg: float = 0.0
    min_score: float = 0.0
    max_score: float = 0.0


@dataclass
class PerformanceMetrics:
    """Performance metrics for evaluation."""

    analyzer_performance: Dict[str, Any] = field(default_factory=dict)
    agent_performance: Dict[str, Any] = field(default_factory=dict)
    overall_score: float = 0.0


@dataclass
class EvaluationReport:
    """Complete evaluation report."""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    component_tests: Dict[str, Any] = field(default_factory=dict)
    integration_tests: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    accuracy_evaluation: Dict[str, Any] = field(default_factory=dict)
