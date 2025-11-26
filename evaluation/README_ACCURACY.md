# Accuracy Evaluation with LLM-as-a-Judge

Evaluates agent response accuracy using LLM-as-a-Judge architecture.

## Process

1. Load test questions from `test_questions.json`
2. Get agent responses for each question
3. Evaluate responses using LLM judge
4. Generate accuracy report

## Test Questions

**Common Questions:** Comprehensive analysis, price, news, sentiment, technical, fundamental queries

**Edge Cases:** Ambiguity handling, vague queries, invalid coins, comparisons, context references, off-topic, general topics, memory retrieval

**Multi-Turn Scenarios:** Conversation flows with context maintenance

## Running Accuracy Evaluation

### Basic Usage

```bash
# Run accuracy evaluation only
python run_evaluation.py --type accuracy

# Run both performance and accuracy
python run_evaluation.py --type both

# Use a different judge model
python run_evaluation.py --type accuracy --judge-model gpt-4
```

### Direct Usage

```bash
python evaluation/evaluate_accuracy.py
```

## Evaluation Criteria

- Accuracy: Factual correctness
- Completeness: Coverage of expected information
- Relevance: How well it answers the question
- Tool Selection: Appropriate tool usage
- Clarity: Response structure
- Context Awareness: Conversation context maintenance
- Error Handling: Graceful error handling

## Scoring (0.0-1.0)

- 0.0-0.3: Poor
- 0.4-0.6: Fair
- 0.7-0.8: Good
- 0.9-1.0: Excellent

## Output

**accuracy_evaluation_report.json**: Individual evaluations, scores, feedback, summary statistics

**Console Summary**: Overall accuracy, performance by category, performance distribution

## Example Output

```
============================================================
Accuracy Evaluation Summary
============================================================

Overall Accuracy:
  Average: 87.50%
  Min: 72.00%
  Max: 95.00%
  Median: 88.00%

Performance by Category:
  comprehensive_analysis: 90.00% (n=1)
  price_query: 85.00% (n=1)

Performance Distribution:
  Excellent (≥90%): 3
  Good (70-89%): 5
  Fair (40-69%): 0
  Poor (<40%): 0
============================================================
```

## Customizing Test Questions

Edit `evaluation/test_questions.json` to add test cases.

## Judge Model Selection

- **gpt-4o-mini** (default): Fast, cost-effective
- **gpt-4**: More thorough
- **gpt-3.5-turbo**: Faster, less detailed

## Interpreting Results

- **≥0.9**: Excellent performance
- **0.7-0.9**: Good, minor improvements possible
- **<0.7**: Needs improvement

## Cost Considerations

Uses OpenAI API for agent responses and judge evaluations. Use gpt-4o-mini for judge to reduce costs.

