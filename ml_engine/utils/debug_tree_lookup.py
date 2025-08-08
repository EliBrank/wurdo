#!/usr/bin/env python3
"""
Debug Probability Tree Lookup
============================

Trace exactly what's happening with probability tree storage and retrieval.
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from services.enhanced_scoring_service import get_enhanced_scoring_service
from services.efficient_word_service import get_efficient_word_service
from models.probability_tree import ProbabilityTreeLookup

async def debug_tree_lookup():
    """Debug probability tree lookup step by step."""
    print("🔍 DEBUGGING PROBABILITY TREE LOOKUP")
    print("=" * 60)
    
    scoring_service = get_enhanced_scoring_service()
    word_service = get_efficient_word_service()
    
    # Test case
    start_word = "xylophone"
    candidate_word = "telephone"
    
    print(f"🎯 Testing: '{start_word}' → '{candidate_word}'")
    print()
    
    # Step 1: Check if tree exists in storage
    print("📦 STEP 1: Check tree storage")
    print("-" * 40)
    
    storage = scoring_service.storage
    tree = storage.get_probability_tree(start_word)
    
    if tree:
        print(f"✅ Tree found in storage for '{start_word}'")
        print(f"   Tree type: {type(tree)}")
        print(f"   Tree attributes: {dir(tree)}")
        
        # Check tree structure
        if hasattr(tree, 'rhy'):
            print(f"   Rhyme data: {type(tree.rhy)}")
        if hasattr(tree, 'ana'):
            print(f"   Anagram data: {type(tree.ana)}")
        if hasattr(tree, 'olo'):
            print(f"   OLO data: {type(tree.olo)}")
    else:
        print(f"❌ No tree found in storage for '{start_word}'")
        return
    
    # Step 2: Get transformations
    print(f"\n🔄 STEP 2: Get transformations")
    print("-" * 40)
    
    transformations = word_service.get_comprehensive_transformations(start_word)
    print(f"Perfect rhymes: {len(transformations.perfect_rhymes)}")
    print(f"Anagrams: {len(transformations.anagrams)}")
    print(f"OLO: {len(transformations.added_letters) + len(transformations.removed_letters) + len(transformations.changed_letters)}")
    
    # Check if candidate is in transformations
    if candidate_word in transformations.perfect_rhymes:
        category = "prf"
        print(f"✅ '{candidate_word}' found in perfect rhymes")
    elif candidate_word in transformations.anagrams:
        category = "ana"
        print(f"✅ '{candidate_word}' found in anagrams")
    else:
        print(f"❌ '{candidate_word}' not found in transformations")
        return
    
    # Step 3: Test direct tree lookup
    print(f"\n🎯 STEP 3: Test direct tree lookup")
    print("-" * 40)
    
    # Tokenize candidate
    candidate_tokens = scoring_service.scorer.tokenizer.encode(candidate_word)
    print(f"Tokenized '{candidate_word}': {candidate_tokens}")
    
    # Map category
    category_mapping = {
        'prf': ('rhy', 'prf'),
        'ana': ('ana', 'ana'),
    }
    
    main_category, subcategory = category_mapping.get(category, (None, None))
    print(f"Category mapping: {category} → ({main_category}, {subcategory})")
    
    # Test lookup methods
    try:
        print(f"\n🔍 Testing ProbabilityTreeLookup.get_sequence_probability()...")
        sequence_prob = ProbabilityTreeLookup.get_sequence_probability(
            tree, main_category, subcategory, candidate_tokens
        )
        print(f"✅ Sequence probability: {sequence_prob}")
    except Exception as e:
        print(f"❌ Error in get_sequence_probability: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        print(f"\n🔍 Testing ProbabilityTreeLookup.get_creativity_score()...")
        creativity_score = ProbabilityTreeLookup.get_creativity_score(
            tree, main_category, subcategory, candidate_tokens
        )
        print(f"✅ Creativity score: {creativity_score}")
    except Exception as e:
        print(f"❌ Error in get_creativity_score: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Test the actual scoring method
    print(f"\n🎯 STEP 4: Test actual scoring method")
    print("-" * 40)
    
    try:
        result = await scoring_service.score_candidate_comprehensive(start_word, candidate_word)
        if result["success"]:
            print(f"✅ Comprehensive scoring succeeded")
            print(f"   Total score: {result['data']['total_score']}")
            print(f"   Categories: {result['data']['valid_categories']}")
        else:
            print(f"❌ Comprehensive scoring failed: {result['message']}")
    except Exception as e:
        print(f"❌ Error in comprehensive scoring: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Check tree completeness for this specific case
    print(f"\n📊 STEP 5: Check tree completeness for this case")
    print("-" * 40)
    
    # Test a few more words from the same tree
    test_words = transformations.perfect_rhymes[:3]
    print(f"Testing {len(test_words)} words from perfect rhymes: {test_words}")
    
    success_count = 0
    for word in test_words:
        try:
            tokens = scoring_service.scorer.tokenizer.encode(word)
            prob = ProbabilityTreeLookup.get_sequence_probability(tree, 'rhy', 'prf', tokens)
            print(f"✅ '{word}': {prob}")
            success_count += 1
        except Exception as e:
            print(f"❌ '{word}': {e}")
    
    print(f"\n📈 Success rate: {success_count}/{len(test_words)} ({success_count/len(test_words)*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(debug_tree_lookup()) 