#!/usr/bin/env python3
"""
Tree Completeness Test
======================

Test the completeness of stored probability trees by examining stored data
and attempting to score all transformations for a set of test words.
"""

import asyncio
import sys
import json
import gzip
import pickle
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from services.enhanced_scoring_service import get_enhanced_scoring_service
from services.efficient_word_service import get_efficient_word_service

def analyze_stored_trees():
    """Analyze stored probability trees without loading ONNX model."""
    print("🔍 STORED TREE ANALYSIS")
    print("=" * 60)
    
    try:
        # Load stored trees data
        with open('game_data/probability_trees.json', 'r') as f:
            stored_data = json.load(f)
        
        print(f"📦 Found {len(stored_data)} stored probability trees")
        print(f"📋 Stored words: {list(stored_data.keys())}")
        print()
        
        total_stored_size = 0
        tree_details = {}
        
        for word, entry in stored_data.items():
            size_bytes = entry['metadata']['size_bytes']
            total_stored_size += size_bytes
            
            print(f"🎯 '{word}': {size_bytes} bytes")
            
            # Decompress and analyze tree structure
            try:
                serialized = entry['serialized']
                decompressed = gzip.decompress(bytes.fromhex(serialized))
                tree_dict = pickle.loads(decompressed)
                
                # Analyze tree structure
                tree_details[word] = {
                    'size_bytes': size_bytes,
                    'frq': tree_dict.get('frq', 0),
                    'ana_sequences': len(tree_dict.get('ana', {}).get('val', [])) if 'ana' in tree_dict else 0,
                    'olo_sequences': sum(len(node.get('val', [])) for node in tree_dict.get('olo', {}).values()) if 'olo' in tree_dict else 0,
                    'rhy_sequences': sum(len(node.get('val', [])) for node in tree_dict.get('rhy', {}).values()) if 'rhy' in tree_dict else 0,
                    'total_sequences': 0
                }
                
                # Calculate total sequences
                tree_details[word]['total_sequences'] = (
                    tree_details[word]['ana_sequences'] + 
                    tree_details[word]['olo_sequences'] + 
                    tree_details[word]['rhy_sequences']
                )
                
                print(f"   📊 Sequences: {tree_details[word]['total_sequences']} total")
                print(f"      - Anagrams: {tree_details[word]['ana_sequences']}")
                print(f"      - OLO: {tree_details[word]['olo_sequences']}")
                print(f"      - Rhymes: {tree_details[word]['rhy_sequences']}")
                
            except Exception as e:
                print(f"   ❌ Error analyzing tree: {e}")
                tree_details[word] = {'error': str(e)}
        
        print(f"\n📊 STORAGE SUMMARY")
        print("=" * 60)
        print(f"Total stored size: {total_stored_size:,} bytes ({total_stored_size/1024:.1f} KB)")
        print(f"Average tree size: {total_stored_size/len(stored_data):.0f} bytes")
        
        # Calculate completeness metrics
        total_sequences = sum(d.get('total_sequences', 0) for d in tree_details.values() if 'error' not in d)
        print(f"Total sequences stored: {total_sequences:,}")
        
        if tree_details:
            avg_sequences = total_sequences / len([d for d in tree_details.values() if 'error' not in d])
            print(f"Average sequences per tree: {avg_sequences:.1f}")
        
        return tree_details, stored_data
        
    except FileNotFoundError:
        print("❌ No probability_trees.json file found")
        return {}, {}
    except Exception as e:
        print(f"❌ Error analyzing stored trees: {e}")
        return {}, {}

def propose_new_word(stored_words):
    """Propose a word that's not in storage."""
    # Common words that are likely to have good transformations
    candidate_words = [
        "happy", "music", "dance", "smile", "dream", "light", "heart", 
        "world", "peace", "love", "hope", "star", "moon", "sun", "rain",
        "tree", "bird", "fish", "book", "time", "life", "work", "play",
        "food", "home", "road", "door", "wall", "floor", "chair", "table"
    ]
    
    # Find a word not in storage
    for word in candidate_words:
        if word not in stored_words:
            return word
    
    # If all common words are stored, use a longer word
    return "beautiful"

async def test_tree_generation_for_new_word(word):
    """Test complete tree generation for a new word."""
    print(f"\n🚀 TESTING TREE GENERATION FOR '{word.upper()}'")
    print("=" * 60)
    
    try:
        scoring_service = get_enhanced_scoring_service()
        word_service = get_efficient_word_service()
        
        print(f"🎯 Building complete probability tree for '{word}'")
        
        # Get transformations for this word
        transformations = word_service.get_comprehensive_transformations(word)
        
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
        total_transformations = sum(len(words) for words in available_categories.values())
        print(f"📈 Total transformations: {total_transformations}")
        
        for category, words in available_categories.items():
            print(f"   {category}: {len(words)} words")
        
        if not available_categories:
            print(f"⚠️  No transformations available for '{word}'")
            return False
        
        # Test scoring for each category
        total_tests = 0
        successful_lookups = 0
        failed_lookups = 0
        
        print(f"\n🔍 Testing scoring for each category:")
        
        for category, words in available_categories.items():
            print(f"\n🎯 Testing category '{category}' ({len(words)} words)")
            
            # Test first 3 words from each category (to avoid too many tests)
            test_words_in_category = words[:3]
            
            for candidate_word in test_words_in_category:
                total_tests += 1
                
                try:
                    # Try to score this word using the tree
                    result = await scoring_service.score_candidate_comprehensive(word, candidate_word)
                    
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
        print(f"\n📊 TREE GENERATION TEST SUMMARY")
        print("=" * 60)
        print(f"Word tested: '{word}'")
        print(f"Total transformations available: {total_transformations}")
        print(f"Total tests: {total_tests}")
        print(f"Successful lookups: {successful_lookups}")
        print(f"Failed lookups: {failed_lookups}")
        
        if total_tests > 0:
            success_rate = (successful_lookups / total_tests) * 100
            print(f"Success rate: {success_rate:.1f}%")
            
            if success_rate >= 95:
                print("🎉 EXCELLENT: Tree generation is working perfectly!")
            elif success_rate >= 80:
                print("✅ GOOD: Tree generation is working well")
            elif success_rate >= 60:
                print("⚠️  FAIR: Tree generation needs improvement")
            else:
                print("❌ POOR: Tree generation has issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing tree generation: {e}")
        return False

async def tree_completeness_test():
    """Test completeness of stored probability trees."""
    print("🔍 TREE COMPLETENESS TEST")
    print("=" * 60)
    
    # First, analyze stored trees without loading model
    stored_analysis, stored_data = analyze_stored_trees()
    
    if not stored_analysis:
        print("❌ No stored trees to analyze")
        return
    
    # Propose a new word to test
    new_word = propose_new_word(stored_data.keys())
    print(f"\n🎯 PROPOSED NEW WORD: '{new_word}'")
    print(f"📋 This word is NOT in storage: {new_word not in stored_data}")
    
    # Test 1: Tree generation for new word
    print(f"\n" + "="*80)
    generation_success = await test_tree_generation_for_new_word(new_word)
    
    # Test 2: Storage completeness check
    print(f"\n" + "="*80)
    print(f"🎯 COMPREHENSIVE STORAGE COMPLETENESS CHECK")
    print("=" * 60)
    
    # Now test with scoring service (if available)
    try:
        scoring_service = get_enhanced_scoring_service()
        word_service = get_efficient_word_service()
        
        # Test words (including our new word)
        test_words = ["xylophone", "bestowed", "cat", "dog", "hello", new_word]
        
        total_tests = 0
        successful_lookups = 0
        failed_lookups = 0
        
        for start_word in test_words:
            print(f"\n🎯 Testing tree for '{start_word}'")
            print("-" * 40)
            
            # Check if tree exists in storage
            if start_word in stored_analysis:
                print(f"✅ Tree found in storage ({stored_analysis[start_word]['size_bytes']} bytes)")
                if 'total_sequences' in stored_analysis[start_word]:
                    print(f"   Sequences: {stored_analysis[start_word]['total_sequences']}")
            else:
                print(f"❌ No tree found in storage for '{start_word}'")
                continue
            
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
            
    except Exception as e:
        print(f"⚠️  Could not run scoring tests (ONNX model not available): {e}")
        print("   Stored tree analysis completed successfully above.")
    
    # Final comparison
    print(f"\n" + "="*80)
    print(f"📊 COMPARISON SUMMARY")
    print("=" * 60)
    print(f"✅ Tree Generation Test: {'PASSED' if generation_success else 'FAILED'}")
    print(f"✅ Storage Completeness Test: {'PASSED' if total_tests > 0 and successful_lookups == total_tests else 'FAILED'}")
    print(f"🎯 New word tested: '{new_word}'")
    print(f"📦 Stored trees analyzed: {len(stored_analysis)}")
    print(f"📈 Total sequences in storage: {sum(d.get('total_sequences', 0) for d in stored_analysis.values() if 'error' not in d):,}")

if __name__ == "__main__":
    asyncio.run(tree_completeness_test()) 