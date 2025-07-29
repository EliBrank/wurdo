#!/usr/bin/env python3
"""
Test script for log-space scoring with carefully selected test words.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.advanced_scorer import get_advanced_scorer
import json

def test_log_space_scoring():
    """Test log-space scoring with carefully selected words."""
    print("Testing Log-Space DistilGPT-2 scoring...\n")
    
    try:
        # Initialize scorer
        print("1. Initializing advanced scorer...")
        scorer = get_advanced_scorer()
        print("Advanced scorer initialized successfully")
        
        # Test model info
        print("\n2. Getting model information...")
        model_info = scorer.get_model_info()
        print("Model info retrieved:")
        print(f"   - Model: {model_info['model_name']}")
        print(f"   - Device: {model_info['device']}")
        print(f"   - Vocabulary size: {model_info['vocabulary_size']:,}")
        print(f"   - Parameters: {model_info['parameters']:,}")
        
        # Define our carefully selected test words
        start_word = "cat"
        prompt = f"a word that rhymes with {start_word}"
        
        # 9 carefully selected candidates:
        # 3 rhymes of differing semantic proximity
        # 3 non-rhymes but semantically similar
        # 3 non-rhymes and not semantically similar
        candidates = {
            "rhymes": ["bat", "hat", "rat"],  # Rhymes with cat
            "semantic_similar": ["dog", "pet", "animal"],  # Semantically similar but not rhymes
            "unrelated": ["tree", "book", "car"]  # Neither rhymes nor semantically similar
        }
        
        all_candidates = candidates["rhymes"] + candidates["semantic_similar"] + candidates["unrelated"]
        
        print(f"\n3. Testing with 9 carefully selected words:")
        print(f"   - Start word: '{start_word}'")
        print(f"   - Prompt: '{prompt}'")
        print(f"   - Rhymes: {candidates['rhymes']}")
        print(f"   - Semantic similar: {candidates['semantic_similar']}")
        print(f"   - Unrelated: {candidates['unrelated']}")
        
        # Score all candidates
        print("\n4. Scoring all candidates with probability-based method...")
        results = scorer.score_multiple_candidates(prompt, all_candidates)
        
        # Display results by category
        print("\n=== RESULTS BY CATEGORY ===")
        
        for category, words in candidates.items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            print("-" * 50)
            
            for word in words:
                # Find results for this word
                score_result = next(r for r in results["scores"] if r["candidate_word"] == word)
                
                print(f"  '{word}':")
                print(f"    Creativity score: {score_result['creativity_score']:.6f}")
                print(f"    Raw probability: {score_result['raw_probability']:.8f}")
                print(f"    Normalized probability: {score_result['normalized_probability']:.6f}")
                print(f"    Max probability: {score_result['max_probability']:.8f}")
        
        # Show overall ranking
        print("\n=== OVERALL RANKING (Most Creative First) ===")
        print("-" * 50)
        
        for i, score_result in enumerate(results["scores"]):
            print(f"{i+1:2d}. '{score_result['candidate_word']}': {score_result['creativity_score']:.6f}")
        
        # Test with different prompts
        print("\n5. Testing different prompt types...")
        different_prompts = [
            f"a word that rhymes with {start_word}",
            f"a word that is one letter different from {start_word}",
            f"a word that adds one letter to {start_word}"
        ]
        
        for prompt in different_prompts:
            print(f"\nPrompt: '{prompt}'")
            for word in all_candidates[:3]:  # Test first 3 words
                result = scorer.score_candidate_probability_based(prompt, word)
                print(f"  '{word}': creativity = {result['creativity_score']:.6f}, prob = {result['raw_probability']:.8f}")
        
        print("\nProbability-based scoring test completed successfully!")
        
        # Save detailed results to file
        output_file = "probability_scoring_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Detailed results saved to: {output_file}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_log_space_scoring()
    sys.exit(0 if success else 1) 