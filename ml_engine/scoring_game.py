#!/usr/bin/env python3
"""
Würdo Scoring Game
==================

A retro console word transformation game with ML-powered scoring.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from utils.redis_DB_storage import populate_database_from_file

sys.path.append(str(Path(__file__).parent))

# Import functions but don't call them yet
def get_services():
    """Get the scoring services with output suppressed."""
    from services.enhanced_scoring_service import get_enhanced_scoring_service
    from services.efficient_word_service import get_efficient_word_service
    return get_enhanced_scoring_service, get_efficient_word_service

def print_title():
    """Print the beautiful retro title screen."""
    title_art = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║    ██╗    ██╗██╗   ██╗██████╗ ██████╗   ██╗        ██╗                       ║             
    ║    ██║    ██║╚═╝   ╚═╝██╔══██╗ ██╔══██╗ █╔╝  ████╗ ╚█║                       ║
    ║    ██║ █╗ ██║██╗   ██╗██████╔╝ ██║  ██║ █║ ██╔══██╗ █║                       ║              
    ║    ██║███╗██║██║   ██║██╔══██╗ ██║  ██║ █║ ██║  ██║ █║                       ║              
    ║    ╚███╔███╔╝╚██████╔╝██║  ██║ ██████╔╝ ██╗╚████╔═╝██║                       ║              
    ║     ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═╝ ╚═══╝  ╚═╝                       ║               
    ║                                                                              ║
    ║                     ✧ Anagram - Rhyme - One-Letter-Off ✧                    ║
    ║                                                                              ║
    ║                    First word supplied - where will you go?                  ║
    ║                                                                              ║
    ║                                                                              ║ 
    ║                              atlas_school 2025                               ║ 
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(title_art)

def print_separator():
    """Print a decorative separator."""
    print("─" * 80)

def print_score_details(score_data):
    """Print detailed score information in a clean format."""
    print(f"\nSCORE BREAKDOWN")
    print("─" * 40)
    
    # Base score
    base_score = score_data.get('base_score', 0)
    print(f"Base Score: {base_score:.2f}")
    
    # Category bonus
    category_bonus = score_data.get('category_bonus', 0)
    if category_bonus > 0:
        print(f"Category Bonus: +{category_bonus:.2f}")
    
    # Creativity score
    creativity_score = score_data.get('creativity_score', 0)
    if creativity_score > 0:
        print(f"Creativity: {creativity_score:.3f}")
    
    # Total score
    total_score = score_data.get('total_score', 0)
    print(f"TOTAL SCORE: {total_score:.2f}")
    
    # Category info
    category = score_data.get('category', 'unknown')
    category_names = {
        'prf': 'Perfect Rhyme',
        'rch': 'Rich Rhyme (Homophone)',
        'sln': 'Slant Rhyme',
        'ana': 'Anagram',
        'ola': 'One-Letter-Added',
        'olr': 'One-Letter-Removed',
        'olx': 'One-Letter-Changed'
    }
    category_name = category_names.get(category, category.upper())
    print(f"Category: {category_name}")

def print_game_stats(session_data):
    """Print current game statistics."""
    print(f"\nGAME STATISTICS")
    print("─" * 40)
    print(f"Rounds Played: {session_data.get('rounds_played', 0)}")
    print(f"Total Score: {session_data.get('total_score', 0):.2f}")
    print(f"Average Score: {session_data.get('average_score', 0):.2f}")
    print(f"Best Score: {session_data.get('best_score', 0):.2f}")

async def play_round(scoring_service, word_service, session_data):
    """Play a single round of the game."""
    print_separator()
    
    # Get start word
    start_word = input("\nEnter a start word: ").strip().lower()
    if not start_word:
        print("Please enter a valid word.")
        return False
    
    if not start_word.isalpha():
        print("Please enter a word with only letters.")
        return False
    
    print(f"\nStarting with: '{start_word.upper()}'")
    
    # Get candidate word
    candidate_word = input("Enter your transformation: ").strip().lower()
    if not candidate_word:
        print("Please enter a valid transformation.")
        return False
    
    if not candidate_word.isalpha():
        print("Please enter a transformation with only letters.")
        return False
    
    print(f"\nScoring: '{start_word}' → '{candidate_word}'")
    
    # Score the candidate
    try:
        # Suppress scoring output
        import os
        from contextlib import redirect_stdout, redirect_stderr
        
        with open(os.devnull, 'w') as devnull:
            with redirect_stdout(devnull), redirect_stderr(devnull):
                result = await scoring_service.score_candidate_comprehensive(start_word, candidate_word)
        
        if result["success"]:
            score_data = result["data"]
            print_score_details(score_data)
            
            # Update session data
            session_data['rounds_played'] = session_data.get('rounds_played', 0) + 1
            session_data['total_score'] = session_data.get('total_score', 0) + score_data['total_score']
            session_data['best_score'] = max(session_data.get('best_score', 0), score_data['total_score'])
            session_data['average_score'] = session_data['total_score'] / session_data['rounds_played']
            
            print_game_stats(session_data)
            
        else:
            print(f"{result['message']}")
            
    except Exception as e:
        print(f"Error scoring word: {e}")
    
    return True

async def main():
    """Main game loop."""
    print_title()
    
    print("\nInitializing Würdo Scoring System...")
    
    try:
        # Suppress ALL output during initialization
        import os
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        # Save original stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Redirect to null
        with open(os.devnull, 'w') as devnull:
            sys.stdout = devnull
            sys.stderr = devnull
            try:
                get_enhanced_scoring_service, get_efficient_word_service = get_services()
                scoring_service = get_enhanced_scoring_service()
                word_service = get_efficient_word_service()
            finally:
                # Restore original stdout/stderr
                sys.stdout = original_stdout
                sys.stderr = original_stderr
        
        print("System ready!")
        
    except Exception as e:
        print(f"Failed to initialize system: {e}")
        return
    
    # Game session data
    session_data = {
        'rounds_played': 0,
        'total_score': 0,
        'best_score': 0,
        'average_score': 0
    }
    
    print("\nWelcome to Würdo! Transform words and earn points!")
    print("Type 'quit' to exit, 'help' for tips")
    
    while True:
        try:
            # Check for special commands
            user_input = input("\n🎯 Enter a start word (or 'quit'/'help'): ").strip().lower()
            
            if user_input == 'quit':
                print("\nThanks for playing Würdo!")
                print_game_stats(session_data)
                break
                
            elif user_input == 'help':
                print("\nGAME TIPS:")
                print("─" * 40)
                print("• Perfect rhymes (cat → hat): Base score + creativity bonus")
                print("• Rich rhymes/homophones (cat → kat): Higher base score")
                print("• Slant rhymes (cat → mat): Bonus points for creativity!")
                print("• Anagrams (cat → act): Rearrange letters")
                print("• One-letter-off: Add, remove, or change one letter")
                print("• Longer words = higher base scores")
                print("• Be creative for higher bonuses!")
                continue
            
            elif not user_input:
                print("Please enter a valid word.")
                continue
            
            elif not user_input.isalpha():
                print("Please enter a word with only letters.")
                continue
            
            # Start the round
            start_word = user_input
            print(f"\nStarting with: '{start_word.upper()}'")
            
            candidate_word = input("Enter your transformation: ").strip().lower()
            
            if candidate_word == 'quit':
                print("\nThanks for playing Würdo!")
                print_game_stats(session_data)
                break
                
            if not candidate_word:
                print("Please enter a valid transformation.")
                continue
            
            if not candidate_word.isalpha():
                print("Please enter a transformation with only letters.")
                continue
            
            print(f"\nScoring: '{start_word}' → '{candidate_word}'")
            
            # Score the candidate
            try:
                # Suppress scoring output
                import os
                from contextlib import redirect_stdout, redirect_stderr
                
                with open(os.devnull, 'w') as devnull:
                    with redirect_stdout(devnull), redirect_stderr(devnull):
                        result = await scoring_service.score_candidate_comprehensive(start_word, candidate_word)
                
                if result["success"]:
                    score_data = result["data"]
                    print_score_details(score_data)
                    
                    # Update session data
                    session_data['rounds_played'] = session_data.get('rounds_played', 0) + 1
                    session_data['total_score'] = session_data.get('total_score', 0) + score_data['total_score']
                    session_data['best_score'] = max(session_data.get('best_score', 0), score_data['total_score'])
                    session_data['average_score'] = session_data['total_score'] / session_data['rounds_played']
                    
                    print_game_stats(session_data)
                    
                else:
                    print(f"{result['message']}")
                    
            except Exception as e:
                print(f"Error scoring word: {e}")
        
        except KeyboardInterrupt:
            print("\n\nThanks for playing Würdo!")
            print_game_stats(session_data)
            populate_database_from_file("ml_engine/game_data/probability_trees.json")
            break
        except EOFError:
            print("\n\nThanks for playing Würdo!")
            print_game_stats(session_data)
            populate_database_from_file("ml_engine/game_data/probability_trees.json")
            break

if __name__ == "__main__":
    asyncio.run(main())