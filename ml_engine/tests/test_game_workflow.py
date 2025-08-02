#!/usr/bin/env python3
"""
Test script to demonstrate the complete game workflow with JSON storage.
"""

import sys
import os
import asyncio
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.game_workflow import GameWorkflow

async def test_game_workflow():
    """Test the complete game workflow with JSON storage."""
    print("Testing Complete Game Workflow\n")
    print("=" * 50)
    
    try:
        # Initialize workflow with JSON storage
        print("1. Initializing GameWorkflow with JSON storage...")
        workflow = GameWorkflow(storage_type="json", json_file_path="test_game_data.json")
        print("✅ GameWorkflow initialized successfully")
        
        # Test word preparation
        test_words = ["cat", "dog", "hat"]
        
        print(f"\n2. Preparing test words for gameplay: {test_words}")
        print("-" * 40)
        
        for word in test_words:
            print(f"\nPreparing '{word}'...")
            result = await workflow.prepare_word_for_gameplay(word)
            
            if result["success"]:
                print(f"✅ {result['message']}")
                if result["data"]["rhyme_data"]["cached"]:
                    print(f"   📦 Used cached rhyme data")
                if result["data"]["probability_vector"]["cached"]:
                    print(f"   📦 Used cached probability vector")
                
                # Handle different data structures
                rhyme_data = result["data"]["rhyme_data"]
                if "total_count" in rhyme_data:
                    print(f"   📊 Rhymes found: {rhyme_data['total_count']}")
                else:
                    print(f"   📊 Used cached rhyme data")
                
                vector_data = result["data"]["probability_vector"]
                if "vector_size" in vector_data:
                    print(f"   🧮 Vector size: {vector_data['vector_size']:,}")
                else:
                    print(f"   🧮 Used cached probability vector")
            else:
                print(f"❌ {result['message']}")
        
        # Test scoring
        print(f"\n3. Testing rhyme scoring")
        print("-" * 40)
        
        test_candidates = [
            ("cat", "bat"),   # Perfect rhyme
            ("cat", "hat"),   # Perfect rhyme
            ("cat", "rat"),   # Perfect rhyme
            ("cat", "sat"),   # Perfect rhyme
            ("cat", "mat"),   # Perfect rhyme
            ("cat", "pat"),   # Perfect rhyme
            ("cat", "fat"),   # Perfect rhyme
            ("cat", "gat"),   # Perfect rhyme
            ("cat", "lat"),   # Perfect rhyme
            ("cat", "nat"),   # Perfect rhyme
        ]
        
        scores = []
        for start_word, candidate in test_candidates:
            print(f"\nScoring '{candidate}' for '{start_word}'...")
            result = workflow.calculate_rhyme_score(start_word, candidate)
            
            if result["success"]:
                data = result["data"]
                print(f"✅ Score: {data['total_score']:.1f} points")
                print(f"   📊 Base score: {data['base_score']:.1f}")
                print(f"   🎯 Bonuses: {data['bonuses']}")
                print(f"   📈 Raw probability: {data['raw_probability']:.8f}")
                print(f"   📉 Normalized: {data['normalized_probability']:.6f}")
                
                scores.append({
                    "start_word": start_word,
                    "candidate": candidate,
                    "score": data['total_score'],
                    "base_score": data['base_score'],
                    "bonuses": data['bonuses']
                })
            else:
                print(f"❌ {result['message']}")
        
        # Sort by score
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"\n4. Score Rankings")
        print("-" * 40)
        for i, score_data in enumerate(scores, 1):
            print(f"{i:2d}. '{score_data['candidate']}' → {score_data['score']:.1f} points")
            print(f"     Base: {score_data['base_score']:.1f}, Bonuses: {score_data['bonuses']}")
        
        # Test invalid candidates
        print(f"\n5. Testing Invalid Candidates")
        print("-" * 40)
        
        invalid_candidates = [
            ("cat", "tree"),   # Not a rhyme
            ("cat", "house"),  # Not a rhyme
            ("cat", "computer"), # Too long
            ("cat", "a"),      # Too short
        ]
        
        for start_word, candidate in invalid_candidates:
            print(f"\nTesting '{candidate}' for '{start_word}'...")
            result = workflow.calculate_rhyme_score(start_word, candidate)
            
            if result["success"]:
                print(f"✅ Unexpected success: {result['data']['total_score']:.1f} points")
            else:
                print(f"❌ Expected failure: {result['message']}")
        
        # Show JSON file info
        print(f"\n6. JSON Storage Information")
        print("-" * 40)
        
        if os.path.exists("test_game_data.json"):
            file_size = os.path.getsize("test_game_data.json")
            print(f"📁 File: test_game_data.json")
            print(f"📏 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            with open("test_game_data.json", 'r') as f:
                data = json.load(f)
                print(f"📊 Words stored: {len(data)}")
                for word, word_data in data.items():
                    rhyme_count = len(word_data.get("rhy.val", []))
                    print(f"   '{word}': {rhyme_count} rhymes")
        else:
            print("❌ JSON file not found")
        
        print(f"\n✅ Game workflow test completed successfully!")
        
        # Save test results
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_words": test_words,
            "scores": scores,
            "invalid_tests": len(invalid_candidates),
            "json_file_size": os.path.getsize("test_game_data.json") if os.path.exists("test_game_data.json") else 0
        }
        
        with open("shared_results/game_workflow_test_results.json", 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"📄 Test results saved to: shared_results/game_workflow_test_results.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_game_workflow())
    sys.exit(0 if success else 1) 