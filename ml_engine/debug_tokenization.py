#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.game_workflow import GameWorkflow
import asyncio

async def debug_tokenization():
    """Debug what words are actually being tokenized and stored."""
    
    # Initialize workflow
    workflow = GameWorkflow(storage_type="json")
    
    # Test word
    start_word = "cat"
    
    print(f"🔍 Debugging tokenization for '{start_word}'")
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
    
    print(f"\n2. Raw rhyme data from CMU:")
    # Get the original rhymes before tokenization
    all_rhymes = workflow.cmu_client.get_rhymes(start_word)
    filtered_rhymes = workflow.cmu_client.filter_rhymes_by_quality(all_rhymes)
    categorized = workflow.cmu_client.categorize_rhymes_by_quality(start_word, filtered_rhymes)
    
    print(f"   Original rhymes from CMU: {len(all_rhymes)}")
    print(f"   After filtering: {len(filtered_rhymes)}")
    print(f"   Perfect rhymes: {len(categorized['perfect'])}")
    print(f"   Near rhymes: {len(categorized['near'])}")
    
    print(f"\n3. Sample filtered rhymes:")
    for i, rhyme in enumerate(filtered_rhymes[:20]):
        print(f"   {i+1:2d}. '{rhyme}' (length: {len(rhyme)})")
    
    print(f"\n4. Sample perfect rhymes:")
    for i, rhyme in enumerate(categorized['perfect'][:20]):
        print(f"   {i+1:2d}. '{rhyme}' (length: {len(rhyme)})")
    
    print(f"\n5. Tokenized data:")
    print(f"   Perfect tokens: {len(rhyme_data['perfect_tokens'])}")
    print(f"   Rich tokens: {len(rhyme_data['rich_tokens'])}")
    print(f"   Slant tokens: {len(rhyme_data['slant_tokens'])}")
    print(f"   All tokens: {len(rhyme_data['all_tokens'])}")
    
    print(f"\n6. Decoding tokens back to words:")
    print(f"   Sample perfect tokens:")
    for i, token in enumerate(rhyme_data['perfect_tokens'][:10]):
        try:
            word = workflow.scorer.tokenizer.decode([token])
            print(f"   {i+1:2d}. Token {token} -> '{word.strip()}'")
        except Exception as e:
            print(f"   {i+1:2d}. Token {token} -> ERROR: {e}")
    
    print(f"\n7. Checking for short words in tokenized data:")
    short_words = []
    for token in rhyme_data['perfect_tokens']:
        try:
            word = workflow.scorer.tokenizer.decode([token])
            word = word.strip()
            if len(word) < 3:
                short_words.append((token, word))
        except:
            pass
    
    if short_words:
        print(f"   Found {len(short_words)} words with < 3 chars:")
        for token, word in short_words[:10]:
            print(f"   Token {token} -> '{word}' (length: {len(word)})")
    else:
        print(f"   No words with < 3 chars found in tokenized data")
    
    print(f"\n8. FULL ANALYSIS: Converting all rhy.val tokens to words:")
    print(f"   Total tokens in rhy.val: {len(rhyme_data['all_tokens'])}")
    
    # Decode all tokens in rhy.val
    all_words = []
    for token in rhyme_data['all_tokens']:
        try:
            word = workflow.scorer.tokenizer.decode([token])
            word = word.strip()
            all_words.append((token, word))
        except Exception as e:
            all_words.append((token, f"ERROR: {e}"))
    
    print(f"   Successfully decoded: {len([w for _, w in all_words if not w.startswith('ERROR')])}")
    
    # Categorize by length
    short_words = [(t, w) for t, w in all_words if len(w) < 3 and not w.startswith('ERROR')]
    medium_words = [(t, w) for t, w in all_words if 3 <= len(w) <= 7 and not w.startswith('ERROR')]
    long_words = [(t, w) for t, w in all_words if len(w) > 7 and not w.startswith('ERROR')]
    error_words = [(t, w) for t, w in all_words if w.startswith('ERROR')]
    
    print(f"\n   Length breakdown:")
    print(f"   < 3 chars: {len(short_words)} words")
    print(f"   3-7 chars: {len(medium_words)} words")
    print(f"   > 7 chars: {len(long_words)} words")
    print(f"   Errors: {len(error_words)} tokens")
    
    print(f"\n   Sample short words (< 3 chars):")
    for i, (token, word) in enumerate(short_words[:15]):
        print(f"   {i+1:2d}. Token {token} -> '{word}' (length: {len(word)})")
    
    print(f"\n   Sample medium words (3-7 chars):")
    for i, (token, word) in enumerate(medium_words[:15]):
        print(f"   {i+1:2d}. Token {token} -> '{word}' (length: {len(word)})")
    
    if long_words:
        print(f"\n   Sample long words (> 7 chars):")
        for i, (token, word) in enumerate(long_words[:10]):
            print(f"   {i+1:2d}. Token {token} -> '{word}' (length: {len(word)})")
    
    if error_words:
        print(f"\n   Sample error tokens:")
        for i, (token, word) in enumerate(error_words[:10]):
            print(f"   {i+1:2d}. Token {token} -> {word}")

if __name__ == "__main__":
    asyncio.run(debug_tokenization()) 