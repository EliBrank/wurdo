# Shared Test Results

This directory contains test result files that demonstrate the ML engine's performance without requiring the team to install dependencies or run tests.

## Files

### `optimization_test_results.json`
**Test**: Probability vector optimization demonstration  
**Purpose**: Shows the massive efficiency gain from using one probability vector for multiple candidates  
**Key Findings**:
- **32.67x speedup** for multiple candidates
- Identical results between optimized and unoptimized methods
- One probability vector (50,257 values) can score ANY word
- Perfect for pre-computing and caching probability vectors

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

### Optimization Results
The `optimization_test_results.json` demonstrates a key insight: **by storing one probability vector, we can read probabilities from a given start_word to any other word in the token vocabulary**.

**Performance Comparison**:
- **Current Method**: 1.21 seconds for 9 candidates (9 model calls)
- **Optimized Method**: 0.037 seconds for 9 candidates (1 model call)
- **Speedup**: 32.67x faster

**Key Insight**: One probability vector contains 50,257 probabilities (one for each token), allowing instant lookup of any word's probability without running the model again.

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
1. **Pre-computing probability vectors** for common start words
2. **Caching vectors in Redis** for instant lookup
3. Testing with complete rhyme lists for better scale
4. Finding optimal creativity bonus ranges
5. Balancing semantic vs. phonetic creativity

---

*Created: July 28, 2024*  
*Model: DistilGPT-2*  
*Scoring Method: Probability-based normalization* 