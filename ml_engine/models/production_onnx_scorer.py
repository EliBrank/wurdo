"""
Production-ready ONNX distilGPT-2 scorer with tiktoken
Exact functional replica of advanced_scorer.py with ONNX optimization
"""

import onnxruntime as ort
import tiktoken
import numpy as np
import logging
import threading
from typing import List, Dict, Optional, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DistilGPT2ONNX:
    """
    Production-ready ONNX distilGPT-2 scorer with exact functional parity to advanced_scorer.py
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        with self._lock:
            if self._initialized:
                return
                
            # Core components (exact replica of advanced_scorer.py structure)
            self.model_name = "distilgpt2"
            self.device = "cpu"
            self._session: Optional[ort.InferenceSession] = None
            self._tokenizer: Optional[tiktoken.Encoding] = None
            self.is_initialized = False
            
            # Model constants (matching GPT-2 vocabulary)
            self.vocab_size = 50257
            self.max_context_length = 1024
            self.eos_token_id = 50256
            
            self._initialized = True
    
    @property
    def tokenizer(self):
        """Public access to tokenizer (for compatibility with EnhancedScoringService)"""
        return self._tokenizer
    
    def initialize(self, model_path: str = "distilgpt2_onnx/model.onnx", providers: Optional[List[str]] = None) -> bool:
        """
        Initialize the model and tokenizer (exact replica of advanced_scorer.py initialize method)
        """
        if self.is_initialized:
            return True
            
        logger.info(f"Initializing {self.model_name} ONNX model...")
        
        try:
            # Validate model exists
            if not Path(model_path).exists():
                logger.error(f"Model not found: {model_path}")
                return False
            
            # Setup providers
            if providers is None:
                providers = ['CPUExecutionProvider']
            
            # Load ONNX session (equivalent to AutoModelForCausalLM)
            self._session = ort.InferenceSession(
                model_path,
                providers=providers
            )
            
            # Load tiktoken encoder (equivalent to AutoTokenizer)
            self._tokenizer = tiktoken.get_encoding("gpt2")
            
            # Validate setup
            if not self._validate_setup():
                logger.error("Setup validation failed")
                self._session = None
                self._tokenizer = None
                return False
            
            self.is_initialized = True
            logger.info(f"✅ {self.model_name} ONNX initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.model_name}: {e}")
            return False
    
    def _validate_setup(self) -> bool:
        """Validate that model and tokenizer are properly loaded"""
        try:
            # Test tokenizer
            test_tokens = self._tokenizer.encode("test")
            if not test_tokens:
                return False
            
            # Test model with cache inputs (for the smaller cached model)
            test_input = np.array([[test_tokens[0]]], dtype=np.int64)
            attention_mask = np.ones((1, 1), dtype=np.int64)
            
            # Create cache states (6 layers, each with key and value)
            cache_states = {}
            for i in range(6):
                # Key cache: (batch_size, n_head, seq_len, head_dim)
                cache_states[f'past_key_values.{i}.key'] = np.zeros((1, 12, 0, 64), dtype=np.float32)
                # Value cache: (batch_size, n_head, seq_len, head_dim)  
                cache_states[f'past_key_values.{i}.value'] = np.zeros((1, 12, 0, 64), dtype=np.float32)
            
            # Prepare input feed
            input_feed = {
                'input_ids': test_input,
                'attention_mask': attention_mask,
                **cache_states
            }
            
            outputs = self._session.run(['logits'], input_feed)
            
            # Check output shape
            if outputs[0].shape[-1] != self.vocab_size:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Setup validation failed: {e}")
            return False
    
    def cleanup(self):
        """
        Clean up model and tokenizer to free memory (exact replica of advanced_scorer.py cleanup)
        """
        if self.is_initialized:
            logger.info(f"🧹 Cleaning up {self.model_name} ONNX model...")
            
            # Delete session and tokenizer (equivalent to deleting model and tokenizer)
            if hasattr(self, '_session') and self._session is not None:
                del self._session
                self._session = None
                
            if hasattr(self, '_tokenizer') and self._tokenizer is not None:
                del self._tokenizer
                self._tokenizer = None
            
            self.is_initialized = False
            
            # Force garbage collection
            import gc
            gc.collect()
            
            logger.info(f"✅ {self.model_name} ONNX cleanup completed")
    
    def __del__(self):
        """Destructor to ensure cleanup when object is deleted (exact replica)"""
        self.cleanup()
    
    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        """Numerically stable softmax (equivalent to F.softmax)"""
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / np.sum(exp_logits)
    
    def get_logits_and_probs(self, prompt: str) -> Tuple[np.ndarray, np.ndarray, List[int]]:
        """
        Get both logits and probabilities for a given prompt using token-by-token processing
        
        Returns:
            logits: Raw logits from the model
            probabilities: Softmax probabilities
            tokens: Token IDs for the prompt
        """
        if not self.is_initialized:
            self.initialize()
            
        # Tokenize the prompt (equivalent to AutoTokenizer.encode)
        tokens = self._tokenizer.encode(prompt)
        
        # Apply length limit
        if len(tokens) > self.max_context_length:
            tokens = tokens[-self.max_context_length:]
        
        # Process tokens one at a time, building up cache
        current_cache = {}
        for i in range(6):
            # Initialize empty cache for each layer
            current_cache[f'past_key_values.{i}.key'] = np.zeros((1, 12, 0, 64), dtype=np.float32)
            current_cache[f'past_key_values.{i}.value'] = np.zeros((1, 12, 0, 64), dtype=np.float32)
        
        # Process each token sequentially
        for token_idx, token in enumerate(tokens):
            # Create input for this single token
            input_ids = np.array([[token]], dtype=np.int64)
            attention_mask = np.ones((1, 1), dtype=np.int64)
            
            # Prepare input feed with current cache
            input_feed = {
                'input_ids': input_ids,
                'attention_mask': attention_mask,
                **current_cache
            }
            
            # Get model outputs
            outputs = self._session.run(None, input_feed)
            logits = outputs[0]
            
            # Update cache for next iteration (if not the last token)
            if token_idx < len(tokens) - 1:
                # Extract cache outputs and update current_cache
                for i in range(6):
                    current_cache[f'past_key_values.{i}.key'] = outputs[1 + i*2]  # present.0.key, present.1.key, etc.
                    current_cache[f'past_key_values.{i}.value'] = outputs[2 + i*2]  # present.0.value, present.1.value, etc.
        
        # Get logits and probabilities for the final position
        last_logits = logits[0, -1, :]
        probabilities = self._softmax(last_logits)
        
        return last_logits, probabilities, tokens
    
    def score_candidate_probability_based(self, prompt: str, candidate_word: str) -> Dict:
        """
        Score candidate using probability-based approach (exact replica of advanced_scorer.py method)
        Uses probabilities directly and scales relative to the highest probability.
        """
        try:
            logits, probs, prompt_tokens = self.get_logits_and_probs(prompt)
            
            # Tokenize candidate (equivalent to AutoTokenizer.encode)
            candidate_tokens = self._tokenizer.encode(candidate_word)
            candidate_token = candidate_tokens[0]
            
            # Get candidate probability
            candidate_prob = float(probs[candidate_token])
            
            # Get max probability (most likely token)
            max_prob = float(np.max(probs))
            
            # Scale relative to max probability (0 to max_prob range)
            normalized_prob = candidate_prob / max_prob
            
            # Creativity score: higher probability = more likely = lower creativity
            creativity_score = 1.0 - normalized_prob
            
            return {
                "method": "probability_based",
                "prompt": prompt,
                "candidate_word": candidate_word,
                "candidate_token": candidate_token,
                "raw_probability": candidate_prob,
                "normalized_probability": normalized_prob,
                "creativity_score": creativity_score,
                "max_probability": max_prob
            }
            
        except Exception as e:
            logger.error(f"Error in probability-based scoring: {e}")
            return {"error": str(e)}
    
    def score_multiple_candidates(self, prompt: str, candidates: List[str]) -> Dict:
        """
        Score multiple candidates using probability-based approach (exact replica)
        """
        results = {
            "prompt": prompt,
            "candidates": candidates,
            "scores": []
        }
        
        for candidate in candidates:
            score_result = self.score_candidate_probability_based(prompt, candidate)
            results["scores"].append(score_result)
        
        # Sort by creativity score (highest first)
        results["scores"].sort(key=lambda x: x["creativity_score"], reverse=True)
        
        return results
    
    def score_multiple_candidates_optimized(self, prompt: str, candidates: List[str]) -> Dict:
        """
        Score multiple candidates using ONE probability vector lookup (exact replica)
        Much more efficient than calling the model multiple times.
        """
        try:
            # Get probability vector ONCE
            logits, probs, prompt_tokens = self.get_logits_and_probs(prompt)
            max_prob = float(np.max(probs))
            
            results = {
                "prompt": prompt,
                "candidates": candidates,
                "scores": [],
                "probability_vector_size": len(probs),
                "max_probability": max_prob
            }
            
            # Look up all candidates from the same probability vector
            for candidate in candidates:
                # Tokenize candidate
                candidate_tokens = self._tokenizer.encode(candidate)
                candidate_token = candidate_tokens[0]
                
                # Get candidate probability from the pre-computed vector
                candidate_prob = float(probs[candidate_token])
                
                # Scale relative to max probability
                normalized_prob = candidate_prob / max_prob
                
                # Creativity score
                creativity_score = 1.0 - normalized_prob
                
                score_result = {
                    "method": "probability_based_optimized",
                    "prompt": prompt,
                    "candidate_word": candidate,
                    "candidate_token": candidate_token,
                    "raw_probability": candidate_prob,
                    "normalized_probability": normalized_prob,
                    "creativity_score": creativity_score,
                    "max_probability": max_prob
                }
                
                results["scores"].append(score_result)
            
            # Sort by creativity score (highest first)
            results["scores"].sort(key=lambda x: x["creativity_score"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in optimized scoring: {e}")
            return {"error": str(e)}
    
    def get_probability_vector(self, prompt: str) -> Dict:
        """
        Get the full probability vector for a prompt (exact replica)
        This can be stored and used to look up ANY word's probability.
        """
        try:
            logits, probs, prompt_tokens = self.get_logits_and_probs(prompt)
            
            return {
                "prompt": prompt,
                "probability_vector": probs.tolist(),
                "max_probability": float(np.max(probs)),
                "vocabulary_size": len(probs),
                "prompt_tokens": prompt_tokens
            }
            
        except Exception as e:
            logger.error(f"Error getting probability vector: {e}")
            return {"error": str(e)}
    
    def lookup_candidate_from_vector(self, probability_vector: List[float], candidate_word: str, max_prob: float) -> Dict:
        """
        Look up a candidate's probability from a pre-computed probability vector (exact replica)
        """
        try:
            # Tokenize candidate
            candidate_tokens = self._tokenizer.encode(candidate_word)
            candidate_token = candidate_tokens[0]
            
            # Get candidate probability from the vector
            candidate_prob = probability_vector[candidate_token]
            
            # Scale relative to max probability
            normalized_prob = candidate_prob / max_prob
            
            # Creativity score
            creativity_score = 1.0 - normalized_prob
            
            return {
                "candidate_word": candidate_word,
                "candidate_token": candidate_token,
                "raw_probability": candidate_prob,
                "normalized_probability": normalized_prob,
                "creativity_score": creativity_score
            }
            
        except Exception as e:
            logger.error(f"Error looking up candidate: {e}")
            return {"error": str(e)}
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model (exact replica)"""
        if not self.is_initialized:
            return {"error": "Model not initialized"}
            
        return {
            "model_name": self.model_name,
            "device": self.device,
            "vocabulary_size": self.vocab_size,
            "max_length": self.max_context_length,
            "parameters": "ONNX model - parameters not directly accessible"
        }

# Global singleton instance (exact replica of advanced_scorer.py pattern)
_global_onnx_scorer = None

def get_onnx_scorer(model_name: str = "distilgpt2", device: str = "cpu") -> DistilGPT2ONNX:
    """Get or create a global ONNX scorer instance (exact replica of get_advanced_scorer)"""
    global _global_onnx_scorer
    
    if _global_onnx_scorer is None:
        _global_onnx_scorer = DistilGPT2ONNX()
        _global_onnx_scorer.initialize()
    
    return _global_onnx_scorer

def initialize_onnx_scorer(model_path: str = "distilgpt2_onnx/model.onnx") -> bool:
    """Initialize the global ONNX scorer"""
    scorer = get_onnx_scorer()
    return scorer.initialize(model_path)

def cleanup_onnx_scorer():
    """Clean up the global ONNX scorer"""
    global _global_onnx_scorer
    
    if _global_onnx_scorer is not None:
        _global_onnx_scorer.cleanup()
        _global_onnx_scorer = None

# ============================================================================
# EFFICIENCY IMPROVEMENT NOTES
# ============================================================================

"""
EFFICIENCY ANALYSIS AND IMPROVEMENT IDEAS:

1. MEMORY OPTIMIZATION:
   - Current: Each service creates its own scorer instance
   - Improvement: Single shared ONNX instance across all services
   - Expected: 10-20x memory reduction (2-4GB → 200MB)

2. TOKENIZATION SPEED:
   - Current: AutoTokenizer (Python-based, 100-500ms)
   - Improvement: Tiktoken (Rust-based, 1-10ms)
   - Expected: 50-500x faster tokenization

3. INFERENCE SPEED:
   - Current: PyTorch model (100-500ms inference)
   - Improvement: ONNX runtime (10-50ms inference)
   - Expected: 10x faster inference

4. MODEL LOADING:
   - Current: Multiple model loads (2-4 instances)
   - Improvement: Single shared model (warm throughout session)
   - Expected: 10-50x faster startup

5. THREAD SAFETY:
   - Current: No thread safety (race conditions possible)
   - Improvement: Thread-safe singleton with locks
   - Expected: Reliable multi-threaded operation

6. ERROR HANDLING:
   - Current: Exceptions thrown on errors
   - Improvement: Graceful failures with None returns
   - Expected: More robust error handling

7. VALIDATION:
   - Current: No setup validation
   - Improvement: Comprehensive validation after loading
   - Expected: Better debugging and reliability

8. RESOURCE CLEANUP:
   - Current: Manual cleanup required
   - Improvement: Automatic cleanup with destructors
   - Expected: No memory leaks

9. API COMPATIBILITY:
   - Current: Exact functional parity maintained
   - Improvement: Same interface, better performance
   - Expected: Drop-in replacement with massive speedup

10. STORAGE IMPLICATIONS:
    - Current: Need lookup_data.json for fast scoring
    - Improvement: Real-time generation becomes fast enough
    - Expected: Eliminate need for pre-computed storage

PERFORMANCE PROJECTIONS:
- Generation time: 2.14s → 0.2s (10x faster)
- Memory usage: 2-4GB → 200MB (20x less)
- Startup time: 5-10s → 0.5s (10-20x faster)
- Thread safety: ❌ → ✅ (reliable)

This could make real-time generation faster than lookup, eliminating the need for lookup_data.json storage entirely.
""" 