#!/usr/bin/env python3
"""
Tree Completeness Test
======================

Test the completeness of stored probability trees by attempting to score
all transformations for a set of test words.
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from services.enhanced_scoring_service import get_enhanced_scoring_service
from services.efficient_word_service import get_efficient_word_service

async def tree_completeness_test():
    """Test completeness of stored probability trees."""
    print("🔍 TREE COMPLETENESS TEST")
    print("=" * 60)
    
    scoring_service = get_enhanced_scoring_service()
    word_service = get_efficient_word_service()
    
    # Test words
    test_words = ["xylophone", "bestowed", "cat", "dog", "hello"]
    
    total_tests = 0
    successful_lookups = 0
    failed_lookups = 0
    
    for start_word in test_words:
        print(f"\n🎯 Testing tree for '{start_word}'")
        print("-" * 40)
        
        # Get transformations for this word
        transformations = word_service.get_comprehensive_transformations(start_word)
        
        # Count available transformations
        available_categories = {}
        if transformations.perfect_rhymes:
            available_categories['prf'] = transformations.perfect_rhymes
        if transformations.rich_rhymes:
            available_categories['rch'] = transformations.rich_rhymes
        if transformations.slant_rhymes:
            available_categories['sln'] = transformations.slant_rhymes
        if transformations.anagrams:
            available_categories['ana'] = transformations.anagrams
        if transformations.added_letters:
            available_categories['ola'] = transformations.added_letters
        if transformations.removed_letters:
            available_categories['olr'] = transformations.removed_letters
        if transformations.changed_letters:
            available_categories['olx'] = transformations.changed_letters
        
        print(f"📊 Available categories: {list(available_categories.keys())}")
        for category, words in available_categories.items():
            print(f"   {category}: {len(words)} words")
        
        if not available_categories:
            print(f"⚠️  No transformations available for '{start_word}'")
            continue
        
        # Test each category that has words
        for category, words in available_categories.items():
            print(f"\n🔍 Testing category '{category}' ({len(words)} words)")
            
            # Test first 5 words from each category (to avoid too many tests)
            test_words_in_category = words[:5]
            
            for candidate_word in test_words_in_category:
                total_tests += 1
                
                try:
                    # Try to score this word using the tree
                    result = await scoring_service.score_candidate_comprehensive(start_word, candidate_word)
                    
                    if result["success"]:
                        successful_lookups += 1
                        print(f"✅ '{candidate_word}': Score {result['data']['total_score']:.2f}")
                    else:
                        failed_lookups += 1
                        print(f"❌ '{candidate_word}': {result['message']}")
                        
                except Exception as e:
                    failed_lookups += 1
                    print(f"❌ '{candidate_word}': Error - {e}")
    
    # Summary
    print(f"\n📊 COMPLETENESS TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Successful lookups: {successful_lookups}")
    print(f"Failed lookups: {failed_lookups}")
    
    if total_tests > 0:
        success_rate = (successful_lookups / total_tests) * 100
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print("🎉 EXCELLENT: Tree completeness is very high!")
        elif success_rate >= 80:
            print("✅ GOOD: Tree completeness is acceptable")
        elif success_rate >= 60:
            print("⚠️  FAIR: Tree completeness needs improvement")
        else:
            print("❌ POOR: Tree completeness is too low")
    else:
        print("⚠️  No tests were performed")

if __name__ == "__main__":
    asyncio.run(tree_completeness_test()) 