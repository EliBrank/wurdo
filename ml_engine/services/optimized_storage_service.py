#!/usr/bin/env python3
"""
Optimized Storage Service
=========================

High-performance storage for probability trees with JSON/Redis compatibility.
Prioritizes speed and memory efficiency for fast lookups.
"""

import json
import os
import redis
import numpy as np
from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path
from dataclasses import asdict, dataclass
import pickle
import gzip

from models.probability_tree import WordProbabilityTree, ProbabilityNode, ProbabilityMetadata, ChildNode

logger = logging.getLogger(__name__)

@dataclass
class StorageConfig:
    """Optimized storage configuration."""
    storage_type: str = "json"           # "json" or "redis"
    json_file_path: str = "probability_trees.json"
    redis_url: Optional[str] = None
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
            if not config.redis_url:
                raise ValueError("Redis URL required for redis storage type")
            self.redis = redis.from_url(config.redis_url)
            self._load_redis_data()
        elif config.storage_type == "json":
            self.redis = None
            self._load_json_data()
        else:
            raise ValueError("storage_type must be 'json' or 'redis'")
        
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
            # Test Redis connection
            self.redis.ping()
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
            
            if self.config.storage_type == "redis":
                # Store in Redis with compression
                serialized = self._serialize_tree(tree)
                self.redis.set(f"tree:{start_word}", serialized)
                logger.info(f"💾 Stored tree for '{start_word}' in Redis ({len(serialized)} bytes)")
                
            elif self.config.storage_type == "json":
                # Store in JSON (serialized as base64 for complex objects)
                serialized = self._serialize_tree(tree)
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
            
            if self.config.storage_type == "redis":
                # Get from Redis
                serialized = self.redis.get(f"tree:{start_word}")
                if serialized is None:
                    return None
                
                tree = self._deserialize_tree(serialized)
                # Cache in memory for future fast access
                self._memory_cache[start_word] = tree
                
                # Maintain cache size
                if len(self._memory_cache) > self.config.cache_size:
                    # Remove oldest entry (simple LRU)
                    oldest_key = next(iter(self._memory_cache))
                    del self._memory_cache[oldest_key]
                
                logger.debug(f"📦 Redis cache hit for '{start_word}'")
                return tree
                
            elif self.config.storage_type == "json":
                # Get from JSON
                if start_word not in self.data:
                    return None
                
                tree_data = self.data[start_word]
                serialized = bytes.fromhex(tree_data['serialized'])
                tree = self._deserialize_tree(serialized)
                
                # Cache in memory for future fast access
                self._memory_cache[start_word] = tree
                
                # Maintain cache size
                if len(self._memory_cache) > self.config.cache_size:
                    oldest_key = next(iter(self._memory_cache))
                    del self._memory_cache[oldest_key]
                
                logger.debug(f"📦 JSON cache hit for '{start_word}'")
                return tree
            
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
        
        if self.config.storage_type == "redis":
            return self.redis.exists(f"tree:{start_word}") > 0
        elif self.config.storage_type == "json":
            return start_word in self.data
    
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
            # Get Redis stats
            info = self.redis.info()
            return {
                'storage_type': 'redis',
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', 'unknown'),
                'total_commands_processed': info.get('total_commands_processed', 0)
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

def get_optimized_storage_service(config: StorageConfig) -> OptimizedStorageService:
    """Factory function to create OptimizedStorageService instance."""
    return OptimizedStorageService(config) 