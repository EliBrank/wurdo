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

### FastAPI Web Application
Run the ML engine as a web service with REST API endpoints:

```bash
# Start the FastAPI server
cd ml_engine
python3 main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Available API Endpoints:**
- `POST /start` - Start a new game with a start word
- `POST /play` - Process a player move and score it
- `POST /end` - End the current game and get performance summary
- `GET /status` - Check service health and status

**Example API Usage:**
```bash
# Start a game
curl -X POST http://localhost:8000/start \
  -H "Content-Type: application/json" \
  -d '{"start_word": "castle"}'

# Play a word
curl -X POST http://localhost:8000/play \
  -H "Content-Type: application/json" \
  -d '{"candidate_word": "castles"}'

# End the game
curl -X POST http://localhost:8000/end \
  -H "Content-Type: application/json"
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
- Real-time ML performance monitoring with detailed breakdowns

**Storage Efficiency Improvement:**
- 150 token sequences: 30.2 MB → 10.2 KB (30.6 sequences/KB)
- 125 probability entries with real model probabilities
- Gzip + pickle compression (52% ratio)
- Hybrid Redis + JSON storage with automatic synchronization
- Reduces redundant compute for ALL players

**Database Estimated Storage:**
- **Complete vocabulary**: 165,587 words
- **Old strategy (full probability arrays)**: 165,587 × 30 MB = **~4.97 TB**
- **Our optimized strategy (sparse trees)**: 165,587 × 10 KB = **~1.66 GB**
- **Storage efficiency improvement**: **3,000x smaller** database size
- **Production impact**: Complete Probability dataset available on mobile devices, and distributed ML network

**Mathematical Accuracy:**
- All probability distributions sum to 1.0
- Proper val-to-prb mapping verified
- Nested structure integrity confirmed
- RMS normalization for stable creativity scoring

**ML Performance Insights:**
- Model calls consume ~97% of ML computation time
- Array building: ~2% of computation time
- Grouping and normalization: ~1% overhead
- Real-time performance tracking during development

## Efficiency Metrics Tracking

**Real-time ML Performance Monitoring:**
The ML engine tracks detailed performance metrics during probability tree generation and provides comprehensive game-level summaries. This enables developers to monitor ML efficiency and identify optimization opportunities.

**Tree Build Performance:**
```
📊 Probability Tree Build Summary for 'zebra':
  Categories: 3 total
  Total Time: 1.116s
  
  Per-Category Averages:
  ├─ Anagrams: 0.667s (0 sequences)
  ├─ One-letter-added: 0.690s (1 sequences)
  ├─ One-letter-changed: 0.664s (8 sequences)
  
  Time Breakdown:
  ├─ Total Grouping:     0.000s (0.0%)
  ├─ Total Model Calls:  1.080s (96.8%)
  ├─ Total Array Building: 0.028s (2.5%)
  ├─ Total Normalization: 0.000s (0.0%)
  └─ Total:              1.116s (100%)
```

**Game Performance Summary:**
```
=== Game Performance Summary ===
Total Rounds Played: 6
Total Categories Built: 22
Total Sequences Generated: 135
Average Categories per Round: 3.67
Average Sequences per Round: 22.50
Total ML Computation Time: 6.000 seconds
ML Time Breakdown:
  ├─ Grouping:        0.030s
  ├─ Model Calls:     5.820s
  ├─ Array Building:   0.120s
  └─ Normalization:   0.030s
Max Categories in a Round: 5
Max Sequences in a Round: 68
===============================
```

**Development Tools:**
- `terminal_game.py` - 🚀 **Primary development tool** for interactive testing with real-time ML performance monitoring
- `scoring_game.py` - Retro gaming interface for scoring demonstrations
- API endpoints return detailed performance summaries in JSON responses
- Cumulative metrics tracking across multiple probability tree builds
- Real-time ML computation time breakdown during development

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

**Development Dependencies:**
See `requirements.txt` for full Python package dependencies including development tools.

**Production Runtime Dependencies:**
See `requirements-runtime.txt` for minimal production dependencies optimized for deployment.

**Key Runtime Dependencies:**
- FastAPI - Web framework
- ONNX Runtime - ML model inference
- Upstash Redis - Distributed caching
- tiktoken - Efficient tokenization
- numpy - Numerical computations

## File Structure

```
ml_engine/
├── models/                    # ML implementations
│   ├── production_onnx_scorer.py
│   ├── probability_tree.py
│   ├── efficient_word_engine.py
│   └── shared_word_engine.py
├── services/                  # Business logic
│   ├── game_service.py       # Main game orchestration
│   ├── enhanced_scoring_service.py
│   ├── optimized_storage_service.py
│   └── efficient_word_service.py
├── distilgpt2_onnx/          # Model assets (80MB quantized)
├── game_data/                # Word lists and data
├── utils/                    # Utility scripts
├── terminal_game.py          # 🚀 Main development tool for testing
├── scoring_game.py           # Retro gaming interface
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Full development dependencies
├── requirements-runtime.txt  # Minimal production dependencies
├── Dockerfile                # Container setup
├── docker-compose.yml
└── README.md
``` 