#!/usr/bin/env python3
"""
Test script to analyze how semantic similarity affects scoring.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.advanced_scorer import get_advanced_scorer
import json

def test_semantic_analysis():
    """Test how semantic similarity affects scoring."""
    print("Testing Semantic Similarity Effects on Scoring...\n")
    
    try:
        # Initialize scorer
        print("1. Initializing advanced scorer...")
        scorer = get_advanced_scorer()
        print("Advanced scorer initialized successfully")
        
        # Test with different semantic categories
        start_word = "cat"
        base_prompt = f"a word that rhymes with {start_word}"
        
        # Define semantic categories
        test_categories = {
            "exact_rhymes": ["bat", "hat", "rat", "sat", "fat"],  # Perfect rhymes
            "near_rhymes": ["mat", "pat", "that", "flat"],  # Near rhymes
            "semantic_related": ["dog", "pet", "animal", "feline", "kitten"],  # Semantically related
            "semantic_unrelated": ["tree", "book", "car", "house", "computer"],  # Semantically unrelated
            "phonetic_similar": ["cap", "cab", "can", "car"],  # Phonetically similar but not rhymes
            "length_similar": ["dog", "pig", "fox", "cow"]  # Similar length, different meaning
        }
        
        print(f"\n2. Testing semantic effects with start word: '{start_word}'")
        print(f"   Prompt: '{base_prompt}'")
        
        all_results = {}
        
        for category, words in test_categories.items():
            print(f"\n=== {category.upper().replace('_', ' ')} ===")
            print("-" * 50)
            
            category_results = []
            
            for word in words:
                # Get scoring results using probability-based method
                result = scorer.score_candidate_probability_based(base_prompt, word)
                
                result_data = {
                    "word": word,
                    "creativity_score": result["creativity_score"],
                    "raw_probability": result["raw_probability"],
                    "normalized_probability": result["normalized_probability"]
                }
                
                category_results.append(result_data)
                
                print(f"  '{word}':")
                print(f"    Creativity score: {result['creativity_score']:.6f}")
                print(f"    Raw probability: {result['raw_probability']:.8f}")
                print(f"    Normalized probability: {result['normalized_probability']:.6f}")
            
            all_results[category] = category_results
        
        # Analyze patterns
        print("\n=== SEMANTIC ANALYSIS ===")
        print("-" * 50)
        
        # Calculate averages by category
        category_averages = {}
        for category, results in all_results.items():
            avg_creativity = sum(r["creativity_score"] for r in results) / len(results)
            avg_probability = sum(r["raw_probability"] for r in results) / len(results)
            
            category_averages[category] = {
                "avg_creativity": avg_creativity,
                "avg_probability": avg_probability,
                "count": len(results)
            }
            
            print(f"\n{category.replace('_', ' ').title()}:")
            print(f"  Avg Creativity score: {avg_creativity:.6f}")
            print(f"  Avg Raw probability: {avg_probability:.8f}")
        
        # Test with different prompts to see semantic effects
        print("\n=== PROMPT VARIATION TEST ===")
        print("-" * 50)
        
        different_prompts = [
            f"a word that rhymes with {start_word}",
            f"a word that is semantically similar to {start_word}",
            f"a word that is an animal like {start_word}",
            f"a word that is a pet like {start_word}"
        ]
        
        test_words = ["bat", "dog", "tree", "hat"]
        
        for prompt in different_prompts:
            print(f"\nPrompt: '{prompt}'")
            for word in test_words:
                result = scorer.score_candidate_probability_based(prompt, word)
                print(f"  '{word}': creativity = {result['creativity_score']:.6f}, prob = {result['raw_probability']:.8f}")
        
        # Test semantic vs phonetic effects
        print("\n=== SEMANTIC VS PHONETIC EFFECTS ===")
        print("-" * 50)
        
        semantic_test = {
            "phonetic_rhyme": ["bat", "hat", "rat"],  # Phonetic rhymes
            "semantic_related": ["dog", "pet", "animal"],  # Semantically related
            "both": ["cat", "kitten", "feline"],  # Both phonetic and semantic
            "neither": ["tree", "book", "car"]  # Neither
        }
        
        for category, words in semantic_test.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for word in words:
                result = scorer.score_candidate_probability_based(base_prompt, word)
                print(f"  '{word}': creativity = {result['creativity_score']:.6f}, prob = {result['raw_probability']:.8f}")
        
        print("\nSemantic analysis completed successfully!")
        
        # Save detailed results
        output_file = "semantic_analysis_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                "all_results": all_results,
                "category_averages": category_averages
            }, f, indent=2, default=str)
        print(f"Detailed results saved to: {output_file}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_semantic_analysis()
    sys.exit(0 if success else 1) 