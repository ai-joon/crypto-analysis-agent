# Agent Evaluation Framework

This directory contains comprehensive evaluation tools for assessing the crypto analysis agent's performance.

## Evaluation Components

### 1. Unit Tests (`../tests/`)
- **test_analyzers.py**: Tests individual analyzer components
- **test_services.py**: Tests service layer components
- **test_integration.py**: Integration tests for full system

### 2. Evaluation Script (`evaluate_agent.py`)
Comprehensive evaluation script that tests:
- Individual analyzer performance
- Agent conversational responses
- Memory and context handling
- Overall performance metrics

### 3. Test Scenarios (`evaluation_scenarios.json`)
Predefined test scenarios for:
- Basic queries
- Ambiguity handling
- Context awareness
- Error handling
- Guardrails

## Running Evaluations

### Quick Component Tests

```bash
# Run unit tests for analyzers
pytest tests/test_analyzers.py -v

# Run unit tests for services
pytest tests/test_services.py -v

# Run all unit tests
pytest tests/ -v
```

### Full Evaluation

```bash
# Run comprehensive evaluation
python evaluation/evaluate_agent.py
```

This will:
1. Test all analyzer components
2. Test agent responses to various queries
3. Test memory and context handling
4. Generate a detailed report (`evaluation_report.json`)

### Specific Component Evaluation

```python
from evaluation.evaluate_agent import AgentEvaluator

evaluator = AgentEvaluator()

# Evaluate only analyzers
results = evaluator.evaluate_analyzers()

# Evaluate only agent responses
results = evaluator.evaluate_agent_responses()

# Evaluate memory
results = evaluator.evaluate_memory_and_context()
```

## Evaluation Metrics

### Component-Level Metrics

1. **Analyzer Performance**
   - Success rate (percentage of successful analyses)
   - Response time (average time per analysis)
   - Output quality (length, data points, structure)

2. **Service Performance**
   - API call success rate
   - Error handling
   - Data retrieval accuracy

### Integration-Level Metrics

1. **Agent Response Quality**
   - Query understanding accuracy
   - Tool selection correctness
   - Response relevance
   - Clarification requests (when appropriate)

2. **Memory & Context**
   - Conversation history retention
   - Context reference accuracy
   - Analysis history storage

3. **Performance**
   - Overall response time
   - API call efficiency
   - Cache hit rate

## Evaluation Report Structure

The generated `evaluation_report.json` contains:

```json
{
  "timestamp": "2024-01-15T10:00:00",
  "component_tests": {
    "analyzers": {
      "bitcoin": {
        "fundamental": {...},
        "price": {...},
        "sentiment": {...},
        "technical": {...}
      }
    }
  },
  "integration_tests": {
    "agent_responses": {...},
    "memory": {...}
  },
  "performance_metrics": {
    "analyzer_performance": {...},
    "agent_performance": {...},
    "overall_score": 0.95
  }
}
```

## Performance Benchmarks

Based on `evaluation_scenarios.json`:

- **Analyzer Response Time**
  - Excellent: < 2 seconds
  - Good: < 5 seconds
  - Acceptable: < 10 seconds

- **Agent Response Time**
  - Excellent: < 5 seconds
  - Good: < 10 seconds
  - Acceptable: < 20 seconds

- **Output Quality**
  - Minimum length: 200 characters
  - Minimum paragraphs: 2
  - Minimum data points: 5

## Continuous Evaluation

For continuous evaluation, you can:

1. **Add to CI/CD pipeline**:
   ```yaml
   - name: Run Evaluation
     run: python evaluation/evaluate_agent.py
   ```

2. **Schedule regular evaluations**:
   ```bash
   # Add to cron or scheduled task
   0 0 * * * cd /path/to/project && python evaluation/evaluate_agent.py
   ```

3. **Monitor performance trends**:
   - Compare reports over time
   - Track metrics in a database
   - Set up alerts for performance degradation

## Custom Evaluation Scenarios

Add custom scenarios to `evaluation_scenarios.json`:

```json
{
  "category": "custom_tests",
  "scenarios": [
    {
      "query": "Your test query",
      "expected_behavior": "expected_behavior",
      "expected_output_contains": ["keyword1", "keyword2"]
    }
  ]
}
```

## Troubleshooting

### Tests Failing
- Check API keys are set in `.env`
- Verify internet connection for API calls
- Check rate limits haven't been exceeded

### Slow Performance
- Check cache configuration
- Verify API response times
- Consider using mock data for faster tests

### Missing Dependencies
```bash
pip install pytest pytest-cov
```

