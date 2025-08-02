import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np

from models.advanced_scorer import get_advanced_scorer
from models.cmu_rhyme_client import CMURhymeClient
from services.rhyme_service import RhymeProcessor
from services.storage_service import StorageService

logger = logging.getLogger(__name__)

class GameWorkflow:
    def __init__(self, storage_type: str = "json", redis_url: str = None, json_file_path: str = "game_data.json"):
        """
        Initialize the game workflow service.
        
        Args:
            storage_type: "json" or "redis"
            redis_url: Redis connection URL (required for redis storage)
            json_file_path: Path to JSON file (for json storage)
        """
        self.scorer = get_advanced_scorer()
        self.storage = StorageService(storage_type, redis_url, json_file_path)
        self.rhyme_processor = RhymeProcessor(self.scorer.tokenizer)
        self.cmu_client = CMURhymeClient()
        
        logger.info(f"Initialized GameWorkflow with {storage_type} storage")
    
    async def generate_rhyme_data(self, start_word: str) -> Dict:
        """
        Generate and store rhyme data for a start word using CMU Dictionary.
        
        Returns:
            Dict with success status and data summary
        """
        try:
            # Check if data already exists
            if self.storage.data_exists(start_word):
                logger.info(f"Rhyme data already exists for '{start_word}'")
                return {
                    "success": True,
                    "message": f"Rhyme data already exists for '{start_word}'",
                    "data": {"cached": True}
                }
            
            # Get rhymes from CMU Dictionary
            logger.info(f"Fetching rhyme data for '{start_word}' from CMU Dictionary...")
            all_rhymes = self.cmu_client.get_rhymes(start_word)
            filtered_rhymes = self.cmu_client.filter_rhymes_by_quality(all_rhymes)
            
            # Create mock API results format for compatibility
            categorized = self.cmu_client.categorize_rhymes_by_quality(start_word, filtered_rhymes)
            
            api_results = {
                "soundLike": [{"word": rhyme, "score": 100, "tags": ["f:10.0"]} for rhyme in categorized.get('perfect', [])],
                "homophones": [],  # CMU doesn't provide homophones directly
                "consonant": [{"word": rhyme, "score": 80, "tags": ["f:5.0"]} for rhyme in categorized.get('near', [])]
            }
            
            # Process and categorize
            logger.info(f"Processing rhyme data for '{start_word}'...")
            rhyme_data = self.rhyme_processor.categorize_rhymes(api_results, start_word)
            
            # Tokenize
            logger.info(f"Tokenizing rhymes for '{start_word}'...")
            tokenized_data = await self.rhyme_processor.tokenize_rhymes(rhyme_data)
            
            # Store in storage
            logger.info(f"Storing rhyme data for '{start_word}'...")
            self.storage.store_rhyme_data(start_word, tokenized_data)
            
            return {
                "success": True,
                "message": f"Generated rhyme data for '{start_word}'",
                "data": {
                    "perfect_count": len(rhyme_data.perfect),
                    "rich_count": len(rhyme_data.rich),
                    "slant_count": len(rhyme_data.slant),
                    "total_count": len(rhyme_data.all_rhymes),
                    "cached": False
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate rhyme data for '{start_word}': {e}")
            return {
                "success": False,
                "message": f"Failed to generate rhyme data: {str(e)}",
                "data": None
            }
    
    async def generate_probability_vector(self, start_word: str) -> Dict:
        """
        Generate and store probability vector for a start word.
        
        Returns:
            Dict with success status and data summary
        """
        try:
            # Check if vector already exists
            existing_vector = self.storage.get_probability_vector(start_word)
            if existing_vector is not None:
                logger.info(f"Probability vector already exists for '{start_word}'")
                return {
                    "success": True,
                    "message": f"Probability vector already exists for '{start_word}'",
                    "data": {"cached": True}
                }
            
            # Generate probability vector
            logger.info(f"Generating probability vector for '{start_word}'...")
            prompt = f"{start_word} is a word that rhymes with"
            _, probs, _ = self.scorer.get_logits_and_probs(prompt)
            
            # Store in storage
            logger.info(f"Storing probability vector for '{start_word}'...")
            self.storage.store_probability_vector(start_word, probs)
            
            # Generate scaling values
            logger.info(f"Generating scaling values for '{start_word}'...")
            scaling_values = self.storage.generate_scaling_values(start_word, probs)
            
            return {
                "success": True,
                "message": f"Generated probability vector for '{start_word}'",
                "data": {
                    "vector_size": len(probs),
                    "max_probability": float(probs.max()),
                    "scaling_values": scaling_values,
                    "cached": False
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate probability vector for '{start_word}': {e}")
            return {
                "success": False,
                "message": f"Failed to generate probability vector: {str(e)}",
                "data": None
            }
    
    def calculate_rhyme_score(self, start_word: str, candidate_word: str) -> Dict:
        """
        Calculate creativity score for a candidate word.
        
        Returns:
            Dict with scoring results
        """
        try:
            # Get stored data
            rhyme_data = self.storage.get_rhyme_data(start_word)
            probability_vector = self.storage.get_probability_vector(start_word)
            
            if not rhyme_data or probability_vector is None:
                return {
                    "success": False,
                    "message": f"No data found for '{start_word}'. Generate data first.",
                    "data": None
                }
            
            # Tokenize candidate word
            candidate_tokens = self.scorer.tokenizer.encode(candidate_word)
            if not candidate_tokens:
                return {
                    "success": False,
                    "message": f"Failed to tokenize candidate word '{candidate_word}'",
                    "data": None
                }
            
            candidate_token = candidate_tokens[0]
            
            # Check if candidate is a valid rhyme
            if candidate_token not in rhyme_data["all_tokens"]:
                return {
                    "success": False,
                    "message": f"'{candidate_word}' is not a valid rhyme for '{start_word}'",
                    "data": None
                }
            
            # Get candidate probability
            if candidate_token >= len(probability_vector):
                return {
                    "success": False,
                    "message": f"Token index {candidate_token} out of range for probability vector",
                    "data": None
                }
            
            candidate_prob = probability_vector[candidate_token]
            
            # Calculate base rhyme score (500-1000 points)
            # Use rhyme-specific scaling instead of global max
            rhyme_scaling = self.storage.data[start_word].get("rhy.sc", {"min": 0, "max": 1})
            if rhyme_scaling["max"] > rhyme_scaling["min"]:
                normalized_prob = (candidate_prob - rhyme_scaling["min"]) / (rhyme_scaling["max"] - rhyme_scaling["min"])
                base_score = 500 + (500 * (1 - normalized_prob))
            else:
                # Fallback if scaling values are identical
                base_score = 500
            
            # Calculate category bonuses
            bonuses = {}
            total_bonus = 0
            
            # Perfect rhyme bonus (20% difficulty, max 100 points)
            if candidate_token in rhyme_data["perfect_tokens"]:
                perfect_scaling = self.storage.data[start_word].get("rhy.prf.sc", {"min": 0, "max": 1})
                if perfect_scaling["max"] > perfect_scaling["min"]:
                    perfect_normalized = (candidate_prob - perfect_scaling["min"]) / (perfect_scaling["max"] - perfect_scaling["min"])
                    perfect_bonus = (500 * 0.20) * (1 - perfect_normalized)
                    bonuses["perfect"] = min(100, max(0, perfect_bonus))
                    total_bonus += bonuses["perfect"]
            
            # Rich rhyme bonus (45% difficulty, max 225 points)
            if candidate_token in rhyme_data["rich_tokens"]:
                rich_scaling = self.storage.data[start_word].get("rhy.rch.sc", {"min": 0, "max": 1})
                if rich_scaling["max"] > rich_scaling["min"]:
                    rich_normalized = (candidate_prob - rich_scaling["min"]) / (rich_scaling["max"] - rich_scaling["min"])
                    rich_bonus = (500 * 0.45) * (1 - rich_normalized)
                    bonuses["rich"] = min(225, max(0, rich_bonus))
                    total_bonus += bonuses["rich"]
            
            # Slant rhyme bonus (35% difficulty, max 175 points)
            if candidate_token in rhyme_data["slant_tokens"]:
                slant_scaling = self.storage.data[start_word].get("rhy.sln.sc", {"min": 0, "max": 1})
                if slant_scaling["max"] > slant_scaling["min"]:
                    slant_normalized = (candidate_prob - slant_scaling["min"]) / (slant_scaling["max"] - slant_scaling["min"])
                    slant_bonus = (500 * 0.35) * (1 - slant_normalized)
                    bonuses["slant"] = min(175, max(0, slant_bonus))
                    total_bonus += bonuses["slant"]
            
            total_score = base_score + total_bonus
            
            return {
                "success": True,
                "message": f"Calculated score for '{candidate_word}'",
                "data": {
                    "candidate_word": candidate_word,
                    "start_word": start_word,
                    "candidate_token": candidate_token,
                    "raw_probability": float(candidate_prob),
                    "normalized_probability": float(normalized_prob),
                    "base_score": float(base_score),
                    "bonuses": bonuses,
                    "total_bonus": float(total_bonus),
                    "total_score": float(total_score),
                    "max_possible_score": 1500.0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate score for '{candidate_word}': {e}")
            return {
                "success": False,
                "message": f"Failed to calculate score: {str(e)}",
                "data": None
            }
    
    async def prepare_word_for_gameplay(self, start_word: str) -> Dict:
        """
        Prepare all necessary data for a word to be used in gameplay.
        
        Returns:
            Dict with preparation status
        """
        try:
            logger.info(f"Preparing '{start_word}' for gameplay...")
            
            # Generate rhyme data
            rhyme_result = await self.generate_rhyme_data(start_word)
            if not rhyme_result["success"]:
                return rhyme_result
            
            # Generate probability vector
            vector_result = await self.generate_probability_vector(start_word)
            if not vector_result["success"]:
                return vector_result
            
            return {
                "success": True,
                "message": f"Successfully prepared '{start_word}' for gameplay",
                "data": {
                    "rhyme_data": rhyme_result["data"],
                    "probability_vector": vector_result["data"]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to prepare '{start_word}' for gameplay: {e}")
            return {
                "success": False,
                "message": f"Failed to prepare word: {str(e)}",
                "data": None
            } 