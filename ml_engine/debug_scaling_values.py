#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.game_workflow import GameWorkflow
import asyncio
import matplotlib.pyplot as plt
import numpy as np

async def debug_scaling_values():
    """Debug scaling values to understand scoring issues."""
    
    # Initialize workflow
    workflow = GameWorkflow(storage_type="json")
    
    # Test word
    start_word = "cat"
    
    print(f"🔍 Debugging scaling values for '{start_word}'")
    print("=" * 50)
    
    # Prepare word data
    print("1. Preparing word data...")
    prepare_result = await workflow.prepare_word_for_gameplay(start_word)
    
    if not prepare_result["success"]:
        print(f"❌ Failed to prepare word: {prepare_result['message']}")
        return
    
    print("✅ Word prepared successfully")
    
    # Get stored data
    rhyme_data = workflow.storage.get_rhyme_data(start_word)
    probability_vector = workflow.storage.get_probability_vector(start_word)
    
    print(f"\n2. Probability vector info:")
    print(f"   Size: {len(probability_vector)}")
    print(f"   Max probability: {probability_vector.max():.6f}")
    print(f"   Min probability: {probability_vector.min():.6f}")
    
    print(f"\n3. Rhyme data info:")
    print(f"   Perfect rhymes: {len(rhyme_data['perfect_tokens'])}")
    print(f"   Rich rhymes: {len(rhyme_data['rich_tokens'])}")
    print(f"   Slant rhymes: {len(rhyme_data['slant_tokens'])}")
    print(f"   Total rhymes: {len(rhyme_data['all_tokens'])}")
    
    # Get scaling values
    scaling_values = workflow.storage.data[start_word]
    
    print(f"\n4. Scaling values:")
    for key in ["rhy.sc", "rhy.prf.sc", "rhy.rch.sc", "rhy.sln.sc"]:
        if key in scaling_values:
            scaling = scaling_values[key]
            print(f"   {key}: min={scaling['min']:.6f}, max={scaling['max']:.6f}")
        else:
            print(f"   {key}: NOT FOUND")
    
    # Graph probability distribution for perfect rhymes
    if rhyme_data['perfect_tokens']:
        print(f"\n5. Graphing perfect rhyme probability distribution...")
        perfect_probs = [probability_vector[token] for token in rhyme_data['perfect_tokens'] 
                        if token < len(probability_vector)]
        
        if perfect_probs:
            plt.figure(figsize=(12, 8))
            
            # Create subplots
            plt.subplot(2, 2, 1)
            plt.hist(perfect_probs, bins=20, alpha=0.7, color='blue', edgecolor='black')
            plt.title('Perfect Rhyme Probability Distribution')
            plt.xlabel('Probability')
            plt.ylabel('Frequency')
            plt.axvline(np.min(perfect_probs), color='red', linestyle='--', label=f'Min: {np.min(perfect_probs):.6f}')
            plt.axvline(np.max(perfect_probs), color='green', linestyle='--', label=f'Max: {np.max(perfect_probs):.6f}')
            plt.legend()
            
            # Box plot
            plt.subplot(2, 2, 2)
            plt.boxplot(perfect_probs)
            plt.title('Perfect Rhyme Probability Box Plot')
            plt.ylabel('Probability')
            
            # Cumulative distribution
            plt.subplot(2, 2, 3)
            sorted_probs = np.sort(perfect_probs)
            cumulative = np.arange(1, len(sorted_probs) + 1) / len(sorted_probs)
            plt.plot(sorted_probs, cumulative, 'b-', linewidth=2)
            plt.title('Cumulative Distribution')
            plt.xlabel('Probability')
            plt.ylabel('Cumulative Probability')
            
            # Log scale histogram
            plt.subplot(2, 2, 4)
            plt.hist(perfect_probs, bins=20, alpha=0.7, color='orange', edgecolor='black')
            plt.title('Perfect Rhyme Probability (Log Scale)')
            plt.xlabel('Probability')
            plt.ylabel('Frequency')
            plt.yscale('log')
            
            plt.tight_layout()
            plt.savefig('perfect_rhyme_distribution.png', dpi=300, bbox_inches='tight')
            print(f"   📊 Graph saved as 'perfect_rhyme_distribution.png'")
            
            # Print statistics
            print(f"\n6. Perfect rhyme probability statistics:")
            print(f"   Count: {len(perfect_probs)}")
            print(f"   Mean: {np.mean(perfect_probs):.8f}")
            print(f"   Median: {np.median(perfect_probs):.8f}")
            print(f"   Std Dev: {np.std(perfect_probs):.8f}")
            print(f"   Min: {np.min(perfect_probs):.8f}")
            print(f"   Max: {np.max(perfect_probs):.8f}")
            print(f"   Range: {np.max(perfect_probs) - np.min(perfect_probs):.8f}")
            
            # Show some examples
            print(f"\n7. Sample perfect rhymes with probabilities:")
            for i, token in enumerate(rhyme_data['perfect_tokens'][:10]):
                if token < len(probability_vector):
                    prob = probability_vector[token]
                    # Try to decode the token back to word
                    try:
                        word = workflow.scorer.tokenizer.decode([token])
                        print(f"   {word.strip()}: {prob:.8f}")
                    except:
                        print(f"   Token {token}: {prob:.8f}")
    
    # Test a specific word
    test_word = "hat"
    print(f"\n8. Testing scoring for '{test_word}':")
    
    score_result = workflow.calculate_rhyme_score(start_word, test_word)
    
    if score_result["success"]:
        data = score_result["data"]
        print(f"   Raw probability: {data['raw_probability']:.6f}")
        print(f"   Normalized probability: {data['normalized_probability']:.6f}")
        print(f"   Base score: {data['base_score']:.2f}")
        print(f"   Bonuses: {data['bonuses']}")
        print(f"   Total bonus: {data['total_bonus']:.2f}")
        print(f"   Total score: {data['total_score']:.2f}")
        
        # Debug the scaling calculation
        candidate_token = data['candidate_token']
        candidate_prob = data['raw_probability']
        
        print(f"\n9. Scaling calculation debug:")
        print(f"   Candidate token: {candidate_token}")
        print(f"   Candidate probability: {candidate_prob:.6f}")
        
        # Check which category this word belongs to
        if candidate_token in rhyme_data["perfect_tokens"]:
            category = "perfect"
            scaling = scaling_values.get("rhy.prf.sc", {"min": 0, "max": 1})
        elif candidate_token in rhyme_data["rich_tokens"]:
            category = "rich"
            scaling = scaling_values.get("rhy.rch.sc", {"min": 0, "max": 1})
        elif candidate_token in rhyme_data["slant_tokens"]:
            category = "slant"
            scaling = scaling_values.get("rhy.sln.sc", {"min": 0, "max": 1})
        else:
            category = "unknown"
            scaling = {"min": 0, "max": 1}
        
        print(f"   Category: {category}")
        print(f"   Category scaling: min={scaling['min']:.6f}, max={scaling['max']:.6f}")
        
        if scaling['max'] > scaling['min']:
            normalized = (candidate_prob - scaling['min']) / (scaling['max'] - scaling['min'])
            print(f"   Category normalized: {normalized:.6f}")
            print(f"   This means: {normalized:.1%} of the way from min to max")
        else:
            print(f"   Category scaling has min=max, so normalized = 0")
    
    else:
        print(f"❌ Scoring failed: {score_result['message']}")

if __name__ == "__main__":
    asyncio.run(debug_scaling_values()) 