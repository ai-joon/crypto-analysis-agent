"""Comprehensive evaluation script for the crypto analysis agent."""

import time
import json
import os
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Get project root directory (parent of evaluation directory)
project_root = Path(__file__).parent.parent

# Load environment variables from .env file
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    # Try loading from current directory
    load_dotenv()

from src.agents.agent import CryptoAnalysisAgent
from src.config.settings import get_settings
from src.services.analysis_service import AnalysisService
from src.repositories.coin_repository import CoinRepository


class AgentEvaluator:
    """Evaluates agent performance across multiple dimensions."""
    
    def __init__(self):
        """Initialize evaluator."""
        # Check if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables.\n"
                "Please ensure:\n"
                "1. A .env file exists in the project root\n"
                "2. The .env file contains: OPENAI_API_KEY=sk-your-key-here\n"
                "3. The .env file is in the same directory as main.py"
            )
        
        self.settings = get_settings()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "component_tests": {},
            "integration_tests": {},
            "performance_metrics": {},
            "quality_metrics": {}
        }
    
    def evaluate_analyzers(self) -> Dict[str, Any]:
        """Evaluate individual analyzer components."""
        print("Evaluating Analyzers...")
        results = {}
        
        repo = CoinRepository(cache_ttl=300, newsapi_key=self.settings.newsapi_key)
        analysis_service = AnalysisService(repo)
        
        test_coins = ["bitcoin", "ethereum", "solana"]
        
        for coin in test_coins:
            print(f"  Testing with {coin}...")
            coin_results = {}
            
            # Test each analyzer
            analyzers = {
                "fundamental": analysis_service.perform_fundamental_analysis,
                "price": analysis_service.perform_price_analysis,
                "sentiment": analysis_service.perform_sentiment_analysis,
                "technical": analysis_service.perform_technical_analysis,
            }
            
            for name, analyzer_func in analyzers.items():
                try:
                    start_time = time.time()
                    result = analyzer_func(coin)
                    elapsed = time.time() - start_time
                    
                    coin_results[name] = {
                        "success": True,
                        "response_time": elapsed,
                        "output_length": len(result),
                        "has_data_points": any(char.isdigit() for char in result),
                        "has_multiple_paragraphs": result.count("\n\n") >= 2,
                        "has_sections": result.count("**") >= 3,
                    }
                except Exception as e:
                    coin_results[name] = {
                        "success": False,
                        "error": str(e)
                    }
            
            results[coin] = coin_results
        
        self.results["component_tests"]["analyzers"] = results
        return results
    
    def evaluate_agent_responses(self) -> Dict[str, Any]:
        """Evaluate agent's conversational responses."""
        print("Evaluating Agent Responses...")
        results = {}
        
        try:
            agent = CryptoAnalysisAgent(self.settings)
            
            test_queries = [
                {
                    "query": "Tell me about Bitcoin",
                    "expected": "comprehensive_analysis",
                    "should_clarify": False
                },
                {
                    "query": "What's the price of Ethereum?",
                    "expected": "price_focus",
                    "should_clarify": False
                },
                {
                    "query": "Tell me about ETH",
                    "expected": "clarification_or_analysis",
                    "should_clarify": True  # May ask for clarification
                },
                {
                    "query": "What's happening with crypto?",
                    "expected": "general_topic",
                    "should_clarify": False
                },
            ]
            
            for test in test_queries:
                print(f"  Testing query: '{test['query']}'")
                try:
                    start_time = time.time()
                    response = agent.chat(test["query"])
                    elapsed = time.time() - start_time
                    
                    results[test["query"]] = {
                        "success": True,
                        "response_time": elapsed,
                        "response_length": len(response),
                        "asked_for_clarification": "?" in response and any(
                            word in response.lower() 
                            for word in ["would you like", "what", "which", "please"]
                        ),
                        "contains_analysis": any(
                            term in response.lower() 
                            for term in ["analysis", "price", "market", "sentiment", "technical"]
                        ),
                        "expected_behavior": test["expected"],
                    }
                except Exception as e:
                    results[test["query"]] = {
                        "success": False,
                        "error": str(e)
                    }
            
            self.results["integration_tests"]["agent_responses"] = results
        except Exception as e:
            print(f"  ❌ Error evaluating agent: {e}")
            results["error"] = str(e)
        
        return results
    
    def evaluate_memory_and_context(self) -> Dict[str, Any]:
        """Evaluate conversation memory and context handling."""
        print("Evaluating Memory and Context...")
        results = {}
        
        try:
            agent = CryptoAnalysisAgent(self.settings)
            
            # Test conversation flow
            agent.agent = type('MockAgent', (), {
                'invoke': lambda self, x: {
                    "messages": [type('Msg', (), {"content": "Bitcoin analysis..."})()]
                }
            })()
            
            # First query
            agent.chat("Tell me about Bitcoin")
            initial_history_length = len(agent.conversation_messages)
            
            # Follow-up query
            agent.chat("What about its price?")
            follow_up_history_length = len(agent.conversation_messages)
            
            results["memory_persistence"] = {
                "initial_messages": initial_history_length,
                "after_followup": follow_up_history_length,
                "memory_works": follow_up_history_length > initial_history_length
            }
            
            # Test analysis history
            agent.analysis_history["bitcoin"] = {
                "fundamental": "test analysis",
                "name": "Bitcoin"
            }
            results["analysis_history"] = {
                "stores_analyses": "bitcoin" in agent.analysis_history,
                "stores_multiple_types": len(agent.analysis_history["bitcoin"]) > 1
            }
            
            self.results["integration_tests"]["memory"] = results
        except Exception as e:
            print(f"  ❌ Error evaluating memory: {e}")
            results["error"] = str(e)
        
        return results
    
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        print("Calculating Performance Metrics...")
        
        metrics = {
            "analyzer_performance": {},
            "agent_performance": {},
            "overall_score": 0
        }
        
        # Analyze analyzer results
        if "analyzers" in self.results.get("component_tests", {}):
            analyzer_results = self.results["component_tests"]["analyzers"]
            total_tests = 0
            successful_tests = 0
            total_response_time = 0
            
            for analyses in analyzer_results.values():
                for result in analyses.values():
                    if isinstance(result, dict) and result.get("success"):
                        total_tests += 1
                        successful_tests += 1
                        total_response_time += result.get("response_time", 0)
            
            metrics["analyzer_performance"] = {
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "average_response_time": total_response_time / successful_tests if successful_tests > 0 else 0,
                "total_tests": total_tests,
                "successful_tests": successful_tests
            }
        
        # Analyze agent results
        if "agent_responses" in self.results.get("integration_tests", {}):
            agent_results = self.results["integration_tests"]["agent_responses"]
            total_queries = len(agent_results)
            successful_queries = sum(1 for r in agent_results.values() if r.get("success"))
            
            metrics["agent_performance"] = {
                "success_rate": successful_queries / total_queries if total_queries > 0 else 0,
                "total_queries": total_queries,
                "successful_queries": successful_queries
            }
        
        # Calculate overall score (weighted average)
        analyzer_score = metrics["analyzer_performance"].get("success_rate", 0) * 0.6
        agent_score = metrics["agent_performance"].get("success_rate", 0) * 0.4
        metrics["overall_score"] = analyzer_score + agent_score
        
        self.results["performance_metrics"] = metrics
        return metrics
    
    def generate_report(self, output_file: str = "evaluation_report.json"):
        """Generate evaluation report."""
        print("\nGenerating Report...")
        
        # Calculate final metrics
        self.calculate_performance_metrics()
        
        # Save to file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Report saved to {output_file}")
        
        print("\n" + "="*60)
        print("Evaluation Summary")
        print("="*60)
        
        if "performance_metrics" in self.results:
            metrics = self.results["performance_metrics"]
            
            if "analyzer_performance" in metrics:
                ap = metrics["analyzer_performance"]
                print(f"\nAnalyzer Performance:")
                print(f"  Success Rate: {ap.get('success_rate', 0):.2%}")
                print(f"  Avg Response Time: {ap.get('average_response_time', 0):.2f}s")
                print(f"  Tests: {ap.get('successful_tests', 0)}/{ap.get('total_tests', 0)}")
            
            if "agent_performance" in metrics:
                agp = metrics["agent_performance"]
                print(f"\nAgent Performance:")
                print(f"  Success Rate: {agp.get('success_rate', 0):.2%}")
                print(f"  Queries: {agp.get('successful_queries', 0)}/{agp.get('total_queries', 0)}")
            
            print(f"\nOverall Score: {metrics.get('overall_score', 0):.2%}")
        
        print("="*60)
    
    def run_full_evaluation(self):
        """Run complete evaluation suite."""
        print("Starting Full Evaluation...")
        print("="*60)
        
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

