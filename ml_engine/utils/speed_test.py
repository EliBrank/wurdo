#!/usr/bin/env python3
"""
Speed Test: Inference vs Lookup
===============================

Compare the performance of:
1. Direct ML model inference (no caching)
2. JSON storage lookup (with caching)

This test will:
1. Time inference for a new start_word (not in cache)
2. Time lookup for the same start_word (now in cache)
3. Compare the performance difference
"""

import time
import logging
import asyncio
from typing import Dict, Any
import sys
from pathlib import Path

# Add ml_engine directory to path so we can import from services and models
sys.path.append(str(Path(__file__).parent.parent))

from services.enhanced_scoring_service import get_enhanced_scoring_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def time_inference_vs_lookup():
    """Test inference time vs lookup time."""
    
    print("🚀 Starting Speed Test: Inference vs Lookup")
    print("=" * 50)
    
    # Initialize the scoring service
    scoring_service = get_enhanced_scoring_service()
    
    # Test word that's unlikely to be cached
    start_word = "xylophone"
    candidate_word = "telephone"
    
    print(f"📝 Testing with start_word: '{start_word}'")
    print(f"🎯 Candidate word: '{candidate_word}'")
    print()
    
    # Test 1: Direct inference (no caching)
    print("🔄 Test 1: Direct ML Model Inference")
    print("-" * 40)
    
    start_time = time.time()
    result1 = await scoring_service.score_candidate_comprehensive(start_word, candidate_word)
    inference_time = time.time() - start_time
    
    print(f"⏱️  Inference time: {inference_time:.4f} seconds")
    if result1["success"]:
        print(f"📊 Score: {result1['data']['best_score']:.2f}")
        print(f"🎨 Creativity: {result1['data']['creativity_score']:.4f}")
    else:
        print(f"❌ Error: {result1['message']}")
    print()
    
    # Test 2: Lookup (should be cached now)
    print("🔍 Test 2: Cached Lookup")
    print("-" * 40)
    
    start_time = time.time()
    result2 = await scoring_service.score_candidate_comprehensive(start_word, candidate_word)
    lookup_time = time.time() - start_time
    
    print(f"⏱️  Lookup time: {lookup_time:.4f} seconds")
    if result2["success"]:
        print(f"📊 Score: {result2['data']['best_score']:.2f}")
        print(f"🎨 Creativity: {result2['data']['creativity_score']:.4f}")
    else:
        print(f"❌ Error: {result2['message']}")
    print()
    
    # Calculate speedup
    if inference_time > 0 and lookup_time > 0:
        speedup = inference_time / lookup_time
        print("📈 Performance Analysis")
        print("-" * 40)
        print(f"🚀 Speedup: {speedup:.2f}x faster with caching")
        print(f"⏱️  Time saved: {inference_time - lookup_time:.4f} seconds")
        print(f"📊 Inference: {inference_time:.4f}s | Lookup: {lookup_time:.4f}s")
    else:
        print("❌ Could not calculate speedup due to errors")
    
    print()
    print("=" * 50)
    print("✅ Speed test completed!")

if __name__ == "__main__":
    asyncio.run(time_inference_vs_lookup()) 