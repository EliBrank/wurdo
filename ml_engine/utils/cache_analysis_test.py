#!/usr/bin/env python3
"""
Cache Analysis Test
==================

Analyze cache usage patterns during tree building to determine if cache_size=1000
is sufficient for all words and whether it generalizes well.
"""

import asyncio
import logging
import time
from typing import Dict, List, Tuple
from pathlib import Path
import sys

# Add ml_engine root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.enhanced_scoring_service import get_enhanced_scoring_service
from services.efficient_word_service import get_efficient_word_service
from services.optimized_storage_service import get_optimized_storage_service, StorageConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CacheAnalysisTest:
    """Analyze cache usage patterns during tree building."""
    
    def __init__(self):
        """Initialize the test."""
        self.scoring_service = get_enhanced_scoring_service()
        self.word_service = get_efficient_word_service()
        self.cache_stats = {}
        
    def get_cache_stats(self) -> Dict:
        """Get current cache statistics."""
        try:
            # Access the storage service's cache stats
            storage = self.scoring_service.storage
            return storage.get_cache_stats()
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics."""
        try:
            storage = self.scoring_service.storage
            return storage.get_storage_stats()
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
    
    async def analyze_tree_building_cache(self, start_word: str) -> Dict:
        """Analyze cache usage during tree building for a specific word."""
        logger.info(f"Analyzing cache usage for tree building: '{start_word}'")
        
        # Get initial cache stats
        initial_cache_stats = self.get_cache_stats()
        initial_storage_stats = self.get_storage_stats()
        
        logger.info(f"Initial cache stats: {initial_cache_stats}")
        logger.info(f"Initial storage stats: {initial_storage_stats}")
        
        # Build the tree (this will use cache)
        start_time = time.time()
        
        # Force tree building by scoring a candidate
        transformations = self.word_service.get_comprehensive_transformations(start_word)
        total_transformations = sum(len(getattr(transformations, attr)) for attr in [
            'perfect_rhymes', 'rich_rhymes', 'slant_rhymes', 
            'anagrams', 'added_letters', 'removed_letters', 'changed_letters'
        ])
        
        # Test a few candidates to trigger tree building
        test_candidates = []
        for attr in ['perfect_rhymes', 'anagrams', 'added_letters', 'changed_letters']:
            words = getattr(transformations, attr)
            if words:
                test_candidates.extend(words[:3])  # Test first 3 from each category
        
        successful_scores = 0
        for candidate in test_candidates[:10]:  # Limit to 10 tests
            try:
                result = await self.scoring_service.score_candidate_comprehensive(start_word, candidate)
                if result["success"]:
                    successful_scores += 1
            except Exception as e:
                logger.error(f"Error scoring {candidate}: {e}")
        
        build_time = time.time() - start_time
        
        # Get final cache stats
        final_cache_stats = self.get_cache_stats()
        final_storage_stats = self.get_storage_stats()
        
        # Calculate cache usage
        cache_usage = {
            'start_word': start_word,
            'total_transformations': total_transformations,
            'test_candidates': len(test_candidates),
            'successful_scores': successful_scores,
            'build_time': build_time,
            'initial_cache_stats': initial_cache_stats,
            'final_cache_stats': final_cache_stats,
            'initial_storage_stats': initial_storage_stats,
            'final_storage_stats': final_storage_stats
        }
        
        # Calculate cache hit/miss ratios
        if 'cache_hits' in final_cache_stats and 'cache_misses' in final_cache_stats:
            total_requests = final_cache_stats['cache_hits'] + final_cache_stats['cache_misses']
            if total_requests > 0:
                cache_hit_rate = final_cache_stats['cache_hits'] / total_requests
                cache_usage['cache_hit_rate'] = cache_hit_rate
                cache_usage['total_cache_requests'] = total_requests
        
        return cache_usage
    
    async def run_cache_analysis(self, test_words: List[str]) -> Dict[str, Dict]:
        """Run cache analysis on multiple words."""
        logger.info(f"Starting cache analysis with {len(test_words)} words")
        
        all_results = {}
        
        for word in test_words:
            logger.info(f"Analyzing cache for word: {word}")
            results = await self.analyze_tree_building_cache(word)
            all_results[word] = results
            
            # Print summary for this word
            print(f"\n📊 Cache Analysis for '{word}':")
            print(f"  Total transformations: {results['total_transformations']}")
            print(f"  Successful scores: {results['successful_scores']}")
            print(f"  Build time: {results['build_time']:.3f}s")
            
            if 'cache_hit_rate' in results:
                print(f"  Cache hit rate: {results['cache_hit_rate']:.2%}")
                print(f"  Total cache requests: {results['total_cache_requests']}")
        
        return all_results
    
    def analyze_cache_capacity(self, results: Dict[str, Dict]) -> Dict:
        """Analyze if cache_size=1000 is sufficient."""
        print("\n" + "="*80)
        print("CACHE CAPACITY ANALYSIS")
        print("="*80)
        
        total_trees = 0
        max_cache_usage = 0
        cache_hit_rates = []
        
        for word, stats in results.items():
            total_trees += 1
            
            # Analyze cache usage patterns
            final_cache = stats['final_cache_stats']
            if 'cache_hits' in final_cache and 'cache_misses' in final_cache:
                total_requests = final_cache['cache_hits'] + final_cache['cache_misses']
                if total_requests > 0:
                    hit_rate = final_cache['cache_hits'] / total_requests
                    cache_hit_rates.append(hit_rate)
                    
                    # Estimate cache usage (this is approximate)
                    cache_usage_estimate = total_requests
                    max_cache_usage = max(max_cache_usage, cache_usage_estimate)
        
        # Analyze storage growth
        storage_growth = []
        for word, stats in results.items():
            initial_storage = stats['initial_storage_stats']
            final_storage = stats['final_storage_stats']
            
            if 'total_trees' in initial_storage and 'total_trees' in final_storage:
                growth = final_storage['total_trees'] - initial_storage['total_trees']
                storage_growth.append(growth)
        
        # Calculate statistics
        avg_cache_hit_rate = sum(cache_hit_rates) / len(cache_hit_rates) if cache_hit_rates else 0
        avg_storage_growth = sum(storage_growth) / len(storage_growth) if storage_growth else 0
        
        analysis = {
            'total_trees_analyzed': total_trees,
            'max_cache_usage_estimate': max_cache_usage,
            'avg_cache_hit_rate': avg_cache_hit_rate,
            'avg_storage_growth_per_tree': avg_storage_growth,
            'cache_size_limit': 1000,  # Current setting
            'cache_utilization_percentage': (max_cache_usage / 1000) * 100 if max_cache_usage > 0 else 0
        }
        
        print(f"Total trees analyzed: {total_trees}")
        print(f"Maximum cache usage estimate: {max_cache_usage}")
        print(f"Average cache hit rate: {avg_cache_hit_rate:.2%}")
        print(f"Average storage growth per tree: {avg_storage_growth:.1f}")
        print(f"Cache utilization percentage: {analysis['cache_utilization_percentage']:.1f}%")
        
        # Recommendations
        print(f"\n" + "="*80)
        print("CACHE SIZE RECOMMENDATIONS")
        print("="*80)
        
        if analysis['cache_utilization_percentage'] > 80:
            print(f"⚠️  HIGH CACHE UTILIZATION DETECTED!")
            print(f"   Current utilization: {analysis['cache_utilization_percentage']:.1f}%")
            print(f"   Recommendation: Increase cache_size to 2000 or higher")
        elif analysis['cache_utilization_percentage'] > 50:
            print(f"⚠️  MODERATE CACHE UTILIZATION")
            print(f"   Current utilization: {analysis['cache_utilization_percentage']:.1f}%")
            print(f"   Recommendation: Consider increasing cache_size to 1500")
        else:
            print(f"✅ CACHE UTILIZATION IS ACCEPTABLE")
            print(f"   Current utilization: {analysis['cache_utilization_percentage']:.1f}%")
            print(f"   Current cache_size=1000 is sufficient")
        
        if avg_cache_hit_rate < 0.5:
            print(f"⚠️  LOW CACHE HIT RATE!")
            print(f"   Average hit rate: {avg_cache_hit_rate:.2%}")
            print(f"   Recommendation: Increase cache_size to improve hit rate")
        else:
            print(f"✅ CACHE HIT RATE IS GOOD")
            print(f"   Average hit rate: {avg_cache_hit_rate:.2%}")
        
        return analysis

async def main():
    """Run the cache analysis test."""
    test = CacheAnalysisTest()
    
    # Test words with varying complexity
    test_words = [
        "cat",      # Simple word
        "dog",      # Simple word  
        "play",     # Medium complexity
        "xylophone", # Complex word
        "computer", # Complex word
        "algorithm" # Very complex word
    ]
    
    logger.info("Starting cache analysis...")
    results = await test.run_cache_analysis(test_words)
    
    # Analyze cache capacity
    analysis = test.analyze_cache_capacity(results)
    
    print(f"\nTest completed!")
    return analysis

if __name__ == "__main__":
    asyncio.run(main()) 