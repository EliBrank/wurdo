#!/usr/bin/env python3
"""
Efficient Word Service
=====================

Comprehensive service that integrates EfficientWordEngine with the multi-token schema
for all transformation categories (rhymes, anagrams, OLO) with proper probability arrays.
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

from models.shared_word_engine import get_shared_word_engine
from production_onnx_scorer import get_onnx_scorer

logger = logging.getLogger(__name__)

@dataclass
class TransformationData:
    """Comprehensive transformation data for all categories."""
    # Rhymes
    perfect_rhymes: List[str]
    near_rhymes: List[str]
    rich_rhymes: List[str]  # homophones
    slant_rhymes: List[str]
    
    # Anagrams
    anagrams: List[str]
    
    # One-Letter-Off
    added_letters: List[str]
    removed_letters: List[str]
    changed_letters: List[str]
    
    # All transformations
    all_transformations: List[str]

@dataclass
class ProbabilityNode:
    """Recursive probability node for multi-token sequences."""
    probability: float
    remaining_sequences: List[List[int]]
    probability_structure: Dict[str, Any]

@dataclass
class CategoryProbabilityData:
    """Probability data for a transformation category."""
    valid_sequences: List[List[int]]  # Token sequences for valid words
    probability_array: List[float]    # Sparse probability array
    metadata: Dict[str, Any]         # org_max, val_prb_sum, max_dep

class EfficientWordService:
    """
    Comprehensive service for word transformations with multi-token schema support.
    
    Integrates EfficientWordEngine with AdvancedScorer to generate probability arrays
    for all transformation categories according to the schema specification.
    """
    
    def __init__(self, model_name: str = "distilgpt2", device: str = "cpu"):
        """Initialize the service with word engine and ML scorer."""
        self.word_engine = get_shared_word_engine()
        self.scorer = get_onnx_scorer(model_name, device)
        
        logger.info("✅ EfficientWordService initialized successfully")
    
    def get_comprehensive_transformations(self, start_word: str) -> TransformationData:
        """
        Get all transformation types from EfficientWordEngine.
        
        Args:
            start_word: The word to transform
            
        Returns:
            TransformationData with all transformation categories
        """
        print(f"🔍 DEBUG [efficient_word_service.py:EfficientWordService:get_comprehensive_transformations:80] Received start_word = '{start_word}'")
        logger.info(f"🔍 Getting comprehensive transformations for '{start_word}'")
        
        # Get all transformation types from engine
        print(f"🔍 DEBUG: Calling word_engine.get_rhymes('{start_word}')")
        rhymes = self.word_engine.get_rhymes(start_word)
        print(f"🔍 DEBUG: Got {len(rhymes)} rhymes for '{start_word}'")
        
        categorized_rhymes = self.word_engine.categorize_rhymes_by_quality(start_word, rhymes)
        anagrams = self.word_engine.get_anagrams(start_word)
        olo = self.word_engine.get_one_letter_off(start_word)
        
        # Combine all transformations
        all_transformations = (
            categorized_rhymes.get('perfect', []) +
            categorized_rhymes.get('near', []) +
            categorized_rhymes.get('rich', []) +
            categorized_rhymes.get('slant', []) +
            anagrams +
            olo.get('added', []) +
            olo.get('removed', []) +
            olo.get('changed', [])
        )
        
        # Remove duplicates and the start word itself
        all_transformations = list(set(all_transformations) - {start_word})
        
        return TransformationData(
            perfect_rhymes=categorized_rhymes.get('perfect', []),
            near_rhymes=categorized_rhymes.get('near', []),
            rich_rhymes=categorized_rhymes.get('rich', []),
            slant_rhymes=categorized_rhymes.get('slant', []),
            anagrams=anagrams,
            added_letters=olo.get('added', []),
            removed_letters=olo.get('removed', []),
            changed_letters=olo.get('changed', []),
            all_transformations=all_transformations
        )
    
    def tokenize_words(self, words: List[str]) -> Dict[str, List[int]]:
        """
        Tokenize words and handle multi-token sequences.
        
        Args:
            words: List of words to tokenize
            
        Returns:
            Dict mapping words to their token sequences
        """
        tokenized = {}
        
        for word in words:
            try:
                tokens = self.scorer.tokenizer.encode(word)
                tokenized[word] = tokens
                logger.debug(f"Tokenized '{word}' -> {tokens}")
            except Exception as e:
                logger.warning(f"Failed to tokenize '{word}': {e}")
                continue
        
        return tokenized
    
    def _get_category_prompt(self, start_word: str, category_name: str, category_words: List[str]) -> str:
        """
        Generate appropriate prompt for each transformation category.
        
        Args:
            start_word: The original word
            category_name: Category name (e.g., 'prf', 'ana', 'ola')
            category_words: List of valid words in this category
            
        Returns:
            Contextualized prompt for the model
        """
        base_context = f"{start_word} is a word"
        
        # Category-specific prompt templates
        prompt_templates = {
            # Rhyme categories
            'prf': f"{base_context} that rhymes perfectly with words like",
            'rch': f"{base_context} whose homophones are words like",  # homophones
            'sln': f"{base_context} that rhymes partially with words like",
            
            # Anagram category
            'ana': f"{base_context} whose letters can be rearranged to form anagrams like",
            
            # One-letter-off categories
            'ola': f"{base_context} which with the addition of one letter can become words like",
            'olr': f"{base_context} which with one letter removed can become words like", 
            'olx': f"{base_context} which with the change of a single letter can become words like",
        }
        
        # Get the appropriate template
        template = prompt_templates.get(category_name, f"{base_context} that relates to words like")
        
        # Add example words if available (limit to 3 for context)
        example_words = category_words[:3]
        if example_words:
            examples = ", ".join(example_words)
            prompt = f"{template} {examples}."
        else:
            prompt = f"{template} other words."
        
        return prompt
    
    def generate_category_probabilities(self, start_word: str, category_words: List[str], 
                                     category_name: str) -> CategoryProbabilityData:
        """
        Generate probability data for a specific transformation category.
        
        Args:
            start_word: The original word
            category_words: List of valid words in this category
            category_name: Name of the category (e.g., 'prf', 'ana', 'ola')
            
        Returns:
            CategoryProbabilityData with probability array and metadata
        """
        if not category_words:
            logger.info(f"No {category_name} transformations found for '{start_word}'")
            return CategoryProbabilityData(
                valid_sequences=[],
                probability_array=[0.0] * 50257,  # distilGPT-2 vocab size
                metadata={'org_max': 0.0, 'val_prb_sum': 0.0, 'max_dep': 0}
            )
        
        # Tokenize category words
        tokenized_words = self.tokenize_words(category_words)
        
        # For schema generation, create simplified probability data
        # This avoids the need for ML model calls during data generation
        valid_sequences = []
        word_probabilities = {}
        
        # Create simplified probability array
        sparse_array = [0.0] * 50257  # distilGPT-2 vocab size
        
        for word, tokens in tokenized_words.items():
            if not tokens:
                continue
                
            # Store token sequence
            valid_sequences.append(tokens)
            
            # Assign simple probability based on word length (shorter = more probable)
            word_prob = 1.0 / (len(word) + 1)  # Simplified probability
            word_probabilities[word] = word_prob
            
            # Set probability for first token
            if tokens:
                sparse_array[tokens[0]] = word_prob
        
        # Calculate metadata
        org_max = max(word_probabilities.values()) if word_probabilities else 0.0
        val_prb_sum = sum(word_probabilities.values())
        max_dep = max(len(seq) for seq in valid_sequences) if valid_sequences else 0
        
        return CategoryProbabilityData(
            valid_sequences=valid_sequences,
            probability_array=sparse_array,
            metadata={
                'org_max': org_max,
                'val_prb_sum': val_prb_sum,
                'max_dep': max_dep
            }
        )
    
    def _group_words_by_first_token(self, tokenized_words: Dict[str, List[int]]) -> Dict[int, List[Tuple[str, List[int]]]]:
        """
        Group words by their first token for efficient probability generation.
        
        Args:
            tokenized_words: Dict mapping words to their token sequences
            
        Returns:
            Dict mapping first tokens to lists of (word, tokens) tuples
        """
        first_token_groups = {}
        
        for word, tokens in tokenized_words.items():
            if not tokens:
                continue
                
            first_token = tokens[0]
            if first_token not in first_token_groups:
                first_token_groups[first_token] = []
            
            first_token_groups[first_token].append((word, tokens))
        
        return first_token_groups
    
    def _calculate_word_probability(self, tokens: List[int], probability_vector: List[float], 
                                  max_prob: float) -> float:
        """
        Calculate probability for a multi-token word using conditional probability.
        
        Args:
            tokens: Token sequence for the word
            probability_vector: Full probability vector
            max_prob: Maximum probability for normalization
            
        Returns:
            Probability for the word
        """
        if not tokens:
            return 0.0
        
        # For single token words, use direct lookup
        if len(tokens) == 1:
            token_prob = probability_vector[tokens[0]]
            return token_prob / max_prob if max_prob > 0 else 0.0
        
        # For multi-token words, calculate conditional probability
        # P(word) = P(token1) * P(token2|token1) * P(token3|token1,token2) * ...
        total_prob = 1.0
        
        for i, token in enumerate(tokens):
            if i == 0:
                # First token probability from the main vector
                token_prob = probability_vector[token]
                total_prob *= token_prob / max_prob if max_prob > 0 else 0.0
            else:
                # For subsequent tokens, we would ideally use context-specific probabilities
                # For now, use a simplified approach that considers the token's frequency
                # in the vocabulary as a proxy for conditional probability
                token_prob = probability_vector[token]
                
                # Apply a context penalty for longer sequences
                # This encourages shorter, more likely sequences
                context_penalty = 1.0 / (i + 1)  # Decreasing penalty for each token
                adjusted_prob = token_prob * context_penalty
                
                total_prob *= adjusted_prob / max_prob if max_prob > 0 else 0.0
        
        return total_prob
    
    def _create_sparse_probability_array(self, valid_sequences: List[List[int]], 
                                       word_probabilities: Dict[str, float], 
                                       vocab_size: int) -> List[float]:
        """
        Create sparse probability array for valid token sequences.
        
        Args:
            valid_sequences: List of token sequences
            word_probabilities: Dict mapping words to probabilities
            vocab_size: Size of vocabulary
            
        Returns:
            Sparse probability array with child node structures for multi-token words
        """
        # Initialize sparse array
        sparse_array = [0.0] * vocab_size
        
        # Group sequences by length for better organization
        single_token_words = []
        multi_token_words = []
        
        for i, sequence in enumerate(valid_sequences):
            word = list(word_probabilities.keys())[i]
            if len(sequence) == 1:
                single_token_words.append((sequence[0], word_probabilities[word]))
            else:
                multi_token_words.append((sequence, word_probabilities[word]))
        
        # Handle single-token words (direct probability assignment)
        for token_idx, prob in single_token_words:
            sparse_array[token_idx] = prob
        
        # Handle multi-token words (create child node structures)
        # Group multi-token words by first token
        multi_token_groups = {}
        for sequence, prob in multi_token_words:
            first_token = sequence[0]
            if first_token not in multi_token_groups:
                multi_token_groups[first_token] = []
            multi_token_groups[first_token].append((sequence, prob))
        
        # Create child node structures for each first token group
        for first_token, sequences_and_probs in multi_token_groups.items():
            sequences = [seq for seq, _ in sequences_and_probs]
            probabilities = [prob for _, prob in sequences_and_probs]
            
            # Create child node structure for all sequences sharing this first token
            child_node = self._create_child_node_structure(sequences, probabilities)
            sparse_array[first_token] = child_node
        
        return sparse_array
    
    def _create_child_node_structure(self, sequences: List[List[int]], probabilities: List[float]) -> List:
        """
        Create a child node structure for multiple sequences sharing the same first token.
        
        Args:
            sequences: List of token sequences (all sharing same first token)
            probabilities: List of probabilities for each sequence
            
        Returns:
            Child node structure: [probability, remaining_sequences, probability_structure]
        """
        if not sequences:
            return [0.0, [], {}]
        
        # All sequences should have the same first token
        first_token = sequences[0][0]
        
        # Extract remaining sequences (all sequences minus first token)
        remaining_sequences = [seq[1:] for seq in sequences if len(seq) > 1]
        
        # Calculate combined probability for this first token
        combined_probability = sum(probabilities)
        
        # Create child node structure
        child_node = [
            combined_probability,  # [0] combined probability for this first token
            remaining_sequences,   # [1] remaining token sequences for all words
            {  # [2] probability structure for next tokens
                'arr': [0.0] * self.scorer.tokenizer.vocab_size,  # Will be populated if needed
                'dat': {
                    'org_max': max(probabilities) if probabilities else 0.0,
                    'val_prb_sum': combined_probability,
                    'max_dep': max(len(seq) for seq in remaining_sequences) if remaining_sequences else 0
                }
            }
        ]
        
        return child_node
    
    def generate_schema_data(self, start_word: str) -> Dict[str, Any]:
        """
        Generate complete schema data for a start word.
        
        Args:
            start_word: The word to generate data for
            
        Returns:
            Complete schema data structure
        """
        logger.info(f"🏗️ Generating schema data for '{start_word}'")
        
        # Get all transformations
        transformations = self.get_comprehensive_transformations(start_word)
        
        # Get word frequency
        frequency = self.word_engine.get_creativity_score(start_word)
        
        # Generate probability data for each category
        schema_data = {
            'frq': int(frequency * 1000000),  # Convert to integer frequency
            'ana': self._generate_category_schema(
                start_word, transformations.anagrams, 'ana'
            ),
            'olo': {
                'ola': self._generate_category_schema(
                    start_word, transformations.added_letters, 'ola'
                ),
                'olr': self._generate_category_schema(
                    start_word, transformations.removed_letters, 'olr'
                ),
                'olx': self._generate_category_schema(
                    start_word, transformations.changed_letters, 'olx'
                )
            },
            'rhy': {
                'prf': self._generate_category_schema(
                    start_word, transformations.perfect_rhymes, 'prf'
                ),
                'rch': self._generate_category_schema(
                    start_word, transformations.rich_rhymes, 'rch'
                ),
                'sln': self._generate_category_schema(
                    start_word, transformations.slant_rhymes, 'sln'
                )
            }
        }
        
        logger.info(f"✅ Generated schema data for '{start_word}' with {len(transformations.all_transformations)} transformations")
        return schema_data
    
    def _generate_category_schema(self, start_word: str, category_words: List[str], 
                                category_name: str) -> Dict[str, Any]:
        """
        Generate schema data for a specific category.
        
        Args:
            start_word: The original word
            category_words: List of words in this category
            category_name: Category name
            
        Returns:
            Category schema data
        """
        prob_data = self.generate_category_probabilities(start_word, category_words, category_name)
        
        return {
            'val': prob_data.valid_sequences,
            'prb': {
                'arr': prob_data.probability_array,
                'dat': prob_data.metadata
            }
        }
    
    async def prepare_word_for_gameplay(self, start_word: str) -> Dict[str, Any]:
        """
        Prepare a word for gameplay with complete schema data.
        
        Args:
            start_word: The word to prepare
            
        Returns:
            Complete gameplay data
        """
        try:
            logger.info(f"🎮 Preparing '{start_word}' for gameplay")
            
            # Generate schema data
            schema_data = self.generate_schema_data(start_word)
            
            # Get transformation summary
            transformations = self.get_comprehensive_transformations(start_word)
            
            return {
                "success": True,
                "start_word": start_word,
                "schema_data": schema_data,
                "transformation_summary": {
                    "total_transformations": len(transformations.all_transformations),
                    "perfect_rhymes": len(transformations.perfect_rhymes),
                    "rich_rhymes": len(transformations.rich_rhymes),
                    "slant_rhymes": len(transformations.slant_rhymes),
                    "anagrams": len(transformations.anagrams),
                    "added_letters": len(transformations.added_letters),
                    "removed_letters": len(transformations.removed_letters),
                    "changed_letters": len(transformations.changed_letters)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare '{start_word}' for gameplay: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def demonstrate_prompts(self, start_word: str) -> Dict[str, str]:
        """
        Demonstrate the contextualized prompts for each category.
        
        Args:
            start_word: The word to generate prompts for
            
        Returns:
            Dict mapping category names to their prompts
        """
        transformations = self.get_comprehensive_transformations(start_word)
        
        prompts = {}
        categories = {
            'prf': transformations.perfect_rhymes,
            'rch': transformations.rich_rhymes,
            'sln': transformations.slant_rhymes,
            'ana': transformations.anagrams,
            'ola': transformations.added_letters,
            'olr': transformations.removed_letters,
            'olx': transformations.changed_letters
        }
        
        for category_name, category_words in categories.items():
            prompt = self._get_category_prompt(start_word, category_name, category_words)
            prompts[category_name] = prompt
        
        return prompts
    
    def demonstrate_efficient_grouping(self, start_word: str, category_name: str = 'ana') -> Dict[str, Any]:
        """
        Demonstrate the efficient grouping by first token.
        
        Args:
            start_word: The word to analyze
            category_name: Category to demonstrate (default: anagrams)
            
        Returns:
            Dict with grouping information
        """
        transformations = self.get_comprehensive_transformations(start_word)
        
        # Get words for the specified category
        category_words = getattr(transformations, {
            'prf': 'perfect_rhymes',
            'rch': 'rich_rhymes', 
            'sln': 'slant_rhymes',
            'ana': 'anagrams',
            'ola': 'added_letters',
            'olr': 'removed_letters',
            'olx': 'changed_letters'
        }.get(category_name, 'anagrams'))
        
        # Tokenize words
        tokenized_words = self.tokenize_words(category_words)
        
        # Group by first token
        first_token_groups = self._group_words_by_first_token(tokenized_words)
        
        # Analyze grouping efficiency
        total_words = len(category_words)
        total_groups = len(first_token_groups)
        efficiency_gain = total_words - total_groups
        
        return {
            'category': category_name,
            'total_words': total_words,
            'total_groups': total_groups,
            'efficiency_gain': efficiency_gain,
            'grouping_details': {
                token: [word for word, _ in words] 
                for token, words in first_token_groups.items()
            }
        }

def get_efficient_word_service(model_name: str = "distilgpt2", device: str = "cpu") -> EfficientWordService:
    """Factory function to create EfficientWordService instance."""
    return EfficientWordService(model_name, device) 