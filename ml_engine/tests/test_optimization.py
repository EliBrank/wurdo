#!/usr/bin/env python3
"""
Test script to demonstrate probability vector optimization.
"""

import sys
import os
import json
from datetime import datetime
from io import StringIO
import contextlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.advanced_scorer import get_advanced_scorer
import time

def test_optimization():
    """Test the optimization of using one probability vector for multiple candidates."""
    
    # Capture console output
    output_buffer = StringIO()
    
    with contextlib.redirect_stdout(output_buffer):
        print("Testing Probability Vector Optimization\n")
        print("=" * 50)
        
        # Prepare results dictionary
        results = {
            "test_name": "probability_vector_optimization",
            "timestamp": datetime.now().isoformat(),
            "description": "Demonstrates the efficiency gain from using one probability vector for multiple candidates",
            "key_insight": "By storing one probability vector, we can read probabilities from a given start_word to any other word in the token vocabulary"
        }
        
        try:
            # Initialize scorer
            print("1. Initializing scorer...")
            scorer = get_advanced_scorer()
            print("Scorer initialized successfully")
            
            # Test parameters
            prompt = "a word that rhymes with cat"
            candidates = ["bat", "hat", "rat", "dog", "tree", "car", "sat", "mat", "pat"]
            
            print(f"\n2. Testing with prompt: '{prompt}'")
            print(f"   Candidates: {candidates}")
            
            results["test_parameters"] = {
                "prompt": prompt,
                "candidates": candidates,
                "num_candidates": len(candidates)
            }
            
            # Test current method (multiple model calls)
            print("\n3. Current Method (Multiple Model Calls)")
            print("-" * 40)
            
            start_time = time.time()
            current_results = scorer.score_multiple_candidates(prompt, candidates)
            current_time = time.time() - start_time
            
            print(f"Time taken: {current_time:.4f} seconds")
            print(f"Number of model calls: {len(candidates)}")
            
            results["current_method"] = {
                "time_taken": current_time,
                "num_model_calls": len(candidates),
                "scores": current_results["scores"]
            }
            
            # Test optimized method (one model call)
            print("\n4. Optimized Method (One Model Call)")
            print("-" * 40)
            
            start_time = time.time()
            optimized_results = scorer.score_multiple_candidates_optimized(prompt, candidates)
            optimized_time = time.time() - start_time
            
            print(f"Time taken: {optimized_time:.4f} seconds")
            print(f"Number of model calls: 1")
            speedup = current_time / optimized_time
            print(f"Speedup: {speedup:.2f}x faster")
            
            results["optimized_method"] = {
                "time_taken": optimized_time,
                "num_model_calls": 1,
                "speedup_factor": speedup,
                "scores": optimized_results["scores"]
            }
            
            # Compare results
            print("\n5. Results Comparison")
            print("-" * 40)
            
            print("Current Method Results:")
            for i, result in enumerate(current_results["scores"][:5]):
                print(f"  {i+1}. '{result['candidate_word']}': {result['creativity_score']:.6f}")
            
            print("\nOptimized Method Results:")
            for i, result in enumerate(optimized_results["scores"][:5]):
                print(f"  {i+1}. '{result['candidate_word']}': {result['creativity_score']:.6f}")
            
            # Test probability vector storage and lookup
            print("\n6. Probability Vector Storage Test")
            print("-" * 40)
            
            # Get probability vector once
            vector_data = scorer.get_probability_vector(prompt)
            print(f"Probability vector size: {vector_data['vocabulary_size']:,}")
            print(f"Max probability: {vector_data['max_probability']:.8f}")
            
            results["probability_vector"] = {
                "vocabulary_size": vector_data["vocabulary_size"],
                "max_probability": vector_data["max_probability"],
                "prompt_tokens": vector_data["prompt_tokens"]
            }
            
            # Look up candidates from stored vector
            print("\nLooking up candidates from stored vector:")
            lookup_results = []
            for candidate in candidates[:3]:
                lookup_result = scorer.lookup_candidate_from_vector(
                    vector_data["probability_vector"], 
                    candidate, 
                    vector_data["max_probability"]
                )
                print(f"  '{candidate}': creativity = {lookup_result['creativity_score']:.6f}")
                lookup_results.append(lookup_result)
            
            results["vector_lookup_demo"] = {
                "candidates_tested": candidates[:3],
                "lookup_results": lookup_results
            }
            
            # Demonstrate the key insight
            print("\n7. Key Insight Demonstration")
            print("-" * 40)
            print("✅ By storing ONE probability vector, we can look up ANY word's probability!")
            print("✅ The vector contains 50,257 probabilities (one for each token)")
            print("✅ We can score ANY word without running the model again")
            
            results["key_insights"] = [
                "By storing ONE probability vector, we can look up ANY word's probability!",
                "The vector contains 50,257 probabilities (one for each token)",
                "We can score ANY word without running the model again",
                f"Speedup of {speedup:.2f}x for multiple candidates",
                "Perfect for pre-computing and caching probability vectors"
            ]
            
            print("\nOptimization test completed successfully!")
            
            # Save console output to file
            console_output = output_buffer.getvalue()
            output_file = "shared_results/optimization_console_output.txt"
            os.makedirs("shared_results", exist_ok=True)
            
            with open(output_file, 'w') as f:
                f.write(console_output)
            
            print(f"\nConsole output saved to: {output_file}")
            
            # Also save JSON results
            json_file = "shared_results/optimization_test_results.json"
            with open(json_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"JSON results saved to: {json_file}")
            
            return True
            
        except Exception as e:
            print(f"Test failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Save error results
            error_results = {
                "test_name": "probability_vector_optimization",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            output_file = "shared_results/optimization_test_error.json"
            os.makedirs("shared_results", exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(error_results, f, indent=2)
            
            print(f"Error results saved to: {output_file}")
            return False

if __name__ == "__main__":
    success = test_optimization()
    sys.exit(0 if success else 1) 