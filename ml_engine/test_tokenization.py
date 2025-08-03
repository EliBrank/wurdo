#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.game_workflow import GameWorkflow
import asyncio

async def test_tokenization():
    """Test if words are being tokenized as single tokens or multiple tokens."""
    
    # Initialize workflow
    workflow = GameWorkflow(storage_type="json")
    
    print("🔍 Testing tokenization behavior")
    print("=" * 50)
    
    # Test words from our rhyme data
    test_words = ["flat", "splat", "bat", "cat", "hat", "rat", "fat", "chat", "brat", "combat"]
    
    print("1. Testing tokenization of individual words:")
    for word in test_words:
        tokens = workflow.scorer.tokenizer.encode(word)
        decoded = workflow.scorer.tokenizer.decode(tokens)
        print(f"   '{word}' -> tokens: {tokens} -> decoded: '{decoded.strip()}'")
        print(f"   Token count: {len(tokens)}")
        if len(tokens) > 1:
            print(f"   ⚠️  MULTIPLE TOKENS!")
        print()
    
    print("2. Testing what happens when we take only the first token:")
    for word in test_words:
        tokens = workflow.scorer.tokenizer.encode(word)
        first_token = tokens[0] if tokens else None
        decoded_first = workflow.scorer.tokenizer.decode([first_token]) if first_token is not None else ""
        print(f"   '{word}' -> first token: {first_token} -> decoded: '{decoded_first.strip()}'")
        print()
    
    print("3. Testing our current tokenization method:")
    # Simulate what we're doing in tokenize_rhymes
    for word in test_words:
        try:
            tokens = workflow.scorer.tokenizer.encode(word)
            first_token = tokens[0] if tokens else None
            decoded_first = workflow.scorer.tokenizer.decode([first_token]) if first_token is not None else ""
            print(f"   '{word}' -> first token only: {first_token} -> '{decoded_first.strip()}'")
        except Exception as e:
            print(f"   '{word}' -> ERROR: {e}")
        print()

if __name__ == "__main__":
    asyncio.run(test_tokenization()) 