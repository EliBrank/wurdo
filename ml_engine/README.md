# ML Engine - Wurdo Word-Chaining Game

## Overview

High-performance ML engine for creativity scoring in the Wurdo word-chaining game. Implements optimized probability tree caching with 65x performance improvement over direct model inference.

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### Setup
```bash
# Build and run the ML engine
docker-compose up --build

# Or run just the ML engine (without Redis)
docker build -t wurdo-ml-engine .
docker run wurdo-ml-engine
```

### Testing the Setup
The container will automatically run a setup test that verifies:
- ✅ All core modules import successfully
- ✅ ONNX model loads correctly
- ✅ Scoring service initializes properly

### Interactive Scoring Game
Test the ML engine with a retro-gaming style interface:

```bash
# Run the interactive scoring game
docker-compose run --rm scoring-game

# Or run directly
docker run -it wurdo-ml-engine python scoring_game.py
```

**Game Features:**
- 🎮 Retro ASCII art title card
- ⚡ Animated loading sequences
- 📊 Visual progress bars for scores
- 🎯 Interactive word input
- 🏆 Detailed score breakdown by category

**Example Session:**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ██╗    ██╗██╗   ██╗██████╗ ██████╗  ██████╗                          ║
║    ██║    ██║██║   ██║██╔══██╗██╔══██╗██╔═══██╗                          ║
║    ██║ █╗ ██║██║   ██║██████╔╝██║  ██║██║   ██║                          ║
║    ██║███╗██║██║   ██║██╔══██╗██║  ██║██║   ██║                          ║
║    ╚███╔███╔╝╚██████╔╝██║  ██║██████╔╝╚██████╔╝                          ║
║     ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝                           ║
║                                                                              ║
║                    ✧ Transform • Anagram • Rhyme • One-Letter-Off ✧        ║
║                                                                              ║
║                         Slant rhymes = bonus points!                        ║
║                           Low stakes, high fun!                            ║
║                                                                              ║
║                              atlas_school 2005                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

⠋ Loading ML Engine... 0%
⠙ Loading ML Engine... 5%
...
✅ ML Engine Ready!    100%

╔══════════════════════════════════════════════════════════════════════════════╗
║                              HOW TO PLAY                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎯 Enter a START WORD (e.g., 'xylophone')                                 ║
║  🎯 Enter a CANDIDATE WORD (e.g., 'telephone')                             ║
║  📊 See the creativity score breakdown                                      ║
║  🚪 Type 'quit' to exit                                                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 START WORD xylophone
🎯 CANDIDATE WORD telephone

🔄 Calculating creativity score...
⠋ Processing...

════════════════════════════════════════════════════════════════════════════════
📊 SCORE RESULTS
════════════════════════════════════════════════════════════════════════════════
🎯 XYLOPHONE → TELEPHONE
🏆 Overall Score: 0.8234 (82%)
   [████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

🔤 Ana 0.1234 (12%) [████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]
🔀 Olo 0.5678 (57%) [████████████████████████████████████████████████████████]
🎵 Rhy 0.9012 (90%) [████████████████████████████████████████████████████████]
📊 Frq 0.3456 (35%) [████████████████████████████████████████████████████████]
⭐ Prf 0.7890 (79%) [████████████████████████████████████████████████████████]
════════════════════════════════════════════════════════════════════════════════
```

## Architecture

### Core Components

**Models:**
- `production_onnx_scorer.py` - ONNX model interface with token-by-token processing
- `probability_tree.py` - Sparse hierarchical data structures for conditional probabilities
- `shared_word_engine.py` - Singleton wrapper for word processing

**Services:**
- `enhanced_scoring_service.py` - Main scoring orchestration with probability tree caching
- `optimized_storage_service.py` - Serialization, compression, and in-memory caching
- `efficient_word_service.py` - Word transformation and processing

**Assets:**
- `distilgpt2_onnx/` - ONNX model files (80MB model, tokenizer, config)

**Data:**
- `game_data/` - Anagrams, frequencies, and word lists
- `probability_trees.json` - Cached probability trees (10.2 KB)
- `scoring_game_results.json` - Game scoring results

**Utils:**
- `examine_stored_data.py` - Data verification and inspection
- `speed_test.py` - Performance benchmarking

## Performance Achievements

**Speed Improvement:**
- Build time: 70+ seconds → 1.08 seconds (65x faster)
- Caching strategy eliminates 99% of redundant model calls

**Storage Efficiency:**
- 150 token sequences in 10.2 KB (30.6 sequences/KB)
- 125 probability entries with real model probabilities
- Gzip + pickle compression (52% ratio)

**Mathematical Accuracy:**
- All probability distributions sum to 1.0
- Proper val-to-prb mapping verified
- Nested structure integrity confirmed

## Scoring System

### Base Scoring by Category and Length

The scoring system factors in both transformation category and word length to reward more complex and creative transformations.

#### Base Scores by Category and Length

| Category | 3-char | 4-char | 5-char | 6-char | 7-char |
|----------|--------|--------|--------|--------|--------|
| **OLA** (One-Letter-Added) | 100 | 200 | 300 | 400 | 500 |
| **OLR** (One-Letter-Removed) | 100 | 200 | 300 | 400 | 500 |
| **OLX** (One-Letter-Changed) | 100 | 200 | 300 | 400 | 500 |
| **PRF** (Perfect Rhymes) | 50 | 100 | 150 | 200 | 250 |
| **RCH** (Rich Rhymes/Homophones) | 150 | 300 | 450 | 600 | 750 |
| **ANA** (Anagrams) | 100 | 300 | 500 | 700 | 900 |

#### Length Multipliers

- **OLO, PRF, and RCH transformations**: 1x at 3 chars, 2x at 4 chars, 3x at 5 chars, 4x at 6 chars, 5x at 7 chars
- **ANA transformations**: 1x for 3 chars, 3x for 4 chars, 5x for 5 chars, 7x for 6 chars, 9x for 7 chars

#### Bonus Scoring

For all categories, creativity scoring adds a bonus calculated as:
```
bonus = base_score × 0.5 × creativity_score
```

#### Total Score Formula

```
total_score = base_score + bonus
```

#### Example Scores (creativity = 1.0)

| Category | Length | Base Score | Bonus | Total Score |
|----------|--------|------------|-------|-------------|
| **PRF** | 3 | 50 | 25 | 75 |
| **PRF** | 7 | 250 | 125 | 375 |
| **RCH** | 3 | 150 | 75 | 225 |
| **RCH** | 7 | 750 | 375 | 1125 |
| **ANA** | 3 | 100 | 50 | 150 |
| **ANA** | 7 | 900 | 450 | 1350 |

### Creativity Scoring Improvements

### Distribution Expansion Algorithm

**Problem Solved:**
- Original creativity scores had narrow distribution (0.0-0.1 range)
- Bimodal clustering at extremes (very predictable vs very creative)
- Poor differentiation between word creativity levels

**Solution Implemented:**
```python
def _expand_creativity_distribution(self, raw_score: float) -> float:
    # Power function expansion (cube root)
    power_expanded = raw_score ** (1/3)
    
    # Sigmoid-like transformation for smooth expansion
    k = 2.5, x0 = 0.3
    sigmoid_expanded = 1.0 / (1.0 + np.exp(-k * (power_expanded - x0)))
    
    # Linear scaling to maximize range
    expanded_score = sigmoid_expanded * 1.2
    
    return max(0.0, min(1.0, expanded_score))
```

**Results Achieved:**
- **Broader Distribution:** 0.39 - 1.0 range (vs 0.0-0.1 before)
- **Better Differentiation:** Clear separation between creativity levels
- **Preserved Relationships:** Relative word creativity maintained
- **Uniform Application:** All scoring methods use same expansion

### Length Normalization

**Problem Solved:**
- Multi-token words artificially penalized vs single-token words
- Token count bias in creativity scoring

**Solution Implemented:**
```python
# In calculate_multi_token_probability
final_probability = current_rms / len(candidate_tokens)  # Length normalization
```

### RMS Normalization

**Problem Solved:**
- Traditional multiplicative probability chains caused vanishing gradients
- Extreme values clustered at 0% or 100% creativity

**Solution Implemented:**
```python
# Root-Mean-Square of conditional probabilities
squared_sum = sum(prob ** 2 for prob in conditional_probabilities)
rms_probability = (squared_sum / len(conditional_probabilities)) ** 0.5
creativity_score = 1.0 - rms_probability
```

## Usage

```python
from services.enhanced_scoring_service import get_enhanced_scoring_service

# Initialize scoring service
scoring_service = get_enhanced_scoring_service()

# Score word transformation
score = await scoring_service.score_candidate_comprehensive("xylophone", "telephone")
```

## Technical Notes

**Optimization Strategy:**
- Sparse probability storage (only non-zero values)
- Shared probability vector caching
- Token-based keys (integers vs strings)
- Null sentinel values for empty categories

**Model Integration:**
- DistilGPT-2 converted to ONNX with FP16 quantization
- Token-by-token processing for autoregressive model
- tiktoken integration for efficient tokenization

**Data Structures:**
- ProbabilityNode with val/prb/dat components
- WordProbabilityTree with ana/olo/rhy categories
- OptimizedStorageService with serialization/compression

## Dependencies

See `requirements.txt` for Python package dependencies.

## File Structure

```
ml_engine/
├── models/           # ML implementations
├── services/         # Business logic
├── distilgpt2_onnx/ # Model assets
├── game_data/       # Word lists and data
├── utils/           # Utility scripts
├── probability_trees.json
├── scoring_game_results.json
├── scoring_game.py  # Retro gaming interface
├── Dockerfile       # Container setup
├── docker-compose.yml
└── requirements.txt
``` 