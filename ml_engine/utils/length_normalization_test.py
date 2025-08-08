#!/usr/bin/env python3
"""
Length Normalization Test
=========================

Test the impact of length normalization on creativity scoring by:
1. Building a fresh probability tree for a chosen word
2. Calculating creativity scores for ALL valid transformations
3. Graphing distributions to visualize the effect
"""

import asyncio
import sys
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

sys.path.append(str(Path(__file__).parent.parent))

from services.enhanced_scoring_service import get_enhanced_scoring_service
from services.efficient_word_service import get_efficient_word_service
from models.probability_tree import ProbabilityTreeLookup

class LengthNormalizationTester:
    def __init__(self):
        self.scoring_service = get_enhanced_scoring_service()
        self.word_service = get_efficient_word_service()
        
    async def test_length_normalization(self, start_word: str):
        """Comprehensive test of length normalization."""
        print(f"🧪 TESTING LENGTH NORMALIZATION")
        print(f"Start word: '{start_word}'")
        print("=" * 60)
        
        # Step 1: Build fresh probability tree
        print(f"\n📦 STEP 1: Building fresh probability tree for '{start_word}'")
        print("-" * 40)
        
        tree = self.scoring_service._get_or_build_probability_tree(start_word)
        if tree is None:
            print(f"❌ Failed to build probability tree for '{start_word}'")
            return
            
        print(f"✅ Probability tree built successfully")
        
        # Step 2: Get all valid transformations
        print(f"\n🔄 STEP 2: Getting all valid transformations")
        print("-" * 40)
        
        transformations = self.word_service.get_comprehensive_transformations(start_word)
        
        # Organize by category
        categories = {
            'prf': transformations.perfect_rhymes,
            'rch': transformations.rich_rhymes, 
            'sln': transformations.slant_rhymes,
            'ana': transformations.anagrams,
            'ola': transformations.added_letters,
            'olr': transformations.removed_letters,
            'olx': transformations.changed_letters
        }
        
        total_words = sum(len(words) for words in categories.values())
        print(f"Total valid transformations: {total_words}")
        
        for category, words in categories.items():
            print(f"  {category.upper()}: {len(words)} words")
        
        # Step 3: Calculate creativity scores for all words
        print(f"\n🎯 STEP 3: Calculating creativity scores")
        print("-" * 40)
        
        results = {}
        category_results = defaultdict(list)
        
        for category, words in categories.items():
            print(f"Processing {category.upper()} ({len(words)} words)...")
            
            for word in words:
                try:
                    # Get creativity score using tree lookup
                    score_data = await self._get_creativity_score_from_tree(
                        tree, start_word, word, category
                    )
                    
                    if score_data:
                        results[word] = score_data
                        category_results[category].append(score_data)
                        
                except Exception as e:
                    print(f"❌ Error processing '{word}': {e}")
        
        print(f"✅ Successfully processed {len(results)} words")
        
        # Step 4: Analyze distributions
        print(f"\n📊 STEP 4: Analyzing distributions")
        print("-" * 40)
        
        self._analyze_distributions(results, category_results)
        
        # Step 5: Generate visualizations
        print(f"\n📈 STEP 5: Generating visualizations")
        print("-" * 40)
        
        self._generate_visualizations(results, category_results, start_word)
        
        return results
    
    async def _get_creativity_score_from_tree(self, tree, start_word: str, candidate_word: str, category: str) -> Dict:
        """Get creativity score using probability tree lookup."""
        
        # Map category to tree structure
        category_mapping = {
            'prf': ('rhy', 'prf'),
            'rch': ('rhy', 'rch'), 
            'sln': ('rhy', 'sln'),
            'ana': ('ana', 'ana'),
            'ola': ('olo', 'ola'),
            'olr': ('olo', 'olr'),
            'olx': ('olo', 'olx')
        }
        
        main_category, subcategory = category_mapping.get(category, (None, None))
        if main_category is None:
            return None
            
        # Tokenize candidate
        candidate_tokens = self.scoring_service.scorer.tokenizer.encode(candidate_word)
        if not candidate_tokens:
            return None
            
        try:
            # Get sequence probability and creativity score from tree
            sequence_prob = ProbabilityTreeLookup.get_sequence_probability(
                tree, main_category, subcategory, candidate_tokens
            )
            
            creativity_score = ProbabilityTreeLookup.get_creativity_score(
                tree, main_category, subcategory, candidate_tokens
            )
            
            return {
                'word': candidate_word,
                'category': category,
                'token_count': len(candidate_tokens),
                'sequence_probability': sequence_prob,
                'creativity_score': creativity_score,
                'word_length': len(candidate_word)
            }
            
        except Exception as e:
            print(f"❌ Tree lookup failed for '{candidate_word}': {e}")
            return None
    
    def _analyze_distributions(self, results: Dict, category_results: Dict):
        """Analyze creativity score distributions."""
        
        all_scores = [data['creativity_score'] for data in results.values()]
        
        print(f"Overall Statistics:")
        print(f"  Total words: {len(all_scores)}")
        print(f"  Mean creativity: {np.mean(all_scores):.4f}")
        print(f"  Std creativity: {np.std(all_scores):.4f}")
        print(f"  Min creativity: {np.min(all_scores):.4f}")
        print(f"  Max creativity: {np.max(all_scores):.4f}")
        
        # Analyze by token count
        token_groups = defaultdict(list)
        for data in results.values():
            token_groups[data['token_count']].append(data['creativity_score'])
        
        print(f"\nBy Token Count:")
        for token_count in sorted(token_groups.keys()):
            scores = token_groups[token_count]
            print(f"  {token_count} token(s): {len(scores)} words, mean={np.mean(scores):.4f}, std={np.std(scores):.4f}")
        
        # Analyze by category
        print(f"\nBy Category:")
        for category, data_list in category_results.items():
            if data_list:
                scores = [d['creativity_score'] for d in data_list]
                print(f"  {category.upper()}: {len(scores)} words, mean={np.mean(scores):.4f}, std={np.std(scores):.4f}")
    
    def _generate_visualizations(self, results: Dict, category_results: Dict, start_word: str):
        """Generate comprehensive visualizations."""
        
        # Prepare data
        all_scores = [data['creativity_score'] for data in results.values()]
        token_counts = [data['token_count'] for data in results.values()]
        word_lengths = [data['word_length'] for data in results.values()]
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Length Normalization Test: "{start_word}" → All Transformations', fontsize=16)
        
        # 1. Overall creativity score distribution
        axes[0, 0].hist(all_scores, bins=30, alpha=0.7, color='blue', edgecolor='black')
        axes[0, 0].set_title('Overall Creativity Score Distribution')
        axes[0, 0].set_xlabel('Creativity Score')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(np.mean(all_scores), color='red', linestyle='--', label=f'Mean: {np.mean(all_scores):.3f}')
        axes[0, 0].legend()
        
        # 2. Creativity vs Token Count
        axes[0, 1].scatter(token_counts, all_scores, alpha=0.6, color='green')
        axes[0, 1].set_title('Creativity Score vs Token Count')
        axes[0, 1].set_xlabel('Token Count')
        axes[0, 1].set_ylabel('Creativity Score')
        
        # 3. Creativity vs Word Length
        axes[0, 2].scatter(word_lengths, all_scores, alpha=0.6, color='orange')
        axes[0, 2].set_title('Creativity Score vs Word Length')
        axes[0, 2].set_xlabel('Word Length (characters)')
        axes[0, 2].set_ylabel('Creativity Score')
        
        # 4. Distribution by category
        category_names = list(category_results.keys())
        category_means = []
        category_stds = []
        
        for category in category_names:
            if category_results[category]:
                scores = [d['creativity_score'] for d in category_results[category]]
                category_means.append(np.mean(scores))
                category_stds.append(np.std(scores))
            else:
                category_means.append(0)
                category_stds.append(0)
        
        x_pos = np.arange(len(category_names))
        axes[1, 0].bar(x_pos, category_means, yerr=category_stds, capsize=5, alpha=0.7)
        axes[1, 0].set_title('Mean Creativity Score by Category')
        axes[1, 0].set_xlabel('Category')
        axes[1, 0].set_ylabel('Mean Creativity Score')
        axes[1, 0].set_xticks(x_pos)
        axes[1, 0].set_xticklabels([c.upper() for c in category_names], rotation=45)
        
        # 5. Token count distribution
        token_count_freq = defaultdict(int)
        for count in token_counts:
            token_count_freq[count] += 1
        
        axes[1, 1].bar(token_count_freq.keys(), token_count_freq.values(), alpha=0.7, color='purple')
        axes[1, 1].set_title('Distribution of Token Counts')
        axes[1, 1].set_xlabel('Token Count')
        axes[1, 1].set_ylabel('Number of Words')
        
        # 6. Creativity score ranges
        score_ranges = [(0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
        range_counts = []
        range_labels = []
        
        for low, high in score_ranges:
            count = sum(1 for score in all_scores if low <= score < high)
            range_counts.append(count)
            range_labels.append(f'{low}-{high}')
        
        axes[1, 2].bar(range_labels, range_counts, alpha=0.7, color='red')
        axes[1, 2].set_title('Creativity Score Ranges')
        axes[1, 2].set_xlabel('Score Range')
        axes[1, 2].set_ylabel('Number of Words')
        axes[1, 2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save the plot
        output_file = f"length_normalization_test_{start_word}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Visualization saved as: {output_file}")
        
        # Show summary statistics
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"  Total words tested: {len(results)}")
        print(f"  Creativity score range: {np.min(all_scores):.4f} - {np.max(all_scores):.4f}")
        print(f"  Mean creativity: {np.mean(all_scores):.4f}")
        print(f"  Standard deviation: {np.std(all_scores):.4f}")
        print(f"  Token count range: {min(token_counts)} - {max(token_counts)}")
        print(f"  Word length range: {min(word_lengths)} - {max(word_lengths)}")

async def main():
    """Main test function."""
    tester = LengthNormalizationTester()
    
    # Choose a good test word with diverse transformations
    test_word = "xylophone"  # Good choice: has rhymes, anagrams, OLO transformations
    
    print(f"🎯 Testing length normalization with start word: '{test_word}'")
    print("This will build a fresh probability tree and analyze all transformations.")
    print()
    
    results = await tester.test_length_normalization(test_word)
    
    if results:
        print(f"\n✅ Test completed successfully!")
        print(f"Analyzed {len(results)} transformations")
        print(f"Check the generated visualization for detailed analysis")
    else:
        print(f"\n❌ Test failed")

if __name__ == "__main__":
    asyncio.run(main()) 