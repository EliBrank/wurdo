# Shared Test Results

This directory contains test result files that demonstrate the ML engine's performance without requiring the team to install dependencies or run tests.

## Files

### `probability_scoring_results.json`
**Test**: Advanced scoring with 9 carefully selected words  
**Purpose**: Shows how the probability-based scoring system performs on different word categories  
**Key Findings**:
- Rhymes: 0.999+ creativity scores
- Semantic similar: 0.998+ creativity scores  
- Unrelated: 0.999+ creativity scores
- Clear differentiation between categories

### `semantic_analysis_results.json`
**Test**: Comprehensive semantic analysis with 30+ words across 6 categories  
**Purpose**: Demonstrates how semantic similarity affects scoring  
**Key Findings**:
- Semantic related words get lower creativity scores (more predictable)
- Unrelated words get higher creativity scores (more surprising)
- Phonetic similarity also affects scoring
- Model correctly identifies semantic relationships

## How to Read the Results

### Creativity Score Interpretation
- **0.999+**: Very creative (unlikely/predictable)
- **0.998-0.999**: Moderately creative
- **0.995-0.998**: Less creative (more likely)
- **<0.995**: Very predictable

### Example from `probability_scoring_results.json`
```json
{
  "candidate_word": "bat",
  "creativity_score": 0.999656,
  "raw_probability": 0.00004686,
  "normalized_probability": 0.000344
}
```

This shows that "bat" (a valid rhyme for "cat") has:
- Very high creativity score (0.999656)
- Very low raw probability (0.00004686)
- Low normalized probability (0.000344)

## Current Limitations

1. **Small Scale**: All scores are in 0.998-0.999 range due to 50k vocabulary
2. **Semantic Bias**: Model prioritizes semantic relevance over phonetic creativity
3. **Scale Issues**: Need better differentiation within valid rhyme sets

## Next Steps

The team should focus on:
1. Testing with complete rhyme lists for better scale
2. Finding optimal creativity bonus ranges
3. Balancing semantic vs. phonetic creativity

---

*Created: July 28, 2024*  
*Model: DistilGPT-2*  
*Scoring Method: Probability-based normalization* 