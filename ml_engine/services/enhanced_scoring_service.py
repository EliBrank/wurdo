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

# Add models directory to path
sys.path.append(str(Path(__file__).parent.parent / "models"))

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
    
    def __init__(self, model_name: str = "distilgpt2", device: str = "cpu", storage_type: str = "json", json_file_path: str = "probability_trees.json"):
        """Initialize the enhanced scoring service with optimized probability trees."""
        self.word_service = EfficientWordService(model_name, device)
        self.scorer = get_onnx_scorer(model_name, device)
        
        # Initialize optimized storage service
        storage_config = StorageConfig(
            storage_type=storage_type,
            json_file_path=json_file_path,
            compression=True,
            cache_size=1000
        )
        self.storage = get_optimized_storage_service(storage_config)
        
        # Initialize probability tree builder
        self.tree_builder = ProbabilityTreeBuilder(
            model=self.scorer,  # Use our ONNX scorer as the model
            tokenizer=self.scorer.tokenizer,
            vocab_size=50257  # distilGPT-2 vocab size
        )
        
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
                return self.storage.get_probability_tree(start_word)
            
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
        Calculate full conditional probability for a multi-token word using progressive context building.
        
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
        
        # Calculate conditional probabilities for each token with progressive context
        token_probabilities = []
        conditional_probabilities = []
        full_probability = 1.0
        current_context = prompt
        
        for i, token in enumerate(candidate_tokens):
            # Get probability vector for current context
            prob_vector_data = self.scorer.get_probability_vector(current_context)
            probability_vector = prob_vector_data["probability_vector"]
            
            # Get probability for this token in current context
            token_prob = probability_vector[token]
            
            # Scale probability based on valid tokens if provided
            if valid_tokens is not None:
                # Calculate sum of probabilities for valid tokens only
                valid_prob_sum = sum(probability_vector[t] for t in valid_tokens if t < len(probability_vector))
                conditional_prob = token_prob / valid_prob_sum if valid_prob_sum > 0 else 0.0
            else:
                # Fallback to max probability scaling (original behavior)
                max_prob = prob_vector_data["max_probability"]
                conditional_prob = token_prob / max_prob if max_prob > 0 else 0.0
            
            token_probabilities.append(token_prob)
            conditional_probabilities.append(conditional_prob)
            full_probability *= conditional_prob
            
            # Update context for next token (if not the last token)
            if i < len(candidate_tokens) - 1:
                # Decode the current token to add to context
                current_token_text = self.scorer.tokenizer.decode([token])
                # Add space to separate tokens properly
                current_context += current_token_text + " "
        
        # Calculate creativity score (inverted probability)
        creativity_score = 1.0 - full_probability
        
        return MultiTokenProbability(
            full_probability=full_probability,
            token_probabilities=token_probabilities,
            conditional_probabilities=conditional_probabilities,
            creativity_score=creativity_score
        )
    
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
            
            # Calculate base score (500-1000 points)
            base_score = 500 + (500 * creativity_score)
            
            # Calculate category bonus based on transformation type
            category_bonus = self._calculate_category_bonus(
                transformation_category, creativity_score
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
        
        # Calculate base score (500-1000 points)
        base_score = 500 + (500 * prob_result.creativity_score)
        
        # Calculate category bonus based on transformation type
        category_bonus = self._calculate_category_bonus(
            transformation_category, prob_result.creativity_score
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
    
    def _calculate_category_bonus(self, category: str, creativity_score: float) -> float:
        """
        Calculate category-specific bonus based on transformation type.
        
        Args:
            category: Transformation category
            creativity_score: Creativity score (0-1)
            
        Returns:
            Category bonus points
        """
        # Category bonus multipliers and max values
        bonus_configs = {
            # Rhyme bonuses (based on difficulty)
            'prf': {'multiplier': 0.20, 'max_bonus': 100},  # Perfect rhymes (easier)
            'rch': {'multiplier': 0.45, 'max_bonus': 225},  # Rich rhymes/homophones (harder)
            'sln': {'multiplier': 0.35, 'max_bonus': 175},  # Slant rhymes (medium)
            
            # Anagram bonus (very creative)
            'ana': {'multiplier': 0.50, 'max_bonus': 250},
            
            # One-letter-off bonuses (based on difficulty)
            'ola': {'multiplier': 0.30, 'max_bonus': 150},  # Added letter
            'olr': {'multiplier': 0.25, 'max_bonus': 125},  # Removed letter
            'olx': {'multiplier': 0.40, 'max_bonus': 200},  # Changed letter
        }
        
        config = bonus_configs.get(category, {'multiplier': 0.25, 'max_bonus': 125})
        
        # Calculate bonus: multiplier × creativity_score × max_bonus
        bonus = config['multiplier'] * creativity_score * config['max_bonus']
        
        return min(bonus, config['max_bonus'])
    
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
            print(f"🔍 DEBUG [enhanced_scoring_service.py:EnhancedScoringService:score_candidate_comprehensive:280] Received start_word = '{start_word}', candidate_word = '{candidate_word}'")
            
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
            
            best_score = None
            best_category = None
            
            for category, word_list in categories_to_check.items():
                if candidate_word in word_list:
                    # Calculate score for this category (pass cached transformations)
                    score_result = self.calculate_transformation_score_with_cache(
                        start_word, candidate_word, category, transformations
                    )
                    category_results[category] = score_result
                    
                    # Track the best score
                    if best_score is None or score_result.total_score > best_score.total_score:
                        best_score = score_result
                        best_category = category
            
            if best_score is None:
                return {
                    "success": False,
                    "message": f"'{candidate_word}' is not a valid transformation of '{start_word}'",
                    "data": None
                }
            
            return {
                "success": True,
                "message": f"Calculated comprehensive score for '{candidate_word}'",
                "data": {
                    "candidate_word": candidate_word,
                    "start_word": start_word,
                    "best_category": best_category,
                    "best_score": best_score.total_score,
                    "creativity_score": best_score.creativity_score,
                    "full_probability": best_score.full_probability,
                    "base_score": best_score.base_score,
                    "category_bonus": best_score.category_bonus,
                    "token_analysis": best_score.token_analysis,
                    "all_category_scores": {
                        cat: result.total_score for cat, result in category_results.items()
                    },
                    "max_possible_score": 1500.0
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
            
            # Calculate base score (500-1000 points)
            base_score = 500 + (500 * creativity_score)
            
            # Calculate category bonus based on transformation type
            category_bonus = self._calculate_category_bonus(
                transformation_category, creativity_score
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

def get_enhanced_scoring_service(model_name: str = "distilgpt2", device: str = "cpu", storage_type: str = "json", json_file_path: str = "probability_trees.json") -> EnhancedScoringService:
    """Factory function to create EnhancedScoringService instance."""
    return EnhancedScoringService(model_name, device, storage_type, json_file_path) 