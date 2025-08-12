#!/usr/bin/env python3
"""
Enhanced Scoring Service
=======================

Advanced scoring system that properly handles multi-token conditional probabilities
for accurate creativity scoring across all transformation categories.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import sys

# Add ml_engine root to path for absolute imports
sys.path.append(str(Path(__file__).parent.parent))

from services.efficient_word_service import EfficientWordService
from models.production_onnx_scorer import get_onnx_scorer
from services.optimized_storage_service import get_optimized_storage_service, StorageConfig
from models.probability_tree import (
    ProbabilityTreeBuilder, 
    ProbabilityTreeLookup, 
    validate_probability_tree,
    WordProbabilityTree
)

logger = logging.getLogger(__name__)

@dataclass
class MultiTokenProbability:
    """Multi-token probability calculation result."""
    full_probability: float
    token_probabilities: List[float]
    conditional_probabilities: List[float]
    creativity_score: float

@dataclass
class ScoringResult:
    """Complete scoring result for a candidate word."""
    candidate_word: str
    start_word: str
    transformation_category: str
    full_probability: float
    creativity_score: float
    base_score: float
    category_bonus: float
    total_score: float
    token_analysis: Dict[str, Any]

class EnhancedScoringService:
    """
    Enhanced scoring service that properly handles multi-token conditional probabilities.
    
    Key improvements:
    1. Calculates full conditional probability: P(word) = P(token1) × P(token2|token1) × ...
    2. Uses final probability as creativity scaler
    3. Applies to all transformation categories (rhymes, anagrams, OLO)
    4. Handles multi-token words correctly
    """
    
    def __init__(self, model_name: str = "distilgpt2", device: str = "cpu", storage_type: str = "json", json_file_path: str = None, storage_service=None):
        """
        Initialize enhanced scoring service with optimized storage.
        
        Args:
            model_name: Name of the ML model to use
            device: Device to run model on ('cpu' or 'cuda')
            storage_type: Storage backend ('json' or 'redis') - only used if storage_service not provided
            json_file_path: Path to JSON storage file (defaults to main game_data location) - only used if storage_service not provided
            storage_service: Existing storage service instance to use (overrides storage_type and json_file_path)
        """
        # Set default path to main game_data location
        if json_file_path is None:
            json_file_path = str(Path(__file__).parent.parent / "game_data" / "probability_trees.json")
        
        self.model_name = model_name
        self.device = device
        
        # Use provided storage service or create new one
        if storage_service is not None:
            self.storage = storage_service
        else:
            # Initialize storage with optimized configuration
            storage_config = StorageConfig(
                storage_type=storage_type,
                json_file_path=json_file_path,
                compression=True,
                cache_size=1000
            )
            self.storage = get_optimized_storage_service(storage_config)
        
        # Initialize word service and scorer
        self.word_service = EfficientWordService(model_name, device)
        self.scorer = get_onnx_scorer(model_name, device)
        
        # Initialize probability tree builder
        self.tree_builder = ProbabilityTreeBuilder(
            model=self.scorer,  # Use our ONNX scorer as the model
            tokenizer=self.scorer.tokenizer,
            vocab_size=50257  # distilGPT-2 vocab size
        )
        
        # Initialize scoring caches for efficiency
        self._base_score_cache = {}  # Cache for base scores
        self._bonus_cache = {}       # Cache for category bonuses
        
        # Initialize the production ONNX model
        model_path = str(Path(__file__).parent.parent / "distilgpt2_onnx" / "model.onnx")
        if not self.scorer.initialize(model_path):
            logger.warning(f"Failed to initialize ONNX model from {model_path}")
            logger.error("ONNX model initialization failed - no fallback available")
            raise RuntimeError("Failed to initialize ONNX model")
        
        logger.info("✅ EnhancedScoringService initialized with optimized probability trees")
    
    def _get_or_build_probability_tree(self, start_word: str, cached_transformations=None) -> Optional[WordProbabilityTree]:
        """
        Get or build probability tree with lazy caching.
        
        Args:
            start_word: The word to get tree for
            cached_transformations: Pre-computed transformations to avoid duplicate calls
            
        Returns:
            WordProbabilityTree or None if building fails
        """
        try:
            # Check if tree exists in storage
            if self.storage.has_probability_tree(start_word):
                logger.debug(f"📦 Using cached probability tree for '{start_word}'")
                tree = self.storage.get_probability_tree(start_word)
                
                # DEBUG: Show which storage method was used
                if hasattr(self.storage, 'config') and hasattr(self.storage.config, 'storage_type'):
                    storage_type = self.storage.config.storage_type
                    if storage_type == "hybrid":
                        # For hybrid, check if it came from Redis or JSON
                        if hasattr(self.storage, 'redis') and self.storage.redis.exists(f"tree:{start_word}"):
                            logger.info(f"🎯 SCORING FROM REDIS STORAGE (efficient base64) for '{start_word}'")
                        else:
                            logger.info(f"📁 SCORING FROM JSON FILE STORAGE for '{start_word}'")
                    elif storage_type == "redis":
                        logger.info(f"🎯 SCORING FROM REDIS STORAGE (efficient base64) for '{start_word}'")
                    else:
                        logger.info(f"📁 SCORING FROM JSON FILE STORAGE for '{start_word}'")
                
                return tree
            
            # Build new tree
            logger.info(f"🔄 Building probability tree for '{start_word}'")
            
            # Get all valid transformations (use cached if provided, otherwise compute)
            if cached_transformations is None:
                transformations = self.word_service.get_comprehensive_transformations(start_word)
            else:
                transformations = cached_transformations
            
            # Prepare valid words for each category
            valid_words = {
                'ana': [self.scorer.tokenizer.encode(word) for word in transformations.anagrams],
                'ola': [self.scorer.tokenizer.encode(word) for word in transformations.added_letters],
                'olr': [self.scorer.tokenizer.encode(word) for word in transformations.removed_letters],
                'olx': [self.scorer.tokenizer.encode(word) for word in transformations.changed_letters],
                'prf': [self.scorer.tokenizer.encode(word) for word in transformations.perfect_rhymes],
                'rch': [self.scorer.tokenizer.encode(word) for word in transformations.rich_rhymes],
                'sln': [self.scorer.tokenizer.encode(word) for word in transformations.slant_rhymes]
            }
            
            # Build probability tree
            tree = self.tree_builder.get_or_build_tree(start_word, valid_words)
            
            # Validate tree
            if validate_probability_tree(tree):
                # Store tree for future use
                self.storage.store_probability_tree(start_word, tree)
                logger.info(f"💾 Stored probability tree for '{start_word}'")
                return tree
            else:
                logger.error(f"❌ Probability tree validation failed for '{start_word}'")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get/build probability tree for '{start_word}': {e}")
            return None
    

    
    def calculate_multi_token_probability(self, prompt: str, candidate_word: str, valid_tokens: List[int] = None) -> MultiTokenProbability:
        """
        Calculate full conditional probability for a multi-token word using progressive context building
        with layer-by-layer RMS normalization to prevent vanishing gradient.
        
        Args:
            prompt: Context prompt for the transformation category
            candidate_word: Word to calculate probability for
            valid_tokens: List of valid token IDs for this transformation category (optional)
            
        Returns:
            MultiTokenProbability with full analysis
        """
        # Tokenize the candidate word
        candidate_tokens = self.scorer.tokenizer.encode(candidate_word)
        
        if not candidate_tokens:
            return MultiTokenProbability(
                full_probability=0.0,
                token_probabilities=[],
                conditional_probabilities=[],
                creativity_score=0.0
            )
        
        # Calculate probabilities for each token with progressive context
        # and layer-by-layer RMS normalization using RAW probabilities
        token_probabilities = []
        conditional_probabilities = []
        current_context = prompt
        
        # Layer-by-layer RMS tracking using raw probabilities
        current_rms = 0.0
        layer_count = 0
        
        for i, token in enumerate(candidate_tokens):
            # Get probability vector for current context
            prob_vector_data = self.scorer.get_probability_vector(current_context)
            probability_vector = prob_vector_data["probability_vector"]
            
            # Get RAW probability for this token in current context
            raw_token_prob = probability_vector[token]
            
            # Store raw token probability
            token_probabilities.append(raw_token_prob)
            
            # Calculate conditional probability for compatibility (but don't use for RMS)
            if valid_tokens is not None:
                # Calculate sum of probabilities for valid tokens only
                valid_prob_sum = sum(probability_vector[t] for t in valid_tokens if t < len(probability_vector))
                conditional_prob = raw_token_prob / valid_prob_sum if valid_prob_sum > 0 else 0.0
            else:
                # Fallback to max probability scaling (original behavior)
                max_prob = prob_vector_data["max_probability"]
                conditional_prob = raw_token_prob / max_prob if max_prob > 0 else 0.0
            
            conditional_probabilities.append(conditional_prob)
            
            # Apply layer-by-layer RMS normalization using RAW probabilities
            layer_count += 1
            current_rms = ((current_rms ** 2 * (layer_count - 1) + raw_token_prob ** 2) / layer_count) ** 0.5
            
            # Update context for next token (if not the last token)
            if i < len(candidate_tokens) - 1:
                # Decode the current token to add to context
                current_token_text = self.scorer.tokenizer.decode([token])
                # Add space to separate tokens properly
                current_context += current_token_text + " "
        
        # Calculate final probability using length-normalized RMS
        final_probability = current_rms / len(candidate_tokens)  # ← LENGTH NORMALIZATION
        
        # Calculate creativity score using UNNORMALIZED RMS (to avoid double penalty)
        creativity_score = self._calculate_layer_rms_creativity_score(conditional_probabilities, current_rms)
        
        return MultiTokenProbability(
            full_probability=final_probability,
            token_probabilities=token_probabilities,
            conditional_probabilities=conditional_probabilities,
            creativity_score=creativity_score
        )
    
    def _calculate_rms_creativity_score(self, conditional_probabilities: List[float], full_probability: float) -> float:
        """
        Calculate creativity score using RMS normalization to reduce bimodal distribution.
        
        This addresses the vanishing gradient problem by:
        1. Using RMS to smooth extreme probability values
        2. Creating more gradual creativity gradients
        3. Reducing sensitivity to outliers
        
        Args:
            conditional_probabilities: List of conditional probabilities for each token
            full_probability: Product of all conditional probabilities
            
        Returns:
            Creativity score (0.0 = predictable, 1.0 = creative)
        """
        if not conditional_probabilities:
            return 0.0
        
        # Calculate RMS of conditional probabilities
        squared_sum = sum(prob ** 2 for prob in conditional_probabilities)
        rms_probability = (squared_sum / len(conditional_probabilities)) ** 0.5
        
        # Calculate RMS-based creativity score
        # Lower RMS = more predictable = lower creativity
        # Higher RMS = more varied = higher creativity
        rms_creativity = 1.0 - rms_probability
        
        # Blend with traditional approach for stability
        traditional_creativity = 1.0 - full_probability
        
        # Weighted combination (favor RMS for better distribution)
        creativity_score = 0.7 * rms_creativity + 0.3 * traditional_creativity
        
        # Apply sigmoid-like smoothing to reduce extreme values
        creativity_score = self._smooth_creativity_score(creativity_score)
        
        return max(0.0, min(1.0, creativity_score))
    
    def _smooth_creativity_score(self, raw_score: float) -> float:
        """
        Apply smoothing function to reduce extreme creativity scores.
        
        Uses a modified sigmoid-like function to create more gradual transitions
        between predictable and creative scores.
        
        Args:
            raw_score: Raw creativity score (0.0 to 1.0)
            
        Returns:
            Smoothed creativity score (0.0 to 1.0)
        """
        # Sigmoid-like smoothing with adjusted parameters
        # This creates more gradual transitions and reduces extreme values
        k = 3.0  # Steepness parameter
        x0 = 0.5  # Midpoint
        
        # Apply smoothing function
        smoothed = 1.0 / (1.0 + np.exp(-k * (raw_score - x0)))
        
        # Ensure we stay in valid range
        return max(0.0, min(1.0, smoothed))
    
    def _calculate_layer_rms_creativity_score(self, conditional_probabilities: List[float], final_rms_probability: float) -> float:
        """
        Calculate creativity score using layer-by-layer RMS normalization.
        
        This method uses the RMS probability calculated progressively at each layer
        instead of the traditional multiplicative chain, preventing vanishing gradient.
        
        Args:
            conditional_probabilities: List of conditional probabilities for each token
            final_rms_probability: RMS probability calculated layer-by-layer
            
        Returns:
            Creativity score (0.0 = predictable, 1.0 = creative)
        """
        if not conditional_probabilities:
            return 0.0
        
        # Use the final RMS probability directly (no blending with traditional)
        creativity_score = 1.0 - final_rms_probability
        
        # Apply smoothing to reduce extreme values
        creativity_score = self._smooth_creativity_score(creativity_score)
        
        return max(0.0, min(1.0, creativity_score))
    
    def demonstrate_progressive_context(self, prompt: str, candidate_word: str) -> Dict[str, Any]:
        """
        Demonstrate progressive context building for multi-token probability calculation.
        
        Args:
            prompt: Initial prompt
            candidate_word: Word to analyze
            
        Returns:
            Dict with progressive context analysis
        """
        candidate_tokens = self.scorer.tokenizer.encode(candidate_word)
        
        if not candidate_tokens:
            return {"error": "Failed to tokenize word"}
        
        context_steps = []
        current_context = prompt
        
        for i, token in enumerate(candidate_tokens):
            # Get probability vector for current context
            prob_vector_data = self.scorer.get_probability_vector(current_context)
            probability_vector = prob_vector_data["probability_vector"]
            max_prob = prob_vector_data["max_probability"]
            
            # Get token probability
            token_prob = probability_vector[token]
            conditional_prob = token_prob / max_prob if max_prob > 0 else 0.0
            
            # Decode token for display
            token_text = self.scorer.tokenizer.decode([token])
            
            context_steps.append({
                "step": i + 1,
                "context": current_context,
                "token": token,
                "token_text": token_text,
                "token_probability": token_prob,
                "conditional_probability": conditional_prob,
                "max_probability": max_prob
            })
            
            # Update context for next step
            if i < len(candidate_tokens) - 1:
                current_context += token_text + " "
        
        return {
            "word": candidate_word,
            "total_tokens": len(candidate_tokens),
            "context_steps": context_steps
        }
    
    def calculate_transformation_score(self, start_word: str, candidate_word: str, 
                                    transformation_category: str) -> ScoringResult:
        """
        Calculate comprehensive score using optimized probability trees.
        
        Args:
            start_word: The original word
            candidate_word: The candidate transformation
            transformation_category: Category (prf, rch, sln, ana, ola, olr, olx)
            
        Returns:
            ScoringResult with complete scoring analysis
        """
        # Get or build probability tree
        tree = self._get_or_build_probability_tree(start_word)
        
        if tree is None:
            logger.error(f"❌ Failed to get probability tree for '{start_word}'")
            logger.info(f"🔄 FALLBACK: Using ML model calculation for '{start_word}' -> '{candidate_word}' (no probability tree available)")
            # Fallback to old method
            return self._calculate_transformation_score_fallback(start_word, candidate_word, transformation_category)
        
        # Map transformation category to tree structure
        category_mapping = {
            'prf': ('rhy', 'prf'),  # Perfect rhymes
            'rch': ('rhy', 'rch'),  # Rich rhymes
            'sln': ('rhy', 'sln'),  # Slant rhymes
            'ana': ('ana', 'ana'),  # Anagrams
            'ola': ('olo', 'ola'),  # One-letter-added
            'olr': ('olo', 'olr'),  # One-letter-removed
            'olx': ('olo', 'olx')   # One-letter-changed
        }
        
        main_category, subcategory = category_mapping.get(transformation_category, (None, None))
        
        if main_category is None:
            logger.error(f"❌ Invalid transformation category: {transformation_category}")
            return self._calculate_transformation_score_fallback(start_word, candidate_word, transformation_category)
        
        # Tokenize candidate word
        candidate_tokens = self.scorer.tokenizer.encode(candidate_word)
        
        if not candidate_tokens:
            logger.warning(f"❌ Failed to tokenize candidate word: {candidate_word}")
            return self._calculate_transformation_score_fallback(start_word, candidate_word, transformation_category)
        
        # Get probability and creativity score from tree
        try:
            sequence_probability = ProbabilityTreeLookup.get_sequence_probability(
                tree, main_category, subcategory, candidate_tokens
            )
            
            creativity_score = ProbabilityTreeLookup.get_creativity_score(
                tree, main_category, subcategory, candidate_tokens
            )
            
            # Calculate base score based on category and word length
            base_score = self._get_base_score(transformation_category, len(candidate_word))
            
            # Calculate category bonus based on transformation type and word length
            category_bonus = self._calculate_category_bonus(
                transformation_category, creativity_score, len(candidate_word)
            )
            
            # Calculate total score
            total_score = base_score + category_bonus
            
            logger.info(f"✅ Calculated score using probability tree: {total_score:.2f}")
            
            return ScoringResult(
                candidate_word=candidate_word,
                start_word=start_word,
                transformation_category=transformation_category,
                full_probability=sequence_probability,
                creativity_score=creativity_score,
                base_score=base_score,
                category_bonus=category_bonus,
                total_score=total_score,
                token_analysis={
                    "token_count": len(candidate_tokens),
                    "candidate_tokens": candidate_tokens,
                    "sequence_probability": sequence_probability,
                    "creativity_score": creativity_score,
                    "using_probability_tree": True,
                    "tree_category": f"{main_category}.{subcategory}"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error calculating score with probability tree: {e}")
            return self._calculate_transformation_score_fallback(start_word, candidate_word, transformation_category)
    
    def _calculate_transformation_score_fallback(self, start_word: str, candidate_word: str, 
                                              transformation_category: str, cached_transformations=None) -> ScoringResult:
        """Fallback method using old ML model approach."""
        logger.warning(f"🔄 Using fallback ML model calculation for '{start_word}' -> '{candidate_word}'")
        
        # Get all transformations to find valid tokens for this category (use cached if provided)
        if cached_transformations is None:
            transformations = self.word_service.get_comprehensive_transformations(start_word)
        else:
            transformations = cached_transformations
        
        # Map category names to transformation lists
        category_mapping = {
            'prf': transformations.perfect_rhymes,
            'rch': transformations.rich_rhymes,
            'sln': transformations.slant_rhymes,
            'ana': transformations.anagrams,
            'ola': transformations.added_letters,
            'olr': transformations.removed_letters,
            'olx': transformations.changed_letters
        }
        
        # Get valid words for this category
        valid_words = category_mapping.get(transformation_category, [])
        
        # Tokenize all valid words to get valid tokens
        valid_tokens = set()
        for word in valid_words:
            tokens = self.scorer.tokenizer.encode(word)
            valid_tokens.update(tokens)
        
        # Create contextualized prompt for this category
        prompt = self._get_category_prompt(start_word, transformation_category, [candidate_word])
        
        # Calculate multi-token probability with valid tokens scaling
        prob_result = self.calculate_multi_token_probability(prompt, candidate_word, list(valid_tokens))
        
        # Calculate base score based on category and word length
        base_score = self._get_base_score(transformation_category, len(candidate_word))
        
        # Calculate category bonus based on transformation type and word length
        category_bonus = self._calculate_category_bonus(
            transformation_category, prob_result.creativity_score, len(candidate_word)
        )
        
        # Calculate total score
        total_score = base_score + category_bonus
        
        return ScoringResult(
            candidate_word=candidate_word,
            start_word=start_word,
            transformation_category=transformation_category,
            full_probability=prob_result.full_probability,
            creativity_score=prob_result.creativity_score,
            base_score=base_score,
            category_bonus=category_bonus,
            total_score=total_score,
            token_analysis={
                "token_count": len(prob_result.token_probabilities),
                "token_probabilities": prob_result.token_probabilities,
                "conditional_probabilities": prob_result.conditional_probabilities,
                "prompt": prompt,
                "valid_tokens_count": len(valid_tokens),
                "using_probability_tree": False,
                "fallback_method": True
            }
        )
    
    def _get_category_prompt(self, start_word: str, category_name: str, 
                           example_words: List[str]) -> str:
        """
        Generate contextualized prompt for scoring.
        
        Args:
            start_word: The original word
            category_name: Category name
            example_words: Example words for context
            
        Returns:
            Contextualized prompt
        """
        base_context = f"{start_word} is a word"
        
        # Category-specific prompt templates
        prompt_templates = {
            # Rhyme categories
            'prf': f"{base_context} that rhymes perfectly with words like",
            'rch': f"{base_context} whose homophones are words like",
            'sln': f"{base_context} that rhymes partially with words like",
            
            # Anagram category
            'ana': f"{base_context} whose letters can be rearranged to form anagrams like",
            
            # One-letter-off categories
            'ola': f"{base_context} which with the addition of one letter can become words like",
            'olr': f"{base_context} which with one letter removed can become words like", 
            'olx': f"{base_context} which with the change of a single letter can become words like",
        }
        
        template = prompt_templates.get(category_name, f"{base_context} that relates to words like")
        
        # Add example words if available
        if example_words:
            examples = ", ".join(example_words[:3])  # Limit to 3 examples
            prompt = f"{template} {examples}. "
        else:
            prompt = f"{template} other words. "
        
        return prompt
    
    def _get_base_score(self, category: str, word_length: int) -> float:
        """
        Get base score based on category and word length with caching for efficiency.
        
        Args:
            category: Transformation category
            word_length: Length of the word (3-7 characters)
            
        Returns:
            Base score for the category and length
        """
        # Create cache key
        cache_key = f"{category}_{word_length}"
        
        # Check cache first
        if cache_key in self._base_score_cache:
            return self._base_score_cache[cache_key]
        
        # Base scores by category and length (3-7 characters)
        base_scores = {
            'ola': {3: 100, 4: 200, 5: 300, 6: 400, 7: 500},  # One-letter-added
            'olr': {3: 100, 4: 200, 5: 300, 6: 400, 7: 500},  # One-letter-removed
            'olx': {3: 100, 4: 200, 5: 300, 6: 400, 7: 500},  # One-letter-changed
            'prf': {3: 50, 4: 100, 5: 150, 6: 200, 7: 250},   # Perfect rhymes
            'rch': {3: 150, 4: 300, 5: 450, 6: 600, 7: 750},  # Rich rhymes/homophones
            'ana': {3: 100, 4: 300, 5: 500, 6: 700, 7: 900},  # Anagrams
            'sln': {3: 75, 4: 150, 5: 225, 6: 300, 7: 375},   # Slant rhymes (intermediate)
        }
        
        # Get base score for category and length, default to 100 if not found
        base_score = base_scores.get(category, {}).get(word_length, 100)
        
        # Cache the result
        self._base_score_cache[cache_key] = base_score
        
        return base_score
    
    def _calculate_category_bonus(self, category: str, creativity_score: float, word_length: int) -> float:
        """
        Calculate category-specific bonus based on transformation type and word length with caching.
        
        Args:
            category: Transformation category
            creativity_score: Creativity score (0-1)
            word_length: Length of the word (3-7 characters)
            
        Returns:
            Category bonus points
        """
        # Create cache key with rounded creativity score for better cache hits
        creativity_rounded = round(creativity_score, 3)  # Round to 3 decimal places
        cache_key = f"{category}_{word_length}_{creativity_rounded}"
        
        # Check cache first
        if cache_key in self._bonus_cache:
            return self._bonus_cache[cache_key]
        
        # Get base score for this category and length
        base_score = self._get_base_score(category, word_length)
        
        # Calculate bonus: base_score × 0.5 × creativity_score
        bonus = base_score * 0.5 * creativity_score
        
        # Cache the result (limit cache size to prevent memory issues)
        if len(self._bonus_cache) < 1000:  # Limit cache to 1000 entries
            self._bonus_cache[cache_key] = bonus
        
        return bonus
    
    def clear_scoring_caches(self):
        """Clear all scoring caches to free memory."""
        self._base_score_cache.clear()
        self._bonus_cache.clear()
        logger.info("🧹 Cleared scoring caches")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about scoring cache usage."""
        return {
            "base_score_cache_size": len(self._base_score_cache),
            "bonus_cache_size": len(self._bonus_cache),
            "total_cache_entries": len(self._base_score_cache) + len(self._bonus_cache)
        }
    
    async def score_candidate_comprehensive(self, start_word: str, candidate_word: str) -> Dict[str, Any]:
        """
        Comprehensive scoring that tries all transformation categories.
        
        Args:
            start_word: The original word
            candidate_word: The candidate word to score
            
        Returns:
            Dict with comprehensive scoring results
        """
        try:
            print(f"🔍 DEBUG [enhanced_scoring_service.py:EnhancedScoringService:280] Received start_word = '{start_word}', candidate_word = '{candidate_word}'")
            
            # Get all possible transformations for the start word (CACHE THIS)
            transformations = self.word_service.get_comprehensive_transformations(start_word)
            
            # Determine which category this candidate belongs to
            category_results = {}
            
            # Check each category
            categories_to_check = {
                'prf': transformations.perfect_rhymes,
                'rch': transformations.rich_rhymes,
                'sln': transformations.slant_rhymes,
                'ana': transformations.anagrams,
                'ola': transformations.added_letters,
                'olr': transformations.removed_letters,
                'olx': transformations.changed_letters
            }
            
            total_score = 0
            valid_categories = []
            category_scores = {}
            
            for category, word_list in categories_to_check.items():
                if candidate_word in word_list:
                    # Calculate score for this category (pass cached transformations)
                    score_result = self.calculate_transformation_score_with_cache(
                        start_word, candidate_word, category, transformations
                    )
                    category_results[category] = score_result
                    category_scores[category] = score_result.total_score
                    valid_categories.append(category)
                    total_score += score_result.total_score
            
            if not valid_categories:
                return {
                    "success": False,
                    "message": f"'{candidate_word}' is not a valid transformation of '{start_word}'",
                    "data": None
                }
            
            # Calculate average creativity score across all categories
            avg_creativity = sum(result.creativity_score for result in category_results.values()) / len(category_results)
            
            return {
                "success": True,
                "message": f"Calculated comprehensive score for '{candidate_word}' across {len(valid_categories)} categories",
                "data": {
                    "candidate_word": candidate_word,
                    "start_word": start_word,
                    "valid_categories": valid_categories,
                    "total_score": total_score,
                    "category_count": len(valid_categories),
                    "avg_creativity_score": avg_creativity,
                    "category_scores": category_scores,
                    "category_results": {
                        cat: {
                            "total_score": result.total_score,
                            "base_score": result.base_score,
                            "category_bonus": result.category_bonus,
                            "creativity_score": result.creativity_score
                        } for cat, result in category_results.items()
                    },
                    "max_possible_score": 1500.0 * len(valid_categories)  # Theoretical max if all categories perfect
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate comprehensive score for '{candidate_word}': {e}")
            return {
                "success": False,
                "message": f"Failed to calculate score: {str(e)}",
                "data": None
            }
    
    def calculate_transformation_score_with_cache(self, start_word: str, candidate_word: str, 
                                               transformation_category: str, cached_transformations) -> ScoringResult:
        """
        Calculate comprehensive score using cached transformations to avoid duplicate calls.
        
        Args:
            start_word: The original word
            candidate_word: The candidate transformation
            transformation_category: Category (prf, rch, sln, ana, ola, olr, olx)
            cached_transformations: Pre-computed transformations
            
        Returns:
            ScoringResult with complete scoring analysis
        """
        # Get or build probability tree with cached transformations
        tree = self._get_or_build_probability_tree(start_word, cached_transformations)
        
        if tree is None:
            logger.error(f"❌ Failed to get probability tree for '{start_word}'")
            # Fallback to old method with cached transformations
            return self._calculate_transformation_score_fallback(start_word, candidate_word, transformation_category, cached_transformations)
        
        # Map transformation category to tree structure
        category_mapping = {
            'prf': ('rhy', 'prf'),  # Perfect rhymes
            'rch': ('rhy', 'rch'),  # Rich rhymes
            'sln': ('rhy', 'sln'),  # Slant rhymes
            'ana': ('ana', 'ana'),  # Anagrams
            'ola': ('olo', 'ola'),  # One-letter-added
            'olr': ('olo', 'olr'),  # One-letter-removed
            'olx': ('olo', 'olx')   # One-letter-changed
        }
        
        main_category, subcategory = category_mapping.get(transformation_category, (None, None))
        
        if main_category is None:
            logger.error(f"❌ Invalid transformation category: {transformation_category}")
            return self._calculate_transformation_score_fallback(start_word, candidate_word, transformation_category, cached_transformations)
        
        # Tokenize candidate word
        candidate_tokens = self.scorer.tokenizer.encode(candidate_word)
        
        if not candidate_tokens:
            logger.warning(f"❌ Failed to tokenize candidate word: {candidate_word}")
            return self._calculate_transformation_score_fallback(start_word, candidate_word, transformation_category, cached_transformations)
        
        # Get probability and creativity score from tree
        try:
            sequence_probability = ProbabilityTreeLookup.get_sequence_probability(
                tree, main_category, subcategory, candidate_tokens
            )
            
            creativity_score = ProbabilityTreeLookup.get_creativity_score(
                tree, main_category, subcategory, candidate_tokens
            )
            
            # Calculate base score based on category and word length
            base_score = self._get_base_score(transformation_category, len(candidate_word))
            
            # Calculate category bonus based on transformation type and word length
            category_bonus = self._calculate_category_bonus(
                transformation_category, creativity_score, len(candidate_word)
            )
            
            # Calculate total score
            total_score = base_score + category_bonus
            
            logger.info(f"✅ Calculated score using probability tree: {total_score:.2f}")
            
            return ScoringResult(
                candidate_word=candidate_word,
                start_word=start_word,
                transformation_category=transformation_category,
                full_probability=sequence_probability,
                creativity_score=creativity_score,
                base_score=base_score,
                category_bonus=category_bonus,
                total_score=total_score,
                token_analysis={
                    "token_count": len(candidate_tokens),
                    "candidate_tokens": candidate_tokens,
                    "sequence_probability": sequence_probability,
                    "creativity_score": creativity_score,
                    "using_probability_tree": True,
                    "tree_category": f"{main_category}.{subcategory}"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error calculating score with probability tree: {e}")
            return self._calculate_transformation_score_fallback(start_word, candidate_word, transformation_category, cached_transformations)

def get_enhanced_scoring_service(model_name: str = "distilgpt2", device: str = "cpu", storage_type: str = "json", json_file_path: str = None, storage_service=None) -> EnhancedScoringService:
    """
    Factory function to create EnhancedScoringService instance.
    
    Args:
        model_name: Name of the ML model to use
        device: Device to run model on ('cpu' or 'cuda')
        storage_type: Storage backend ('json' or 'redis') - only used if storage_service not provided
        json_file_path: Path to JSON storage file (defaults to main game_data location) - only used if storage_service not provided
        storage_service: Existing storage service instance to use (overrides storage_type and json_file_path)
        
    Returns:
        Configured EnhancedScoringService instance
    """
    # Set default path to main game_data location
    if json_file_path is None:
        json_file_path = str(Path(__file__).parent.parent / "game_data" / "probability_trees.json")
    
    return EnhancedScoringService(
        model_name=model_name,
        device=device,
        storage_type=storage_type,
        json_file_path=json_file_path,
        storage_service=storage_service
    ) 