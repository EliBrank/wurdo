#!/usr/bin/env python3
"""
Optimized Storage Service
=========================

High-performance storage for probability trees with JSON/Redis compatibility.
Prioritizes speed and memory efficiency for fast lookups.
"""

import json
import os
import numpy as np
from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path
from dataclasses import asdict, dataclass
import pickle
import gzip
from dotenv import load_dotenv

from models.probability_tree import WordProbabilityTree, ProbabilityNode, ProbabilityMetadata, ChildNode

logger = logging.getLogger(__name__)

@dataclass
class StorageConfig:
    """Optimized storage configuration."""
    storage_type: str = "json"           # "json", "redis", or "hybrid"
    json_file_path: str = "game_data/probability_trees.json"
    redis_connection: Optional[Any] = None  # For connection sharing (Upstash Redis)
    compression: bool = True              # Use gzip compression for large objects
    cache_size: int = 1000               # In-memory cache size
    
class OptimizedStorageService:
    """
    Optimized storage service for probability trees.
    
    Features:
    - Lazy loading with in-memory cache
    - Gzip compression for large objects
    - Fast JSON/Redis lookups
    - Memory-efficient serialization
    """
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self._memory_cache = {}  # Fast in-memory cache
        self._cache_hits = 0
        self._cache_misses = 0
        
        if config.storage_type == "redis":
            if not config.redis_connection:
                raise ValueError("Redis connection required for redis storage type")
            self.redis = config.redis_connection
            self._load_redis_data()
        elif config.storage_type == "hybrid":
            # For hybrid mode, we need Redis for caching and JSON for fallback
            # Use Isaac's Upstash connection pattern for compatibility
            if config.redis_connection:
                self.redis = config.redis_connection
            else:
                # Try to get Redis connection using Isaac's Upstash pattern
                try:
                    # Load environment variables from .env.local
                    load_dotenv(dotenv_path="../.env.local")
                    
                    # Use Isaac's Upstash pattern
                    kv_url = os.environ.get("KV_REST_API_URL")
                    kv_token = os.environ.get("KV_REST_API_TOKEN")
                    
                    if kv_url and kv_token:
                        # Use upstash_redis for Upstash compatibility
                        from upstash_redis import Redis
                        self.redis = Redis(url=kv_url, token=kv_token)
                        logger.info("✅ Connected to Upstash Redis using Isaac's pattern")
                    else:
                        # Fall back to JSON-only mode if no Upstash Redis available
                        logger.warning("No Upstash Redis connection available, falling back to JSON-only mode")
                        config.storage_type = "json"
                        self.redis = None
                except Exception as e:
                    logger.warning(f"Failed to establish Upstash Redis connection: {e}, falling back to JSON-only mode")
                    config.storage_type = "json"
                    self.redis = None
            
            if self.redis:
                self._load_redis_data()
            self._load_json_data()  # Load JSON as fallback
        elif config.storage_type == "json":
            self.redis = None
            self._load_json_data()
        else:
            raise ValueError("storage_type must be 'json', 'redis', or 'hybrid'")
        
        logger.info(f"✅ OptimizedStorageService initialized with {config.storage_type} storage")
    
    def _load_json_data(self):
        """Load data from JSON file or create new if doesn't exist."""
        try:
            if os.path.exists(self.config.json_file_path):
                with open(self.config.json_file_path, 'r') as f:
                    self.data = json.load(f)
                logger.info(f"📦 Loaded {len(self.data)} probability trees from JSON")
            else:
                # Create directory if it doesn't exist
                Path(self.config.json_file_path).parent.mkdir(parents=True, exist_ok=True)
                self.data = {}
                logger.info("🆕 Created new JSON storage file")
        except Exception as e:
            logger.warning(f"Failed to load JSON data: {e}")
            self.data = {}
    
    def _load_redis_data(self):
        """Initialize Redis connection and load metadata."""
        try:
            # Test Redis connection with a simple operation
            self.redis.get("test_connection")
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _save_json_data(self):
        """Save data to JSON file with error handling."""
        try:
            with open(self.config.json_file_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save JSON data: {e}")
            raise
    
    def _serialize_tree(self, tree: WordProbabilityTree) -> bytes:
        """Efficiently serialize probability tree."""
        try:
            # Convert to dict for serialization
            tree_dict = self._tree_to_dict(tree)
            
            if self.config.compression:
                # Use gzip compression for large objects
                return gzip.compress(pickle.dumps(tree_dict))
            else:
                return pickle.dumps(tree_dict)
        except Exception as e:
            logger.error(f"Failed to serialize tree: {e}")
            raise
    
    def _deserialize_tree(self, data: bytes) -> WordProbabilityTree:
        """Efficiently deserialize probability tree."""
        try:
            if self.config.compression:
                # Decompress gzipped data
                tree_dict = pickle.loads(gzip.decompress(data))
            else:
                tree_dict = pickle.loads(data)
            
            return self._dict_to_tree(tree_dict)
        except Exception as e:
            logger.error(f"Failed to deserialize tree: {e}")
            raise
    
    def _get_from_storage(self, start_word: str) -> Optional[WordProbabilityTree]:
        """
        Unified storage retrieval method that handles Redis, JSON, and hybrid modes.
        For hybrid mode: Redis first, then JSON fallback.
        Returns deserialized tree or None if not found.
        """
        try:
            if self.config.storage_type == "redis":
                # Get from Redis only - now uses efficient base64 storage (no metadata)
                serialized = self.redis.get(f"tree:{start_word}")
                if serialized is None:
                    return None
                
                # Handle both new base64 format and legacy formats
                if isinstance(serialized, bytes):
                    serialized = serialized.decode('utf-8')
                
                if isinstance(serialized, str):
                    # Try to decode as base64 first (new efficient format)
                    try:
                        import base64
                        decoded = base64.b64decode(serialized)
                        tree = self._deserialize_tree(decoded)
                        logger.debug(f"📦 Redis base64 storage hit for '{start_word}' (efficient)")
                        return tree
                    except Exception:
                        # Fallback: try to parse as legacy JSON (very old format)
                        try:
                            tree_data = json.loads(serialized)
                            if 'serialized' in tree_data:
                                serialized_bytes = bytes.fromhex(tree_data['serialized'])
                                tree = self._deserialize_tree(serialized_bytes)
                                logger.debug(f"📦 Redis hex storage hit for '{start_word}' (legacy)")
                                return tree
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.error(f"Failed to parse Redis data for '{start_word}': {e}")
                            return None
                
                return None
                
            elif self.config.storage_type == "hybrid":
                # Try Redis first, then JSON fallback - now uses efficient base64 storage (no metadata)
                serialized = self.redis.get(f"tree:{start_word}")
                if serialized is not None:
                    # Handle both new base64 format and legacy formats
                    if isinstance(serialized, bytes):
                        serialized = serialized.decode('utf-8')
                    
                    if isinstance(serialized, str):
                        # Try to decode as base64 first (new efficient format)
                        try:
                            import base64
                            decoded = base64.b64decode(serialized)
                            tree = self._deserialize_tree(decoded)
                            logger.debug(f"📦 Redis base64 storage hit for '{start_word}' (hybrid mode, efficient)")
                            return tree
                        except Exception:
                            # Fallback: try to parse as legacy JSON (very old format)
                            try:
                                tree_data = json.loads(serialized)
                                if 'serialized' in tree_data:
                                    serialized_bytes = bytes.fromhex(tree_data['serialized'])
                                    tree = self._deserialize_tree(serialized_bytes)
                                    logger.debug(f"📦 Redis hex storage hit for '{start_word}' (hybrid mode, legacy)")
                                    return tree
                            except (json.JSONDecodeError, KeyError) as e:
                                logger.error(f"Failed to parse Redis data for '{start_word}' in hybrid mode: {e}")
                                # Continue to JSON fallback
                
                # Fallback to JSON
                if start_word in self.data:
                    tree_data = self.data[start_word]
                    serialized = bytes.fromhex(tree_data['serialized'])
                    tree = self._deserialize_tree(serialized)
                    logger.debug(f"📦 JSON fallback hit for '{start_word}' (hybrid mode)")
                    return tree
                
                return None
                
            elif self.config.storage_type == "json":
                # Get from JSON only
                if start_word not in self.data:
                    return None
                
                tree_data = self.data[start_word]
                serialized = bytes.fromhex(tree_data['serialized'])
                tree = self._deserialize_tree(serialized)
                logger.debug(f"📦 JSON storage hit for '{start_word}'")
                return tree
                
        except Exception as e:
            logger.error(f"Failed to get tree from storage for '{start_word}': {e}")
            return None
    
    def _cache_tree_result(self, start_word: str, tree: WordProbabilityTree) -> None:
        """
        Unified caching logic for storing trees in memory cache.
        Maintains cache size and updates statistics.
        """
        try:
            # Cache in memory for future fast access
            self._memory_cache[start_word] = tree
            
            # Maintain cache size
            if len(self._memory_cache) > self.config.cache_size:
                # Remove oldest entry (simple LRU)
                oldest_key = next(iter(self._memory_cache))
                del self._memory_cache[oldest_key]
                
        except Exception as e:
            logger.error(f"Failed to cache tree for '{start_word}': {e}")
    
    def _storage_exists(self, start_word: str) -> bool:
        """Check if tree exists in storage."""
        try:
            if self.config.storage_type == "redis":
                # Check Redis - use efficient base64 storage
                result = self.redis.get(f"tree:{start_word}")
                return result is not None
                
            elif self.config.storage_type == "hybrid":
                # Check Redis first, then JSON
                result = self.redis.get(f"tree:{start_word}")
                if result is not None:
                    return True
                return start_word in self.data
                
            elif self.config.storage_type == "json":
                return start_word in self.data
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to check existence for '{start_word}': {e}")
            return False
    
    def _serialize_and_store(self, start_word: str, tree: WordProbabilityTree) -> None:
        """
        Unified serialization and storage method that handles Redis, JSON, and hybrid modes.
        For hybrid mode: stores in both Redis and JSON.
        """
        try:
            # Serialize the tree once
            serialized = self._serialize_tree(tree)
            
            if self.config.storage_type == "redis":
                # Store in Redis with compression - use efficient base64 storage (no metadata overhead)
                import base64
                encoded_data = base64.b64encode(serialized).decode('utf-8')
                self.redis.set(f"tree:{start_word}", encoded_data)
                logger.info(f"💾 Stored tree for '{start_word}' in Redis (base64, {len(serialized)} bytes)")
                
            elif self.config.storage_type == "hybrid":
                # Store in both Redis and JSON for hybrid mode - ALWAYS use efficient base64 storage
                # Upstash Redis supports .set() but not binary data, so encode as base64
                import base64
                encoded_data = base64.b64encode(serialized).decode('utf-8')
                # Store in Redis as base64 (no metadata overhead)
                self.redis.set(f"tree:{start_word}", encoded_data)
                # Store in JSON with hex (maintain backward compatibility)
                self.data[start_word] = {
                    'serialized': serialized.hex(),  # Store as hex string for JSON compatibility
                    'metadata': {
                        'size_bytes': len(serialized),
                        'compressed': self.config.compression,
                        'stored_at': str(np.datetime64('now'))
                    }
                }
                self._save_json_data()
                logger.info(f"💾 Stored tree for '{start_word}' in both Redis and JSON ({len(serialized)} bytes)")
                
            elif self.config.storage_type == "json":
                # Store in JSON (serialized as hex string)
                self.data[start_word] = {
                    'serialized': serialized.hex(),  # Store as hex string
                    'metadata': {
                        'size_bytes': len(serialized),
                        'compressed': self.config.compression,
                        'stored_at': str(np.datetime64('now'))
                    }
                }
                self._save_json_data()
                logger.info(f"💾 Stored tree for '{start_word}' in JSON ({len(serialized)} bytes)")
                
        except Exception as e:
            logger.error(f"Failed to serialize and store tree for '{start_word}': {e}")
            raise
    
    def _tree_to_dict(self, tree: WordProbabilityTree) -> Dict:
        """Convert probability tree to serializable dict."""
        return {
            'frq': tree.frq,
            'ana': self._node_to_dict(tree.ana),
            'olo': {k: self._node_to_dict(v) for k, v in tree.olo.items()},
            'rhy': {k: self._node_to_dict(v) for k, v in tree.rhy.items()}
        }
    
    def _node_to_dict(self, node: ProbabilityNode) -> Dict:
        """Convert probability node to serializable dict."""
        return {
            'val': node.val,
            'prb': {str(k): v if isinstance(v, float) else self._child_to_dict(v) 
                   for k, v in node.prb.items()},
            'dat': {
                'org_max': node.dat.org_max,
                'val_prb_sum': node.dat.val_prb_sum,
                'max_dep': node.dat.max_dep
            }
        }
    
    def _child_to_dict(self, child: ChildNode) -> Dict:
        """Convert child node to serializable dict."""
        return {
            'probability': child.probability,
            'remaining_sequences': child.remaining_sequences,
            'child_prb': self._node_to_dict(child.child_prb)
        }
    
    def _dict_to_tree(self, tree_dict: Dict) -> WordProbabilityTree:
        """Convert dict back to probability tree."""
        return WordProbabilityTree(
            frq=tree_dict['frq'],
            ana=self._dict_to_node(tree_dict['ana']),
            olo={k: self._dict_to_node(v) for k, v in tree_dict['olo'].items()},
            rhy={k: self._dict_to_node(v) for k, v in tree_dict['rhy'].items()}
        )
    
    def _dict_to_node(self, node_dict: Dict) -> ProbabilityNode:
        """Convert dict back to probability node."""
        # Reconstruct sparse array
        prb = {}
        for k_str, v in node_dict['prb'].items():
            k = int(k_str)
            if isinstance(v, float):
                prb[k] = v
            else:
                prb[k] = ChildNode(
                    probability=v['probability'],
                    remaining_sequences=v['remaining_sequences'],
                    child_prb=self._dict_to_node(v['child_prb'])
                )
        
        return ProbabilityNode(
            val=node_dict['val'],
            prb=prb,
            dat=ProbabilityMetadata(
                org_max=node_dict['dat']['org_max'],
                val_prb_sum=node_dict['dat']['val_prb_sum'],
                max_dep=node_dict['dat']['max_dep']
            )
        )
    
    def store_probability_tree(self, start_word: str, tree: WordProbabilityTree) -> None:
        """
        Store probability tree with optimized serialization.
        
        Args:
            start_word: The word to store tree for
            tree: WordProbabilityTree to store
        """
        try:
            # Update in-memory cache
            self._memory_cache[start_word] = tree
            
            # Use the unified serialization and storage method
            self._serialize_and_store(start_word, tree)
            
        except Exception as e:
            logger.error(f"Failed to store tree for '{start_word}': {e}")
            raise
    
    def get_probability_tree(self, start_word: str) -> Optional[WordProbabilityTree]:
        """
        Get probability tree with optimized caching.
        
        Args:
            start_word: The word to get tree for
            
        Returns:
            WordProbabilityTree or None if not found
        """
        try:
            # Check in-memory cache first (fastest)
            if start_word in self._memory_cache:
                self._cache_hits += 1
                logger.debug(f"⚡ Memory cache hit for '{start_word}'")
                return self._memory_cache[start_word]
            
            self._cache_misses += 1
            
            # Use the unified retrieval method
            tree = self._get_from_storage(start_word)
            
            # Cache the result if found
            if tree is not None:
                self._cache_tree_result(start_word, tree)
                return tree
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get tree for '{start_word}': {e}")
            return None
    
    def has_probability_tree(self, start_word: str) -> bool:
        """
        Fast check if probability tree exists.
        
        Args:
            start_word: The word to check
            
        Returns:
            True if tree exists, False otherwise
        """
        # Check memory cache first
        if start_word in self._memory_cache:
            return True
        
        # Use the unified existence check
        return self._storage_exists(start_word)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'memory_cache_size': len(self._memory_cache),
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }
    
    def clear_memory_cache(self):
        """Clear in-memory cache."""
        self._memory_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("🧹 Memory cache cleared")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        if self.config.storage_type == "redis":
            # Get Redis stats - use efficient base64 storage
            try:
                # Get basic Redis info
                info = self.redis.info()
                return {
                    'storage_type': 'redis',
                    'connected_clients': info.get('connected_clients', 'unknown'),
                    'used_memory_human': info.get('used_memory_human', 'unknown'),
                    'total_commands_processed': info.get('total_commands_processed', 'unknown')
                }
            except Exception as e:
                logger.warning(f"Failed to get Redis stats: {e}")
                return {
                    'storage_type': 'redis',
                    'error': str(e)
                }
        elif self.config.storage_type == "json":
            # Get JSON file stats
            file_size = os.path.getsize(self.config.json_file_path) if os.path.exists(self.config.json_file_path) else 0
            return {
                'storage_type': 'json',
                'file_size_bytes': file_size,
                'file_size_mb': file_size / (1024 * 1024),
                'total_trees': len(self.data)
            }
        elif self.config.storage_type == "hybrid":
            # Get hybrid stats
            redis_stats = {}
            try:
                info = self.redis.info()
                redis_stats = {
                    'redis_connected_clients': info.get('connected_clients', 'unknown'),
                    'redis_used_memory_human': info.get('used_memory_human', 'unknown')
                }
            except Exception as e:
                redis_stats = {'redis_error': str(e)}
            
            file_size = os.path.getsize(self.config.json_file_path) if os.path.exists(self.config.json_file_path) else 0
            return {
                'storage_type': 'hybrid',
                'redis': redis_stats,
                'json_file_size_bytes': file_size,
                'json_file_size_mb': file_size / (1024 * 1024),
                'total_trees': len(self.data)
            }
        else:
            return {'storage_type': 'unknown'}
    
    async def populate_from_file(self, file_path: str) -> Dict[str, int]:
        """
        Populate storage with pre-compressed probability trees from JSON file.
        Uses efficient base64 storage for Redis operations.
        
        Args:
            file_path: Path to probability_trees.json file (contains pre-compressed data)
            
        Returns:
            Dict with counts of new trees added and total processed
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Probability trees file not found: {file_path}")
                return {"new_trees_added": 0, "total_processed": 0}
            
            # Load the JSON file (this decompresses, but we'll preserve compression efficiently)
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            new_trees = 0
            total_trees = len(data)
            
            # Process trees based on storage type
            if self.config.storage_type in ["redis", "hybrid"]:
                # Use concurrent async operations for efficiency
                import asyncio
                
                # Collect all trees that need to be added to Redis
                trees_to_add = []
                for word, tree_data in data.items():
                    # Check if tree already exists in Redis
                    try:
                        result = self.redis.get(f"tree:{word}")
                        tree_exists = result is not None
                        
                        if not tree_exists:
                            # Store the tree efficiently with base64 encoding (no metadata overhead)
                            if isinstance(tree_data, dict) and 'serialized' in tree_data:
                                # Extract the compressed binary data
                                serialized_bytes = bytes.fromhex(tree_data['serialized'])
                                # Store as base64 string directly (no metadata overhead)
                                import base64
                                encoded_data = base64.b64encode(serialized_bytes).decode('utf-8')
                                trees_to_add.append((word, encoded_data))
                                logger.debug(f"Queued efficient base64 tree for '{word}' (no metadata)")
                            else:
                                logger.warning(f"Tree data for '{word}' is not in expected format")
                                continue
                    except Exception as e:
                        logger.warning(f"Error checking tree existence for '{word}': {e}")
                        continue
                
                # Execute Redis operations concurrently for efficiency
                if trees_to_add:
                    # Create async tasks for all Redis operations
                    async def store_tree(word: str, encoded_data: str):
                        try:
                            # Store base64 data directly (no metadata overhead)
                            await asyncio.to_thread(self.redis.set, f"tree:{word}", encoded_data)
                            logger.debug(f"Stored tree '{word}' with efficient base64 storage (no metadata)")
                            return True
                        except Exception as e:
                            logger.error(f"Failed to store tree '{word}': {e}")
                            return False
                    
                    # Execute all operations concurrently
                    tasks = [store_tree(word, encoded_data) for word, encoded_data in trees_to_add]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Count successful operations
                    new_trees = sum(1 for result in results if result is True)
                    logger.info(f"Successfully stored {new_trees} new trees in Redis using efficient base64 storage (no metadata)")
                else:
                    logger.info("All trees already exist in Redis")
            
            return {"new_trees_added": new_trees, "total_processed": total_trees}
            
        except Exception as e:
            logger.error(f"Failed to populate from file: {e}")
            return {"new_trees_added": 0, "total_processed": 0}

def get_optimized_storage_service(config: StorageConfig) -> OptimizedStorageService:
    """Factory function to create OptimizedStorageService instance."""
    return OptimizedStorageService(config) 