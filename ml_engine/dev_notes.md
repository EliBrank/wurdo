# ML Engine Development Notes

## Current Implementation

### Overview
We've implemented a probability-based creativity scoring system using DistilGPT-2 that analyzes word likelihood in context. The system yields logit vectors over the entire token vocabulary (50,257 tokens) and can score any candidate word against any given start word.

### Key Findings

#### ✅ **What Works**
- **Logit Analysis**: The scoring engine successfully yields logit vectors over the whole token vocabulary
- **Context Awareness**: Can use them for probability scoring on any word from any given start word
- **Semantic Understanding**: Model correctly identifies semantic relationships (e.g., "dog" gets higher probability than "tree" for animal-related prompts)
- **Probability Scaling**: Using `candidate_probability / max_probability` gives meaningful creativity scores

#### ⚠️ **Current Limitations**
- **Small Probabilities**: All probabilities are split over 50,000 possibilities, making raw logits very small (0.00001-0.0001 range)
- **Semantic Bias**: Probabilities are significantly boosted by relevance to start_word in natural language
- **Scale Issues**: Raw probabilities are too small to use as meaningful creativity scalars

### Technical Architecture

#### Dependencies
```bash
torch>=2.0.0
transformers>=4.30.0
numpy>=1.24.0
redis>=4.5.0
python-dotenv>=1.0.0
scikit-learn>=1.3.0
```

**⚠️ IMPORTANT**: This is a **proof-of-concept implementation**. The Python dependencies are heavy (~2GB+ for PyTorch + Transformers). We're using this as a temporary solution while we find an ONNX-converted DistilGPT-2 model that can run outside of PyTorch to lighten the package.

#### Scoring Method
```python
# Current approach
normalized_prob = candidate_probability / max_probability
creativity_score = 1.0 - normalized_prob
```

### Example Results
For prompt "a word that rhymes with cat":
- `'dog'`: 0.998667 (semantic related, lower creativity)
- `'hat'`: 0.999421 (valid rhyme, moderate creativity)  
- `'tree'`: 0.999983 (unrelated, highest creativity)

## Future Direction

### Immediate Next Steps
1. **Rhyme List Analysis**: Test with complete lists of rhyming words for example start_words
2. **Scale Optimization**: Find satisfying scale from least-likely valid rhyme to most-likely valid rhyme
3. **Bonus Scaler**: Develop more useful creativity bonus scaler based on rhyme likelihood

### Long-term Goals
1. **ONNX Conversion**: Find or create ONNX-converted DistilGPT-2 model
2. **Lightweight Implementation**: Reduce package size from ~2GB to <100MB
3. **Mobile Optimization**: Ensure scoring works in resource-constrained environments
4. **Integration**: Connect with main Wurdo application

### Research Questions
- Can we get meaningful differentiation within valid rhyme sets?
- What's the optimal scale for creativity bonuses?
- How do we balance semantic relevance vs. phonetic creativity?

## File Structure
```
ml_engine/
├── models/
│   └── advanced_scorer.py      # Main scoring engine
├── tests/
│   ├── test_advanced_scoring.py
│   ├── test_semantic_analysis.py
│   └── test_scorer.py
├── shared_results/             # Team-accessible test results
│   ├── README.md
│   ├── probability_scoring_results.json
│   └── semantic_analysis_results.json
├── requirements.txt
└── dev_notes.md               # This file
```

## Team Access
The `shared_results/` directory contains test output files that the team can review without installing dependencies or running tests. See `shared_results/README.md` for detailed explanations of the results.

## Usage Example
```python
from models.advanced_scorer import get_advanced_scorer

scorer = get_advanced_scorer()
result = scorer.score_candidate_probability_based(
    prompt="a word that rhymes with cat",
    candidate_word="bat"
)
print(f"Creativity score: {result['creativity_score']:.6f}")
```

## Notes
- All test result JSON files are gitignored
- Model files and cache directories are excluded
- Python bytecode and cache files are ignored
- Environment files (.env*) are excluded for security

---

*Last updated: July 28, 2024*
*Status: Proof of concept - ready for rhyme list analysis* 