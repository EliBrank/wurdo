import json
import os
import redis
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, storage_type: str = "json", redis_url: str = None, json_file_path: str = "game_data.json"):
        """
        Initialize storage service with toggle between JSON and Redis.
        
        Args:
            storage_type: "json" or "redis"
            redis_url: Redis connection URL (required for redis storage)
            json_file_path: Path to JSON file (for json storage)
        """
        self.storage_type = storage_type
        self.json_file_path = json_file_path
        
        if storage_type == "redis":
            if not redis_url:
                raise ValueError("Redis URL required for redis storage type")
            self.redis = redis.from_url(redis_url)
            self.data = None
        elif storage_type == "json":
            self.redis = None
            self.data = self._load_json_data()
        else:
            raise ValueError("storage_type must be 'json' or 'redis'")
    
    def _load_json_data(self) -> Dict:
        """Load data from JSON file or create new if doesn't exist."""
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r') as f:
                    return json.load(f)
            else:
                # Create directory if it doesn't exist
                Path(self.json_file_path).parent.mkdir(parents=True, exist_ok=True)
                return {}
        except Exception as e:
            logger.warning(f"Failed to load JSON data: {e}")
            return {}
    
    def _save_json_data(self):
        """Save data to JSON file."""
        try:
            with open(self.json_file_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save JSON data: {e}")
            raise
    
    def _get_redis_key(self, start_word: str, key_type: str) -> str:
        """Generate Redis key for a word and key type."""
        return f"{start_word}.rhy.{key_type}"
    
    def store_rhyme_data(self, start_word: str, tokenized_data: Dict) -> None:
        """Store tokenized rhyme data."""
        try:
            if self.storage_type == "redis":
                pipeline = self.redis.pipeline()
                pipeline.hset(self._get_redis_key(start_word, "prf.val"), 
                             json.dumps(tokenized_data["perfect_tokens"]))
                pipeline.hset(self._get_redis_key(start_word, "rch.val"), 
                             json.dumps(tokenized_data["rich_tokens"]))
                pipeline.hset(self._get_redis_key(start_word, "sln.val"), 
                             json.dumps(tokenized_data["slant_tokens"]))
                pipeline.hset(self._get_redis_key(start_word, "val"), 
                             json.dumps(tokenized_data["all_tokens"]))
                pipeline.execute()
                
            elif self.storage_type == "json":
                if start_word not in self.data:
                    self.data[start_word] = {}
                
                self.data[start_word].update({
                    "rhy.prf.val": tokenized_data["perfect_tokens"],
                    "rhy.rch.val": tokenized_data["rich_tokens"],
                    "rhy.sln.val": tokenized_data["slant_tokens"],
                    "rhy.val": tokenized_data["all_tokens"]
                })
                self._save_json_data()
            
            logger.info(f"Stored rhyme data for '{start_word}' using {self.storage_type}")
            
        except Exception as e:
            logger.error(f"Failed to store rhyme data for '{start_word}': {e}")
            raise
    
    def store_probability_vector(self, start_word: str, probability_vector) -> None:
        """Store probability vector."""
        try:
            # Convert PyTorch tensor to numpy array if needed
            if hasattr(probability_vector, 'cpu'):
                # It's a PyTorch tensor
                probability_vector = probability_vector.cpu().numpy()
            elif not hasattr(probability_vector, 'astype'):
                # It's not a numpy array, try to convert
                probability_vector = np.array(probability_vector)
            
            if self.storage_type == "redis":
                # Convert to float32 for efficiency
                vector_bytes = probability_vector.astype(np.float32).tobytes()
                self.redis.hset(self._get_redis_key(start_word, "prb"), vector_bytes)
                
            elif self.storage_type == "json":
                if start_word not in self.data:
                    self.data[start_word] = {}
                
                # Convert to list for JSON storage
                self.data[start_word]["rhy.prb"] = probability_vector.astype(np.float32).tolist()
                self._save_json_data()
            
            logger.info(f"Stored probability vector for '{start_word}' using {self.storage_type}")
            
        except Exception as e:
            logger.error(f"Failed to store probability vector for '{start_word}': {e}")
            raise
    
    def get_rhyme_data(self, start_word: str) -> Optional[Dict]:
        """Get stored rhyme data for a word."""
        try:
            if self.storage_type == "redis":
                keys = [
                    self._get_redis_key(start_word, "val"),
                    self._get_redis_key(start_word, "prf.val"),
                    self._get_redis_key(start_word, "rch.val"),
                    self._get_redis_key(start_word, "sln.val")
                ]
                results = self.redis.hmget(*keys)
                
                if results[0] is None:
                    return None
                
                return {
                    "all_tokens": json.loads(results[0]) if results[0] else [],
                    "perfect_tokens": json.loads(results[1]) if results[1] else [],
                    "rich_tokens": json.loads(results[2]) if results[2] else [],
                    "slant_tokens": json.loads(results[3]) if results[3] else []
                }
                
            elif self.storage_type == "json":
                if start_word not in self.data:
                    return None
                
                word_data = self.data[start_word]
                return {
                    "all_tokens": word_data.get("rhy.val", []),
                    "perfect_tokens": word_data.get("rhy.prf.val", []),
                    "rich_tokens": word_data.get("rhy.rch.val", []),
                    "slant_tokens": word_data.get("rhy.sln.val", [])
                }
                
        except Exception as e:
            logger.error(f"Failed to get rhyme data for '{start_word}': {e}")
            return None
    
    def get_probability_vector(self, start_word: str) -> Optional[np.ndarray]:
        """Get stored probability vector for a word."""
        try:
            if self.storage_type == "redis":
                vector_bytes = self.redis.hget(self._get_redis_key(start_word, "prb"))
                if vector_bytes is None:
                    return None
                return np.frombuffer(vector_bytes, dtype=np.float32)
                
            elif self.storage_type == "json":
                if start_word not in self.data:
                    return None
                
                vector_list = self.data[start_word].get("rhy.prb")
                if vector_list is None:
                    return None
                
                return np.array(vector_list, dtype=np.float32)
                
        except Exception as e:
            logger.error(f"Failed to get probability vector for '{start_word}': {e}")
            return None
    
    def generate_scaling_values(self, start_word: str, probability_vector: np.ndarray) -> Dict:
        """Generate scaling values for rhyme categories."""
        try:
            rhyme_data = self.get_rhyme_data(start_word)
            if not rhyme_data:
                raise ValueError(f"No rhyme data found for '{start_word}'")
            
            scaling_values = {}
            
            for category, tokens in [
                ("overall", rhyme_data["all_tokens"]),
                ("perfect", rhyme_data["perfect_tokens"]),
                ("rich", rhyme_data["rich_tokens"]),
                ("slant", rhyme_data["slant_tokens"])
            ]:
                probs = [probability_vector[token] for token in tokens 
                        if token < len(probability_vector)]
                
                if probs:
                    scaling_values[category] = {
                        "min": float(np.min(probs)),
                        "max": float(np.max(probs))
                    }
                else:
                    scaling_values[category] = {"min": 0.0, "max": 0.0}
            
            # Store scaling values
            if self.storage_type == "redis":
                pipeline = self.redis.pipeline()
                pipeline.hset(self._get_redis_key(start_word, "sc"), 
                             json.dumps(scaling_values["overall"]))
                pipeline.hset(self._get_redis_key(start_word, "prf.sc"), 
                             json.dumps(scaling_values["perfect"]))
                pipeline.hset(self._get_redis_key(start_word, "rch.sc"), 
                             json.dumps(scaling_values["rich"]))
                pipeline.hset(self._get_redis_key(start_word, "sln.sc"), 
                             json.dumps(scaling_values["slant"]))
                pipeline.execute()
                
            elif self.storage_type == "json":
                if start_word not in self.data:
                    self.data[start_word] = {}
                
                self.data[start_word].update({
                    "rhy.sc": scaling_values["overall"],
                    "rhy.prf.sc": scaling_values["perfect"],
                    "rhy.rch.sc": scaling_values["rich"],
                    "rhy.sln.sc": scaling_values["slant"]
                })
                self._save_json_data()
            
            return scaling_values
            
        except Exception as e:
            logger.error(f"Failed to generate scaling values for '{start_word}': {e}")
            raise
    
    def data_exists(self, start_word: str) -> bool:
        """Check if data exists for a word."""
        try:
            if self.storage_type == "redis":
                return self.redis.hexists(self._get_redis_key(start_word, "val"), "")
            elif self.storage_type == "json":
                return start_word in self.data and "rhy.val" in self.data[start_word]
        except Exception as e:
            logger.error(f"Failed to check data existence for '{start_word}': {e}")
            return False 