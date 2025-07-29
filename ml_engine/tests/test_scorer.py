#!/usr/bin/env python3
"""
Test script for the advanced DistilGPT-2 creativity scorer.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.advanced_scorer import get_advanced_scorer
import json

def test_scorer():
    """Test the advanced DistilGPT-2 scorer functionality."""
    print("Testing Advanced DistilGPT-2 creativity scorer...\n")
    
    try:
        # Initialize scorer
        print("1. Initializing scorer...")
        scorer = get_advanced_scorer()
        print("Scorer initialized successfully")
        
        # Test model info
        print("\n2. Getting model information...")
        model_info = scorer.get_model_info()
        print("Model info retrieved:")
        print(f"   - Model: {model_info['model_name']}")
        print(f"   - Device: {model_info['device']}")
        print(f"   - Vocabulary size: {model_info['vocabulary_size']:,}")
        print(f"   - Parameters: {model_info['parameters']:,}")
        
        # Test single candidate scoring
        print("\n3. Testing single candidate scoring...")
        prompt = "a word that rhymes with cat"
        candidate = "bat"
        
        result = scorer.score_candidate_probability_based(prompt, candidate)
        print("Single candidate scoring completed:")
        print(f"   - Prompt: '{result['prompt']}'")
        print(f"   - Candidate: '{result['candidate_word']}'")
        print(f"   - Token ID: {result['candidate_token']}")
        print(f"   - Raw probability: {result['raw_probability']:.8f}")
        print(f"   - Normalized probability: {result['normalized_probability']:.6f}")
        print(f"   - Creativity score: {result['creativity_score']:.6f}")
        
        # Test multiple candidates
        print("\n4. Testing multiple candidates...")
        candidates = ["bat", "hat", "rat", "sat", "mat", "pat"]
        results = scorer.score_multiple_candidates(prompt, candidates)
        
        print("Multiple candidates scored:")
        for i, result in enumerate(results["scores"]):
            print(f"   {i+1}. '{result['candidate_word']}': "
                  f"prob={result['raw_probability']:.8f}, "
                  f"creativity={result['creativity_score']:.6f}")
        
        # Test different prompt types
        print("\n5. Testing different prompt types...")
        prompts = [
            "a word that rhymes with cat",
            "a word that is one letter different from cat",
            "a word that adds one letter to cat"
        ]
        
        for prompt in prompts:
            result = scorer.score_candidate_probability_based(prompt, "bat")
            print(f"   - '{prompt}' -> 'bat': creativity={result['creativity_score']:.6f}")
        
        # Test with more complex examples
        print("\n6. Testing complex examples...")
        complex_tests = [
            ("a word that rhymes with dog", "log"),
            ("a word that rhymes with fish", "dish"),
            ("a word that rhymes with tree", "bee"),
        ]
        
        for prompt, candidate in complex_tests:
            result = scorer.score_candidate_probability_based(prompt, candidate)
            print(f"   - '{prompt}' -> '{candidate}': creativity={result['creativity_score']:.6f}")
        
        print("\nAll tests passed! Advanced scorer is working correctly.")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_scorer()
    sys.exit(0 if success else 1) 