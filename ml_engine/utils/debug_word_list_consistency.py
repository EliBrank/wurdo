#!/usr/bin/env python3
"""
Debug Word List Consistency
==========================

Check if word lists are consistent between tree building and testing.
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from services.enhanced_scoring_service import get_enhanced_scoring_service
from services.efficient_word_service import get_efficient_word_service

async def debug_word_list_consistency():
    """Debug word list consistency between tree building and testing."""
    print("🔍 DEBUGGING WORD LIST CONSISTENCY")
    print("=" * 60)
    
    scoring_service = get_enhanced_scoring_service()
    word_service = get_efficient_word_service()
    
    # Test case
    start_word = "xylophone"
    
    print(f"🎯 Testing word lists for '{start_word}'")
    print()
    
    # Get transformations (same as used in tree building)
    transformations = word_service.get_comprehensive_transformations(start_word)
    
    print("📊 TRANSFORMATIONS FROM WORD SERVICE:")
    print(f"   Perfect rhymes: {len(transformations.perfect_rhymes)}")
    print(f"   Rich rhymes: {len(transformations.rich_rhymes)}")
    print(f"   Slant rhymes: {len(transformations.slant_rhymes)}")
    print(f"   Anagrams: {len(transformations.anagrams)}")
    print(f"   Added letters: {len(transformations.added_letters)}")
    print(f"   Removed letters: {len(transformations.removed_letters)}")
    print(f"   Changed letters: {len(transformations.changed_letters)}")
    
    # Show some examples
    print(f"\n🎵 PERFECT RHYMES (first 10):")
    for word in transformations.perfect_rhymes[:10]:
        print(f"   • {word}")
    
    print(f"\n🔄 ANAGRAMS:")
    for word in transformations.anagrams[:5]:
        print(f"   • {word}")
    
    # Check if tree exists and what it contains
    print(f"\n📦 CHECKING STORED TREE:")
    print("-" * 40)
    
    storage = scoring_service.storage
    tree = storage.get_probability_tree(start_word)
    
    if tree:
        print(f"✅ Tree found in storage")
        
        # Check what's actually in the tree
        if hasattr(tree, 'rhy') and 'prf' in tree.rhy:
            prf_node = tree.rhy['prf']
            if hasattr(prf_node, 'val'):
                stored_sequences = prf_node.val
                print(f"   Stored perfect rhyme sequences: {len(stored_sequences)}")
                
                # Decode some sequences to see what words they represent
                print(f"   First 5 stored sequences:")
                for i, seq in enumerate(stored_sequences[:5]):
                    try:
                        word = scoring_service.scorer.tokenizer.decode(seq)
                        print(f"     {i+1}. {seq} → '{word}'")
                    except:
                        print(f"     {i+1}. {seq} → [decode error]")
        
        if hasattr(tree, 'ana') and hasattr(tree.ana, 'val'):
            stored_sequences = tree.ana.val
            print(f"   Stored anagram sequences: {len(stored_sequences)}")
    
    # Test if the words from transformations are actually in the tree
    print(f"\n🎯 TESTING WORD-TREE CONSISTENCY:")
    print("-" * 40)
    
    test_words = transformations.perfect_rhymes[:5]
    print(f"Testing {len(test_words)} words from perfect rhymes:")
    
    success_count = 0
    for word in test_words:
        try:
            tokens = scoring_service.scorer.tokenizer.encode(word)
            # Try to get probability from tree
            prob = scoring_service.tree_builder.get_or_build_tree(start_word, {
                'prf': [tokens]
            })
            if prob:
                print(f"✅ '{word}': Found in tree")
                success_count += 1
            else:
                print(f"❌ '{word}': Not found in tree")
        except Exception as e:
            print(f"❌ '{word}': Error - {e}")
    
    print(f"\n📈 Consistency rate: {success_count}/{len(test_words)} ({success_count/len(test_words)*100:.1f}%)")
    
    # Check if the issue is with the tree lookup vs tree building
    print(f"\n🔍 COMPARING TREE BUILDING VS LOOKUP:")
    print("-" * 40)
    
    # Try to build a new tree for the same word
    print(f"Building new tree for '{start_word}'...")
    try:
        new_tree = scoring_service.tree_builder.get_or_build_tree(start_word, {
            'prf': [scoring_service.scorer.tokenizer.encode(word) for word in transformations.perfect_rhymes[:10]]
        })
        if new_tree:
            print(f"✅ New tree built successfully")
            print(f"   Tree type: {type(new_tree)}")
            print(f"   Tree size: {len(str(new_tree))} characters")
        else:
            print(f"❌ Failed to build new tree")
    except Exception as e:
        print(f"❌ Error building new tree: {e}")

if __name__ == "__main__":
    asyncio.run(debug_word_list_consistency()) 